# Phase 20: 3-Way Merge - Research

**Researched:** 2026-03-26
**Domain:** Section-level 3-way merge for markdown guidance and rules files within a Claude Code plugin
**Confidence:** HIGH

## Summary

Phase 20 extends the existing `/doc-writer:upgrade` command (SKILL.md) with section-level 3-way merge logic for guidance files (`{doc_system}.md`) and rules files (`rules.md`). Currently, the upgrade skill's Step 3 detects customized files but skips them with the message "Merge support coming in a future upgrade." Phase 20 replaces that skip-with-message behavior with actual merge logic: parsing files by `##` headings into sections, comparing sections three ways (BASE from `.originals/`, USER from `.doc-writer/`, NEW from plugin defaults), auto-applying non-conflicting changes, and presenting conflicts one at a time via AskUserQuestion.

The scope also includes MERGE-04: a 2-way diff bootstrap path for pre-v1.5.0 projects that lack `.originals/`. These projects cannot perform a true 3-way merge because there is no BASE. Instead, the user is shown what would change (plugin defaults vs their current file) and can accept/reject each change. After completion, `.originals/` is bootstrapped with the NEW plugin defaults.

The key design challenge is defining what constitutes a "section" and what constitutes a "conflict." The files use `##` as the primary section delimiter, with `###` and `####` sub-headings nested within. Sections are compared as atomic units -- the entire text block from one `##` heading to the next. Content before the first `##` heading (the `# Title` line and introductory paragraph) is treated as a special "preamble" section. This section-level granularity is a deliberate design choice: it prevents silent prose corruption that line-level diff3 would cause in natural language documents, while still being granular enough to auto-merge most non-conflicting changes.

**Primary recommendation:** Modify `doc-writer/skills/upgrade/SKILL.md` to replace Step 3's skip-customized-files logic with full section-level 3-way merge instructions. Add a new Step 3.5 (or restructure Step 3) for the pre-v1.5.0 2-way diff bootstrap path. The merge algorithm is expressed entirely as Claude instructions in prose -- no executable code, no diff library. Claude IS the merge engine: it reads all three versions, parses sections, classifies changes, and applies them.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MERGE-01 | User runs `/doc-writer:upgrade` and `{doc_system}.md` is updated via section-level 3-way merge -- non-conflicting upstream changes applied automatically, user-customized sections preserved | Step 3 merge algorithm: parse by `##` headings, classify each section as unchanged/added/removed/modified, auto-apply non-conflicting changes, preserve user customizations |
| MERGE-02 | User runs `/doc-writer:upgrade` and `rules.md` is updated via the same section-level 3-way merge -- project-specific rules preserved while new default rules are added | Same merge algorithm applied to rules.md; user's `## Project Rules` content is preserved while new `##` sections from plugin defaults are added |
| MERGE-03 | User resolves each merge conflict individually via AskUserQuestion with options: keep user version, take plugin version, or provide custom resolution | Conflict presentation via AskUserQuestion with 4 options per conflict: keep yours, take theirs, custom resolution, chat about this |
| MERGE-04 | Pre-v1.5.0 project (no `.originals/`) runs upgrade and gets 2-way diff with per-change accept/reject, then `.originals/` bootstrapped | 2-way diff path: compare USER file vs NEW plugin defaults section by section, present each difference with accept/reject, then write `.originals/` with NEW content |
</phase_requirements>

## Standard Stack

This phase modifies a markdown instruction file for a Claude Code plugin. There are no npm packages, no compiled code, no external dependencies. The "stack" is:

### Core
| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| `SKILL.md` (upgrade) | Claude Code plugin format | Upgrade workflow instructions -- being extended | Existing file from Phase 19; merge logic is added to Step 3 |
| `.originals/` directory | Established Phase 18 | BASE files for 3-way merge | Created by setup, used by upgrade |
| `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/` | Plugin defaults directory | NEW files for merge comparison | Source of truth for current plugin version files |
| AskUserQuestion | Claude Code built-in tool | Conflict resolution UI | Only way to present structured choices in a skill |

