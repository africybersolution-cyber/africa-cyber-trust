"""Test SendGrid security alert email directly."""
import os

# You need to set your SendGrid API key here temporarily for testing
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY") or input("Enter SendGrid API Key (or press Enter to skip): ").strip()

if not SENDGRID_API_KEY:
    print("⚠️  No SendGrid API key provided. Skipping SendGrid test.")
    print("   Set SENDGRID_API_KEY environment variable or enter when prompted.")
    exit(0)

# Set it for the test
os.environ["SENDGRID_API_KEY"] = SENDGRID_API_KEY

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Test data
test_email = "africybersolution@gmail.com"
asset_name = "ktravo.net"

print("=" * 60)
print("TESTING SENDGRID SECURITY ALERT")
print("=" * 60)
print(f"API Key: {SENDGRID_API_KEY[:10]}..." if len(SENDGRID_API_KEY) > 10 else "INVALID")
print(f"To: {test_email}")
print(f"Asset: {asset_name}")
print("=" * 60)

# Simple HTML content
html_content = """
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%); padding: 30px; text-align: center; color: white;">
            <h1>AFRICA CYBER TRUST</h1>
            <p>Security Alert</p>
        </div>
        <div style="padding: 30px;">
            <h2>Security Alert - ktravo.net</h2>
            <p><strong>Security Score:</strong> 45/100</p>
            <p><strong>Issues:</strong> 2 Critical, 3 High</p>
            <p>Security issues detected on your asset.</p>
            <a href="https://www.africybertrust.com/dashboard" style="background: #0047AB; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">View Report</a>
        </div>
    </div>
</body>
</html>
"""

text_content = """
Security Alert - Africa Cyber Trust

Asset: ktravo.net
Security Score: 45/100
Issues: 2 Critical, 3 High

View your dashboard: https://www.africybertrust.com/dashboard
"""

try:
    print("\nSending via SendGrid...")

    message = Mail(
        from_email=Email("africybersolution@gmail.com", "Africa Cyber Trust"),
        to_emails=To(test_email),
        subject=f"Security Alert - {asset_name}",
        plain_text_content=Content("text/plain", text_content),
        html_content=Content("text/html", html_content)
    )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)

    print(f"\n✓ SUCCESS! Status: {response.status_code}")
    print(f"✓ SendGrid accepted the email")
    print(f"\nCheck inbox: {test_email}")
    print("Subject: 'Security Alert - ktravo.net'")
    print("\nIf it doesn't arrive in 1-2 minutes:")
    print("  1. Check spam folder")
    print("  2. Check SendGrid activity log")
    print("  3. Verify sender domain authentication")

except Exception as e:
    print(f"\n✗ FAILED: {str(e)}")
    print(f"Error type: {type(e).__name__}")

print("=" * 60)
