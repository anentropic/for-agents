# Technology Stack: Plugin Upgrade Helpers

**Project:** doc-writer v1.5.0 Plugin Upgrade Helpers
**Researched:** 2026-03-26
**Scope:** 3-way text merge, YAML config schema diffing, Q&A version tracking
**Constraint:** Must work within Claude Code skill system (bash scripts + markdown instructions, no heavy npm dependencies, no Node.js app structure)

## Recommended Stack

### 3-Way Merge: `diff3` (System Utility)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| diff3 | FreeBSD diff3 20220517 (macOS built-in) | 3-way merge of guidance/rules markdown files | Zero-dependency, pre-installed on macOS and Linux, purpose-built for exactly this problem |

**How it works:**

`diff3 -m <user-modified> <original-at-setup> <new-plugin-version>` produces a merged file that:
- Auto-applies non-overlapping changes from both sides (exit code 0)
- Inserts conflict markers for overlapping changes (exit code 1)
- Preserves the full diff3 marker format: `<<<<<<<`, `|||||||` (base), `=======`, `>>>>>>>`

**Verified on this system:** `/usr/bin/diff3` is present (FreeBSD diff3 20220517). Tested with markdown content -- non-overlapping section edits merge cleanly; overlapping edits produce parseable conflict markers.

**Integration with skill system:**

The upgrade skill runs diff3 via Bash tool on each guidance file:

```bash
diff3 -m .doc-writer/{framework}.md \
         .doc-writer/.originals/{framework}.md \
         ${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{framework}.md \
         > /tmp/merged-{framework}.md
```

Exit code 0: auto-merged cleanly, replace file.
Exit code 1: conflicts present, Claude reads the merged file, presents conflicts to user via AskUserQuestion.
Exit code 2: trouble (file missing, etc.), fall back to manual review.

**File sizes in play (guidance markdown files):**

| File | Lines |
|------|-------|
| mkdocs-material.md | 196 |
| sphinx-shibuya.md | 288 |
| odoc.md | 399 |
| plain-markdown.md | 68 |
| rules.md | 27 |

These are small enough that diff3 handles them instantly. The conflict markers are also easy for Claude to read and present to the user.

**Why this and not alternatives:**

| Alternative | Why Not |
|-------------|---------|
| Node.js diff3 npm package | Adds npm dependency to a markdown/bash skill system -- architectural mismatch |
| Git's merge-file | Requires files to be in a git repo and staged -- too heavyweight for config file merge |
| Python difflib | Not 3-way; only 2-way diff. Would need custom merge logic |
| Claude-as-merger (prompt-based) | Unreliable for precise text operations; could hallucinate content; not auditable |
| Manual side-by-side | Bad UX for non-conflicting changes that should auto-merge |

### YAML Config Schema Diffing: Claude-as-Reader (No External Tool)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Claude agent (skill instructions) | N/A | Detect new/removed/changed fields between config template versions | Config template is 35 lines of simple YAML -- Claude reads both versions and compares them more reliably than bash regex |

**Why not a YAML parser tool:**

The config-template.yaml is intentionally simple (35 lines, 2 levels of nesting). Bash-based YAML key extraction was tested and is fragile for nested structures (array items, indented sub-keys parse incorrectly). External tools like `yq` or `dyff` are not guaranteed to be installed on user systems. Since the upgrade skill runs within Claude Code (an LLM agent), Claude itself is the most reliable YAML reader available -- it can:

1. Read the old config template (stored at setup time in `.doc-writer/.originals/config-template.yaml`)
2. Read the new config template from `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/config-template.yaml`
3. Compare them to identify: new top-level fields, new sub-fields within existing sections, removed/deprecated fields, changed default values
4. Read the user's `.doc-writer/config.yaml` to check which new fields are already present (user may have added them manually)
5. Apply additions with defaults, warn on deprecations

**The skill instructions encode the comparison logic** -- no code needed. This is the same pattern used throughout doc-writer: Claude reads files and acts on instructions.

**Fallback for version field detection (bash-based):**

One specific check does benefit from bash: reading the `version:` field from config.yaml to determine if migration is needed. This is a single-line grep:

```bash
grep -E '^version:' .doc-writer/config.yaml | awk '{print $2}'
```

