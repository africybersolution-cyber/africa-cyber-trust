"""Test AI Risk Scorer with mock data"""
import sys
sys.path.insert(0, 'backend')

from app.services.ai_risk_scorer import AIRiskScorer
from datetime import datetime, timezone
from unittest.mock import Mock

print("="*60)
print("TESTING AI RISK SCORER")
print("="*60)

# Create mock scan
mock_scan = Mock()
mock_scan.id = "test-scan-id"
mock_scan.findings_count = 0

# Create mock findings
mock_findings = []

# Critical SQL Injection
finding1 = Mock()
finding1.severity = "critical"
finding1.category = "injection"
finding1.title = "SQL Injection in 'id' parameter"
finding1.description = "Database exposed via SQL injection vulnerability"
finding1.recommendation = "Use parameterized queries. TIME: 1-2 hours | SEVERITY: CRITICAL"
finding1.created_at = datetime.now(timezone.utc)
mock_findings.append(finding1)

# High - Exposed MongoDB
finding2 = Mock()
finding2.severity = "high"
finding2.category = "exposed_service"
finding2.title = "MongoDB Exposed Without Authentication"
finding2.description = "MongoDB database is accessible from internet without password"
finding2.recommendation = "Enable authentication. TIME: 15 minutes | SEVERITY: CRITICAL"
finding2.created_at = datetime.now(timezone.utc)
mock_findings.append(finding2)

# Medium - WordPress XML-RPC
finding3 = Mock()
finding3.severity = "medium"
finding3.category = "wordpress_vulnerability"
finding3.title = "WordPress XML-RPC Enabled"
finding3.description = "XML-RPC can be used for brute force attacks"
finding3.recommendation = "Disable XML-RPC. TIME: 5 minutes | SEVERITY: HIGH"
finding3.created_at = datetime.now(timezone.utc)
mock_findings.append(finding3)

# Low - Server version disclosure
finding4 = Mock()
finding4.severity = "low"
finding4.category = "information_disclosure"
finding4.title = "Server Version Disclosed"
finding4.description = "Server header reveals version information"
finding4.recommendation = "Remove server version. TIME: 5 minutes | SEVERITY: LOW"
finding4.created_at = datetime.now(timezone.utc)
mock_findings.append(finding4)

print(f"\nCreated {len(mock_findings)} mock findings:")
for f in mock_findings:
    print(f"  - {f.severity.upper()}: {f.title}")

print("\n" + "="*60)
print("CALCULATING RISK SCORE...")
print("="*60)

try:
    # Calculate risk score
    risk_analysis = AIRiskScorer.calculate_scan_risk_score(mock_scan, mock_findings)

    print(f"\n[SUCCESS] RISK SCORING SUCCESSFUL!\n")

    print(f"Overall Risk Score: {risk_analysis['overall_score']}/100")
    print(f"Risk Level: {risk_analysis['risk_level']}")
    print(f"\nTotal Findings: {risk_analysis['total_findings']}")
    print(f"  - Critical: {risk_analysis['critical_count']}")
    print(f"  - High: {risk_analysis['high_count']}")

    print(f"\nTop 3 Priority Findings:")
    for i, item in enumerate(risk_analysis['priority_findings'][:3], 1):
        print(f"  {i}. [{item['priority']}] {item['finding'].title}")
        print(f"     Risk Score: {item['risk_score']:.1f}")

    print(f"\nQuick Wins ({len(risk_analysis['quick_wins'])}):")
    for i, item in enumerate(risk_analysis['quick_wins'], 1):
        print(f"  {i}. {item['finding'].title}")
        print(f"     Time: {item['estimated_time']}")
        print(f"     {item['impact']}")

    print(f"\nRemediation Phases: {len(risk_analysis['remediation_order'])}")
    for phase in risk_analysis['remediation_order']:
        print(f"  - {phase['phase']}: {len(phase['findings'])} findings")

    print(f"\nExecutive Summary:")
    print(f"  {risk_analysis['executive_summary']}")

    print("\n" + "="*60)
    print("✅ AI RISK SCORER: ALL TESTS PASSED")
    print("="*60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
    print("❌ AI RISK SCORER: TEST FAILED")
    print("="*60)
