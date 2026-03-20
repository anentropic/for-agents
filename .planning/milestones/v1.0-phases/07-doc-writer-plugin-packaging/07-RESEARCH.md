# Phase 7: Doc-Writer Plugin Packaging - Research

**Researched:** 2026-03-15
**Domain:** Claude Code plugin system — directory structure, manifest schema, namespace conventions, marketplace distribution
**Confidence:** HIGH (primary sources: official Claude Code documentation at code.claude.com, verified against existing codebase)

---

## Summary

The Claude Code plugin system is well-specified and the existing `skills/` and `agents/` directories already use the correct internal structure. Phase 7 is a reorganisation and wrapping exercise: move the existing tree into a `doc-writer/` subdirectory, add a `.claude-plugin/plugin.json` manifest, and register a `marketplace.json` at the repo root so future plugins can be added alongside it. No agent or skill logic needs to change — only file paths and the manifest declaration.

The existing codebase already uses `${CLAUDE_PLUGIN_ROOT}` correctly in all skill files and the `doc-writer:` namespace prefix in agent frontmatter `skills:` references. The reorganisation formalises what was already being assumed.

The right distribution pattern for this project is a **self-hosted GitHub marketplace** (a `marketplace.json` at the repo root pointing to `./doc-writer` as a relative-path plugin source). Users install the marketplace once and then `claude plugin install doc-writer@<marketplace-name>`. This supports the stated goal of hosting multiple plugins in future milestones — each plugin becomes another subdirectory and another entry in `marketplace.json`.

**Primary recommendation:** Move `skills/` and `agents/` into `doc-writer/`, add `.claude-plugin/plugin.json` with `name: "doc-writer"`, add repo-root `.claude-plugin/marketplace.json` listing the plugin, and update any hardcoded path references in bats tests.

---

## Standard Stack

### Core
| Component | Version/Format | Purpose | Why Standard |
|-----------|---------------|---------|--------------|
| `.claude-plugin/plugin.json` | JSON (Claude Code spec) | Plugin manifest — declares name, version, description | Required by CC plugin loader; `name` field drives namespace |
| `.claude-plugin/marketplace.json` | JSON (Claude Code spec) | Marketplace catalog at repo root | Allows `claude plugin install` and supports multi-plugin repo |
| `skills/<name>/SKILL.md` | Markdown + YAML frontmatter | Skill definition; directory name = slash-command suffix | CC auto-discovers at this path |
| `agents/*.md` | Markdown + YAML frontmatter | Subagent definitions | CC auto-discovers at `agents/` in plugin root |

### Supporting
| Component | Purpose | When to Use |
|-----------|---------|-------------|
| `CHANGELOG.md` | Version history | Release tracking; recommend adding alongside plugin.json |
| `settings.json` (plugin root) | Default settings applied on enable | Only if a default agent should be activated — not needed here |
| `--plugin-dir ./doc-writer` | Local testing flag | Development validation before distribution |
| `claude plugin validate .` | Validate JSON syntax | After creating/editing manifest files |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Marketplace (marketplace.json) | Direct `--plugin-dir` only | No `claude plugin install` support; users must clone and reference path manually |
| Relative-path plugin source | npm package | npm requires package.json, publishing step; overkill for a Markdown-only plugin |
| Single-plugin repo | Multi-plugin repo via marketplace | Repo already explicitly designed for multi-plugin future milestones |

---

## Architecture Patterns

### Recommended Project Structure

After Phase 7, the repo root should look like:

```
doc-writer-agent/           # repo root
├── .claude-plugin/
│   └── marketplace.json    # repo-level marketplace catalog
├── doc-writer/             # plugin directory (was: skills/ + agents/ at root)
│   ├── .claude-plugin/
│   │   └── plugin.json     # plugin manifest
│   ├── skills/
│   │   ├── diataxis/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   ├── edit/
│   │   │   └── SKILL.md
│   │   ├── quality-rules/
│   │   │   └── SKILL.md
│   │   ├── review/
│   │   │   └── SKILL.md
│   │   ├── setup/
│   │   │   ├── SKILL.md
│   │   │   ├── defaults/
│   │   │   └── scripts/
│   │   └── write/
│   │       ├── SKILL.md
│   │       └── scripts/
│   └── agents/
│       ├── doc-author.md
│       ├── doc-editor.md
│       └── doc-persona.md
├── tests/                  # unchanged
└── .planning/              # unchanged
```

