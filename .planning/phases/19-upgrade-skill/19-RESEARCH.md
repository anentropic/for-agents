# Phase 19: Upgrade Skill - Research

**Researched:** 2026-03-26
**Domain:** Claude Code plugin skill authoring -- upgrade command for doc-writer
**Confidence:** HIGH

## Summary

Phase 19 creates a new `/doc-writer:upgrade` command as a separate SKILL.md file. The command detects version mismatches between the installed plugin and the user's config, migrates new config fields with semantically inferred values, silently updates unmodified guidance/rules files, removes deprecated config fields, and reports all changes in a summary. The scope is limited to Steps 1 (Version Detection), 2 (Config Migration), and 6 (Finalize/Summary) of the full upgrade flow, plus a subset of Step 3 (unchanged-file detection only -- no 3-way merge). Steps 3 (full merge), 4 (Q&A gap detection), and 5 (researcher re-run) are deferred to Phases 20-21.

This phase is entirely about authoring a markdown SKILL.md file that instructs Claude how to perform the upgrade flow. There are no external libraries, no compiled code, no test frameworks. The "stack" is the skill file format itself, YAML config manipulation, and JSON reading -- all performed by Claude as the runtime. The primary risk is getting the instructions wrong such that Claude misinterprets the upgrade flow, especially around config field inference and the unchanged-file detection logic.

**Primary recommendation:** Create `doc-writer/skills/upgrade/SKILL.md` following the exact same frontmatter and prose instruction patterns as `setup/SKILL.md`, implementing a linear 4-step flow (version check, config migration, unchanged-file update, finalize). Also bump `plugin.json` version to `1.5.0`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** New file `doc-writer/skills/upgrade/SKILL.md` -- separate skill, not an extension of setup SKILL.md
- **D-02:** Bump `plugin.json` version from `1.4.0` to `1.5.0` as part of this phase
- **D-03:** Phase 19 delivers a minimal complete command covering Steps 1, 2, and 6 of the full upgrade flow. No placeholder/stub steps for Phase 20/21 work
- **D-04:** Infer new config field values silently when confident (single obvious source field, unambiguous mapping). Write the inference and note it in the summary
- **D-05:** Pause and ask the user via `AskUserQuestion` whenever any ambiguity exists
- **D-06:** When asking about an ambiguous field, use `AskUserQuestion` with the field's valid values as options
- **D-07:** After all migration changes, display a consolidated summary of every field added (with inferred value noted) and every field removed
- **D-08:** Phase 19's UPGRADE-04 scope is limited to config fields only (not guidance file sections)
- **D-09:** Auto-remove deprecated config fields without prompting. List removed fields in the upgrade summary
- **D-10:** For each file in `.originals/` -- compare user's `.doc-writer/{file}` to `.originals/{file}`. If identical, silently overwrite with new plugin defaults. Note in summary
- **D-11:** If user's file differs from `.originals/` (customized), skip it. Inform user in summary: "Customized files skipped -- merge coming in a future upgrade."

### Claude's Discretion
- Exact wording and formatting of the upgrade summary output
- How to structure the "already up to date" message (UPGRADE-01 fast path)
- How to handle edge case: `.originals/` is absent (pre-v1.5.0 project with no Phase 18 setup) -- acceptable to warn and skip file-update steps

### Deferred Ideas (OUT OF SCOPE)
- Phase 19/20/21 stub steps in SKILL.md -- not needed
- Guidance file section deprecation warnings -- belongs in Phase 20's merge logic
- `--dry-run` flag -- not scoped to Phase 19
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| UPGRADE-01 | User runs `/doc-writer:upgrade` and receives "already up to date" when config plugin_version matches plugin.json version | Step 1 (Version Detection) -- compare two version strings, fast-path exit with clear message |
| UPGRADE-02 | User runs `/doc-writer:upgrade` and has new config fields added with semantically inferred values (not blank defaults) | Step 2 (Config Migration) -- diff config.yaml against config-template.yaml, infer values from existing config context, ask via AskUserQuestion when ambiguous |
| UPGRADE-03 | User runs `/doc-writer:upgrade` and has files identical to `.originals/` silently updated to new plugin version without prompts | Step 3 subset (Unchanged File Update) -- compare user file to `.originals/` counterpart, if identical overwrite with new plugin defaults from `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/` |
| UPGRADE-04 | User runs `/doc-writer:upgrade` and receives deprecation warnings for config fields present in user's config but absent from new config-template.yaml (Phase 19 scope: config fields only) | Step 2 (Config Migration) -- detect fields in config.yaml absent from config-template.yaml, auto-remove, list in summary |
</phase_requirements>

