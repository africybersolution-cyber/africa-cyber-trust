"""
Asset-type-specific ownership verification.

Domain / subdomain verification continues to live in ``verification_service.py``
(DNS TXT + HTML file + admin email) and is intentionally left untouched.

This module adds simple, industry-standard ownership checks for the asset
types that cannot use DNS/email:

    ip_address / ip_range  -> HTTP well-known file
    mobile_app             -> token in the public store listing (or APK upload)
    source_code_repo       -> act-verify.txt committed to the repo root
    cloud_storage          -> act-verify.txt object in the bucket root
    email_domain           -> DNS TXT (reuses the domain verifier)

Every method is token-based: the user places the verification token where only
the legitimate owner could, and we fetch it back over HTTPS. No third-party
OAuth secrets are required, which keeps the flow self-service and deployable.

The token is always rendered as ``acti-verification=<token>`` so a single string
search works across every transport.
"""
from typing import Dict, List, Tuple
from urllib.parse import urlparse, quote
import ipaddress

import requests

VERIFY_FILENAME = "act-verify.txt"
WELL_KNOWN_PATH = f"/.well-known/{VERIFY_FILENAME}"
HTTP_TIMEOUT = 10
USER_AGENT = "AfricaCyberTrust-Verifier/1.0"


def _expected_value(token: str) -> str:
    """Canonical content we expect to find, regardless of transport."""
    return f"acti-verification={token}"


def _content_matches(content: str, token: str) -> bool:
    if not content:
        return False
    if not token:
        # Never treat an empty token as verifiable, otherwise a file containing
        # just "acti-verification=" would pass for any asset.
        return False
    return _expected_value(token) in content.strip()


