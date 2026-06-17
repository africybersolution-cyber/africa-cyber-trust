"""WhatsApp notification service using Twilio."""
from twilio.rest import Client
from typing import Optional
from app.core.config import settings


class WhatsAppService:
    """Service for sending WhatsApp notifications to agents."""

    def __init__(self):
        """Initialize Twilio client."""
        # Twilio credentials (set in environment)
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.whatsapp_from = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')  # Twilio sandbox default

        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("[WARNING] Twilio credentials not set - WhatsApp notifications disabled")

    def send_message(self, to_number: str, message: str) -> dict:
        """
        Send WhatsApp message to a phone number.

        Args:
            to_number: Phone number in format +1234567890
            message: Message text to send

        Returns:
            dict with success status and message_sid or error
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twilio not configured"
            }

        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            message_obj = self.client.messages.create(
                from_=self.whatsapp_from,
                body=message,
                to=to_number
            )

            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status
            }

        except Exception as e:
            print(f"[ERROR] WhatsApp send failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ===== MESSAGE TEMPLATES =====

    def send_agent_approved(self, to_number: str, agent_name: str, referral_code: str) -> dict:
        """Send approval notification."""
        message = f"""🎉 *Congratulations {agent_name}!*

Your agent application has been approved!

*Your Referral Code:* {referral_code}

*Next Steps:*
1. Complete required training courses
2. Start referring customers
3. Earn commissions (15-25%)

*Commission Tiers:*
🥉 Bronze: 15% ($0-500/mo)
🥈 Silver: 20% ($501-2000/mo)
🥇 Gold: 25% ($2001+/mo)

Welcome to the team! 🚀"""

        return self.send_message(to_number, message)

    def send_commission_earned(self, to_number: str, agent_name: str, amount: float, customer_email: str) -> dict:
        """Send commission notification."""
        message = f"""💰 *New Commission Earned!*

Hi {agent_name},

You just earned *${amount:.2f}* from a referral!

*Customer:* {customer_email}
*Your Balance:* Check dashboard for total

Keep up the great work! 🎯"""

        return self.send_message(to_number, message)

    def send_payout_processed(self, to_number: str, agent_name: str, amount: float, method: str) -> dict:
        """Send payout confirmation."""
        message = f"""✅ *Payout Processed*

Hi {agent_name},

Your payout of *${amount:.2f}* has been processed!

*Method:* {method}
*Status:* Completed

The funds should arrive within 1-3 business days.

Thanks for being an amazing agent! 🌟"""

        return self.send_message(to_number, message)

    def send_fraud_alert(self, to_number: str, agent_name: str, reason: str) -> dict:
        """Send fraud alert notification."""
        message = f"""⚠️ *Account Review*

Hi {agent_name},

Your account is under review for the following reason:

*{reason}*

Please contact support immediately to resolve this issue.

*Support:* africybersolution@gmail.com"""

        return self.send_message(to_number, message)

    def send_monthly_summary(self, to_number: str, agent_name: str, total_sales: float, commissions: float, customers: int) -> dict:
        """Send monthly performance summary."""
        message = f"""📊 *Monthly Performance Summary*

Hi {agent_name},

Here's your performance for the month:

*Total Sales:* ${total_sales:.2f}
*Commissions Earned:* ${commissions:.2f}
*New Customers:* {customers}

Keep up the excellent work! 💪

View detailed stats in your dashboard."""

        return self.send_message(to_number, message)

    def send_training_reminder(self, to_number: str, agent_name: str, course_title: str) -> dict:
        """Send training course reminder."""
        message = f"""📚 *Training Reminder*

Hi {agent_name},

You have an incomplete required course:

*{course_title}*

Please complete it to activate your agent account and start earning commissions.

Login to complete: [Dashboard Link]"""

        return self.send_message(to_number, message)

    def send_agent_rejected(self, to_number: str, agent_name: str, reason: str) -> dict:
        """Send agent application rejection notification."""
        message = f"""❌ *Application Update*

Hi {agent_name},

Unfortunately, your agent application has been rejected.

*Reason:* {reason}

You may reapply after addressing the concerns mentioned above.

For questions, contact: africybersolution@gmail.com"""

        return self.send_message(to_number, message)

    def send_payout_rejected(self, to_number: str, agent_name: str, amount: float, reason: str) -> dict:
        """Send payout rejection notification."""
        message = f"""⚠️ *Payout Request Rejected*

Hi {agent_name},

Your payout request of *${amount:.2f}* has been rejected.

*Reason:* {reason}

Please contact support if you have questions.

*Support:* africybersolution@gmail.com"""

        return self.send_message(to_number, message)


# Singleton instance
whatsapp_service = WhatsAppService()
