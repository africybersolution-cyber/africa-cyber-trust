"""Trust scoring service that calculates risk scores."""
from typing import Dict, Any, List


class TrustScorerService:
    """Calculates trust scores based on check results."""

    def calculate_url_score(self, check_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate trust score for a URL based on passive checks.

        Starts at 100 and subtracts points for risk factors.
        """
        score = 100
        red_flags = []

        # Check domain
        domain_data = check_results.get("checks", {}).get("domain", {})
        if domain_data.get("age_days") is not None and domain_data["age_days"] < 30:
            score -= 20
            red_flags.append({
                "severity": "high",
                "category": "domain_age",
                "message": "Domain is less than 30 days old",
                "evidence": f"Created {domain_data['age_days']} days ago"
            })

        # Check SSL
        ssl_data = check_results.get("checks", {}).get("ssl", {})
        if ssl_data.get("valid") is False:
            score -= 25
            red_flags.append({
                "severity": "critical",
                "category": "ssl",
                "message": "Invalid or missing SSL certificate",
                "evidence": ssl_data.get("error", "Certificate validation failed")
            })

        # Check security headers
        headers_data = check_results.get("checks", {}).get("headers", {})
        if headers_data.get("status") == "completed":
            missing_headers = []
            if not headers_data.get("hsts"):
                missing_headers.append("HSTS")
            if not headers_data.get("csp"):
                missing_headers.append("CSP")
            if not headers_data.get("x_frame_options"):
                missing_headers.append("X-Frame-Options")

            if missing_headers:
                score -= 10
                red_flags.append({
                    "severity": "medium",
                    "category": "security_headers",
                    "message": f"Missing security headers: {', '.join(missing_headers)}",
                    "evidence": "Security headers help protect against common attacks"
                })

        # Check blacklists
        blacklist_data = check_results.get("checks", {}).get("blacklist", {})
        if blacklist_data.get("google_safe_browsing") == "malicious":
            score -= 50
            red_flags.append({
                "severity": "critical",
                "category": "blacklist",
                "message": "Listed in Google Safe Browsing as malicious",
                "evidence": "This site has been flagged for malware or phishing"
            })

        # Check redirects
        redirect_data = check_results.get("checks", {}).get("redirects", {})
        if redirect_data.get("suspicious"):
            score -= 20
            red_flags.append({
                "severity": "high",
                "category": "redirects",
                "message": "Suspicious redirect chain detected",
                "evidence": f"Redirects {redirect_data.get('redirect_count', 0)} times"
            })

        # Determine risk level
        if score >= 80:
            risk_level = "low"
        elif score >= 60:
            risk_level = "medium"
        elif score >= 40:
            risk_level = "high"
        else:
            risk_level = "critical"

        # Generate summary
        summary = self._generate_summary(score, risk_level, red_flags)

        # Generate safety advice
        safety_advice = self._generate_safety_advice(risk_level, red_flags)

        return {
            "score": max(0, score),  # Ensure score doesn't go below 0
            "risk_level": risk_level,
            "red_flags": red_flags,
            "summary": summary,
            "safety_advice": safety_advice,
        }

    def _generate_summary(self, score: int, risk_level: str, red_flags: List[Dict]) -> str:
        """Generate human-readable summary."""
        if risk_level == "low":
            return f"This website appears safe with a trust score of {score}/100."
        elif risk_level == "medium":
            return f"This website has some concerns (score: {score}/100). {len(red_flags)} issue(s) detected."
        elif risk_level == "high":
            return f"This website shows significant risk factors (score: {score}/100). Proceed with caution."
        else:
            return f"This website shows critical security risks (score: {score}/100). We recommend avoiding it."

    def _generate_safety_advice(self, risk_level: str, red_flags: List[Dict]) -> str:
        """Generate safety recommendations."""
        if risk_level == "low":
            return "This site appears legitimate. Always verify you're on the correct URL and look for the padlock icon."
        elif risk_level == "medium":
            return "Exercise caution. Verify this is the legitimate website before entering personal information or making payments."
        elif risk_level == "high":
            return "High risk detected. Do not enter passwords, payment details, or personal information. Verify the site's legitimacy through official channels."
        else:
            return "Critical risk detected. We strongly recommend not using this website. It may be attempting to steal your information."
