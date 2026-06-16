"""Test verification email sending locally."""
import sys
sys.path.insert(0, 'C:/Users/Admin/africa-cyber-trust/backend')

from app.services.email_service import EmailService

print("=" * 60)
print("Testing Verification Email")
print("=" * 60)

# Test data
test_email = "admin@ktravo.net"
test_domain = "ktravo.net"
test_link = "https://www.africybertrust.com/verify-asset?asset=test123&token=test456"

print(f"\nSending verification email to: {test_email}")
print(f"Domain: {test_domain}")
print(f"Link: {test_link}")
print("\nAttempting to send...")

try:
    success = EmailService.send_verification_email(
        to_email=test_email,
        domain=test_domain,
        verification_link=test_link
    )

    if success:
        print("\n[SUCCESS] Email sent successfully!")
        print(f"Check {test_email} inbox for the verification email.")
    else:
        print("\n[FAILED] Email service returned False")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
