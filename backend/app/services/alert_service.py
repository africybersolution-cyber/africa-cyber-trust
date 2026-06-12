"""Alert notification service for sending emails and SMS."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import httpx
import africastalking

from app.models.alert import Alert, AlertSettings
from app.models.user import User
from app.core.config import settings


class AlertService:
    """Service for sending alert notifications."""

    # Email configuration (Gmail SMTP)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_EMAIL = "africybersolution@gmail.com"
    SMTP_PASSWORD = "mwqwbdrywmsezcuh"  # Gmail app password (same as verification emails)

    # Africa's Talking configuration
    @staticmethod
    def _init_africastalking():
        """Initialize Africa's Talking SDK."""
        if settings.AFRICASTALKING_API_KEY:
            africastalking.initialize(
                username=settings.AFRICASTALKING_USERNAME,
                api_key=settings.AFRICASTALKING_API_KEY
            )

    @staticmethod
    def send_email(to_email: str, subject: str, html_body: str) -> bool:
        """Send email via Gmail SMTP."""
        try:
            if not AlertService.SMTP_PASSWORD:
                print("[ALERT] WARNING: Gmail app password not configured")
                return False

            msg = MIMEMultipart('alternative')
            msg['From'] = AlertService.SMTP_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(AlertService.SMTP_SERVER, AlertService.SMTP_PORT) as server:
                server.starttls()
                server.login(AlertService.SMTP_EMAIL, AlertService.SMTP_PASSWORD)
                server.send_message(msg)

            print(f"[ALERT] Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"[ALERT] Email failed: {str(e)}")
            return False

    @staticmethod
    async def send_sms(phone_number: str, message: str) -> bool:
        """Send SMS via Africa's Talking."""
        try:
            if not settings.AFRICASTALKING_API_KEY:
                print("[ALERT] WARNING: Africa's Talking API key not configured")
                return False

            AlertService._init_africastalking()
            sms = africastalking.SMS

            response = sms.send(
                message=message,
                recipients=[phone_number],
                sender_id=settings.AFRICASTALKING_FROM
            )

            print(f"[ALERT] SUCCESS SMS sent to {phone_number}")
            print(f"   Response: {response}")
            return True

        except Exception as e:
            print(f"[ALERT] ERROR SMS failed: {str(e)}")
            return False

    @staticmethod
    async def send_whatsapp(phone_number: str, message: str) -> bool:
        """Send WhatsApp message via Africa's Talking."""
        try:
            if not settings.AFRICASTALKING_API_KEY:
                print("[ALERT] WARNING: Africa's Talking API key not configured")
                return False

            AlertService._init_africastalking()

            # Africa's Talking requires phone numbers in international format (e.g., +254712345678)
            if not phone_number.startswith('+'):
                print(f"[ALERT] WARNING: Phone number must start with + for WhatsApp: {phone_number}")
                return False

            # Use SMS endpoint for WhatsApp (Africa's Talking handles routing)
            sms = africastalking.SMS
            response = sms.send(
                message=message,
                recipients=[phone_number],
                sender_id=settings.AFRICASTALKING_FROM
            )

            print(f"[ALERT] SUCCESS WhatsApp sent to {phone_number}")
            print(f"   Response: {response}")
            return True

        except Exception as e:
            print(f"[ALERT] ERROR WhatsApp failed: {str(e)}")
            return False

    @staticmethod
    async def send_slack(webhook_url: str, message: Dict[str, Any]) -> bool:
        """Send Slack notification."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=message)
                return response.status_code == 200
        except Exception as e:
            print(f"[ALERT] ERROR Slack failed: {str(e)}")
            return False

    @staticmethod
    def create_alert_email_html(severity: str, title: str, message: str, asset_name: Optional[str] = None) -> str:
        """Generate HTML email for alert."""
        severity_colors = {
            'critical': '#DC2626',  # Red
            'high': '#F59E0B',      # Orange
            'medium': '#3B82F6',    # Blue
            'low': '#10B981'        # Green
        }

        color = severity_colors.get(severity, '#6B7280')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0047AB 0%, #DAA520 100%);
                          color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .alert-box {{ border-left: 5px solid {color}; padding: 20px;
                             background-color: #f9fafb; margin: 20px 0; }}
                .severity {{ background-color: {color}; color: white; padding: 5px 15px;
                            border-radius: 20px; display: inline-block; font-weight: bold; }}
                .footer {{ background-color: #f3f4f6; padding: 20px; text-align: center;
                          border-radius: 0 0 10px 10px; margin-top: 20px; }}
                .button {{ background-color: #0047AB; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Africa Cyber Trust</h1>
                    <p>Security Alert</p>
                </div>

                <div class="alert-box">
                    <p><span class="severity">{severity.upper()}</span></p>
                    <h2>{title}</h2>
                    {f'<p><strong>Asset:</strong> {asset_name}</p>' if asset_name else ''}
                    <p>{message}</p>
                    <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>

                <p style="text-align: center;">
                    <a href="https://africacybertrust.com/dashboard" class="button">View Dashboard</a>
                </p>

                <div class="footer">
                    <p style="color: #6b7280; font-size: 14px;">
                        You're receiving this because you have email alerts enabled in your Africa Cyber Trust account.
                    </p>
                    <p style="color: #6b7280; font-size: 12px;">
                        <a href="https://africacybertrust.com/dashboard/alerts">Manage Alert Settings</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    async def send_alert(
        db: Session,
        user: User,
        severity: str,
        title: str,
        message: str,
        asset_id: Optional[str] = None,
        asset_name: Optional[str] = None,
        scan_id: Optional[str] = None,
        vulnerability_id: Optional[str] = None
    ) -> Alert:
        """
        Create alert and send notifications based on user settings.

        Args:
            db: Database session
            user: User to send alert to
            severity: 'critical', 'high', 'medium', 'low'
            title: Alert title
            message: Alert message body
            asset_id: Optional asset UUID
            asset_name: Optional asset name
            scan_id: Optional scan UUID
            vulnerability_id: Optional vulnerability ID

        Returns:
            Created Alert object
        """
        # Get user's alert settings
        settings = db.query(AlertSettings).filter(AlertSettings.user_id == user.id).first()

        # Create default settings if not exists
        if not settings:
            settings = AlertSettings(
                user_id=user.id,
                email_address=user.email
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)

        # Create alert record
        alert = Alert(
            user_id=user.id,
            severity=severity,
            title=title,
            message=message,
            asset_id=asset_id,
            asset_name=asset_name,
            scan_id=scan_id,
            vulnerability_id=vulnerability_id
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Check if this severity level should trigger notification
        severity_enabled = {
            'critical': settings.critical_issues,
            'high': settings.high_issues,
            'medium': settings.medium_issues,
            'low': settings.low_issues
        }.get(severity, False)

        if not severity_enabled:
            print(f"[ALERT] Severity '{severity}' disabled for user {user.email}")
            return alert

        # Send email if enabled
        if settings.email_enabled:
            email = settings.email_address or user.email
            html = AlertService.create_alert_email_html(severity, title, message, asset_name)

            if AlertService.send_email(email, f"[{severity.upper()}] {title}", html):
                alert.email_sent = True
                alert.email_sent_at = datetime.utcnow()

        # Send SMS if enabled
        if settings.sms_enabled and settings.phone_number:
            sms_message = f"[{severity.upper()}] {title}: {message[:100]}"
            if await AlertService.send_sms(settings.phone_number, sms_message):
                alert.sms_sent = True
                alert.sms_sent_at = datetime.utcnow()

        # Send WhatsApp if enabled
        if settings.whatsapp_enabled and settings.phone_number:
            wa_message = f"🛡️ *Africa Cyber Trust Alert*\n\n*[{severity.upper()}]* {title}\n\n{message}"
            if asset_name:
                wa_message += f"\n\n*Asset:* {asset_name}"
            wa_message += f"\n\n_Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC_"

            await AlertService.send_whatsapp(settings.phone_number, wa_message)

        # Send Slack if enabled
        if settings.slack_enabled and settings.slack_webhook_url:
            slack_msg = {
                "text": f"🚨 *{title}*",
                "attachments": [{
                    "color": "#DC2626" if severity == 'critical' else "#F59E0B",
                    "fields": [
                        {"title": "Severity", "value": severity.upper(), "short": True},
                        {"title": "Asset", "value": asset_name or "N/A", "short": True},
                        {"title": "Message", "value": message}
                    ]
                }]
            }
            await AlertService.send_slack(settings.slack_webhook_url, slack_msg)

        db.commit()
        return alert
