#!/usr/bin/env python3
"""
Marketplace plugin validator with tiered security policies.

Validates:
- Marketplace schema (marketplace.json)
- Plugin manifests (plugin.json) against JSON schema
- Tier-specific policies (curated vs community)
- Security scanning (secrets, network, telemetry)
- Consistency checks (declared vs detected capabilities)

Exit codes:
- 0: All plugins pass validation
- 1: One or more plugins failed validation
"""
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_FILE = ROOT / ".claude-plugin" / "marketplace.json"
SCHEMA_DIR = ROOT / "schema"
TMP_DIR = ROOT / ".tmp_plugin_validation"

# =========================
# TUNABLE POLICY SETTINGS
# =========================

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024      # 2MB per file hard fail
MAX_REPO_SIZE_BYTES = 20 * 1024 * 1024     # 20MB total repo hard fail (excluding .git)
MAX_FILES_COUNT = 2500                     # avoid huge repos
MAX_READ_BYTES_FOR_BINARY_CHECK = 4096

ALLOWED_TIERS = {"curated", "community"}
ALLOWED_SOURCE_TYPES = {"git"}

REQUIRED_FILES = ["README.md", "LICENSE"]
POSSIBLE_PLUGIN_MANIFESTS = ["plugin.json", ".claude-plugin/plugin.json"]
POSSIBLE_CONTENT_DIRS = ["commands", "agents", "hooks", "skills"]

# Disallowed binary-ish extensions often abused / bloating marketplace
DISALLOWED_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib",
    ".bin", ".dat",
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".avi", ".mkv",
    ".pdf",
    ".wasm",
}

# Allowed large-ish text formats (still size-limited above)
TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".yml", ".yaml", ".toml",
    ".py", ".js", ".ts", ".sh", ".zsh", ".bash",
    ".rb", ".go", ".rs", ".java", ".kt", ".swift",
}

# Skip noise dirs during scan
SKIP_DIRS = {
    ".git", ".idea", ".vscode", "__pycache__", ".gradle", "build",
    "dist", "node_modules", ".tmp", ".cache"
}

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z\.-]+)?(\+[0-9A-Za-z\.-]+)?$")
GITHUB_REPO_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+(\.git)?$")
PLUGIN_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
DOMAIN_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$")

# =========================
# SECURITY PATTERNS
# =========================

# Secrets detection patterns (hardcoded credentials)
SECRET_PATTERNS = [
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"][^'\"]+['\"]", "AWS Secret Key assignment"),
    # Generic API keys
    (r"(?i)api[_-]?key\s*[=:]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", "API key assignment"),
    (r"(?i)api[_-]?secret\s*[=:]\s*['\"][^'\"]+['\"]", "API secret assignment"),
    # Tokens
    (r"(?i)bearer\s+[a-zA-Z0-9_\-\.]+", "Bearer token"),
    (r"(?i)token\s*[=:]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", "Token assignment"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}", "GitHub Fine-grained PAT"),
    # Private keys
    (r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----", "Private key"),
    # Passwords
    (r"(?i)password\s*[=:]\s*['\"][^'\"]{8,}['\"]", "Password assignment"),
    (r"(?i)passwd\s*[=:]\s*['\"][^'\"]+['\"]", "Password assignment"),
    # Slack/Discord
    (r"xox[baprs]-[0-9a-zA-Z-]+", "Slack token"),
    (r"(?i)discord[_-]?(?:token|webhook)\s*[=:]\s*['\"][^'\"]+['\"]", "Discord token/webhook"),
    # Generic secrets
    (r"(?i)secret\s*[=:]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", "Secret assignment"),
]

# Network/telemetry patterns - code libraries
NETWORK_CODE_PATTERNS = [
    # Python
    (r"^\s*import\s+requests\b", "requests import"),
    (r"^\s*from\s+requests\s+import", "requests import"),
    (r"^\s*import\s+urllib\.request", "urllib.request import"),
    (r"^\s*from\s+urllib\.request\s+import", "urllib.request import"),
    (r"^\s*import\s+http\.client", "http.client import"),
    (r"^\s*import\s+aiohttp", "aiohttp import"),
    (r"^\s*import\s+httpx", "httpx import"),
    (r"requests\.(get|post|put|delete|patch)\s*\(", "requests HTTP call"),
    (r"urllib\.request\.(urlopen|Request)", "urllib HTTP call"),
    (r"^\s*import\s+socket\b", "socket import"),
    (r"^\s*from\s+socket\s+import", "socket import"),
    # JavaScript/TypeScript
    (r"\bfetch\s*\(", "fetch() call"),
    (r"\baxios\s*[\.\(]", "axios call"),
    (r"new\s+XMLHttpRequest", "XMLHttpRequest"),
    (r"\.ajax\s*\(", "jQuery ajax call"),
    (r"require\s*\(\s*['\"]https?['\"]", "Node http/https require"),
    (r"from\s+['\"]node:https?['\"]", "Node http/https import"),
    # WebSocket
    (r"\bWebSocket\s*\(", "WebSocket connection"),
    (r"^\s*import\s+websocket", "websocket import"),
]