## Standard Stack

This phase creates markdown instruction files for a Claude Code plugin. There are no npm packages, no compiled code, no external dependencies. The "stack" is:

### Core
| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| SKILL.md (YAML frontmatter + markdown) | Claude Code plugin format | Skill definition and instructions | Only format Claude Code supports for skills |
| plugin.json | JSON, semver versioning | Plugin metadata and version source | Claude Code plugin standard |
| config.yaml | YAML | User project configuration | Established in Phase 18 and all prior phases |
| config-template.yaml | YAML | Canonical schema for config fields | Established in setup skill as migration reference |

### Supporting
| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| AskUserQuestion | Claude Code built-in tool | Structured user prompts with options | When config field inference is ambiguous (D-05, D-06) |
| `${CLAUDE_PLUGIN_ROOT}` | Claude Code variable | Plugin-relative file paths | All references to plugin-side files |

### Alternatives Considered
Not applicable -- the technology choices are fully constrained by the Claude Code plugin system.

## Architecture Patterns

### Recommended Project Structure
```
doc-writer/
  skills/
    upgrade/
      SKILL.md           # NEW: upgrade workflow (this phase)
    setup/
      SKILL.md           # EXISTING: setup workflow (reference pattern)
      defaults/
        config-template.yaml  # EXISTING: canonical config schema
        rules.md              # EXISTING: default rules
        {framework}.md        # EXISTING: guidance files
  .claude-plugin/
    plugin.json           # MODIFIED: version bump 1.4.0 -> 1.5.0
```

### Pattern 1: SKILL.md Frontmatter Convention
**What:** Every skill uses identical YAML frontmatter format with `disable-model-invocation: true` and explicit `allowed-tools`
**When to use:** Always -- this is how Claude Code plugin skills work
**Example:**
```yaml
---
name: doc-writer:upgrade
description: Upgrade doc-writer configuration after a plugin update. Detects version changes, migrates config fields, updates unchanged files, and reports all changes.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: ""
---
```
Note: No `Agent` tool needed in Phase 19 -- no researcher re-run or sub-agent spawning. No `argument-hint` needed -- no flags in Phase 19 scope.

### Pattern 2: AskUserQuestion for Structured Choices
**What:** When the upgrade skill needs user input for ambiguous config field values, it uses AskUserQuestion with labeled options (same pattern as setup skill)
**When to use:** Only when config field inference is genuinely ambiguous (D-05)
**Example:** From setup SKILL.md, the established pattern is:
```
Use AskUserQuestion:
- header: "{Section Name}"
- question: "{Clear question text}"
- options:
  - { label: "{Option 1}", description: "{What this option means}" }
  - { label: "{Option 2}", description: "{What this option means}" }
  - { label: "Type something else", description: "{Freeform alternative}" }
  - { label: "Chat about this", description: "{Discussion option}" }
```

### Pattern 3: User Interaction Pattern Block
**What:** The setup SKILL.md includes a "User Interaction Pattern" section explaining how to handle "Type something else" and "Chat about this" selections
**When to use:** The upgrade SKILL.md should include the same block for consistency, since it uses AskUserQuestion for ambiguous field inference
**Example:** See setup SKILL.md lines 13-19 for the canonical text

