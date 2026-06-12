"""
Security Scanning Service

Performs actual security scans on domains/assets and detects vulnerabilities.
"""
import socket
import ssl
import requests
from datetime import datetime, timezone
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.models.scan import Scan, Finding
from app.models.asset import Asset


class RecommendationGenerator:
    """Detailed, actionable recommendations with step-by-step instructions."""

    @staticmethod
    def get_ssl_expiry_fix(days_until_expiry: int) -> str:
        return f"""SSL certificate expires in {days_until_expiry} days. Renew immediately to avoid service disruption.

OPTION 1: Let's Encrypt (Free - Recommended)
Step 1: Install Certbot
  Ubuntu/Debian: sudo apt-get install certbot python3-certbot-nginx
  CentOS/RHEL: sudo yum install certbot python3-certbot-nginx

Step 2: Obtain and install certificate
  sudo certbot --nginx -d yourdomain.com

Step 3: Test auto-renewal
  sudo certbot renew --dry-run

OPTION 2: Commercial Certificate
Step 1: Generate CSR
  openssl req -new -newkey rsa-2048 -nodes -keyout domain.key -out domain.csr

Step 2: Purchase certificate from provider (GoDaddy, Namecheap, etc.)

Step 3: Install received certificate files on your server

VERIFICATION: Check expiry date
  echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

TIME: 10-20 minutes | COST: Free (Let's Encrypt)"""

    @staticmethod
    def get_weak_cipher_fix() -> str:
        return """Weak SSL ciphers detected. Update to modern TLS 1.2+ with strong cipher suites.

FOR NGINX:
Step 1: Edit /etc/nginx/nginx.conf or your site config

Step 2: Add these lines in the server block:
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
  ssl_prefer_server_ciphers off;

Step 3: Test and reload
  sudo nginx -t
  sudo systemctl reload nginx

FOR APACHE:
Step 1: Edit /etc/apache2/mods-available/ssl.conf

Step 2: Add these lines:
  SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
  SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256

Step 3: Restart Apache
  sudo systemctl restart apache2

VERIFICATION: Test at https://www.ssllabs.com/ssltest/ (should get A or A+)

TIME: 10 minutes | DIFFICULTY: Easy"""

    @staticmethod
    def get_x_frame_options_fix() -> str:
        return """Add X-Frame-Options header to prevent clickjacking attacks.

FOR NGINX:
Step 1: Edit your site config file (/etc/nginx/sites-available/yoursite)

Step 2: Add this line inside the server block:
  add_header X-Frame-Options "SAMEORIGIN" always;

Step 3: Test and reload
  sudo nginx -t
  sudo systemctl reload nginx

FOR APACHE:
Step 1: Edit .htaccess or httpd.conf

Step 2: Add this line:
  Header always set X-Frame-Options "SAMEORIGIN"

Step 3: Restart Apache
  sudo systemctl restart apache2

FOR NODE.JS (Express):
Add this middleware in your app.js:
  app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'SAMEORIGIN');
    next();
  });

HEADER OPTIONS:
- DENY: Never allow framing (most secure)
- SAMEORIGIN: Allow framing from same domain only (recommended)

VERIFICATION: Test with curl
  curl -I https://yourdomain.com | grep -i x-frame
  (Should show: x-frame-options: SAMEORIGIN)

TIME: 5 minutes | DIFFICULTY: Easy"""

    @staticmethod
    def get_hsts_fix() -> str:
        return """Enable HSTS (HTTP Strict Transport Security) to force HTTPS connections and prevent downgrade attacks.

FOR NGINX:
Step 1: Edit your site config (/etc/nginx/sites-available/yoursite)

Step 2: Add this inside the server block:
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

Step 3: Reload Nginx
  sudo systemctl reload nginx

FOR APACHE:
Step 1: Edit your VirtualHost config

Step 2: Add this line:
  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

Step 3: Restart Apache
  sudo systemctl restart apache2

FOR NODE.JS (Express with Helmet):
  const helmet = require('helmet');
  app.use(helmet.hsts({
    maxAge: 31536000,
    includeSubDomains: true
  }));

IMPORTANT NOTES:
- Ensure ALL subdomains support HTTPS before using includeSubDomains
- Start with a short max-age (300 seconds) for testing
- Once confirmed working, increase to 31536000 (1 year)

VERIFICATION:
  curl -I https://yourdomain.com | grep -i strict
  (Should show: strict-transport-security: max-age=31536000; includeSubDomains)

TIME: 10 minutes | DIFFICULTY: Easy"""

    @staticmethod
    def get_spf_record_fix() -> str:
        return """Add SPF (Sender Policy Framework) record to prevent email spoofing.

FOR CLOUDFLARE:
Step 1: Log into Cloudflare dashboard
Step 2: Select your domain
Step 3: Go to DNS > Records
Step 4: Click "Add record"
Step 5: Fill in:
  Type: TXT
  Name: @ (or your domain)
  Content: v=spf1 include:_spf.google.com ~all
  (Replace google.com with your email provider)
Step 6: Click Save

FOR OTHER DNS PROVIDERS (GoDaddy, Namecheap, etc.):
Step 1: Log into DNS management
Step 2: Add new TXT record
Step 3: Name: @ (or leave blank)
Step 4: Value: v=spf1 include:_spf.youremailprovider.com ~all

COMMON EMAIL PROVIDERS:
- Google Workspace: v=spf1 include:_spf.google.com ~all
- Microsoft 365: v=spf1 include:spf.protection.outlook.com ~all
- SendGrid: v=spf1 include:sendgrid.net ~all

VERIFICATION (after 24-48 hours):
  dig TXT yourdomain.com | grep spf
  Or test at: https://mxtoolbox.com/spf.aspx

TIME: 15 minutes | DIFFICULTY: Easy"""

    @staticmethod
    def get_csp_fix() -> str:
        return """Add Content-Security-Policy header to prevent XSS attacks.

FOR NGINX:
  add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

FOR APACHE:
  Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"

FOR NODE.JS:
  app.use((req, res, next) => {
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'");
    next();
  });

NOTE: Start with a basic policy then adjust based on your site's needs.

VERIFICATION:
  curl -I https://yourdomain.com | grep -i content-security

TIME: 10 minutes | DIFFICULTY: Medium"""

    @staticmethod
    def get_x_content_type_options_fix() -> str:
        return """Add X-Content-Type-Options header to prevent MIME-sniffing attacks.

FOR NGINX:
Step 1: Edit your site config
Step 2: Add: add_header X-Content-Type-Options "nosniff" always;
Step 3: Reload: sudo systemctl reload nginx

FOR APACHE:
Step 1: Edit .htaccess or httpd.conf
Step 2: Add: Header always set X-Content-Type-Options "nosniff"
Step 3: Restart: sudo systemctl restart apache2

FOR NODE.JS:
  app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    next();
  });

VERIFICATION:
  curl -I https://yourdomain.com | grep -i x-content-type

TIME: 5 minutes | DIFFICULTY: Easy"""

    @staticmethod
    def get_x_xss_protection_fix() -> str:
        return """Add X-XSS-Protection header to enable browser XSS filtering.

FOR NGINX:
Step 1: Edit your site config
Step 2: Add: add_header X-XSS-Protection "1; mode=block" always;
Step 3: Reload: sudo systemctl reload nginx

FOR APACHE:
Step 1: Edit .htaccess or httpd.conf
Step 2: Add: Header always set X-XSS-Protection "1; mode=block"
Step 3: Restart: sudo systemctl restart apache2

FOR NODE.JS:
  app.use((req, res, next) => {
    res.setHeader('X-XSS-Protection', '1; mode=block');
    next();
  });

VERIFICATION:
  curl -I https://yourdomain.com | grep -i x-xss

TIME: 5 minutes | DIFFICULTY: Easy"""