# Shell network commands
SHELL_NETWORK_PATTERNS = [
    (r"\bcurl\s+", "curl command"),
    (r"\bwget\s+", "wget command"),
    (r"\bnc\s+", "netcat (nc) command"),
    (r"\bncat\s+", "ncat command"),
    (r"\bsocat\s+", "socat command"),
    (r"\bssh\s+", "ssh command"),
    (r"\bscp\s+", "scp command"),
    (r"\brsync\s+.*:", "rsync remote command"),
    (r"Invoke-WebRequest", "PowerShell Invoke-WebRequest"),
    (r"Invoke-RestMethod", "PowerShell Invoke-RestMethod"),
    (r"\btelnet\s+", "telnet command"),
]

# Telemetry/analytics patterns (always blocked)
TELEMETRY_PATTERNS = [
    (r"https?://[^'\"\s]*(?:posthog|segment|amplitude|mixpanel)[^'\"\s]*", "Analytics service URL"),
    (r"https?://[^'\"\s]*(?:sentry\.io|bugsnag|rollbar)[^'\"\s]*", "Error tracking URL"),
    (r"https?://[^'\"\s]*(?:analytics|telemetry|tracking|metrics|beacon)[^'\"\s]*", "Analytics/telemetry URL"),
    (r"(?i)posthog\.capture", "PostHog tracking call"),
    (r"(?i)analytics\.track", "Analytics tracking call"),
    (r"(?i)Sentry\.init", "Sentry initialization"),
]

# Combined network patterns for general scanning
NETWORK_PATTERNS = NETWORK_CODE_PATTERNS + SHELL_NETWORK_PATTERNS + TELEMETRY_PATTERNS

# Files to scan for security issues
SCANNABLE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".bash", ".zsh", ".rb", ".go", ".rs", ".ps1"}


@dataclass
class PluginResult:
    name: str
    tier: str
    url: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    network_detected: bool = False
    detected_domains: Set[str] = field(default_factory=set)


def run(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out.strip()


def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)


def load_marketplace() -> dict:
    if not MARKETPLACE_FILE.exists():
        fail(f"Marketplace index not found: {MARKETPLACE_FILE}")
    with MARKETPLACE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_tmp() -> None:
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_tmp() -> None:
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)


def clone_repo(url: str, dest: Path) -> Tuple[bool, str]:
    code, out = run(["git", "clone", "--depth", "1", url, str(dest)])
    if code != 0:
        return False, f"Could not clone {url}: {out}"
    return True, ""


def exists_any(repo_path: Path, paths: List[str]) -> Optional[str]:
    for p in paths:
        if (repo_path / p).exists():
            return p
    return None


