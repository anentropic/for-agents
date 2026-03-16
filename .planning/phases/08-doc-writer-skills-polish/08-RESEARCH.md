# Phase 8: doc-writer skills polish - Research

**Researched:** 2026-03-16
**Domain:** Claude Code skill/agent UX patterns (argument-hint frontmatter, AskUserQuestion tool)
**Confidence:** HIGH

## Summary

This phase is purely UX polish on existing, working skills and one agent. There are two distinct workstreams: (1) adding `argument-hint` frontmatter to the one skill that lacks it (review), and verifying the three that already have it match the CONTEXT.md specifications, and (2) converting plain-text list-based user choice points in skills and the doc-author agent to use the AskUserQuestion tool with the project's standard option pattern (includes "Type something else" and "Chat about this" as final options on every question).

No new pipeline logic, no new agents, no new features. The scope is editing existing SKILL.md files and one agent `.md` file to improve the Claude Code UI experience. The key risk is prompt bloat: AskUserQuestion instruction blocks are longer than the plain-text patterns they replace, so concise wording matters.

**Primary recommendation:** Split into two plans -- one for argument-hint (trivial, touches 1 file), one for AskUserQuestion conversions (touches 4 skills + 1 agent, requires careful per-question judgment about which interactions benefit from structured choices).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- All four user-invocable skills get `argument-hint`: write, setup, review, edit
  - `doc-writer:write` -> `[--skip-gap-scan]`
  - `doc-writer:setup` -> `[--reset]`
  - `doc-writer:review` -> `[--edit]`
  - `doc-writer:edit` -> `[issue-numbers-or-description]` (freeform, not a flag)
- Skills to get AskUserQuestion: write, review, edit, setup
- Doc Author agent: page inventory approval step gets AskUserQuestion
- Doc Editor and Doc Persona agents: excluded (do not ask users questions mid-run)
- Every AskUserQuestion must include:
  - One "Type something else" option in the main options group (before the chat option)
  - One "Chat about this" option as the final option
- "Type something else" handling: agent uses judgment based on context
- "Chat about this" handling: agent explains current decision point, opens plain-text dialogue, then resumes structured flow
- Format follows `frontmatter-reference.md`: square brackets per argument, descriptive names

### Claude's Discretion
- Exact wording of "Type something else" and "Chat about this" option descriptions
- Which questions within a skill get multi-choice vs remain plain-text (structured choices benefit from AskUserQuestion, open-ended inputs like "describe the issue you want fixed" do not)
- AskUserQuestion header text (max 12 chars)
- Whether to use multiSelect: true for page inventory approval (likely yes)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

## Standard Stack

### Core
| Library/Tool | Version | Purpose | Why Standard |
|-------------|---------|---------|--------------|
| AskUserQuestion | CC built-in | Structured multi-choice UI for user interaction | Native Claude Code tool; auto-adds "Other" option; supports multiSelect |
| argument-hint | CC frontmatter field | Documents expected arguments for autocomplete | CC frontmatter standard per frontmatter-reference.md |

### Supporting
No additional libraries required. This phase modifies only markdown prompt files.

## Architecture Patterns

### Current File Structure (files to modify)
```
doc-writer/
  skills/
    write/SKILL.md       # argument-hint: ALREADY EXISTS "[--skip-gap-scan]"
    setup/SKILL.md        # argument-hint: ALREADY EXISTS "[--reset]"
    review/SKILL.md       # argument-hint: MISSING (needs "[--edit]")
    edit/SKILL.md         # argument-hint: ALREADY EXISTS "[issue description or page path]"
  agents/
    doc-author.md         # Page inventory approval step needs AskUserQuestion
```

### Pattern 1: argument-hint Frontmatter
**What:** YAML frontmatter field that tells Claude Code UI what arguments a command accepts.
**When to use:** Every user-invocable skill/command.
**Example:**
```yaml
# Source: frontmatter-reference.md
---
name: doc-writer:review
description: Audit existing documentation...
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--edit]"
---
```
**Key rules:**
- Square brackets `[]` around each argument
- Descriptive names (not `arg1`)
- Freeform arguments use descriptive text: `[issue-numbers-or-description]`