### Pattern 4: Linear Step Flow
**What:** Instructions are organized as numbered steps with clear preconditions and exit points
**When to use:** Always for skill workflows
**Structure for Phase 19:**
```
Step 1: Version Detection (fast-path exit if up to date)
Step 2: Config Format Migration (add new fields, remove deprecated)
Step 3: Unchanged File Update (compare .originals/, overwrite if identical)
Step 4: Finalize (update plugin_version, display summary)
```

### Pattern 5: File Comparison Using Read
**What:** Claude reads file contents and compares them (content equality check for .originals/ vs user files)
**When to use:** Step 3 unchanged-file detection
**How it works:** Claude reads both files and determines if their content is identical. This is reliable for the files in scope (guidance .md and rules.md -- typically 1-15KB each).

### Anti-Patterns to Avoid
- **Stub steps for future phases:** D-03 explicitly forbids placeholder steps for Phase 20/21 work. The skill should end cleanly after its implemented scope.
- **Blank/empty defaults for new config fields:** UPGRADE-02 requires "semantically inferred" values. Writing `user_tasks: []` when the user clearly has tasks described in `domain_context` is wrong -- infer from existing config data.
- **Asking when inference is clear:** D-04 says infer silently when confident. Only ask via AskUserQuestion when genuinely ambiguous.
- **Prompting before removing deprecated fields:** D-09 says auto-remove and list in summary. Do not ask "shall I remove this?"
- **Including Agent in allowed-tools:** Phase 19 does not spawn sub-agents. Including unused tools is misleading.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version comparison | Custom semver parser in bash | Claude string comparison | Plugin versions are simple semver strings; Claude can compare "1.4.0" < "1.5.0" directly |
| Config field diffing | Bash diff of YAML files | Claude reads both files and compares field-by-field | Claude is already reading the YAML; field-level comparison is more reliable than line-level diff for structured data (per REQUIREMENTS.md: "YAML 3-way merge via diff3 is out of scope") |
| File identity check | `diff` or `sha256sum` in bash | Claude reads both files and checks content equality | The files are small (<15KB); Claude reading both is simpler and avoids bash tool dependency for what is a straightforward comparison |

**Key insight:** This is a SKILL.md (instructions for Claude), not executable code. Claude IS the runtime. The instructions tell Claude what to read, compare, and write -- there are no external tools to orchestrate.

## Common Pitfalls

### Pitfall 1: Confusing "config schema version" with "plugin version"
**What goes wrong:** The skill conflates `version: 1` (config schema version) with `plugin_version: "1.5.0"` (plugin release version)
**Why it happens:** Both are version-related fields at the top of config.yaml
**How to avoid:** SKILL.md must explicitly name `plugin_version` in all version-detection instructions, never just "version"
**Warning signs:** Instructions that say "read the version from config.yaml" without specifying which version field

### Pitfall 2: Inferring config values from the template instead of existing config
**What goes wrong:** New fields get template placeholder values (empty strings, empty arrays) instead of semantically inferred values
**Why it happens:** The SKILL.md tells Claude to "add fields from config-template.yaml" without emphasizing that values must be inferred from the user's existing configuration context
**How to avoid:** SKILL.md must explicitly instruct: "For each new field, examine the user's existing config values to infer an appropriate value. Never copy placeholder values from the template."
**Warning signs:** Instructions that say "copy the field from config-template.yaml" without a separate inference step

### Pitfall 3: Missing the pre-1.5.0 edge case
**What goes wrong:** The skill crashes or produces confusing output when `plugin_version` is absent from config.yaml
**Why it happens:** The skill assumes plugin_version always exists
**How to avoid:** Step 1 must handle missing plugin_version: "If plugin_version is absent, treat as pre-1.5.0 (version unknown). Proceed with full upgrade from unknown to current."
**Warning signs:** No conditional check for missing plugin_version in Step 1

### Pitfall 4: Missing the .originals/ absent edge case
**What goes wrong:** The skill tries to compare files to .originals/ when the directory does not exist (pre-1.5.0 project)
**Why it happens:** D-10 describes comparing .originals/ files but does not apply to projects that never ran the Phase 18 setup
**How to avoid:** Claude's Discretion note says "acceptable to warn and skip file-update steps" if .originals/ is absent. The SKILL.md should check for .originals/ before Step 3 and skip with a message if absent.
**Warning signs:** No existence check for .originals/ directory

