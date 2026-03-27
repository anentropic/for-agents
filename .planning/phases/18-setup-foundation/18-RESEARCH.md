# Phase 18: Setup Foundation - Research

**Researched:** 2026-03-26
**Domain:** Doc-writer setup skill modifications -- version tracking, originals storage, Q&A answer persistence
**Confidence:** HIGH

## Summary

Phase 18 modifies the existing `/doc-writer:setup` skill to produce three new data artifacts that downstream phases (19-21) depend on: (1) a `plugin_version` field in `config.yaml` matching the version from `plugin.json`, (2) a `.doc-writer/.originals/` directory containing pristine copies of guidance and rules files as shipped by the plugin, and (3) a `qa_answers` section in `config.yaml` that persists framework Q&A answers keyed by question header. Additionally, the `odoc_author_scope` one-off exception must be folded into the `qa_answers` structure, and `doc-author.md` updated to read from there instead.

The scope is well-bounded: two files are modified (`skills/setup/SKILL.md` and `skills/setup/defaults/config-template.yaml`), one agent file is updated (`agents/doc-author.md`), and no new files or external dependencies are introduced. The existing setup flow (first-time, `--reset`, `--refresh-context`, update menu) must continue working identically for users who do not use the upgrade system. The modifications are purely additive -- new fields in config, new directory created alongside existing files, new persistence step after Q&A.

**Primary recommendation:** Implement as three focused changes to `SKILL.md` (write `plugin_version` in Step 3, create `.originals/` in Step 3, persist `qa_answers` after Step 2b.5) plus the config template update and the `odoc_author_scope` migration. Each change is independent and testable in isolation.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SETUP-01 | `plugin_version` field in `config.yaml` matching `plugin.json` version after setup | Add `plugin_version: ""` to config-template.yaml; modify Step 3 to read `plugin.json` and write the version value |
| SETUP-02 | `.doc-writer/.originals/` created with pristine copies of guidance and rules files | Modify Step 3 to create `.originals/` dir and copy files there alongside the user-facing copies |
| SETUP-03 | `qa_answers` section in `config.yaml` keyed by question headers from `.qa.md` files | Add `qa_answers:` structure to config-template.yaml; modify Step 2b.5 to persist answers; fold `odoc_author_scope` into `qa_answers.author_scope` |
| SETUP-04 | `--reset` refreshes `.originals/` with current plugin files | `--reset` already re-runs full Q&A then Step 3; since Step 3 will now create `.originals/`, reset automatically gets fresh originals |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

No CLAUDE.md file exists in the project root. Constraints are derived from the existing codebase conventions:

- **Agent files are markdown instruction files** -- no executable code; Claude interprets them directly
- **Skills use `${CLAUDE_PLUGIN_ROOT}` for portable file references** -- all paths in SKILL.md reference plugin files via this variable
- **Config is YAML** -- `config.yaml` is the single source of truth for project configuration; manually parsed by Claude
- **No external dependencies** -- the plugin uses only standard Unix tools (bash scripts) and Claude's built-in tool set
- **Existing flags must keep working** -- `--reset` and `--refresh-context` behavior must be preserved exactly

## Standard Stack

### Core

No new libraries or tools are needed. All changes are to markdown instruction files and a YAML template.

| Component | Purpose | Why Standard |
|-----------|---------|--------------|
| `config-template.yaml` | Config schema template populated at setup time | Existing pattern; adding fields to it |
| `SKILL.md` (setup) | Setup workflow instructions for Claude | Existing 583-line file; surgical additions |
| `plugin.json` | Source of truth for plugin version | Already exists at `doc-writer/.claude-plugin/plugin.json` |
| `.qa.md` files | Framework Q&A definitions with `header` fields | 4 existing files, unmodified by this phase |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `plugin_version` in config.yaml | Separate VERSION file | Extra file to maintain; plugin.json already has the version |
| `.originals/` inside `.doc-writer/` | Git history-based originals | Requires git, breaks for .gitignore'd projects, ambiguous commit selection |
| `qa_answers` in config.yaml | Separate `qa-answers.yaml` file | Extra file; config.yaml already holds all setup decisions |

## Architecture Patterns

### Current Setup Flow (Reference)