This is reliable because `version:` is always a top-level scalar. Similarly for `plugin_version:`.

### Q&A Version Tracking: Question ID Matching

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Markdown section headers as stable IDs | N/A | Track which Q&A questions have been answered across plugin versions | Questions already have stable identifiers (`## Question N: {topic}`) in .qa.md files; no new tooling needed |

**Approach: Store answered question IDs at setup time.**

Current Q&A files use `## Question N: {topic}` headers (e.g., `## Question 1: Navigation strategy`). These are already unique per framework. The upgrade system:

1. At setup time, record which questions were asked and answered in a manifest file
2. At upgrade time, compare the current .qa.md file's question headers against the manifest
3. New questions (headers not in manifest) get presented to the user
4. Removed questions are ignored (answers remain in context.md)

**Manifest format** (stored in `.doc-writer/.originals/qa-manifest.yaml`):

```yaml
framework: mkdocs-material
plugin_version: "1.4.0"
questions_answered:
  - id: "Question 1: Navigation strategy"
    answer: "Sections as top tabs"
  - id: "Question 2: API reference approach"
    answer: "mkdocstrings"
  - id: "Question 3: Rich features usage"
    answer: ["Content tabs", "Mermaid diagrams", "Admonitions"]
```

**Detection of new questions is a simple set difference:**

```bash
# Extract question IDs from current .qa.md
grep -E '^## Question' ${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/${framework}.qa.md | sed 's/^## //'

# Compare against manifest
# (Claude reads both and identifies gaps -- same pattern as config diffing)
```

**Why this approach:**

- No schema migration system needed -- the .qa.md files are versioned with the plugin
- Question headers are human-readable IDs (not opaque UUIDs)
- Storing answers enables re-ask only if the question changed (compare answer options too)
- Works for dynamically-generated Q&A (odoc sub-topic questions) by storing the topic name

### Version Tracking: plugin.json + config.yaml

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| plugin.json `version` field | Existing | Source of truth for current plugin version | Already exists, already maintained |
| config.yaml `plugin_version` field | New | Record which plugin version was used at setup/upgrade time | Enables version comparison at upgrade time |

**Version comparison is string-based semver:**

```bash
# Read versions
INSTALLED=$(python3 -c "import json; print(json.load(open('${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json'))['version'])" 2>/dev/null)
# Fallback if python unavailable:
INSTALLED=$(grep '"version"' ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json | sed 's/.*: "//;s/".*//')

CONFIGURED=$(grep -E '^plugin_version:' .doc-writer/config.yaml | awk '{print $2}' | tr -d '"')
```

For semver comparison in bash, `sort -V` handles it:

```bash
if [ "$INSTALLED" != "$CONFIGURED" ]; then
  NEWER=$(printf '%s\n%s' "$INSTALLED" "$CONFIGURED" | sort -V | tail -1)
  if [ "$NEWER" = "$INSTALLED" ]; then
    echo "Plugin upgraded from $CONFIGURED to $INSTALLED"
  fi
fi
```

**Note:** `sort -V` (version sort) is available on both GNU coreutils (Linux) and macOS.

### Originals Storage: File Copy at Setup Time

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| File copy (cp) | System built-in | Store original copies of files at setup time for 3-way merge base | Simplest possible approach; no database; no serialization |

**Storage location:** `.doc-writer/.originals/`

```
.doc-writer/
  .originals/
    config-template.yaml    # Template used to generate config
    {framework}.md          # Guidance file as shipped
    rules.md                # Rules file as shipped
    qa-manifest.yaml        # Q&A answers (generated, not copied)
  config.yaml              # User's config (possibly customized)
  {framework}.md           # User's guidance (possibly customized)
  rules.md                 # User's rules (possibly customized)
  context.md               # Generated by researcher
```

