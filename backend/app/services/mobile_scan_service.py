"""
Mobile App Security Scanner

Analyzes Android APK files for security vulnerabilities.
"""
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Tuple
import shutil


class MobileAppScanner:
    """Scanner for mobile applications (APK files)."""

    def __init__(self, db):
        self.db = db

    async def scan_apk(self, asset_id: str) -> Dict:
        """
        Scan Android APK file for security issues.

        Args:
            asset_id: Asset UUID

        Returns:
            Scan results with findings
        """
        from app.models.asset import Asset
        from app.models.scan import Scan, Finding

        # Get asset
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset or not asset.app_file_path:
            raise ValueError("Asset not found or no APK file")

        # Create scan record
        scan = Scan(
            asset_id=asset_id,
            status="running",
            started_at=datetime.now(timezone.utc),
            scan_type="mobile_app"
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)

        try:
            apk_path = asset.app_file_path
            extract_dir = f"temp/apk_extract/{asset_id}"

            # Extract APK (it's just a ZIP file)
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Run security checks
            findings = []
            findings.extend(self._check_manifest_security(extract_dir, asset_id, scan.id))
            findings.extend(self._scan_for_secrets(extract_dir, asset_id, scan.id))
            findings.extend(self._check_libs_and_resources(extract_dir, asset_id, scan.id))

            # Save findings
            for finding in findings:
                self.db.add(finding)

            # Count by severity
            scan.findings_count = len(findings)
            scan.critical_count = sum(1 for f in findings if f.severity == "critical")
            scan.high_count = sum(1 for f in findings if f.severity == "high")
            scan.medium_count = sum(1 for f in findings if f.severity == "medium")
            scan.low_count = sum(1 for f in findings if f.severity == "low")

            # Calculate score
            scan.score = scan.calculate_score()
            scan.status = "completed"
            scan.completed_at = datetime.now(timezone.utc)

            # Update asset
            asset.security_score = scan.score
            asset.findings_count = scan.findings_count
            asset.last_scanned_at = scan.completed_at

            self.db.commit()
            self.db.refresh(scan)

            # Cleanup
            shutil.rmtree(extract_dir, ignore_errors=True)

            # Send email alert if critical/high issues
            if scan.critical_count > 0 or scan.high_count > 0:
                try:
                    from app.services.email_service import email_service
                    from app.models.user import User
                    from app.models.company import Company

                    company = self.db.query(Company).filter(Company.id == asset.company_id).first()
                    if company:
                        user = self.db.query(User).filter(
                            User.company_id == company.id,
                            User.role == 'company_admin'
                        ).first()

                        if user and user.email:
                            findings_data = [
                                {
                                    'severity': f.severity,
                                    'category': f.category,
                                    'title': f.title,
                                    'description': f.description,
                                    'recommendation': f.recommendation
                                }
                                for f in findings
                            ]

                            email_service.send_security_alert(
                                to_email=user.email,
                                asset_name=asset.name,
                                asset_url=f"Mobile App ({asset.app_platform})",
                                security_score=scan.score,
                                critical_count=scan.critical_count,
                                high_count=scan.high_count,
                                findings=findings_data
                            )
                except Exception as email_error:
                    print(f"Failed to send email alert: {email_error}")

            return {
                "scan_id": str(scan.id),
                "score": scan.score,
                "findings_count": scan.findings_count
            }

        except Exception as e:
            scan.status = "failed"
            scan.completed_at = datetime.now(timezone.utc)
            scan.scan_data = {"error": str(e)}
            self.db.commit()
            raise

    def _check_manifest_security(self, extract_dir: str, asset_id: str, scan_id: str) -> List:
        """Check AndroidManifest.xml for security issues."""
        from app.models.scan import Finding

        findings = []
        manifest_path = os.path.join(extract_dir, "AndroidManifest.xml")

        if not os.path.exists(manifest_path):
            return findings

        try:
            # Parse manifest (might be binary, try text first)
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # Define dangerous permissions
            dangerous_permissions = {
                'READ_CONTACTS': ('high', 'Contact Access', 'App can read all contacts'),
                'READ_SMS': ('critical', 'SMS Access', 'App can read text messages'),
                'SEND_SMS': ('critical', 'SMS Sending', 'App can send SMS without user knowing'),
                'RECORD_AUDIO': ('high', 'Microphone Access', 'App can record audio'),
                'CAMERA': ('medium', 'Camera Access', 'App can take photos/videos'),
                'ACCESS_FINE_LOCATION': ('high', 'Precise Location', 'App tracks exact location'),
                'READ_CALL_LOG': ('high', 'Call Log Access', 'App can see call history'),
                'WRITE_EXTERNAL_STORAGE': ('medium', 'Storage Write', 'App can write to storage'),
                'READ_EXTERNAL_STORAGE': ('low', 'Storage Read', 'App can read storage'),
            }

            # Check permissions
            for perm_elem in root.findall('.//{http://schemas.android.com/apk/res/android}permission'):
                perm_name = perm_elem.get('{http://schemas.android.com/apk/res/android}name', '')

                for danger_perm, (severity, title, desc) in dangerous_permissions.items():
                    if danger_perm in perm_name:
                        findings.append(Finding(
                            scan_id=scan_id,
                            asset_id=asset_id,
                            severity=severity,
                            category='Permissions',
                            title=f'{title} Permission',
                            description=desc,
                            recommendation=f'Ensure {title} permission is necessary. Consider alternatives or request only when needed.'
                        ))

            # Check for cleartext traffic
            for app_elem in root.findall('.//application'):
                cleartext = app_elem.get('{http://schemas.android.com/apk/res/android}usesCleartextTraffic')
                if cleartext == 'true':
                    findings.append(Finding(
                        scan_id=scan_id,
                        asset_id=asset_id,
                        severity='high',
                        category='Network Security',
                        title='Cleartext Traffic Allowed',
                        description='App allows unencrypted HTTP communication',
                        recommendation='Set usesCleartextTraffic to false and use HTTPS only'
                    ))

                # Check for debuggable
                debuggable = app_elem.get('{http://schemas.android.com/apk/res/android}debuggable')
                if debuggable == 'true':
                    findings.append(Finding(
                        scan_id=scan_id,
                        asset_id=asset_id,
                        severity='high',
                        category='App Configuration',
                        title='Debug Mode Enabled',
                        description='App is debuggable in production',
                        recommendation='Remove android:debuggable="true" from manifest'
                    ))

        except ET.ParseError:
            # Binary manifest - would need APKTool to decode
            findings.append(Finding(
                scan_id=scan_id,
                asset_id=asset_id,
                severity='low',
                category='Analysis',
                title='Binary Manifest',
                description='AndroidManifest.xml is in binary format. Install APKTool for deeper analysis.',
                recommendation='For detailed manifest analysis, decode APK with APKTool first'
            ))

        return findings

    def _scan_for_secrets(self, extract_dir: str, asset_id: str, scan_id: str) -> List:
        """Scan for hardcoded secrets in extracted files."""
        from app.models.scan import Finding

        findings = []

        # Secret patterns
        secret_patterns = {
            'API Key': (r'api[_-]?key["\s:=]+["\']?([A-Za-z0-9_\-]{20,})', 'critical'),
            'AWS Access Key': (r'AKIA[0-9A-Z]{16}', 'critical'),
            'Firebase Key': (r'AIzaSy[A-Za-z0-9_\-]{33}', 'critical'),
            'Private Key': (r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----', 'critical'),
            'Password': (r'password["\s:=]+["\']([^"\']{8,})', 'high'),
            'Secret': (r'secret["\s:=]+["\']([^"\']{8,})', 'high'),
            'Token': (r'token["\s:=]+["\']([A-Za-z0-9_\-\.]{20,})', 'high'),
        }

        scanned_files = 0
        max_files = 100  # Limit to avoid long scans

        # Scan XML and text files
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if scanned_files >= max_files:
                    break

                if file.endswith(('.xml', '.json', '.txt', '.properties', '.js')):
                    file_path = os.path.join(root, file)
                    scanned_files += 1

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(1024 * 100)  # Read first 100KB

                            for secret_type, (pattern, severity) in secret_patterns.items():
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                if matches:
                                    findings.append(Finding(
                                        scan_id=scan_id,
                                        asset_id=asset_id,
                                        severity=severity,
                                        category='Hardcoded Secrets',
                                        title=f'{secret_type} Found in Code',
                                        description=f'Potential {secret_type} detected in {file}',
                                        recommendation=f'Remove hardcoded {secret_type}. Use secure storage or server-side configuration.'
                                    ))
                                    break  # One finding per file

                    except Exception:
                        continue

        return findings

    def _check_libs_and_resources(self, extract_dir: str, asset_id: str, scan_id: str) -> List:
        """Check libraries and resources for issues."""
        from app.models.scan import Finding

        findings = []

        # Check lib folder for native libraries
        lib_dir = os.path.join(extract_dir, "lib")
        if os.path.exists(lib_dir):
            architectures = os.listdir(lib_dir)
            if len(architectures) > 3:
                findings.append(Finding(
                    scan_id=scan_id,
                    asset_id=asset_id,
                    severity='low',
                    category='App Size',
                    title='Multiple Architectures',
                    description=f'APK includes {len(architectures)} architectures, increasing size',
                    recommendation='Consider using App Bundles or separate APKs per architecture'
                ))

        # Check for large resources
        res_dir = os.path.join(extract_dir, "res")
        if os.path.exists(res_dir):
            # Check for uncompressed images
            drawable_dirs = [d for d in os.listdir(res_dir) if d.startswith('drawable')]
            large_images = 0

            for drawable_dir in drawable_dirs:
                drawable_path = os.path.join(res_dir, drawable_dir)
                if os.path.isdir(drawable_path):
                    for img_file in os.listdir(drawable_path):
                        img_path = os.path.join(drawable_path, img_file)
                        if os.path.isfile(img_path):
                            size_mb = os.path.getsize(img_path) / (1024 * 1024)
                            if size_mb > 0.5:  # > 500KB
                                large_images += 1

            if large_images > 5:
                findings.append(Finding(
                    scan_id=scan_id,
                    asset_id=asset_id,
                    severity='low',
                    category='App Size',
                    title='Large Image Resources',
                    description=f'Found {large_images} large images (>500KB)',
                    recommendation='Optimize images using WebP format or compression'
                ))

        return findings


def get_mobile_scanner(db):
    """Get mobile scanner instance."""
    return MobileAppScanner(db)
