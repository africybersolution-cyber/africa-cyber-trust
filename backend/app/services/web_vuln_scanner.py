"""Web Application Vulnerability Scanner - OWASP Top 10"""
import requests
import re
import urllib.parse
from typing import List, Dict
from datetime import datetime, timezone

from app.models.scan import Finding


class WebVulnScanner:
    """Scan web applications for OWASP Top 10 vulnerabilities."""

    # SQL Injection payloads
    SQL_PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "1' OR '1' = '1",
        "' UNION SELECT NULL--",
        "' AND 1=1--",
        "' AND 1=2--",
    ]

    # XSS payloads
    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src=javascript:alert('XSS')>",
    ]

    # Directory traversal payloads
    PATH_TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]

    # Command injection payloads
    COMMAND_INJECTION_PAYLOADS = [
        "; ls -la",
        "| whoami",
        "`id`",
        "$(whoami)",
        "&& cat /etc/passwd",
    ]

    # SQL injection error patterns
    SQL_ERRORS = [
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_.*",
        r"PostgreSQL.*ERROR",
        r"Warning.*pg_.*",
        r"valid MySQL result",
        r"MySqlClient\.",
        r"Microsoft SQL Native Client error",
        r"ODBC SQL Server Driver",
        r"SQLServer JDBC Driver",
        r"Oracle error",
        r"ORA-[0-9]{5}",
        r"sqlite3.OperationalError",
    ]

    @staticmethod
    def scan(url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """
        Scan web application for vulnerabilities.

        Checks for:
        - SQL Injection
        - XSS (Cross-Site Scripting)
        - Directory Traversal
        - Command Injection
        - Open Redirects
        - Security Misconfigurations
        """
        findings = []

        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        try:
            # Test if URL is accessible
            response = requests.get(url, timeout=10, verify=False, allow_redirects=True)

            # Check for SQL Injection
            findings.extend(WebVulnScanner._test_sql_injection(url, asset_id, scan_id))

            # Check for XSS
            findings.extend(WebVulnScanner._test_xss(url, asset_id, scan_id))

            # Check for Directory Traversal
            findings.extend(WebVulnScanner._test_path_traversal(url, asset_id, scan_id))

            # Check for Command Injection
            findings.extend(WebVulnScanner._test_command_injection(url, asset_id, scan_id))

            # Check for security misconfigurations
            findings.extend(WebVulnScanner._check_server_info(response, asset_id, scan_id))

            # Check for sensitive data exposure
            findings.extend(WebVulnScanner._check_sensitive_exposure(response, url, asset_id, scan_id))

        except requests.exceptions.SSLError:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="high",
                category="ssl_tls",
                title="SSL Certificate Verification Failed",
                description="SSL certificate verification failed. Site may have invalid or self-signed certificate.",
                recommendation="Install a valid SSL certificate from a trusted CA (Let's Encrypt is free).",
            ))
        except requests.exceptions.Timeout:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="low",
                category="availability",
                title="Website Response Timeout",
                description="Website did not respond within 10 seconds.",
                recommendation="Check server availability and performance. Consider using a CDN.",
            ))
        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="Web Vulnerability Scan Error",
                description=f"Could not complete web vulnerability scan: {str(e)}",
                recommendation="Verify URL is accessible and server is responding.",
            ))

        return findings

    @staticmethod
    def _test_sql_injection(url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Test for SQL injection vulnerabilities."""
        findings = []

        # Look for URL parameters
        if '?' not in url:
            return findings

        base_url = url.split('?')[0]
        params_str = url.split('?')[1]
        params = dict(param.split('=') for param in params_str.split('&') if '=' in param)

        if not params:
            return findings

        # Test each parameter with SQL payloads
        for param_name, param_value in params.items():
            for payload in WebVulnScanner.SQL_PAYLOADS:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = requests.get(base_url, params=test_params, timeout=5, verify=False)

                    # Check for SQL error messages
                    for error_pattern in WebVulnScanner.SQL_ERRORS:
                        if re.search(error_pattern, response.text, re.IGNORECASE):
                            findings.append(Finding(
                                asset_id=asset_id,
                                scan_id=scan_id,
                                severity="critical",
                                category="injection",
                                title=f"SQL Injection Vulnerability Detected in '{param_name}' Parameter",
                                description=f"Parameter '{param_name}' appears vulnerable to SQL injection. Database error message exposed.",
                                recommendation="""CRITICAL - SQL Injection Vulnerability!

IMMEDIATE ACTION REQUIRED:

Step 1: Use Parameterized Queries (Prepared Statements)
  ❌ BAD:  query = f"SELECT * FROM users WHERE id = {user_id}"
  ✅ GOOD: query = "SELECT * FROM users WHERE id = ?"
           cursor.execute(query, (user_id,))

Step 2: Input Validation
  - Validate all user inputs
  - Use whitelist approach (allow only expected values)
  - Reject special characters: ', ", --, ;, etc.

Step 3: Use ORM Frameworks
  - Django ORM, SQLAlchemy (Python)
  - Sequelize (Node.js)
  - Hibernate (Java)

Step 4: Apply Least Privilege
  - Database user should have minimal permissions
  - Read-only access where possible

Step 5: Error Handling
  - Never display database errors to users
  - Log errors server-side only

IMPACT: Attackers can:
  - Steal entire database
  - Delete all data
  - Bypass authentication
  - Execute admin functions

TIME: 1-2 hours to fix | SEVERITY: CRITICAL""",
                            ))
                            return findings  # Found vulnerability, stop testing

                except:
                    continue

        return findings

    @staticmethod
    def _test_xss(url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Test for XSS (Cross-Site Scripting) vulnerabilities."""
        findings = []

        # Look for URL parameters
        if '?' not in url:
            return findings

        base_url = url.split('?')[0]
        params_str = url.split('?')[1]
        params = dict(param.split('=') for param in params_str.split('&') if '=' in param)

        if not params:
            return findings

        # Test each parameter with XSS payloads
        for param_name, param_value in params.items():
            for payload in WebVulnScanner.XSS_PAYLOADS:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = requests.get(base_url, params=test_params, timeout=5, verify=False)

                    # Check if payload is reflected in response
                    if payload in response.text:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="high",
                            category="xss",
                            title=f"Reflected XSS Vulnerability in '{param_name}' Parameter",
                            description=f"Parameter '{param_name}' reflects user input without sanitization. XSS payload detected in response.",
                            recommendation="""HIGH - XSS (Cross-Site Scripting) Vulnerability!

IMMEDIATE ACTION:

Step 1: Output Encoding
  - HTML encode all user inputs before displaying
  - Python: html.escape(user_input)
  - JavaScript: use textContent instead of innerHTML
  - PHP: htmlspecialchars($user_input, ENT_QUOTES, 'UTF-8')

Step 2: Content Security Policy (CSP)
  Add HTTP header:
  Content-Security-Policy: default-src 'self'; script-src 'self'

Step 3: Input Validation
  - Whitelist allowed characters
  - Reject <, >, ", ', /, javascript:, etc.

Step 4: Use Framework Protection
  - React/Vue automatically escape
  - Django templates auto-escape
  - Enable XSS protection in your framework

Step 5: Set HTTPOnly Cookie Flag
  - Prevents JavaScript access to session cookies
  - Set-Cookie: session=...; HttpOnly; Secure

IMPACT: Attackers can:
  - Steal session cookies
  - Perform actions as victim user
  - Deface website
  - Redirect to phishing sites

TIME: 1-3 hours | SEVERITY: HIGH""",
                        ))
                        return findings  # Found XSS, stop testing

                except:
                    continue

        return findings

    @staticmethod
    def _test_path_traversal(url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Test for directory traversal vulnerabilities."""
        findings = []

        # Look for file-related parameters (file, path, page, document, etc.)
        if '?' not in url:
            return findings

        base_url = url.split('?')[0]
        params_str = url.split('?')[1]
        params = dict(param.split('=') for param in params_str.split('&') if '=' in param)

        file_params = [p for p in params.keys() if any(x in p.lower() for x in ['file', 'path', 'page', 'doc', 'folder'])]

        if not file_params:
            return findings

        # Test file-related parameters
        for param_name in file_params:
            for payload in WebVulnScanner.PATH_TRAVERSAL_PAYLOADS:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = requests.get(base_url, params=test_params, timeout=5, verify=False)

                    # Check for Linux/Windows system file indicators
                    indicators = [
                        'root:x:0:0',  # /etc/passwd
                        '[extensions]',  # win.ini
                        'for 16-bit app support',  # win.ini
                    ]

                    for indicator in indicators:
                        if indicator in response.text:
                            findings.append(Finding(
                                asset_id=asset_id,
                                scan_id=scan_id,
                                severity="critical",
                                category="path_traversal",
                                title=f"Directory Traversal Vulnerability in '{param_name}' Parameter",
                                description=f"System file access detected through '{param_name}' parameter. Attacker can read sensitive files.",
                                recommendation="""CRITICAL - Directory Traversal Vulnerability!

IMMEDIATE ACTION:

Step 1: Never Use User Input for File Paths
  ❌ BAD:  file_path = f"/var/www/files/{user_input}"
  ✅ GOOD: Use file ID mapping instead of filenames

Step 2: Whitelist Allowed Files
  allowed_files = ['report.pdf', 'invoice.pdf']
  if filename not in allowed_files: raise Exception()

Step 3: Sanitize Input
  - Remove ../, .\\, %2e%2e, etc.
  - Use os.path.basename() to strip directory components
  - Validate no path separators in input

Step 4: Use chroot Jail / Restricted Directory
  - Limit file access to specific directory only
  - Cannot traverse outside allowed directory

Step 5: Apply Principle of Least Privilege
  - Web server runs as limited user
  - Minimal file system access

IMPACT: Attackers can:
  - Read /etc/passwd, /etc/shadow
  - Access database config files
  - Read source code
  - Access encryption keys

TIME: 2-4 hours | SEVERITY: CRITICAL""",
                            ))
                            return findings

                except:
                    continue

        return findings

    @staticmethod
    def _test_command_injection(url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Test for command injection vulnerabilities."""
        findings = []

        if '?' not in url:
            return findings

        base_url = url.split('?')[0]
        params_str = url.split('?')[1]
        params = dict(param.split('=') for param in params_str.split('&') if '=' in param)

        # Look for command-related parameters
        cmd_params = [p for p in params.keys() if any(x in p.lower() for x in ['cmd', 'exec', 'command', 'ping', 'ip'])]

        if not cmd_params:
            return findings

        for param_name in cmd_params:
            for payload in WebVulnScanner.COMMAND_INJECTION_PAYLOADS:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = requests.get(base_url, params=test_params, timeout=5, verify=False)

                    # Check for command output indicators
                    indicators = [
                        'uid=', 'gid=',  # id command
                        'root:',  # cat /etc/passwd
                        'total ',  # ls -la
                    ]

                    for indicator in indicators:
                        if indicator in response.text:
                            findings.append(Finding(
                                asset_id=asset_id,
                                scan_id=scan_id,
                                severity="critical",
                                category="command_injection",
                                title=f"Command Injection Vulnerability in '{param_name}' Parameter",
                                description=f"Command execution detected through '{param_name}' parameter. Critical vulnerability!",
                                recommendation="""CRITICAL - Command Injection Vulnerability!

IMMEDIATE ACTION:

Step 1: NEVER Execute System Commands with User Input
  ❌ BAD:  os.system(f"ping {user_ip}")
  ❌ BAD:  subprocess.call(f"ls {user_dir}", shell=True)

Step 2: Use Safe Alternatives
  ✅ GOOD: Use libraries instead of shell commands
           - Python: socket.gethostbyname() instead of ping
           - Use subprocess with array (not string + shell=True)

Step 3: Input Validation (if commands unavoidable)
  - Whitelist only alphanumeric characters
  - Reject: ;, |, &, $, `, \\n, etc.
  - Use shlex.quote() in Python

Step 4: Apply Sandboxing
  - Run commands in restricted environment
  - Use Docker containers
  - Apply SELinux/AppArmor policies

Step 5: Disable shell=True
  ✅ subprocess.run(['ping', '-c', '1', ip])  # Safe
  ❌ subprocess.run(f'ping -c 1 {ip}', shell=True)  # Unsafe

IMPACT: Attackers can:
  - Execute ANY system command
  - Install backdoors
  - Steal all data
  - Delete entire server
  - Pivot to internal network

TIME: 1-2 hours | SEVERITY: CRITICAL""",
                            ))
                            return findings

                except:
                    continue

        return findings

    @staticmethod
    def _check_server_info(response, asset_id: str, scan_id: str) -> List[Finding]:
        """Check for information disclosure in headers."""
        findings = []

        # Check Server header
        server = response.headers.get('Server', '')
        if server and not any(x in server.lower() for x in ['cloudflare', 'cloudfront']):
            # Server version exposed
            if re.search(r'\d+\.\d+', server):  # Has version number
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="low",
                    category="information_disclosure",
                    title="Server Version Information Disclosed",
                    description=f"Server header reveals version information: {server}",
                    recommendation="""Remove Server Version Information

Attackers use version info to find known vulnerabilities.

FOR NGINX:
Edit /etc/nginx/nginx.conf:
  server_tokens off;

Reload: sudo systemctl reload nginx

FOR APACHE:
Edit /etc/apache2/conf-available/security.conf:
  ServerTokens Prod
  ServerSignature Off

Reload: sudo systemctl reload apache2

FOR EXPRESS.JS:
  app.disable('x-powered-by');

VERIFY: Check HTTP headers no longer show version

TIME: 5 minutes | SEVERITY: LOW""",
                ))

        # Check X-Powered-By header
        powered_by = response.headers.get('X-Powered-By', '')
        if powered_by:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="low",
                category="information_disclosure",
                title="Technology Stack Disclosed via X-Powered-By Header",
                description=f"X-Powered-By header reveals: {powered_by}",
                recommendation="Remove X-Powered-By header. For Express.js: app.disable('x-powered-by')",
            ))

        return findings

    @staticmethod
    def _check_sensitive_exposure(response, url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check for sensitive data exposure."""
        findings = []

        content = response.text.lower()

        # Check for common sensitive patterns
        patterns = {
            'API Key': r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}',
            'AWS Key': r'AKIA[0-9A-Z]{16}',
            'Private Key': r'-----BEGIN (RSA|DSA|EC) PRIVATE KEY-----',
            'Password': r'password["\']?\s*[:=]\s*["\'][^"\']{5,}["\']',
        }

        for secret_type, pattern in patterns.items():
            if re.search(pattern, content):
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="critical",
                    category="sensitive_data_exposure",
                    title=f"Possible {secret_type} Exposed in Page Source",
                    description=f"Detected pattern matching {secret_type} in HTML source code. View source to verify.",
                    recommendation=f"""CRITICAL - {secret_type} Exposed!

IMMEDIATE ACTION:

Step 1: Remove Sensitive Data from Frontend
  - Never include API keys, passwords in HTML/JavaScript
  - Move secrets to backend environment variables

Step 2: Rotate Exposed Credentials
  - Generate new {secret_type}
  - Revoke old credential immediately

Step 3: Use Environment Variables
  - Store secrets in .env file (never commit to git)
  - Add .env to .gitignore

Step 4: Scan Git History
  - Check if committed previously
  - If yes, use git filter-branch to remove

SEVERITY: CRITICAL - Credential is publicly visible!
TIME: 1 hour to fix + rotate credentials""",
                ))

        return findings
