# Contributing to juni-skills-marketplace

We welcome community plugin contributions! This document explains how to submit your plugin.

## Plugin Requirements

Before submitting, ensure your plugin meets these requirements:

### Required

- [ ] Public GitHub repository
- [ ] Valid `plugin.json` manifest with required fields
- [ ] README.md with:
  - What the plugin does
  - Installation command
  - Example usage
- [ ] License file (MIT or Apache 2.0 recommended)
- [ ] At least one version tag (e.g., `v1.0.0`)

### Quality Bar

- [ ] Plugin serves a clear, documented use case
- [ ] Commands/skills have meaningful descriptions
- [ ] No duplicate functionality with existing plugins
- [ ] No binaries or large generated files committed

### Security

- [ ] No hardcoded credentials or secrets
- [ ] No obfuscated code
- [ ] No hidden telemetry (must be disclosed if present)
- [ ] No data exfiltration to external servers

## Submission Process

### 1. Fork and Clone

```bash
gh repo fork PJuniszewski/juni-skills-marketplace --clone
cd juni-skills-marketplace
```

### 2. Add Your Plugin Entry

Edit `.claude-plugin/marketplace.json` and add your plugin to the `plugins` array:

```json
{
  "name": "your-plugin-name",
  "category": "community",
  "description": "Brief description of what your plugin does (one sentence)",
  "source": {
    "source": "url",
    "url": "https://github.com/YourUsername/your-plugin.git"
  },
  "tags": ["relevant", "tags"]
}
```

**Important:**
- Use `"category": "community"` for all community submissions
- Plugin name should be lowercase with hyphens (e.g., `my-cool-plugin`)
- Description should be concise (one sentence)
- Tags help users discover your plugin

### 3. Submit a Pull Request

```bash
git checkout -b add-your-plugin-name
git add .claude-plugin/marketplace.json
git commit -m "feat: Add your-plugin-name to community plugins"
gh pr create
```

The PR template will auto-populate with a checklist. Complete all items.

### 4. Address Review Feedback

A maintainer will review your submission. Be prepared to:
- Answer questions about your plugin's functionality
- Make changes if issues are found
- Provide additional documentation if needed

## Security Considerations

**Your plugin will execute with the user's full permissions.**

This means your plugin can:
- Access the filesystem
- Run shell commands
- Read environment variables
- Make network requests

**You are responsible for:**
- Ensuring your plugin does not contain malicious code
- Disclosing any telemetry or data collection
- Responding to security reports about your plugin
- Keeping your plugin updated and secure

**Malicious plugins will be removed and authors banned.**

## Review Timeline

- Initial review: 3-5 business days
- Complex plugins may take longer
- You'll receive feedback via PR comments

## After Approval

Once merged, your plugin will appear in:
- The "Community Plugins" section of the README
- The marketplace index (`marketplace.json`)

Users can install via:
```bash
claude /plugin install juni-skills:your-plugin-name
```

## Questions?

Open an issue for questions about the contribution process.
