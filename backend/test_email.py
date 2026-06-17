"""Test email sending."""
import os
import sys
from dotenv import load_dotenv

# Load .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
print(f"Loading .env from: {env_path}")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService

# Check environment variables
print("=" * 60)
print("EMAIL CONFIGURATION CHECK")
print("=" * 60)

gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")
sendgrid_key = os.getenv("SENDGRID_API_KEY", "")

print(f"GMAIL_APP_PASSWORD: {'[SET]' if gmail_password else '[NOT SET]'}")
print(f"SENDGRID_API_KEY: {'[SET]' if sendgrid_key else '[NOT SET]'}")
print(f"Sender Email: {EmailService.SENDER_EMAIL}")
print()

if not gmail_password and not sendgrid_key:
    print("[ERROR] ERROR: No email credentials configured!")
    print()
    print("To fix this, set one of these environment variables:")
    print("1. GMAIL_APP_PASSWORD (for local testing)")
    print("2. SENDGRID_API_KEY (for production/Render)")
    print()
    print("How to get Gmail App Password:")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Sign in with: africybersolution@gmail.com")
    print("3. Create 'App Password' for 'Mail'")
    print("4. Copy the 16-character password")
    print("5. Set: $env:GMAIL_APP_PASSWORD='your-password-here'")
    print()
    sys.exit(1)

# Test sending email
print("Testing email send...")
test_email = "africybersolution@gmail.com"  # Send to self

try:
    result = EmailService.send_agent_credentials(
        to_email=test_email,
        agent_name="Test Agent",
        password="TestPassword123",
        referral_code="TEST1234",
        portal_url="http://localhost:3004"
    )

    if result:
        print(f"[SUCCESS] SUCCESS! Email sent to {test_email}")
        print("Check your inbox (and spam folder)")
    else:
        print("[ERROR] FAILED! Check error logs above")

except Exception as e:
    print(f"[ERROR] ERROR: {e}")
    import traceback
    traceback.print_exc()
