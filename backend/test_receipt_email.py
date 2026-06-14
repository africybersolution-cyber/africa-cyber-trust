"""Test script to send a sample payment receipt email."""
import sys
sys.path.insert(0, 'backend')

from app.services.email_service import EmailService
from datetime import datetime, timedelta

# Test data
test_email = "admin@ktravo.net"  # Your test email
payment_id = "550e8400-e29b-41d4-a716-446655440000"
plan_name = "professional"
amount = "69000"
currency = "RWF"
payment_method = "Mobile Money (MTN)"
payment_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
subscription_expires = (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")

print("=" * 60)
print("TESTING PAYMENT RECEIPT EMAIL")
print("=" * 60)
print(f"To: {test_email}")
print(f"Plan: {plan_name}")
print(f"Amount: {amount} {currency}")
print(f"Payment Method: {payment_method}")
print("=" * 60)
print("\nSending email...")

# Send test receipt
result = EmailService.send_payment_receipt(
    to_email=test_email,
    payment_id=payment_id,
    plan_name=plan_name,
    amount=amount,
    currency=currency,
    payment_method=payment_method,
    payment_date=payment_date,
    subscription_expires=subscription_expires
)

if result:
    print("\n[SUCCESS] Check your email inbox:")
    print(f"          {test_email}")
    print("\nLook for: 'Payment Receipt - Africa Cyber Trust'")
    print("Also check spam folder if not in inbox!")
else:
    print("\n[FAILED] Check error message above.")

print("=" * 60)