### Pitfall 5: Forgetting to update .originals/ after silent overwrite
**What goes wrong:** After overwriting an unchanged user file with new plugin defaults, the .originals/ copy is not updated to match. Future upgrades would then see a diff between .originals/ (old default) and user's file (new default) and incorrectly treat the file as "customized."
**How to avoid:** When Step 3 overwrites an unchanged file, it must ALSO update .originals/{file} with the same new content
**Warning signs:** Instructions that say "overwrite .doc-writer/{file}" without also saying "update .originals/{file}"

### Pitfall 6: Writing plugin_version before migration completes
**What goes wrong:** If the skill writes the new plugin_version to config.yaml at the beginning and then fails mid-migration, subsequent upgrade runs will think the upgrade already completed ("already up to date")
**How to avoid:** plugin_version must be updated LAST, in the finalize step, after all migration and file updates are complete
**Warning signs:** plugin_version written in Step 1 or Step 2 instead of the final step

### Pitfall 7: Not handling the "no changes needed" upgrade case
**What goes wrong:** Plugin version bumped but no actual field changes between config-template versions -- the skill produces a confusing or empty migration
**Why it happens:** Version bump does not necessarily mean config schema changed
**How to avoid:** Step 2 should detect "no new fields, no deprecated fields" and skip migration gracefully. Step 4 summary should still report the version bump.

### Pitfall 8: config-template.yaml meta-fields treated as user config fields
**What goes wrong:** Fields like `version: 1`, `plugin_version: ""`, and `detected:` are compared as "user-configurable fields" and trigger false migration warnings
**Why it happens:** The config-template.yaml contains both meta-fields (managed by setup/upgrade) and user-configured fields
**How to avoid:** The SKILL.md must explicitly list fields to EXCLUDE from migration comparison: `version`, `plugin_version`, `detected`, and `qa_answers` (these are managed programmatically, not user-configured)

## Code Examples

### Example 1: SKILL.md Frontmatter (from existing skills)
```yaml
# Source: doc-writer/skills/review/SKILL.md
---
name: doc-writer:review
description: Audit documentation quality and coverage...
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--edit]"
---
```

### Example 2: AskUserQuestion Pattern (from setup SKILL.md)
```markdown
# Source: doc-writer/skills/setup/SKILL.md lines 255-265
Use AskUserQuestion:
- header: "Persona"
- question: "Does this capture your user persona?"
- options:
  - { label: "Looks good", description: "Save this persona and continue" }
  - { label: "Edit", description: "Change specific fields" }
  - { label: "Chat about this", description: "Discuss what these fields mean" }
```

### Example 3: Plugin Version Read Path (from setup SKILL.md)
```markdown
# Source: doc-writer/skills/setup/SKILL.md line 469
Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and extract the `version` field.
```

### Example 4: Config Template Field Structure
```yaml
# Source: doc-writer/skills/setup/defaults/config-template.yaml
version: 1
plugin_version: ""

user_personas:
  - name: ""
    skill_level: ""
    assumed_knowledge: []
    never_assume: []
    domain_context: ""
    discovery_story: ""
    user_tasks: []

tone: ""

use_cases:
  - title: ""
    problem: ""
    capability: ""
    outcome: ""

use_cases_section: false

doc_system: ""
api_reference: ""

paths:
  docs_root: "docs/"
  source_root: "src/"

detected:
  language: ""
  doc_system: ""
  existing_docs: false

qa_answers: {}
```

### Example 5: .originals/ File Paths (from ARCHITECTURE.md)
```
.doc-writer/.originals/rules.md         -> compare against .doc-writer/rules.md
.doc-writer/.originals/{doc_system}.md   -> compare against .doc-writer/{doc_system}.md
```

New plugin defaults (THEIRS) come from:
```
${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/rules.md
${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.md
```

## Upgrade Flow Design (Phase 19 Scope)

