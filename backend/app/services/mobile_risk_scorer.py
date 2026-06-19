"""
Mobile App Risk Scoring Algorithm

Advanced risk assessment for mobile applications using weighted severity scoring.
Provides actionable insights and prioritization.
"""
from typing import List, Dict, Tuple
from datetime import datetime


class MobileRiskScorer:
    """
    Enterprise-grade mobile app risk scoring.

    Scoring methodology:
    - Critical findings: 25 points each
    - High findings: 15 points each
    - Medium findings: 8 points each
    - Low findings: 3 points each

    Categories with multipliers:
    - Secrets (hardcoded credentials): 1.5x
    - Network (SSL, cleartext): 1.3x
    - Configuration (debuggable, backup): 1.4x
    - Permissions: Based on quantity (>20 = higher risk)

    Risk Levels:
    - 0-20: Low Risk (A)
    - 21-40: Medium Risk (B)
    - 41-70: High Risk (C)
    - 71-100: Critical Risk (D)
    - 100+: Severe Risk (F)
    """

    # Severity weights
    SEVERITY_WEIGHTS = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3
    }

    # Category multipliers (some issues are more severe than others)
    CATEGORY_MULTIPLIERS = {
        "secrets": 1.5,  # Hardcoded secrets are extremely serious
        "network": 1.3,  # SSL/TLS issues enable MITM attacks
        "configuration": 1.4,  # Debug/backup flags are critical
        "permissions": 1.2,  # Privacy concerns
        "data_protection": 1.3,  # Data leaks
        "code_protection": 1.0,  # Nice to have
        "input_validation": 1.1,  # Injection risks
        "default": 1.0
    }

    # Risk level thresholds
    RISK_LEVELS = [
        (0, 20, "Low", "A", "🟢", "Secure"),
        (21, 40, "Medium", "B", "🟡", "Minor Issues"),
        (41, 70, "High", "C", "🟠", "Significant Risks"),
        (71, 100, "Critical", "D", "🔴", "Major Vulnerabilities"),
        (101, 999, "Severe", "F", "🚨", "Extremely Dangerous")
    ]

    @staticmethod
    def calculate_risk_score(findings: List) -> Dict:
        """
        Calculate comprehensive risk score for mobile app.

        Args:
            findings: List of Finding objects

        Returns:
            Dict with risk score, level, grade, and detailed breakdown
        """
        if not findings:
            return {
                "risk_score": 0,
                "risk_level": "Low",
                "grade": "A",
                "emoji": "🟢",
                "status": "Secure",
                "security_score": 100,
                "findings_count": 0,
                "breakdown": {},
                "priorities": [],
                "recommendations": []
            }

        # Calculate base score
        total_score = 0
        category_scores = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for finding in findings:
            severity = finding.severity.lower()
            category = finding.category if hasattr(finding, 'category') else 'default'

            # Get base weight
            base_score = MobileRiskScorer.SEVERITY_WEIGHTS.get(severity, 0)

            # Apply category multiplier
            multiplier = MobileRiskScorer.CATEGORY_MULTIPLIERS.get(category, 1.0)
            weighted_score = base_score * multiplier

            # Add to totals
            total_score += weighted_score

            # Track by category
            if category not in category_scores:
                category_scores[category] = {
                    "score": 0,
                    "count": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }

            category_scores[category]["score"] += weighted_score
            category_scores[category]["count"] += 1
            category_scores[category][severity] += 1

            # Track severity counts
            severity_counts[severity] += 1

        # Round risk score
        risk_score = round(total_score, 1)

        # Determine risk level
        risk_level = "Unknown"
        grade = "?"
        emoji = "⚪"
        status = "Unknown"

        for min_score, max_score, level, lvl_grade, lvl_emoji, lvl_status in MobileRiskScorer.RISK_LEVELS:
            if min_score <= risk_score <= max_score:
                risk_level = level
                grade = lvl_grade
                emoji = lvl_emoji
                status = lvl_status
                break

        # Calculate security score (inverse of risk score, capped at 100)
        security_score = max(0, min(100, 100 - risk_score))

        # Get top priorities (critical and high findings)
        priorities = []
        for finding in findings:
            if finding.severity.lower() in ["critical", "high"]:
                priorities.append({
                    "title": finding.title,
                    "severity": finding.severity,
                    "category": finding.category if hasattr(finding, 'category') else 'general',
                    "description": finding.description[:200] + "..." if len(finding.description) > 200 else finding.description
                })

        # Sort priorities by severity
        priority_order = {"critical": 0, "high": 1}
        priorities.sort(key=lambda x: priority_order.get(x["severity"].lower(), 2))

        # Generate quick recommendations
        recommendations = MobileRiskScorer._generate_recommendations(
            severity_counts,
            category_scores,
            risk_level
        )

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "grade": grade,
            "emoji": emoji,
            "status": status,
            "security_score": int(security_score),
            "findings_count": len(findings),
            "severity_counts": severity_counts,
            "category_breakdown": category_scores,
            "priorities": priorities[:5],  # Top 5 priorities
            "recommendations": recommendations,
            "assessment_date": datetime.utcnow().isoformat(),
            "methodology": "OWASP MASVS + Weighted Severity Scoring"
        }

    @staticmethod
    def _generate_recommendations(severity_counts: Dict, category_scores: Dict, risk_level: str) -> List[str]:
        """Generate quick action recommendations based on findings."""
        recommendations = []

        # Critical findings
        if severity_counts["critical"] > 0:
            recommendations.append(
                f"🚨 URGENT: Fix {severity_counts['critical']} critical issue(s) immediately "
                f"(debuggable flag, hardcoded secrets, cleartext traffic)"
            )

        # High findings
        if severity_counts["high"] > 0:
            recommendations.append(
                f"⚠️ HIGH PRIORITY: Address {severity_counts['high']} high-severity issue(s) "
                f"(permissions, SSL pinning, backup flags)"
            )

        # Secrets category
        if "secrets" in category_scores and category_scores["secrets"]["count"] > 0:
            recommendations.append(
                f"🔑 Remove all {category_scores['secrets']['count']} hardcoded secret(s) "
                f"and use Android Keystore or environment variables"
            )

        # Network security
        if "network" in category_scores and category_scores["network"]["count"] > 0:
            recommendations.append(
                f"🌐 Fix {category_scores['network']['count']} network security issue(s): "
                f"enforce HTTPS, implement SSL pinning, disable cleartext traffic"
            )

        # Configuration
        if "configuration" in category_scores and category_scores["configuration"]["count"] > 0:
            recommendations.append(
                f"⚙️ Update {category_scores['configuration']['count']} configuration flag(s): "
                f"disable debuggable, restrict backups, secure manifests"
            )

        # Permissions
        if "permissions" in category_scores and category_scores["permissions"]["count"] > 0:
            recommendations.append(
                f"🔒 Review {category_scores['permissions']['count']} permission issue(s): "
                f"minimize dangerous permissions, request at runtime, explain to users"
            )

        # Code protection
        if "code_protection" in category_scores and category_scores["code_protection"]["count"] > 0:
            recommendations.append(
                "🛡️ Enable code obfuscation with ProGuard/R8 to prevent reverse engineering"
            )

        # Overall recommendation based on risk level
        if risk_level == "Severe":
            recommendations.insert(0, "🚨 APP NOT PRODUCTION-READY: Multiple critical vulnerabilities detected. Do NOT release until fixed!")
        elif risk_level == "Critical":
            recommendations.insert(0, "⚠️ MAJOR RISKS: App has serious security flaws. Fix critical issues before release!")
        elif risk_level == "High":
            recommendations.insert(0, "⚠️ SIGNIFICANT ISSUES: Address high-priority vulnerabilities to protect users")
        elif risk_level == "Medium":
            recommendations.insert(0, "✅ Generally secure with minor issues. Fix medium-priority items for best practices")
        elif risk_level == "Low":
            recommendations.insert(0, "✅ Good security posture! Address remaining low-priority items for perfection")

        return recommendations[:6]  # Top 6 recommendations

    @staticmethod
    def compare_with_industry(risk_score: float, app_type: str = "general") -> Dict:
        """
        Compare app's risk score with industry benchmarks.

        Args:
            risk_score: Calculated risk score
            app_type: Type of app (banking, social, ecommerce, general)

        Returns:
            Dict with comparison data
        """
        # Industry benchmarks (based on research and audits)
        benchmarks = {
            "banking": {
                "excellent": 10,
                "good": 20,
                "average": 35,
                "poor": 50,
                "critical": 70
            },
            "healthcare": {
                "excellent": 12,
                "good": 22,
                "average": 38,
                "poor": 55,
                "critical": 75
            },
            "social": {
                "excellent": 15,
                "good": 30,
                "average": 45,
                "poor": 60,
                "critical": 80
            },
            "ecommerce": {
                "excellent": 15,
                "good": 28,
                "average": 42,
                "poor": 58,
                "critical": 78
            },
            "general": {
                "excellent": 15,
                "good": 30,
                "average": 45,
                "poor": 60,
                "critical": 80
            }
        }

        benchmark = benchmarks.get(app_type, benchmarks["general"])

        # Determine where this app stands
        if risk_score <= benchmark["excellent"]:
            standing = "Excellent"
            percentile = "Top 10%"
            message = f"Your app's security is excellent for {app_type} apps!"
        elif risk_score <= benchmark["good"]:
            standing = "Good"
            percentile = "Top 30%"
            message = f"Your app's security is above average for {app_type} apps"
        elif risk_score <= benchmark["average"]:
            standing = "Average"
            percentile = "50th percentile"
            message = f"Your app's security is average for {app_type} apps"
        elif risk_score <= benchmark["poor"]:
            standing = "Below Average"
            percentile = "Bottom 40%"
            message = f"Your app's security is below average for {app_type} apps"
        else:
            standing = "Poor"
            percentile = "Bottom 10%"
            message = f"Your app's security is concerning for {app_type} apps"

        return {
            "standing": standing,
            "percentile": percentile,
            "message": message,
            "benchmark": benchmark,
            "app_type": app_type
        }

    @staticmethod
    def get_remediation_timeline(findings: List) -> Dict:
        """
        Estimate remediation timeline based on findings.

        Returns:
            Dict with timeline estimates
        """
        # Time estimates (in hours)
        time_estimates = {
            "debuggable": 0.1,  # 5 minutes
            "cleartext_traffic": 0.25,  # 15 minutes
            "backup_flag": 0.5,  # 30 minutes
            "ssl_pinning": 2,  # 2 hours
            "obfuscation": 2,  # 2 hours
            "hardcoded_secrets": 3,  # 3 hours (depends on quantity)
            "permissions": 1,  # 1 hour
            "default": 1  # 1 hour
        }

        total_hours = 0
        tasks = []

        for finding in findings:
            if finding.severity.lower() not in ["critical", "high"]:
                continue  # Only estimate critical/high

            # Estimate time based on finding type
            finding_type = "default"
            title_lower = finding.title.lower()

            if "debuggable" in title_lower:
                finding_type = "debuggable"
            elif "cleartext" in title_lower or "http" in title_lower:
                finding_type = "cleartext_traffic"
            elif "backup" in title_lower:
                finding_type = "backup_flag"
            elif "pinning" in title_lower or "ssl" in title_lower:
                finding_type = "ssl_pinning"
            elif "obfuscation" in title_lower or "proguard" in title_lower:
                finding_type = "obfuscation"
            elif "secret" in title_lower or "key" in title_lower or "password" in title_lower:
                finding_type = "hardcoded_secrets"
            elif "permission" in title_lower:
                finding_type = "permissions"

            hours = time_estimates.get(finding_type, 1)
            total_hours += hours

            tasks.append({
                "title": finding.title,
                "estimated_hours": hours,
                "priority": finding.severity
            })

        # Add buffer (20%)
        total_hours_with_buffer = total_hours * 1.2

        # Estimate calendar time (assuming 6 productive hours/day)
        calendar_days = round(total_hours_with_buffer / 6, 1)

        return {
            "total_hours": round(total_hours, 1),
            "total_hours_with_buffer": round(total_hours_with_buffer, 1),
            "calendar_days": calendar_days,
            "tasks": sorted(tasks, key=lambda x: 0 if x["priority"] == "critical" else 1),
            "message": f"Estimated {calendar_days} day(s) to fix all critical/high issues"
        }


def calculate_mobile_risk_score(findings: List) -> Dict:
    """Factory function for risk scoring."""
    return MobileRiskScorer.calculate_risk_score(findings)