**Why `.originals/` inside `.doc-writer/`:**
- Co-located with the files they track
- User can inspect them
- No hidden metadata outside the project's doc-writer directory
- Dot-prefixed so it does not clutter the directory for normal operations

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| 3-way merge | diff3 (system) | node-diff3 npm package | Architectural mismatch -- skill system is bash/markdown, not Node.js |
| 3-way merge | diff3 (system) | Claude-as-merger | Unreliable for precise text; not auditable; uses context window for mechanical task |
| 3-way merge | diff3 (system) | git merge-file | Requires git-tracked files; more complex invocation for same result |
| YAML diff | Claude-as-reader | yq CLI | Not guaranteed installed; overkill for 35-line file |
| YAML diff | Claude-as-reader | dyff CLI | External binary dependency; overkill for simple comparison |
| YAML diff | Claude-as-reader | Python PyYAML | Not guaranteed installed (verified: not available on this system) |
| YAML diff | Claude-as-reader | bash grep/awk | Tested: fragile for nested YAML structures |
| Q&A tracking | Question header IDs | Database/SQLite | Massive overkill; adds binary dependency |
| Q&A tracking | Question header IDs | JSON manifest | YAML is already used everywhere in this project; consistency |
| Version tracking | config.yaml field | Separate version file | Adds another file; config.yaml is the natural home |
| Originals storage | File copies | Git-based diffing | Not all projects use git; adds complexity; originals may not be in history |
| Originals storage | File copies | Checksums only | Detects changes but cannot merge; need actual content for diff3 |

## Architecture Fit Assessment

### What the skill system provides natively

The doc-writer skill system is **Claude + Bash + Read/Write/Glob/Grep**. Every "tool" must be either:

1. **A bash command** available on standard macOS/Linux (used via `Bash` tool or `!` backtick dynamic context)
2. **Claude itself** reading files and following instructions (the primary "compute engine")
3. **File I/O** via Read/Write tools

The recommended stack uses only (1) for diff3/grep/cp and (2) for YAML comparison and conflict resolution. No new dependencies are introduced.

### What must NOT be added

| Anti-dependency | Why |
|-----------------|-----|
| npm packages | Plugin is not a Node.js project; no package.json; would require install step |
| Python libraries | Not guaranteed on user systems (PyYAML verified not installed on this macOS) |
| Compiled binaries | Distribution nightmare for a Claude Code plugin |
| External services | Plugin must work offline |
| Database files | Overkill; state is in .doc-writer/ directory |

## Installation / Setup

No installation needed. All tools are:
- `diff3`: pre-installed on macOS (FreeBSD diff3) and Linux (GNU diffutils)
- `grep`, `awk`, `sed`, `sort`, `cp`: standard Unix utilities
- Claude: the runtime environment itself

The only new artifacts are:
1. An upgrade skill file (new `skills/upgrade/SKILL.md`)
2. An upgrade detection script (new `skills/upgrade/scripts/detect-upgrade.sh`)
3. Modifications to setup skill to store originals at setup time
4. A new `plugin_version` field in config-template.yaml

## Confidence Assessment

| Component | Confidence | Reason |
|-----------|------------|--------|
| diff3 for 3-way merge | HIGH | Verified on system; tested with markdown; well-documented Unix utility since 1979 |
| Claude-as-reader for YAML | HIGH | Already the pattern used throughout doc-writer; config template is small and simple |
| Q&A question header IDs | HIGH | Existing .qa.md files already use this naming convention; tested grep extraction |
| Version comparison via sort -V | MEDIUM | Available on modern macOS/Linux but not verified on all target systems |
| .originals/ storage pattern | HIGH | Simple file copy; no moving parts; users can inspect and understand |

## Sources

- [diff3 Wikipedia](https://en.wikipedia.org/wiki/Diff3) -- algorithm description and history
- [GNU Diffutils Manual](https://www.gnu.org/software/diffutils/manual/html_mono/diff.html) -- diff3 options and conflict markers
- [Merging with diff3 (blog)](https://blog.jcoglan.com/2017/05/08/merging-with-diff3/) -- detailed algorithm walkthrough
- [zdiff3 and conflict styles](https://www.ductile.systems/zdiff3/) -- conflict marker format reference
- [diff3 Linux examples](https://www.tecmint.com/diff3-command-in-linux/) -- practical usage patterns
- Verified: `/usr/bin/diff3` present on macOS Darwin 24.6.0 (FreeBSD diff3 20220517)
- Verified: `python3 -c "import yaml"` fails on this system (PyYAML not available)
- Verified: `which yq` not found on this system
- Verified: diff3 tested with markdown guidance-like content; non-overlapping changes merge cleanly (exit 0); overlapping changes produce parseable conflict markers (exit 1)
