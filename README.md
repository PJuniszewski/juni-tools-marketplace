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
  <img src="https://img.shields.io/badge/Curated-Official%20%2B%20Community-7c3aed" alt="Curated">
  <img src="https://img.shields.io/badge/Plugins-1-ff69b4" alt="Plugins">
  <img src="https://img.shields.io/badge/Version-2.0.0-blue" alt="Version">
</p>

<!-- TRUST & SECURITY -->
<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-success" alt="License">
  <img src="https://img.shields.io/badge/Secrets-Hard%20Fail-dc2626" alt="Secrets Hard Fail">
  <img src="https://img.shields.io/badge/Network-Hard%20Fail-dc2626" alt="Network Hard Fail">
  <img src="https://img.shields.io/badge/Telemetry-Blocked-dc2626" alt="Telemetry Blocked">
  <img src="https://img.shields.io/badge/Tests-27-22c55e" alt="Tests">
</p>

<p align="center">
  <strong>Supply-chain hardened Claude Code marketplace. Secrets scanning, network blocking, zero telemetry.</strong>
</p>

---

> **Security Notice:** Plugins execute with your full user permissions (filesystem, shell, environment variables). Official plugins are maintained by [@PJuniszewski](https://github.com/PJuniszewski). Community plugins are third-party contributions — review source code before enabling.

---

## Security Posture

This marketplace enforces **supply-chain hygiene**:

- **Secrets scanning (HARD FAIL)** — blocks committed credentials (AWS keys, GitHub tokens, private keys, Slack tokens, bearer tokens)
- **Network/telemetry scanning (HARD FAIL)** — blocks hidden network calls and analytics endpoints
- **CI validated** — every plugin must pass structural + security checks before merge

Scope: Only plugin content directories are scanned (`commands/`, `hooks/`, `agents/`, `skills/`).

---

## Official Plugins

Maintained by [@PJuniszewski](https://github.com/PJuniszewski).

| Plugin | Description | Version | Repo |
|--------|-------------|---------|------|
| **juni** | Juni Skills Suite - Feature development workflows (`/juni:cook`) + context safety (`/juni:guard`) | v2.0.0 | [View](https://github.com/PJuniszewski/cook) |

### Commands in juni plugin

| Command | Description |
|---------|-------------|
| `/juni:cook` | Structured feature development with planning phases |
| `/juni:cook-menu` | Interactive artifact management |
| `/juni:cook-stats` | Analytics and insights for cook artifacts |
| `/juni:sous-chef` | Background monitoring for cooking discipline |
| `/juni:guard` | Epistemic safety for JSON data in prompts |

## Community Plugins

Third-party contributions. Install at your own discretion.

| Plugin | Author | Description | Version |
|--------|--------|-------------|---------|
| *No community plugins yet* | — | [Submit yours!](CONTRIBUTING.md) | — |

---

## Quick Install

### 1. Add the Marketplace

```bash
claude /plugin
# Select "Add Marketplace" → enter: PJuniszewski/juni-skills-marketplace
```

### 2. Install & Enable

```bash
# Install juni plugin
claude /plugin install juni-skills:juni

# Enable plugin
claude /plugin enable juni
```

### 3. Verify

```bash
claude /plugin list
```

---

## Team Setup

Pre-configure plugins for your team in `.claude/settings.json`:

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

Team members automatically get marketplace access when they clone and run Claude Code.

> **Note:** Organization policies may restrict plugin execution. Check with your org admin if plugins fail to load.

---

## Migration from v1.x

If you had the old `cook` and `context-guard` plugins:

```bash
# Remove old plugins
claude /plugin uninstall juni-skills:cook
claude /plugin uninstall juni-skills:context-guard

# Install unified plugin
claude /plugin install juni-skills:juni
claude /plugin enable juni
```

**Command changes:**
| Old | New |
|-----|-----|
| `/cook` | `/juni:cook` |
| `/cook-menu` | `/juni:cook-menu` |
| `/guard` | `/juni:guard` |

---

## Validation

All plugins are automatically validated via CI:

| Check | Description |
|-------|-------------|
| Manifest | `plugin.json` or `.claude-plugin/plugin.json` exists |
| Required files | `README.md`, `LICENSE` present |
| Content | At least one of: `commands/`, `hooks/`, `agents/`, `skills/` |
| Size limits | No oversized files (2MB/file, 20MB/repo) |
| No binaries | Blocks `.exe`, `.dll`, `.so`, images, archives |
| **No secrets** | Scans for API keys, tokens, passwords, private keys |
| **No network** | Blocks `requests`, `fetch`, `urllib`, telemetry (banned) |

**Run locally:**

```bash
python scripts/validate-plugins.py
```

**Run tests:**

```bash
python scripts/test_validator.py
```

PRs that fail validation cannot be merged.

---

## Contributing

Want to add your plugin? See **[CONTRIBUTING.md](CONTRIBUTING.md)** for requirements and submission process.

---

## License

MIT License - see [LICENSE](LICENSE)