The `skills/` and `agents/` directories at the repo root disappear entirely. Everything moves one level deeper under `doc-writer/`.

### Pattern 1: Plugin Manifest (plugin.json)

**What:** A minimal JSON manifest in `.claude-plugin/plugin.json` inside the plugin directory that declares the plugin identity. The `name` field drives namespacing — skills become `/doc-writer:<skill-name>`.

**When to use:** Always required when distributing as a formal plugin. Without it, CC auto-discovers components but the plugin has no stable name or version.

```json
// Source: https://code.claude.com/docs/en/plugins-reference
// doc-writer/.claude-plugin/plugin.json
{
  "name": "doc-writer",
  "version": "1.0.0",
  "description": "AI-powered library documentation generator. Produces audience-calibrated, Diataxis-structured docs via a full Author > Editor > Persona pipeline.",
  "author": {
    "name": "Your Name"
  },
  "homepage": "https://github.com/you/doc-writer-agent",
  "repository": "https://github.com/you/doc-writer-agent",
  "license": "MIT"
}
```

**Key point:** `name: "doc-writer"` means all skills become `/doc-writer:write`, `/doc-writer:setup`, `/doc-writer:review`, `/doc-writer:edit`. This matches the namespace already embedded in agent frontmatter `skills:` references (e.g. `doc-writer:quality-rules`).

### Pattern 2: Marketplace Catalog (marketplace.json)

**What:** A `marketplace.json` at the repo root (under `.claude-plugin/`) that lists the plugin. This is the multi-plugin-ready structure — future plugins are additional entries.

**When to use:** When you want users to install via `claude plugin install` and when the repo will host multiple plugins.

```json
// Source: https://code.claude.com/docs/en/plugin-marketplaces
// .claude-plugin/marketplace.json (repo root)
{
  "name": "doc-writer-agent",
  "owner": {
    "name": "Your Name"
  },
  "metadata": {
    "description": "Claude Code plugins for automated library documentation",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "doc-writer",
      "source": "./doc-writer",
      "description": "AI-powered library documentation generator",
      "version": "1.0.0"
    }
  ]
}
```

**Note:** With `metadata.pluginRoot: "./plugins"`, the source `"./doc-writer"` resolves relative to that root. Alternatively, omit `pluginRoot` and write `"source": "./doc-writer"` with paths relative to the repo root.

**Installation flow for users:**
```bash
# Add the marketplace (once)
/plugin marketplace add <github-owner>/<repo-name>
# or from local:
/plugin marketplace add ./path/to/doc-writer-agent

# Install the plugin
/plugin install doc-writer@doc-writer-agent
```

### Pattern 3: Namespace Conventions

**What:** Plugin name in `plugin.json` defines the namespace prefix for all skills and agents.

**Source:** https://code.claude.com/docs/en/plugins-reference (confirmed HIGH confidence)

| Component | Before (standalone) | After (plugin) |
|-----------|--------------------|----|
| Skill invocation | `/write` | `/doc-writer:write` |
| Skill invocation | `/setup` | `/doc-writer:setup` |
| Agent reference in skills field | `doc-writer:quality-rules` | `doc-writer:quality-rules` (UNCHANGED — already correct) |
| Agent names | `doc-author`, `doc-editor`, `doc-persona` | unchanged (agent names are not namespaced in frontmatter) |

**Critical finding:** The existing agent files (`doc-author.md`, `doc-editor.md`, `doc-persona.md`) already reference skills with the `doc-writer:` prefix:
```yaml
skills:
  - doc-writer:quality-rules
  - doc-writer:diataxis
```
These references are already correct for the plugin namespace. No changes needed to agent frontmatter `skills:` lists.

### Pattern 4: CLAUDE_PLUGIN_ROOT in Skill Content

**What:** All path references to plugin-internal files use `${CLAUDE_PLUGIN_ROOT}` so they resolve correctly regardless of installation location.

**Verification:** The existing skill files already use this correctly:
- `bash ${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/detect-project.sh`
- `bash ${CLAUDE_PLUGIN_ROOT}/skills/write/scripts/scan-exports.sh`

After reorganisation, these paths remain valid because the skills and scripts move together inside the `doc-writer/` plugin directory. `${CLAUDE_PLUGIN_ROOT}` will point to the `doc-writer/` directory after installation.

