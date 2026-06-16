"""Breach monitoring service using HaveIBeenPwned API."""
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime


class BreachMonitorService:
    """Monitor email addresses and domains for data breaches using HaveIBeenPwned."""

    HIBP_API_URL = "https://haveibeenpwned.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize breach monitor service.

        Args:
            api_key: HaveIBeenPwned API key (optional for domain checks, required for email)
        """
        self.api_key = api_key
        self.headers = {
            "User-Agent": "AfricaCyberTrust-BreachMonitor/1.0",
        }
        if api_key:
            self.headers["hibp-api-key"] = api_key

    async def check_email_breaches(self, email: str) -> List[Dict[str, Any]]:
        """
        Check if an email address has been in any data breaches.

        Args:
            email: Email address to check

        Returns:
            List of breach dictionaries with details

        Raises:
            Exception: If API key is not configured
        """
        if not self.api_key:
            raise Exception("HaveIBeenPwned API key required for email checks")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.HIBP_API_URL}/breachedaccount/{email}",
                    headers=self.headers,
                    params={"truncateResponse": "false"},
                    timeout=10.0
                )

                # 404 = no breaches found (good!)
                if response.status_code == 404:
                    print(f"[BREACH] No breaches found for {email}")
                    return []

                # 200 = breaches found
                if response.status_code == 200:
                    breaches = response.json()
                    print(f"[BREACH] Found {len(breaches)} breaches for {email}")
                    return self._format_breaches(breaches)

                # 429 = rate limited
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    raise Exception(f"Rate limited. Retry after {retry_after} seconds")

                # Other errors
                raise Exception(f"API error: {response.status_code} - {response.text}")

        except httpx.TimeoutException:
            raise Exception("HaveIBeenPwned API timeout")
        except Exception as e:
            print(f"[BREACH] Error checking email {email}: {str(e)}")
            raise

    async def check_domain_breaches(self, domain: str) -> List[Dict[str, Any]]:
        """
        Check if a domain has been involved in any data breaches.

        Args:
            domain: Domain to check (e.g., 'adobe.com')

        Returns:
            List of breach dictionaries
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.HIBP_API_URL}/breaches",
                    headers=self.headers,
                    params={"domain": domain},
                    timeout=10.0
                )

                if response.status_code == 404:
                    print(f"[BREACH] No breaches found for domain {domain}")
                    return []

                if response.status_code == 200:
                    breaches = response.json()
                    print(f"[BREACH] Found {len(breaches)} breaches for domain {domain}")
                    return self._format_breaches(breaches)

                raise Exception(f"API error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"[BREACH] Error checking domain {domain}: {str(e)}")
            raise

    async def check_paste_exposures(self, email: str) -> List[Dict[str, Any]]:
        """
        Check if an email has been exposed in pastes (e.g., Pastebin).

        Args:
            email: Email address to check

        Returns:
            List of paste exposure dictionaries
        """
        if not self.api_key:
            raise Exception("HaveIBeenPwned API key required for paste checks")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.HIBP_API_URL}/pasteaccount/{email}",
                    headers=self.headers,
                    timeout=10.0
                )

                if response.status_code == 404:
                    print(f"[BREACH] No paste exposures for {email}")
                    return []

                if response.status_code == 200:
                    pastes = response.json()
                    print(f"[BREACH] Found {len(pastes)} paste exposures for {email}")
                    return self._format_pastes(pastes)

                raise Exception(f"API error: {response.status_code}")

        except Exception as e:
            print(f"[BREACH] Error checking pastes for {email}: {str(e)}")
            raise

    async def check_password_pwned(self, password: str) -> int:
        """
        Check how many times a password appears in known breaches using k-anonymity.

        Args:
            password: Password to check

        Returns:
            Number of times the password has been seen in breaches (0 = safe)
        """
        import hashlib

        # SHA-1 hash the password
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        hash_prefix = sha1_hash[:5]
        hash_suffix = sha1_hash[5:]

        try:
            async with httpx.AsyncClient() as client:
                # k-anonymity: only send first 5 chars
                response = await client.get(
                    f"https://api.pwnedpasswords.com/range/{hash_prefix}",
                    headers={"User-Agent": "AfricaCyberTrust-PasswordCheck/1.0"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    raise Exception(f"API error: {response.status_code}")

                # Parse response (format: SUFFIX:COUNT\r\n)
                for line in response.text.splitlines():
                    if ':' in line:
                        suffix, count = line.split(':')
                        if suffix == hash_suffix:
                            count = int(count)
                            print(f"[BREACH] Password found in {count} breaches")
                            return count

                # Not found in breaches (good!)
                print("[BREACH] Password not found in breaches")
                return 0

        except Exception as e:
            print(f"[BREACH] Error checking password: {str(e)}")
            raise

    def _format_breaches(self, breaches: List[Dict]) -> List[Dict[str, Any]]:
        """Format breach data for storage/display."""
        formatted = []
        for breach in breaches:
            formatted.append({
                "name": breach.get("Name"),
                "title": breach.get("Title"),
                "domain": breach.get("Domain"),
                "breach_date": breach.get("BreachDate"),
                "added_date": breach.get("AddedDate"),
                "modified_date": breach.get("ModifiedDate"),
                "pwn_count": breach.get("PwnCount", 0),
                "description": breach.get("Description", ""),
                "data_classes": breach.get("DataClasses", []),  # What data was leaked
                "is_verified": breach.get("IsVerified", False),
                "is_fabricated": breach.get("IsFabricated", False),
                "is_sensitive": breach.get("IsSensitive", False),
                "is_retired": breach.get("IsRetired", False),
                "is_spam_list": breach.get("IsSpamList", False),
                "logo_path": breach.get("LogoPath", ""),
            })
        return formatted

    def _format_pastes(self, pastes: List[Dict]) -> List[Dict[str, Any]]:
        """Format paste exposure data."""
        formatted = []
        for paste in pastes:
            formatted.append({
                "source": paste.get("Source"),
                "id": paste.get("Id"),
                "title": paste.get("Title"),
                "date": paste.get("Date"),
                "email_count": paste.get("EmailCount", 0),
            })
        return formatted

    def get_severity(self, breach: Dict[str, Any]) -> str:
        """
        Determine severity level of a breach.

        Returns: 'critical', 'high', 'medium', or 'low'
        """
        # Critical if sensitive data
        if breach.get("is_sensitive"):
            return "critical"

        # Check what data was leaked
        data_classes = breach.get("data_classes", [])
        sensitive_classes = ["Passwords", "Credit cards", "Social security numbers",
                            "Bank account numbers", "Financial information"]

        if any(sc in data_classes for sc in sensitive_classes):
            return "critical"

        # High if password hashes leaked
        if "Password hints" in data_classes or "Security questions and answers" in data_classes:
            return "high"

        # Medium for verified breaches with significant data
        if breach.get("is_verified") and breach.get("pwn_count", 0) > 100000:
            return "high"

        if breach.get("is_verified"):
            return "medium"

        return "low"


# Singleton instance
breach_monitor_service = BreachMonitorService()
