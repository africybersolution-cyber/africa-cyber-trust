"""
Mobile App Security Scanner

Comprehensive security analysis for Android APK and iOS IPA files.
Detects: permissions, secrets, insecure storage, SSL issues, code obfuscation, etc.
"""
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple
from datetime import datetime, timezone
import subprocess
import json

from app.models.scan import Finding
from app.services.mobile_recommendations import get_recommendation


class MobileAppScanner:
    """
    Enterprise-grade mobile app security scanner.

    Analyzes:
    - Dangerous permissions
    - Hardcoded secrets (API keys, passwords)
    - Certificate security
    - Insecure data storage
    - Network security config
    - Code obfuscation
    - Backup flags
    - Debuggable flags
    - Deep link security
    """

    # Dangerous Android permissions
    DANGEROUS_PERMISSIONS = {
        'android.permission.READ_CONTACTS': 'high',
        'android.permission.WRITE_CONTACTS': 'high',
        'android.permission.READ_CALENDAR': 'medium',
        'android.permission.WRITE_CALENDAR': 'medium',
        'android.permission.READ_CALL_LOG': 'critical',
        'android.permission.WRITE_CALL_LOG': 'critical',
        'android.permission.PROCESS_OUTGOING_CALLS': 'critical',
        'android.permission.READ_SMS': 'critical',
        'android.permission.SEND_SMS': 'critical',
        'android.permission.RECEIVE_SMS': 'critical',
        'android.permission.CAMERA': 'high',
        'android.permission.RECORD_AUDIO': 'high',
        'android.permission.ACCESS_FINE_LOCATION': 'high',
        'android.permission.ACCESS_COARSE_LOCATION': 'high',
        'android.permission.READ_EXTERNAL_STORAGE': 'medium',
        'android.permission.WRITE_EXTERNAL_STORAGE': 'high',
        'android.permission.ACCESS_MEDIA_LOCATION': 'medium',
        'android.permission.READ_PHONE_STATE': 'high',
        'android.permission.CALL_PHONE': 'medium',
        'android.permission.GET_ACCOUNTS': 'medium',
        'android.permission.BODY_SENSORS': 'high',
        'android.permission.ACTIVITY_RECOGNITION': 'medium',
    }

    # Critical flags
    CRITICAL_FLAGS = {
        'android:debuggable': 'critical',
        'android:allowBackup': 'high',
        'android:usesCleartextTraffic': 'critical',
    }

    # Secret patterns (API keys, tokens, passwords)
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', 'API Key'),
        (r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*["\']([^"\']{6,})["\']', 'Password/Secret'),
        (r'(?i)(token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', 'Auth Token'),
        (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*["\']?([A-Z0-9]{20})["\']?', 'AWS Access Key'),
        (r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', 'AWS Secret Key'),
        (r'sk_live_[a-zA-Z0-9]{24,}', 'Stripe Live Key'),
        (r'pk_live_[a-zA-Z0-9]{24,}', 'Stripe Publishable Key'),
        (r'AIza[a-zA-Z0-9_\-]{35}', 'Google API Key'),
        (r'ya29\.[a-zA-Z0-9_\-]{100,}', 'Google OAuth Token'),
        (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
        (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
    ]

    @staticmethod
    def scan(value: str, asset_id: str, scan_id: str, file_path: str = None) -> List[Finding]:
        """
        Main entry point for mobile app scanning.

        Args:
            value: Asset value (filename or URL)
            asset_id: Asset UUID
            scan_id: Scan UUID
            file_path: Optional local file path to uploaded APK/IPA

        Returns:
            List of Finding objects
        """
        findings = []

        # Determine scan type
        if value.startswith('http') and not file_path:
            # Store URL scanning (scrape app info from store)
            findings.extend(MobileAppScanner._scan_app_store(value, asset_id, scan_id))
        elif file_path or value.endswith(('.apk', '.ipa')):
            # Local file analysis
            scan_path = file_path if file_path else value

            if scan_path.endswith('.apk'):
                # Android APK analysis
                findings.extend(MobileAppScanner._scan_apk(scan_path, asset_id, scan_id))
            elif scan_path.endswith('.ipa'):
                # iOS IPA analysis
                findings.extend(MobileAppScanner._scan_ipa(scan_path, asset_id, scan_id))
            else:
                # Unknown format
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="medium",
                    title="Unknown Mobile App Format",
                    description=f"File format not recognized: {value}",
                    recommendation="Upload a valid APK (Android) or IPA (iOS) file, or provide an App Store URL.",
                    category="configuration",
                    found_at=datetime.now(timezone.utc)
                ))
        else:
            # Unknown format
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="medium",
                title="Mobile App Not Found",
                description=f"Could not find mobile app file: {value}",
                recommendation="Upload a valid APK (Android) or IPA (iOS) file.",
                category="configuration",
                found_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _scan_apk(apk_path: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Comprehensive Android APK security analysis."""
        findings = []

        try:
            # 1. Extract APK contents
            extract_dir = apk_path.replace('.apk', '_extracted')
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # 2. Parse AndroidManifest.xml
            manifest_path = os.path.join(extract_dir, 'AndroidManifest.xml')
            if os.path.exists(manifest_path):
                findings.extend(MobileAppScanner._analyze_manifest(manifest_path, asset_id, scan_id))

            # 3. Scan for hardcoded secrets
            findings.extend(MobileAppScanner._scan_for_secrets(extract_dir, asset_id, scan_id))

            # 4. Check network security config
            nsc_path = os.path.join(extract_dir, 'res', 'xml', 'network_security_config.xml')
            if os.path.exists(nsc_path):
                findings.extend(MobileAppScanner._check_network_security_config(nsc_path, asset_id, scan_id))
            else:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="medium",
                    title="Missing Network Security Config",
                    description="No network_security_config.xml found. App may not enforce SSL pinning.",
                    recommendation="Add network security config to enforce SSL/TLS best practices and certificate pinning.",
                    category="network",
                    found_at=datetime.now(timezone.utc)
                ))

            # 5. Check for certificate pinning
            findings.extend(MobileAppScanner._check_ssl_pinning(extract_dir, asset_id, scan_id))

            # 6. Analyze code obfuscation
            findings.extend(MobileAppScanner._check_code_obfuscation(extract_dir, asset_id, scan_id))

            # 7. Check AndroidManifest flags
            findings.extend(MobileAppScanner._check_critical_flags(manifest_path, asset_id, scan_id))

            # 8. Analyze deep links
            findings.extend(MobileAppScanner._check_deep_links(manifest_path, asset_id, scan_id))

            # 9. Check file permissions in storage
            findings.extend(MobileAppScanner._check_file_permissions(extract_dir, asset_id, scan_id))

            # Cleanup
            # os.system(f'rm -rf {extract_dir}')  # Uncomment in production

        except zipfile.BadZipFile:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="critical",
                title="Invalid APK File",
                description="The uploaded file is not a valid APK archive.",
                recommendation="Upload a valid Android APK file.",
                category="configuration",
                found_at=datetime.now(timezone.utc)
            ))
        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="medium",
                title="APK Scan Error",
                description=f"Error during APK analysis: {str(e)}",
                recommendation="Check APK file integrity and try again.",
                category="scan_error",
                found_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _analyze_manifest(manifest_path: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Analyze AndroidManifest.xml for security issues."""
        findings = []

        try:
            # Parse manifest (might be binary XML - need aapt or androguard)
            # For now, we'll use basic parsing (assumes decompiled manifest)
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # Extract permissions
            permissions = []
            for elem in root.findall('.//{http://schemas.android.com/apk/res/android}uses-permission'):
                perm_name = elem.get('{http://schemas.android.com/apk/res/android}name')
                if perm_name:
                    permissions.append(perm_name)

            # Check for dangerous permissions
            dangerous_perms = []
            for perm in permissions:
                if perm in MobileAppScanner.DANGEROUS_PERMISSIONS:
                    dangerous_perms.append((perm, MobileAppScanner.DANGEROUS_PERMISSIONS[perm]))

            if dangerous_perms:
                perm_list = '\n'.join([f"- {p[0]} ({p[1].upper()})" for p in dangerous_perms])

                # Group by severity
                critical_perms = [p[0] for p in dangerous_perms if p[1] == 'critical']
                high_perms = [p[0] for p in dangerous_perms if p[1] == 'high']

                if critical_perms:
                    severity = "critical"
                elif high_perms:
                    severity = "high"
                else:
                    severity = "medium"

                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity=severity,
                    title=f"Dangerous Permissions Detected ({len(dangerous_perms)} found)",
                    description=f"App requests {len(dangerous_perms)} dangerous permissions:\n{perm_list}",
                    recommendation="Review each permission and ensure it's necessary for core app functionality. Remove unused permissions to reduce attack surface.",
                    category="permissions",
                    found_at=datetime.now(timezone.utc)
                ))

        except ET.ParseError:
            # Binary XML - need aapt/androguard
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="low",
                title="Manifest Parsing Limited",
                description="AndroidManifest.xml is in binary format. Full analysis requires decompilation.",
                recommendation="Use apktool or androguard for deep manifest analysis.",
                category="analysis",
                found_at=datetime.now(timezone.utc)
            ))
        except Exception as e:
            pass  # Silent fail for manifest parsing

        return findings

    @staticmethod
    def _scan_for_secrets(directory: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scan decompiled code for hardcoded secrets."""
        findings = []
        secrets_found = []

        try:
            # Scan all text files
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.xml', '.json', '.txt', '.properties', '.smali', '.java')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()

                                # Check against secret patterns
                                for pattern, secret_type in MobileAppScanner.SECRET_PATTERNS:
                                    matches = re.finditer(pattern, content)
                                    for match in matches:
                                        secret_value = match.group(0)
                                        relative_path = file_path.replace(directory, '')
                                        secrets_found.append({
                                            'type': secret_type,
                                            'file': relative_path,
                                            'preview': secret_value[:50] + '...' if len(secret_value) > 50 else secret_value
                                        })
                        except Exception:
                            continue

            if secrets_found:
                secret_list = '\n'.join([f"- {s['type']} in {s['file']}: {s['preview']}" for s in secrets_found[:10]])
                rec = get_recommendation("hardcoded_secrets")

                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="critical",
                    title=f"Hardcoded Secrets Detected ({len(secrets_found)} found) - OWASP MASVS: MSTG-STORAGE-14",
                    description=f"Found {len(secrets_found)} potential hardcoded secrets:\n{secret_list}\n\n" + rec['description'],
                    recommendation=rec['fix'],
                    category="secrets",
                    found_at=datetime.now(timezone.utc)
                ))

        except Exception as e:
            pass  # Silent fail

        return findings

    @staticmethod
    def _check_network_security_config(nsc_path: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check network security config for SSL/TLS issues."""
        findings = []

        try:
            tree = ET.parse(nsc_path)
            root = tree.getroot()

            # Check for cleartext traffic
            base_config = root.find('.//base-config')
            if base_config is not None:
                cleartext = base_config.get('cleartextTrafficPermitted')
                if cleartext == 'true':
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="critical",
                        title="Cleartext Traffic Allowed",
                        description="Network security config allows unencrypted HTTP traffic.",
                        recommendation="Set cleartextTrafficPermitted=\"false\" in network_security_config.xml to enforce HTTPS.",
                        category="network",
                        found_at=datetime.now(timezone.utc)
                    ))

            # Check for certificate pinning
            trust_anchors = root.findall('.//trust-anchors')
            if not trust_anchors:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="medium",
                    title="No Certificate Pinning",
                    description="App does not implement SSL certificate pinning.",
                    recommendation="Add certificate pinning to prevent MITM attacks.",
                    category="network",
                    found_at=datetime.now(timezone.utc)
                ))

        except Exception as e:
            pass

        return findings

    @staticmethod
    def _check_ssl_pinning(directory: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check if SSL pinning is implemented."""
        findings = []

        # Look for common pinning libraries/implementations
        pinning_indicators = [
            'CertificatePinner',
            'SSLPinning',
            'TrustKit',
            'pinning',
            'certificate-pinner'
        ]

        pinning_found = False
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.smali', '.java', '.xml')):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if any(indicator in content for indicator in pinning_indicators):
                                pinning_found = True
                                break
                    except:
                        continue
            if pinning_found:
                break

        if not pinning_found:
            rec = get_recommendation("ssl_pinning")
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="high",
                title="SSL Pinning Not Detected (OWASP MASVS: MSTG-NETWORK-3)",
                description=rec['description'],
                recommendation=rec['fix'],
                category="network",
                found_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _check_code_obfuscation(directory: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check if code is obfuscated (ProGuard/R8)."""
        findings = []

        # Check for ProGuard/R8 mapping file
        mapping_file = os.path.join(directory, 'mapping.txt')

        # Check for obfuscated class names in smali files
        obfuscated = False
        smali_dir = os.path.join(directory, 'smali')

        if os.path.exists(smali_dir):
            # Look for typical obfuscated class names (a.class, b.class, etc.)
            for root, dirs, files in os.walk(smali_dir):
                obfuscated_pattern = re.compile(r'^[a-z]\.smali$')
                obfuscated_files = [f for f in files if obfuscated_pattern.match(f)]
                if len(obfuscated_files) > 10:  # If many single-letter classes found
                    obfuscated = True
                    break

        if not obfuscated and not os.path.exists(mapping_file):
            rec = get_recommendation("obfuscation")
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="medium",
                title="Code Obfuscation Not Detected (OWASP MASVS: MSTG-RESILIENCE-9)",
                description=rec['description'],
                recommendation=rec['fix'],
                category="code_protection",
                found_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _check_critical_flags(manifest_path: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check for critical security flags in manifest."""
        findings = []

        try:
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Check for debuggable flag
                if 'android:debuggable="true"' in content:
                    rec = get_recommendation("debuggable")
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="critical",
                        title="App is Debuggable (OWASP MASVS: MSTG-CODE-2)",
                        description=rec['description'],
                        recommendation=rec['fix'],
                        category="configuration",
                        found_at=datetime.now(timezone.utc)
                    ))

                # Check for allowBackup flag
                if 'android:allowBackup="true"' in content or 'android:allowBackup' not in content:
                    rec = get_recommendation("backup_flag")
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="high",
                        title="Backup Allowed (OWASP MASVS: MSTG-STORAGE-8)",
                        description=rec['description'],
                        recommendation=rec['fix'],
                        category="data_protection",
                        found_at=datetime.now(timezone.utc)
                    ))

                # Check for cleartext traffic
                if 'android:usesCleartextTraffic="true"' in content:
                    rec = get_recommendation("cleartext_traffic")
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="critical",
                        title="Cleartext Traffic Allowed (OWASP MASVS: MSTG-NETWORK-1)",
                        description=rec['description'],
                        recommendation=rec['fix'],
                        category="network",
                        found_at=datetime.now(timezone.utc)
                    ))

        except Exception as e:
            pass

        return findings

    @staticmethod
    def _check_deep_links(manifest_path: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check deep link security."""
        findings = []

        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # Find all intent filters with deep links
            intent_filters = root.findall('.//intent-filter')
            deep_links = []

            for intent_filter in intent_filters:
                data_elements = intent_filter.findall('.//{http://schemas.android.com/apk/res/android}data')
                for data in data_elements:
                    scheme = data.get('{http://schemas.android.com/apk/res/android}scheme')
                    host = data.get('{http://schemas.android.com/apk/res/android}host')
                    if scheme or host:
                        deep_links.append(f"{scheme}://{host}" if scheme and host else scheme or host)

            if deep_links:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="medium",
                    title=f"Deep Links Found ({len(deep_links)})",
                    description=f"App registers {len(deep_links)} deep link handlers. Ensure proper validation:\n" + '\n'.join([f"- {link}" for link in deep_links[:5]]),
                    recommendation="Validate all deep link parameters to prevent injection attacks. Use Android App Links for verified domains.",
                    category="input_validation",
                    found_at=datetime.now(timezone.utc)
                ))

        except Exception as e:
            pass

        return findings

    @staticmethod
    def _check_file_permissions(directory: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Check for world-readable/writable files."""
        findings = []

        # Check for shared preferences with MODE_WORLD_READABLE/WRITABLE
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.smali') or file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if 'MODE_WORLD_READABLE' in content or 'MODE_WORLD_WRITABLE' in content:
                                findings.append(Finding(
                                    asset_id=asset_id,
                                    scan_id=scan_id,
                                    severity="critical",
                                    title="World-Readable/Writable Files",
                                    description="App uses MODE_WORLD_READABLE or MODE_WORLD_WRITABLE for file storage. Other apps can read/modify sensitive data.",
                                    recommendation="Use MODE_PRIVATE for all SharedPreferences and internal file storage. Never use MODE_WORLD_READABLE or MODE_WORLD_WRITABLE.",
                                    category="data_protection",
                                    found_at=datetime.now(timezone.utc)
                                ))
                                break
        except Exception:
            pass

        return findings

    @staticmethod
    def _scan_ipa(ipa_path: str, asset_id: str, scan_id: str) -> List[Finding]:
        """iOS IPA security analysis (placeholder - needs implementation)."""
        findings = []

        findings.append(Finding(
            asset_id=asset_id,
            scan_id=scan_id,
            severity="low",
            title="iOS Analysis Coming Soon",
            description="iOS IPA scanning is under development. Currently supports Android APK only.",
            recommendation="Check back soon for iOS security scanning capabilities.",
            category="analysis",
            found_at=datetime.now(timezone.utc)
        ))

        return findings

    @staticmethod
    def _scan_app_store(store_url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scrape Play Store/App Store for public info (placeholder)."""
        findings = []

        # TODO: Scrape store listing for:
        # - Privacy policy URL
        # - Data collection practices
        # - Permissions listed
        # - User reviews mentioning security
        # - Update frequency

        findings.append(Finding(
            asset_id=asset_id,
            scan_id=scan_id,
            severity="low",
            title="App Store Analysis",
            description=f"App Store URL: {store_url}",
            recommendation="For complete analysis, upload the APK/IPA file directly.",
            category="information",
            found_at=datetime.now(timezone.utc)
        ))

        return findings


def get_mobile_app_scanner():
    """Factory function for mobile app scanner."""
    return MobileAppScanner()
