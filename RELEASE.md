# Release Strategy

This document describes the release tagging strategy for the marketplace.

## Tag Types

| Tag | Content | Stability | Use Case |
|-----|---------|-----------|----------|
| `stable` | Curated plugins only | Production-ready | Teams, production |
| `edge` | Curated + all community | Latest features | Development, testing |
| `vX.Y.Z` | Specific release | Pinned version | Reproducibility |

## For Users

### Production/Teams: Use `stable`

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace@stable"
  ]
}
```

The `stable` tag:
- Only includes curated plugins
- Updated when curated plugins change
- Security-reviewed before tagging

### Development: Use `edge`

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace@edge"
  ]
}
```

The `edge` tag:
- Includes all plugins (curated + community)
- Updated on every main branch commit
- Latest features, may have rough edges

### Reproducibility: Use Version Tags

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace@v3.0.0"
  ]
}
```

Version tags:
- Immutable, never moved
- Follow semver (MAJOR.MINOR.PATCH)
- Recommended for production with update management

---

## For Maintainers

### Creating a Release

1. **Update version in marketplace.json**

   ```bash
   # Edit .claude-plugin/marketplace.json
   # Bump "version": "X.Y.Z"
   ```

2. **Regenerate catalog**

   ```bash
   python scripts/generate-catalog.py
   ```

3. **Commit and push**

   ```bash
   git add .
   git commit -m "chore: Release vX.Y.Z"
   git push origin main
   ```

4. **Create version tag**

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

5. **Update floating tags**

   ```bash
   # Update stable (curated only - verify no community plugins with issues)
   git tag -f stable
   git push -f origin stable

   # Update edge (all plugins)
   git tag -f edge
   git push -f origin edge
   ```

### Version Bumping Guidelines

| Change | Bump | Example |
|--------|------|---------|
| New curated plugin | MINOR | 3.0.0 → 3.1.0 |
| New community plugin | MINOR | 3.1.0 → 3.2.0 |
| Plugin update (features) | MINOR | 3.2.0 → 3.3.0 |
| Plugin fix (bugfix) | PATCH | 3.3.0 → 3.3.1 |
| Breaking schema change | MAJOR | 3.3.1 → 4.0.0 |
| Security fix | PATCH | (immediate) |
| Remove plugin | MAJOR | (breaking change) |

### Stable Tag Criteria

Before moving the `stable` tag:

- [ ] All curated plugins pass validation
- [ ] No security issues in curated plugins
- [ ] CATALOG.md is up to date
- [ ] CI is green

### Edge Tag Updates

The `edge` tag should be updated:
- On every merge to main
- After any plugin addition
- After validation changes

---

## Automation (Future)

Consider adding GitHub Actions to:
- Auto-update `edge` tag on main push
- Notify on `stable` tag updates
- Generate release notes from commits

Example workflow (`.github/workflows/release.yml`):

```yaml
name: Update edge tag

on:
  push:
    branches: [main]

jobs:
  update-edge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Update edge tag
        run: |
          git tag -f edge
          git push -f origin edge
```

---

## Changelog

Maintain a changelog for releases:

### v3.0.0

- Add A+B tiered security model
- Add JSON schema for plugin manifests
- Add tier enforcement in validator
- Add CATALOG.md auto-generation
- Expand test suite to 53 tests

### v2.0.0

- Unify cook and context-guard into juni plugin
- Add security scanning (secrets + network)

### v1.0.0

- Initial marketplace release