### Pattern 2: AskUserQuestion with Standard Option Set
**What:** Replace plain-text numbered lists with AskUserQuestion tool calls, adding two mandatory trailing options.
**When to use:** Any user choice point where there are concrete selectable options (NOT for open-ended input like "describe the issue").

**Standard option template (every question):**
```
AskUserQuestion(
  header: "{max 12 chars}",
  question: "{the decision being made}",
  options: [
    { label: "{choice 1}", description: "{what this means}" },
    { label: "{choice 2}", description: "{what this means}" },
    // ... concrete choices ...
    { label: "Type something else", description: "{context-specific hint}" },
    { label: "Chat about this", description: "Discuss this decision before choosing" }
  ],
  multiSelect: false  // or true for batch selections
)
```

**Important:** AskUserQuestion auto-adds "Other" to every question. The "Type something else" option is DIFFERENT from "Other" -- it's an explicit option in the main list that signals the user wants to provide a custom answer. "Other" is the system-level escape hatch.

### Pattern 3: Freeform Rule (from questioning.md)
**What:** When user selects "Type something else" or "Chat about this" or the system "Other" option, the agent MUST ask follow-up as plain text, NOT via another AskUserQuestion.
**When to use:** After any freeform-indicating selection.
**Example instruction to embed in skills:**
```markdown
If the user selects "Type something else" or "Other": ask your follow-up as plain text.
Wait for their response at the normal prompt. Then resume structured flow.

If the user selects "Chat about this": explain the current decision in detail,
open a plain-text conversation, and after it resolves, re-present the original
question or proceed based on what was discussed.
```

### Pattern 4: multiSelect for Batch Approvals
**What:** Use `multiSelect: true` when the user needs to select/deselect multiple items from a list.
**When to use:** PARTIAL approval list (write skill), issue selection (edit skill), page inventory approval (doc-author agent).

### Anti-Patterns to Avoid
- **AskUserQuestion for open-ended input:** "Describe the issue you want fixed" should remain plain text. AskUserQuestion is for concrete choices.
- **Header > 12 characters:** Hard limit. "Confirm Edits" (13 chars) is too long; use "Edit mode" (9 chars).
- **More than 4 options (before the two mandatory trailing options):** 2-4 concrete options is ideal. With the two trailing options, max total is 6.
- **AskUserQuestion after freeform selection:** Never respond to "Other" / "Type something else" / "Chat about this" with another AskUserQuestion. Use plain text.
- **Removing the mandatory trailing options:** "Type something else" and "Chat about this" appear on EVERY AskUserQuestion call, no exceptions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Multi-choice UI | Plain-text numbered lists with "Enter numbers" | AskUserQuestion with multiSelect: true | Native UI, better UX, type-safe selections |
| Binary confirmation | "Proceed? (yes/no)" text | AskUserQuestion with two options | Consistent UI, adds escape hatches |
| Argument documentation | Comments in prompt body | argument-hint frontmatter | CC autocomplete integration |

## Common Pitfalls

### Pitfall 1: Forgetting that AskUserQuestion Auto-Adds "Other"
**What goes wrong:** Skill author adds "Other" as an explicit option, creating a duplicate.
**Why it happens:** Not reading the AskUserQuestion docs carefully.
**How to avoid:** The two mandatory trailing options are "Type something else" and "Chat about this" -- NOT "Other". "Other" is auto-added by the tool.
**Warning signs:** Three freeform-like options appearing in the UI.

### Pitfall 2: Header Length Violation
**What goes wrong:** Header > 12 characters is rejected by validation.
**Why it happens:** Natural phrasing is often > 12 chars.
**How to avoid:** Plan headers before writing. Examples: "Approve" (7), "Edit mode" (9), "Doc system" (10), "Issues" (6), "Pages" (5), "Confirm" (7).
**Warning signs:** Headers like "Partial Fixes" (13) or "Select Issues" (13).