def is_probably_binary(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            chunk = f.read(MAX_READ_BYTES_FOR_BINARY_CHECK)
        if b"\x00" in chunk:
            return True
        printable = set(range(32, 127)) | {9, 10, 13}
        if not chunk:
            return False
        non_printable = sum(1 for b in chunk if b not in printable)
        ratio = non_printable / max(1, len(chunk))
        return ratio > 0.35
    except Exception:
        return True


def walk_repo_files(repo_path: Path) -> List[Path]:
    files: List[Path] = []
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in filenames:
            files.append(Path(root) / fn)
    return files


def get_repo_size_bytes(files: List[Path]) -> int:
    total = 0
    for f in files:
        try:
            total += f.stat().st_size
        except Exception:
            continue
    return total


# =========================
# SCHEMA VALIDATION
# =========================

def validate_marketplace_schema(marketplace: dict) -> List[str]:
    """Validate marketplace.json structure."""
    errors = []

    name = marketplace.get("name")
    if not name or not isinstance(name, str):
        errors.append("marketplace.name missing or invalid")

    version = marketplace.get("version")
    if not version or not isinstance(version, str) or not SEMVER_RE.match(version):
        errors.append("marketplace.version missing or not semver (e.g. 1.0.0)")

    owner = marketplace.get("owner", {})
    if not isinstance(owner, dict) or not owner.get("name"):
        errors.append("marketplace.owner.name missing")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append("marketplace.plugins must be an array")

    # Ensure plugin names unique
    seen: Set[str] = set()
    if isinstance(plugins, list):
        for p in plugins:
            n = p.get("name")
            if not n:
                continue
            if n in seen:
                errors.append(f"duplicate plugin.name detected: '{n}'")
            seen.add(n)

    return errors


def validate_plugin_manifest_schema(manifest: dict, tier: str) -> Tuple[List[str], List[str]]:
    """
    Validate plugin manifest against schema rules.
    Lightweight validation without external jsonschema dependency.

    Returns (errors, warnings).
    Supports legacy manifests without policyTier/capabilities (with warnings).
    """
    errors = []
    warnings = []

    # Core required fields (always required)
    for field in ["name"]:
        if field not in manifest:
            errors.append(f"manifest missing required field: {field}")

    # Recommended fields (warn if missing)
    for field in ["version", "description"]:
        if field not in manifest:
            warnings.append(f"manifest missing recommended field: {field}")

    # New schema fields (warn if missing for backward compatibility)
    is_legacy = False
    if "policyTier" not in manifest:
        warnings.append(f"manifest missing policyTier field (legacy manifest). Assuming tier='{tier}' from marketplace entry.")
        is_legacy = True
    if "capabilities" not in manifest:
        warnings.append("manifest missing capabilities field (legacy manifest). Assuming network.mode='none'.")
        is_legacy = True

    # Name format
    name = manifest.get("name", "")
    if name and not PLUGIN_NAME_RE.match(name):
        warnings.append(f"manifest.name should be lowercase with hyphens: '{name}'")

    # Version format
    version = manifest.get("version", "")
    if version and not SEMVER_RE.match(version):
        warnings.append(f"manifest.version should be semver: '{version}'")

    # Policy tier validation (if present)
    policy_tier = manifest.get("policyTier")
    if policy_tier:
        if policy_tier not in ALLOWED_TIERS:
            errors.append(f"manifest.policyTier must be one of: {sorted(ALLOWED_TIERS)}")
        elif policy_tier != tier:
            errors.append(f"manifest.policyTier '{policy_tier}' does not match marketplace tier '{tier}'")

    # Capabilities validation (if present)
    caps = manifest.get("capabilities")
    if caps is not None:
        if not isinstance(caps, dict):
            errors.append("manifest.capabilities must be an object")
        else:
            # Network capability validation
            network = caps.get("network", {})
            if not isinstance(network, dict):
                errors.append("manifest.capabilities.network must be an object")
            else:
                mode = network.get("mode")
                if mode is not None and mode not in ["none", "allowlist"]:
                    errors.append("manifest.capabilities.network.mode must be 'none' or 'allowlist'")

                domains = network.get("domains", [])
                if mode == "allowlist":
                    if not domains or not isinstance(domains, list):
                        errors.append("manifest.capabilities.network.domains required when mode is 'allowlist'")
                    else:
                        for d in domains:
                            if not isinstance(d, str):
                                errors.append(f"domain must be string: {d}")
                            elif not DOMAIN_RE.match(d):
                                errors.append(f"invalid domain format (no wildcards, no IPs, no protocols): '{d}'")
                            elif d.startswith("*."):
                                errors.append(f"wildcard domains not allowed: '{d}'")
                            elif re.match(r"^\d+\.\d+\.\d+\.\d+$", d):
                                errors.append(f"IP addresses not allowed as domains: '{d}'")
                elif mode == "none" and domains:
                    errors.append("manifest.capabilities.network.domains should not be present when mode is 'none'")

    # Risk metadata (required for community with new schema)
    effective_tier = policy_tier or tier
    risk = manifest.get("risk")
    if effective_tier == "community" and not is_legacy:
        if not risk:
            errors.append("manifest.risk required for community tier plugins")
        elif not isinstance(risk, dict):
            errors.append("manifest.risk must be an object")
        else:
            egress = risk.get("dataEgress")
            if egress not in ["low", "medium", "high"]:
                errors.append("manifest.risk.dataEgress must be 'low', 'medium', or 'high'")

    return errors, warnings


def validate_tier_policy(manifest: dict, tier: str, is_legacy: bool = False) -> List[str]:
    """Enforce tier-specific policy rules."""
    errors = []

    # For legacy manifests, assume network.mode='none' (curated default)
    caps = manifest.get("capabilities", {})
    network = caps.get("network", {}) if caps else {}
    mode = network.get("mode", "none") if network else "none"

    if tier == "curated":
        # Curated plugins must have network.mode = "none"
        if mode != "none":
            errors.append(
                f"TIER POLICY: curated plugins must have capabilities.network.mode='none', "
                f"found '{mode}'. Remove network access or move to community tier."
            )

        # Curated plugins should not have risk metadata (or it should be low)
        risk = manifest.get("risk", {})
        if risk and risk.get("dataEgress") in ["medium", "high"]:
            errors.append(
                f"TIER POLICY: curated plugins cannot have medium/high risk. "
                f"Found risk.dataEgress='{risk.get('dataEgress')}'"
            )

    elif tier == "community":
        # Community plugins with network must use allowlist
        if mode not in ["none", "allowlist"]:
            errors.append(
                f"TIER POLICY: community plugins must use network.mode='none' or 'allowlist', "
                f"found '{mode}'"
            )

        # If allowlist, domains must be specified
        if mode == "allowlist":
            domains = network.get("domains", [])
            if not domains:
                errors.append(
                    "TIER POLICY: community plugins with network.mode='allowlist' must "
                    "declare explicit domains in capabilities.network.domains"
                )

    return errors


# =========================
# MARKETPLACE ENTRY PARSING
# =========================

def parse_plugin_entry(plugin: dict) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
    """Parse and validate a plugin entry from marketplace.json."""
    errors = []

    name = plugin.get("name")
    if not name or not isinstance(name, str):
        errors.append("plugin.name missing or invalid")
    elif not PLUGIN_NAME_RE.match(name):
        errors.append(f"plugin.name must be lowercase with hyphens: '{name}'")

    # Support both 'tier' (new) and 'category' (legacy) for backward compatibility
    tier = plugin.get("tier") or plugin.get("category")
    if tier == "official":
        tier = "curated"  # Map legacy 'official' to 'curated'
    if tier not in ALLOWED_TIERS:
        errors.append(f"plugin.tier must be one of: {sorted(ALLOWED_TIERS)}")

    tags = plugin.get("tags", [])
    if tags is None:
        tags = []
    if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
        errors.append("plugin.tags must be a list of strings")

    src = plugin.get("source", {})
    url = None
    if isinstance(src, dict):
        # Support both 'type' (new) and 'source' (legacy) for backward compatibility
        source_type = src.get("type") or src.get("source")
        if source_type == "url":
            source_type = "git"  # Map legacy 'url' to 'git'
        if source_type not in ALLOWED_SOURCE_TYPES:
            errors.append(f"plugin.source.type must be one of: {sorted(ALLOWED_SOURCE_TYPES)}")
        url = src.get("url")

    if not url or not isinstance(url, str) or not url.startswith("http"):
        errors.append("plugin.source.url missing or invalid")

    if url and isinstance(url, str):
        if url.endswith(".git"):
            pass
        elif GITHUB_REPO_RE.match(url):
            pass
        else:
            errors.append("plugin.source.url must be a valid GitHub repo URL or end with .git")

    return name, tier, url, errors


# =========================
# SECURITY SCANNING
# =========================

def scan_file_for_secrets(file_path: Path, content: str) -> List[Tuple[int, str, str]]:
    """Scan file content for hardcoded secrets."""
    findings: List[Tuple[int, str, str]] = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
            continue

        for pattern, name in SECRET_PATTERNS:
            if re.search(pattern, line):
                match = re.search(pattern, line)
                if match:
                    matched = match.group(0)
                    if len(matched) > 20:
                        matched = matched[:8] + "..." + matched[-4:]
                    findings.append((line_num, name, matched))

    return findings


def scan_file_for_network(file_path: Path, content: str) -> List[Tuple[int, str, str]]:
    """Scan file content for network/telemetry code."""
    findings: List[Tuple[int, str, str]] = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
            continue

        for pattern, name in NETWORK_PATTERNS:
            if re.search(pattern, line):
                match = re.search(pattern, line)
                if match:
                    matched = match.group(0)[:50]
                    findings.append((line_num, name, matched))

    return findings


def scan_file_for_telemetry(file_path: Path, content: str) -> List[Tuple[int, str, str]]:
    """Scan specifically for telemetry/analytics (always blocked)."""
    findings: List[Tuple[int, str, str]] = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
            continue

        for pattern, name in TELEMETRY_PATTERNS:
            if re.search(pattern, line):
                match = re.search(pattern, line)
                if match:
                    matched = match.group(0)[:50]
                    findings.append((line_num, name, matched))

    return findings


def security_scan_repo(
    repo_path: Path,
    files: List[Path],
    tier: str,
    allowed_domains: Set[str]
) -> Tuple[List[str], List[str], bool, Set[str]]:
    """
    Scan repository for security issues.
    Returns (errors, warnings, network_detected, detected_domains).
    """
    errors: List[str] = []
    warnings: List[str] = []
    network_detected = False
    detected_domains: Set[str] = set()

    content_dirs = {"commands", "hooks", "agents", "skills"}

    for f in files:
        if f.suffix.lower() not in SCANNABLE_EXTENSIONS:
            continue

        try:
            rel_parts = f.relative_to(repo_path).parts
            if not rel_parts or rel_parts[0] not in content_dirs:
                continue
        except ValueError:
            continue

        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            rel = f.relative_to(repo_path)

            # Check for secrets (HARD FAIL for all tiers)
            secret_findings = scan_file_for_secrets(f, content)
            for line_num, name, matched in secret_findings:
                errors.append(
                    f"SECURITY: Hardcoded secret detected & rejected by validator in {rel}:{line_num} - {name}"
                )

            # Check for telemetry (HARD FAIL for all tiers)
            telemetry_findings = scan_file_for_telemetry(f, content)
            for line_num, name, matched in telemetry_findings:
                errors.append(
                    f"SECURITY: Telemetry/analytics detected & rejected by validator in {rel}:{line_num} - {name}"
                )

            # Check for network code
            network_findings = scan_file_for_network(f, content)
            if network_findings:
                network_detected = True

                for line_num, name, matched in network_findings:
                    # Skip if it's a telemetry finding (already handled above)
                    is_telemetry = any(
                        re.search(tp[0], matched) for tp in TELEMETRY_PATTERNS
                    )
                    if is_telemetry:
                        continue

                    if tier == "curated":
                        # Curated: all network code is banned
                        errors.append(
                            f"SECURITY: Network code detected & rejected by validator in {rel}:{line_num} - {name}. "
                            f"Curated plugins must not use network. Remove network code or move to community tier."
                        )
                    else:
                        # Community: warn but allow if domains declared
                        warnings.append(
                            f"Network code in {rel}:{line_num} - {name}. "
                            f"Ensure all accessed domains are declared in manifest."
                        )

                    # Try to extract domains from URLs in the line
                    url_match = re.search(r'https?://([^/\s\'"]+)', content.split("\n")[line_num - 1])
                    if url_match:
                        detected_domains.add(url_match.group(1))

        except Exception as e:
            warnings.append(f"Could not security scan {f.relative_to(repo_path)}: {e}")

    return errors, warnings, network_detected, detected_domains


def check_consistency(
    tier: str,
    manifest: dict,
    network_detected: bool,
    detected_domains: Set[str]
) -> List[str]:
    """Check consistency between declared capabilities and detected usage."""
    errors = []

    caps = manifest.get("capabilities", {})
    network = caps.get("network", {})
    declared_mode = network.get("mode", "none")
    declared_domains = set(network.get("domains", []))

    # If network detected but manifest says mode=none -> inconsistency
    if network_detected and declared_mode == "none":
        errors.append(
            "CONSISTENCY: Network code detected in plugin but manifest declares "
            "capabilities.network.mode='none'. Either remove network code or "
            "update manifest to mode='allowlist' with explicit domains."
        )

    # For community with allowlist, check if detected domains are declared
    if tier == "community" and declared_mode == "allowlist" and detected_domains:
        undeclared = detected_domains - declared_domains
        if undeclared:
            errors.append(
                f"CONSISTENCY: Detected network access to domains not in allowlist: "
                f"{sorted(undeclared)}. Add these to capabilities.network.domains or remove access."
            )

    return errors


# =========================
# PLUGIN REPO VALIDATION
# =========================

def extract_command_names(repo_path: Path) -> Set[str]:
    """Extract command names from commands directory."""
    cmds: Set[str] = set()
    cmd_dir = repo_path / "commands"
    if not cmd_dir.exists() or not cmd_dir.is_dir():
        return cmds

    for f in cmd_dir.rglob("*"):
        if f.is_file() and f.suffix.lower() in {".md", ".txt"}:
            cmds.add(f.stem.strip())
    return cmds


def validate_plugin_repo(
    repo_path: Path,
    tier: str
) -> Tuple[List[str], List[str], Set[str], Optional[dict], bool, Set[str]]:
    """
    Validate a cloned plugin repository.
    Returns (errors, warnings, commands, manifest, network_detected, detected_domains).
    """
    errors: List[str] = []
    warnings: List[str] = []
    manifest_data: Optional[dict] = None

    # Required: manifest exists
    manifest = exists_any(repo_path, POSSIBLE_PLUGIN_MANIFESTS)
    if not manifest:
        errors.append(f"Missing plugin manifest (expected one of: {POSSIBLE_PLUGIN_MANIFESTS})")

    # Required: README + LICENSE
    for f in REQUIRED_FILES:
        if not (repo_path / f).exists():
            errors.append(f"Missing required file: {f}")

    # Required: content dirs
    has_content = any((repo_path / d).exists() for d in POSSIBLE_CONTENT_DIRS)
    if not has_content:
        errors.append(f"No content dirs found (expected one of: {POSSIBLE_CONTENT_DIRS})")

    # Parse and validate manifest
    allowed_domains: Set[str] = set()
    is_legacy = False
    if manifest:
        try:
            manifest_data = json.loads((repo_path / manifest).read_text(encoding="utf-8"))

            # Validate manifest schema (returns errors, warnings)
            schema_errors, schema_warnings = validate_plugin_manifest_schema(manifest_data, tier)
            errors.extend(schema_errors)
            warnings.extend(schema_warnings)

            # Check if legacy manifest
            is_legacy = "policyTier" not in manifest_data or "capabilities" not in manifest_data

            # Validate tier policy
            policy_errors = validate_tier_policy(manifest_data, tier, is_legacy)
            errors.extend(policy_errors)

            # Extract allowed domains for security scanning
            caps = manifest_data.get("capabilities", {})
            if caps:
                network = caps.get("network", {})
                allowed_domains = set(network.get("domains", []))

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {manifest}: {e}")
        except Exception as e:
            errors.append(f"Error reading {manifest}: {e}")

    # Deep scan: file sizes, binaries, repo size
    files = walk_repo_files(repo_path)

    if len(files) > MAX_FILES_COUNT:
        errors.append(f"Repo contains too many files: {len(files)} > {MAX_FILES_COUNT}")

    repo_size = get_repo_size_bytes(files)
    if repo_size > MAX_REPO_SIZE_BYTES:
        errors.append(
            f"Repo too large: {repo_size/1024/1024:.2f}MB > {MAX_REPO_SIZE_BYTES/1024/1024:.2f}MB"
        )

    for f in files:
        try:
            if f.is_symlink():
                warnings.append(f"Symlink detected: {f.relative_to(repo_path)} (review manually)")
                continue

            size = f.stat().st_size
            rel = f.relative_to(repo_path)

            if size > MAX_FILE_SIZE_BYTES:
                errors.append(
                    f"File too large: {rel} ({size/1024/1024:.2f}MB) > {MAX_FILE_SIZE_BYTES/1024/1024:.2f}MB"
                )

            ext = f.suffix.lower()

            if ext in DISALLOWED_EXTENSIONS:
                errors.append(f"Disallowed file type in repo: {rel} ({ext})")

            if ext not in TEXT_EXTENSIONS and size > 0:
                if is_probably_binary(f):
                    errors.append(f"Binary/suspicious file detected: {rel}")

        except Exception as e:
            warnings.append(f"Could not inspect file: {f} ({e})")

    commands = extract_command_names(repo_path)
    if len(commands) == 0:
        warnings.append("No commands detected under commands/ (ok if plugin uses hooks/agents only)")

    # Security scan
    sec_errors, sec_warnings, network_detected, detected_domains = security_scan_repo(
        repo_path, files, tier, allowed_domains
    )
    errors.extend(sec_errors)
    warnings.extend(sec_warnings)

    # Consistency check
    if manifest_data:
        consistency_errors = check_consistency(tier, manifest_data, network_detected, detected_domains)
        errors.extend(consistency_errors)

    return errors, warnings, commands, manifest_data, network_detected, detected_domains


# =========================
# MAIN
# =========================

def main() -> int:
    marketplace = load_marketplace()

    schema_errors = validate_marketplace_schema(marketplace)
    if schema_errors:
        print("❌ Marketplace schema invalid:")
        for e in schema_errors:
            print(f"  - {e}")
        return 1

    plugins = marketplace.get("plugins", [])

    if not plugins:
        print("✅ Marketplace validated (no plugins to check)")
        return 0

    ensure_tmp()

    results: List[PluginResult] = []
    all_command_index: Dict[str, List[str]] = {}

    for idx, plugin in enumerate(plugins):
        name, tier, url, entry_errors = parse_plugin_entry(plugin)

        if entry_errors or not name or not tier or not url:
            results.append(
                PluginResult(
                    name=name or f"plugin_{idx}",
                    tier=tier or "unknown",
                    url=url or "missing",
                    errors=entry_errors or ["Invalid marketplace entry"],
                )
            )
            continue

        safe_dir = name.replace("/", "_").replace(":", "_")
        dest = TMP_DIR / safe_dir

        tier_badge = "🔒" if tier == "curated" else "🌐"
        print(f"{tier_badge} Validating: {name} [{tier}] -> {url}")

        result = PluginResult(name=name, tier=tier, url=url)

        success, clone_error = clone_repo(url, dest)
        if not success:
            result.errors.append(clone_error)
            print(f"❌ FAIL: {name}")
            results.append(result)
            continue

        try:
            repo_errors, repo_warnings, cmd_names, manifest, net_detected, det_domains = validate_plugin_repo(
                dest, tier
            )
            result.errors.extend(repo_errors)
            result.warnings.extend(repo_warnings)
            result.network_detected = net_detected
            result.detected_domains = det_domains

            for c in cmd_names:
                all_command_index.setdefault(c, []).append(name)

            if result.errors:
                print(f"❌ FAIL: {name}")
            else:
                print(f"✅ OK: {name}")

        except Exception as e:
            result.errors.append(f"Unhandled error: {e}")
            print(f"❌ FAIL: {name}")

        results.append(result)

    cleanup_tmp()

    # Cross-plugin command collision warnings
    collisions = {cmd: pls for cmd, pls in all_command_index.items() if len(pls) > 1}

    failed = [r for r in results if r.errors]
    passed = [r for r in results if not r.errors]

    print("\n" + "=" * 60)
    print("📦 Validation Report")
    print("=" * 60 + "\n")

    # Summary by tier
    curated_count = len([r for r in results if r.tier == "curated"])
    community_count = len([r for r in results if r.tier == "community"])
    print(f"Plugins: {len(results)} total ({curated_count} curated, {community_count} community)\n")

    for r in results:
        tier_badge = "🔒" if r.tier == "curated" else "🌐"
        status = "❌" if r.errors else "✅"
        print(f"{status} {r.name} [{r.tier}] {tier_badge}")
        print(f"   url: {r.url}")

        if r.errors:
            for e in r.errors:
                print(f"   ❌ {e}")
        if r.warnings:
            for w in r.warnings:
                print(f"   ⚠️  {w}")

        if r.tier == "community" and r.network_detected:
            print(f"   📡 Network usage detected")
            if r.detected_domains:
                print(f"   📡 Detected domains: {sorted(r.detected_domains)}")

        print()

    if collisions:
        print("⚠️  Command name collisions detected (warning only):")
        for cmd, pls in sorted(collisions.items(), key=lambda x: x[0]):
            print(f"   - '{cmd}' appears in: {', '.join(pls)}")
        print("   Note: Usually OK - Claude Code namespaces commands by plugin name.\n")

    print("=" * 60)
    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Failed: {len(failed)}")
    print("=" * 60)

    if failed:
        print("\n💡 Remediation hints:")
        print("   - Secrets: Remove hardcoded credentials, use environment variables")
        print("   - Network (curated): Remove network code or move plugin to community tier")
        print("   - Network (community): Declare all domains in capabilities.network.domains")
        print("   - Telemetry: Remove all analytics/tracking code (not allowed in any tier)")
        print("   - Consistency: Ensure manifest matches actual code behavior")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