### Anti-Patterns to Avoid

- **Putting `commands/`, `agents/`, or `skills/` inside `.claude-plugin/`:** Only `plugin.json` belongs in `.claude-plugin/`. All component directories must be at the plugin root (i.e., directly inside `doc-writer/`).
- **Absolute paths in scripts:** Existing scripts reference `${CLAUDE_PLUGIN_ROOT}` correctly. Do not introduce absolute paths.
- **Relative paths with `../`:** Installed plugins cannot reference files outside their directory. The marketplace docs explicitly warn against `../shared-utils` patterns.
- **Version mismatch between plugin.json and marketplace.json:** Set version in only one place. For relative-path plugins, the marketplace entry takes precedence; for git/npm sources, `plugin.json` wins. Recommendation: set version in `plugin.json` only and omit from marketplace entry.
- **Leaving old `skills/` and `agents/` at repo root:** After moving to `doc-writer/`, remove the originals to avoid CC loading both.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Plugin loading/discovery | Custom loader scripts | CC native auto-discovery from `skills/` and `agents/` directories | CC handles this automatically when `plugin.json` name is set |
| Namespace enforcement | Prefix-injection scripts | `name` field in `plugin.json` | CC derives all component names from the manifest name |
| Installer script (npx/uv/shell) | Custom install script | CC marketplace (`claude plugin install`) | Marketplace is the native install mechanism; custom scripts would duplicate and diverge |
| File copying on install | Manual `cp -r` scripts | Marketplace caching (`~/.claude/plugins/cache`) | CC handles copying; plugins that work with `--plugin-dir` work installed |

**Key insight:** For a Markdown-only plugin (no compiled binaries, no npm packages), the CC marketplace with relative-path plugin source is the complete distribution solution. No installer script needed.

---

## Common Pitfalls

### Pitfall 1: Component directories inside .claude-plugin/

**What goes wrong:** Plugin loads but commands, agents, and skills are missing from Claude's context.
**Why it happens:** Developers assume `.claude-plugin/` is the plugin's root — it is not. It is only a metadata directory.
**How to avoid:** Only `plugin.json` (and `marketplace.json` at the repo level) go in `.claude-plugin/`. `skills/`, `agents/`, `hooks/` must be siblings of `.claude-plugin/`, not children.
**Warning signs:** `/doc-writer:write` not appearing after `--plugin-dir` load; `/help` shows no skills from the plugin.

### Pitfall 2: Tests with hardcoded pre-reorganisation paths

**What goes wrong:** Existing `.bats` test files reference `${PROJECT_ROOT}/skills/` and `${PROJECT_ROOT}/agents/` which will break after files move to `${PROJECT_ROOT}/doc-writer/skills/` and `${PROJECT_ROOT}/doc-writer/agents/`.
**Why it happens:** Tests were written against the original flat structure.
**How to avoid:** Update all bats test path references as part of the reorganisation. This is a required step, not optional.
**Warning signs:** `bats tests/phase-01-validation.bats` reports "file not found" errors.

### Pitfall 3: Relative-path plugin source fails with URL-based marketplace

**What goes wrong:** Users try to add the marketplace via a direct URL to `marketplace.json` (not the git repo), and plugins with `"source": "./doc-writer"` fail to install.
**Why it happens:** URL-based marketplace fetch only downloads the JSON file; relative paths require the full repo to be cloned.
**How to avoid:** Distribute the marketplace as a GitHub repo reference (the default recommended pattern), not as a raw URL. Document this in the README.
**Warning signs:** Plugin install fails with "path not found" after marketplace is added via URL.

### Pitfall 4: Missing version bump prevents updates

**What goes wrong:** Plugin is updated (skills changed, bugs fixed) but installed users don't receive the update.
**Why it happens:** CC uses the version field to detect whether to update. If version stays the same, CC treats it as already up-to-date.
**How to avoid:** Bump `version` in `plugin.json` with every release that users should receive as an update.
**Warning signs:** `/plugin update doc-writer@marketplace` reports "already up to date" despite changed files.

### Pitfall 5: Agent skills field references wrong namespace

**What goes wrong:** Agents fail to load preloaded skills because the `skills:` field doesn't match the plugin namespace.
**Why it happens:** Namespace derives from `plugin.json` `name` field. If the name changes (e.g., from `doc-writer` to something else), all agent frontmatter `skills:` references break.
**How to avoid:** Keep `plugin.json` `name: "doc-writer"` stable. Don't rename the plugin without updating all agent files.
**Warning signs:** Agents spawn without quality-rules and diataxis context; runtime errors about skill not found.

