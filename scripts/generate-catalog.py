#!/usr/bin/env python3
"""
Generate CATALOG.md from marketplace.json and plugin manifests.

Usage:
  python scripts/generate-catalog.py          # Generate CATALOG.md
  python scripts/generate-catalog.py --check  # Check if CATALOG.md is up to date (CI mode)
"""
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_FILE = ROOT / ".claude-plugin" / "marketplace.json"
CATALOG_FILE = ROOT / "CATALOG.md"
TMP_DIR = ROOT / ".tmp_catalog_gen"


@dataclass
class PluginInfo:
    name: str
    tier: str
    description: str
    url: str
    tags: List[str]
    version: Optional[str] = None
    network_mode: str = "none"
    network_domains: List[str] = None
    fs_read: List[str] = None
    fs_write: List[str] = None
    commands_allow: List[str] = None
    commands_deny: List[str] = None
    secrets_required: List[str] = None
    risk_egress: Optional[str] = None
    risk_notes: Optional[str] = None


def run(cmd: List[str], cwd: Optional[Path] = None) -> tuple:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def clone_repo(url: str, dest: Path) -> bool:
    if dest.exists():
        shutil.rmtree(dest)
    code, _ = run(["git", "clone", "--depth", "1", url, str(dest)])
    return code == 0


def load_marketplace() -> dict:
    with MARKETPLACE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_manifest(repo_path: Path) -> Optional[Path]:
    for p in ["plugin.json", ".claude-plugin/plugin.json"]:
        manifest = repo_path / p
        if manifest.exists():
            return manifest
    return None


def extract_plugin_info(plugin: dict, repo_path: Optional[Path]) -> PluginInfo:
    """Extract plugin info from marketplace entry and manifest."""

    # Basic info from marketplace entry
    tier = plugin.get("tier") or plugin.get("category", "unknown")
    if tier == "official":
        tier = "curated"

    info = PluginInfo(
        name=plugin.get("name", "unknown"),
        tier=tier,
        description=plugin.get("description", ""),
        url=plugin.get("source", {}).get("url", ""),
        tags=plugin.get("tags", []),
    )

    # Try to read manifest from cloned repo
    if repo_path:
        manifest_path = find_manifest(repo_path)
        if manifest_path:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

                info.version = manifest.get("version")

                caps = manifest.get("capabilities", {})

                # Network
                network = caps.get("network", {})
                info.network_mode = network.get("mode", "none")
                info.network_domains = network.get("domains", [])

                # Filesystem
                fs = caps.get("filesystem", {})
                info.fs_read = fs.get("read", [])
                info.fs_write = fs.get("write", [])

                # Commands
                cmds = caps.get("commands", {})
                info.commands_allow = cmds.get("allow", [])
                info.commands_deny = cmds.get("deny", [])

                # Secrets
                secrets = caps.get("secrets", {})
                info.secrets_required = secrets.get("required", [])

                # Risk
                risk = manifest.get("risk", {})
                info.risk_egress = risk.get("dataEgress")
                info.risk_notes = risk.get("notes")

            except Exception as e:
                print(f"  Warning: Could not read manifest: {e}")

    return info


def network_badge(info: PluginInfo) -> str:
    """Generate network badge markdown."""
    if info.network_mode == "none":
        return "![None](https://img.shields.io/badge/Network-None-success)"
    elif info.network_mode == "allowlist":
        domains = ", ".join(info.network_domains or [])
        return f"![Allowlist](https://img.shields.io/badge/Network-Allowlist-yellow) `{domains}`"
    return "![Unknown](https://img.shields.io/badge/Network-Unknown-gray)"


def tier_badge(tier: str) -> str:
    """Generate tier badge markdown."""
    if tier == "curated":
        return "![Curated](https://img.shields.io/badge/Tier-Curated-7c3aed)"
    elif tier == "community":
        return "![Community](https://img.shields.io/badge/Tier-Community-blue)"
    return f"![{tier}](https://img.shields.io/badge/Tier-{tier}-gray)"


def risk_badge(egress: Optional[str]) -> str:
    """Generate risk badge markdown."""
    if not egress:
        return ""
    colors = {"low": "success", "medium": "yellow", "high": "red"}
    color = colors.get(egress, "gray")
    return f"![Risk: {egress}](https://img.shields.io/badge/Risk-{egress}-{color})"