The following is the complete flow that the SKILL.md must implement, derived from ARCHITECTURE.md and CONTEXT.md decisions:

### Step 1: Version Detection
1. Read `.doc-writer/config.yaml`. If it does not exist, inform user: "No doc-writer configuration found. Run `/doc-writer:setup` first." Stop.
2. Extract `plugin_version` from config.yaml. If absent, treat as `"unknown"` (pre-1.5.0 project).
3. Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Extract `version`.
4. If `plugin_version` equals `version`: display "already up to date" message with current version. Stop.
5. Display: "Upgrading from {old_version} to {new_version}..."

### Step 2: Config Format Migration
1. Read `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/config-template.yaml` as the canonical schema.
2. Compare user's config.yaml fields against the template fields.
3. **Exclude from comparison:** `version`, `plugin_version`, `detected`, `qa_answers` (meta-fields managed by setup/upgrade, not user fields).
4. **New fields** (in template, absent from config): For each new field, examine the user's existing config context to infer a value. If inference is clear and unambiguous, write the field silently and note it for the summary. If ambiguous, use AskUserQuestion with the field's valid values as options (D-05, D-06).
5. **Deprecated fields** (in config, absent from template): Auto-remove without prompting (D-09). Record removed fields for summary.
6. Write updated config.yaml with new fields added and deprecated fields removed.

### Step 3: Unchanged File Update
1. Check if `.doc-writer/.originals/` directory exists.
   - If absent: warn user ("This project was set up before upgrade support was available. File comparison skipped. Run `/doc-writer:setup --reset` to establish baseline files."). Skip to Step 4.
2. For each file in `.originals/` (typically `rules.md` and `{doc_system}.md`):
   a. Read `.doc-writer/.originals/{file}` (BASE)
   b. Read `.doc-writer/{file}` (USER)
   c. Read `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{file}` (NEW)
   d. If BASE == NEW: no upstream changes to this file. Skip.
   e. If USER == BASE: user did not customize. Silently overwrite `.doc-writer/{file}` with NEW content. Also update `.originals/{file}` with NEW content. Record for summary.
   f. If USER != BASE: user customized this file. Skip. Record for summary: "Customized files skipped -- merge coming in a future upgrade."

### Step 4: Finalize
1. Write new `plugin_version` to config.yaml (the current plugin.json version).
2. Display consolidated upgrade summary:
   - Version: {old} -> {new}
   - Config fields added (with inferred values noted)
   - Config fields removed (deprecated)
   - Files updated (unchanged files overwritten)
   - Files skipped (customized files deferred)
   - Any warnings (missing .originals/, etc.)

## Config Field Migration: Inference Strategy

When a new field appears in config-template.yaml that is absent from the user's config.yaml, the upgrade skill must infer its value from the existing config context. The SKILL.md needs to instruct Claude on this clearly.

**Inference rules by field type:**

| New Field | Inference Source | Example |
|-----------|-----------------|---------|
| String field with semantic meaning | Other config fields with related semantics | `domain_context` can be inferred from `user_personas[].name` + `assumed_knowledge` |
| Array field | Related array fields or decomposition of existing string fields | `user_tasks` could be inferred from `domain_context` if it describes what users do |
| Boolean field | Most conservative default, or infer from existing config state | `use_cases_section: false` if `use_cases` is empty |
| Nested object | Decomposition of existing flat fields, or reasonable defaults | `paths.docs_root` from any existing path configuration |

**The SKILL.md must instruct:** "Read the user's existing config values holistically. Use domain knowledge to infer what the new field should be for THIS specific project. The inference should feel natural -- as if the user had been asked the question during setup and answered based on their existing configuration."

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No version tracking | plugin_version in config.yaml | Phase 18 (v1.5.0) | Enables upgrade detection |
| No originals storage | .originals/ directory | Phase 18 (v1.5.0) | Enables file comparison and future 3-way merge |
| No qa_answers persistence | qa_answers in config.yaml | Phase 18 (v1.5.0) | Enables Q&A gap detection in Phase 21 |

## Open Questions

