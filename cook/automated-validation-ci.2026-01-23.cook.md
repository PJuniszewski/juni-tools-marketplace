# Cooking Result

## Dish
Add automated plugin validation with CI pipeline to ensure marketplace quality and contributor safety.

## Status
well-done

## Cooking Mode
well-done

## Current Phase
Complete - Ready for Implementation

## Ownership
- Decision Owner: @PJuniszewski
- Reviewers: Product, Security, QA
- Approved by: _TBD_

---

# Phase 0 - Project Policy & Context

## Sources Scanned
| File | Status | Key Rules |
|------|--------|-----------|
| CLAUDE.md | Not found | N/A |
| README.md | Scanned | Security warning for plugins, Official vs Community separation |
| .claude/agents/*.md | Not found | N/A |
| CONTRIBUTING.md | Scanned | Contribution flow documented, PR checklist exists |
| CODEOWNERS | Scanned | @PJuniszewski reviews all changes |

## Hard Rules (must not be violated)
1. Do not break existing `marketplace.json` schema
2. Maintain Official vs Community category distinction
3. Security checklist requirements in PR template must be preserved
4. CODEOWNERS review requirement for marketplace.json

## Preferred Patterns
1. Pure Python standard library (no heavy dependencies)
2. GitHub Actions for CI
3. Deterministic, fast validation
4. Clean report output with pass/fail counts

## Detected Conflicts
None - this is additive functionality.

## Policy Alignment Risk
LOW - Automated validation strengthens existing contributor guidelines.

---

# Step 1 - Read the Order

## Feature Summary
Add automated plugin validation infrastructure to ensure marketplace quality:
- **A)** Python validation script (`scripts/validate-plugins.py`) that:
  - Parses marketplace.json
  - Clones each plugin repo (depth=1)
  - Validates: manifest, README, LICENSE, content directories
  - Validates: JSON schema, required fields, unique names, valid URLs
  - Detects: binary files, oversized files, disallowed extensions
  - Reports: pass/fail per plugin with detailed reasons
  - Exits non-zero on any failure (CI-compatible)
- **B)** GitHub Actions workflow (`.github/workflows/validate.yml`):
  - Triggers on PR touching marketplace.json or validator
  - Triggers on push to main
  - Runs Python 3.11 validation
- **C)** Update contribution scaffolding:
  - CONTRIBUTING.md already exists - update with validator instructions
  - PR template already exists - verify checklist matches validator
  - CODEOWNERS already exists - moved to .github/CODEOWNERS
- **D)** README polish:
  - Document validation CI
  - Explain marketplace/plugin installation
  - Clarify Official vs Community distinction

## Affected Modules/Components
| Module | Impact | Risk Level |
|--------|--------|------------|
| scripts/validate-plugins.py | New file | LOW |
| .github/workflows/validate.yml | New file | LOW |
| .github/CODEOWNERS | Move from root | LOW |
| CONTRIBUTING.md | Update | LOW |
| README.md | Update | LOW |
| CODEOWNERS (root) | Delete (move) | LOW |

## Dependencies
- Python 3.11 (GitHub Actions runner)
- git CLI (for cloning plugin repos)
- No external Python packages (stdlib only)

## Microwave Blocker Check
NOT BLOCKED - This is infrastructure/tooling, not auth/schema/API/payments.

---

# Step 2 - Ingredient Approval (Product Review)

## Product Decision
**APPROVED** - Essential for marketplace scalability and contributor safety.

## Scope

### In Scope
- Python validation script with comprehensive checks
- GitHub Actions CI pipeline
- Updated contribution documentation
- CODEOWNERS in proper location (.github/)

### Out of Scope
- Automated security scanning (SAST/DAST)
- Commit pinning for plugin versions
- Automated release tagging
- Plugin signature verification

### Non-goals
- This is NOT a plugin execution sandbox
- This is NOT a malware scanner (only structure validation)
- This does NOT verify plugin functionality works correctly

## User Value
1. **Contributors**: Clear, automated feedback on plugin requirements
2. **Maintainers**: Reduced manual review burden, consistent quality bar
3. **Users**: Higher confidence in marketplace plugin quality

## Assumptions
- Contributors have git CLI available locally
- Plugin repos are public and clonable
- Python 3.11+ available on CI runners

---

# Step 3 - Presentation Planning (UX Review)

## UX Decision
**Not Required** - This is backend tooling/CI with no user-facing UI.

## User Flow
CLI-based developer workflow:
1. Contributor forks repo
2. Adds plugin entry to marketplace.json
3. Runs `python scripts/validate-plugins.py` locally
4. Opens PR
5. CI runs automatically, blocks merge if validation fails

## UI Components Affected
| Component | Change Type | Notes |
|-----------|-------------|-------|
| GitHub PR checks | New | Shows validation pass/fail |
| Terminal output | New | Validation report with emoji indicators |

## Accessibility Considerations
N/A - CLI output only. Report uses text indicators alongside emoji (✅/❌).

---

# Step 4 - Implementation Plan

## Architecture Decision

### Selected Approach
Single Python script with pure stdlib, comprehensive validation, and clean reporting.

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Bash script | Simple, ubiquitous | Hard to maintain, poor error handling | Rejected: maintainability |
| Node.js | Familiar to web devs | Adds dependency, heavier | Rejected: unnecessary complexity |
| Python + external libs | Rich ecosystem | Dependency management overhead | Rejected: unnecessary for scope |
| **Python stdlib only** | No deps, fast, cross-platform | Limited features | **Selected**: fits requirements |

### Trade-offs
- Sacrificing: Rich library features (requests, pyyaml, etc.)
- Gaining: Zero dependencies, fast CI, no version conflicts

## Patch Plan

### Files to Modify
| File | Change | Risk |
|------|--------|------|
| scripts/validate-plugins.py | Create (~350 lines) | LOW |
| .github/workflows/validate.yml | Create (~25 lines) | LOW |
| .github/CODEOWNERS | Create (move from root) | LOW |
| CODEOWNERS | Delete (replaced by .github/CODEOWNERS) | LOW |
| CONTRIBUTING.md | Update with validator instructions | LOW |
| README.md | Add CI badge, validation explanation | LOW |

### Commit Sequence
1. `feat: Add plugin validation script with comprehensive checks`
2. `ci: Add GitHub Actions workflow for plugin validation`
3. `chore: Move CODEOWNERS to .github/ directory`
4. `docs: Update CONTRIBUTING.md with validator instructions`
5. `docs: Update README.md with CI validation info`

(Or single commit: `feat: Add automated plugin validation with CI`)

### High-risk Areas
- Cloning external repos (network dependency, could fail in CI)
- Binary detection heuristics (false positives possible)
- File size limits (may reject legitimate large plugins)

---

# Step 5 - QA Review

## Test Plan

### Test Cases
| # | Scenario | Given | When | Then |
|---|----------|-------|------|------|
| 1 | Valid plugins | Both cook and context-guard are valid | Run validator | Both pass, exit 0 |
| 2 | Missing manifest | Plugin repo lacks plugin.json | Run validator | Fail with clear message |
| 3 | Missing LICENSE | Plugin repo lacks LICENSE | Run validator | Fail with clear message |
| 4 | Duplicate plugin name | Two plugins with same name | Run validator | Fail: duplicate detected |
| 5 | Invalid category | Plugin has category "premium" | Run validator | Fail: invalid category |
| 6 | Binary file detected | Plugin contains .exe file | Run validator | Fail: disallowed file type |
| 7 | Invalid JSON manifest | plugin.json is malformed | Run validator | Fail: invalid JSON |
| 8 | Missing content dirs | No commands/hooks/agents/skills | Run validator | Fail: no content dirs |
| 9 | Invalid source URL | URL doesn't start with https:// | Run validator | Fail: invalid URL |
| 10 | CI trigger on PR | PR touches marketplace.json | Push to PR | CI runs validation |

### Edge Cases
- Plugin repo is private (clone fails gracefully)
- Plugin repo is very large (size limit enforced)
- Plugin has symlinks (warned, not failed)
- Plugin name contains special chars (sanitized for temp dir)
- Network timeout during clone (CI retry handles)

### Acceptance Criteria
- [ ] Given valid marketplace.json, when running validator, then exit code is 0
- [ ] Given plugin missing LICENSE, when running validator, then exit code is 1 with clear error
- [ ] Given PR touching marketplace.json, when pushed, then CI runs validation workflow
- [ ] Given validator script, when run locally, then same result as CI

### Regression Checks
- Existing README installation instructions still work
- Existing CONTRIBUTING.md checklist still valid
- marketplace.json schema unchanged for existing plugins

---

# Step 6 - Security Review

## Security Status
- Reviewed: yes
- Risk level: **MEDIUM** (clones external repos, runs in CI)

## Security Checklist
| Check | Status | Notes |
|-------|--------|-------|
| Input validation | PASS | marketplace.json schema validated before processing |
| Auth/authz | N/A | Public repos only, no auth required |
| Data exposure | PASS | No secrets in script, temp dirs cleaned up |
| Injection vectors | PASS | No shell interpolation of untrusted input |
| Command injection | PASS | subprocess with list args, not shell=True |
| Path traversal | PASS | Relative paths derived from plugin name, sanitized |
| DoS via large repos | PASS | MAX_REPO_SIZE_BYTES and MAX_FILES_COUNT limits |
| Binary/malware | PARTIAL | Detects known bad extensions, but not malware scanner |

## Issues Found
1. **MEDIUM**: Cloning arbitrary URLs could expose CI to malicious repos
   - Mitigation: Depth=1 clone, size limits, temp dir cleanup
   - Mitigation: URL must be valid GitHub URL pattern

2. **LOW**: Bait-and-switch attack (plugin passes validation, then changes)
   - Mitigation: Existing README security warning, CODEOWNERS review
   - Future: Consider commit pinning in marketplace.json

3. **LOW**: Validator cannot detect obfuscated malicious code
   - Mitigation: This is a structure validator, not SAST
   - Mitigation: Human review still required for community plugins

## Security Approval
**APPROVED with MEDIUM risk accepted** - Mitigations in place, residual risk documented.

---

# Step 7 - Documentation

## Documentation Updates
| File | Change Needed |
|------|---------------|
| CONTRIBUTING.md | Add local validation instructions |
| README.md | Add CI badge, validation section, How to Verify |
| .github/PULL_REQUEST_TEMPLATE.md | Verify checklist matches validator (already good) |

## New Documentation Needed
- **How to Verify** section in README with exact commands:
  ```bash
  python scripts/validate-plugins.py
  ```
- CI workflow explanation for contributors
- Validation report interpretation guide (inline in validator output)

---

# Risk Management

## Pre-mortem (3 scenarios required)
| # | What Could Go Wrong | Likelihood | Impact | Mitigation |
|---|---------------------|------------|--------|------------|
| 1 | Validator false positive blocks valid plugin | LOW | MEDIUM | Tune limits, clear error messages, maintainer can override |
| 2 | CI fails due to network issues cloning repos | MEDIUM | LOW | GitHub Actions retry, contributor can re-run |
| 3 | Existing plugins fail validation unexpectedly | LOW | HIGH | Test against current plugins before merge |

## Rollback Plan
1. Delete `.github/workflows/validate.yml` to disable CI
2. Keep `scripts/validate-plugins.py` for local use (optional)
3. Revert CONTRIBUTING.md changes if needed

## Blast Radius
- Affected users/modules: Contributors only (no runtime impact)
- Feature flag: No (can disable by deleting workflow)
- Rollout strategy: Immediate (CI infra, not user-facing)

---

# Decision Log

| Date | Phase | Decision | Rationale |
|------|-------|----------|-----------|
| 2026-01-23 | Step 0.0 | Artifact created | Starting cook flow |
| 2026-01-23 | Phase 0 | Project scanned | No CLAUDE.md, existing docs reviewed |
| 2026-01-23 | Step 1 | Order read | 4 deliverables: validator, CI, docs, README |
| 2026-01-23 | Step 2 | Product APPROVED | Essential for marketplace scalability |
| 2026-01-23 | Step 3 | UX Not Required | CLI-only tooling |
| 2026-01-23 | Step 4 | Python stdlib approach | Zero dependencies, fits requirements |
| 2026-01-23 | Step 5 | QA plan defined | 10 test cases, edge cases documented |
| 2026-01-23 | Step 6 | Security APPROVED | MEDIUM risk accepted with mitigations |
| 2026-01-23 | Step 7 | Docs identified | CONTRIBUTING.md, README.md updates |
| 2026-01-23 | Implementation | Complete | All files created, validator tested ✅ |
