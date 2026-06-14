"""Source Code Repository Scanner - GitHub/GitLab Secret Detection"""
import re
import requests
from typing import List, Dict
from datetime import datetime, timezone

from app.models.scan import Finding


class SourceCodeRepoScanner:
    """Scan source code repositories for leaked secrets and credentials."""

    # Secret detection patterns (similar to truffleHog/gitleaks)
    SECRET_PATTERNS = {
        "AWS Access Key": r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
        "AWS Secret Key": r"(?i)aws(.{0,20})?['\"][0-9a-zA-Z/+]{40}['\"]",
        "GitHub Token": r"ghp_[0-9a-zA-Z]{36}",
        "GitHub OAuth": r"gho_[0-9a-zA-Z]{36}",
        "Generic API Key": r"(?i)(api[_-]?key|apikey|api[_-]?token)['\"]?\s*[:=]\s*['\"]?[0-9a-zA-Z]{20,}['\"]?",
        "Generic Secret": r"(?i)(secret|password|passwd|pwd)['\"]?\s*[:=]\s*['\"]?[^'\"\s]{8,}['\"]?",
        "Private Key": r"-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
        "Slack Token": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[0-9a-zA-Z]{24,32}",
        "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
        "Google OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
        "Stripe Key": r"(?:sk|pk)_(test|live)_[0-9a-zA-Z]{24,99}",
        "Twilio Key": r"SK[0-9a-fA-F]{32}",
        "SendGrid Key": r"SG\\.[0-9A-Za-z\\-_]{22}\\.[0-9A-Za-z\\-_]{43}",
        "Mailgun Key": r"key-[0-9a-zA-Z]{32}",
        "Azure Key": r"(?i)azure[_-]?(client[_-]?secret|api[_-]?key)['\"]?\s*[:=]\s*['\"]?[0-9a-zA-Z/+]{32,}['\"]?",
        "Database URL": r"(?i)(postgres|mysql|mongodb|redis)://[^\\s\"']+:[^\\s\"']+@[^\\s\"']+",
        "Firebase URL": r"https://[a-z0-9-]+\\.firebaseio\\.com"
    }

    @staticmethod
    def scan(repo_url: str, asset_id: str, scan_id: str) -> List[Finding]:
        """
        Scan source code repository for exposed secrets.

        Supports:
        - GitHub: github.com/user/repo
        - GitLab: gitlab.com/user/repo
        """
        findings = []

        # Parse repository URL
        repo_info = SourceCodeRepoScanner._parse_repo_url(repo_url)

        if not repo_info:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="configuration",
                title="Invalid Repository URL",
                description=f"Could not parse repository URL: {repo_url}",
                recommendation="Provide URL in format: github.com/user/repo or gitlab.com/user/repo",
                created_at=datetime.now(timezone.utc)
            ))
            return findings

        platform, owner, repo = repo_info

        # Check if repository is public
        if platform == "github":
            findings.extend(SourceCodeRepoScanner._scan_github(owner, repo, asset_id, scan_id))
        elif platform == "gitlab":
            findings.extend(SourceCodeRepoScanner._scan_gitlab(owner, repo, asset_id, scan_id))

        return findings

    @staticmethod
    def _parse_repo_url(url: str) -> tuple:
        """Parse repository URL and return (platform, owner, repo)."""
        url = url.strip().lower().replace("https://", "").replace("http://", "").rstrip("/")

        # GitHub
        github_match = re.match(r"github\.com/([^/]+)/([^/]+)", url)
        if github_match:
            return ("github", github_match.group(1), github_match.group(2).replace(".git", ""))

        # GitLab
        gitlab_match = re.match(r"gitlab\.com/([^/]+)/([^/]+)", url)
        if gitlab_match:
            return ("gitlab", gitlab_match.group(1), gitlab_match.group(2).replace(".git", ""))

        return None

    @staticmethod
    def _scan_github(owner: str, repo: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scan GitHub repository."""
        findings = []

        try:
            # Check if repo is public
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 404:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="access_control",
                    title="Repository Private or Not Found",
                    description=f"GitHub repository '{owner}/{repo}' is private or doesn't exist. Cannot scan.",
                    recommendation="If repository exists and is private, that's good for security. Public repos can be scanned by anyone.",
                    created_at=datetime.now(timezone.utc)
                ))
                return findings

            if response.status_code != 200:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="scan_error",
                    title="GitHub API Error",
                    description=f"Could not access GitHub API: HTTP {response.status_code}",
                    recommendation="Check repository URL and try again later.",
                    created_at=datetime.now(timezone.utc)
                ))
                return findings

            repo_data = response.json()

            # Check if repository is public
            if not repo_data.get("private", True):
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="medium",
                    category="access_control",
                    title="Repository is Public",
                    description=f"Repository '{owner}/{repo}' is publicly accessible. Ensure no secrets are committed.",
                    recommendation="""Review Public Repository for Secrets

Step 1: Scan with git-secrets or truffleHog
  # Install truffleHog
  pip install truffleHog

  # Scan repository
  trufflehog github --repo https://github.com/{owner}/{repo}

Step 2: If secrets found, take action immediately
  1. Rotate ALL exposed credentials
  2. Remove secrets from git history:
     git filter-branch --force --index-filter \\
       'git rm --cached --ignore-unmatch path/to/secret/file' \\
       --prune-empty --tag-name-filter cat -- --all

  3. Force push (WARNING: destructive)
     git push origin --force --all

Step 3: Prevent future leaks
  1. Add .gitignore for .env, config files
  2. Use git-secrets or pre-commit hooks
  3. Use environment variables instead of hardcoded secrets

ALTERNATIVE: Make repository private if not needed public

TIME: 1-2 hours | SEVERITY: MEDIUM""",
                    created_at=datetime.now(timezone.utc)
                ))

                # Scan README for common secrets (lightweight scan)
                findings.extend(SourceCodeRepoScanner._scan_readme(owner, repo, asset_id, scan_id))

        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="GitHub Scan Error",
                description=f"Error scanning GitHub repository: {str(e)}",
                recommendation="Verify repository URL and network connectivity.",
                created_at=datetime.now(timezone.utc)
            ))

        return findings

    @staticmethod
    def _scan_readme(owner: str, repo: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scan README for exposed secrets (lightweight check)."""
        findings = []

        try:
            # Get README content
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
            response = requests.get(readme_url, timeout=10)

            if response.status_code == 404:
                # Try master branch
                readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
                response = requests.get(readme_url, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Scan for secrets
                for secret_name, pattern in SourceCodeRepoScanner.SECRET_PATTERNS.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        findings.append(Finding(
                            asset_id=asset_id,
                            scan_id=scan_id,
                            severity="critical",
                            category="secrets",
                            title=f"Possible {secret_name} Exposed in README",
                            description=f"Detected pattern matching {secret_name} in repository README. Found {len(matches)} match(es).",
                            recommendation=f"""IMMEDIATE ACTION - {secret_name} Exposed!

Step 1: ROTATE CREDENTIAL IMMEDIATELY
  - Generate new {secret_name}
  - Update all services using old credential
  - Revoke/delete old credential

Step 2: Remove from Git History
  git filter-branch --force --index-filter \\
    'git rm --cached --ignore-unmatch README.md' \\
    --prune-empty -- --all

  git push origin --force --all

Step 3: Store Securely
  - Use environment variables
  - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
  - Never commit credentials to git

Step 4: Add Pre-commit Hook
  Install git-secrets to prevent future leaks:
  git secrets --install
  git secrets --register-aws

SEVERITY: CRITICAL - Credential is publicly visible!""",
                            created_at=datetime.now(timezone.utc)
                        ))

        except Exception as e:
            # Silently skip README scan if fails
            pass

        return findings

    @staticmethod
    def _scan_gitlab(owner: str, repo: str, asset_id: str, scan_id: str) -> List[Finding]:
        """Scan GitLab repository."""
        findings = []

        try:
            # URL encode the project path
            project_path = f"{owner}/{repo}".replace("/", "%2F")
            api_url = f"https://gitlab.com/api/v4/projects/{project_path}"

            response = requests.get(api_url, timeout=10)

            if response.status_code == 404:
                findings.append(Finding(
                    asset_id=asset_id,
                    scan_id=scan_id,
                    severity="info",
                    category="access_control",
                    title="Repository Private or Not Found",
                    description=f"GitLab repository '{owner}/{repo}' is private or doesn't exist.",
                    recommendation="If repository is private, that's secure. Public repos can expose code.",
                    created_at=datetime.now(timezone.utc)
                ))
                return findings

            if response.status_code == 200:
                repo_data = response.json()

                if repo_data.get("visibility") == "public":
                    findings.append(Finding(
                        asset_id=asset_id,
                        scan_id=scan_id,
                        severity="medium",
                        category="access_control",
                        title="GitLab Repository is Public",
                        description=f"Repository is publicly accessible. Review for exposed secrets.",
                        recommendation="Use gitleaks or truffleHog to scan for secrets. Consider making private if not needed public.",
                        created_at=datetime.now(timezone.utc)
                    ))

        except Exception as e:
            findings.append(Finding(
                asset_id=asset_id,
                scan_id=scan_id,
                severity="info",
                category="scan_error",
                title="GitLab Scan Error",
                description=f"Error scanning GitLab repository: {str(e)}",
                recommendation="Verify repository URL.",
                created_at=datetime.now(timezone.utc)
            ))

        return findings