### Supporting
| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| `config.yaml` | YAML | Reads `doc_system` to identify guidance file | Already read in Step 1; doc_system needed for file naming |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Section-level merge (by `##` headings) | Line-level diff3 | Line-level diff3 corrupts natural language prose -- a reworded sentence shows as a conflict even though the meaning is preserved. Section-level is coarser but safer for guidance documents. Explicitly chosen per REQUIREMENTS.md |
| Claude-as-merge-engine | External diff tool via Bash | Claude already reads the files; it can parse markdown headings and compare content more semantically than a text diff tool. No bash dependency needed. |

## Architecture Patterns

### File Structure (Changes from Phase 19)
```
doc-writer/
  skills/
    upgrade/
      SKILL.md           # MODIFIED: Step 3 expanded with merge logic
    setup/
      defaults/
        rules.md              # EXISTING: source for NEW in merge
        {framework}.md        # EXISTING: source for NEW in merge
```

No new files are created. This phase is a single-file modification to `doc-writer/skills/upgrade/SKILL.md`.

### Pattern 1: Section Parsing by `##` Headings
**What:** Files are parsed into sections where each section starts at a `##` heading and extends to the next `##` heading (or end of file). Content before the first `##` heading (title, intro paragraph) is treated as a "preamble" section.
**When to use:** Every merge operation on guidance and rules files.
**Structure:**
```
Preamble:   "# Title\n\nIntro paragraph..."
Section 1:  "## Admonitions\n\n- bullet 1\n- bullet 2..."
Section 2:  "## Code Blocks\n\n- bullet 1..."
...
```

**Key details:**
- The section key is the `##` heading text itself (e.g., `"## Admonitions"`)
- Sub-headings (`###`, `####`) are part of their parent `##` section, not separate sections
- The preamble (everything before the first `##`) uses a special key like `__preamble__`
- Section ordering matters -- when reassembling the file, preserve the order from the merged result

**Example: mkdocs-material.md sections:**
```
Preamble: "# MkDocs Material Guidance\n\nOpinionated preferences..."
## Admonitions        (5 bullets, no sub-headings)
## Code Blocks        (5 bullets, no sub-headings)
## Content Tabs       (4 bullets, no sub-headings)
## Navigation         (contains ### and #### sub-headings -- all part of this section)
## Frontmatter        (3 bullets)
## Cross-References   (3 bullets)
## Mermaid Diagrams   (5 bullets, code block)
```

**Example: rules.md sections:**
```
Preamble: "# Project Documentation Rules\n\nThese rules are specific..."
## How Rules Work     (3 bullets)
## Project Rules      (HTML comments with examples -- users add content here)
```

### Pattern 2: 3-Way Section Classification
**What:** For each section identified by its `##` heading, classify the change type by comparing BASE, USER, and NEW content.
**When to use:** Every 3-way merge.

| BASE | USER | NEW | Classification | Action |
|------|------|-----|---------------|--------|
| has section | same as BASE | same as BASE | No change | Skip (keep as-is) |
| has section | same as BASE | different | Upstream change only | Auto-apply NEW (user never customized) |
| has section | different | same as BASE | User change only | Keep USER (no upstream changes) |
| has section | different | different, same as USER | Convergent change | Keep USER (both arrived at same content) |
| has section | different | different, different from USER | True conflict | Present to user via AskUserQuestion |
| missing | missing | has section | New section | Auto-add from NEW |
| has section | has section | missing | Upstream removal | If USER == BASE: auto-remove. If USER != BASE: conflict (user customized a section that upstream removed) |
| has section | missing | has section | User removed section | Keep removed (user intentionally deleted it) |
| missing | has section | missing | User added section | Keep USER's addition |
| missing | has section | has section | User and upstream both added | If USER == NEW: keep (convergent). If different: conflict |

