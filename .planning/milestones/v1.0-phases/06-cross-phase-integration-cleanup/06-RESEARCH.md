# Phase 6: Cross-Phase Integration Cleanup - Research

**Researched:** 2026-03-04
**Domain:** Markdown agent prompt files -- cross-file consistency and wiring fixes
**Confidence:** HIGH

## Summary

This phase addresses seven integration gaps (INT-01 through INT-07) identified in the v1.0 milestone audit. All gaps are in markdown prompt files (skill SKILL.md files, agent .md files, and the config-template.yaml). There are no code changes, no library installations, and no architectural decisions. Every fix is a targeted text edit to an existing file.

The gaps fall into three categories: (1) stale content that diverged after the Diataxis integration commit (INT-01), (2) missing wiring where one phase added a feature that an earlier phase's file does not reference (INT-02, INT-04, INT-06, INT-07), and (3) naming/variable inconsistencies between files that should use identical conventions (INT-03, INT-05).

**Primary recommendation:** Organize the work into a single plan with seven tasks, one per INT gap. Each task is a surgical edit to 1-3 files. No task depends on another, so execution order does not matter.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SETUP-01 | Setup Q&A persists config | INT-02 fix extends the Q&A to collect domain_context and discovery_story |
| EDIT-04 | Structured feedback with severity levels | INT-01 fix ensures delegation messages name all four Editor passes |
| INTG-01 | /doc:write full pipeline | INT-01 (delegation text), INT-04 (read editor-report.md for summary) |
| INTG-02 | /doc:review audit | INT-01 (delegation text), INT-05 (variable naming) |
| INTG-03 | /doc:edit targeted fixes | INT-01 (delegation text) |
| PERS-01 | Auto-generated scenarios | INT-02 (richer scenario generation from domain_context/discovery_story) |
| PERS-02 | Goal-oriented doc testing | INT-03 (consistent report filenames for reliable reading) |
</phase_requirements>

## Standard Stack

Not applicable. This project has no runtime dependencies, no package.json, and no executable code. All artifacts are markdown prompt files and YAML templates consumed by Claude Code. The "stack" is:

| File Type | Location | Purpose |
|-----------|----------|---------|
| Skill SKILL.md | `skills/{name}/SKILL.md` | Orchestrator instructions for Claude Code |
| Agent .md | `agents/{name}.md` | System prompts for spawned subagents |
| Config template | `skills/setup/defaults/config-template.yaml` | Template populated during `/doc-writer:setup` |

No libraries, no installation, no build step.

## Architecture Patterns

### File Inventory Affected by This Phase

Seven files require edits:

```
skills/
  write/SKILL.md        # INT-01 (lines 102, 108), INT-03 (line 124), INT-04 (new step before line 220)
  review/SKILL.md       # INT-01 (line 74), INT-03 (line 86), INT-05 (lines 74, 86)
  edit/SKILL.md          # INT-01 (line 118)
  setup/SKILL.md         # INT-02 (new questions in Step 2a, around line 72)
  setup/defaults/config-template.yaml  # INT-07 (add api_reference field)
agents/
  doc-editor.md          # INT-06 (add guidance file read in Step 1, after line 41)
```

### Pattern: Delegation Message Format

All three orchestrator skills (write, review, edit) delegate to subagents using a quoted blockquote message passed to the Agent tool. The canonical format is:

```markdown
> {instruction}. Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking. {additional context}.
```

The key principle: delegation messages must name ALL passes so the Editor executes each one. The Diataxis Type Integrity pass was added in commit b126e44 but the delegation messages were not updated.

### Pattern: Config Variable References

The project uses two variable reference conventions in skill files:
- **Full path:** `{paths.docs_root}` -- references the config YAML path explicitly
- **Short form:** `{docs_root}` -- assumes the value has been extracted

The correct convention (used consistently in write/SKILL.md and in the Pre-Flight extraction sections) is `{paths.docs_root}`. Short-form `{docs_root}` appears only in delegation messages within review/SKILL.md lines 74 and 86.

### Pattern: Audience Slug Convention