```
User runs /doc-writer:setup
  |
  v
Step 1: Re-Run Detection (check if config exists, handle flags)
  |
  v
Step 2: Full Q&A Flow
  2a.0: Use Cases -> 2a: Personas -> 2a.5: Tone -> 2b: Doc System
  -> 2b.3: Scaffold -> 2b.5: Framework Q&A -> 2c: Paths
  |
  v
Step 3: File Creation
  - Create .doc-writer/ directory
  - Write config.yaml from template + Q&A answers
  - Copy defaults/{doc_system}.md -> .doc-writer/{doc_system}.md
  - Copy defaults/rules.md -> .doc-writer/rules.md
  |
  v
Step 5: Context Enrichment (spawn doc-researcher)
```

### Modification Points (4 total)

**Modification 1: config-template.yaml -- add `plugin_version` and `qa_answers`**

Current template ends at:
```yaml
detected:
  language: ""
  doc_system: ""
  existing_docs: false
```

Add after `version: 1` (before `user_personas`):
```yaml
plugin_version: ""
```

Add after `detected:` block (at end of file):
```yaml
qa_answers: {}
```

**Modification 2: SKILL.md Step 3 -- write `plugin_version` and create `.originals/`**

In Step 3 (File Creation), add to the config.yaml write instruction (item 2):
- Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` to get the `version` field
- Write it as `plugin_version: "{version}"` in config.yaml

Add new items after item 4 (Copy rules file):
- Create `.doc-writer/.originals/` directory
- Copy `defaults/{doc_system}.md` to `.doc-writer/.originals/{doc_system}.md`
- Copy `defaults/rules.md` to `.doc-writer/.originals/rules.md`
- For FALLBACK framework (researcher-generated files): copy from `.doc-writer/{doc_system}.md` to `.doc-writer/.originals/{doc_system}.md` (the researcher-generated file IS the baseline)

**Modification 3: SKILL.md Step 2b.5 -- persist `qa_answers`**

Current behavior (Step 2b.5, item 4):
> Record all answers. Framework Q&A answers do NOT go into config.yaml.

Change to:
> Record all answers. **After all framework questions are answered, persist the answers to `config.yaml` under a `qa_answers` section.** Use the `header` field from each question (lowercased, spaces replaced with underscores) as the key. Store selected label(s) as the value (string for single-select, array for multi-select). Also pass answers in-memory to the researcher in Step 5 (unchanged).

Key derivation from header fields across all frameworks:

| Framework | Question | Header | qa_answers Key |
|-----------|----------|--------|---------------|
| mkdocs-material | Q1 | "Navigation" | `navigation` |
| mkdocs-material | Q2 | "API docs" | `api_docs` |
| mkdocs-material | Q3 | "Features" | `features` |
| sphinx-shibuya | Q1 | "Navigation" | `navigation` |
| sphinx-shibuya | Q2 | "API docs" | `api_docs` |
| sphinx-shibuya | Q3 | "Features" | `features` |
| odoc | Q1 | "Structure" | `structure` |
| odoc | Q2 | "Scope" | `scope` (replaces `odoc_author_scope`) |
| odoc | Q3 | "Guides" | `guides` |
| plain-markdown | Q1 | "Callouts" | `callouts` |
| plain-markdown | Q2 | "Headings" | `headings` |
| plain-markdown | Q3 | "TOC" | `toc` |

**Modification 4: Fold `odoc_author_scope` into `qa_answers`**

Current exception in Step 2b.5:
> If `doc_system` is `odoc`, persist the Question 2 answer (author scope) to `config.yaml` as `odoc_author_scope`.

Remove this exception. The answer is now stored at `qa_answers.scope` (from the "Scope" header). The `odoc_author_scope` field is removed from config-template.yaml.

Update `doc-author.md` line 372 to read `qa_answers.scope` instead of `odoc_author_scope`:
> **Scope control:** Read `qa_answers.scope` from `.doc-writer/config.yaml`. If the value is `".mld pages only"` (the label text), skip this entire section. If the value contains ".mld pages + .mli" or is absent/empty, proceed with the enrichment workflow below.

Note: The stored value changes from the internal code `"mld-only"` / `"mld-and-mli"` to the actual label text `".mld pages only"` / `".mld pages + .mli doc comment improvements (Recommended)"`. The doc-author check must match against the label, not the old code. This is simpler (no translation layer) and consistent with how all other qa_answers store the literal label.

### Resulting Config Example (mkdocs-material)

```yaml
# .doc-writer/config.yaml -- generated by /doc-writer:setup
version: 1
plugin_version: "1.5.0"

user_personas:
  - name: "Python developers building REST APIs"
    skill_level: "intermediate"
    assumed_knowledge: ["Python basics", "HTTP/REST"]
    never_assume: ["Library internals"]
    domain_context: "Web API development"
    discovery_story: "Found via PyPI search"
    user_tasks: ["Set up rate limiting", "Configure per-route limits"]

