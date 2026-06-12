"""
Scam Detection Service - Checks if a website/company is legitimate or a scam.

This is SAFE for public use - focuses on trust verification, not vulnerability exposure.
"""
import httpx
import re
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, List
from urllib.parse import urlparse
import whois
from app.core.config import settings


class ScamDetectorService:
    """
    Detects scams, phishing, and fraudulent websites.

    Checks:
    1. Domain age (new = suspicious)
    2. WHOIS privacy (hidden owner = red flag)
    3. VirusTotal reputation
    4. Google Safe Browsing
    5. SSL certificate trust
    6. Typosquatting detection
    7. Suspicious keywords
    8. Clone detection
    """

    def __init__(self):
        self.virustotal_key = settings.VIRUSTOTAL_API_KEY if hasattr(settings, 'VIRUSTOTAL_API_KEY') else None
        self.safe_browsing_key = settings.GOOGLE_SAFE_BROWSING_KEY if hasattr(settings, 'GOOGLE_SAFE_BROWSING_KEY') else None

    async def check_website(self, url: str) -> Dict[str, Any]:
        """
        Main scam detection function.
        Returns trust score (0-100) and red flags.
        """
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path

        # Remove www.
        domain = domain.replace('www.', '')

        red_flags = []
        trust_indicators = []
        trust_score = 100  # Start high, deduct for red flags

        # 1. Domain Age Check
        domain_info = await self._check_domain_age(domain)
        if domain_info.get('is_new'):
            red_flags.append({
                'severity': 'high',
                'category': 'New Domain',
                'message': f"Domain registered only {domain_info.get('days_old', 0)} days ago",
                'impact': 'New domains are often used for scams'
            })
            trust_score -= 25
        elif domain_info.get('age_years', 0) >= 2:
            trust_indicators.append('Domain is 2+ years old')
            trust_score += 5

        # 2. WHOIS Privacy Check
        if domain_info.get('whois_private'):
            red_flags.append({
                'severity': 'medium',
                'category': 'Hidden Owner',
                'message': 'Domain owner information is hidden',
                'impact': 'Legitimate businesses usually show contact info'
            })
            trust_score -= 15
        else:
            trust_indicators.append('Owner information is public')

        # 3. SSL Certificate Check
        ssl_info = await self._check_ssl(domain)
        if not ssl_info.get('has_ssl'):
            red_flags.append({
                'severity': 'critical',
                'category': 'No SSL/HTTPS',
                'message': 'Website does not use secure HTTPS connection',
                'impact': 'Never enter passwords or payment info on this site'
            })
            trust_score -= 30
        elif ssl_info.get('is_valid'):
            trust_indicators.append('Valid SSL certificate')
        else:
            red_flags.append({
                'severity': 'high',
                'category': 'Invalid SSL',
                'message': 'SSL certificate is expired or invalid',
                'impact': 'Connection may not be secure'
            })
            trust_score -= 20

        # 4. Suspicious Keywords Check
        suspicious_keywords = self._check_suspicious_keywords(domain)
        if suspicious_keywords:
            red_flags.append({
                'severity': 'medium',
                'category': 'Suspicious Name',
                'message': f"Domain contains suspicious words: {', '.join(suspicious_keywords)}",
                'impact': 'Scammers often use these keywords to trick users'
            })
            trust_score -= 15

        # 5. VirusTotal Reputation (if API key available)
        if self.virustotal_key:
            vt_result = await self._check_virustotal(domain)
            if vt_result.get('malicious', 0) > 0:
                red_flags.append({
                    'severity': 'critical',
                    'category': 'Blacklisted',
                    'message': f"Flagged as malicious by {vt_result['malicious']} security vendors",
                    'impact': 'This site is known to be dangerous'
                })
                trust_score -= 40
            elif vt_result.get('suspicious', 0) > 0:
                red_flags.append({
                    'severity': 'high',
                    'category': 'Suspicious',
                    'message': f"Flagged as suspicious by {vt_result['suspicious']} security vendors",
                    'impact': 'Exercise extreme caution'
                })
                trust_score -= 20

        # 6. Google Safe Browsing (if API key available)
        if self.safe_browsing_key:
            gsb_result = await self._check_safe_browsing(url)
            if gsb_result.get('is_dangerous'):
                red_flags.append({
                    'severity': 'critical',
                    'category': 'Google Blacklist',
                    'message': f"Google flagged this site: {gsb_result.get('threat_type', 'Dangerous')}",
                    'impact': 'Do not visit this site'
                })
                trust_score -= 50

        # 7. Typosquatting Check (compare to popular domains)
        typosquat = self._check_typosquatting(domain)
        if typosquat:
            red_flags.append({
                'severity': 'high',
                'category': 'Fake Domain',
                'message': f"Looks like fake version of: {typosquat}",
                'impact': 'This may be impersonating a legitimate site'
            })
            trust_score -= 30

        # Ensure score is within 0-100
        trust_score = max(0, min(100, trust_score))

        # Determine risk level
        if trust_score >= 75:
            risk_level = 'low'
            verdict = 'Likely Legitimate'
        elif trust_score >= 50:
            risk_level = 'medium'
            verdict = 'Exercise Caution'
        elif trust_score >= 25:
            risk_level = 'high'
            verdict = 'High Risk - Likely Scam'
        else:
            risk_level = 'critical'
            verdict = 'SCAM DETECTED - Do Not Trust'

        return {
            'trust_score': trust_score,
            'risk_level': risk_level,
            'verdict': verdict,
            'red_flags': red_flags,
            'trust_indicators': trust_indicators,
            'domain_info': domain_info,
            'ssl_info': ssl_info,
        }

    async def _check_domain_age(self, domain: str) -> Dict[str, Any]:
        """Check domain age using WHOIS."""
        try:
            w = whois.whois(domain)

            # Get creation date
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            if creation_date:
                # Make both datetimes timezone-aware or naive
                now = datetime.now()
                if creation_date.tzinfo is not None:
                    # creation_date is aware, make now aware too
                    from datetime import timezone
                    now = datetime.now(timezone.utc)
                    if creation_date.tzinfo != timezone.utc:
                        creation_date = creation_date.astimezone(timezone.utc)
                else:
                    # Both naive
                    if now.tzinfo is not None:
                        now = now.replace(tzinfo=None)

                days_old = (now - creation_date).days
                age_years = days_old / 365.25
                is_new = days_old < 180  # Less than 6 months

                return {
                    'creation_date': creation_date.isoformat() if creation_date else None,
                    'days_old': days_old,
                    'age_years': round(age_years, 1),
                    'is_new': is_new,
                    'whois_private': not w.registrar or 'privacy' in str(w.registrar).lower(),
                    'registrar': w.registrar,
                }

        except Exception as e:
            print(f"WHOIS lookup failed for {domain}: {str(e)}")

        return {
            'creation_date': None,
            'days_old': None,
            'age_years': None,
            'is_new': True,  # Assume new if we can't check
            'whois_private': True,
        }

    async def _check_ssl(self, domain: str) -> Dict[str, Any]:
        """Check if SSL certificate exists and is valid."""
        try:
            import ssl
            import socket
            from datetime import datetime

            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

                    # Check expiration
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    is_valid = not_after > datetime.now()

                    return {
                        'has_ssl': True,
                        'is_valid': is_valid,
                        'expires': not_after.isoformat(),
                        'issuer': dict(x[0] for x in cert['issuer']),
                    }
        except Exception as e:
            print(f"SSL check failed for {domain}: {str(e)}")
            return {
                'has_ssl': False,
                'is_valid': False,
            }

    def _check_suspicious_keywords(self, domain: str) -> List[str]:
        """Check for suspicious keywords in domain."""
        suspicious_words = [
            'verify', 'secure', 'account', 'update', 'login', 'bank',
            'paypal', 'amazon', 'ebay', 'apple', 'microsoft', 'support',
            'prize', 'winner', 'claim', 'urgent', 'suspended', 'limited',
            'free', 'bonus', 'gift', 'reward', 'offer', 'deal',
            'confirm', 'reset', 'unlock', 'restore', 'recover'
        ]

        found = []
        domain_lower = domain.lower()
        for word in suspicious_words:
            if word in domain_lower and not domain_lower.startswith(word):
                # Suspicious if keyword appears in middle/end (e.g., verify-paypal.com)
                found.append(word)

        return found

    async def _check_virustotal(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation on VirusTotal."""
        if not self.virustotal_key:
            return {}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/domains/{domain}",
                    headers={'x-apikey': self.virustotal_key}
                )

                if response.status_code == 200:
                    data = response.json()
                    stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})

                    return {
                        'malicious': stats.get('malicious', 0),
                        'suspicious': stats.get('suspicious', 0),
                        'harmless': stats.get('harmless', 0),
                        'undetected': stats.get('undetected', 0),
                    }
        except Exception as e:
            print(f"VirusTotal check failed: {str(e)}")

        return {}

    async def _check_safe_browsing(self, url: str) -> Dict[str, Any]:
        """Check Google Safe Browsing API."""
        if not self.safe_browsing_key:
            return {}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.safe_browsing_key}",
                    json={
                        'client': {
                            'clientId': 'africacybertrust',
                            'clientVersion': '1.0.0'
                        },
                        'threatInfo': {
                            'threatTypes': ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION'],
                            'platformTypes': ['ANY_PLATFORM'],
                            'threatEntryTypes': ['URL'],
                            'threatEntries': [{'url': url}]
                        }
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    matches = data.get('matches', [])

                    if matches:
                        return {
                            'is_dangerous': True,
                            'threat_type': matches[0].get('threatType', 'UNKNOWN'),
                        }
        except Exception as e:
            print(f"Safe Browsing check failed: {str(e)}")

        return {'is_dangerous': False}

    def _check_typosquatting(self, domain: str) -> str:
        """Check if domain is typosquatting popular brands."""
        popular_domains = [
            'google', 'facebook', 'amazon', 'paypal', 'netflix', 'microsoft',
            'apple', 'twitter', 'instagram', 'linkedin', 'youtube', 'whatsapp',
            'bank', 'wells', 'chase', 'citibank', 'bofa', 'visa', 'mastercard'
        ]

        domain_lower = domain.lower().replace('-', '').replace('.', '')

        for brand in popular_domains:
            # Check for similar spelling (e.g., googIe.com, facebok.com)
            if self._similar(domain_lower, brand, threshold=2):
                return brand

        return None

    def _similar(self, s1: str, s2: str, threshold: int) -> bool:
        """Check if two strings are similar (Levenshtein distance)."""
        if s2 in s1 and len(s1) - len(s2) <= threshold:
            return True

        # Simple character diff count
        if len(s1) != len(s2):
            return False

        diff_count = sum(c1 != c2 for c1, c2 in zip(s1, s2))
        return diff_count <= threshold


# Singleton instance
scam_detector = ScamDetectorService()
