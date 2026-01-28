# Marketplace Tiers

This marketplace uses a two-tier security model:

| Tier | Network | Risk | Default For |
|------|---------|------|-------------|
| **curated/** | None | Low | Teams, Production |
| **community/** | Allowlist only | Declared | Opt-in, Individual use |

## Directory Structure

```
marketplace/
├── curated/         # Security-first plugins (no network)
│   └── <plugin>/    # Each plugin has its own directory
└── community/       # Community plugins (network via allowlist)
    └── <plugin>/
```

## Tier Selection

### Use `curated/` when:
- Deploying to teams or organizations
- Security is a primary concern
- You need plugins that work fully offline
- You want minimal attack surface

### Use `community/` when:
- You need network-dependent features (API integrations, webhooks)
- You accept the declared risk profile
- You've reviewed the allowlisted domains
- Individual/personal use with understood trade-offs

## Plugin Requirements by Tier

### Curated Tier

- `policyTier: "curated"` in manifest
- `capabilities.network.mode: "none"` (enforced)
- No network libraries in code (detected & rejected by validator)
- No telemetry or analytics (detected & rejected by validator)
- Full code review by maintainers

### Community Tier

- `policyTier: "community"` in manifest
- `capabilities.network.mode: "allowlist"` with explicit domains
- `risk.dataEgress: "low" | "medium" | "high"` (required)
- Domains must be explicit hostnames (no wildcards, no IPs)
- Network usage must match declared domains

## Validation

All plugins are validated by CI:

```bash
# Run validator locally
python scripts/validate-plugins.py

# Run tests
python scripts/test_validator.py
```

The validator:
1. Validates manifest against JSON schema
2. Enforces tier-specific policies
3. Scans code for network/telemetry usage
4. Checks consistency (declared vs detected)
5. Fails on secrets detection