### Pitfall 3: Prompt Bloat from AskUserQuestion Instructions
**What goes wrong:** Adding AskUserQuestion handling instructions makes SKILL.md files significantly longer, potentially exceeding context windows or making prompts hard to follow.
**Why it happens:** Each AskUserQuestion needs: the call itself, handling for each response type, freeform fallback instructions, "Chat about this" handling.
**How to avoid:** Write concise instructions. Reference a shared pattern rather than re-explaining the full protocol at each call site. State the rule once at the top of the skill, then reference it at each call point.
**Warning signs:** SKILL.md growing by more than 30-40 lines per AskUserQuestion conversion.

### Pitfall 4: Converting Questions That Should Stay Plain-Text
**What goes wrong:** Open-ended inputs get forced into AskUserQuestion options that don't fit.
**Why it happens:** Over-applying the conversion rule.
**How to avoid:** The CONTEXT.md gives Claude's discretion here. Questions like "describe the issue" or audience definition Q&A (name, skill level, assumed knowledge) are inherently freeform and should stay as plain text.
**Warning signs:** Options that are vague or generic like "Something simple", "Something complex".

### Pitfall 5: Losing Existing Behavior When Converting
**What goes wrong:** The conversion changes what happens after the user selects an option, breaking existing pipeline logic.
**Why it happens:** Focus on the UI change without carefully mapping existing response handling.
**How to avoid:** For each conversion, document: (1) what the user currently sees, (2) what they currently can respond, (3) what happens for each response. Then map each to the new AskUserQuestion flow, ensuring all paths are preserved.
**Warning signs:** "all" / "none" / numeric selection behaviors disappearing from the write skill's PARTIAL approval.

## Code Examples

### Example 1: Adding argument-hint to review skill
```yaml
# Current frontmatter (review skill):
---
name: doc-writer:review
description: Audit existing documentation without generating new content...
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
---

# After adding argument-hint:
---
name: doc-writer:review
description: Audit existing documentation without generating new content...
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--edit]"
---
```

### Example 2: Converting PARTIAL approval (write skill, Step 6)
```markdown
# CURRENT (plain text):
Enter numbers to approve (e.g., "1,3"), "all", or "none":

# CONVERTED (AskUserQuestion with multiSelect):
Use AskUserQuestion:
- header: "Approve"
- question: "Select PARTIAL fixes to apply, or choose an action below."
- multiSelect: true
- options: [dynamically generated from PARTIAL verdicts, each as:]
  - { label: "[N] {page} > {section}", description: "{fix description}" }
  - ... (one per PARTIAL issue)
  - { label: "Apply all fixes", description: "Approve every suggestion above" }
  - { label: "Skip all fixes", description: "Proceed without applying any" }
  - { label: "Type something else", description: "Describe additional changes" }
  - { label: "Chat about this", description: "Discuss these issues before deciding" }
```

### Example 3: Converting doc system selection (setup skill, Step 2b)
```markdown
# CURRENT (plain text):
Which documentation system does this project use?
1. mkdocs-material (MkDocs with Material theme)
2. plain-markdown (standard Markdown, no doc framework)
3. custom -- enter a name

# CONVERTED (AskUserQuestion):
Use AskUserQuestion:
- header: "Doc system"
- question: "Which documentation system does this project use? Detected: {detected_system}"
- options:
  - { label: "mkdocs-material", description: "MkDocs with Material theme" }
  - { label: "plain-markdown", description: "Standard Markdown, no doc framework" }
  - { label: "Type something else", description: "Enter a custom doc system name" }
  - { label: "Chat about this", description: "Discuss doc system options" }
```

### Example 4: Converting --edit confirmation (review skill)
```markdown
# CURRENT (plain text):
Proceed? (yes/no)

# CONVERTED (AskUserQuestion):
Use AskUserQuestion:
- header: "Edit mode"
- question: "The Editor will rewrite docs directly. Files: {file list}. Manual edits may be overwritten."
- options:
  - { label: "Apply edits", description: "Let the Editor fix issues in doc files" }
  - { label: "Report only", description: "Skip editing, just show findings" }
  - { label: "Type something else", description: "Specify which files to edit" }
  - { label: "Chat about this", description: "Discuss what the Editor will change" }
```

