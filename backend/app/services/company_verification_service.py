"""Company verification service."""
from sqlalchemy.orm import Session
from app.models.subscription import CompanyReport
from app.services.subscription_service import SubscriptionService
import uuid
from datetime import datetime
import random


class CompanyVerificationService:
    """Company verification and due diligence reports."""

    @staticmethod
    async def create_report(
        db: Session,
        user_id: uuid.UUID,
        company_name: str,
        company_tin: str,
        country: str,
        report_type: str = "basic"
    ):
        """Create company verification report."""
        
        has_credits = SubscriptionService.use_credits(
            db, user_id, "company_verification"
        )
        
        if not has_credits:
            raise Exception("Insufficient credits")
        
        report = CompanyReport(
            user_id=user_id,
            company_name=company_name,
            company_tin=company_tin,
            country=country,
            report_type=report_type,
            status="processing",
            credits_used=5
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        report_data = CompanyVerificationService._generate_mock_report(
            company_name, company_tin, country
        )
        
        report.status = "completed"
        report.risk_score = report_data["risk_score"]
        report.report_data = str(report_data)
        
        db.commit()
        db.refresh(report)
        
        return report

    @staticmethod
    def _generate_mock_report(company_name: str, tin: str, country: str) -> dict:
        """Generate mock report data."""
        risk_score = random.randint(40, 95)
        
        return {
            "company_name": company_name,
            "tin": tin,
            "country": country,
            "risk_score": risk_score,
            "registration_status": "Active" if risk_score > 50 else "Inactive",
            "registration_date": "2015-03-15",
            "business_type": "Private Limited Company",
            "directors": [
                {"name": "John Doe", "role": "CEO", "since": "2015-03-15"},
                {"name": "Jane Smith", "role": "CFO", "since": "2016-06-01"}
            ],
            "financial_health": {
                "score": risk_score,
                "status": "Good" if risk_score > 70 else "Fair",
                "annual_revenue": "$2.5M",
                "profit_margin": "15%"
            },
            "compliance": {
                "tax_status": "Compliant",
                "licenses": ["Trade License", "VAT Registration"],
                "last_audit": "2024-12-01"
            },
            "court_cases": {
                "total": 0 if risk_score > 80 else 2,
                "pending": 0,
                "closed": 0 if risk_score > 80 else 2
            },
            "reputation": {
                "online_presence": "Strong",
                "social_media": "Active",
                "customer_reviews": "4.2/5.0",
                "news_mentions": 15
            },
            "red_flags": [] if risk_score > 70 else [
                "Pending lawsuit filed in 2023",
                "Late tax filing in 2022"
            ],
            "recommendation": (
                "Low Risk - Proceed with confidence"
                if risk_score > 80 else
                "Medium Risk - Proceed with caution"
            ),
            "generated_at": datetime.utcnow().isoformat()
        }
