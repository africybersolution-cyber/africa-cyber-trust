"""Email Domain Security Scanner - SPF, DKIM, DMARC validation"""
import dns.resolver
import re
from typing import List
from datetime import datetime, timezone

from app.models.scan import Finding


class EmailDomainScanner:
    """Scan email domains for SPF, DKIM, DMARC security records."""

    @staticmethod
    def scan(domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """
        Scan email domain for email security configuration.

        Checks:
        - SPF (Sender Policy Framework)
        - DMARC (Domain-based Message Authentication)
        - MX records
        """
        findings = []

        # Clean domain (remove @ prefix if present)
        domain = domain.strip().lstrip("@")

        # Check SPF
        findings.extend(EmailDomainScanner._check_spf(domain, asset_id, scan_id))

        # Check DMARC
        findings.extend(EmailDomainScanner._check_dmarc(domain, asset_id, scan_id))

        # Check MX records
        findings.extend(EmailDomainScanner._check_mx(domain, asset_id, scan_id))

        return findings

    @staticmethod
    def _check_spf(domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check SPF record."""
        findings = []

        try:
            # Query TXT records for SPF
            answers = dns.resolver.resolve(domain, 'TXT')
            spf_records = [str(rdata) for rdata in answers if 'v=spf1' in str(rdata)]

            if not spf_records:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="high",
                    category="email_security",
                    title="No SPF Record Found",
                    description=f"Domain '{domain}' has no SPF record. Emails may be marked as spam or spoofed by attackers.",
                    recommendation="""Add SPF Record to Prevent Email Spoofing

Step 1: Identify Your Email Sending Sources
  - Your mail server IPs
  - Third-party services (Gmail, SendGrid, Mailchimp, etc.)

Step 2: Create SPF Record
  Basic example for Gmail:
  v=spf1 include:_spf.google.com ~all

  For multiple sources:
  v=spf1 ip4:203.0.113.1 include:_spf.google.com include:sendgrid.net ~all

Step 3: Add TXT Record to DNS
  - Login to your DNS provider (Namecheap, GoDaddy, etc.)
  - Add TXT record for @ (root domain)
  - Value: v=spf1 include:_spf.google.com ~all
  - TTL: 3600

Step 4: Verify
  dig TXT yourdomain.com
  or use: https://mxtoolbox.com/spf.aspx

IMPORTANCE: Without SPF, attackers can easily spoof your domain

TIME: 10 minutes | SEVERITY: HIGH""",
                    created_at=datetime.now(timezone.utc)
                ))
            else:
                spf_record = spf_records[0].strip('"')

                # Check if SPF is too permissive
                if '+all' in spf_record or '?all' in spf_record:
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="critical",
                        category="email_security",
                        title="Dangerously Permissive SPF Record",
                        description=f"SPF record allows anyone to send email as your domain: {spf_record}",
                        recommendation="""Fix Overly Permissive SPF Record

PROBLEM: '+all' or '?all' allows ANY server to send email as your domain

Step 1: Update SPF to use '~all' (soft fail) or '-all' (hard fail)

  Current (DANGEROUS):
  v=spf1 +all

  Recommended:
  v=spf1 include:_spf.google.com ~all

Step 2: Update DNS TXT record
  - Remove '+all' or '?all'
  - Replace with '~all' or '-all'

Step 3: Test before deploying '-all'
  - Use '~all' (soft fail) for 1-2 weeks
  - Monitor email delivery
  - Then switch to '-all' (hard fail)

VERIFICATION: Check at mxtoolbox.com/spf.aspx

TIME: 5 minutes | SEVERITY: CRITICAL""",
                        created_at=datetime.now(timezone.utc)
                    ))
                elif '~all' in spf_record or '-all' in spf_record:
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="info",
                        category="email_security",
                        title="SPF Record Configured",
                        description=f"SPF record found and properly configured: {spf_record}",
                        recommendation="SPF is correctly configured. Monitor for any authorized sending sources that need to be added.",
                        created_at=datetime.now(timezone.utc)
                    ))

        except dns.resolver.NXDOMAIN:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="medium",
                category="dns",
                title="Domain Does Not Exist",
                description=f"Domain '{domain}' does not exist or DNS is misconfigured.",
                recommendation="Verify domain name spelling and DNS configuration.",
                created_at=datetime.now(timezone.utc)
            ))
        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="SPF Check Error",
                description=f"Could not check SPF record: {str(e)}",
                recommendation="Verify DNS is accessible and domain is correct.",
                created_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _check_dmarc(domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check DMARC record."""
        findings = []

        try:
            # DMARC record is at _dmarc.domain.com
            dmarc_domain = f"_dmarc.{domain}"
            answers = dns.resolver.resolve(dmarc_domain, 'TXT')
            dmarc_records = [str(rdata).strip('"') for rdata in answers if 'v=DMARC1' in str(rdata)]

            if not dmarc_records:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="high",
                    category="email_security",
                    title="No DMARC Record Found",
                    description=f"Domain '{domain}' has no DMARC policy. Email authentication cannot be enforced.",
                    recommendation="""Add DMARC Record for Email Protection

Step 1: Create DMARC Policy
  Basic (monitoring only):
  v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com

  Recommended (enforce):
  v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; pct=100

  Strict (reject):
  v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com; pct=100

Step 2: Add DNS TXT Record
  - Hostname: _dmarc
  - Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
  - TTL: 3600

Step 3: Monitor Reports
  - Reports sent to email in 'rua' tag
  - Review for 2-4 weeks with p=none
  - Then switch to p=quarantine or p=reject

Step 4: Verify
  dig TXT _dmarc.yourdomain.com

IMPORTANCE: DMARC prevents email spoofing and phishing

TIME: 15 minutes | SEVERITY: HIGH""",
                    created_at=datetime.now(timezone.utc)
                ))
            else:
                dmarc_record = dmarc_records[0]

                # Check DMARC policy strictness
                if 'p=none' in dmarc_record:
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="medium",
                        category="email_security",
                        title="DMARC Policy Set to None (Monitoring Only)",
                        description=f"DMARC is in monitoring mode only, not enforcing: {dmarc_record}",
                        recommendation="""Upgrade DMARC to Enforcement Mode

Current: p=none (only monitors, doesn't protect)

Step 1: Review DMARC Reports
  - Check reports from 'rua' email for 2 weeks
  - Identify all legitimate senders

Step 2: Update to Quarantine
  v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; pct=100

Step 3: Monitor for 2 weeks
  - Ensure no legitimate emails blocked

Step 4: Consider 'reject' for maximum security
  v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com; pct=100

TIME: Update takes 5 min, monitoring takes 2-4 weeks""",
                        created_at=datetime.now(timezone.utc)
                    ))
                elif 'p=quarantine' in dmarc_record or 'p=reject' in dmarc_record:
                    policy = 'quarantine' if 'p=quarantine' in dmarc_record else 'reject'
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="info",
                        category="email_security",
                        title=f"DMARC Enforced ({policy.upper()} Policy)",
                        description=f"DMARC is properly configured with {policy} policy: {dmarc_record}",
                        recommendation="Excellent! Continue monitoring DMARC reports and update SPF/DKIM as needed.",
                        created_at=datetime.now(timezone.utc)
                    ))

        except dns.resolver.NXDOMAIN:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="high",
                category="email_security",
                title="No DMARC Record Found",
                description=f"No DMARC record at _dmarc.{domain}",
                recommendation="Add DMARC record to prevent email spoofing. See SPF recommendation for steps.",
                created_at=datetime.now(timezone.utc)
            ))
        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="DMARC Check Error",
                description=f"Could not check DMARC record: {str(e)}",
                recommendation="Verify DNS and domain configuration.",
                created_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _check_mx(domain: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check MX records."""
        findings = []

        try:
            answers = dns.resolver.resolve(domain, 'MX')
            mx_records = [str(rdata.exchange) for rdata in answers]

            if mx_records:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="email_security",
                    title="MX Records Found",
                    description=f"Domain has {len(mx_records)} MX record(s): {', '.join(mx_records[:3])}",
                    recommendation="MX records are configured. Ensure they point to your actual mail servers.",
                    created_at=datetime.now(timezone.utc)
                ))
            else:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="low",
                    category="email_security",
                    title="No MX Records",
                    description=f"Domain has no MX records. Email cannot be received.",
                    recommendation="If you need to receive email at this domain, add MX records pointing to your mail server.",
                    created_at=datetime.now(timezone.utc)
                ))

        except dns.resolver.NoAnswer:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="low",
                category="email_security",
                title="No MX Records",
                description="Domain has no MX records configured.",
                recommendation="Add MX records if you need to receive email at this domain.",
                created_at=datetime.now(timezone.utc)
            ))
        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="MX Check Error",
                description=f"Could not check MX records: {str(e)}",
                recommendation="Verify DNS configuration.",
                created_at=datetime.now(timezone.utc)
            ))

        return findings
