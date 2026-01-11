# juni-tools-marketplace

A curated marketplace of Claude Code plugins for professional development workflows.

## Available Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| **cook** | Feature development with guardrails. Plan, Review, Code, Ship. | v1.0.1 |
| **trimmer** | Token guard hook that blocks oversized prompts. | v1.0.0 |

---

## Quick Install (60 seconds)

### Step 1: Add the Marketplace

```bash
claude /marketplace add github:PJuniszewski/juni-tools-marketplace
```

### Step 2: Install Plugin(s)

**Install a single plugin:**
```bash
claude /plugin install juni-tools:cook
```

**Install all plugins:**
```bash
claude /plugin install juni-tools:cook juni-tools:trimmer
```

### Step 3: Enable Plugin(s)

```bash
claude /plugin enable cook
claude /plugin enable trimmer
```

---

## Configuration

### trimmer

The trimmer plugin requires two environment variables:

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

### Example 1: Install Only Trimmer

```bash
# Add marketplace
claude /marketplace add github:PJuniszewski/juni-tools-marketplace

# Install and enable trimmer
claude /plugin install juni-tools:trimmer
claude /plugin enable trimmer

# Configure environment
export ANTHROPIC_API_KEY="sk-ant-..."
export TOKEN_GUARD_MODEL="claude-sonnet-4-20250514"
```

### Example 2: Install Both Plugins

```bash
# Add marketplace
claude /marketplace add github:PJuniszewski/juni-tools-marketplace

# Install both plugins
claude /plugin install juni-tools:cook juni-tools:trimmer

# Enable both plugins
claude /plugin enable cook trimmer

# Configure trimmer environment
export ANTHROPIC_API_KEY="sk-ant-..."
export TOKEN_GUARD_MODEL="claude-sonnet-4-20250514"
```

---

## Team / Project Setup

For teams, you can pre-configure plugins in your project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": [
    "github:PJuniszewski/juni-tools-marketplace"
  ],
  "enabledPlugins": [
    "juni-tools:trimmer",
    "juni-tools:cook"
  ]
}
```

When team members clone the project and run Claude Code, the marketplace and plugins are automatically recognized.

### Per-Plugin Example

Enable only trimmer for a project:

```json
{
  "extraKnownMarketplaces": [
    "github:PJuniszewski/juni-tools-marketplace"
  ],
  "enabledPlugins": [
    "juni-tools:trimmer"
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
claude /plugin install juni-tools:trimmer@v1.0.0

# Install latest
claude /plugin install juni-tools:trimmer
```

### Marketplace Repository

The marketplace itself is versioned, but plugin installs reference individual plugin versions.

---

## Release Checklist

When releasing a new plugin version:

### 1. Tag Plugin Release

```bash
cd claude-cook  # or claude-trimmer
git tag v1.0.1
git push origin v1.0.1
```

### 2. Update Marketplace (if needed)

Update `recommended_version` in `.claude-plugin/marketplace.json`:

```json
{
  "name": "cook",
  "recommended_version": "v1.0.1",
  ...
}
```

Commit and push:

```bash
cd juni-tools-marketplace
git add .claude-plugin/marketplace.json
git commit -m "Update cook to v1.0.1"
git push origin main
```

### 3. Verify Install Commands

Test the installation flow:

```bash
# Fresh install test
claude /marketplace add github:PJuniszewski/juni-tools-marketplace
claude /plugin install juni-tools:cook@v1.0.1
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
| trimmer | [PJuniszewski/claude-trimmer](https://github.com/PJuniszewski/claude-trimmer) |

---

## License

MIT License - see [LICENSE](LICENSE)
