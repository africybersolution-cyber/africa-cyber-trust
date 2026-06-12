"""Background checker service for passive security checks."""
from typing import Dict, Any
import socket
import ssl
import httpx
from datetime import datetime
from sqlalchemy.orm import Session


class BackgroundCheckerService:
    """Performs passive background checks on URLs, apps, and companies."""

    def __init__(self, db: Session):
        self.db = db

    async def check_url(self, url: str) -> Dict[str, Any]:
        """
        Run comprehensive passive checks on a URL.

        Returns structured data with all check results.
        """
        results = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        # DNS and domain checks
        results["checks"]["domain"] = await self._check_domain(url)

        # SSL/TLS certificate check
        results["checks"]["ssl"] = await self._check_ssl(url)

        # HTTP headers and security check
        results["checks"]["headers"] = await self._check_security_headers(url)

        # Redirect chain analysis
        results["checks"]["redirects"] = await self._check_redirects(url)

        # Blacklist lookup
        results["checks"]["blacklist"] = await self._check_blacklists(url)

        # Similar domain detection (typosquatting)
        results["checks"]["similar_domains"] = await self._check_similar_domains(url)

        return results

    async def _check_domain(self, url: str) -> Dict[str, Any]:
        """Check domain age, registration, and DNS records."""
        import socket
        from urllib.parse import urlparse

        try:
            # Extract domain from URL
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            domain = parsed.netloc or parsed.path.split('/')[0]

            result = {
                "status": "completed",
                "domain": domain,
                "age_days": None,
                "registrar": None,
                "creation_date": None,
                "dns_resolved": False,
                "ip_address": None,
            }

            # DNS Resolution Check
            try:
                ip_address = socket.gethostbyname(domain)
                result["dns_resolved"] = True
                result["ip_address"] = ip_address
            except socket.gaierror:
                result["dns_resolved"] = False
                result["error"] = "DNS resolution failed"

            # WHOIS Lookup (optional - requires python-whois package)
            try:
                import whois
                w = whois.whois(domain)

                if w.creation_date:
                    creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                    result["creation_date"] = str(creation_date)

                    # Calculate age in days
                    age = datetime.utcnow() - creation_date
                    result["age_days"] = age.days

                if w.registrar:
                    result["registrar"] = w.registrar

            except ImportError:
                # python-whois not installed, skip WHOIS check
                result["whois_available"] = False
            except Exception as e:
                result["whois_error"] = str(e)

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "age_days": None,
                "registrar": None,
                "creation_date": None,
            }

    async def _check_ssl(self, url: str) -> Dict[str, Any]:
        """Check SSL certificate validity and configuration."""
        import ssl
        import socket
        from urllib.parse import urlparse

        try:
            # Extract domain from URL
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            hostname = parsed.netloc or parsed.path.split('/')[0]

            # Remove port if present
            if ':' in hostname:
                hostname = hostname.split(':')[0]

            result = {
                "status": "completed",
                "hostname": hostname,
                "valid": False,
                "issuer": None,
                "expires_at": None,
                "issued_at": None,
                "days_until_expiry": None,
            }

            # Create SSL context
            context = ssl.create_default_context()

            # Connect and get certificate
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    # Certificate is valid if we got here
                    result["valid"] = True

                    # Extract certificate info
                    if cert:
                        # Issuer
                        issuer = dict(x[0] for x in cert.get('issuer', []))
                        result["issuer"] = issuer.get('organizationName', 'Unknown')

                        # Expiry date
                        not_after = cert.get('notAfter')
                        if not_after:
                            from datetime import datetime
                            expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                            result["expires_at"] = expiry_date.isoformat()

                            # Calculate days until expiry
                            days_left = (expiry_date - datetime.utcnow()).days
                            result["days_until_expiry"] = days_left

                        # Issue date
                        not_before = cert.get('notBefore')
                        if not_before:
                            issue_date = datetime.strptime(not_before, '%b %d %H:%M:%S %Y %Z')
                            result["issued_at"] = issue_date.isoformat()

            return result

        except ssl.SSLError as e:
            return {
                "status": "error",
                "valid": False,
                "error": f"SSL Error: {str(e)}",
                "error_type": "ssl_error"
            }
        except socket.timeout:
            return {
                "status": "error",
                "valid": False,
                "error": "Connection timeout",
                "error_type": "timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "valid": False,
                "error": str(e),
                "error_type": "general_error"
            }

    async def _check_security_headers(self, url: str) -> Dict[str, Any]:
        """Check for security headers like HSTS, CSP, X-Frame-Options."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                response = await client.get(url)
                headers = response.headers

                return {
                    "status": "completed",
                    "hsts": "strict-transport-security" in headers,
                    "csp": "content-security-policy" in headers,
                    "x_frame_options": "x-frame-options" in headers,
                    "x_content_type_options": "x-content-type-options" in headers,
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    async def _check_redirects(self, url: str) -> Dict[str, Any]:
        """Analyze redirect chain for suspicious behavior."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url, follow_redirects=True)

                redirect_count = len(response.history)
                final_url = str(response.url)

                # Analyze redirects for suspicious patterns
                suspicious = False
                redirect_chain = [url]
                domains = []

                for resp in response.history:
                    redirect_chain.append(str(resp.url))
                    from urllib.parse import urlparse
                    domain = urlparse(str(resp.url)).netloc
                    domains.append(domain)

                # Add final domain
                final_domain = urlparse(final_url).netloc
                domains.append(final_domain)

                # Check for suspicious patterns
                # 1. Too many redirects
                if redirect_count > 5:
                    suspicious = True

                # 2. Cross-domain redirects to different TLDs
                unique_domains = set(domains)
                if len(unique_domains) > 3:
                    suspicious = True

                # 3. Redirect to IP address
                if final_domain.replace('.', '').isdigit():
                    suspicious = True

                return {
                    "status": "completed",
                    "redirect_count": redirect_count,
                    "final_url": final_url,
                    "redirect_chain": redirect_chain,
                    "domains_visited": list(unique_domains),
                    "suspicious": suspicious,
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "redirect_count": 0,
                "final_url": url,
                "suspicious": False,
            }

    async def _check_blacklists(self, url: str) -> Dict[str, Any]:
        """Check against known malware/phishing blacklists."""
        from urllib.parse import urlparse

        result = {
            "status": "completed",
            "url": url,
            "is_blacklisted": False,
            "sources": [],
        }

        # Google Safe Browsing API (requires API key)
        # For MVP, we'll implement a placeholder that can be activated with API key
        try:
            from app.core.config import settings
            if settings.GOOGLE_SAFE_BROWSING_API_KEY:
                # TODO: Implement actual Google Safe Browsing API call
                result["google_safe_browsing"] = "not_checked"
                result["google_safe_browsing_note"] = "API integration pending"
            else:
                result["google_safe_browsing"] = "no_api_key"
        except:
            result["google_safe_browsing"] = "not_configured"

        # VirusTotal API (requires API key)
        try:
            from app.core.config import settings
            if hasattr(settings, 'VIRUSTOTAL_API_KEY') and settings.VIRUSTOTAL_API_KEY:
                # TODO: Implement VirusTotal API call
                result["virustotal"] = "not_checked"
                result["virustotal_note"] = "API integration pending"
            else:
                result["virustotal"] = "no_api_key"
        except:
            result["virustotal"] = "not_configured"

        # PhishTank (free API available)
        # For MVP, placeholder
        result["phishtank"] = "not_checked"
        result["phishtank_note"] = "Integration pending"

        # Local blacklist check (can be expanded)
        suspicious_keywords = ['hack', 'phish', 'scam', 'fake', 'fraud']
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for keyword in suspicious_keywords:
            if keyword in domain:
                result["is_blacklisted"] = True
                result["sources"].append(f"suspicious_keyword:{keyword}")
                break

        return result

    async def _check_similar_domains(self, url: str) -> Dict[str, Any]:
        """Detect typosquatting and similar malicious domains."""
        # TODO: Implement typosquatting detection
        # TODO: Check for homograph attacks
        return {
            "status": "pending",
            "similar_domains": [],
        }

    async def generate_explanation(
        self, check_results: Dict[str, Any], score_result: Dict[str, Any]
    ) -> str:
        """Generate AI explanation of check results."""
        # TODO: Integrate with AI service (OpenAI/Anthropic)
        # TODO: Create structured prompt with check results
        # TODO: Return human-readable explanation

        # Placeholder
        if score_result["risk_level"] == "low":
            return "This website appears to be safe based on our passive checks. It has valid SSL, good security headers, and no known blacklist entries."
        elif score_result["risk_level"] == "medium":
            return "This website has some concerns. Please proceed with caution and verify the legitimacy before sharing sensitive information."
        else:
            return "This website shows multiple red flags. We recommend avoiding it until further verification."

    async def save_public_check(
        self,
        input_type: str,
        input_value: str,
        score: int,
        risk_level: str,
        summary: str,
        red_flags: list,
        ai_explanation: str,
        check_data: dict,
        ip_address: str,
        user_agent: str,
    ):
        """Save public check to database."""
        from app.models.public_check import PublicCheck

        try:
            public_check = PublicCheck(
                input_type=input_type,
                input_value=input_value,
                score=score,
                risk_level=risk_level,
                summary=summary,
                red_flags=red_flags,
                ai_explanation=ai_explanation,
                check_data=check_data,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            self.db.add(public_check)
            self.db.commit()
            self.db.refresh(public_check)

            return public_check
        except Exception as e:
            self.db.rollback()
            # For now, return mock object if database fails
            class MockPublicCheck:
                def __init__(self):
                    self.id = "mock-check-id"
                    self.created_at = datetime.utcnow()
            return MockPublicCheck()