### Example 5: Converting page inventory approval (doc-author agent)
```markdown
# CURRENT (plain text):
Wait for the user to approve, modify, add, or remove pages before proceeding.

# CONVERTED (AskUserQuestion with multiSelect):
Use AskUserQuestion:
- header: "Pages"
- question: "Confirm the page inventory. Deselect pages to exclude, or choose an action."
- multiSelect: true
- options: [dynamically generated from proposed pages:]
  - { label: "{title} ({type})", description: "{key sections}" }
  - ... (one per proposed page, all pre-selected)
  - { label: "Type something else", description: "Add pages or modify the plan" }
  - { label: "Chat about this", description: "Discuss the page inventory" }
```

## Specific Conversion Points (Full Inventory)

### Write Skill (write/SKILL.md)
| Location | Current Pattern | Convert? | Notes |
|----------|----------------|----------|-------|
| Step 6: PARTIAL approval | "Enter numbers to approve" plain-text list | YES (multiSelect) | Primary conversion target. Must preserve "all"/"none"/numeric/freeform handling |

### Setup Skill (setup/SKILL.md)
| Location | Current Pattern | Convert? | Notes |
|----------|----------------|----------|-------|
| Step 1: --reset confirmation | "Continue? (yes/no)" | YES | Binary choice |
| Step 1: Existing config update menu | "audiences/doc system/paths/rules/guidance/done" | YES | 6 options -- may need to trim descriptions to fit |
| Step 2a: Secondary audience prompt | "Do you have a secondary audience?" | YES | Binary yes/no |
| Step 2b: Doc system selection | Numbered list (1/2/3) | YES | See Example 3 above |
| Step 2c: Paths confirmation | "Press Enter to accept defaults" | DISCRETION | Might stay plain-text since it's a confirmation of auto-detected values |
| Step 4: Re-run update sections | Various per-field prompts | DISCRETION | "Edit/add/remove audience" could be AskUserQuestion |

### Review Skill (review/SKILL.md)
| Location | Current Pattern | Convert? | Notes |
|----------|----------------|----------|-------|
| Step 2: --edit confirmation gate | "Proceed? (yes/no)" | YES | Binary choice, see Example 4 |

### Edit Skill (edit/SKILL.md)
| Location | Current Pattern | Convert? | Notes |
|----------|----------------|----------|-------|
| Step 1: Issue selection | Numbered list + "select issues to fix" | YES (multiSelect) | Must preserve $ARGUMENTS freeform bypass |
| Step 1: "Describe something else" | Currently the last numbered item | MERGE | Becomes the "Type something else" mandatory option |

### Doc Author Agent (doc-author.md)
| Location | Current Pattern | Convert? | Notes |
|----------|----------------|----------|-------|
| Step 3: Page inventory approval | "Wait for user to approve/modify/add/remove" | YES (multiSelect) | See Example 5. Pre-select all pages. User deselects to exclude |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Plain-text numbered lists | AskUserQuestion tool | CC plugin ecosystem standard | Clickable UI, better accessibility, type-safe responses |
| No argument hints | argument-hint frontmatter | CC frontmatter spec | Autocomplete suggestions in Claude Code CLI |

**Note:** Three of four skills already have argument-hint. Only review is missing it. The existing argument-hints match the CONTEXT.md specifications exactly, so no changes needed to write, setup, or edit skill hints.

## Open Questions

1. **multiSelect pre-selection behavior**
   - What we know: multiSelect: true allows selecting multiple options. The doc-author page inventory should pre-select all pages.
   - What's unclear: Whether AskUserQuestion supports pre-selecting options (default checked). If not, the "deselect to exclude" UX pattern may need adjustment.
   - Recommendation: Write the instruction assuming pre-selection is possible. If it's not, fall back to "select pages to include" (user checks the ones they want).