class SecurityScanner:
    """Performs security scans on assets."""

    def __init__(self, db: Session):
        self.db = db

    async def scan_asset(self, asset_id: str) -> Scan:
        """
        Perform a comprehensive security scan on an asset.

        Args:
            asset_id: Asset UUID to scan

        Returns:
            Scan object with results
        """
        # Get asset
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Create scan record
        scan = Scan(
            asset_id=asset_id,
            status="running",
            started_at=datetime.now(timezone.utc),
            scan_type="full"
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)

        try:
            # Extract domain from asset value
            domain = self._extract_domain(asset.value)

            # Run all security checks
            findings = []
            findings.extend(self._check_ssl_tls(domain, asset_id, scan.id))
            findings.extend(self._check_security_headers(domain, asset_id, scan.id))
            findings.extend(self._check_dns_security(domain, asset_id, scan.id))
            findings.extend(self._check_common_vulns(domain, asset_id, scan.id))

            # Deduplicate findings (same title + asset + scan = duplicate)
            unique_findings = {}
            for finding in findings:
                key = f"{finding.title}_{finding.asset_id}_{finding.scan_id}"
                if key not in unique_findings:
                    unique_findings[key] = finding

            # Save unique findings only
            for finding in unique_findings.values():
                self.db.add(finding)

            # Update findings list to reflect actual saved count
            findings = list(unique_findings.values())

            # Count findings by severity
            scan.findings_count = len(findings)
            scan.critical_count = sum(1 for f in findings if f.severity == "critical")
            scan.high_count = sum(1 for f in findings if f.severity == "high")
            scan.medium_count = sum(1 for f in findings if f.severity == "medium")
            scan.low_count = sum(1 for f in findings if f.severity == "low")

            # Calculate security score
            scan.score = scan.calculate_score()

            # Update scan status
            scan.status = "completed"
            scan.completed_at = datetime.now(timezone.utc)

            # Update asset
            asset.last_scanned_at = scan.completed_at  # Fixed: was last_scan_at
            asset.security_score = scan.score
            asset.findings_count = scan.findings_count

            # Update next scheduled scan time
            from datetime import timedelta
            interval_map = {
                '1h': timedelta(hours=1),
                '6h': timedelta(hours=6),
                '12h': timedelta(hours=12),
                '24h': timedelta(hours=24),
                'daily': timedelta(days=1),
                'weekly': timedelta(weeks=1),
                'monthly': timedelta(days=30)
            }
            interval = interval_map.get(asset.scan_interval, timedelta(days=1))
            asset.next_scan_at = scan.completed_at + interval

            self.db.commit()
            self.db.refresh(scan)
            self.db.refresh(asset)  # Refresh asset to get updated values

            # Send email alert if critical or high severity issues found
            if scan.critical_count > 0 or scan.high_count > 0:
                try:
                    # Get user email from company owner
                    from app.models.user import User
                    from app.models.company import Company

                    company = self.db.query(Company).filter(Company.id == asset.company_id).first()
                    if company:
                        # Get company owner/admin
                        user = self.db.query(User).filter(
                            User.company_id == company.id,
                            User.role == 'company_admin'
                        ).first()

                        if user and user.email:
                            # Send alert email
                            from app.services.email_service import email_service

                            findings_data = [
                                {
                                    'severity': f.severity,
                                    'category': f.category,
                                    'title': f.title,
                                    'description': f.description,
                                    'recommendation': f.recommendation
                                }
                                for f in findings
                            ]

                            email_service.send_security_alert(
                                to_email=user.email,
                                asset_name=asset.name,
                                asset_url=asset.value,
                                security_score=scan.score,
                                critical_count=scan.critical_count,
                                high_count=scan.high_count,
                                findings=findings_data
                            )
                            print(f"📧 Security alert sent to {user.email}")
                except Exception as email_error:
                    print(f"⚠️ Failed to send email alert: {email_error}")
                    # Don't fail the scan if email fails

            return scan

        except Exception as e:
            scan.status = "failed"
            scan.completed_at = datetime.now(timezone.utc)
            scan.scan_data = {"error": str(e)}
            self.db.commit()
            raise

    def _extract_domain(self, value: str) -> str:
        """Extract clean domain from asset value."""
        if "://" in value:
            parsed = urlparse(value)
            return parsed.netloc or parsed.path
        return value.split("/")[0]

    def _check_ssl_tls(self, domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check SSL/TLS configuration."""
        findings = []

        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()

                    # Check certificate expiration
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days

                    if days_until_expiry < 30:
                        findings.append(Finding(
                            scan_id=scan_id,
                            asset_id=asset_id,
                            severity="high" if days_until_expiry < 7 else "medium",
                            title="SSL Certificate Expiring Soon",
                            description=f"SSL certificate expires in {days_until_expiry} days",
                            recommendation=RecommendationGenerator.get_ssl_expiry_fix(days_until_expiry),
                            category="SSL/TLS"
                        ))

                    # Check weak ciphers
                    cipher_name = cipher[0] if cipher else ""
                    if any(weak in cipher_name.lower() for weak in ['rc4', 'des', 'md5']):
                        findings.append(Finding(
                            scan_id=scan_id,
                            asset_id=asset_id,
                            severity="high",
                            title="Weak SSL Cipher Suite",
                            description=f"Weak cipher detected: {cipher_name}",
                            recommendation="Update SSL configuration to use strong ciphers",
                            category="SSL/TLS"
                        ))

        except ssl.SSLError as e:
            findings.append(Finding(
                scan_id=scan_id,
                asset_id=asset_id,
                severity="critical",
                title="SSL/TLS Configuration Error",
                description=f"SSL/TLS error: {str(e)}",
                recommendation="Fix SSL/TLS configuration",
                category="SSL/TLS"
            ))
        except socket.timeout:
            findings.append(Finding(
                scan_id=scan_id,
                asset_id=asset_id,
                severity="medium",
                title="Connection Timeout",
                description="Could not establish SSL connection (timeout)",
                recommendation="Check if domain is accessible",
                category="Availability"
            ))
        except Exception as e:
            # Domain might not support HTTPS or other issues
            findings.append(Finding(
                scan_id=scan_id,
                asset_id=asset_id,
                severity="low",
                title="HTTPS Not Available",
                description=f"Could not establish HTTPS connection: {str(e)}",
                recommendation="Enable HTTPS for better security",
                category="SSL/TLS"
            ))

        return findings

    def _check_security_headers(self, domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check for security headers."""
        findings = []

        try:
            response = requests.get(f"https://{domain}", timeout=10, allow_redirects=True)
            headers = response.headers

            # Critical security headers
            required_headers = {
                'Strict-Transport-Security': ('high', 'HSTS Not Enabled'),
                'X-Content-Type-Options': ('medium', 'X-Content-Type-Options Missing'),
                'X-Frame-Options': ('medium', 'X-Frame-Options Missing'),
                'Content-Security-Policy': ('high', 'Content Security Policy Missing'),
                'X-XSS-Protection': ('low', 'X-XSS-Protection Missing')
            }

            for header, (severity, title) in required_headers.items():
                if header not in headers:
                    # Get appropriate detailed recommendation
                    if header == 'Strict-Transport-Security':
                        recommendation = RecommendationGenerator.get_hsts_fix()
                    elif header == 'X-Frame-Options':
                        recommendation = RecommendationGenerator.get_x_frame_options_fix()
                    elif header == 'X-Content-Type-Options':
                        recommendation = RecommendationGenerator.get_x_content_type_options_fix()
                    elif header == 'X-XSS-Protection':
                        recommendation = RecommendationGenerator.get_x_xss_protection_fix()
                    elif header == 'Content-Security-Policy':
                        recommendation = RecommendationGenerator.get_csp_fix()
                    else:
                        recommendation = f"Add {header} header"

                    findings.append(Finding(
                        scan_id=scan_id,
                        asset_id=asset_id,
                        severity=severity,
                        title=title,
                        description=f"Security header '{header}' is not set",
                        recommendation=recommendation,
                        category="Security Headers"
                    ))

            # Check for insecure headers
            if 'Server' in headers:
                findings.append(Finding(
                    scan_id=scan_id,
                    asset_id=asset_id,
                    severity="low",
                    title="Server Information Disclosure",
                    description=f"Server header reveals: {headers['Server']}",
                    recommendation="Remove or obscure Server header",
                    category="Information Disclosure"
                ))

        except requests.exceptions.SSLError:
            pass  # Already handled in SSL check
        except Exception as e:
            # Domain might not be accessible
            pass

        return findings

    def _check_dns_security(self, domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check DNS security configuration."""
        findings = []

        try:
            import dns.resolver

            # Check for SPF record
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                has_spf = any('spf' in str(rdata).lower() for rdata in answers)
                if not has_spf:
                    findings.append(Finding(
                        scan_id=scan_id,
                        asset_id=asset_id,
                        severity="medium",
                        title="SPF Record Missing",
                        description="Domain lacks SPF record for email authentication",
                        recommendation=RecommendationGenerator.get_spf_record_fix(),
                        category="DNS Security"
                    ))
            except:
                findings.append(Finding(
                    scan_id=scan_id,
                    asset_id=asset_id,
                    severity="low",
                    title="DNS TXT Records Not Found",
                    description="Could not query DNS TXT records",
                    recommendation="Verify DNS configuration",
                    category="DNS Security"
                ))

            # Check for DNSSEC
            try:
                resolver = dns.resolver.Resolver()
                resolver.use_edns(0, dns.flags.DO, 4096)
                answers = resolver.resolve(domain, 'A')
                if not answers.response.flags & dns.flags.AD:
                    findings.append(Finding(
                        scan_id=scan_id,
                        asset_id=asset_id,
                        severity="low",
                        title="DNSSEC Not Enabled",
                        description="Domain does not use DNSSEC",
                        recommendation="Enable DNSSEC for DNS security",
                        category="DNS Security"
                    ))
            except:
                pass

        except ImportError:
            # dnspython not installed - skip DNS checks
            pass
        except Exception:
            pass

        return findings

    def _check_common_vulns(self, domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check for common vulnerabilities."""
        findings = []

        try:
            # Check for default/common paths
            common_paths = [
                '/admin', '/.git', '/.env', '/config', '/backup',
                '/phpinfo.php', '/test.php', '/.htaccess'
            ]

            for path in common_paths[:3]:  # Check first 3 to avoid too many requests
                try:
                    response = requests.get(f"https://{domain}{path}", timeout=5, allow_redirects=False)
                    if response.status_code not in [404, 403, 401]:
                        findings.append(Finding(
                            scan_id=scan_id,
                            asset_id=asset_id,
                            severity="medium",
                            title=f"Sensitive Path Exposed: {path}",
                            description=f"Path '{path}' returns HTTP {response.status_code}",
                            recommendation=f"Restrict access to {path}",
                            category="Access Control"
                        ))
                except:
                    pass

        except Exception:
            pass

        return findings


# Singleton service instance
def get_scanner(db: Session) -> SecurityScanner:
    """Get scanner instance."""
    return SecurityScanner(db)
