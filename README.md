# juni-tools-marketplace

A curated marketplace of Claude Code plugins for professional development workflows.

## Available Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| **cook** | Feature development with guardrails. Plan, Review, Code, Ship. | v1.0.2 |
| **context-guard** | LLM Epistemic Safety Layer - prevents hallucinations on incomplete data. | v1.0.0-alpha.2 |

---

## Quick Install (60 seconds)

### Step 1: Add the Marketplace

```bash
claude /plugin
# Then select "Add Marketplace" and enter: PJuniszewski/juni-tools-marketplace
```

### Step 2: Install Plugin(s)

**Install a single plugin:**
```bash
claude /plugin install juni-tools:cook
```

**Install all plugins:**
```bash
claude /plugin install juni-tools:cook juni-tools:context-guard
```

### Step 3: Enable Plugin(s)

```bash
claude /plugin enable cook
claude /plugin enable context-guard
```

---

## Configuration

### context-guard

The context-guard plugin requires two environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export TOKEN_GUARD_MODEL="claude-sonnet-4-20250514"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) for persistence:

```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
echo 'export TOKEN_GUARD_MODEL="claude-sonnet-4-20250514"' >> ~/.zshrc
```

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for token counting |
| `TOKEN_GUARD_MODEL` | Yes | Model ID for token calculation (e.g., `claude-sonnet-4-20250514`) |

### cook

The cook plugin works out of the box. Optional configuration:

- Add `CLAUDE.md` to your project root for project-specific rules
- Create `.claude/agents/` directory for custom review agents

---

## Installation Examples

### Example 1: Install Only Context Guard

```bash
# Add marketplace (run /plugin, select "Add Marketplace", enter: PJuniszewski/juni-tools-marketplace)

# Install and enable context-guard
claude /plugin install juni-tools:context-guard
claude /plugin enable context-guard

# Configure environment
export ANTHROPIC_API_KEY="sk-ant-..."
export TOKEN_GUARD_MODEL="claude-sonnet-4-20250514"
```

### Example 2: Install Both Plugins

```bash
# Add marketplace (run /plugin, select "Add Marketplace", enter: PJuniszewski/juni-tools-marketplace)

# Install both plugins
claude /plugin install juni-tools:cook juni-tools:context-guard

# Enable both plugins
claude /plugin enable cook context-guard

# Configure context-guard environment
export ANTHROPIC_API_KEY="sk-ant-..."
export TOKEN_GUARD_MODEL="claude-sonnet-4-20250514"
```

---

## Team / Project Setup

For teams, you can pre-configure plugins in your project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-tools-marketplace"
  ],
  "enabledPlugins": [
    "juni-tools:context-guard",
    "juni-tools:cook"
  ]
}
```

When team members clone the project and run Claude Code, the marketplace and plugins are automatically recognized.

### Per-Plugin Example

Enable only context-guard for a project:

```json
{
  "extraKnownMarketplaces": [
    "PJuniszewski/juni-tools-marketplace"
  ],
  "enabledPlugins": [
    "juni-tools:context-guard"
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
claude /plugin install juni-tools:context-guard@v1.0.0

# Install latest
claude /plugin install juni-tools:context-guard
```

### Marketplace Repository

The marketplace itself is versioned, but plugin installs reference individual plugin versions.

---

## Release Checklist

When releasing a new plugin version:

### 1. Tag Plugin Release

```bash
cd claude-cook  # or context-guard
git tag v1.0.2
git push origin v1.0.2
```

### 2. Update README Version Table

Update the version in this README's Available Plugins table to reflect the new release.

Commit and push:

```bash
cd juni-tools-marketplace
git add README.md
git commit -m "Update cook to v1.0.2"
git push origin main
```

### 3. Verify Install Commands

Test the installation flow:

```bash
# Fresh install test (run /plugin, select "Add Marketplace", enter: PJuniszewski/juni-tools-marketplace)
claude /plugin install juni-tools:cook@v1.0.2
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
| Marketplace | [PJuniszewski/juni-tools-marketplace](https://github.com/PJuniszewski/juni-tools-marketplace) |
| cook | [PJuniszewski/claude-cook](https://github.com/PJuniszewski/claude-cook) |
| context-guard | [PJuniszewski/context-guard](https://github.com/PJuniszewski/context-guard) |

---

## License

MIT License - see [LICENSE](LICENSE)