tone: "warm-businesslike"

use_cases: []
use_cases_section: false

doc_system: "mkdocs-material"
api_reference: "mkdocstrings"

paths:
  docs_root: "docs/"
  source_root: "src/"

detected:
  language: "python"
  doc_system: "mkdocs-material"
  existing_docs: true

qa_answers:
  navigation: "Sections as top tabs"
  api_docs: "mkdocstrings"
  features:
    - "Content tabs"
    - "Mermaid diagrams"
    - "Admonitions"
```

### Resulting Config Example (odoc)

```yaml
# excerpt showing qa_answers for odoc
qa_answers:
  structure: "Single library"
  scope: ".mld pages + .mli doc comment improvements (Recommended)"
  guides:
    - "Getting started / Tutorial"
    - "How-to guides"
```

Note: No more `odoc_author_scope` field. The value lives at `qa_answers.scope`.

### Resulting Directory Structure

```
.doc-writer/
  config.yaml              # now includes plugin_version + qa_answers
  rules.md                 # user's copy (possibly customized)
  mkdocs-material.md       # user's copy (possibly customized)
  context.md               # regenerated by researcher
  .originals/
    rules.md               # pristine copy from defaults/ at setup time
    mkdocs-material.md     # pristine copy from defaults/ at setup time
```

### Anti-Patterns to Avoid

- **Do not change the Q&A interaction flow:** The questions asked, their order, and the user experience remain identical. Only what happens AFTER answers are collected changes (persistence to config).
- **Do not write `.originals/` before the user-facing copies:** Write user-facing copies first (existing behavior), then copy to `.originals/`. This preserves the existing write order and makes the originals a clear derivative step.
- **Do not modify `--refresh-context` behavior:** This flag skips Q&A entirely and only re-runs the researcher. It must not touch `qa_answers` or `.originals/`.
- **Do not introduce framework-specific logic into the qa_answers persistence:** The persistence logic is generic -- iterate over Q&A answers, derive key from header, write to `qa_answers`. The odoc `author_scope` exception is eliminated by this generalization, not replaced with a new exception.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML key derivation from headers | Complex slug function | Simple lowercase + underscore replacement | Headers are already short, single-word or two-word phrases; over-engineering adds no value |
| Version reading from plugin.json | JSON parser | Claude reads the file and extracts the version field | plugin.json is 11 lines; Claude already parses it reliably; no external tool needed |
| Originals directory management | Complex sync logic | Simple file copy in Step 3 | Originals are only written at setup/reset time; no partial sync, no differential update |

## Common Pitfalls

### Pitfall 1: Forgetting to handle the FALLBACK framework path for `.originals/`

**What goes wrong:** For custom/unknown frameworks, the researcher generates `{doc_system}.md` locally in `.doc-writer/` via the FALLBACK path. There is no corresponding file in `defaults/`. If `.originals/` tries to copy from `defaults/`, it will fail.
**Why it happens:** The setup flow has two file sources: `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/` for built-in frameworks, and `.doc-writer/` for FALLBACK-generated frameworks (where `framework_root` = `.doc-writer`).
**How to avoid:** After the user-facing guidance file is written (Step 3, item 3), the originals copy should use the SAME source that was used for the user-facing copy. If `framework_root` is `.doc-writer` (FALLBACK), copy from `.doc-writer/{doc_system}.md` to `.doc-writer/.originals/{doc_system}.md`. If `framework_root` is `defaults/`, copy from `defaults/` to `.originals/`.
**Warning signs:** Missing `.originals/{doc_system}.md` file for projects using non-standard frameworks.

### Pitfall 2: Breaking the `--reset` confirmation message

**What goes wrong:** The `--reset` confirmation mentions "Guidance files and rules will be replaced with defaults." After adding `.originals/`, the message should also mention that originals will be refreshed.
**Why it happens:** The confirmation message in Step 1 is static text that does not mention `.originals/`.
**How to avoid:** Update the `--reset` confirmation to mention that `.originals/` will also be refreshed. This is a cosmetic but important clarity change.
**Warning signs:** User confused about what `--reset` does to `.originals/`.

### Pitfall 3: The `odoc_author_scope` migration breaking doc-author

**What goes wrong:** `doc-author.md` currently reads `odoc_author_scope` from config. If we remove the field from config-template but do not update doc-author, the .mli enrichment workflow will silently default to "enabled" (because absent/empty defaults to running enrichment).
**Why it happens:** The doc-author reads this field at write time, potentially long after setup. If an existing project upgrades, the old `odoc_author_scope` field still exists in their config but is no longer written by new setups.
**How to avoid:** Update doc-author.md to read from `qa_answers.scope` instead. For backward compatibility, also check `odoc_author_scope` as a fallback: if `qa_answers.scope` is absent but `odoc_author_scope` is present, use the old field.
**Warning signs:** doc-author running .mli enrichment on a project that selected "mld-only" scope.

### Pitfall 4: Dynamic follow-on questions in odoc Q&A

**What goes wrong:** The odoc `.qa.md` has follow-on sub-topic questions (after Q3: Guides) that are dynamically generated from project scanning. These produce headers like `"{guide_type} topics"`. The keys for these would be `getting_started_/_tutorial_topics`, `how-to_guides_topics`, etc. -- awkward but functional.
**Why it happens:** The dynamic nature of follow-on questions means the exact headers are not known until runtime.
**How to avoid:** Accept that follow-on question keys will be dynamically generated from their headers at runtime, just like static questions. The key derivation algorithm (lowercase, spaces to underscores) handles them uniformly. Document this in the SKILL.md instructions so the implementing agent understands these are expected to be variable.
**Warning signs:** Missing qa_answers entries for sub-topic questions.

### Pitfall 5: Step 3 ordering -- config.yaml must be written AFTER reading plugin.json

**What goes wrong:** Step 3 currently writes config.yaml as a single operation. Now it needs to read `plugin.json` first to get the version. If the implementing agent structures Step 3 as "generate config then write" without the read-first step, `plugin_version` will be empty.
**Why it happens:** The instruction to "populate template with Q&A answers" may be interpreted as only Q&A-derived values, missing the plugin.json read.
**How to avoid:** The SKILL.md instruction must explicitly state: "Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and extract the `version` field. Write this value as `plugin_version` in config.yaml."
**Warning signs:** `plugin_version: ""` in the generated config.yaml.

## Code Examples

### Example: qa_answers key derivation

```
Header: "Navigation"      -> Key: "navigation"
Header: "API docs"        -> Key: "api_docs"
Header: "Rich features"   -> Key: "rich_features"
Header: "TOC"             -> Key: "toc"
Header: "Guides"          -> Key: "guides"
Header: "Getting started / Tutorial topics" -> Key: "getting_started_/_tutorial_topics"
```

Rule: lowercase the header, replace spaces with underscores. No other normalization.

### Example: Updated Step 3 instruction text (additions in bold context)

The following additions go into Step 3 of SKILL.md:

After item 2 (Write config.yaml), add to the instruction:
> Before writing config.yaml, read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and extract the `version` field. Include this as `plugin_version: "{version}"` in config.yaml, placed immediately after `version: 1`.

After item 4 (Copy rules file), add new items:
> 5. **Create `.doc-writer/.originals/` directory** if it does not exist.
> 6. **Copy pristine originals:**
>    - Copy the guidance file source to `.doc-writer/.originals/{doc_system}.md` (use the same source as item 3 -- from `defaults/` for built-in frameworks, from `.doc-writer/` for FALLBACK frameworks)
>    - Copy `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/rules.md` to `.doc-writer/.originals/rules.md`

### Example: Updated Step 2b.5 instruction text

Replace item 4 of Step 2b.5:

Current:
> 4. **Record all answers.** Framework Q&A answers do NOT go into config.yaml. Store them in-memory and pass them to the researcher via the Agent tool invocation message in Step 5.
>
>    **Exception:** If `doc_system` is `odoc`, persist the Question 2 answer (author scope) to `config.yaml` as `odoc_author_scope`.

New:
> 4. **Record all answers.** After all framework questions are answered, persist the answers to `config.yaml` under a `qa_answers` section. For each question answered, derive the key by lowercasing the question's `header` field and replacing spaces with underscores (e.g., "Navigation" becomes `navigation`, "API docs" becomes `api_docs`). Store the selected label as the value (string for single-select, array of strings for multi-select). For "Type something else" responses, store the user's freeform text.
>
>    Also pass all answers in-memory to the researcher via the Agent tool invocation message in Step 5 (unchanged from current behavior).

### Example: Updated doc-author.md scope control

Current (line 372):
> **Scope control:** Read `odoc_author_scope` from `.doc-writer/config.yaml`. If the value is `"mld-only"`, skip this entire section. If the value is `"mld-and-mli"` (or absent/empty, which defaults to running enrichment), proceed with the enrichment workflow below.

New:
> **Scope control:** Read `qa_answers.scope` from `.doc-writer/config.yaml`. If the value is `".mld pages only"`, skip this entire section. If the value contains ".mld pages + .mli" or is absent/empty (which defaults to running enrichment), proceed with the enrichment workflow below. **Backward compatibility:** If `qa_answers` does not exist or has no `scope` key, check the legacy `odoc_author_scope` field. If it is `"mld-only"`, skip. Otherwise proceed.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual validation via `/doc-writer:setup` execution |
| Config file | None -- this is an LLM-driven skill, not a code test suite |
| Quick run command | Run `/doc-writer:setup` on a test project, inspect output files |
| Full suite command | Run setup for each framework (mkdocs-material, sphinx-shibuya, odoc, plain-markdown), inspect all artifacts |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SETUP-01 | `plugin_version` in config.yaml matches plugin.json version | manual inspection | `grep plugin_version .doc-writer/config.yaml` | N/A |
| SETUP-02 | `.originals/` directory has pristine guidance + rules | manual inspection | `diff .doc-writer/.originals/rules.md doc-writer/skills/setup/defaults/rules.md` | N/A |
| SETUP-03 | `qa_answers` section with header-derived keys | manual inspection | `grep -A 10 qa_answers .doc-writer/config.yaml` | N/A |
| SETUP-04 | `--reset` refreshes `.originals/` | manual inspection | Run `--reset`, then `diff .doc-writer/.originals/rules.md doc-writer/skills/setup/defaults/rules.md` | N/A |

### Sampling Rate

- **Per task commit:** Review modified SKILL.md, config-template.yaml, and doc-author.md for correctness
- **Per wave merge:** Run `/doc-writer:setup` on a test project and verify all 4 success criteria
- **Phase gate:** All 4 success criteria verified before `/gsd:verify-work`

### Wave 0 Gaps

None -- this phase modifies instruction files (markdown), not executable code. Validation is via manual setup runs and file inspection. No test framework to install.

## Open Questions

1. **Dynamic follow-on question key format for odoc**
   - What we know: odoc Q3 has follow-on sub-topic questions with headers like `"{guide_type} topics"`. These headers are dynamically generated at runtime.
   - What's unclear: Whether the resulting keys like `getting_started_/_tutorial_topics` are acceptable or too unwieldy.
   - Recommendation: Accept the dynamic keys as-is. The upgrade flow (Phase 21) will match on these keys for gap detection. They are ugly but unambiguous and derived from a consistent rule.

2. **Should `.originals/` be added to `.gitignore`?**
   - What we know: `.originals/` contains exact copies of plugin default files. They are not user-authored content.
   - What's unclear: Whether users want these tracked in git (for auditability) or ignored (to reduce noise).
   - Recommendation: Do NOT add to `.gitignore` by default. Users who want to ignore them can add the pattern themselves. Tracking them in git provides an audit trail of what plugin version's defaults were active, which is valuable for debugging merge issues.

## Sources

### Primary (HIGH confidence)

- `doc-writer/skills/setup/SKILL.md` (583 lines, direct reading) -- complete setup flow, all modification points identified
- `doc-writer/skills/setup/defaults/config-template.yaml` (direct reading) -- current config schema, 35 lines
- `doc-writer/.claude-plugin/plugin.json` (direct reading) -- version source, currently `1.4.0`
- `doc-writer/skills/setup/defaults/*.qa.md` (4 files, direct reading) -- all `header` fields catalogued for key derivation
- `doc-writer/agents/doc-author.md` (line 372, direct reading) -- `odoc_author_scope` usage confirmed
- `.planning/research/ARCHITECTURE.md` (direct reading) -- detailed design for plugin_version, .originals/, qa_answers, upgrade skill structure

### Secondary (MEDIUM confidence)

- `.planning/research/SUMMARY.md` (direct reading) -- phase ordering rationale, build dependencies
- `.planning/research/PITFALLS.md` (direct reading) -- pitfall patterns relevant to setup modifications

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all changes are to existing files using existing patterns; no new tools or libraries
- Architecture: HIGH - detailed design already documented in ARCHITECTURE.md; modifications are surgical and well-specified
- Pitfalls: HIGH - all pitfalls identified from direct codebase analysis; the FALLBACK path and odoc_author_scope migration are the only non-trivial edge cases

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stable -- no external dependencies that could change)
