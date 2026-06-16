"""SSL/TLS Certificate Scanner - Expiry and Configuration Check"""
import ssl
import socket
from datetime import datetime, timezone
from typing import List
from urllib.parse import urlparse

from app.models.scan import Finding


class SSLCertificateScanner:
    """Scan SSL/TLS certificates for expiry, validity, and configuration issues."""

    @staticmethod
    def scan(value: str, asset_id: str, scan_id: str) -> List[Finding]:
        """
        Scan SSL certificate for security issues.

        Accepts:
        - domain.com:443
        - https://domain.com
        - domain.com (defaults to port 443)
        """
        findings = []

        # Parse hostname and port
        hostname, port = SSLCertificateScanner._parse_host_port(value)

        if not hostname:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="configuration",
                title="Invalid SSL Certificate Target",
                description=f"Could not parse hostname from: {value}",
                recommendation="Provide hostname in format: domain.com:443 or https://domain.com",
            ))
            return findings

        # Scan SSL certificate
        findings.extend(SSLCertificateScanner._check_certificate(hostname, port, asset_id, scan_id))

        return findings

    @staticmethod
    def _parse_host_port(value: str) -> tuple:
        """Parse hostname and port from value."""
        value = value.strip()

        # Remove protocol if present
        if "://" in value:
            parsed = urlparse(value)
            hostname = parsed.hostname or parsed.netloc
            port = parsed.port or 443
            return (hostname, port)

        # Check for port notation
        if ":" in value and not value.count(":") > 1:  # Not IPv6
            parts = value.split(":")
            try:
                return (parts[0], int(parts[1]))
            except:
                return (parts[0], 443)

        # Default to port 443
        return (value, 443)

    @staticmethod
    def _check_certificate(hostname: str, port: int, asset_id: str, scan_id: str) -> List[Finding]:
        """Check SSL certificate configuration."""
        findings = []

        try:
            # Create SSL context
            context = ssl.create_default_context()

            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    # Check certificate expiry
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    not_after = not_after.replace(tzinfo=timezone.utc)
                    days_until_expiry = (not_after - datetime.now(timezone.utc)).days

                    if days_until_expiry < 0:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="critical",
                            category="ssl_tls",
                            title="SSL Certificate Expired",
                            description=f"Certificate expired {abs(days_until_expiry)} days ago on {not_after.strftime('%Y-%m-%d')}",
                            recommendation="""CRITICAL - Certificate Expired!

Browsers will show security warnings to all visitors!

IMMEDIATE ACTION (Let's Encrypt - Free):
Step 1: Install Certbot
  Ubuntu/Debian:
  sudo apt-get update
  sudo apt-get install certbot python3-certbot-nginx

  CentOS/RHEL:
  sudo yum install certbot python3-certbot-nginx

Step 2: Obtain new certificate
  sudo certbot --nginx -d {hostname}

Step 3: Verify auto-renewal
  sudo certbot renew --dry-run

ALTERNATIVE (Commercial Certificate):
Step 1: Generate CSR
  openssl req -new -newkey rsa-2048 -nodes -keyout {hostname}.key -out {hostname}.csr

Step 2: Purchase certificate (GoDaddy, Namecheap, etc.)

Step 3: Install received certificate

VERIFICATION: Visit https://{hostname} - should show valid certificate

TIME: 10-20 minutes | SEVERITY: CRITICAL""",
                        ))
                    elif days_until_expiry <= 7:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="critical",
                            category="ssl_tls",
                            title=f"SSL Certificate Expires in {days_until_expiry} Days",
                            description=f"Certificate expires on {not_after.strftime('%Y-%m-%d')}. Renew immediately!",
                            recommendation=f"""URGENT - Certificate Expires Soon!

Expires: {not_after.strftime('%Y-%m-%d %H:%M:%S UTC')} ({days_until_expiry} days)

Quick Renewal (Let's Encrypt):
  sudo certbot renew
  sudo systemctl reload nginx

Verify Renewal:
  sudo certbot certificates

Set up auto-renewal if not already enabled:
  sudo systemctl enable certbot.timer
  sudo systemctl start certbot.timer

TIME: 5 minutes | SEVERITY: CRITICAL""",
                        ))
                    elif days_until_expiry <= 30:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="high",
                            category="ssl_tls",
                            title=f"SSL Certificate Expires in {days_until_expiry} Days",
                            description=f"Certificate expires on {not_after.strftime('%Y-%m-%d')}. Plan renewal soon.",
                            recommendation=f"""Schedule Certificate Renewal

Expires: {not_after.strftime('%Y-%m-%d')} ({days_until_expiry} days)

Action: Renew before {(not_after - datetime.now(timezone.utc)).days - 7} days

Let's Encrypt (automatic):
  sudo certbot renew --dry-run

Check auto-renewal is enabled:
  sudo systemctl status certbot.timer

TIME: 5 minutes""",
                        ))
                    else:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="info",
                            category="ssl_tls",
                            title=f"SSL Certificate Valid ({days_until_expiry} Days Remaining)",
                            description=f"Certificate is valid and expires on {not_after.strftime('%Y-%m-%d')} ({days_until_expiry} days).",
                            recommendation="Certificate is valid. Ensure auto-renewal is configured to prevent expiry.",
                        ))

                    # Check certificate issuer
                    issuer = dict(x[0] for x in cert['issuer'])
                    issuer_cn = issuer.get('commonName', 'Unknown')

                    # Check for self-signed certificate
                    subject = dict(x[0] for x in cert['subject'])
                    subject_cn = subject.get('commonName', '')

                    if issuer_cn == subject_cn or 'self' in issuer_cn.lower():
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="high",
                            category="ssl_tls",
                            title="Self-Signed Certificate Detected",
                            description="Certificate is self-signed. Browsers will show security warnings to users.",
                            recommendation="""Replace Self-Signed Certificate with Trusted Certificate

PROBLEM: Browsers don't trust self-signed certificates

SOLUTION 1: Let's Encrypt (Free & Trusted):
  sudo certbot --nginx -d {hostname}

SOLUTION 2: Commercial Certificate:
  Purchase from GoDaddy, Namecheap, etc.

WHY: Trusted certificates provide:
  - No browser warnings
  - User confidence
  - SEO benefits

TIME: 15 minutes | SEVERITY: HIGH""",
                        ))

                    # Check TLS version
                    tls_version = ssock.version()
                    if tls_version in ['TLSv1', 'TLSv1.1', 'SSLv2', 'SSLv3']:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="high",
                            category="ssl_tls",
                            title=f"Weak TLS Version: {tls_version}",
                            description=f"Server supports weak TLS version {tls_version}. Should use TLS 1.2 or 1.3 only.",
                            recommendation="""Disable Weak TLS Versions

FOR NGINX:
Edit /etc/nginx/nginx.conf:
  ssl_protocols TLSv1.2 TLSv1.3;

Reload: sudo systemctl reload nginx

FOR APACHE:
Edit /etc/apache2/mods-available/ssl.conf:
  SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1

Restart: sudo systemctl restart apache2

VERIFY: https://www.ssllabs.com/ssltest/

TIME: 10 minutes | SEVERITY: HIGH""",
                        ))
                    else:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="info",
                            category="ssl_tls",
                            title=f"Strong TLS Version: {tls_version}",
                            description=f"Server uses modern {tls_version} protocol. Good configuration!",
                            recommendation="TLS configuration is secure. Continue monitoring.",
                        ))

        except ssl.SSLError as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="high",
                category="ssl_tls",
                title="SSL Connection Error",
                description=f"SSL/TLS connection failed: {str(e)}",
                recommendation="""SSL Connection Failed

Possible causes:
1. Certificate hostname mismatch
2. Expired or invalid certificate
3. Server doesn't support TLS
4. Firewall blocking port {port}

ACTION:
1. Verify certificate is valid for {hostname}
2. Check certificate expiry
3. Ensure port {port} is open
4. Test at: https://www.ssllabs.com/ssltest/analyze.html?d={hostname}

TIME: 10-30 minutes depending on issue""",
            ))
        except socket.timeout:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="medium",
                category="network",
                title="Connection Timeout",
                description=f"Could not connect to {hostname}:{port} - connection timed out.",
                recommendation=f"Verify {hostname} is accessible and port {port} is open. Check firewall rules.",
            ))
        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="SSL Scan Error",
                description=f"Could not scan SSL certificate: {str(e)}",
                recommendation="Verify hostname and port are correct. Ensure server is accessible.",
            ))

        return findings
