"""CVE enrichment API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.scan import Finding
from app.models.asset import Asset
from app.services.cve_intelligence_service import cve_intelligence_service


router = APIRouter(prefix="/api/cve", tags=["CVE Intelligence"])


class CVELookupRequest(BaseModel):
    """Request to look up a CVE."""
    cve_id: str


class ProductVulnSearchRequest(BaseModel):
    """Request to search vulnerabilities for a product."""
    product: str
    version: str | None = None


@router.post("/lookup")
async def lookup_cve(request: CVELookupRequest):
    """
    Look up a specific CVE by ID.

    Returns detailed CVE information from NVD.
    """
    cve_data = await cve_intelligence_service.lookup_cve(request.cve_id)

    if not cve_data:
        raise HTTPException(status_code=404, detail=f"CVE {request.cve_id} not found")

    return cve_data


@router.post("/search")
async def search_product_vulnerabilities(request: ProductVulnSearchRequest):
    """
    Search for vulnerabilities affecting a product/version.

    Example:
        product: "nginx"
        version: "1.18.0"
    """
    vulns = await cve_intelligence_service.search_vulnerabilities_by_product(
        request.product,
        request.version
    )

    return {
        "product": request.product,
        "version": request.version,
        "vulnerabilities_found": len(vulns),
        "vulnerabilities": vulns
    }


@router.post("/enrich-finding/{finding_id}")
async def enrich_finding(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enrich a finding with CVE intelligence.

    Automatically detects software/version from the finding and looks up CVEs.
    """
    # Get finding
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Check access
    asset = db.query(Asset).filter(Asset.id == finding.asset_id).first()
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Extract software/version from finding
    # Try to get from finding_data first, then parse from title/description
    software = None
    version = None
    existing_cve = finding.cve_id

    if finding.finding_data:
        software = finding.finding_data.get("software")
        version = finding.finding_data.get("version")

    # If not in finding_data, try to extract from title
    if not software:
        software = _extract_software_from_text(finding.title or finding.description or "")

    # Enrich with CVE data
    enrichment = await cve_intelligence_service.enrich_finding_with_cve(
        software=software or "unknown",
        version=version,
        existing_cve=existing_cve
    )

    # Update finding with enrichment data
    if enrichment["cves_found"]:
        # Update CVE ID if found
        if not finding.cve_id and enrichment["cves_found"]:
            finding.cve_id = enrichment["cves_found"][0].get("cve_id")

        # Store enrichment in finding_data
        if not finding.finding_data:
            finding.finding_data = {}

        finding.finding_data["cve_enrichment"] = {
            "cves": enrichment["cves_found"],
            "highest_cvss": enrichment["highest_cvss"],
            "critical_count": enrichment["critical_count"],
            "high_count": enrichment["high_count"],
            "enriched_at": str(db.query(Finding).first().found_at)  # Current timestamp
        }

        # Upgrade severity if CVE is more severe
        cvss = enrichment["highest_cvss"]
        if cvss >= 9.0 and finding.severity != "critical":
            finding.severity = "critical"
        elif cvss >= 7.0 and finding.severity not in ["critical", "high"]:
            finding.severity = "high"

        db.commit()
        db.refresh(finding)

    return {
        "finding_id": str(finding.id),
        "enrichment": enrichment,
        "updated": len(enrichment["cves_found"]) > 0
    }


@router.post("/enrich-scan/{scan_id}")
async def enrich_scan_findings(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enrich all findings from a scan with CVE intelligence.

    Processes all findings in the background.
    """
    # Get scan findings
    findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()

    if not findings:
        raise HTTPException(status_code=404, detail="No findings found for this scan")

    # Check access (via first finding)
    asset = db.query(Asset).filter(Asset.id == findings[0].asset_id).first()
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    enriched_count = 0
    cves_found = 0

    # Enrich each finding
    for finding in findings:
        # Extract software info
        software = None
        version = None

        if finding.finding_data:
            software = finding.finding_data.get("software")
            version = finding.finding_data.get("version")

        if not software:
            software = _extract_software_from_text(finding.title or "")

        if software and software != "unknown":
            enrichment = await cve_intelligence_service.enrich_finding_with_cve(
                software=software,
                version=version,
                existing_cve=finding.cve_id
            )

            if enrichment["cves_found"]:
                # Update finding
                if not finding.cve_id:
                    finding.cve_id = enrichment["cves_found"][0].get("cve_id")

                if not finding.finding_data:
                    finding.finding_data = {}

                finding.finding_data["cve_enrichment"] = {
                    "cves": enrichment["cves_found"],
                    "highest_cvss": enrichment["highest_cvss"]
                }

                # Update severity
                cvss = enrichment["highest_cvss"]
                if cvss >= 9.0:
                    finding.severity = "critical"
                elif cvss >= 7.0 and finding.severity != "critical":
                    finding.severity = "high"

                enriched_count += 1
                cves_found += len(enrichment["cves_found"])

    db.commit()

    return {
        "scan_id": scan_id,
        "total_findings": len(findings),
        "enriched_findings": enriched_count,
        "cves_found": cves_found
    }


def _extract_software_from_text(text: str) -> str | None:
    """Extract software name from finding text."""
    text_lower = text.lower()

    # Common software names to look for
    software_names = [
        "nginx", "apache", "iis", "tomcat",
        "wordpress", "drupal", "joomla",
        "php", "python", "node", "nodejs",
        "mysql", "postgresql", "mongodb",
        "jquery", "react", "angular", "vue",
        "openssl", "openssh", "ssl", "tls"
    ]

    for software in software_names:
        if software in text_lower:
            return software

    return None
