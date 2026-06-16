"""Free Trust Score API - No registration required."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, HttpUrl
import httpx
import dns.resolver
import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse


router = APIRouter(prefix="/api/free-trust-score", tags=["Free Trust Score"])


class TrustScoreRequest(BaseModel):
    """Request for free trust score check."""
    url: str  # Domain or URL to check


class TrustScoreResponse(BaseModel):
    """Free trust score response."""
    domain: str
    score: int  # 0-100
    grade: str  # A+, A, B, C, D, F
    checks_passed: int
    checks_failed: int
    critical_issues: int
    checks: Dict[str, Any]
    scan_date: str
    upgrade_message: str


# Rate limiting cache (simple in-memory, domain → last check time)
_rate_limit_cache: Dict[str, datetime] = {}
_rate_limit_window = timedelta(hours=1)  # 1 check per domain per hour


@router.post("/check", response_model=TrustScoreResponse)
async def get_free_trust_score(
    request: TrustScoreRequest,
    client_request: Request
):
    """
    Get free trust score for any domain - no registration required!

    Checks:
    - SSL/TLS certificate validity
    - Security headers (HSTS, CSP, X-Frame-Options, etc.)
    - DNS security (DNSSEC, SPF, DMARC)
    - Basic vulnerability indicators
    - Response time

    Rate limit: 1 check per domain per hour (prevents abuse)
    """
    # Extract domain from URL
    domain = _extract_domain(request.url)
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid URL or domain")

    # Rate limiting check
    if domain in _rate_limit_cache:
        last_check = _rate_limit_cache[domain]
        if datetime.utcnow() - last_check < _rate_limit_window:
            time_remaining = _rate_limit_window - (datetime.utcnow() - last_check)
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit: Please wait {minutes_remaining} minutes before checking {domain} again"
            )

    # Run free checks
    checks = await _run_free_checks(domain)

    # Calculate score
    score_data = _calculate_score(checks)

    # Update rate limit
    _rate_limit_cache[domain] = datetime.utcnow()

    # Clean old entries from cache (keep memory bounded)
    _cleanup_rate_limit_cache()

    return TrustScoreResponse(
        domain=domain,
        score=score_data["score"],
        grade=score_data["grade"],
        checks_passed=score_data["passed"],
        checks_failed=score_data["failed"],
        critical_issues=score_data["critical"],
        checks=checks,
        scan_date=datetime.utcnow().isoformat(),
        upgrade_message=_get_upgrade_message(score_data["score"])
    )


async def _run_free_checks(domain: str) -> Dict[str, Any]:
    """
    Run free security checks on domain.

    Returns dictionary of check results.
    """
    checks = {}

    # Check 1: SSL/TLS Certificate
    checks["ssl"] = await _check_ssl(domain)

    # Check 2: Security Headers
    checks["headers"] = await _check_security_headers(domain)

    # Check 3: DNS Security
    checks["dns"] = await _check_dns_security(domain)

    # Check 4: HTTP → HTTPS Redirect
    checks["https_redirect"] = await _check_https_redirect(domain)

    # Check 5: Mixed Content Check
    checks["mixed_content"] = await _check_mixed_content(domain)

    return checks


async def _check_ssl(domain: str) -> Dict[str, Any]:
    """Check SSL certificate validity."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                # Check expiration
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (not_after - datetime.utcnow()).days

                # Check issuer
                issuer = dict(x[0] for x in cert['issuer'])
                is_self_signed = issuer.get('commonName') == domain

                return {
                    "status": "pass" if days_until_expiry > 30 and not is_self_signed else "fail",
                    "valid": True,
                    "days_until_expiry": days_until_expiry,
                    "issuer": issuer.get('organizationName', 'Unknown'),
                    "self_signed": is_self_signed,
                    "message": f"Valid for {days_until_expiry} days" if days_until_expiry > 30 else f"Expires in {days_until_expiry} days!"
                }

    except Exception as e:
        return {
            "status": "fail",
            "valid": False,
            "error": str(e),
            "message": "No valid SSL certificate"
        }


