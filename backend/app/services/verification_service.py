"""Domain verification service for asset ownership."""
import secrets
import string
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import dns.resolver


class VerificationService:
    """Service for verifying domain ownership."""

    @staticmethod
    def generate_verification_token() -> str:
        """Generate a random verification token."""
        # Generate 8-character alphanumeric token
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(8))

    @staticmethod
    def get_verification_instructions(domain: str, token: str) -> Dict:
        """Get verification instructions for all methods."""
        return {
            "dns_txt": {
                "method": "DNS TXT Record",
                "recommended": True,
                "name": "_acti-verify",
                "value": f"acti-{token}",
                "instructions": f"Add a TXT record to your DNS with name '_acti-verify' and value 'acti-{token}'"
            },
            "html_file": {
                "method": "HTML File Upload",
                "recommended": False,
                "filename": "acti-verify.html",
                "url": f"https://{domain}/acti-verify.html",
                "content": f"acti-verification={token}",
                "instructions": f"Upload a file named 'acti-verify.html' to your website root containing: acti-verification={token}"
            },
            "email": {
                "method": "Email Verification",
                "recommended": False,
                "email": f"admin@{domain}",
                "instructions": f"We'll send a verification link to admin@{domain}"
            }
        }

    @staticmethod
    def verify_dns_txt(domain: str, expected_token: str) -> Tuple[bool, str]:
        """Verify domain ownership via DNS TXT record."""
        try:
            # Query DNS for TXT records
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5

            # Look for _acti-verify TXT record
            answers = resolver.resolve(f"_acti-verify.{domain}", 'TXT')

            for rdata in answers:
                txt_value = rdata.to_text().strip('"')
                if txt_value == f"acti-{expected_token}":
                    return True, "DNS TXT record verified successfully"

            return False, "DNS TXT record not found or token mismatch"

        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist"
        except dns.resolver.NoAnswer:
            return False, "No TXT records found for _acti-verify"
        except dns.resolver.Timeout:
            return False, "DNS query timeout"
        except Exception as e:
            return False, f"DNS verification failed: {str(e)}"

    @staticmethod
    def verify_html_file(domain: str, expected_token: str) -> Tuple[bool, str]:
        """Verify domain ownership via HTML file."""
        try:
            # Try HTTPS first
            url = f"https://{domain}/acti-verify.html"
            response = requests.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                content = response.text.strip()
                if f"acti-verification={expected_token}" in content:
                    return True, "HTML file verified successfully"
                else:
                    return False, "HTML file found but token mismatch"
            else:
                return False, f"HTML file not found (HTTP {response.status_code})"

        except requests.exceptions.SSLError:
            # Try HTTP if HTTPS fails
            try:
                url = f"http://{domain}/acti-verify.html"
                response = requests.get(url, timeout=10, allow_redirects=True)

                if response.status_code == 200:
                    content = response.text.strip()
                    if f"acti-verification={expected_token}" in content:
                        return True, "HTML file verified successfully (HTTP)"
                    else:
                        return False, "HTML file found but token mismatch"
                else:
                    return False, f"HTML file not found (HTTP {response.status_code})"
            except Exception as e:
                return False, f"HTML verification failed: {str(e)}"

        except Exception as e:
            return False, f"HTML verification failed: {str(e)}"

    @staticmethod
    def verify_domain(domain: str, token: str, method: str = "auto") -> Tuple[bool, str, str]:
        """
        Verify domain ownership.

        Args:
            domain: Domain to verify
            token: Expected verification token
            method: Verification method ("dns_txt", "html_file", or "auto")

        Returns:
            Tuple of (success, message, method_used)
        """
        if method == "dns_txt":
            success, message = VerificationService.verify_dns_txt(domain, token)
            return success, message, "dns_txt"

        elif method == "html_file":
            success, message = VerificationService.verify_html_file(domain, token)
            return success, message, "html_file"

        elif method == "auto":
            # Try DNS first (recommended)
            success, message = VerificationService.verify_dns_txt(domain, token)
            if success:
                return True, message, "dns_txt"

            # Try HTML file if DNS fails
            success, message = VerificationService.verify_html_file(domain, token)
            if success:
                return True, message, "html_file"

            return False, "Verification failed for all methods", "auto"

        else:
            return False, "Invalid verification method", "unknown"


# Create singleton instance
verification_service = VerificationService()