Persona report filenames for multi-audience execution should use a consistent slug transformation. The review skill (line 88) defines the canonical rule: "audience name lowercased with spaces replaced by hyphens." This should be applied everywhere that references `{audience-name}` in filenames.

### Anti-Patterns to Avoid

- **Editing agent behavior while fixing orchestrator wiring.** INT-01 through INT-07 are orchestrator/config fixes. Do not modify the agent's core logic (passes, verdict criteria, etc.).
- **Adding new features under the guise of cleanup.** Each INT fix has a specific, bounded scope from the audit. Do not expand scope.
- **Changing the persona agent's report-writing logic.** INT-03 is about making the orchestrator skills use consistent filenames in their instructions; the persona agent itself already uses `{audience-name}` consistently.

## Don't Hand-Roll

Not applicable for this phase. All changes are text edits to existing markdown files. There are no libraries, no algorithms, and no hand-roll-vs-library decisions.

## Common Pitfalls

### Pitfall 1: Inconsistent Slug Transformation Definition

**What goes wrong:** Defining the slug transformation differently in different files (e.g., "lowercase with hyphens" in one place, "kebab-case" in another, or forgetting to specify the transformation).
**Why it happens:** The write skill (line 124) says `{audience-name}` without defining the transformation. The review skill (line 88) explicitly defines it.
**How to avoid:** Use the SAME explanatory sentence everywhere: `Where {audience_name_slug} is the audience name lowercased with spaces replaced by hyphens.` Add this to write/SKILL.md near line 124.
**Warning signs:** Different files using different placeholder names (`{audience-name}` vs `{audience_name_slug}`).

### Pitfall 2: Forgetting Revision Pass Delegation Messages

**What goes wrong:** Fixing the initial delegation message for INT-01 but forgetting the revision pass delegation message in the same file.
**Why it happens:** Write/SKILL.md has TWO delegation messages for the Editor: initial (line 102) and revision (line 108). Both say "three passes."
**How to avoid:** For each file with INT-01, search for ALL occurrences of "three passes" and update every one.
**Warning signs:** Running `grep -n "three passes" skills/*/SKILL.md` still returns results after the fix.

### Pitfall 3: Breaking Config Template YAML Syntax

**What goes wrong:** Adding the `api_reference` field to config-template.yaml with incorrect indentation or missing quotes.
**Why it happens:** YAML is whitespace-sensitive and the template already has specific indentation.
**How to avoid:** The `api_reference` field should be a top-level key (same indentation as `doc_system:` and `paths:`), with an empty string default.
**Warning signs:** A YAML linter would flag syntax errors. Verify indentation matches surrounding keys.

### Pitfall 4: Guidance File Read Step Placed Too Late in Editor

**What goes wrong:** Adding the guidance file read after the Pre-Processing section instead of within it, causing the Editor to start its passes without formatting context.
**Why it happens:** The Editor's Pre-Processing has 4 steps already. The new read needs to be inserted at the right position.
**How to avoid:** Insert the guidance file read as a new sub-step within Step 1 (Read Configuration), immediately after loading `rules.md` (after current line 42). This follows the same pattern as the Author agent (doc-author.md lines 37-38).
**Warning signs:** The guidance file read appearing after Step 4 (Verify Accuracy Claims) means it happens too late.

## Code Examples

### INT-01: Updated Delegation Message (write/SKILL.md)

Current (line 102):
```markdown
> Edit the documentation in {paths.docs_root}. Run all three passes: terminology, humanizer, and cross-references.
```

Fixed:
```markdown
> Edit the documentation in {paths.docs_root}. Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking.
```

### INT-02: New Setup Questions (setup/SKILL.md, after audience definition)

Insert after the "Never assume" question in Step 2a, before the secondary audience prompt:

```markdown
5. **Domain context** (optional): What problem domain does this audience work in? (e.g., "building REST APIs for fintech applications")
6. **Discovery story** (optional): How did this audience discover your library? (e.g., "searching for a Python HTTP client that handles retries")

These optional fields help the User Persona agent generate more realistic testing scenarios.
```

### INT-04: Read Editor Report Before Summary (write/SKILL.md)