---

## Code Examples

Verified patterns from official sources:

### plugin.json (minimal, correct)
```json
// Source: https://code.claude.com/docs/en/plugins-reference
{
  "name": "doc-writer",
  "version": "1.0.0",
  "description": "AI-powered library documentation generator",
  "author": {
    "name": "Your Name"
  }
}
```

### marketplace.json (repo root, multi-plugin ready)
```json
// Source: https://code.claude.com/docs/en/plugin-marketplaces
{
  "name": "doc-writer-plugins",
  "owner": {
    "name": "Your Name"
  },
  "plugins": [
    {
      "name": "doc-writer",
      "source": "./doc-writer",
      "description": "AI-powered library documentation generator"
    }
  ]
}
```

### Local development test command
```bash
# Source: https://code.claude.com/docs/en/plugins
claude --plugin-dir ./doc-writer
# Then in CC session:
# /doc-writer:setup
# /doc-writer:write
```

### Installation from GitHub marketplace
```bash
# Source: https://code.claude.com/docs/en/plugin-marketplaces
# Users run (once):
/plugin marketplace add github-owner/doc-writer-agent
# Then:
/plugin install doc-writer@doc-writer-plugins
```

### Validate plugin structure
```bash
# Source: https://code.claude.com/docs/en/plugin-marketplaces
claude plugin validate .
# Or from within a CC session:
/plugin validate .
```

### Skill frontmatter — no changes needed (already correct)
```yaml
# Source: existing skills/write/SKILL.md — verified correct
---
name: write
description: Generate new documentation using the full Author > Editor > Persona pipeline with gap detection, revision loop, and quality validation.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--skip-gap-scan]"
---
```

### Agent frontmatter — skills references already namespaced correctly
```yaml
# Source: existing agents/doc-author.md — verified correct
---
name: doc-author
description: Writes draft library documentation using Diataxis framework.
tools: Read, Write, Glob, Grep, Bash
model: inherit
skills:
  - doc-writer:quality-rules
  - doc-writer:diataxis
---
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.claude/commands/*.md` (standalone) | `skills/<name>/SKILL.md` in plugin | CC introduced skills system | Existing code already uses new format |
| No marketplace support | `marketplace.json` with `git-subdir` source type for monorepos | Current | Supports sparse clone of plugin subdirectory from multi-plugin repo |
| Manual file copying to `~/.claude/` | `claude plugin install` via marketplace | Current | Native installer; no shell scripts needed |

**Deprecated/outdated:**
- `.claude/commands/*.md` files: Still work but skills (`SKILL.md` in subdirectory) are the current recommended approach. Existing code already uses the skill format correctly.
- Manual `cp -r` installer scripts: Superseded by marketplace installation. No need to build one.

---

## Open Questions

1. **Marketplace name choice**
   - What we know: `name` in `marketplace.json` is the `@suffix` users see when installing (`doc-writer@<name>`). Reserved names include anthropic-related strings.
   - What's unclear: Whether to name it `doc-writer-agent` (matches repo name) or `doc-writer-plugins` (describes content category better).
   - Recommendation: Use `doc-writer-plugins` to signal future multi-plugin intent. The planner can decide.

2. **extraKnownMarketplaces in .claude/settings.json**
   - What we know: Adding `extraKnownMarketplaces` to `.claude/settings.json` pre-registers the marketplace for anyone who clones the repo. This prompts team members to install automatically.
   - What's unclear: Whether the project author wants this in-repo convenience config.
   - Recommendation: Add it to `.claude/settings.json` pointing to the GitHub repo. Makes the plugin self-advertising to repo cloners.

3. **Phase 7 scope — README.md**
   - What we know: Official docs recommend a `README.md` with installation and usage instructions inside the plugin directory.
   - What's unclear: Whether README.md is in scope for Phase 7 or deferred.
   - Recommendation: Include a minimal plugin-level `README.md` in `doc-writer/` as part of packaging. It is trivial to write and expected by marketplace conventions.

