<p align="center">
  <img src="assets/marketplace.png" alt="juni-skills-marketplace" width="100%">
</p>

<!-- STATUS & PLATFORM -->
<p align="center">
  <a href="https://github.com/PJuniszewski/juni-skills-marketplace/actions/workflows/validate.yml"><img src="https://github.com/PJuniszewski/juni-skills-marketplace/actions/workflows/validate.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/Claude%20Code-Marketplace-black" alt="Claude Code">
</p>

<!-- METADATA -->
<p align="center">
  <img src="https://img.shields.io/badge/Curated-Security%20First-7c3aed" alt="Curated">
  <img src="https://img.shields.io/badge/Community-Allowlist%20Network-blue" alt="Community">
  <img src="https://img.shields.io/badge/Version-3.0.0-blue" alt="Version">
</p>

<!-- TRUST & SECURITY -->
<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-success" alt="License">
  <img src="https://img.shields.io/badge/Secrets-Hard%20Fail-dc2626" alt="Secrets Hard Fail">
  <img src="https://img.shields.io/badge/Telemetry-Blocked-dc2626" alt="Telemetry Blocked">
  <img src="https://img.shields.io/badge/Tests-53-22c55e" alt="Tests">
</p>

<p align="center">
  <strong>Supply-chain hardened Claude Code marketplace with tiered security policies.</strong>
</p>

---

## Tiered Security Model

This marketplace uses an **A+B tier strategy**:

| Tier | Network | Risk | Recommended For |
|------|---------|------|-----------------|
| **Curated** | None | Low | Teams, Production, Security-conscious users |
| **Community** | Allowlist only | Declared | Individual use, Opt-in |

### Curated Tier (Default for Teams)

- **No network access** - plugins cannot make HTTP requests, open sockets, or phone home
- **Zero telemetry** - no analytics, tracking, or data collection
- Network code is **detected & rejected by validator** at PR time
- Full security review by maintainers

### Community Tier (Opt-in)

- Network allowed **only via explicit domain allowlist**
- No wildcards (`*.example.com`), no IP addresses
- Required risk declaration (`low`/`medium`/`high` data egress)
- User must explicitly enable community plugins

---

> **Security Notice:** Plugins execute with your full user permissions (filesystem, shell, environment variables). Curated plugins are maintained by [@PJuniszewski](https://github.com/PJuniszewski). Community plugins are third-party contributions — review source code and risk metadata before enabling.

---

## Threat Model

### What the validator does

| Check | Scope | Enforcement |
|-------|-------|-------------|
| **Secrets scanning** | All plugin code | Detected & rejected by validator (HARD FAIL) |
| **Network code detection** | Plugin content dirs | Detected & rejected for curated; allowed via allowlist for community |
| **Telemetry detection** | All plugin code | Detected & rejected by validator (HARD FAIL) |
| **Binary/blob detection** | Entire repo | Blocked |
| **Tier policy enforcement** | Manifest + code | Consistency check |

### What the validator does NOT do

- **Runtime sandboxing** - plugins execute with user permissions
- **Network firewall** - validator detects code patterns, not runtime traffic
- **Dynamic analysis** - static scanning only
- **Obfuscation detection** - minified code may bypass pattern matching

**Bottom line:** The validator reduces supply-chain risk at merge time. It is not a runtime security boundary.

---

## Curated Plugins

Security-first plugins with no network access. See [CATALOG.md](CATALOG.md) for details.

| Plugin | Description | Version |
|--------|-------------|---------|
| **juni** | Juni Skills Suite - /juni:cook (workflows), /juni:guard (context safety) | v2.1.0 |

## Community Plugins

Third-party contributions with network via allowlist. See [CATALOG.md](CATALOG.md) for details.

| Plugin | Author | Network Domains | Risk |
|--------|--------|-----------------|------|
| *No community plugins yet* | — | — | [Submit yours!](CONTRIBUTING.md) |

---

## Quick Install

### 1. Add the Marketplace

```bash
claude /plugin
# Select "Add Marketplace" → enter: PJuniszewski/juni-skills-marketplace
```

### 2. Install & Enable

```bash
# Install juni plugin (curated)
claude /plugin install juni-skills:juni

# Enable plugin
claude /plugin enable juni
```

### 3. Verify

```bash
claude /plugin list
```

---

## Team Setup (Curated Only)

For teams, we recommend pinning to curated plugins only:

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace"
  ],
  "enabledPlugins": [
    "juni-skills:juni"
  ]
}
```

### Pinning to a Specific Version

Pin your marketplace to a specific tag or commit for reproducibility:

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace@v3.0.0"
  ]
}
```

Or pin to a commit SHA:

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace@abc1234"
  ]
}
```

### Release Tags

| Tag | Content | Stability |
|-----|---------|-----------|
| `stable` | Curated plugins only | Production-ready |
| `edge` | Curated + all community | Latest features |
| `vX.Y.Z` | Specific release | Pinned version |

---

## Validation

All plugins are validated via CI before merge:

| Check | Description |
|-------|-------------|
| Schema | Manifest matches JSON schema |
| Tier policy | Curated has no network; community has allowlist + risk |
| Secrets | API keys, tokens, passwords detected & rejected |
| Network | HTTP libs, curl, fetch detected (rejected for curated) |
| Telemetry | Analytics/tracking code detected & rejected |
| Consistency | Declared capabilities match detected usage |

**Run locally:**

```bash
# Run tests (53 tests)
python scripts/test_validator.py

# Validate plugins
python scripts/validate-plugins.py

# Generate catalog
python scripts/generate-catalog.py
```

PRs that fail validation cannot be merged.

---

## Files

| File | Description |
|------|-------------|
| [CATALOG.md](CATALOG.md) | Auto-generated plugin catalog with badges |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to submit plugins |
| [marketplace/](marketplace/) | Tier documentation |
| [schema/](schema/) | JSON schemas + examples |

---

## Contributing

Want to add your plugin? See **[CONTRIBUTING.md](CONTRIBUTING.md)** for requirements and submission process.

**Quick checklist:**
- [ ] Curated: `policyTier: "curated"`, no network code
- [ ] Community: `policyTier: "community"`, explicit domain allowlist, risk declaration
- [ ] Run `python scripts/validate-plugins.py` locally before PR

---

## License

MIT License - see [LICENSE](LICENSE)
