"""Test script to send a sample security alert email."""
import sys
sys.path.insert(0, 'backend')

from app.services.email_service import EmailService

# Test data
test_email = "africybersolution@gmail.com"  # User's email
asset_name = "ktravo.net"
asset_url = "https://ktravo.net"
security_score = 45  # Low score to show issues
critical_count = 2
high_count = 3

# Sample findings
findings = [
    {
        'severity': 'critical',
        'category': 'Security Headers',
        'title': 'Missing Security Headers',
        'description': 'Critical security headers (CSP, X-Frame-Options) are not configured',
        'recommendation': 'Add Content-Security-Policy and X-Frame-Options headers to protect against XSS and clickjacking'
    },
    {
        'severity': 'critical',
        'category': 'SSL/TLS',
        'title': 'Weak SSL Configuration',
        'description': 'SSL certificate uses weak encryption protocols (TLS 1.0/1.1)',
        'recommendation': 'Upgrade to TLS 1.2 or higher and disable weak cipher suites'
    },
    {
        'severity': 'high',
        'category': 'Web Security',
        'title': 'CORS Misconfiguration',
        'description': 'CORS policy allows requests from any origin (*), exposing API to unauthorized access',
        'recommendation': 'Configure CORS to only allow trusted domains'
    },
    {
        'severity': 'high',
        'category': 'Authentication',
        'title': 'No Rate Limiting',
        'description': 'Login endpoint has no rate limiting, vulnerable to brute force attacks',
        'recommendation': 'Implement rate limiting on authentication endpoints (max 5 attempts per minute)'
    },
    {
        'severity': 'high',
        'category': 'Data Exposure',
        'title': 'Sensitive Data in URLs',
        'description': 'API endpoints expose user IDs and session tokens in URL parameters',
        'recommendation': 'Move sensitive data to request headers or body instead of URL parameters'
    }
]

print("=" * 60)
print("TESTING SECURITY ALERT EMAIL")
print("=" * 60)
print(f"To: {test_email}")
print(f"Asset: {asset_name}")
print(f"Security Score: {security_score}/100")
print(f"Critical Issues: {critical_count}")
print(f"High Issues: {high_count}")
print("=" * 60)
print("\nSending email...")

# Send test alert
result = EmailService.send_security_alert(
    to_email=test_email,
    asset_name=asset_name,
    asset_url=asset_url,
    security_score=security_score,
    critical_count=critical_count,
    high_count=high_count,
    findings=findings
)

if result:
    print("\n[SUCCESS] Security alert email sent!")
    print(f"          Check inbox: {test_email}")
    print("\nLook for: 'Security Alert - ktravo.net'")
    print("Also check spam folder if not in inbox!")
else:
    print("\n[FAILED] Check error message above.")

print("=" * 60)