Insert before Step 7 (Summary Report), after all persona evaluations and verdict routing complete:

```markdown
### Read Editor Report

Before presenting the summary, read `.doc-writer/editor-report.md` to extract change counts for the summary:
- Parse the "Changes made" section for BLOCKING, SUGGESTION, and NITPICK counts
- If the file does not exist (Editor was skipped or failed), use "N/A" for all counts
```

### INT-06: Editor Reads Guidance File (agents/doc-editor.md)

Insert as new item 3 in Step 1 (Read Configuration), after the current item 2 (rules.md) and before the current item 3 (terminology.yaml):

```markdown
3. **`.doc-writer/{doc_system}.md`** -- Load the doc-system guidance file for the active documentation system. This file contains formatting preferences (heading case, admonition style, code block conventions) that inform your editing decisions. If the file does not exist, proceed without doc-system-specific formatting preferences.
```

Renumber current item 3 (terminology.yaml) to item 4.

### INT-07: Config Template Addition (config-template.yaml)

Add after the `doc_system:` line:

```yaml
api_reference: ""
```

This is a top-level key, same indentation as `doc_system:`.

## State of the Art

Not applicable. This is an internal project cleanup phase with no external technology decisions.

## Open Questions

None. All seven gaps are precisely specified in the v1.0 milestone audit with file paths, line numbers, affected requirements, and prescribed fixes. No ambiguity remains.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual CC session testing (no executable code in this project) |
| Config file | None -- agents are markdown prompts |
| Quick run command | `grep -n "three passes" skills/*/SKILL.md` (should return 0 results after INT-01) |
| Full suite command | Manual: run `/doc-writer:write`, `/doc-writer:review`, `/doc-writer:edit` in a CC session |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INT-01 | Delegation messages say "four passes" | grep-verify | `grep -c "four passes" skills/write/SKILL.md skills/review/SKILL.md skills/edit/SKILL.md` (expect 4, 1, 1) | N/A |
| INT-02 | Setup Q&A asks domain_context + discovery_story | manual | Verify text present in `skills/setup/SKILL.md` Step 2a | N/A |
| INT-03 | Persona filenames use consistent slug | grep-verify | `grep "audience_name_slug" skills/write/SKILL.md` (expect match) | N/A |
| INT-04 | Write skill reads editor-report.md | grep-verify | `grep "editor-report.md" skills/write/SKILL.md` (expect match in summary section) | N/A |
| INT-05 | Review skill uses {paths.docs_root} consistently | grep-verify | `grep "{docs_root}" skills/review/SKILL.md` should return only `{paths.docs_root}` forms | N/A |
| INT-06 | Editor reads guidance file | grep-verify | `grep "doc_system.*md\|guidance" agents/doc-editor.md` (expect match in Step 1) | N/A |
| INT-07 | Config template includes api_reference | grep-verify | `grep "api_reference" skills/setup/defaults/config-template.yaml` (expect match) | N/A |

### Sampling Rate

- **Per task commit:** Run the grep-verify command for the specific INT being fixed
- **Per wave merge:** Run all 7 grep-verify commands
- **Phase gate:** All 7 grep-verify commands pass, then full manual CC session testing

### Wave 0 Gaps

None -- existing file infrastructure covers all phase requirements. No test framework, fixtures, or config files need to be created.

## Detailed Gap Analysis

### INT-01 (MEDIUM): Stale Delegation Messages

**Root cause:** Commit b126e44 added Diataxis Type Integrity as Pass 2 in doc-editor.md but did not update the orchestrator skills that delegate to the Editor.

**Files to edit:**
| File | Line(s) | Current | Target |
|------|---------|---------|--------|
| `skills/write/SKILL.md` | 102 | "Run all three passes: terminology, humanizer, and cross-references." | "Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking." |
| `skills/write/SKILL.md` | 108 | "Run all three passes on the changed pages." | "Run all four passes on the changed pages." |
| `skills/review/SKILL.md` | 74 | "Run all three passes: terminology consistency, humanizer review, cross-reference verification." | "Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking." |
| `skills/edit/SKILL.md` | 118 | "Run all three passes: terminology consistency, humanizer review, and cross-reference verification" | "Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking." |

