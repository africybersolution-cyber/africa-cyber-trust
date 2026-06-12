"""
Clean RecommendationGenerator class with ASCII-only text (no emoji or Unicode).
This can be copied into scan_service.py
"""

class RecommendationGenerator:
    """Generates professional, actionable fix recommendations with code examples."""

    @staticmethod
    def get_ssl_expiry_fix(days_until_expiry: int) -> str:
        """SSL certificate expiring soon - detailed fix."""
        return f"""SSL certificate expires in {days_until_expiry} days. Renew immediately to avoid service disruption.

==================================================
HOW TO FIX
==================================================

OPTION 1: Let's Encrypt (Free, Recommended)
--------------------------------------------------
1. Install Certbot:
   Ubuntu/Debian:
   $ sudo apt-get update
   $ sudo apt-get install certbot python3-certbot-nginx

2. Obtain certificate:
   $ sudo certbot --nginx -d yourdomain.com

3. Auto-renewal (recommended):
   $ sudo certbot renew --dry-run

OPTION 2: Manual Certificate Renewal
--------------------------------------------------
1. Purchase SSL certificate from your provider
2. Generate CSR on your server:
   $ openssl req -new -newkey rsa:2048 -nodes \\
     -keyout yourdomain.key -out yourdomain.csr

3. Submit CSR to certificate authority
4. Install received certificate files

==================================================
VERIFICATION
==================================================

Check expiry date:
$ echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | \\
  openssl x509 -noout -dates

Or test online: https://www.ssllabs.com/ssltest/

TIME NEEDED: 10-20 minutes
DIFFICULTY: Easy (Let's Encrypt) / Medium (Manual)
COST: Free (Let's Encrypt) or $50-200/year
"""

    @staticmethod
    def get_weak_cipher_fix() -> str:
        """Weak SSL cipher detected - detailed fix."""
        return """Weak SSL cipher suites detected. Modern ciphers protect against attacks.

==================================================
HOW TO FIX
==================================================

NGINX:
--------------------------------------------------
Edit /etc/nginx/nginx.conf or your site config:

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;

Test and reload:
$ sudo nginx -t
$ sudo systemctl reload nginx

APACHE:
--------------------------------------------------
Edit /etc/apache2/mods-available/ssl.conf:

SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
SSLHonorCipherOrder off

Test and restart:
$ sudo apachectl configtest
$ sudo systemctl restart apache2

==================================================
VERIFICATION
==================================================

Test your SSL configuration:
https://www.ssllabs.com/ssltest/

Target grade: A or A+

TIME NEEDED: 10 minutes
DIFFICULTY: Easy
COST: Free
MOZILLA CONFIG GENERATOR: https://ssl-config.mozilla.org/
"""

    @staticmethod
    def get_x_frame_options_fix() -> str:
        """X-Frame-Options missing - detailed fix."""
        return """X-Frame-Options header prevents clickjacking attacks by controlling if your site can be embedded in iframes.

==================================================
HOW TO FIX
==================================================

NGINX:
--------------------------------------------------
Add to your server block in nginx.conf:

add_header X-Frame-Options "SAMEORIGIN" always;

Test and reload:
$ sudo nginx -t
$ sudo systemctl reload nginx

APACHE:
--------------------------------------------------
Add to .htaccess or httpd.conf:

Header always set X-Frame-Options "SAMEORIGIN"

Restart Apache:
$ sudo systemctl restart apache2

NODE.JS (Express):
--------------------------------------------------
Option 1 - Manual:
app.use((req, res, next) => {
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');
  next();
});

Option 2 - Using Helmet (Recommended):
const helmet = require('helmet');
app.use(helmet.frameguard({ action: 'sameorigin' }));

==================================================
HEADER OPTIONS
==================================================

- DENY: Never allow framing (most secure)
- SAMEORIGIN: Allow framing from same domain
- ALLOW-FROM uri: Allow specific domain (deprecated)

Recommended: Use "SAMEORIGIN" or "DENY"

==================================================
VERIFICATION
==================================================

Test with curl:
$ curl -I https://yourdomain.com | grep -i x-frame

Expected output:
x-frame-options: SAMEORIGIN

Or check online:
https://securityheaders.com/

TIME NEEDED: 5 minutes
DIFFICULTY: Easy
COST: Free
MDN DOCS: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
"""

    @staticmethod
    def get_hsts_fix() -> str:
        """HSTS not enabled - detailed fix."""
        return """HSTS (HTTP Strict Transport Security) forces browsers to only connect via HTTPS, preventing downgrade attacks.

==================================================
HOW TO FIX
==================================================

NGINX:
--------------------------------------------------
Add to your server block:

add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

For HSTS preload (optional, permanent):
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

Reload:
$ sudo systemctl reload nginx

APACHE:
--------------------------------------------------
Add to your VirtualHost:

Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

Restart:
$ sudo systemctl restart apache2

NODE.JS (Express with Helmet):
--------------------------------------------------
const helmet = require('helmet');
app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: true,
  preload: true
}));

==================================================
IMPORTANT
==================================================

- Ensure ALL subdomains support HTTPS before using includeSubDomains
- Start with short max-age (e.g., 300) for testing
- Only use "preload" if you're sure (it's permanent!)

==================================================
VERIFICATION
==================================================

Check header:
$ curl -I https://yourdomain.com | grep -i strict

Expected:
strict-transport-security: max-age=31536000; includeSubDomains

Test online: https://securityheaders.com/

TIME NEEDED: 10 minutes
DIFFICULTY: Easy
COST: Free
HSTS PRELOAD: https://hstspreload.org/
"""

    @staticmethod
    def get_spf_record_fix() -> str:
        """SPF record missing - detailed fix."""
        return """SPF (Sender Policy Framework) prevents email spoofing by specifying which servers can send email for your domain.

==================================================
HOW TO FIX
==================================================

CLOUDFLARE DNS:
--------------------------------------------------
1. Log into Cloudflare dashboard
2. Select your domain
3. Go to DNS → Records
4. Click "Add record"
5. Type: TXT
6. Name: @ (or your domain)
7. Content: v=spf1 include:_spf.google.com ~all
   (Adjust based on your email provider)
8. TTL: Auto
9. Click Save

ROUTE53 (AWS):
--------------------------------------------------
1. Open Route53 console
2. Select your hosted zone
3. Click "Create Record"
4. Record type: TXT
5. Name: leave blank (or @)
6. Value: "v=spf1 include:_spf.google.com ~all"
7. Click Create

OTHER DNS PROVIDERS:
--------------------------------------------------
Add a TXT record with:
- Name: @ or your domain
- Value: v=spf1 include:_spf.youremailprovider.com ~all

Common providers:
- Google Workspace: include:_spf.google.com
- Microsoft 365: include:spf.protection.outlook.com
- SendGrid: include:sendgrid.net

==================================================
VERIFICATION
==================================================

After 24-48 hours, check with:
$ dig +short TXT yourdomain.com | grep spf

Test online: https://mxtoolbox.com/spf.aspx

TIME NEEDED: 15 minutes
DIFFICULTY: Easy
COST: Free
"""

    @staticmethod
    def get_csp_fix() -> str:
        """Content Security Policy missing - detailed fix."""
        return """Content Security Policy (CSP) prevents XSS attacks by controlling which resources can load.

==================================================
HOW TO FIX
==================================================

NGINX:
--------------------------------------------------
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

APACHE:
--------------------------------------------------
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"

NODE.JS:
--------------------------------------------------
app.use((req, res, next) => {
  res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';");
  next();
});

==================================================
VERIFICATION
==================================================

$ curl -I https://yourdomain.com | grep -i content-security

TIME NEEDED: 10 minutes
DIFFICULTY: Medium
COST: Free
"""

    @staticmethod
    def get_x_content_type_options_fix() -> str:
        """X-Content-Type-Options missing - detailed fix."""
        return """X-Content-Type-Options prevents MIME-sniffing attacks.

==================================================
HOW TO FIX
==================================================

NGINX:
--------------------------------------------------
add_header X-Content-Type-Options "nosniff" always;

Reload: $ sudo systemctl reload nginx

APACHE:
--------------------------------------------------
Header always set X-Content-Type-Options "nosniff"

Restart: $ sudo systemctl restart apache2

NODE.JS:
--------------------------------------------------
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  next();
});

TIME: 5 minutes | DIFFICULTY: Easy | COST: Free
"""

    @staticmethod
    def get_x_xss_protection_fix() -> str:
        """X-XSS-Protection missing - detailed fix."""
        return """X-XSS-Protection enables browser XSS filtering.

==================================================
HOW TO FIX
==================================================

NGINX:
--------------------------------------------------
add_header X-XSS-Protection "1; mode=block" always;

APACHE:
--------------------------------------------------
Header always set X-XSS-Protection "1; mode=block"

NODE.JS:
--------------------------------------------------
app.use((req, res, next) => {
  res.setHeader('X-XSS-Protection', '1; mode=block');
  next();
});

TIME: 5 minutes | DIFFICULTY: Easy | COST: Free
"""