def generate_catalog(plugins: List[PluginInfo], marketplace: dict) -> str:
    """Generate CATALOG.md content."""
    lines = []

    # Header
    lines.append("# Plugin Catalog")
    lines.append("")
    lines.append(f"**Marketplace:** {marketplace.get('name', 'Unknown')}")
    lines.append(f"**Version:** {marketplace.get('version', 'Unknown')}")
    lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append("> This file is auto-generated by `scripts/generate-catalog.py`. Do not edit manually.")
    lines.append("")

    # Summary badges
    curated = [p for p in plugins if p.tier == "curated"]
    community = [p for p in plugins if p.tier == "community"]

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total plugins:** {len(plugins)}")
    lines.append(f"- **Curated:** {len(curated)} (no network access)")
    lines.append(f"- **Community:** {len(community)} (network via allowlist)")
    lines.append("")

    # Curated plugins section
    lines.append("---")
    lines.append("")
    lines.append("## Curated Plugins")
    lines.append("")
    lines.append("Security-first plugins with no network access. Recommended for teams.")
    lines.append("")

    if curated:
        for p in curated:
            lines.append(f"### {p.name}")
            lines.append("")
            lines.append(f"{tier_badge(p.tier)} {network_badge(p)}")
            lines.append("")
            lines.append(f"**Description:** {p.description}")
            lines.append("")
            if p.version:
                lines.append(f"**Version:** {p.version}")
            lines.append(f"**Repository:** [{p.url}]({p.url})")
            if p.tags:
                lines.append(f"**Tags:** {', '.join(p.tags)}")
            lines.append("")

            # Capabilities table
            lines.append("| Capability | Value |")
            lines.append("|------------|-------|")
            lines.append(f"| Network | None |")
            if p.fs_write:
                lines.append(f"| FS Writes | `{', '.join(p.fs_write[:3])}` |")
            if p.commands_allow:
                lines.append(f"| Commands Allow | `{', '.join(p.commands_allow[:3])}` |")
            if p.commands_deny:
                lines.append(f"| Commands Deny | `{', '.join(p.commands_deny[:3])}` |")
            if p.secrets_required:
                lines.append(f"| Secrets Required | `{', '.join(p.secrets_required)}` |")
            lines.append("")
    else:
        lines.append("*No curated plugins yet.*")
        lines.append("")

    # Community plugins section
    lines.append("---")
    lines.append("")
    lines.append("## Community Plugins")
    lines.append("")
    lines.append("Community-contributed plugins. May use network via explicit allowlist.")
    lines.append("")

    if community:
        for p in community:
            lines.append(f"### {p.name}")
            lines.append("")
            lines.append(f"{tier_badge(p.tier)} {network_badge(p)} {risk_badge(p.risk_egress)}")
            lines.append("")
            lines.append(f"**Description:** {p.description}")
            lines.append("")
            if p.version:
                lines.append(f"**Version:** {p.version}")
            lines.append(f"**Repository:** [{p.url}]({p.url})")
            if p.tags:
                lines.append(f"**Tags:** {', '.join(p.tags)}")
            lines.append("")

            # Capabilities table
            lines.append("| Capability | Value |")
            lines.append("|------------|-------|")
            if p.network_mode == "allowlist" and p.network_domains:
                lines.append(f"| Network Domains | `{', '.join(p.network_domains)}` |")
            if p.fs_write:
                lines.append(f"| FS Writes | `{', '.join(p.fs_write[:3])}` |")
            if p.secrets_required:
                lines.append(f"| Secrets Required | `{', '.join(p.secrets_required)}` |")
            if p.risk_egress:
                lines.append(f"| Risk Level | {p.risk_egress} |")
            if p.risk_notes:
                lines.append(f"| Risk Notes | {p.risk_notes} |")
            lines.append("")
    else:
        lines.append("*No community plugins yet. [Submit yours!](CONTRIBUTING.md)*")
        lines.append("")

    # Permission legend
    lines.append("---")
    lines.append("")
    lines.append("## Permission Badges Legend")
    lines.append("")
    lines.append("| Badge | Meaning |")
    lines.append("|-------|---------|")
    lines.append("| ![Curated](https://img.shields.io/badge/Tier-Curated-7c3aed) | Security-first, no network |")
    lines.append("| ![Community](https://img.shields.io/badge/Tier-Community-blue) | Network via allowlist |")
    lines.append("| ![None](https://img.shields.io/badge/Network-None-success) | No network access |")
    lines.append("| ![Allowlist](https://img.shields.io/badge/Network-Allowlist-yellow) | Specific domains only |")
    lines.append("| ![Risk: low](https://img.shields.io/badge/Risk-low-success) | Low data egress risk |")
    lines.append("| ![Risk: medium](https://img.shields.io/badge/Risk-medium-yellow) | Medium data egress risk |")
    lines.append("| ![Risk: high](https://img.shields.io/badge/Risk-high-red) | High data egress risk |")
    lines.append("")

    return "\n".join(lines)


def main():
    check_mode = "--check" in sys.argv

    marketplace = load_marketplace()
    plugins_data = marketplace.get("plugins", [])

    if not plugins_data:
        print("No plugins found in marketplace.json")
        if check_mode:
            return 0
        # Still generate empty catalog
        content = generate_catalog([], marketplace)
        CATALOG_FILE.write_text(content, encoding="utf-8")
        print(f"Generated {CATALOG_FILE}")
        return 0

    # Create temp directory
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir(parents=True)

    plugins: List[PluginInfo] = []

    try:
        for plugin in plugins_data:
            name = plugin.get("name", "unknown")
            url = plugin.get("source", {}).get("url", "")

            print(f"Processing: {name}")

            repo_path = None
            if url:
                dest = TMP_DIR / name.replace("/", "_")
                if clone_repo(url, dest):
                    repo_path = dest
                else:
                    print(f"  Warning: Could not clone {url}")

            info = extract_plugin_info(plugin, repo_path)
            plugins.append(info)

        content = generate_catalog(plugins, marketplace)

        if check_mode:
            # Check if existing catalog matches
            if CATALOG_FILE.exists():
                existing = CATALOG_FILE.read_text(encoding="utf-8")
                # Compare ignoring the "Generated:" timestamp line
                def strip_timestamp(s):
                    lines = s.split("\n")
                    return "\n".join(l for l in lines if not l.startswith("**Generated:**"))

                if strip_timestamp(existing) != strip_timestamp(content):
                    print("❌ CATALOG.md is out of date. Run: python scripts/generate-catalog.py")
                    return 1
                else:
                    print("✅ CATALOG.md is up to date")
                    return 0
            else:
                print("❌ CATALOG.md does not exist. Run: python scripts/generate-catalog.py")
                return 1
        else:
            CATALOG_FILE.write_text(content, encoding="utf-8")
            print(f"\n✅ Generated {CATALOG_FILE}")
            return 0

    finally:
        if TMP_DIR.exists():
            shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    sys.exit(main())
