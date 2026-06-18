"""Email service for sending verification emails."""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False


class EmailService:
    """Service for sending emails."""

    # Gmail SMTP settings (fallback)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "africybersolution@gmail.com"
    # SECURITY: Password from environment variable (fallback for local dev only)
    SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

    # SendGrid API key (primary method - from environment variable)
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

    @staticmethod
    def send_verification_email(
        to_email: str,
        domain: str,
        verification_link: str
    ) -> bool:
        """Send domain verification email via SendGrid (primary) or SMTP (fallback)."""

        # Email HTML content
        html_content = f"""
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

        text_content = f"""
        Domain Verification - Africa Cyber Trust Infrastructure

        You've added {domain} for security monitoring.

        Click this link to verify domain ownership:
        {verification_link}

        This link will expire in 24 hours.

        If you didn't request this, ignore this email.

        © 2026 Africa Cyber Trust Infrastructure
        """

        # Try SendGrid first (works on Render)
        if SENDGRID_AVAILABLE and EmailService.SENDGRID_API_KEY:
            try:
                print(f"[EMAIL] Attempting to send via SendGrid to {to_email}")
                message = Mail(
                    from_email=Email(EmailService.SENDER_EMAIL, "Africa Cyber Trust"),
                    to_emails=To(to_email),
                    subject=f"Verify your domain: {domain}",
                    plain_text_content=Content("text/plain", text_content),
                    html_content=Content("text/html", html_content)
                )

                sg = SendGridAPIClient(EmailService.SENDGRID_API_KEY)
                response = sg.send(message)

                print(f"[EMAIL] SendGrid success! Status: {response.status_code}")
                return True

            except Exception as e:
                print(f"[EMAIL] SendGrid failed: {str(e)}")
                print(f"[EMAIL] Falling back to SMTP...")

        # Fallback to SMTP (works locally)
        try:
            print(f"[EMAIL] Attempting to send via SMTP to {to_email}")
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Verify your domain: {domain}"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["To"] = to_email

            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)

            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.send_message(message)

            print(f"[EMAIL] SMTP success!")
            return True

        except Exception as e:
            print(f"[EMAIL] Failed to send verification email to {to_email}: {str(e)}")
            print(f"        Error type: {type(e).__name__}")
            import traceback
            print(f"        Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def send_agent_credentials(
        to_email: str,
        agent_name: str,
        password: str,
        referral_code: str,
        portal_url: str = "http://localhost:3004"
    ) -> bool:
        """Send agent approval email with login credentials (same as payment receipts)."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Your Africa Cyber Trust Agent Account is Approved"
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
                .credentials {{ background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .code {{ background-color: #e5e7eb; padding: 4px 8px; border-radius: 4px; font-family: monospace; }}
                .button {{ display: inline-block; background: #0047AB; color: white;
                          padding: 15px 40px; text-decoration: none; border-radius: 8px;
                          font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                    <p>Your Agent Application is Approved</p>
                </div>
                <div class="content">
                    <h2>Welcome {agent_name}!</h2>
                    <p>Your application to become an Africa Cyber Trust agent has been <strong>approved</strong>! You can now start earning commissions by referring customers to our cybersecurity services.</p>
                    <div class="credentials">
                        <h3>Your Login Credentials:</h3>
                        <p><strong>Email:</strong> {to_email}</p>
                        <p><strong>Password:</strong> <span class="code">{password}</span></p>
                        <p><strong>Your Referral Code:</strong> <span class="code" style="background-color: #dbeafe; color: #1e40af; font-weight: bold;">{referral_code}</span></p>
                    </div>
                    <a href="{portal_url}" class="button">Access Agent Portal</a>
                    <h3>What's Next?</h3>
                    <ul>
                        <li>Log in to your agent portal using the credentials above</li>
                        <li>Complete the training courses to learn how to be a successful agent</li>
                        <li>Start referring customers and earning commissions!</li>
                        <li>Share your referral code to build your network</li>
                    </ul>
                    <p style="margin-top: 30px;"><strong>Welcome to the Africa Cyber Trust agent network!</strong></p>
                </div>
                <p style="color: #6b7280; font-size: 12px; text-align: center;">
                    This email was sent by Africa Cyber Trust. If you did not apply to become an agent, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """

            # Plain text fallback
            text = f"""
Congratulations {agent_name}! Your Africa Cyber Trust agent application is approved.

Login Credentials:
Email: {to_email}
Password: {password}
Referral Code: {referral_code}

Access the agent portal: {portal_url}

Next steps:
- Log in using the credentials above
- Complete the training courses
- Start referring customers and earning commissions
- Share your referral code to build your network

Welcome to the Africa Cyber Trust agent network!
"""

            # Attach both HTML and plain text versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            # Send via SMTP (same as payment receipts)
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.send_message(message)

            print(f"[EMAIL] Agent credentials sent to {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] Failed to send agent credentials: {str(e)}")
            print(f"        Error details: {type(e).__name__}")
            import traceback
            print(f"        Traceback: {traceback.format_exc()}")
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
        """Send security alert notification via SendGrid (primary) or SMTP (fallback)."""
        from datetime import datetime

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
                    <strong>Fix:</strong> {finding.get('recommendation', 'Review and address')}
                </p>
            </div>
            """

        score_color = '#DC2626' if security_score < 40 else '#F97316' if security_score < 60 else '#EAB308' if security_score < 80 else '#10B981'

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF;">
                <div style="background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%); padding: 30px 20px; text-align: center;">
                    <h1 style="color: #FFFFFF; margin: 0; font-size: 24px;">AFRICA CYBER TRUST</h1>
                    <p style="color: #E0E7FF; margin: 10px 0 0 0;">Security Alert</p>
                </div>
                <div style="padding: 30px 20px;">
                    <div style="background-color: #FEF2F2; border-left: 4px solid #DC2626; padding: 15px; margin-bottom: 25px;">
                        <p style="margin: 0; color: #991B1B; font-weight: bold;">Security issues detected on {asset_name}</p>
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
                        <a href="https://www.africybertrust.com/dashboard/assets" style="background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%); color: #FFFFFF; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">View Full Report</a>
                    </div>
                    <div style="background-color: #EFF6FF; padding: 15px; border-radius: 8px; margin-top: 25px;">
                        <p style="margin: 0; color: #1E40AF; font-size: 13px;">
                            <strong>Recommendation:</strong> Address critical and high severity issues immediately.
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

        text_content = f"""
Security Alert - Africa Cyber Trust

Asset: {asset_name}
URL: {asset_url}
Security Score: {security_score}/100
Issues: {critical_count} Critical, {high_count} High

Security issues have been detected on your asset. Please review the full report at:
https://www.africybertrust.com/dashboard/assets

© {datetime.now().year} Africa Cyber Trust
        """

        # Try SendGrid first (works on Render, more reliable)
        if SENDGRID_AVAILABLE and EmailService.SENDGRID_API_KEY:
            try:
                print(f"[EMAIL] Attempting to send security alert via SendGrid to {to_email}")
                message = Mail(
                    from_email=Email(EmailService.SENDER_EMAIL, "Africa Cyber Trust"),
                    to_emails=To(to_email),
                    subject=f"Security Alert - {asset_name}",
                    plain_text_content=Content("text/plain", text_content),
                    html_content=Content("text/html", html_content)
                )

                sg = SendGridAPIClient(EmailService.SENDGRID_API_KEY)
                response = sg.send(message)

                print(f"[EMAIL] SendGrid success! Security alert sent. Status: {response.status_code}")
                return True

            except Exception as e:
                print(f"[EMAIL] SendGrid failed: {str(e)}")
                print(f"[EMAIL] Falling back to SMTP...")

        # Fallback to SMTP
        try:
            print(f"[EMAIL] Attempting to send security alert via SMTP to {to_email}")
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Security Alert - {asset_name}"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["Reply-To"] = EmailService.SENDER_EMAIL
            message["To"] = to_email

            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)

            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT, timeout=10) as server:
                server.set_debuglevel(0)
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                result = server.send_message(message)

                if result:
                    print(f"[EMAIL] Warning - Some recipients rejected: {result}")

            print(f"[EMAIL] SMTP success! Security alert sent to {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] Failed to send security alert: {str(e)}")
            print(f"        Error type: {type(e).__name__}")
            import traceback
            print(f"        Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def send_password_reset_email(
        to_email: str,
        reset_link: str
    ) -> bool:
        """Send password reset email via SendGrid (primary) or SMTP (fallback)."""

        # Email HTML content
        html_content = f"""
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
        text_content = f"""
        Password Reset Request - Africa Cyber Trust Infrastructure

        You requested to reset your password.

        Click this link to reset your password:
        {reset_link}

        This link will expire in 1 hour.

        If you didn't request this, ignore this email.

        © 2026 Africa Cyber Trust Infrastructure
        """

        # Try SendGrid first (works on Render)
        if SENDGRID_AVAILABLE and EmailService.SENDGRID_API_KEY:
            try:
                print(f"[EMAIL] Attempting to send password reset via SendGrid to {to_email}")
                message = Mail(
                    from_email=Email(EmailService.SENDER_EMAIL, "Africa Cyber Trust"),
                    to_emails=To(to_email),
                    subject="Reset Your Password - Africa Cyber Trust",
                    plain_text_content=Content("text/plain", text_content),
                    html_content=Content("text/html", html_content)
                )

                sg = SendGridAPIClient(EmailService.SENDGRID_API_KEY)
                response = sg.send(message)

                print(f"[EMAIL] SendGrid success! Password reset sent. Status: {response.status_code}")
                return True

            except Exception as e:
                print(f"[EMAIL] SendGrid failed: {str(e)}")
                print(f"[EMAIL] Falling back to SMTP...")

        # Fallback to SMTP (works locally)
        try:
            print(f"[EMAIL] Attempting to send password reset via SMTP to {to_email}")
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Password - Africa Cyber Trust"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["To"] = to_email

            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)

            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.send_message(message)

            print(f"[EMAIL] SMTP success! Password reset sent.")
            return True

        except Exception as e:
            print(f"[EMAIL] Failed to send password reset email: {str(e)}")
            print(f"        Error type: {type(e).__name__}")
            import traceback
            print(f"        Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def send_payment_receipt(
        to_email: str,
        payment_id: str,
        plan_name: str,
        amount: str,
        currency: str,
        payment_method: str,
        payment_date: str,
        subscription_expires: str
    ) -> bool:
        """Send payment receipt email after successful payment."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Payment Receipt - Africa Cyber Trust"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["To"] = to_email

            # Format plan name nicely
            plan_display = {
                'starter': 'Starter',
                'professional': 'Professional',
                'enterprise': 'Enterprise',
                'personal': 'Personal'  # Legacy plan
            }.get(plan_name, plan_name.title())

            # Email HTML content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0047AB 0%, #DAA520 100%);
                              color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .receipt-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                                    border: 2px solid #0047AB; }}
                    .row {{ display: flex; justify-content: space-between; padding: 12px 0;
                            border-bottom: 1px solid #eee; }}
                    .label {{ font-weight: bold; color: #666; }}
                    .value {{ color: #0047AB; font-weight: bold; }}
                    .total {{ font-size: 24px; color: #0047AB; font-weight: bold; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #0047AB 0%, #DAA520 100%);
                              color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px;
                              font-weight: bold; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                    .success-box {{ background: #EFF6FF; padding: 15px; border-radius: 8px; margin-top: 20px;
                                    border-left: 4px solid #0047AB; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Payment Successful!</h1>
                        <p>Thank you for your subscription</p>
                    </div>

                    <div class="content">
                        <h2 style="color: #0047AB;">Receipt #{payment_id[:8].upper()}</h2>

                        <div class="receipt-box">
                            <div class="row">
                                <span class="label">Plan:</span>
                                <span class="value">{plan_display}</span>
                            </div>
                            <div class="row">
                                <span class="label">Amount Paid:</span>
                                <span class="value">{amount} {currency}</span>
                            </div>
                            <div class="row">
                                <span class="label">Payment Method:</span>
                                <span class="value">{payment_method}</span>
                            </div>
                            <div class="row">
                                <span class="label">Payment Date:</span>
                                <span class="value">{payment_date}</span>
                            </div>
                            <div class="row">
                                <span class="label">Subscription Valid Until:</span>
                                <span class="value">{subscription_expires}</span>
                            </div>
                            <div class="row" style="border-bottom: none; margin-top: 20px;">
                                <span class="label">Receipt ID:</span>
                                <span style="font-family: monospace; font-size: 11px; color: #888;">{payment_id}</span>
                            </div>
                        </div>

                        <div class="success-box">
                            <p style="margin: 0; color: #1E40AF;">
                                <strong>✓ Your subscription is now active!</strong><br/>
                                You now have full access to all {plan_display} features.
                            </p>
                        </div>

                        <div style="text-align: center; margin-top: 30px;">
                            <a href="https://www.africybertrust.com/dashboard" class="button">
                                Go to Dashboard →
                            </a>
                        </div>

                        <div style="background: #F9FAFB; padding: 15px; border-radius: 8px; margin-top: 20px;">
                            <p style="margin: 0; color: #666; font-size: 13px;">
                                <strong>Need help?</strong> Contact us at support@africybertrust.com
                            </p>
                        </div>
                    </div>

                    <div class="footer">
                        <p>Africa Cyber Trust Infrastructure</p>
                        <p>© 2026 All rights reserved</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text fallback
            text = f"""
            Payment Receipt - Africa Cyber Trust Infrastructure

            🎉 PAYMENT SUCCESSFUL!

            Thank you for your subscription to {plan_display} plan.

            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            RECEIPT #{payment_id[:8].upper()}
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            Plan: {plan_display}
            Amount Paid: {amount} {currency}
            Payment Method: {payment_method}
            Payment Date: {payment_date}
            Subscription Valid Until: {subscription_expires}

            Receipt ID: {payment_id}
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            ✓ Your subscription is now active!
            You have full access to all {plan_display} features.

            Visit your dashboard: https://www.africybertrust.com/dashboard

            Need help? Contact us at support@africybertrust.com

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

            print(f"[EMAIL] Payment receipt sent to {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] Failed to send payment receipt: {str(e)}")
            print(f"        Error details: {type(e).__name__}")
            import traceback
            print(f"        Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def send_agent_rejection(
        to_email: str,
        agent_name: str,
        reason: str
    ) -> bool:
        """Send agent application rejection email (same as payment receipts)."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Africa Cyber Trust Agent Application Update"
            message["From"] = f"Africa Cyber Trust <{EmailService.SENDER_EMAIL}>"
            message["To"] = to_email

            # Email HTML content
            html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f7; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ padding: 40px 30px; }}
                .reason-box {{ background-color: #FEF2F2; border-left: 4px solid #DC2626; padding: 20px; margin: 20px 0; border-radius: 4px; }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">Application Update</h1>
                </div>
                <div class="content">
                    <p>Dear {agent_name},</p>
                    <p>Thank you for your interest in becoming an Africa Cyber Trust agent.</p>
                    <p>After careful review of your application, we regret to inform you that we are unable to approve it at this time.</p>
                    <div class="reason-box">
                        <strong>Reason:</strong><br>
                        {reason}
                    </div>
                    <p><strong>You may reapply after addressing the concerns mentioned above.</strong></p>
                    <p>If you have any questions or need clarification, please contact us at <a href="mailto:africybersolution@gmail.com">africybersolution@gmail.com</a>.</p>
                    <p>Best regards,<br><strong>Africa Cyber Trust Team</strong></p>
                </div>
                <div class="footer">
                    <p>© 2026 Africa Cyber Trust Infrastructure</p>
                </div>
            </div>
        </body>
        </html>
        """

            # Plain text fallback
            text = f"""
Application Update - Africa Cyber Trust

Dear {agent_name},

Thank you for your interest in becoming an Africa Cyber Trust agent.

After careful review of your application, we regret to inform you that we are unable to approve it at this time.

Reason:
{reason}

You may reapply after addressing the concerns mentioned above.

If you have any questions or need clarification, please contact us at africybersolution@gmail.com.

Best regards,
Africa Cyber Trust Team
"""

            # Attach both HTML and plain text versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            # Send via SMTP (same as payment receipts)
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.send_message(message)

            print(f"[EMAIL] Agent rejection sent to {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] Failed to send agent rejection: {str(e)}")
            print(f"        Error details: {type(e).__name__}")
            import traceback
            print(f"        Traceback: {traceback.format_exc()}")
            return False


# Create singleton instance
email_service = EmailService()
