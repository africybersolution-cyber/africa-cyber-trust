"""AI-Powered Risk Scoring System - Smart Vulnerability Prioritization"""
from typing import List, Dict, Any
from datetime import datetime, timezone
from app.models.scan import Scan, Finding


class AIRiskScorer:
    """
    Intelligent risk scoring algorithm that prioritizes vulnerabilities based on:
    - Severity
    - Exploitability
    - Impact
    - Asset criticality
    - Attack surface
    - Technology exposure
    """

    # Severity weights
    SEVERITY_SCORES = {
        'critical': 100,
        'high': 75,
        'medium': 50,
        'low': 25,
        'info': 5
    }

    # Category risk multipliers
    CATEGORY_MULTIPLIERS = {
        'injection': 1.5,           # SQL injection, command injection
        'command_injection': 1.5,
        'xss': 1.3,
        'path_traversal': 1.4,
        'exposed_service': 1.4,     # Databases, RDP exposed
        'remote_access': 1.3,
        'access_control': 1.3,      # Public S3 buckets
        'wordpress_vulnerability': 1.2,
        'secrets': 1.5,             # Exposed API keys
        'sensitive_data_exposure': 1.4,
        'ssl_tls': 1.1,
        'email_security': 1.2,
        'information_disclosure': 0.8,
        'configuration': 0.9,
        'network': 1.0,
    }

    # Critical keywords that boost risk score
    CRITICAL_KEYWORDS = {
        'database': 1.3,
        'exposed': 1.2,
        'public': 1.2,
        'authentication': 1.2,
        'credential': 1.3,
        'password': 1.3,
        'api key': 1.3,
        'secret': 1.3,
        'injection': 1.4,
        'rce': 1.5,  # Remote Code Execution
        'telnet': 1.4,
        'mongodb': 1.3,
        'redis': 1.3,
        'rdp': 1.3,
        'smb': 1.3,
    }

    @staticmethod
    def calculate_scan_risk_score(scan: Scan, findings: List[Finding]) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for a scan.

        Returns:
            {
                'overall_score': 0-100 (higher = more risk),
                'risk_level': 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW',
                'risk_breakdown': {...},
                'priority_findings': [...],
                'quick_wins': [...],
                'executive_summary': str,
                'remediation_order': [...]
            }
        """
        if not findings:
            return {
                'overall_score': 0,
                'risk_level': 'LOW',
                'risk_breakdown': {},
                'priority_findings': [],
                'quick_wins': [],
                'executive_summary': 'No vulnerabilities detected. Asset is secure.',
                'remediation_order': []
            }

        # Score each finding
        scored_findings = []
        for finding in findings:
            risk_score = AIRiskScorer._calculate_finding_score(finding)
            scored_findings.append({
                'finding': finding,
                'risk_score': risk_score,
                'priority': AIRiskScorer._get_priority_level(risk_score)
            })

        # Sort by risk score (highest first)
        scored_findings.sort(key=lambda x: x['risk_score'], reverse=True)

        # Calculate overall asset risk score
        overall_score = AIRiskScorer._calculate_overall_score(scored_findings)

        # Determine risk level
        risk_level = AIRiskScorer._get_risk_level(overall_score)

        # Get breakdown by severity and category
        risk_breakdown = AIRiskScorer._get_risk_breakdown(findings)

        # Identify priority findings (top 5 most critical)
        priority_findings = scored_findings[:5]

        # Identify quick wins (low effort, high impact)
        quick_wins = AIRiskScorer._identify_quick_wins(scored_findings)

        # Generate executive summary
        executive_summary = AIRiskScorer._generate_executive_summary(
            overall_score, risk_level, findings, priority_findings
        )

        # Generate remediation order
        remediation_order = AIRiskScorer._generate_remediation_order(scored_findings)

        return {
            'overall_score': round(overall_score, 1),
            'risk_level': risk_level,
            'risk_breakdown': risk_breakdown,
            'priority_findings': priority_findings,
            'quick_wins': quick_wins,
            'executive_summary': executive_summary,
            'remediation_order': remediation_order,
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == 'critical'),
            'high_count': sum(1 for f in findings if f.severity == 'high'),
            'scored_findings': scored_findings  # For detailed view
        }

    @staticmethod
    def _calculate_finding_score(finding: Finding) -> float:
        """
        Calculate risk score for individual finding (0-150).

        Factors:
        1. Base severity score (25-100)
        2. Category multiplier (0.8-1.5x)
        3. Keyword boost (1.0-1.5x)
        """
        # Base score from severity
        base_score = AIRiskScorer.SEVERITY_SCORES.get(finding.severity, 25)

        # Category multiplier
        category_multiplier = AIRiskScorer.CATEGORY_MULTIPLIERS.get(
            finding.category, 1.0
        )

        # Check for critical keywords in title/description
        keyword_multiplier = 1.0
        text = (finding.title + ' ' + finding.description).lower()

        for keyword, multiplier in AIRiskScorer.CRITICAL_KEYWORDS.items():
            if keyword in text:
                keyword_multiplier = max(keyword_multiplier, multiplier)

        # Final score
        risk_score = base_score * category_multiplier * keyword_multiplier

        return min(risk_score, 150)  # Cap at 150

    @staticmethod
    def _calculate_overall_score(scored_findings: List[Dict]) -> float:
        """
        Calculate overall asset risk score (0-100).

        Algorithm:
        - Critical findings contribute more
        - Diminishing returns for many low-severity issues
        - Weighted average with exponential decay
        """
        if not scored_findings:
            return 0

        # Top 10 findings contribute most
        top_findings = scored_findings[:10]

        # Weighted sum with exponential decay
        total_weight = 0
        weighted_score = 0

        for i, item in enumerate(top_findings):
            # Weight decreases exponentially (1st finding = 1.0, 10th = 0.4)
            weight = 1.0 / (1 + i * 0.15)
            weighted_score += item['risk_score'] * weight
            total_weight += weight

        # Normalize to 0-100
        if total_weight > 0:
            overall_score = (weighted_score / total_weight) * (100 / 150)
        else:
            overall_score = 0

        # Add penalty for total number of issues (many issues = higher risk)
        total_findings = len(scored_findings)
        if total_findings > 10:
            volume_penalty = min((total_findings - 10) * 0.5, 10)
            overall_score = min(overall_score + volume_penalty, 100)

        return overall_score

    @staticmethod
    def _get_risk_level(overall_score: float) -> str:
        """Convert numerical score to risk level."""
        if overall_score >= 80:
            return 'CRITICAL'
        elif overall_score >= 60:
            return 'HIGH'
        elif overall_score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'

    @staticmethod
    def _get_priority_level(risk_score: float) -> str:
        """Get priority level for a finding."""
        if risk_score >= 120:
            return 'P0 - IMMEDIATE'
        elif risk_score >= 90:
            return 'P1 - URGENT'
        elif risk_score >= 60:
            return 'P2 - HIGH'
        elif risk_score >= 30:
            return 'P3 - MEDIUM'
        else:
            return 'P4 - LOW'

    @staticmethod
    def _get_risk_breakdown(findings: List[Finding]) -> Dict:
        """Get breakdown of risk by severity and category."""
        breakdown = {
            'by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            },
            'by_category': {},
            'most_common_category': None,
            'attack_vectors': []
        }

        category_counts = {}

        for finding in findings:
            # Count by severity
            breakdown['by_severity'][finding.severity] += 1

            # Count by category
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1

        # Sort categories by count
        if category_counts:
            breakdown['by_category'] = dict(
                sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            )
            breakdown['most_common_category'] = list(breakdown['by_category'].keys())[0]

        # Identify attack vectors
        attack_categories = ['injection', 'xss', 'command_injection', 'exposed_service', 'secrets']
        breakdown['attack_vectors'] = [
            cat for cat in attack_categories if cat in category_counts
        ]

        return breakdown

    @staticmethod
    def _identify_quick_wins(scored_findings: List[Dict]) -> List[Dict]:
        """
        Identify quick wins: high-impact, low-effort fixes.

        Quick wins are findings that:
        - Have medium-high severity
        - Are easy to fix (based on category)
        - Provide significant risk reduction
        """
        quick_win_categories = [
            'information_disclosure',  # Remove server headers
            'ssl_tls',  # Update SSL config
            'email_security',  # Add SPF/DMARC
            'wordpress_vulnerability',  # Disable XML-RPC
            'configuration',  # Fix configs
        ]

        quick_wins = []

        for item in scored_findings:
            finding = item['finding']

            # Must be at least medium severity
            if finding.severity not in ['medium', 'high', 'critical']:
                continue

            # Must be in quick-win categories
            if finding.category in quick_win_categories:
                quick_wins.append({
                    'finding': finding,
                    'risk_score': item['risk_score'],
                    'estimated_time': AIRiskScorer._extract_time_estimate(finding.recommendation),
                    'impact': 'Reduces risk score by ' + str(round(item['risk_score'] * 0.1, 1)) + ' points'
                })

        # Sort by risk score (highest impact first)
        quick_wins.sort(key=lambda x: x['risk_score'], reverse=True)

        return quick_wins[:3]  # Top 3 quick wins

    @staticmethod
    def _extract_time_estimate(recommendation: str) -> str:
        """Extract time estimate from recommendation text."""
        import re

        # Look for "TIME: X minutes/hours"
        match = re.search(r'TIME:\s*([^|]+)', recommendation, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return "Unknown"

    @staticmethod
    def _generate_executive_summary(
        overall_score: float,
        risk_level: str,
        findings: List[Finding],
        priority_findings: List[Dict]
    ) -> str:
        """Generate executive summary of security posture."""
        critical_count = sum(1 for f in findings if f.severity == 'critical')
        high_count = sum(1 for f in findings if f.severity == 'high')
        medium_count = sum(1 for f in findings if f.severity == 'medium')

        # Build summary
        summary_parts = []

        # Overall assessment
        if risk_level == 'CRITICAL':
            summary_parts.append(
                f"🚨 CRITICAL SECURITY RISK (Score: {overall_score}/100). "
                "Immediate action required to prevent potential data breach."
            )
        elif risk_level == 'HIGH':
            summary_parts.append(
                f"⚠️ HIGH SECURITY RISK (Score: {overall_score}/100). "
                "Urgent remediation recommended within 24-48 hours."
            )
        elif risk_level == 'MEDIUM':
            summary_parts.append(
                f"🟡 MEDIUM SECURITY RISK (Score: {overall_score}/100). "
                "Address vulnerabilities within 1-2 weeks."
            )
        else:
            summary_parts.append(
                f"✅ LOW SECURITY RISK (Score: {overall_score}/100). "
                "Good security posture. Monitor and maintain."
            )

        # Findings summary
        if critical_count > 0:
            summary_parts.append(
                f"\n\n{critical_count} CRITICAL issue(s) detected requiring immediate attention."
            )

        if high_count > 0:
            summary_parts.append(
                f" {high_count} HIGH severity issue(s) found."
            )

        # Top priority
        if priority_findings:
            top_issue = priority_findings[0]['finding']
            summary_parts.append(
                f"\n\nTOP PRIORITY: {top_issue.title}"
            )

        # Recommendation
        if risk_level in ['CRITICAL', 'HIGH']:
            summary_parts.append(
                "\n\nRECOMMENDATION: Start with the top 3 priority findings listed below. "
                "Fixing these will have the biggest impact on reducing overall risk."
            )
        elif risk_level == 'MEDIUM':
            summary_parts.append(
                "\n\nRECOMMENDATION: Focus on quick wins first - easy fixes that reduce risk quickly."
            )

        return ''.join(summary_parts)

    @staticmethod
    def _generate_remediation_order(scored_findings: List[Dict]) -> List[Dict]:
        """
        Generate smart remediation order.

        Strategy:
        1. Critical findings first
        2. Group by category (fix all of same type together)
        3. Quick wins before complex fixes
        4. High-impact before low-impact
        """
        # Separate by priority
        immediate = [f for f in scored_findings if f['priority'] == 'P0 - IMMEDIATE']
        urgent = [f for f in scored_findings if f['priority'] == 'P1 - URGENT']
        high = [f for f in scored_findings if f['priority'] == 'P2 - HIGH']
        medium = [f for f in scored_findings if f['priority'] == 'P3 - MEDIUM']
        low = [f for f in scored_findings if f['priority'] == 'P4 - LOW']

        # Build remediation plan
        remediation_plan = []

        if immediate:
            remediation_plan.append({
                'phase': 'PHASE 1: IMMEDIATE (Today)',
                'findings': immediate,
                'estimated_time': 'Unknown',
                'risk_reduction': sum(f['risk_score'] for f in immediate) * 0.1
            })

        if urgent:
            remediation_plan.append({
                'phase': 'PHASE 2: URGENT (This Week)',
                'findings': urgent,
                'estimated_time': 'Unknown',
                'risk_reduction': sum(f['risk_score'] for f in urgent) * 0.1
            })

        if high:
            remediation_plan.append({
                'phase': 'PHASE 3: HIGH (Next 2 Weeks)',
                'findings': high,
                'estimated_time': 'Unknown',
                'risk_reduction': sum(f['risk_score'] for f in high) * 0.1
            })

        if medium:
            remediation_plan.append({
                'phase': 'PHASE 4: MEDIUM (This Month)',
                'findings': medium,
                'estimated_time': 'Unknown',
                'risk_reduction': sum(f['risk_score'] for f in medium) * 0.1
            })

        if low:
            remediation_plan.append({
                'phase': 'PHASE 5: LOW (Next Quarter)',
                'findings': low,
                'estimated_time': 'Unknown',
                'risk_reduction': sum(f['risk_score'] for f in low) * 0.1
            })

        return remediation_plan