**Pass name alignment with doc-editor.md (lines 14-18):**
1. Terminology Consistency (unchanged)
2. Diataxis Type Integrity (NEW -- must be named)
3. Humanizer (unchanged)
4. Cross-Reference Linking (unchanged)

### INT-02 (HIGH): Setup Q&A Missing domain_context and discovery_story

**Root cause:** Phase 4 (commit 04-01) added `domain_context` and `discovery_story` to the config template but the setup skill's Q&A flow was not extended.

**Files to edit:**
| File | Location | Change |
|------|----------|--------|
| `skills/setup/SKILL.md` | Step 2a (after line 72, within audience definition questions) | Add two optional questions (domain_context, discovery_story) per audience |

The questions should be clearly marked as optional. The persona agent already handles graceful degradation when these fields are empty (doc-persona.md lines 46-48).

### INT-03 (LOW): Persona Report Filename Inconsistency

**Root cause:** Write skill uses `{audience-name}` without defining slug transformation. Review skill uses `{audience_name_slug}` and defines the transformation. Persona agent uses `{audience-name}` without defining.

**Files to edit:**
| File | Line(s) | Change |
|------|---------|--------|
| `skills/write/SKILL.md` | 124 | Change `{audience-name}` to `{audience_name_slug}` and add slug definition line |
| `agents/doc-persona.md` | 252, 372, 389 | Change `{audience-name}` to `{audience_name_slug}` and add slug definition |

The canonical slug definition (from review/SKILL.md line 88): "the audience name lowercased with spaces replaced by hyphens."

### INT-04 (LOW): Write Skill Missing editor-report.md Read

**Root cause:** The write skill's Step 7 summary template (lines 230-233) references editor change counts but the orchestrator never reads `.doc-writer/editor-report.md` to obtain them.

**Files to edit:**
| File | Location | Change |
|------|----------|--------|
| `skills/write/SKILL.md` | Before Step 7 (before line 220) | Add instruction to read `.doc-writer/editor-report.md` and parse counts |

### INT-05 (LOW): Variable Naming Inconsistency in Review Skill

**Root cause:** Pre-flight section uses `{paths.docs_root}` but delegation messages on lines 74 and 86 use shorthand `{docs_root}`.

**Files to edit:**
| File | Line(s) | Change |
|------|---------|--------|
| `skills/review/SKILL.md` | 74 | Change `{docs_root}` to `{paths.docs_root}` |
| `skills/review/SKILL.md` | 86 | Change `{docs_root}` to `{paths.docs_root}` |

### INT-06 (LOW): Editor Does Not Read Guidance File

**Root cause:** The Editor agent reads `doc_system` from config (line 36) but never loads `.doc-writer/{doc_system}.md`. The Author agent does load it (doc-author.md line 37).

**Files to edit:**
| File | Location | Change |
|------|----------|--------|
| `agents/doc-editor.md` | Step 1, after item 2 (after line 42) | Add guidance file read, following the Author's pattern |

### INT-07 (LOW): api_reference Field Missing from Config Template

**Root cause:** Author (line 85) and Editor (line 308) both check for `api_reference` in config, but the template does not include it.

**Files to edit:**
| File | Location | Change |
|------|----------|--------|
| `skills/setup/defaults/config-template.yaml` | After `doc_system:` line (after line 12) | Add `api_reference: ""` top-level key |

## Sources

### Primary (HIGH confidence)
- `v1.0-MILESTONE-AUDIT.md` -- source of all gap definitions, line references, and severity ratings
- Direct file reads of all 7 affected files -- current state verified against audit claims
- `grep` verification of all line references and pattern occurrences

### Secondary
- None needed -- all findings are from primary project files

### Tertiary
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no stack; all edits are to existing markdown files
- Architecture: HIGH -- all patterns observed directly in the codebase
- Pitfalls: HIGH -- pitfalls derived from actual file structure and known inconsistencies

**Research date:** 2026-03-04
**Valid until:** indefinite (internal project files, not external dependencies)
