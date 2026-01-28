# Contributing to juni-skills-marketplace

We welcome community plugin contributions! This document explains how to submit your plugin.

## Choose Your Tier

Before submitting, decide which tier fits your plugin:

| Tier | When to Use | Network | Requirements |
|------|-------------|---------|--------------|
| **Curated** | Security-first, no external dependencies | None | No network code, maintainer review |
| **Community** | Needs API access or external data | Allowlist only | Explicit domains, risk declaration |

### Curated Tier

Best for plugins that:
- Work entirely offline
- Process local files only
- Don't need external APIs
- Target team/production use

### Community Tier

Required for plugins that:
- Call external APIs (GitHub, Jira, etc.)
- Fetch remote data
- Need any network access

---

## Plugin Requirements

### Required for All Plugins

- [ ] Public GitHub repository
- [ ] Valid `plugin.json` manifest with new schema fields
- [ ] README.md with installation and usage
- [ ] LICENSE file (MIT or Apache 2.0 recommended)
- [ ] At least one version tag (e.g., `v1.0.0`)
- [ ] At least one content directory: `commands/`, `hooks/`, `agents/`, or `skills/`

### Required Manifest Fields

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "Brief description of what your plugin does",
  "policyTier": "curated",
  "capabilities": {
    "network": {
      "mode": "none"
    }
  }
}
```

### Curated-Specific Requirements

- [ ] `policyTier: "curated"` in manifest
- [ ] `capabilities.network.mode: "none"`
- [ ] **No network code** in `commands/`, `hooks/`, `agents/`, `skills/`
- [ ] No telemetry or analytics

### Community-Specific Requirements

- [ ] `policyTier: "community"` in manifest
- [ ] `capabilities.network.mode: "allowlist"` with explicit domains
- [ ] `risk.dataEgress: "low" | "medium" | "high"`
- [ ] Domain allowlist (no wildcards, no IPs)

**Example community manifest:**

```json
{
  "name": "github-issues",
  "version": "1.0.0",
  "description": "Fetch and summarize GitHub issues for the current repository",
  "policyTier": "community",
  "capabilities": {
    "network": {
      "mode": "allowlist",
      "domains": ["api.github.com"]
    },
    "filesystem": {
      "read": [".git/config"],
      "write": []
    },
    "secrets": {
      "required": ["GITHUB_TOKEN"]
    }
  },
  "risk": {
    "dataEgress": "medium",
    "notes": "Sends repository name to GitHub API"
  }
}
```

---

## Domain Allowlist Rules

For community plugins, domains must be:

**Allowed:**
- Explicit hostnames: `api.github.com`, `example.com`
- Subdomains: `api.service.example.com`

**Not Allowed:**
- Wildcards: `*.example.com`
- IP addresses: `192.168.1.1`
- Protocols in domain: `https://example.com`

---

## Submission Process

### 1. Fork and Clone

```bash
gh repo fork PJuniszewski/juni-skills-marketplace --clone
cd juni-skills-marketplace
```

### 2. Add Your Plugin Entry

Edit `.claude-plugin/marketplace.json` and add your plugin:

```json
{
  "name": "your-plugin-name",
  "tier": "community",
  "description": "Brief description (one sentence)",
  "source": {
    "type": "git",
    "url": "https://github.com/YourUsername/your-plugin.git"
  },
  "tags": ["relevant", "tags"]
}
```

**Important:**
- Use `"tier": "curated"` or `"tier": "community"`
- Plugin name must be lowercase with hyphens
- Description should be concise

### 3. Run the Validator Locally

```bash
python scripts/validate-plugins.py
```

The validator will:
1. Clone your plugin repository
2. Validate manifest against schema
3. Check tier policy compliance
4. Scan for secrets (HARD FAIL)
5. Scan for network code (enforced per tier)
6. Scan for telemetry (HARD FAIL)
7. Check consistency (declared vs detected)

**Fix any errors before proceeding.**

### 4. Submit a Pull Request

```bash
git checkout -b add-your-plugin-name
git add .claude-plugin/marketplace.json
git commit -m "feat: Add your-plugin-name to community plugins"
gh pr create
```

### 5. Address Review Feedback

A maintainer will review:
- Security scan results
- Manifest accuracy
- Domain allowlist (for community)
- Risk declaration accuracy

---

## Security Policy

### Always Blocked (All Tiers)

- **Hardcoded secrets** - API keys, tokens, passwords, private keys
- **Telemetry/analytics** - PostHog, Sentry, Segment, etc.
- **Obfuscated code** - Minified or encoded payloads

### Curated-Specific Blocks

- **All network code** - requests, fetch, curl, urllib, axios
- **Socket usage** - Python socket module
- **Shell network commands** - wget, nc, ssh, scp

### Community-Specific Rules

- Network code **allowed only if**:
  - `capabilities.network.mode: "allowlist"`
  - All domains explicitly declared
  - `risk.dataEgress` specified
- Detected domains must match declared domains

### Enforcement

All checks are enforced at PR validation time:

| Check | Curated | Community |
|-------|---------|-----------|
| Secrets | HARD FAIL | HARD FAIL |
| Telemetry | HARD FAIL | HARD FAIL |
| Network code | HARD FAIL | Allowed with allowlist |
| Undeclared domains | N/A | HARD FAIL |

**Malicious plugins will be removed and authors banned.**

---

## Declaring Network Domains

If your community plugin needs network access:

1. List all domains your code accesses
2. Add them to `capabilities.network.domains`
3. Specify risk level in `risk.dataEgress`
4. Add notes explaining data flow

```json
{
  "capabilities": {
    "network": {
      "mode": "allowlist",
      "domains": [
        "api.github.com",
        "api.linear.app"
      ]
    }
  },
  "risk": {
    "dataEgress": "medium",
    "notes": "Sends repository name and issue IDs to GitHub/Linear APIs"
  }
}
```

---

## Review Timeline

- Initial review: 3-5 business days
- Complex plugins may take longer
- Community plugins require additional security review

---

## After Approval

Once merged:
- Plugin appears in [CATALOG.md](CATALOG.md)
- Users can install via: `claude /plugin install juni-skills:your-plugin-name`

---

## Questions?

- Open an issue for questions about contribution process
- See [schema/examples/](schema/examples/) for manifest examples
- See [marketplace/](marketplace/) for tier documentation
