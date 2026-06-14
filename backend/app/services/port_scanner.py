"""Comprehensive Port Scanner with Service Detection"""
import socket
import concurrent.futures
from typing import List, Dict, Tuple
from datetime import datetime, timezone

from app.models.scan import Finding


class PortScanner:
    """Advanced port scanner with service detection and vulnerability mapping."""

    # Common ports to scan (top 100 most used)
    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
        1433, 1521, 1723, 3306, 3389, 5432, 5900, 6379, 8000, 8080, 8443, 8888,
        9000, 9090, 27017, 27018, 50000
    ]

    # Service detection patterns
    SERVICE_BANNERS = {
        21: ("FTP", "File Transfer Protocol"),
        22: ("SSH", "Secure Shell"),
        23: ("Telnet", "Telnet (INSECURE)"),
        25: ("SMTP", "Email Server"),
        53: ("DNS", "Domain Name System"),
        80: ("HTTP", "Web Server"),
        110: ("POP3", "Email (POP3)"),
        111: ("RPC", "RPC Bind"),
        135: ("MSRPC", "Microsoft RPC"),
        139: ("NetBIOS", "Windows File Sharing"),
        143: ("IMAP", "Email (IMAP)"),
        443: ("HTTPS", "Secure Web Server"),
        445: ("SMB", "Windows File Sharing"),
        993: ("IMAPS", "Secure Email (IMAPS)"),
        995: ("POP3S", "Secure Email (POP3S)"),
        1433: ("MSSQL", "Microsoft SQL Server"),
        1521: ("Oracle", "Oracle Database"),
        1723: ("PPTP", "VPN (PPTP)"),
        3306: ("MySQL", "MySQL Database"),
        3389: ("RDP", "Remote Desktop"),
        5432: ("PostgreSQL", "PostgreSQL Database"),
        5900: ("VNC", "VNC Remote Desktop"),
        6379: ("Redis", "Redis Database"),
        8000: ("HTTP-Alt", "Alternative HTTP"),
        8080: ("HTTP-Proxy", "HTTP Proxy"),
        8443: ("HTTPS-Alt", "Alternative HTTPS"),
        8888: ("HTTP-Alt", "Alternative HTTP"),
        9000: ("HTTP-Alt", "Alternative HTTP"),
        9090: ("HTTP-Alt", "Alternative HTTP"),
        27017: ("MongoDB", "MongoDB Database"),
        27018: ("MongoDB", "MongoDB Shard"),
        50000: ("SAP", "SAP System"),
    }

    # Critical/dangerous open ports
    DANGEROUS_PORTS = {
        23: "Telnet - Transmits passwords in plaintext",
        21: "FTP - Often misconfigured, allows anonymous access",
        445: "SMB - Target for ransomware (WannaCry, NotPetya)",
        3389: "RDP - Brute force target",
        1433: "MSSQL - Database should not be internet-facing",
        3306: "MySQL - Database should not be internet-facing",
        5432: "PostgreSQL - Database should not be internet-facing",
        27017: "MongoDB - Often left without authentication",
        6379: "Redis - Often configured without password",
        5900: "VNC - Weak authentication",
    }

    @staticmethod
    def scan(target: str, asset_id: str, scan_id: str, full_scan: bool = False) -> List[Finding]:
        """
        Scan target for open ports and services.

        Args:
            target: IP address or hostname
            asset_id: Asset UUID
            scan_id: Scan UUID
            full_scan: If True, scan all 65535 ports (takes longer)

        Returns:
            List of Finding objects
        """
        findings = []

        # Clean target (remove protocol, path)
        target = PortScanner._clean_target(target)

        if not target:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="configuration",
                title="Invalid Port Scan Target",
                description="Could not extract valid hostname/IP from target",
                recommendation="Provide valid hostname or IP address",
                created_at=datetime.now(timezone.utc)
            ))
            return findings

        # Determine ports to scan
        ports_to_scan = list(range(1, 65536)) if full_scan else PortScanner.COMMON_PORTS

        # Scan ports
        open_ports = PortScanner._scan_ports(target, ports_to_scan)

        if not open_ports:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="network",
                title="No Open Ports Detected",
                description=f"Scanned {len(ports_to_scan)} ports on {target}, none are open or firewall is blocking.",
                recommendation="Good! Minimal attack surface. Ensure only necessary services are running.",
                created_at=datetime.now(timezone.utc)
            ))
            return findings

        # Analyze open ports
        findings.extend(PortScanner._analyze_open_ports(target, open_ports, asset_id, scan_id))

        return findings

    @staticmethod
    def _clean_target(target: str) -> str:
        """Extract hostname/IP from target string."""
        target = target.strip()

        # Remove protocol
        if '://' in target:
            target = target.split('://')[1]

        # Remove path
        if '/' in target:
            target = target.split('/')[0]

        # Remove port if present
        if ':' in target and not target.count(':') > 1:  # Not IPv6
            target = target.split(':')[0]

        return target

    @staticmethod
    def _scan_ports(target: str, ports: List[int], timeout: float = 1.0) -> List[Tuple[int, str]]:
        """
        Scan list of ports and return open ones.

        Returns:
            List of (port, service_name) tuples
        """
        open_ports = []

        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                sock.close()

                if result == 0:
                    service_name = PortScanner.SERVICE_BANNERS.get(port, ("Unknown", "Unknown Service"))[0]
                    return (port, service_name)
            except:
                pass
            return None

        # Use thread pool for faster scanning
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(scan_port, ports)
            open_ports = [r for r in results if r is not None]

        return open_ports

    @staticmethod
    def _analyze_open_ports(target: str, open_ports: List[Tuple[int, str]], asset_id: str, scan_id: str) -> List[Finding]:
        """Analyze open ports and generate findings."""
        findings = []

        # Summary finding
        port_list = ', '.join([f"{port} ({service})" for port, service in open_ports])
        findings.append(Finding(
            asset_id=asset_id,
            scan_id=scan_id,
            severity="info",
            category="network",
            title=f"{len(open_ports)} Open Ports Detected",
            description=f"Open ports on {target}: {port_list}",
            recommendation="Review all open ports. Close unnecessary services to reduce attack surface.",
            created_at=datetime.now(timezone.utc)
        ))

        # Check each port for security issues
        for port, service in open_ports:
            if port in PortScanner.DANGEROUS_PORTS:
                risk_description = PortScanner.DANGEROUS_PORTS[port]
                severity = "critical" if port in [23, 445, 3389, 27017, 6379] else "high"

                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity=severity,
                    category="exposed_service",
                    title=f"Dangerous Port {port} ({service}) Is Open",
                    description=f"Port {port} ({service}) is exposed to the internet. {risk_description}",
                    recommendation=PortScanner._get_port_remediation(port, service),
                    created_at=datetime.now(timezone.utc)
                ))

        # Check for database ports
        db_ports = [p for p, s in open_ports if p in [1433, 3306, 5432, 27017, 6379]]
        if db_ports:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="critical",
                category="exposed_service",
                title="Database Ports Exposed to Internet",
                description=f"Database ports {', '.join(map(str, db_ports))} are accessible from the internet. Critical risk!",
                recommendation="""CRITICAL - Database Exposed to Internet!

IMMEDIATE ACTION:

Step 1: Block Database Ports at Firewall
  Databases should NEVER be internet-facing.

  AWS Security Group:
  - Remove 0.0.0.0/0 inbound rule
  - Allow only from application server IPs

  Linux iptables:
  sudo iptables -A INPUT -p tcp --dport 3306 -s 10.0.0.0/8 -j ACCEPT
  sudo iptables -A INPUT -p tcp --dport 3306 -j DROP

Step 2: Use VPN/Bastion for Remote Access
  - Never expose database directly
  - Use SSH tunnel or VPN

Step 3: Enable Authentication
  - MySQL: Require strong passwords
  - MongoDB: Enable --auth
  - Redis: requirepass directive

Step 4: Network Segmentation
  - Place database in private subnet
  - Only application tier can access

IMPACT: Direct internet access to database = data breach

TIME: 30 minutes | SEVERITY: CRITICAL""",
                created_at=datetime.now(timezone.utc)
            ))

        # Check for remote access ports
        remote_ports = [p for p, s in open_ports if p in [22, 3389, 5900, 23]]
        if remote_ports:
            telnet_open = 23 in remote_ports

            if telnet_open:
                severity = "critical"
                title = "Telnet (Port 23) Is Open - INSECURE!"
            elif 3389 in remote_ports:
                severity = "high"
                title = "Remote Desktop (RDP) Exposed to Internet"
            else:
                severity = "medium"
                title = "Remote Access Ports Detected"

            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity=severity,
                category="remote_access",
                title=title,
                description=f"Remote access ports {', '.join(map(str, remote_ports))} are open.",
                recommendation="""Secure Remote Access

Step 1: Disable Telnet (if port 23 open)
  Telnet sends passwords in plaintext. Use SSH instead.
  sudo systemctl stop telnet
  sudo systemctl disable telnet

Step 2: Restrict SSH/RDP Access
  - Limit to specific IP addresses (office, VPN)
  - Use SSH keys instead of passwords
  - Change default port (security through obscurity)

Step 3: Enable Fail2Ban
  Auto-ban IPs after failed login attempts:
  sudo apt-get install fail2ban

Step 4: Use VPN for Remote Access
  - Never expose RDP/SSH to 0.0.0.0/0
  - Require VPN connection first

Step 5: Enable MFA (Multi-Factor Authentication)
  - SSH: Google Authenticator PAM module
  - RDP: Windows MFA

TIME: 1-2 hours | SEVERITY: MEDIUM-HIGH""",
                created_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _get_port_remediation(port: int, service: str) -> str:
        """Get specific remediation for dangerous port."""
        remediations = {
            23: """CRITICAL - Disable Telnet Immediately!

Telnet transmits ALL data (including passwords) in plaintext.

Step 1: Disable Telnet Service
  sudo systemctl stop telnet
  sudo systemctl disable telnet

Step 2: Use SSH Instead
  sudo apt-get install openssh-server
  sudo systemctl start ssh

Step 3: Block Port 23 at Firewall
  sudo iptables -A INPUT -p tcp --dport 23 -j DROP

NEVER use Telnet. Always use SSH (port 22) with encryption.

TIME: 10 minutes | SEVERITY: CRITICAL""",

            445: """CRITICAL - SMB Port 445 Exposed!

Port 445 was exploited by WannaCry and NotPetya ransomware.

Step 1: Block SMB at Firewall
  Should only be accessible within local network

  Linux:
  sudo iptables -A INPUT -p tcp --dport 445 -s 192.168.0.0/16 -j ACCEPT
  sudo iptables -A INPUT -p tcp --dport 445 -j DROP

  Windows Firewall:
  - Block 445 from public networks
  - Allow only from private/domain networks

Step 2: Keep SMB Updated
  Install latest security patches

Step 3: Disable SMBv1
  SMBv1 has critical vulnerabilities
  Windows: Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol

TIME: 20 minutes | SEVERITY: CRITICAL""",

            3389: """HIGH - RDP Exposed to Internet!

RDP is #1 target for brute force attacks and ransomware.

Step 1: Restrict RDP Access
  - Use VPN for remote access
  - Or whitelist specific IPs only

Step 2: Change Default Port (Optional)
  Change from 3389 to custom port

Step 3: Enable Network Level Authentication (NLA)
  Requires authentication before RDP session starts

Step 4: Use Strong Passwords + MFA
  - 15+ character passwords
  - Enable multi-factor authentication

Step 5: Monitor Failed Logins
  Event ID 4625 in Security log

TIME: 30 minutes | SEVERITY: HIGH""",

            27017: """CRITICAL - MongoDB Exposed Without Authentication!

Thousands of MongoDB databases have been wiped by attackers.

Step 1: Enable Authentication
  Edit /etc/mongod.conf:
    security:
      authorization: enabled

  Create admin user:
  use admin
  db.createUser({user: "admin", pwd: "strong_password", roles: ["root"]})

Step 2: Block Port from Internet
  sudo iptables -A INPUT -p tcp --dport 27017 -s 10.0.0.0/8 -j ACCEPT
  sudo iptables -A INPUT -p tcp --dport 27017 -j DROP

Step 3: Bind to Localhost Only
  bindIp: 127.0.0.1

Step 4: Use VPN for Remote Access
  Never expose MongoDB directly to internet

TIME: 15 minutes | SEVERITY: CRITICAL""",

            6379: """CRITICAL - Redis Exposed Without Password!

Redis defaults to no authentication. Mass exploitation underway.

Step 1: Set Password
  Edit /etc/redis/redis.conf:
    requirepass your_strong_password_here

  Restart: sudo systemctl restart redis

Step 2: Bind to Localhost
  bind 127.0.0.1

Step 3: Block Port 6379 from Internet
  sudo iptables -A INPUT -p tcp --dport 6379 -j DROP

Step 4: Disable Dangerous Commands
  rename-command CONFIG ""
  rename-command FLUSHALL ""
  rename-command FLUSHDB ""

TIME: 10 minutes | SEVERITY: CRITICAL""",
        }

        return remediations.get(port, f"Close port {port} ({service}) if not required. Review firewall rules.")