2. **Option count limits**
   - What we know: GSD questioning guide says 2-4 options is ideal.
   - What's unclear: With 2 mandatory trailing options, the practical limit for concrete choices is 2-4. But PARTIAL approval and page inventory could have many items.
   - Recommendation: For dynamic lists (PARTIAL fixes, page inventory, issue selection), the 2-4 guideline doesn't apply -- these are data-driven option sets. Keep the guideline for static choice points only.

3. **Shared pattern block vs per-question instructions**
   - What we know: Multiple AskUserQuestion calls in one SKILL.md means repeated handling instructions for "Type something else" and "Chat about this".
   - What's unclear: Whether to define the pattern once at the top of the skill and reference it, or repeat instructions at each call site.
   - Recommendation: Define the standard pattern once near the top of each SKILL.md file under a "## User Interaction Pattern" section, then reference it at each call point: "Use AskUserQuestion (see User Interaction Pattern above)."

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bats (Bash Automated Testing System) |
| Config file | none -- tests run directly |
| Quick run command | `bats tests/phase-08-validation.bats` |
| Full suite command | `bats tests/` |

### Phase Requirements -> Test Map

Since phase 8 has no formal requirement IDs (TBD in ROADMAP), the validation tests map to the two workstreams:

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P8-01 | All 4 skills have argument-hint frontmatter | unit (grep) | `bats tests/phase-08-validation.bats -f "argument-hint"` | No -- Wave 0 |
| P8-02 | argument-hint values match spec | unit (grep) | `bats tests/phase-08-validation.bats -f "argument-hint"` | No -- Wave 0 |
| P8-03 | Write skill Step 6 uses AskUserQuestion pattern | unit (grep) | `bats tests/phase-08-validation.bats -f "AskUserQuestion"` | No -- Wave 0 |
| P8-04 | Setup skill has AskUserQuestion for doc system selection | unit (grep) | `bats tests/phase-08-validation.bats -f "AskUserQuestion"` | No -- Wave 0 |
| P8-05 | Review skill has AskUserQuestion for --edit confirmation | unit (grep) | `bats tests/phase-08-validation.bats -f "AskUserQuestion"` | No -- Wave 0 |
| P8-06 | Edit skill has AskUserQuestion for issue selection | unit (grep) | `bats tests/phase-08-validation.bats -f "AskUserQuestion"` | No -- Wave 0 |
| P8-07 | Doc-author agent has AskUserQuestion for page inventory | unit (grep) | `bats tests/phase-08-validation.bats -f "AskUserQuestion"` | No -- Wave 0 |
| P8-08 | Every AskUserQuestion block includes "Type something else" | unit (grep) | `bats tests/phase-08-validation.bats -f "Type something"` | No -- Wave 0 |
| P8-09 | Every AskUserQuestion block includes "Chat about this" | unit (grep) | `bats tests/phase-08-validation.bats -f "Chat about"` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `bats tests/phase-08-validation.bats`
- **Per wave merge:** `bats tests/`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/phase-08-validation.bats` -- covers P8-01 through P8-09
- [ ] Framework install: `bats` -- already available (used in phase 07)

## Sources

### Primary (HIGH confidence)
- `/Users/paul/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/command-development/references/frontmatter-reference.md` -- argument-hint syntax, examples, best practices
- `/Users/paul/.claude/get-shit-done/references/questioning.md` -- AskUserQuestion usage, freeform_rule, anti-patterns
- Direct file reads of all 4 SKILL.md files and doc-author.md -- current state baseline
- GSD workflow files (discuss-phase.md, quick.md) -- real-world AskUserQuestion usage patterns with multiSelect

### Secondary (MEDIUM confidence)
- CONTEXT.md decisions from user discussion session -- locked conversion targets and option patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- tools are CC built-ins with clear documentation
- Architecture: HIGH -- patterns are directly observable in GSD workflows and reference docs
- Pitfalls: HIGH -- derived from direct analysis of existing SKILL.md files against AskUserQuestion constraints
- Conversion inventory: HIGH -- exhaustive grep + manual review of all 5 target files

**Research date:** 2026-03-16
**Valid until:** 2026-04-16 (stable -- CC frontmatter and AskUserQuestion API unlikely to change)
