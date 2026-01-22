# juni-skills-marketplace

A curated marketplace of Claude Code plugins for professional development workflows.

> **Security Notice:** Plugins execute with your full user permissions (filesystem, shell, environment variables). Official plugins are maintained by [@PJuniszewski](https://github.com/PJuniszewski). Community plugins are third-party contributions — review source code before enabling. This marketplace does NOT guarantee plugin safety.

## Official Plugins

Maintained by [@PJuniszewski](https://github.com/PJuniszewski).

| Plugin | Description | Version |
|--------|-------------|---------|
| **cook** | Feature development with guardrails. Plan, Review, Code, Ship. | v1.5.3 |
| **context-guard** | Context optimization for JSON data - lossless compression, token analysis, sampling warnings. | v1.0.0 |

## Community Plugins

Third-party contributions. Install at your own discretion.

| Plugin | Author | Description | Version |
|--------|--------|-------------|---------|
| *No community plugins yet* | — | [Submit yours!](CONTRIBUTING.md) | — |

## Contributing

Want to add your plugin to the marketplace? See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Plugin requirements checklist
- Submission process
- Review criteria

---

## Quick Install (60 seconds)

### Step 1: Add the Marketplace

```bash
claude /plugin
# Then select "Add Marketplace" and enter: PJuniszewski/juni-skills-marketplace
```

### Step 2: Install Plugin(s)

**Install a single plugin:**
```bash
claude /plugin install juni-skills:cook
```

**Install all plugins:**
```bash
claude /plugin install juni-skills:cook juni-skills:context-guard
```

### Step 3: Enable Plugin(s)

```bash
claude /plugin enable cook
claude /plugin enable context-guard
```

---

## Configuration

### context-guard

Works out of the box - no configuration required.

**How it works:** Automatically analyzes every prompt you send. When you paste large JSON data and ask forensic questions (e.g., "Why did request id=abc123 fail?"), the plugin warns you that sampling might hide the answer.

**Example scenario:**
```
You: Here's my API logs: [50,000 chars of JSON]
     Why did request id=abc123 fail?

[context-guard] WARNING: Forensic query detected ("request id=abc123")
                         with large payload (~12,500 tokens)
[context-guard] HINT: The specific record might get trimmed.
                      Add #trimmer:mode=analysis to allow sampling.
```

**Optional environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `TOKEN_GUARD_MIN_CHARS` | 6000 | Below this, always allow |
| `TOKEN_GUARD_WARN_CHARS` | 15000 | Above this, warn user |
| `TOKEN_GUARD_HARD_LIMIT_CHARS` | 100000 | Above this, block (context flooding) |
| `TOKEN_GUARD_FAIL_CLOSED` | false | Block on forensic+large (vs warn) |

**Escape hatches in prompts:**
- `#trimmer:off` - Disable for this prompt
- `#trimmer:force` - Bypass all checks
- `#trimmer:mode=analysis` - Allow sampling for forensic queries

### cook

The cook plugin works out of the box. Optional configuration:

- Add `CLAUDE.md` to your project root for project-specific rules
- Create `.claude/agents/` directory for custom review agents

---

## Installation Examples

### Example 1: Install Only Context Guard

```bash
# Add marketplace (run /plugin, select "Add Marketplace", enter: PJuniszewski/juni-skills-marketplace)

# Install and enable context-guard
claude /plugin install juni-skills:context-guard
claude /plugin enable context-guard

# Ready! Hook auto-analyzes prompts with large JSON payloads.
```

### Example 2: Install Both Plugins

```bash
# Add marketplace (run /plugin, select "Add Marketplace", enter: PJuniszewski/juni-skills-marketplace)

# Install both plugins
claude /plugin install juni-skills:cook juni-skills:context-guard

# Enable both plugins
claude /plugin enable cook context-guard

# Both plugins work out of the box!
```

---

## Team / Project Setup

For teams, you can pre-configure plugins in your project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace"
  ],
  "enabledPlugins": [
    "juni-skills:context-guard",
    "juni-skills:cook"
  ]
}
```

When team members clone the project and run Claude Code, the marketplace and plugins are automatically recognized.

### Per-Plugin Example

Enable only context-guard for a project:

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-skills-marketplace"
  ],
  "enabledPlugins": [
    "juni-skills:context-guard"
  ]
}
```

> **Note:** Organization policies may restrict hooks and plugin execution. Check with your org admin if plugins fail to load or execute.

---

## Versioning Strategy

### Plugin Repositories

Each plugin repository uses semantic versioning tags:

```
v0.1.0  - Initial release
v0.1.1  - Patch/bugfix
v0.2.0  - Minor feature addition
v1.0.0  - Stable release
```

### Installing Specific Versions

```bash
# Install specific version
claude /plugin install juni-skills:context-guard@v1.0.0

# Install latest
claude /plugin install juni-skills:context-guard
```

### Marketplace Repository

The marketplace itself is versioned, but plugin installs reference individual plugin versions.

---

## Release Checklist

When releasing a new plugin version:

### 1. Tag Plugin Release

```bash
cd cook  # or context-guard
git tag v1.5.3
git push origin v1.5.3
```

### 2. Update README Version Table

Update the version in this README's Available Plugins table to reflect the new release.

Commit and push:

```bash
cd juni-skills-marketplace
git add README.md
git commit -m "Update cook to v1.5.3"
git push origin main
```

### 3. Verify Install Commands

Test the installation flow:

```bash
# Fresh install test (run /plugin, select "Add Marketplace", enter: PJuniszewski/juni-skills-marketplace)
claude /plugin install juni-skills:cook@v1.5.3
claude /plugin enable cook

# Verify plugin loads
claude /plugin list
```

### 4. Update Changelog

Document changes in each plugin's CHANGELOG.md.

---

## Repository Links

| Repository | URL |
|------------|-----|
| Marketplace | [PJuniszewski/juni-skills-marketplace](https://github.com/PJuniszewski/juni-skills-marketplace) |
| cook | [PJuniszewski/cook](https://github.com/PJuniszewski/cook) |
| context-guard | [PJuniszewski/context-guard](https://github.com/PJuniszewski/context-guard) |

---

## License

MIT License - see [LICENSE](LICENSE)
