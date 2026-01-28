# Curated Plugins

Security-first plugins with **no network access**. Recommended for teams and production use.

## Policy Requirements

| Requirement | Value | Enforcement |
|-------------|-------|-------------|
| Network | None | Detected & rejected by validator |
| Telemetry | None | Detected & rejected by validator |
| Secrets in code | None | Detected & rejected by validator |
| Risk level | Low | Enforced by tier policy |

## Manifest Requirements

```json
{
  "policyTier": "curated",
  "capabilities": {
    "network": {
      "mode": "none"
    }
  }
}
```

## What Gets Scanned

The validator scans `commands/`, `hooks/`, `agents/`, and `skills/` directories for:

### Network Libraries (blocked)
- Python: `requests`, `urllib.request`, `http.client`, `aiohttp`, `httpx`
- JavaScript: `fetch()`, `axios`, `XMLHttpRequest`, WebSocket
- Shell: `curl`, `wget`, `nc`, `socat`

### Telemetry (blocked)
- Analytics URLs (posthog, sentry, segment, amplitude)
- Tracking endpoints
- Beacon URLs

### Secrets (blocked)
- AWS keys, GitHub tokens, private keys
- API keys, bearer tokens
- Password assignments

## Current Curated Plugins

Plugins in this directory have passed full security review:

| Plugin | Description | Maintainer |
|--------|-------------|------------|
| juni | Juni Skills Suite - workflows + context safety | @PJuniszewski |

## Becoming Curated

Community plugins may be promoted to curated if:
1. Network code is removed or refactored
2. Full code review passes
3. Maintainer commits to ongoing review
