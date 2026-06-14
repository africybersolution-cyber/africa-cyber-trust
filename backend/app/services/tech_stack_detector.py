"""Technology Stack Detection - CMS, Frameworks, Libraries, Servers"""
import requests
import re
from typing import List, Dict, Set
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin

from app.models.scan import Finding


class TechStackDetector:
    """Detect technology stack: CMS, frameworks, web servers, JavaScript libraries."""

    # CMS Detection Patterns
    CMS_PATTERNS = {
        'WordPress': [
            r'wp-content',
            r'wp-includes',
            r'/wp-json/',
            r'wordpress',
        ],
        'Drupal': [
            r'Drupal',
            r'/sites/default/',
            r'/modules/',
            r'/themes/',
        ],
        'Joomla': [
            r'Joomla',
            r'/components/com_',
            r'/templates/',
            r'joomla',
        ],
        'Magento': [
            r'Magento',
            r'/skin/frontend/',
            r'/media/catalog/',
        ],
        'Shopify': [
            r'cdn.shopify.com',
            r'myshopify.com',
        ],
        'Wix': [
            r'wix.com',
            r'wixstatic.com',
        ],
        'Squarespace': [
            r'squarespace',
        ],
    }

    # JavaScript Framework Detection
    JS_FRAMEWORKS = {
        'React': [r'react', r'_react', r'ReactDOM'],
        'Vue.js': [r'Vue', r'vue.js', r'__vue__'],
        'Angular': [r'angular', r'ng-'],
        'jQuery': [r'jquery', r'jQuery'],
        'Bootstrap': [r'bootstrap'],
        'Tailwind CSS': [r'tailwindcss'],
    }

    # Web Server Headers
    SERVER_PATTERNS = {
        'nginx': 'Nginx',
        'apache': 'Apache',
        'iis': 'Microsoft IIS',
        'cloudflare': 'Cloudflare',
        'cloudfront': 'AWS CloudFront',
    }

    @staticmethod
    def detect(url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """
        Detect technology stack of website.

        Returns findings with detected technologies and recommendations.
        """
        findings = []

        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        try:
            # Fetch website
            response = requests.get(url, timeout=10, verify=False, allow_redirects=True)
            headers = response.headers
            content = response.text

            detected_tech = {
                'cms': set(),
                'frameworks': set(),
                'servers': set(),
                'languages': set(),
                'libraries': set(),
            }

            # Detect CMS
            for cms_name, patterns in TechStackDetector.CMS_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        detected_tech['cms'].add(cms_name)
                        break

            # Detect JavaScript frameworks
            for fw_name, patterns in TechStackDetector.JS_FRAMEWORKS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        detected_tech['frameworks'].add(fw_name)
                        break

            # Detect web server from headers
            server_header = headers.get('Server', '').lower()
            for pattern, server_name in TechStackDetector.SERVER_PATTERNS.items():
                if pattern in server_header:
                    detected_tech['servers'].add(server_name)

            # Detect from X-Powered-By
            powered_by = headers.get('X-Powered-By', '')
            if powered_by:
                detected_tech['languages'].add(powered_by)

            # Detect programming language hints
            TechStackDetector._detect_languages(content, headers, detected_tech)

            # Generate findings
            findings.extend(TechStackDetector._generate_findings(
                detected_tech, url, asset_id, scan_id, response
            ))

        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="Technology Detection Error",
                description=f"Could not detect technology stack: {str(e)}",
                recommendation="Verify URL is accessible",
                created_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _detect_languages(content: str, headers: Dict, detected_tech: Dict):
        """Detect programming languages and frameworks."""
        # PHP
        if 'PHPSESSID' in content or '.php' in content:
            detected_tech['languages'].add('PHP')

        # ASP.NET
        if 'ASP.NET' in headers.get('X-Powered-By', '') or 'ASPXAUTH' in content:
            detected_tech['languages'].add('ASP.NET')

        # Python/Django
        if 'csrftoken' in content or 'django' in content.lower():
            detected_tech['languages'].add('Python/Django')

        # Node.js/Express
        if 'express' in headers.get('X-Powered-By', '').lower():
            detected_tech['languages'].add('Node.js/Express')

        # Ruby on Rails
        if 'rails' in content.lower() or '_rails_' in content:
            detected_tech['languages'].add('Ruby on Rails')

    @staticmethod
    def _generate_findings(detected_tech: Dict, url: str, asset_id: str, scan_id: str, response) -> List[Finding]:
        """Generate findings from detected technologies."""
        findings = []

        # CMS Findings
        if detected_tech['cms']:
            cms_list = ', '.join(detected_tech['cms'])

            # Check for WordPress specifically
            if 'WordPress' in detected_tech['cms']:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="medium",
                    category="technology_stack",
                    title="WordPress CMS Detected",
                    description="Site is running WordPress. Ensure it's updated and secured.",
                    recommendation="""WordPress Security Checklist

Step 1: Keep WordPress Updated
  - Update core, themes, and plugins regularly
  - Enable automatic updates: define('WP_AUTO_UPDATE_CORE', true);

Step 2: Remove Version Information
  Add to functions.php:
  remove_action('wp_head', 'wp_generator');

Step 3: Disable XML-RPC (if not needed)
  Add to .htaccess:
  <Files xmlrpc.php>
    Order Deny,Allow
    Deny from all
  </Files>

Step 4: Limit Login Attempts
  Install: Limit Login Attempts Reloaded plugin

Step 5: Use Security Plugin
  Install: Wordfence or Sucuri Security

Step 6: Change Admin Username
  Never use 'admin' as username

Step 7: Use Strong Passwords + 2FA
  Install: Two Factor Authentication plugin

Step 8: Regular Backups
  Install: UpdraftPlus plugin

Step 9: Hide wp-admin
  Use custom login URL

Step 10: Scan for Vulnerabilities
  Use WPScan: wpscan --url {url}

TIME: 2-3 hours initial setup | SEVERITY: MEDIUM""",
                    created_at=datetime.now(timezone.utc)
                ))

                # Check for common WordPress vulnerabilities
                findings.extend(TechStackDetector._check_wordpress_vulns(url, asset_id, scan_id))

            else:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="technology_stack",
                    title=f"CMS Detected: {cms_list}",
                    description=f"Website is running {cms_list}.",
                    recommendation=f"Keep {cms_list} and all plugins/themes updated. Enable security features.",
                    created_at=datetime.now(timezone.utc)
                ))

        # Web Server Findings
        if detected_tech['servers']:
            server_list = ', '.join(detected_tech['servers'])
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="technology_stack",
                title=f"Web Server: {server_list}",
                description=f"Detected web server: {server_list}",
                recommendation="Keep web server updated to latest stable version.",
                created_at=datetime.now(timezone.utc)
            ))

        # JavaScript Framework Findings
        if detected_tech['frameworks']:
            fw_list = ', '.join(detected_tech['frameworks'])

            # Check for jQuery (often outdated)
            if 'jQuery' in detected_tech['frameworks']:
                jquery_version = TechStackDetector._extract_jquery_version(response.text)
                if jquery_version:
                    version_parts = jquery_version.split('.')
                    major_version = int(version_parts[0]) if version_parts else 0

                    if major_version < 3:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="medium",
                            category="outdated_library",
                            title=f"Outdated jQuery Version: {jquery_version}",
                            description=f"jQuery {jquery_version} has known security vulnerabilities.",
                            recommendation="""Update jQuery to Latest Version

jQuery versions < 3.0 have XSS vulnerabilities.

Step 1: Update jQuery
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

Step 2: Test Website
  - Check all JavaScript functionality
  - jQuery 3.x has breaking changes from 1.x/2.x

Step 3: Use Subresource Integrity (SRI)
  <script src="..." integrity="sha384-..." crossorigin="anonymous"></script>

Step 4: Consider Removing jQuery
  - Modern JavaScript can replace many jQuery functions
  - Reduces page load time

TIME: 1-2 hours | SEVERITY: MEDIUM""",
                            created_at=datetime.now(timezone.utc)
                        ))

            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="technology_stack",
                title=f"JavaScript Frameworks: {fw_list}",
                description=f"Detected frameworks/libraries: {fw_list}",
                recommendation="Keep all JavaScript libraries updated to latest versions.",
                created_at=datetime.now(timezone.utc)
            ))

        # Programming Language Findings
        if detected_tech['languages']:
            lang_list = ', '.join(detected_tech['languages'])
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="technology_stack",
                title=f"Programming Language/Framework: {lang_list}",
                description=f"Detected: {lang_list}",
                recommendation="Keep runtime and framework versions updated.",
                created_at=datetime.now(timezone.utc)
            ))

        # If nothing detected
        if not any(detected_tech.values()):
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="technology_stack",
                title="Technology Stack Not Detected",
                description="Could not identify specific technologies. Site may be using custom stack or obscured headers.",
                recommendation="Good! Less information disclosure reduces attack surface.",
                created_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _check_wordpress_vulns(url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check for common WordPress vulnerabilities."""
        findings = []

        try:
            # Check if xmlrpc.php is accessible
            xmlrpc_url = urljoin(url, '/xmlrpc.php')
            response = requests.post(xmlrpc_url, timeout=5, verify=False)

            if response.status_code == 200:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="high",
                    category="wordpress_vulnerability",
                    title="WordPress XML-RPC Enabled (Attack Vector)",
                    description="XML-RPC is enabled and can be exploited for DDoS and brute force attacks.",
                    recommendation="""Disable XML-RPC Immediately

XML-RPC is used for brute force and DDoS amplification attacks.

Method 1: .htaccess (Recommended)
  Add to .htaccess:
  <Files xmlrpc.php>
    Order Deny,Allow
    Deny from all
  </Files>

Method 2: Plugin
  Install 'Disable XML-RPC' plugin

Method 3: functions.php
  add_filter('xmlrpc_enabled', '__return_false');

VERIFY: Visit /xmlrpc.php should return 403

TIME: 5 minutes | SEVERITY: HIGH""",
                    created_at=datetime.now(timezone.utc)
                ))

            # Check wp-json API
            wpjson_url = urljoin(url, '/wp-json/wp/v2/users')
            response = requests.get(wpjson_url, timeout=5, verify=False)

            if response.status_code == 200:
                try:
                    users = response.json()
                    if users and isinstance(users, list) and len(users) > 0:
                        usernames = [user.get('slug', user.get('name', '')) for user in users[:3]]
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="medium",
                            category="information_disclosure",
                            title="WordPress User Enumeration via REST API",
                            description=f"Usernames exposed via REST API: {', '.join(usernames)}",
                            recommendation="""Disable WordPress User Enumeration

Step 1: Restrict REST API
  Add to functions.php:

  add_filter('rest_endpoints', function($endpoints) {
      if (isset($endpoints['/wp/v2/users'])) {
          unset($endpoints['/wp/v2/users']);
      }
      return $endpoints;
  });

Step 2: Use Security Plugin
  Wordfence and Sucuri block user enumeration

Step 3: Change Admin Username
  Don't use 'admin', 'administrator', or site name

TIME: 10 minutes | SEVERITY: MEDIUM""",
                            created_at=datetime.now(timezone.utc)
                        ))
                except:
                    pass

        except:
            pass

        return findings

    @staticmethod
    def _extract_jquery_version(content: str) -> str:
        """Extract jQuery version from page content."""
        match = re.search(r'jquery[/-](\d+\.\d+\.?\d*)', content, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
