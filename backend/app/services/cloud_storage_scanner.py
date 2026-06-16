"""Cloud Storage Security Scanner - S3, Azure Blob, GCP Storage"""
import requests
import re
from typing import List, Dict
from datetime import datetime, timezone

from app.models.scan import Finding


class CloudStorageScanner:
    """Scan cloud storage buckets for public access and misconfigurations."""

    @staticmethod
    def scan(value: str, asset_id: str, scan_id: str) -> List[Finding]:
        """
        Scan cloud storage bucket for security issues.

        Supports:
        - AWS S3: s3://bucket-name or https://bucket-name.s3.amazonaws.com
        - Azure Blob: https://account.blob.core.windows.net/container
        - GCP Storage: gs://bucket-name or https://storage.googleapis.com/bucket-name
        """
        findings = []

        # Detect storage type and extract bucket/container name
        storage_type, identifier = CloudStorageScanner._parse_storage_url(value)

        if not storage_type:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="configuration",
                title="Unknown Cloud Storage Format",
                description=f"Could not identify cloud storage type from: {value}",
                recommendation="Provide storage URL in format: s3://bucket, gs://bucket, or https://account.blob.core.windows.net/container",
            ))
            return findings

        # Scan based on storage type
        if storage_type == "s3":
            findings.extend(CloudStorageScanner._scan_s3(identifier, asset_id, scan_id))
        elif storage_type == "azure":
            findings.extend(CloudStorageScanner._scan_azure(identifier, asset_id, scan_id))
        elif storage_type == "gcp":
            findings.extend(CloudStorageScanner._scan_gcp(identifier, asset_id, scan_id))

        return findings

    @staticmethod
    def _parse_storage_url(value: str) -> tuple:
        """Parse storage URL and return (type, identifier)."""
        value = value.strip()

        # AWS S3
        if value.startswith("s3://"):
            return ("s3", value.replace("s3://", "").split("/")[0])
        if "s3.amazonaws.com" in value or "s3-" in value:
            # https://bucket.s3.amazonaws.com or https://s3.region.amazonaws.com/bucket
            if value.count(".s3") > 0:
                bucket = value.split("//")[1].split(".s3")[0] if "//" in value else value.split(".s3")[0]
                return ("s3", bucket)
            elif "amazonaws.com/" in value:
                bucket = value.split("amazonaws.com/")[1].split("/")[0]
                return ("s3", bucket)

        # Azure Blob Storage
        if "blob.core.windows.net" in value:
            # https://account.blob.core.windows.net/container
            parts = value.split("blob.core.windows.net/")
            if len(parts) > 1:
                account = parts[0].split("//")[1].rstrip(".")
                container = parts[1].split("/")[0]
                return ("azure", f"{account}/{container}")

        # Google Cloud Storage
        if value.startswith("gs://"):
            return ("gcp", value.replace("gs://", "").split("/")[0])
        if "storage.googleapis.com" in value:
            bucket = value.split("storage.googleapis.com/")[1].split("/")[0] if "storage.googleapis.com/" in value else None
            if bucket:
                return ("gcp", bucket)

        return (None, None)

    @staticmethod
    def _scan_s3(bucket_name: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scan AWS S3 bucket for public access."""
        findings = []

        # Check if bucket is publicly listable
        try:
            url = f"https://{bucket_name}.s3.amazonaws.com"
            response = requests.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                # Bucket is publicly accessible
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="critical",
                    category="access_control",
                    title="S3 Bucket Publicly Accessible",
                    description=f"S3 bucket '{bucket_name}' is publicly listable. Anyone on the internet can view and download files.",
                    recommendation="""IMMEDIATE ACTION REQUIRED - Block Public Access

Step 1: Block via AWS Console
  1. Go to S3 console → Select bucket
  2. Click "Permissions" → "Block public access"
  3. Enable all 4 settings
  4. Click "Save changes"

Step 2: Verify with AWS CLI
  aws s3api get-bucket-acl --bucket your-bucket-name

Step 3: Remove public ACLs
  aws s3api put-bucket-acl --bucket your-bucket-name --acl private

Step 4: Add bucket policy to deny public access
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }]
  }