### Pattern 3: Section Ordering in Merged Output
**What:** After classifying all sections, the merged file must be reassembled in a sensible order.
**When to use:** Writing the merged result.

**Ordering rules:**
1. Preamble always comes first
2. Sections present in NEW define the canonical order (this is the plugin's intended structure)
3. User-added sections (present in USER but not in NEW or BASE) are appended after the last NEW section, preserving their relative order from USER
4. Removed sections are omitted

### Pattern 4: Conflict Resolution via AskUserQuestion
**What:** When a true conflict is detected, present it to the user one conflict at a time.
**When to use:** MERGE-03 -- any section where BASE, USER, and NEW all differ.

**AskUserQuestion format:**
```
Use AskUserQuestion:
- header: "Merge Conflict"
- question: "Section '## {heading}' in {filename} was changed both by you and the plugin update.\n\nYour version:\n{user_content_preview}\n\nPlugin version:\n{new_content_preview}"
- options:
  - { label: "Keep mine", description: "Preserve your customized version" }
  - { label: "Take plugin update", description: "Replace with the new plugin version" }
  - { label: "Type something else", description: "Provide a custom resolution" }
  - { label: "Chat about this", description: "Discuss the differences in detail" }
```

### Pattern 5: 2-Way Diff for Pre-v1.5.0 Bootstrap (MERGE-04)
**What:** When `.originals/` does not exist, there is no BASE for 3-way merge. Instead, compare USER vs NEW section by section.
**When to use:** Pre-v1.5.0 projects running upgrade for the first time.

**Flow:**
1. Parse USER file into sections by `##` headings
2. Parse NEW file into sections by `##` headings
3. For each section in NEW that is identical to USER: skip (no change needed)
4. For each section in NEW that differs from USER: present the change via AskUserQuestion with accept/reject
5. For each section in USER that is not in NEW: keep (user addition)
6. For each section in NEW that is not in USER: present as "new section -- add?" with accept/reject
7. After all decisions: write merged result to `.doc-writer/{file}`
8. Write NEW content to `.doc-writer/.originals/{file}` (bootstrap the baseline)

**AskUserQuestion format for 2-way:**
```
Use AskUserQuestion:
- header: "File Update"
- question: "Section '## {heading}' in {filename} differs from the current plugin version.\n\nYour version:\n{user_content_preview}\n\nPlugin version:\n{new_content_preview}"
- options:
  - { label: "Keep mine", description: "Preserve your current version" }
  - { label: "Accept update", description: "Take the plugin version" }
  - { label: "Type something else", description: "Provide a custom version" }
  - { label: "Chat about this", description: "Discuss the differences" }
```

### Anti-Patterns to Avoid
- **Line-level diff3:** Natural language documents are not code. A reworded bullet point is not a "conflict" -- it is an upstream improvement. Section-level comparison avoids false conflicts from minor prose edits within a section.
- **Merging sub-headings independently:** `###` and `####` headings within a `##` section are part of that section. Splitting them out would fragment the Navigation section (which has `### Three Navigation Strategies` containing `#### Strategy 1/2/3`) into 5+ separate merge units, making auto-merge unreliable.
- **Silently removing user content:** If the user customized a section that upstream removed, that is a conflict, not an auto-remove. The user invested effort in customization; removing it silently violates trust.
- **Modifying .originals/ before merge completes:** If the merge fails partway through, `.originals/` should still reflect the previous state. Update `.originals/` only after the merged file is successfully written.
- **Presenting all conflicts at once:** MERGE-03 requires one-at-a-time presentation. Dumping all conflicts in a single message overwhelms the user and makes custom resolution impractical.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Section parsing | Custom regex parser in bash | Claude reads the file and identifies `##` headings | Claude already reads the file; heading detection is trivial for an LLM. Bash regex would be fragile with code blocks containing `##` |
| Content comparison | `diff` command in bash | Claude reads both sections and determines if identical | Files are small (<400 lines). Claude comparing two text blocks is more reliable than parsing diff output |
| Merge resolution | Custom merge driver | Claude applies the classification table directly | The "merge engine" is the classification table above. Claude follows the table, applies results, and asks the user on conflicts. No algorithm to implement. |
| Conflict display | Custom diff formatting | Show sections directly in AskUserQuestion | The sections are readable markdown. Showing them directly is clearer than diff markers. |

**Key insight:** This is a SKILL.md -- instructions for Claude. Claude IS the merge engine. The instructions tell Claude how to parse sections, classify changes, and handle each case. There is no code to write. The "algorithm" is expressed as prose instructions that Claude follows.

## Common Pitfalls

### Pitfall 1: Code blocks containing `##` headings
**What goes wrong:** A code block inside a section contains `## Example Heading` as part of an example, and the parser incorrectly splits the section at that line.
**Why it happens:** Naive parsing of `##` at line start without accounting for fenced code block context.
**How to avoid:** The SKILL.md must instruct Claude: "When parsing sections, ignore `##` headings that appear inside fenced code blocks (between ``` delimiters). Only split on `##` headings that are at the top level of the markdown document."
**Warning signs:** Sections that end mid-code-block. Navigation section being split by YAML examples containing `##` comments.

### Pitfall 2: Forgetting to update .originals/ after merge
**What goes wrong:** After a successful merge, `.originals/` still contains the old BASE content. Future upgrades would compute the wrong diff (comparing against stale originals).
**Why it happens:** The merge focuses on producing the merged output for `.doc-writer/{file}` and forgets the bookkeeping step.
**How to avoid:** After writing the merged file, ALSO write the NEW content (not the merged content) to `.originals/{file}`. The originals always track what the plugin shipped, not what the user has.
**Warning signs:** `.originals/` content unchanged after an upgrade that performed merges.

### Pitfall 3: Section ordering drift
**What goes wrong:** The merged file has sections in an unexpected order -- user-added sections interspersed randomly with plugin sections.
**Why it happens:** No ordering rule specified, so Claude uses an arbitrary order.
**How to avoid:** Specify explicit ordering: NEW defines the canonical order, user-added sections go at the end.
**Warning signs:** User's custom `## My Project Rules` section appearing between `## How Rules Work` and `## Project Rules` instead of after `## Project Rules`.

### Pitfall 4: Preamble not handled
**What goes wrong:** The `# Title` line and introductory paragraph are not compared or merged, leading to stale titles or intro text.
**Why it happens:** The parsing only looks for `##` headings and misses content before the first `##`.
**How to avoid:** Treat everything before the first `##` as a special "preamble" section and include it in the merge classification.
**Warning signs:** File title or intro paragraph not updated when upstream changes them.

### Pitfall 5: Conflict resolution loses context
**What goes wrong:** When presenting a conflict to the user, only the diff is shown without the section heading or file context, leaving the user confused about what they are deciding.
**Why it happens:** The AskUserQuestion only shows content snippets without identifying which file or section.
**How to avoid:** Always include the filename and section heading in the conflict question. If sections are long, show the first few lines as a preview with a note about full content.
**Warning signs:** Conflict questions that say "this section changed" without specifying which section or file.

### Pitfall 6: 2-way bootstrap writes wrong content to .originals/
**What goes wrong:** For pre-v1.5.0 bootstrap (MERGE-04), `.originals/` is written with the USER's current content instead of the NEW plugin defaults.
**Why it happens:** Confusion about what `.originals/` represents -- it should always be the plugin's shipped version, not the user's version.
**How to avoid:** The SKILL.md must explicitly state: "Write the NEW (current plugin default) content to `.originals/`, regardless of what the user accepted or rejected during the 2-way diff."
**Warning signs:** `.originals/` content matching the user's file instead of the plugin defaults.

### Pitfall 7: FALLBACK framework files treated as mergeable
**What goes wrong:** Researcher-generated guidance files (for unknown frameworks) are passed through the merge logic, but they have no corresponding plugin default.
**Why it happens:** The Phase 19 SKILL.md already handles this case (skip FALLBACK files), but the new merge logic might re-introduce the check.
**How to avoid:** The existing check in Step 3c handles this: "Check if this file exists [in plugin defaults]. If it does not exist (FALLBACK framework): skip this file." This check must remain in the merged Step 3 logic, before the merge algorithm runs.
**Warning signs:** Merge attempting to read `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/custom-framework.md` which does not exist.

### Pitfall 8: Empty sections or whitespace-only differences treated as conflicts
**What goes wrong:** Trailing whitespace or blank line differences between sections cause false conflicts.
**Why it happens:** Exact string comparison of section content without normalizing whitespace.
**How to avoid:** The SKILL.md should instruct Claude to compare section content after trimming trailing whitespace from each line and normalizing trailing newlines. Semantic comparison, not byte-exact.
**Warning signs:** Conflict reported for a section where the only difference is trailing whitespace.

## Merge Algorithm: Complete Specification

This is the definitive specification that the SKILL.md instructions must encode.

### Input
- **BASE**: `.doc-writer/.originals/{file}` (what the plugin shipped last time)
- **USER**: `.doc-writer/{file}` (user's current working copy)
- **NEW**: `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{file}` (current plugin version)

### Step 1: Parse All Three Files Into Sections

Parse each file into an ordered list of sections:
```
Section = { key: string, heading: string, content: string }
```

- **Preamble**: Everything before the first `##` heading. Key = `__preamble__`.
- **Named sections**: Each `##` heading starts a new section. Key = the heading text (e.g., `"## Admonitions"`). Content = everything from the heading line through the last line before the next `##` heading (or EOF).
- **Important**: `###` and `####` headings do NOT start new sections. They are part of their parent `##` section.
- **Important**: `##` headings inside fenced code blocks (between ``` delimiters) do NOT start new sections.

### Step 2: Classify Each Section

Build a unified section list from the union of all section keys across BASE, USER, and NEW.

For each section key, classify using the decision table:

| In BASE? | In USER? | In NEW? | BASE==USER? | BASE==NEW? | USER==NEW? | Classification | Action |
|----------|----------|---------|-------------|------------|------------|----------------|--------|
| Y | Y | Y | Y | Y | - | Unchanged | Keep as-is |
| Y | Y | Y | Y | N | - | Upstream only | Auto-apply NEW |
| Y | Y | Y | N | Y | - | User only | Keep USER |
| Y | Y | Y | N | N | Y | Convergent | Keep USER |
| Y | Y | Y | N | N | N | **Conflict** | Ask user |
| N | N | Y | - | - | - | Added upstream | Auto-add from NEW |
| Y | Y | N | Y | - | - | Removed upstream (user didn't customize) | Auto-remove |
| Y | Y | N | N | - | - | **Conflict** (user customized, upstream removed) | Ask user |
| Y | N | Y | - | - | - | User removed | Keep removed |
| Y | N | N | - | - | - | Both removed | Already gone |
| N | Y | N | - | - | - | User added | Keep USER |
| N | Y | Y | - | - | Y | Both added (same) | Keep USER |
| N | Y | Y | - | - | N | **Conflict** (both added differently) | Ask user |

### Step 3: Apply Non-Conflicting Changes

Build the merged section list:
1. Start with NEW's section order as the canonical ordering
2. For each section in NEW's order: use the classified action (keep USER, apply NEW, etc.)
3. Append USER-only sections (not in NEW or BASE) at the end, preserving their relative order from USER
4. Omit removed sections

### Step 4: Resolve Conflicts

For each conflict (there may be zero):
1. Present via AskUserQuestion with the section heading, filename, and both versions
2. Apply the user's choice
3. Move to the next conflict

### Step 5: Reassemble and Write

1. Concatenate all sections in order (preamble first, then named sections)
2. Write the result to `.doc-writer/{file}`
3. Write NEW content to `.doc-writer/.originals/{file}` (always tracks what the plugin shipped)

### Upgrade Summary Additions

After merge, add to the upgrade summary:
```
### File Merges
- {file}: {N} sections auto-merged, {M} conflicts resolved by user
- {file}: No upstream changes (all sections unchanged)
```

## Integration with Existing SKILL.md

The current upgrade SKILL.md (160 lines) has a 4-step flow. Phase 20 modifies **Step 3 only**. Steps 1, 2, and 4 are unchanged except for summary additions.

### Current Step 3 Structure (Phase 19)

```
Step 3: Unchanged File Update
  3.1: Check .originals/ exists
  3.2: Read doc_system from config
  3.3: For each file in .originals/:
    3.3a: Read BASE (.originals/)
    3.3b: Read USER (.doc-writer/)
    3.3c: Read NEW (plugin defaults) -- skip if FALLBACK
    3.3d: Check if this file exists in defaults
    3.3e: If BASE == NEW: skip (no upstream changes)
    3.3f: If USER == BASE: silently overwrite (unchanged file)
    3.3g: If USER != BASE: **SKIP** -- "Merge support coming in a future upgrade."
```

### Phase 20 Modification

Replace Step 3.3g with the full merge algorithm. The existing 3.3a-3.3f flow remains as-is (those are the non-conflict fast paths that Phase 19 already handles correctly). The only change is: when USER differs from BASE AND BASE differs from NEW (3.3g), instead of skipping, run the section-level merge.

Additionally, replace the current Step 3.1 behavior for missing `.originals/` (which currently warns and skips) with the MERGE-04 2-way diff bootstrap path.

### Revised Step 3 Structure (Phase 20)

```
Step 3: File Merge
  3.1: Check .originals/ exists
    IF MISSING: Run 2-way diff bootstrap (MERGE-04 path)
      For each file: parse USER and NEW by sections, present diffs, write merged result
      Create .originals/ with NEW content
      Skip to Step 4
  3.2: Read doc_system from config
  3.3: For each file in .originals/:
    3.3a: Read BASE (.originals/)
    3.3b: Read USER (.doc-writer/)
    3.3c: Check if NEW exists in plugin defaults -- skip if FALLBACK
    3.3d: Read NEW (plugin defaults)
    3.3e: If BASE == NEW: skip (no upstream changes to this file)
    3.3f: If USER == BASE: silently overwrite with NEW + update .originals/ (unchanged file path -- existing Phase 19 logic)
    3.3g: If USER != BASE AND BASE != NEW: RUN SECTION-LEVEL 3-WAY MERGE
      - Parse BASE, USER, NEW into sections
      - Classify each section per decision table
      - Auto-apply non-conflicting changes
      - Present conflicts one at a time via AskUserQuestion
      - Write merged result to .doc-writer/{file}
      - Write NEW to .originals/{file}
      - Record merge stats for summary
```

### allowed-tools Update

Phase 19 SKILL.md has `allowed-tools: Read, Write, Bash, Glob, Grep`. Phase 20 may need to keep this unchanged -- AskUserQuestion is always available to skills regardless of the allowed-tools list (it is a built-in Claude Code capability, not a user tool). Verify this assumption during implementation.

## Code Examples

### Example 1: Section Parsing Instruction (for SKILL.md prose)

```markdown
**Parsing files into sections:**

Read the file content and split it into sections at `##` heading boundaries:

1. **Preamble**: Everything from the start of the file up to (but not including) the first line that starts with `## `. If no `## ` line exists, the entire file is a single preamble section.

2. **Named sections**: Each line that starts with `## ` (at the document top level, NOT inside a fenced code block) begins a new section. The section includes the heading line itself and all content up to the next `## ` heading or end of file.

3. **Sub-headings are NOT section boundaries**: Lines starting with `### ` or `#### ` are part of their parent `## ` section. Do not split on them.

4. **Code block awareness**: When scanning for `## ` headings, track whether you are inside a fenced code block (between ``` delimiters). Skip any `## ` that appears within a fenced code block.

Identify each section by its heading text (e.g., `"## Admonitions"`, `"## Navigation"`). The preamble is identified by a special marker (e.g., `"__preamble__"`).
```

### Example 2: Conflict Presentation (for SKILL.md prose)

```markdown
**Presenting a conflict to the user:**

For each conflict, use AskUserQuestion:
- header: "Merge Conflict"
- question: "Section '{heading}' in {filename} was changed both by you and in the plugin update.

Your version:
---
{first 10 lines of USER section, or full section if <= 10 lines}
{if truncated: '... ({N} more lines)'}
---

Plugin version:
---
{first 10 lines of NEW section, or full section if <= 10 lines}
{if truncated: '... ({N} more lines)'}
---"
- options:
  - { label: "Keep mine", description: "Preserve your customized version of this section" }
  - { label: "Take plugin update", description: "Replace with the new plugin version of this section" }
  - { label: "Type something else", description: "Provide a custom resolution for this section" }
  - { label: "Chat about this", description: "See full content and discuss the differences" }
```

### Example 3: 2-Way Diff Bootstrap (for SKILL.md prose)

```markdown
**2-way diff for pre-v1.5.0 projects (no .originals/):**

This project was set up before upgrade support was available. Since there are no original baseline files, a full 3-way merge is not possible. Instead, compare your current files against the current plugin defaults section by section.

1. For each guidance/rules file, parse both USER and NEW into sections.
2. Sections that are identical between USER and NEW: no action needed.
3. Sections in NEW but not in USER (new sections): present to user:
   - header: "New Section"
   - question: "The plugin update adds a new section '## {heading}' to {filename}:\n\n{section_preview}\n\nAdd this section?"
   - options:
     - { label: "Add", description: "Include this new section" }
     - { label: "Skip", description: "Do not add this section" }
     - { label: "Chat about this", description: "Discuss what this section covers" }
4. Sections that differ between USER and NEW: present to user:
   - header: "Section Difference"
   - question: "Section '## {heading}' in {filename} differs from the current plugin version. ..."
   (same format as conflict resolution)
5. Sections in USER but not in NEW (user additions): keep silently.
6. After all decisions: write merged result, create .originals/ with NEW content.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Skip customized files with message | Section-level 3-way merge | Phase 20 (this phase) | Users no longer need to manually apply upstream changes to customized files |
| No upgrade path for pre-v1.5.0 | 2-way diff bootstrap | Phase 20 (this phase) | Pre-v1.5.0 projects can upgrade with guided file migration |
| Line-level diff3 (rejected) | Section-level merge by `##` headings | Architecture research | Prevents false conflicts from prose rewording within sections |

## Open Questions

1. **Should "Type something else" for conflicts allow full section editing?**
   - What we know: The user selects "Type something else" and provides custom text. For a section that might be 20-50 lines, this is awkward in a chat interface.
   - What's unclear: Whether Claude should offer to merge the two versions intelligently (e.g., "I'll combine the best parts of both") or just accept raw text.
   - Recommendation: Accept freeform text for the replacement section content. If the user asks Claude to merge, Claude can do so conversationally since "Chat about this" is available. Keep the base interaction simple.

2. **Should the merge summary show auto-applied changes?**
   - What we know: Non-conflicting changes are applied silently (user did not customize those sections).
   - What's unclear: Whether users want to see "Auto-applied upstream changes to ## Admonitions, ## Code Blocks" in the summary, or just "2 sections auto-merged."
   - Recommendation: Show section names in the summary. Users should know what changed even if it was automatic. Pattern: "Auto-applied upstream changes: ## Admonitions, ## Code Blocks, ## Mermaid Diagrams"

3. **File-level preamble changes: auto-apply or ask?**
   - What we know: The preamble is the title + intro paragraph. Upstream might change the intro text.
   - What's unclear: Whether preamble changes should follow the same rules as section changes (auto-apply if user didn't customize, ask if they did).
   - Recommendation: Yes, treat the preamble the same as any other section. Same classification table, same conflict resolution. The preamble is just a section with a special key.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None -- no test framework for SKILL.md files |
| Config file | none |
| Quick run command | N/A |
| Full suite command | N/A |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MERGE-01 | Guidance file 3-way merge with auto-apply and preservation | manual-only | Run `/doc-writer:upgrade` after modifying a guidance file and updating plugin defaults | N/A |
| MERGE-02 | Rules file 3-way merge with project rules preserved | manual-only | Run `/doc-writer:upgrade` after adding custom rules and updating plugin defaults | N/A |
| MERGE-03 | Conflict resolution one-at-a-time via AskUserQuestion | manual-only | Run `/doc-writer:upgrade` with both user customizations and upstream changes in the same section | N/A |
| MERGE-04 | Pre-v1.5.0 2-way diff bootstrap | manual-only | Run `/doc-writer:upgrade` on a project with no `.originals/` directory (delete it to simulate) | N/A |

**Justification for manual-only:** Same as Phase 19 -- the deliverable is a markdown instruction file. The "test" is Claude interpreting the SKILL.md and performing the merge correctly. Validated by running the command in a real project.

### Sampling Rate
- **Per task commit:** Content review of SKILL.md changes
- **Per wave merge:** N/A
- **Phase gate:** Manual run of `/doc-writer:upgrade` against a test project with customized files

### Wave 0 Gaps
None -- no test infrastructure needed.

## Sources

### Primary (HIGH confidence)
- `doc-writer/skills/upgrade/SKILL.md` -- 160 lines, current upgrade flow that Phase 20 extends
- `doc-writer/skills/setup/SKILL.md` -- 591 lines, canonical AskUserQuestion patterns and file handling
- `doc-writer/skills/setup/defaults/rules.md` -- 27 lines, rules file structure (2 `##` sections)
- `doc-writer/skills/setup/defaults/mkdocs-material.md` -- 196 lines, guidance file structure (7 `##` sections, `###`/`####` sub-headings under Navigation)
- `doc-writer/skills/setup/defaults/sphinx-shibuya.md` -- 288 lines, guidance file structure (9 `##` sections, `###`/`####` sub-headings under Navigation)
- `doc-writer/skills/setup/defaults/odoc.md` -- 399 lines, guidance file structure (11 `##` sections, no sub-headings)
- `doc-writer/skills/setup/defaults/plain-markdown.md` -- 68 lines, guidance file structure (8 `##` sections)
- `.planning/research/ARCHITECTURE.md` -- 3-way merge design, .originals/ data flow, pre-v1.5.0 handling
- `.planning/REQUIREMENTS.md` -- MERGE-01 through MERGE-04 requirements and Out of Scope items
- `.planning/phases/19-upgrade-skill/19-CONTEXT.md` -- Phase 19 decisions (D-10, D-11 on file handling; deferred merge to Phase 20)
- `.planning/phases/19-upgrade-skill/19-01-SUMMARY.md` -- Phase 19 outputs confirming Step 3g is the merge extension point

### Secondary (MEDIUM confidence)
None needed -- all findings from reading existing codebase.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- fully constrained by Claude Code plugin format, no choices to make
- Architecture: HIGH -- merge algorithm is well-defined from first principles; section parsing is straightforward for the known file structures; all files are small (<400 lines)
- Pitfalls: HIGH -- derived from careful analysis of the file structures and merge edge cases

**Research date:** 2026-03-26
**Valid until:** Indefinite -- internal project architecture, not external library versions