---

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation: true` in .planning/config.json). Test framework is bats.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bats (Bash Automated Testing System) |
| Config file | none — test files invoked directly |
| Quick run command | `bats tests/phase-07-validation.bats` |
| Full suite command | `bats tests/` |

### Phase Requirements to Test Map

Phase 7 requirements are structural/packaging (no runtime logic to unit-test). All tests are structural assertions (file existence, JSON validity, content checks).

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PKG-01 | `doc-writer/` directory exists with correct structure | structural | `bats tests/phase-07-validation.bats::PKG-01` | ❌ Wave 0 |
| PKG-02 | `doc-writer/.claude-plugin/plugin.json` exists and has `name: "doc-writer"` | structural | `bats tests/phase-07-validation.bats::PKG-02` | ❌ Wave 0 |
| PKG-03 | `.claude-plugin/marketplace.json` exists at repo root with plugin entry | structural | `bats tests/phase-07-validation.bats::PKG-03` | ❌ Wave 0 |
| PKG-04 | All 6 skills exist at new path `doc-writer/skills/<name>/SKILL.md` | structural | `bats tests/phase-07-validation.bats::PKG-04` | ❌ Wave 0 |
| PKG-05 | All 3 agents exist at new path `doc-writer/agents/*.md` | structural | `bats tests/phase-07-validation.bats::PKG-05` | ❌ Wave 0 |
| PKG-06 | `${CLAUDE_PLUGIN_ROOT}` references in skill files point to valid relative paths under `doc-writer/` | structural | `bats tests/phase-07-validation.bats::PKG-06` | ❌ Wave 0 |
| PKG-07 | Old `skills/` and `agents/` directories at repo root are gone | structural | `bats tests/phase-07-validation.bats::PKG-07` | ❌ Wave 0 |
| PKG-08 | Existing phase-01-validation.bats passes with updated paths | regression | `bats tests/phase-01-validation.bats` | ✅ (needs path update) |
| PKG-09 | `claude plugin validate ./doc-writer` exits 0 (plugin JSON valid) | structural | `claude plugin validate ./doc-writer` (manual gate) | ❌ Wave 0 |

Note: PKG-09 requires Claude Code CLI — flag as manual-only if `claude` is not available in CI.

### Sampling Rate
- **Per task commit:** `bats tests/phase-07-validation.bats`
- **Per wave merge:** `bats tests/`
- **Phase gate:** Full suite green + manual `claude --plugin-dir ./doc-writer` smoke test before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/phase-07-validation.bats` — covers PKG-01 through PKG-08
- [ ] Update `tests/phase-01-validation.bats` — change `${PROJECT_ROOT}/skills/` to `${PROJECT_ROOT}/doc-writer/skills/` and `${PROJECT_ROOT}/agents/` to `${PROJECT_ROOT}/doc-writer/agents/`

---

## Sources

### Primary (HIGH confidence)
- https://code.claude.com/docs/en/plugins-reference — Complete plugin manifest schema, component paths, CLAUDE_PLUGIN_ROOT, CLI commands, directory structure
- https://code.claude.com/docs/en/plugins — Plugin creation walkthrough, --plugin-dir testing, migration from .claude/ to plugin, structure overview
- https://code.claude.com/docs/en/plugin-marketplaces — marketplace.json schema, relative-path plugin sources, git-subdir sparse clone, GitHub hosting, extraKnownMarketplaces
- https://code.claude.com/docs/en/skills — Skill frontmatter reference, namespace conventions (plugin-name:skill-name), user-invocable vs disable-model-invocation, CLAUDE_PLUGIN_ROOT vs CLAUDE_SKILL_DIR

### Secondary (MEDIUM confidence)
- Existing codebase at `/Users/paul/Documents/Dev/Personal/doc-writer-agent/` — verified that agent frontmatter already uses correct `doc-writer:` namespace prefix in `skills:` references; skill files already use `${CLAUDE_PLUGIN_ROOT}` correctly

### Tertiary (LOW confidence)
- None — all critical claims verified against official docs

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all specifications from official Claude Code docs fetched 2026-03-15
- Architecture: HIGH — directory structure, manifest schema, and namespace rules fully specified in official docs
- Pitfalls: HIGH — most pitfalls explicitly called out in official documentation warnings; test path breakage confirmed by reading existing test files
- Distribution: HIGH — marketplace.json format and git-based distribution fully specified

**Research date:** 2026-03-15
**Valid until:** 2026-05-15 (stable spec; Claude Code plugin system is documented and versioned)