VERIFICATION: Try accessing bucket URL in incognito - should return 403

TIME: 5 minutes | SEVERITY: CRITICAL""",
                ))
            elif response.status_code == 403:
                # Good! Bucket blocks public access
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="access_control",
                    title="S3 Bucket Access Properly Restricted",
                    description=f"S3 bucket '{bucket_name}' returns 403 Forbidden for anonymous access. Good configuration!",
                    recommendation="No action needed. Continue monitoring for configuration changes.",
                ))
            elif response.status_code == 404:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="low",
                    category="configuration",
                    title="S3 Bucket Not Found or Private",
                    description=f"S3 bucket '{bucket_name}' returned 404. Either doesn't exist, is in different region, or blocks listing.",
                    recommendation="If bucket exists, verify correct region and name. If accessible via AWS credentials, configuration is secure.",
                ))

        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="S3 Bucket Scan Error",
                description=f"Could not scan S3 bucket '{bucket_name}': {str(e)}",
                recommendation="Verify bucket name and network connectivity. Bucket may be in different region.",
            ))

        return findings

    @staticmethod
    def _scan_azure(identifier: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scan Azure Blob Storage for public access."""
        findings = []

        # identifier format: "account/container"
        try:
            account, container = identifier.split("/")
            url = f"https://{account}.blob.core.windows.net/{container}?restype=container&comp=list"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="critical",
                    category="access_control",
                    title="Azure Blob Container Publicly Accessible",
                    description=f"Azure container '{container}' in account '{account}' is publicly listable.",
                    recommendation="""IMMEDIATE ACTION - Set Container Access to Private

Step 1: Via Azure Portal
  1. Go to Storage Account → Containers
  2. Select container → Access policy
  3. Set to "Private (no anonymous access)"
  4. Click Save

Step 2: Via Azure CLI
  az storage container set-permission \\
    --name container-name \\
    --account-name account-name \\
    --public-access off

VERIFICATION: Try accessing container URL - should return 403

TIME: 2 minutes | SEVERITY: CRITICAL""",
                ))
            elif response.status_code == 404:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="access_control",
                    title="Azure Container Access Properly Restricted",
                    description=f"Container returns 404/403 for anonymous access. Properly secured.",
                    recommendation="No action needed. Continue monitoring.",
                ))

        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="Azure Blob Scan Error",
                description=f"Could not scan Azure container: {str(e)}",
                recommendation="Verify account and container names.",
            ))

        return findings

    @staticmethod
    def _scan_gcp(bucket_name: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scan Google Cloud Storage bucket for public access."""
        findings = []

        try:
            url = f"https://storage.googleapis.com/{bucket_name}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="critical",
                    category="access_control",
                    title="GCP Bucket Publicly Accessible",
                    description=f"GCP bucket '{bucket_name}' is publicly listable.",
                    recommendation="""IMMEDIATE ACTION - Remove Public Access

Step 1: Via GCP Console
  1. Go to Cloud Storage → Browser
  2. Select bucket → Permissions tab
  3. Remove "allUsers" and "allAuthenticatedUsers"
  4. Click Save

Step 2: Via gcloud CLI
  gsutil iam ch -d allUsers gs://bucket-name
  gsutil iam ch -d allAuthenticatedUsers gs://bucket-name

VERIFICATION: Try accessing bucket - should return 403

TIME: 3 minutes | SEVERITY: CRITICAL""",
                ))
            elif response.status_code == 403 or response.status_code == 404:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="access_control",
                    title="GCP Bucket Access Properly Restricted",
                    description=f"Bucket access is properly restricted. Good configuration!",
                    recommendation="No action needed.",
                ))

        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="GCP Bucket Scan Error",
                description=f"Could not scan GCP bucket: {str(e)}",
                recommendation="Verify bucket name and permissions.",
            ))

        return findings