1. **Edge case: doc_system is a FALLBACK framework**
   - What we know: FALLBACK frameworks store guidance in `.doc-writer/{name}.md` (project-local), not in plugin defaults. `.originals/` stores the researcher-generated file.
   - What's unclear: In Step 3, the "NEW" file for comparison should come from `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.md` -- but for FALLBACK frameworks, this file does not exist in the plugin defaults directory. The user's file IS the generated one.
   - Recommendation: In Step 3, before reading the NEW file from plugin defaults, check if it exists. If it does not (FALLBACK framework), skip file comparison for that file and note in summary. This is an edge case that Phase 20's merge logic will handle more completely.

2. **What counts as "meta-fields" to exclude from migration comparison?**
   - What we know: `version`, `plugin_version`, `detected`, `qa_answers` are programmatically managed
   - What's unclear: Whether future template changes might add new meta-fields
   - Recommendation: Explicitly list the exclusions in the SKILL.md. If new meta-fields are added later, the SKILL.md can be updated.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None -- no test framework in project |
| Config file | none |
| Quick run command | N/A |
| Full suite command | N/A |

Note: The project has bats test suites from earlier phases (`tests/` directory) but they test earlier-phase functionality. Phase 19 delivers a markdown SKILL.md file -- its "test" is running `/doc-writer:upgrade` manually in a project and observing behavior.

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UPGRADE-01 | "Already up to date" when versions match | manual-only | Run `/doc-writer:upgrade` on a project where config plugin_version matches plugin.json | N/A |
| UPGRADE-02 | New config fields added with inferred values | manual-only | Run `/doc-writer:upgrade` after adding a field to config-template.yaml | N/A |
| UPGRADE-03 | Unchanged files silently updated | manual-only | Run `/doc-writer:upgrade` on a project with unmodified guidance/rules files after updating plugin defaults | N/A |
| UPGRADE-04 | Deprecation warnings for removed config fields | manual-only | Run `/doc-writer:upgrade` after removing a field from config-template.yaml | N/A |

**Justification for manual-only:** The deliverable is a markdown instruction file that runs inside Claude Code's agent system. There is no CLI entry point, no function to call, no testable API. The "test" is Claude interpreting the SKILL.md and performing the upgrade flow correctly. This is validated by running the command in a real project.

### Sampling Rate
- **Per task commit:** Visual review of SKILL.md changes
- **Per wave merge:** N/A
- **Phase gate:** Manual run of `/doc-writer:upgrade` against a test project by the user

### Wave 0 Gaps
None -- no test infrastructure needed. The deliverable is a markdown file whose correctness is verified through content review and manual testing.

## Sources

### Primary (HIGH confidence)
- `doc-writer/skills/setup/SKILL.md` -- 591 lines, canonical skill structure and AskUserQuestion patterns
- `doc-writer/skills/setup/defaults/config-template.yaml` -- canonical config schema (38 lines)
- `doc-writer/.claude-plugin/plugin.json` -- current version source (1.4.0)
- `.planning/research/ARCHITECTURE.md` -- settled decisions for upgrade skill structure, version tracking, .originals/, qa_answers
- `.planning/phases/19-upgrade-skill/19-CONTEXT.md` -- 11 locked decisions (D-01 through D-11), discretion areas, deferred items
- `.planning/phases/18-setup-foundation/18-VERIFICATION.md` -- confirms Phase 18 outputs (plugin_version, .originals/, qa_answers) are verified and in place
- `.planning/REQUIREMENTS.md` -- UPGRADE-01 through UPGRADE-04 acceptance criteria

### Secondary (MEDIUM confidence)
None needed -- all findings derived from reading the existing codebase.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- fully constrained by Claude Code plugin format, no choices to make
- Architecture: HIGH -- settled in ARCHITECTURE.md and CONTEXT.md decisions, skill patterns established by existing skills
- Pitfalls: HIGH -- derived from reading the actual code and reasoning about edge cases in the upgrade flow

**Research date:** 2026-03-26
**Valid until:** Indefinite -- this is internal project architecture, not external library versions
