"""Email service for sending verification emails."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailService:
    """Service for sending emails."""

    # Gmail SMTP settings (configured for production)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "africybersolution@gmail.com"
    SENDER_PASSWORD = "mwqwbdrywmsezcuh"  # Gmail App Password (spaces removed)

    @staticmethod
    def send_verification_email(
        to_email: str,
        domain: str,
        verification_link: str
    ) -> bool:
        """Send domain verification email."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Verify your domain: {domain}"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["To"] = to_email

            # Email HTML content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%);
                              color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                    .content {{ background: #f9f9f9; padding: 30px; margin: 20px 0; border-radius: 10px; }}
                    .button {{ display: inline-block; background: #0047AB; color: white;
                              padding: 15px 40px; text-decoration: none; border-radius: 8px;
                              font-weight: bold; margin: 20px 0; }}
                    .button:hover {{ background: #1E90FF; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🛡️ Domain Verification</h1>
                    </div>

                    <div class="content">
                        <h2>Verify {domain}</h2>
                        <p>Hello,</p>
                        <p>You've added <strong>{domain}</strong> to Africa Cyber Trust Infrastructure
                           for security monitoring.</p>
                        <p>Click the button below to verify that you own this domain:</p>

                        <center>
                            <a href="{verification_link}" class="button">
                                Verify Domain Ownership
                            </a>
                        </center>

                        <p><strong>This link will expire in 24 hours.</strong></p>

                        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                            If you didn't request this verification, you can safely ignore this email.
                        </p>
                    </div>

                    <div class="footer">
                        <p>© 2026 Africa Cyber Trust Infrastructure</p>
                        <p>Building trusted digital infrastructure for Africa</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text fallback
            text = f"""
            Domain Verification - Africa Cyber Trust Infrastructure

            You've added {domain} for security monitoring.

            Click this link to verify domain ownership:
            {verification_link}

            This link will expire in 24 hours.

            If you didn't request this, ignore this email.

            © 2026 Africa Cyber Trust Infrastructure
            """

            # Attach both HTML and plain text versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            # Send email (only if SMTP credentials are configured)
            if not EmailService.SENDER_PASSWORD:
                print(f"[DEMO MODE] Would send verification email to: {to_email}")
                print(f"Verification link: {verification_link}")
                return True

            # Send via SMTP
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.send_message(message)

            return True

        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_security_alert(
        to_email: str,
        asset_name: str,
        asset_url: str,
        security_score: int,
        critical_count: int,
        high_count: int,
        findings: list
    ) -> bool:
        """Send security alert notification."""
        try:
            from datetime import datetime

            message = MIMEMultipart("alternative")
            message["Subject"] = f"🚨 Security Alert - {asset_name}"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["To"] = to_email

            # Build findings HTML
            findings_html = ""
            for finding in findings[:5]:  # Top 5 issues
                severity_colors = {
                    'critical': '#DC2626',
                    'high': '#F97316',
                    'medium': '#EAB308',
                    'low': '#3B82F6'
                }
                color = severity_colors.get(finding.get('severity', 'low'), '#6B7280')

                findings_html += f"""
                <div style="margin: 15px 0; padding: 15px; border-left: 4px solid {color}; background-color: #F9FAFB; border-radius: 4px;">
                    <div style="margin-bottom: 8px;">
                        <span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-right: 10px;">
                            {finding.get('severity', 'unknown')}
                        </span>
                        <span style="color: #6B7280; font-size: 12px;">{finding.get('category', 'Security')}</span>
                    </div>
                    <h4 style="margin: 8px 0; color: #111827;">{finding.get('title', 'Security Issue')}</h4>
                    <p style="margin: 8px 0; color: #4B5563; font-size: 13px;">{finding.get('description', '')}</p>
                    <p style="margin: 8px 0; color: #059669; font-size: 13px;">
                        <strong>✓ Fix:</strong> {finding.get('recommendation', 'Review and address')}
                    </p>
                </div>
                """

            score_color = '#DC2626' if security_score < 40 else '#F97316' if security_score < 60 else '#EAB308' if security_score < 80 else '#10B981'

            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF;">
                    <div style="background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%); padding: 30px 20px; text-align: center;">
                        <h1 style="color: #FFFFFF; margin: 0; font-size: 24px;">🛡️ AFRICA CYBER TRUST</h1>
                        <p style="color: #E0E7FF; margin: 10px 0 0 0;">Security Alert</p>
                    </div>
                    <div style="padding: 30px 20px;">
                        <div style="background-color: #FEF2F2; border-left: 4px solid #DC2626; padding: 15px; margin-bottom: 25px;">
                            <p style="margin: 0; color: #991B1B; font-weight: bold;">⚠️ Security issues detected on {asset_name}</p>
                        </div>
                        <table style="width: 100%; margin-bottom: 25px; border-collapse: collapse;">
                            <tr><td style="padding: 10px 0; border-bottom: 1px solid #E5E7EB;"><strong>Asset:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #E5E7EB; text-align: right;">{asset_name}</td></tr>
                            <tr><td style="padding: 10px 0; border-bottom: 1px solid #E5E7EB;"><strong>URL:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #E5E7EB; text-align: right;">{asset_url}</td></tr>
                            <tr><td style="padding: 10px 0; border-bottom: 1px solid #E5E7EB;"><strong>Security Score:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #E5E7EB; text-align: right;"><span style="color: {score_color}; font-weight: bold; font-size: 20px;">{security_score}/100</span></td></tr>
                            <tr><td style="padding: 10px 0;"><strong>Issues Found:</strong></td><td style="padding: 10px 0; text-align: right;"><span style="color: #DC2626; font-weight: bold;">{critical_count} Critical</span>, <span style="color: #F97316; font-weight: bold;">{high_count} High</span></td></tr>
                        </table>
                        <h2 style="color: #111827; margin: 30px 0 15px 0; font-size: 18px;">Security Issues Detected</h2>
                        {findings_html}
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:3001/dashboard/assets" style="background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%); color: #FFFFFF; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">View Full Report →</a>
                        </div>
                        <div style="background-color: #EFF6FF; padding: 15px; border-radius: 8px; margin-top: 25px;">
                            <p style="margin: 0; color: #1E40AF; font-size: 13px;">
                                <strong>💡 Recommendation:</strong> Address critical and high severity issues immediately.
                            </p>
                        </div>
                    </div>
                    <div style="background-color: #F9FAFB; padding: 20px; text-align: center; border-top: 1px solid #E5E7EB;">
                        <p style="margin: 0 0 10px 0; color: #6B7280; font-size: 12px;">
                            Scan: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                        </p>
                        <p style="margin: 0; color: #9CA3AF; font-size: 11px;">© {datetime.now().year} Africa Cyber Trust. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text = f"""
Security Alert - Africa Cyber Trust

Asset: {asset_name}
URL: {asset_url}
Security Score: {security_score}/100
Issues: {critical_count} Critical, {high_count} High

Security issues have been detected on your asset. Please review the full report at:
http://localhost:3001/dashboard/assets

© {datetime.now().year} Africa Cyber Trust
            """

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            # Send via SMTP
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.send_message(message)

            print(f"✅ Security alert sent to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send security alert: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(
        to_email: str,
        reset_link: str
    ) -> bool:
        """Send password reset email."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Password - Africa Cyber Trust"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["To"] = to_email

            # Email HTML content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0047AB 0%, #DAA520 100%);
                              color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                    .content {{ background: #f9f9f9; padding: 30px; margin: 20px 0; border-radius: 10px; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #0047AB 0%, #DAA520 100%);
                              color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px;
                              font-weight: bold; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                    </div>

                    <div class="content">
                        <h2>Reset Your Password</h2>
                        <p>Hello,</p>
                        <p>You requested to reset your password for Africa Cyber Trust Infrastructure.</p>
                        <p>Click the button below to reset your password:</p>

                        <center>
                            <a href="{reset_link}" class="button">
                                Reset Password
                            </a>
                        </center>

                        <p><strong>This link will expire in 1 hour.</strong></p>

                        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                            If you didn't request this, please ignore this email.
                            Your password will remain unchanged.
                        </p>
                    </div>

                    <div class="footer">
                        <p>© 2026 Africa Cyber Trust Infrastructure</p>
                        <p>Building trusted digital infrastructure for Africa</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text fallback
            text = f"""
            Password Reset Request - Africa Cyber Trust Infrastructure

            You requested to reset your password.

            Click this link to reset your password:
            {reset_link}

            This link will expire in 1 hour.

            If you didn't request this, ignore this email.

            © 2026 Africa Cyber Trust Infrastructure
            """

            # Attach both HTML and plain text versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            # Send via SMTP
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.send_message(message)

            print(f"✅ Password reset email sent to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send password reset email: {str(e)}")
            return False


# Create singleton instance
email_service = EmailService()
