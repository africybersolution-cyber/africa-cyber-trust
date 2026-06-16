"""CVE/NVD intelligence service for vulnerability enrichment."""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class CVEIntelligenceService:
    """
    Enriches vulnerability findings with CVE/NVD data.

    Uses:
    - NVD API (NIST National Vulnerability Database)
    - OSV.dev (Open Source Vulnerabilities)
    - CVE.org API
    """

    # NVD API (free, no key needed for basic queries)
    NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    # OSV.dev API (free, open source focused)
    OSV_API_URL = "https://api.osv.dev/v1"

    # Cache to avoid repeated API calls
    _cve_cache: Dict[str, Dict] = {}
    _cache_ttl = timedelta(hours=24)  # Cache CVE data for 24 hours

    @staticmethod
    async def lookup_cve(cve_id: str) -> Optional[Dict[str, Any]]:
        """
        Look up a specific CVE by ID.

        Args:
            cve_id: CVE identifier (e.g., "CVE-2021-23017")

        Returns:
            Dictionary with CVE details or None if not found
        """
        # Check cache first
        cache_key = f"cve_{cve_id}"
        if cache_key in CVEIntelligenceService._cve_cache:
            cached = CVEIntelligenceService._cve_cache[cache_key]
            if datetime.utcnow() - cached["cached_at"] < CVEIntelligenceService._cache_ttl:
                print(f"[CVE] Cache hit for {cve_id}")
                return cached["data"]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Query NVD API
                response = await client.get(
                    CVEIntelligenceService.NVD_API_URL,
                    params={"cveId": cve_id}
                )

                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get("vulnerabilities", [])

                    if vulnerabilities:
                        vuln = vulnerabilities[0]
                        cve_data = CVEIntelligenceService._parse_nvd_response(vuln)

                        # Cache it
                        CVEIntelligenceService._cve_cache[cache_key] = {
                            "data": cve_data,
                            "cached_at": datetime.utcnow()
                        }

                        print(f"[CVE] Found {cve_id} - CVSS: {cve_data.get('cvss_score')}")
                        return cve_data

                print(f"[CVE] {cve_id} not found in NVD")
                return None

        except Exception as e:
            print(f"[CVE] Error looking up {cve_id}: {str(e)}")
            return None

    @staticmethod
    async def search_vulnerabilities_by_product(
        product: str,
        version: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for vulnerabilities affecting a product/version.

        Args:
            product: Software name (e.g., "nginx", "wordpress")
            version: Version string (e.g., "1.18.0")
            limit: Maximum results to return

        Returns:
            List of CVE dictionaries
        """
        try:
            # Use OSV.dev for product/version queries (better for this)
            async with httpx.AsyncClient(timeout=15.0) as client:
                query = {
                    "package": {"name": product}
                }

                if version:
                    query["version"] = version

                response = await client.post(
                    f"{CVEIntelligenceService.OSV_API_URL}/query",
                    json=query
                )

                if response.status_code == 200:
                    data = response.json()
                    vulns = data.get("vulns", [])[:limit]

                    results = []
                    for vuln in vulns:
                        parsed = CVEIntelligenceService._parse_osv_response(vuln)
                        results.append(parsed)

                    print(f"[CVE] Found {len(results)} vulnerabilities for {product} {version or 'any version'}")
                    return results

                return []

        except Exception as e:
            print(f"[CVE] Error searching {product}: {str(e)}")
            return []

    @staticmethod
    async def enrich_finding_with_cve(
        software: str,
        version: Optional[str] = None,
        existing_cve: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich a finding with CVE intelligence.

        Args:
            software: Detected software (e.g., "nginx")
            version: Version if known
            existing_cve: CVE ID if already detected

        Returns:
            Enrichment data with CVEs, CVSS scores, references
        """
        enrichment = {
            "software": software,
            "version": version,
            "cves_found": [],
            "highest_cvss": 0.0,
            "critical_count": 0,
            "high_count": 0,
            "references": []
        }

        # If we already have a CVE ID, look it up directly
        if existing_cve:
            cve_data = await CVEIntelligenceService.lookup_cve(existing_cve)
            if cve_data:
                enrichment["cves_found"].append(cve_data)
                enrichment["highest_cvss"] = cve_data.get("cvss_score", 0)
                if cve_data.get("severity") == "CRITICAL":
                    enrichment["critical_count"] = 1

        # Search by product/version
        if software:
            vulns = await CVEIntelligenceService.search_vulnerabilities_by_product(
                software, version, limit=5
            )

            for vuln in vulns:
                # Avoid duplicates
                if not any(v.get("cve_id") == vuln.get("cve_id") for v in enrichment["cves_found"]):
                    enrichment["cves_found"].append(vuln)

                    # Update counts
                    cvss = vuln.get("cvss_score", 0)
                    if cvss > enrichment["highest_cvss"]:
                        enrichment["highest_cvss"] = cvss

                    if cvss >= 9.0:
                        enrichment["critical_count"] += 1
                    elif cvss >= 7.0:
                        enrichment["high_count"] += 1

        return enrichment

    @staticmethod
    def _parse_nvd_response(vuln_data: Dict) -> Dict[str, Any]:
        """Parse NVD API response into our format."""
        cve = vuln_data.get("cve", {})
        cve_id = cve.get("id", "")

        # Extract CVSS score (prefer v3.1, fallback to v2)
        cvss_score = 0.0
        severity = "UNKNOWN"

        metrics = cve.get("metrics", {})
        if "cvssMetricV31" in metrics:
            cvss_v3 = metrics["cvssMetricV31"][0]["cvssData"]
            cvss_score = cvss_v3.get("baseScore", 0.0)
            severity = cvss_v3.get("baseSeverity", "UNKNOWN")
        elif "cvssMetricV2" in metrics:
            cvss_v2 = metrics["cvssMetricV2"][0]["cvssData"]
            cvss_score = cvss_v2.get("baseScore", 0.0)
            severity = CVEIntelligenceService._cvss_v2_to_severity(cvss_score)

        # Extract description
        descriptions = cve.get("descriptions", [])
        description = ""
        for desc in descriptions:
            if desc.get("lang") == "en":
                description = desc.get("value", "")
                break

        # Extract references
        references = []
        for ref in cve.get("references", [])[:3]:  # Limit to 3
            references.append({
                "url": ref.get("url"),
                "source": ref.get("source")
            })

        # Published date
        published = cve.get("published", "")
        if published:
            published = published.split("T")[0]  # Keep just the date

        return {
            "cve_id": cve_id,
            "cvss_score": cvss_score,
            "severity": severity,
            "description": description[:500],  # Truncate long descriptions
            "published_date": published,
            "references": references,
            "source": "NVD"
        }

    @staticmethod
    def _parse_osv_response(vuln_data: Dict) -> Dict[str, Any]:
        """Parse OSV.dev API response into our format."""
        vuln_id = vuln_data.get("id", "")

        # OSV includes multiple IDs, prefer CVE
        aliases = vuln_data.get("aliases", [])
        cve_id = next((a for a in aliases if a.startswith("CVE-")), vuln_id)

        # Extract severity (OSV uses database-specific scoring)
        severity_data = vuln_data.get("severity", [])
        cvss_score = 0.0
        severity = "UNKNOWN"

        for sev in severity_data:
            if sev.get("type") == "CVSS_V3":
                score_str = sev.get("score", "")
                # Parse CVSS:3.1/AV:N/AC:L/... format
                if "baseScore:" in score_str:
                    try:
                        cvss_score = float(score_str.split("baseScore:")[1].split("/")[0])
                    except:
                        pass

        # Estimate severity from score if not provided
        if cvss_score > 0:
            severity = CVEIntelligenceService._cvss_to_severity(cvss_score)

        # Summary
        summary = vuln_data.get("summary", "")

        # Published
        published = vuln_data.get("published", "")
        if published:
            published = published.split("T")[0]

        # References
        references = []
        for ref in vuln_data.get("references", [])[:3]:
            references.append({
                "url": ref.get("url"),
                "source": ref.get("type")
            })

        return {
            "cve_id": cve_id,
            "cvss_score": cvss_score,
            "severity": severity,
            "description": summary[:500],
            "published_date": published,
            "references": references,
            "source": "OSV"
        }

    @staticmethod
    def _cvss_to_severity(score: float) -> str:
        """Convert CVSS score to severity level."""
        if score >= 9.0:
            return "CRITICAL"
        elif score >= 7.0:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "NONE"

    @staticmethod
    def _cvss_v2_to_severity(score: float) -> str:
        """Convert CVSS v2 score to severity level."""
        if score >= 7.0:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "NONE"


# Singleton instance
cve_intelligence_service = CVEIntelligenceService()