def _fetch(url: str) -> Tuple[bool, int, str]:
    """GET a URL, returning (ok, status_code, text). Never raises."""
    try:
        resp = requests.get(
            url,
            timeout=HTTP_TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        return resp.status_code == 200, resp.status_code, resp.text or ""
    except requests.exceptions.SSLError:
        return False, -1, "ssl_error"
    except requests.exceptions.ConnectionError:
        return False, -2, "connection_error"
    except requests.exceptions.Timeout:
        return False, -3, "timeout"
    except Exception as exc:  # noqa: BLE001
        return False, -99, str(exc)


# ---------------------------------------------------------------------------
# IP address / IP range
# ---------------------------------------------------------------------------
def _clean_ip(value: str) -> str:
    """Strip scheme/port/path/CIDR and return the bare host/IP."""
    v = value.strip()
    if "://" in v:
        v = v.split("://", 1)[1]
    v = v.split("/")[0]      # drop path or CIDR suffix
    v = v.split(":")[0]      # drop port
    return v


def _is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private/internal (RFC1918, loopback, link-local)."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        return False


def verify_ip_http_file(value: str, token: str) -> Tuple[bool, str]:
    """
    Verify ownership of an IP (or IP range) by serving a token file at
    http(s)://IP/.well-known/act-verify.txt.

    For an IP range (CIDR) we verify the network/base address — the user only
    needs one reachable host in the block to host the file.

    Private IPs (RFC1918, loopback, link-local) are auto-approved since they
    cannot be verified from the public internet.
    """
    ip = _clean_ip(value)
    if not ip:
        return False, "Could not parse an IP address from this asset."

    # Auto-approve private/internal IPs - they cannot be verified from public internet
    if _is_private_ip(ip):
        return True, (
            f"Private IP address detected ({ip}). Verification skipped - "
            f"private IPs (192.168.x.x, 10.x.x.x, 172.16-31.x.x, 127.x.x.x) "
            f"cannot be verified from the public internet. Auto-approved for scanning."
        )

    # Try HTTPS first (common for load balancers), then plain HTTP.
    for scheme in ("https", "http"):
        url = f"{scheme}://{ip}{WELL_KNOWN_PATH}"
        ok, status, text = _fetch(url)
        if ok and _content_matches(text, token):
            return True, f"IP ownership verified via {scheme.upper()} well-known file."
        if ok and not _content_matches(text, token):
            return False, (
                f"Found {WELL_KNOWN_PATH} on {ip} but the token did not match. "
                f"The file must contain exactly: {_expected_value(token)}"
            )

    return False, (
        f"Could not retrieve http(s)://{ip}{WELL_KNOWN_PATH}. "
        f"Make sure a web server on {ip} serves a file at "
        f"{WELL_KNOWN_PATH} containing: {_expected_value(token)}"
    )


# ---------------------------------------------------------------------------
# Mobile app
# ---------------------------------------------------------------------------
def _store_listing_urls(value: str) -> List[str]:
    """
    Build candidate public listing URLs from a package id or store URL.

    Accepts:
      - com.example.app            (Android package)
      - https://play.google.com/store/apps/details?id=com.example.app
      - https://apps.apple.com/app/id123456789
      - 123456789 / id123456789    (Apple app id)
    """
    v = value.strip()
    urls: List[str] = []

    if v.startswith("http://") or v.startswith("https://"):
        urls.append(v)
        return urls

    # Apple numeric id
    apple_id = v[2:] if v.lower().startswith("id") else v
    if apple_id.isdigit():
        urls.append(f"https://apps.apple.com/app/id{apple_id}")
        return urls

    # Otherwise treat it as an Android package name
    pkg = quote(v)
    urls.append(f"https://play.google.com/store/apps/details?id={pkg}&hl=en")
    return urls


def verify_mobile_app_listing(value: str, token: str) -> Tuple[bool, str]:
    """
    Verify mobile app ownership by checking that the developer added the
    verification token somewhere in the public store listing (typically the
    app description). Only the account that owns the listing can edit it.
    """
    urls = _store_listing_urls(value)
    if not urls:
        return False, "Could not determine an app store listing URL for this app."

    for url in urls:
        ok, status, text = _fetch(url)
        if ok:
            # Stores routinely HTML-escape the '=' sign in the public listing
            # (Google Play renders it as &#x3D; or &#61;). Accept the raw form
            # and both numeric-entity encodings of '='.
            escaped_variants = (
                _expected_value(token),
                f"acti-verification&#x3D;{token}",
                f"acti-verification&#61;{token}",
            )
            if any(v in text for v in escaped_variants):
                return True, "Mobile app ownership verified via store listing token."
            return False, (
                "Found the store listing but the verification token was not "
                f"present. Add this exact text to your app description: "
                f"{_expected_value(token)}"
            )

    return False, (
        "Could not load the public store listing. Confirm the package name / "
        "store URL is correct and the app is published, then add this text to "
        f"the description: {_expected_value(token)}"
    )


# ---------------------------------------------------------------------------
# Source code repository (GitHub / GitLab / Bitbucket / generic git host)
# ---------------------------------------------------------------------------
def _repo_raw_urls(value: str) -> List[str]:
    """Build raw-file URLs for act-verify.txt at the repo root."""
    v = value.strip().rstrip("/")
    if v.endswith(".git"):
        v = v[:-4]

    parsed = urlparse(v if "://" in v else f"https://{v}")
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if not path:
        return []

    parts = path.split("/")
    if len(parts) < 2:
        return []
    owner, repo = parts[0], parts[1]

    candidates: List[str] = []
    if "github.com" in host:
        for branch in ("main", "master"):
            candidates.append(
                f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{VERIFY_FILENAME}"
            )
    elif "gitlab.com" in host:
        for branch in ("main", "master"):
            candidates.append(
                f"https://gitlab.com/{owner}/{repo}/-/raw/{branch}/{VERIFY_FILENAME}"
            )
    elif "bitbucket.org" in host:
        for branch in ("main", "master"):
            candidates.append(
                f"https://bitbucket.org/{owner}/{repo}/raw/{branch}/{VERIFY_FILENAME}"
            )
    else:
        # Generic git host: best-effort raw path
        for branch in ("main", "master"):
            candidates.append(f"{parsed.scheme}://{host}/{owner}/{repo}/raw/{branch}/{VERIFY_FILENAME}")
    return candidates


def verify_source_code_repo(value: str, token: str) -> Tuple[bool, str]:
    """
    Verify repo ownership by checking for act-verify.txt committed to the
    default branch root. Only someone with write access can push it.
    """
    urls = _repo_raw_urls(value)
    if not urls:
        return False, (
            "Could not parse the repository URL. Use a full URL like "
            "https://github.com/owner/repo"
        )

    for url in urls:
        ok, status, text = _fetch(url)
        if ok and _content_matches(text, token):
            return True, "Repository ownership verified via act-verify.txt."

    return False, (
        f"Could not find {VERIFY_FILENAME} on the default branch (checked main "
        f"and master). Commit a file named {VERIFY_FILENAME} to the repo root "
        f"containing: {_expected_value(token)}"
    )


# ---------------------------------------------------------------------------
# Cloud storage bucket (S3 / GCS / Azure Blob)
# ---------------------------------------------------------------------------
def _bucket_object_urls(value: str) -> List[str]:
    """Build candidate public object URLs for act-verify.txt in a bucket root."""
    v = value.strip().rstrip("/")
    urls: List[str] = []

    # s3://bucket -> https://bucket.s3.amazonaws.com/act-verify.txt
    if v.startswith("s3://"):
        bucket = v[len("s3://"):].split("/")[0]
        urls.append(f"https://{bucket}.s3.amazonaws.com/{VERIFY_FILENAME}")
        urls.append(f"https://s3.amazonaws.com/{bucket}/{VERIFY_FILENAME}")
        return urls

    # gs://bucket -> https://storage.googleapis.com/bucket/act-verify.txt
    if v.startswith("gs://"):
        bucket = v[len("gs://"):].split("/")[0]
        urls.append(f"https://storage.googleapis.com/{bucket}/{VERIFY_FILENAME}")
        return urls

    # Already an http(s) bucket URL: append the object to the root
    if v.startswith("http://") or v.startswith("https://"):
        parsed = urlparse(v)
        base = f"{parsed.scheme}://{parsed.netloc}"
        urls.append(f"{base}/{VERIFY_FILENAME}")
        # Also handle path-style (bucket in the path)
        if parsed.path.strip("/"):
            first_seg = parsed.path.strip("/").split("/")[0]
            urls.append(f"{base}/{first_seg}/{VERIFY_FILENAME}")
        return urls

    # Bare bucket name -> assume S3
    urls.append(f"https://{v}.s3.amazonaws.com/{VERIFY_FILENAME}")
    return urls


def verify_cloud_storage(value: str, token: str) -> Tuple[bool, str]:
    """
    Verify bucket ownership by reading a public act-verify.txt object placed in
    the bucket root. Only someone with write access to the bucket can upload it.
    """
    urls = _bucket_object_urls(value)
    if not urls:
        return False, "Could not parse the bucket URL."

    saw_object = False
    for url in urls:
        ok, status, text = _fetch(url)
        if ok:
            if _content_matches(text, token):
                return True, "Cloud storage ownership verified via bucket object."
            saw_object = True

    if saw_object:
        return False, (
            f"Found {VERIFY_FILENAME} in the bucket but the token did not match. "
            f"The object must contain exactly: {_expected_value(token)}"
        )

    return False, (
        f"Could not read {VERIFY_FILENAME} from the bucket root. Upload a "
        f"publicly-readable object named {VERIFY_FILENAME} to the bucket root "
        f"containing: {_expected_value(token)}"
    )


# ---------------------------------------------------------------------------
# Dispatcher + instructions
# ---------------------------------------------------------------------------
class AssetVerificationService:
    """Routes verification to the correct handler for non-domain asset types."""

    # Asset types this service is responsible for. domain/subdomain/email_domain
    # are handled by the existing domain verification flow.
    SUPPORTED = {
        "ip_address",
        "ip_range",
        "mobile_app",
        "source_code_repo",
        "cloud_storage",
    }

    @staticmethod
    def get_instructions(asset_type: str, value: str, token: str) -> Dict:
        """Return UI instructions for the primary method of an asset type."""
        expected = _expected_value(token)
        t = asset_type.lower()

        if t in ("ip_address", "ip_range"):
            ip = _clean_ip(value)
            return {
                "method": "http_file",
                "title": "HTTP File Verification",
                "filename": VERIFY_FILENAME,
                "url": f"http://{ip}{WELL_KNOWN_PATH}",
                "content": expected,
                "instructions": (
                    f"On a web server reachable at {ip}, create a file at "
                    f"{WELL_KNOWN_PATH} containing exactly: {expected}"
                ),
            }

        if t == "mobile_app":
            return {
                "method": "app_listing",
                "title": "App Store Listing Verification",
                "content": expected,
                "instructions": (
                    "Add the following line anywhere in your app's public store "
                    f"description (Google Play or App Store): {expected}. "
                    "You can remove it after verification. Alternatively, upload "
                    "the signed APK/IPA using the Add Mobile App button."
                ),
            }

        if t == "source_code_repo":
            return {
                "method": "repo_file",
                "title": "Repository File Verification",
                "filename": VERIFY_FILENAME,
                "content": expected,
                "instructions": (
                    f"Commit a file named {VERIFY_FILENAME} to the root of your "
                    f"repository's default branch (main or master) containing "
                    f"exactly: {expected}"
                ),
            }

        if t == "cloud_storage":
            return {
                "method": "bucket_file",
                "title": "Bucket Object Verification",
                "filename": VERIFY_FILENAME,
                "content": expected,
                "instructions": (
                    f"Upload a publicly-readable object named {VERIFY_FILENAME} "
                    f"to the root of your bucket containing exactly: {expected}"
                ),
            }

        return {}

    @staticmethod
    def verify(asset_type: str, value: str, token: str) -> Tuple[bool, str, str]:
        """
        Run the correct verification for an asset type.

        Returns (success, message, method_used).
        """
        t = asset_type.lower()
        if t in ("ip_address", "ip_range"):
            ok, msg = verify_ip_http_file(value, token)
            return ok, msg, "http_file"
        if t == "mobile_app":
            ok, msg = verify_mobile_app_listing(value, token)
            return ok, msg, "app_listing"
        if t == "source_code_repo":
            ok, msg = verify_source_code_repo(value, token)
            return ok, msg, "repo_file"
        if t == "cloud_storage":
            ok, msg = verify_cloud_storage(value, token)
            return ok, msg, "bucket_file"
        return False, f"No verification handler for asset type '{asset_type}'.", "unknown"


asset_verification_service = AssetVerificationService()
