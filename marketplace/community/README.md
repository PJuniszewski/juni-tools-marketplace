# Community Plugins

Community-contributed plugins that **may use network** via explicit allowlist. Install at your discretion.

## Policy Requirements

| Requirement | Value | Enforcement |
|-------------|-------|-------------|
| Network | Allowlist only | Detected & validated by validator |
| Domains | Explicit hostnames | No wildcards, no IPs |
| Risk declaration | Required | `risk.dataEgress` must be specified |
| Telemetry | None | Detected & rejected by validator |
| Secrets in code | None | Detected & rejected by validator |

## Manifest Requirements

```json
{
  "policyTier": "community",
  "capabilities": {
    "network": {
      "mode": "allowlist",
      "domains": [
        "api.github.com",
        "api.example.com"
      ]
    }
  },
  "risk": {
    "dataEgress": "medium",
    "notes": "Sends repository metadata to GitHub API"
  }
}
```

## Domain Allowlist Rules

Allowed:
- Explicit hostnames: `api.github.com`, `example.com`
- Subdomains: `api.service.example.com`

**Not allowed:**
- Wildcards: `*.example.com`
- IP addresses: `192.168.1.1`
- Protocols in domain: `https://example.com`
- Catch-all: `*`

## Risk Levels

| Level | Description | Example |
|-------|-------------|---------|
| `low` | Reads public data only | Fetch public API docs |
| `medium` | Sends non-sensitive metadata | Repository name, file counts |
| `high` | May send sensitive data | File contents, code snippets |

## Current Community Plugins

| Plugin | Network Domains | Risk | Author |
|--------|-----------------|------|--------|
| *None yet* | — | — | [Submit yours!](../../CONTRIBUTING.md) |

## Submitting a Community Plugin

1. Fork this repository
2. Add your plugin with `policyTier: "community"`
3. Declare all network domains in `capabilities.network.domains`
4. Specify `risk.dataEgress` and optional `risk.notes`
5. Run validator locally: `python scripts/validate-plugins.py`
6. Submit PR with filled-out checklist

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for full instructions.