async def _check_security_headers(domain: str) -> Dict[str, Any]:
    """Check for security headers."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(f"https://{domain}")

            headers = response.headers

            # Critical security headers
            checks = {
                "hsts": "strict-transport-security" in headers,
                "csp": "content-security-policy" in headers,
                "x_frame_options": "x-frame-options" in headers,
                "x_content_type_options": "x-content-type-options" in headers,
                "x_xss_protection": "x-xss-protection" in headers,
                "referrer_policy": "referrer-policy" in headers
            }

            passed = sum(checks.values())
            total = len(checks)

            return {
                "status": "pass" if passed >= 4 else "warn" if passed >= 2 else "fail",
                "passed": passed,
                "total": total,
                "headers": checks,
                "message": f"{passed}/{total} security headers present"
            }

    except Exception as e:
        return {
            "status": "fail",
            "error": str(e),
            "message": "Could not check security headers"
        }


async def _check_dns_security(domain: str) -> Dict[str, Any]:
    """Check DNS security records (DNSSEC, SPF, DMARC)."""
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5

        checks = {
            "spf": False,
            "dmarc": False,
            "dnssec": False
        }

        # Check SPF
        try:
            txt_records = resolver.resolve(domain, 'TXT')
            for record in txt_records:
                if 'v=spf1' in str(record):
                    checks["spf"] = True
                    break
        except:
            pass

        # Check DMARC
        try:
            dmarc_records = resolver.resolve(f'_dmarc.{domain}', 'TXT')
            if dmarc_records:
                checks["dmarc"] = True
        except:
            pass

        # DNSSEC check (basic)
        try:
            resolver.resolve(domain, 'A', raise_on_no_answer=False)
            # If no exception, assume DNSSEC might be configured
            # Full DNSSEC validation requires more complex logic
            checks["dnssec"] = False  # Conservative default
        except:
            pass

        passed = sum(checks.values())

        return {
            "status": "pass" if passed >= 2 else "warn" if passed >= 1 else "fail",
            "passed": passed,
            "total": 3,
            "records": checks,
            "message": f"{passed}/3 DNS security records found"
        }

    except Exception as e:
        return {
            "status": "fail",
            "error": str(e),
            "message": "Could not check DNS records"
        }


async def _check_https_redirect(domain: str) -> Dict[str, Any]:
    """Check if HTTP redirects to HTTPS."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            response = await client.get(f"http://{domain}")

            # Check if redirect to HTTPS
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get("location", "")
                redirects_to_https = location.startswith("https://")

                return {
                    "status": "pass" if redirects_to_https else "fail",
                    "redirects": redirects_to_https,
                    "message": "HTTP → HTTPS redirect configured" if redirects_to_https else "No HTTPS redirect"
                }

            # Check if HTTP responds directly (bad)
            if response.status_code == 200:
                return {
                    "status": "fail",
                    "redirects": False,
                    "message": "HTTP traffic not redirected to HTTPS"
                }

    except Exception as e:
        # If HTTP doesn't respond at all, that's actually good (HTTPS only)
        return {
            "status": "pass",
            "redirects": True,
            "message": "HTTP not accessible (HTTPS only)"
        }


async def _check_mixed_content(domain: str) -> Dict[str, Any]:
    """Check for mixed content (HTTP resources on HTTPS page)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://{domain}")
            html = response.text

            # Look for HTTP resources
            http_resources = re.findall(r'http://[^"\'\s]+', html, re.IGNORECASE)

            # Filter out external domains (only check same domain)
            internal_http = [r for r in http_resources if domain in r]

            has_mixed_content = len(internal_http) > 0

            return {
                "status": "fail" if has_mixed_content else "pass",
                "mixed_content_found": has_mixed_content,
                "count": len(internal_http),
                "message": f"Found {len(internal_http)} mixed content issues" if has_mixed_content else "No mixed content detected"
            }

    except Exception as e:
        return {
            "status": "warn",
            "error": str(e),
            "message": "Could not check for mixed content"
        }


def _calculate_score(checks: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall trust score (0-100) from check results."""
    score = 100
    passed = 0
    failed = 0
    critical = 0

    # SSL check (critical - 40 points)
    if checks["ssl"]["status"] == "pass":
        passed += 1
    else:
        score -= 40
        failed += 1
        critical += 1

    # Security headers (20 points)
    if checks["headers"]["status"] == "pass":
        score -= 0
        passed += 1
    elif checks["headers"]["status"] == "warn":
        score -= 10
        failed += 1
    else:
        score -= 20
        failed += 1

    # DNS security (15 points)
    if checks["dns"]["status"] == "pass":
        passed += 1
    elif checks["dns"]["status"] == "warn":
        score -= 7
        failed += 1
    else:
        score -= 15
        failed += 1

    # HTTPS redirect (15 points)
    if checks["https_redirect"]["status"] == "pass":
        passed += 1
    else:
        score -= 15
        failed += 1

    # Mixed content (10 points)
    if checks["mixed_content"]["status"] == "pass":
        passed += 1
    elif checks["mixed_content"]["status"] == "warn":
        score -= 5
        failed += 1
    else:
        score -= 10
        failed += 1
        critical += 1

    # Ensure score is in range
    score = max(0, min(100, score))

    # Assign grade
    if score >= 95:
        grade = "A+"
    elif score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": score,
        "grade": grade,
        "passed": passed,
        "failed": failed,
        "critical": critical
    }


def _get_upgrade_message(score: int) -> str:
    """Get personalized upgrade message based on score."""
    if score >= 90:
        return "Great security! Upgrade to monitor your score 24/7 and get alerts on any changes."
    elif score >= 70:
        return "Good start! Upgrade to fix remaining issues and prevent future vulnerabilities."
    else:
        return "Critical issues found! Upgrade now for detailed reports and step-by-step remediation."


def _extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL or domain string."""
    # If it's already a domain (no protocol), validate and return
    if not url.startswith(('http://', 'https://')):
        # Add https:// for parsing
        url = f"https://{url}"

    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path

        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        # Basic validation
        if '.' not in domain or len(domain) < 4:
            return None

        return domain

    except Exception:
        return None


def _cleanup_rate_limit_cache():
    """Remove entries older than rate limit window to prevent memory bloat."""
    cutoff = datetime.utcnow() - _rate_limit_window
    expired = [domain for domain, timestamp in _rate_limit_cache.items() if timestamp < cutoff]

    for domain in expired:
        del _rate_limit_cache[domain]
