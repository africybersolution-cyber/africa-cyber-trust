"""
Test email service with real SMTP configuration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import email_service


def test_email_sending():
    """Test sending a real verification email."""
    print("=" * 60)
    print("EMAIL SERVICE TEST - REAL SMTP")
    print("=" * 60)
    print()

    # Test email address (change this to your test email)
    test_email = "admin@ktravo.net"  # Change to your email for testing
    test_domain = "ktravo.net"
    test_link = "http://localhost:3001/verify?asset=test123&token=test456"

    print(f"Testing email sending to: {test_email}")
    print(f"Domain: {test_domain}")
    print()

    try:
        print("Sending email...")
        success = email_service.send_verification_email(
            to_email=test_email,
            domain=test_domain,
            verification_link=test_link
        )

        if success:
            print()
            print("=" * 60)
            print("EMAIL SENT SUCCESSFULLY!")
            print("=" * 60)
            print()
            print(f"Check inbox: {test_email}")
            print("Subject: Verify your domain: ktravo.net")
            print()
            print("If you don't see it:")
            print("  1. Check spam/junk folder")
            print("  2. Wait 1-2 minutes")
            print("  3. Check email address is correct")
            print()
            return True
        else:
            print()
            print("[ERROR] Email sending failed!")
            return False

    except Exception as e:
        print()
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_email_sending()
    sys.exit(0 if success else 1)
