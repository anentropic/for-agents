# Phase 21: Q&A Gap Detection and Finalization - Research

**Researched:** 2026-03-26
**Domain:** Q&A gap detection and researcher re-run within a Claude Code plugin upgrade skill
**Confidence:** HIGH

## Summary

Phase 21 is the final phase of the v1.5.0 milestone. It extends the existing `/doc-writer:upgrade` command (SKILL.md) with two new capabilities: (1) detecting new framework Q&A questions that were added since the user last ran setup, asking only those unanswered questions, and (2) triggering a researcher re-run to regenerate `context.md` whenever the upgrade has produced actual changes (new Q&A answers or config field additions from Step 2).

The implementation requires two modifications to the upgrade SKILL.md: a new Step 3.5 (or inserted between existing Steps 3 and 4) for Q&A gap detection, and a new Step 4.5 (or Step 5) for researcher re-run. The existing Step 4 (Finalize) needs minor adjustments to its summary template. Additionally, the `allowed-tools` in the SKILL.md frontmatter must be updated to include `Agent` since the researcher re-run spawns the `doc-researcher` agent.

The core mechanism for QA-01 is straightforward: read the current framework's `.qa.md` file, extract question headers, derive their keys (lowercase + underscores), compare against the `qa_answers` section in `config.yaml`, and present only questions whose keys are absent from `qa_answers`. The key design decisions from the assumptions review simplify implementation: FALLBACK frameworks skip Q&A gap detection entirely (no upstream `.qa.md` to compare against), question ID derivation uses the same rule as setup (lowercase header, spaces to underscores), and the researcher re-run only triggers when there are actual changes.

**Primary recommendation:** Modify `doc-writer/skills/upgrade/SKILL.md` to add Q&A gap detection after the file merge step and a conditional researcher re-run before finalization. Add `Agent` to `allowed-tools`. Update the Notes section to remove the "Q&A gap detection is handled by a separate future upgrade" note. Update the summary template to include Q&A and context refresh reporting.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| QA-01 | User runs `/doc-writer:upgrade` after plugin adds new Q&A questions and is asked only those new questions -- previously answered questions are not re-asked | New step between file merge and finalize: read `{doc_system}.qa.md` from plugin defaults, extract question headers, derive keys, compare against `qa_answers` in config.yaml, present only questions with absent keys via AskUserQuestion |
| QA-02 | User runs `/doc-writer:upgrade` after config field additions or new Q&A answers and `context.md` is refreshed via a researcher re-run reflecting the updated configuration | Conditional researcher re-run: if Step 2 added config fields OR the new Q&A step collected new answers, spawn `doc-researcher` agent with the same invocation pattern as setup Step 5 |
</phase_requirements>

## Standard Stack

This phase modifies a markdown instruction file for a Claude Code plugin. There are no npm packages, no compiled code, no external dependencies. The "stack" is:

### Core
| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| `SKILL.md` (upgrade) | Claude Code plugin format | Upgrade workflow instructions -- being extended | Existing file from Phase 19/20; Q&A gap and researcher steps added |
| `.qa.md` files | Framework Q&A definitions | Source of truth for question headers and IDs | 4 existing built-in files (mkdocs-material, sphinx-shibuya, odoc, plain-markdown) plus researcher-generated files for FALLBACK frameworks |
| `config.yaml` | YAML | User config with `qa_answers` section | Established in Phase 18; `qa_answers` keys match question header IDs |
| Agent tool | Claude Code built-in | Spawns doc-researcher agent | Used by setup skill for context enrichment; upgrade skill needs it for re-run |
| `doc-researcher` agent | Markdown agent definition | Regenerates `context.md` from config + codebase | Existing agent; same invocation as setup Step 5 |

### Supporting
| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.qa.md` | Plugin defaults directory | Source of NEW Q&A questions | Read during gap detection to find new questions |
| AskUserQuestion | Claude Code built-in tool | Present new Q&A questions to user | Same pattern as setup Step 2b.5 framework Q&A |

### Alternatives Considered
Not applicable -- technology choices are fully constrained by the Claude Code plugin system and existing patterns.

## Architecture Patterns

### File Structure (Changes from Phase 20)
```
doc-writer/
  skills/
    upgrade/
      SKILL.md           # MODIFIED: new Q&A gap step, researcher re-run, Agent in allowed-tools
    setup/
      defaults/
        {framework}.qa.md     # EXISTING: source of Q&A question definitions
        config-template.yaml  # EXISTING: unchanged
  agents/
    doc-researcher.md         # EXISTING: spawned for context.md refresh
```

No new files are created. This phase is a single-file modification to `doc-writer/skills/upgrade/SKILL.md`.

### Pattern 1: Q&A Gap Detection Algorithm
**What:** Compare stored `qa_answers` keys against current `.qa.md` question headers to find unanswered questions.
**When to use:** Every upgrade run (after file merge, before finalize).

**Algorithm:**
1. Read `doc_system` from config.yaml (already available from Step 1)
2. Determine the `.qa.md` file path: `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.qa.md`
3. Check if the `.qa.md` file exists. If not (FALLBACK framework), skip Q&A gap detection entirely
4. Read the `.qa.md` file. Parse `## Question N:` sections. Extract the `header` field from each question
5. Derive the expected key for each header: lowercase, replace spaces with underscores (e.g., "API docs" -> `api_docs`, "Navigation" -> `navigation`)
6. Read the `qa_answers` section from the user's config.yaml
7. For each derived key: if the key is absent from `qa_answers`, the question is new -- add to the "new questions" list
8. If no new questions: record "No new Q&A questions" for summary. Skip to next step.
9. If new questions found: present each one via AskUserQuestion using the same format as setup Step 2b.5

**Key detail:** The header-to-key derivation MUST match the setup skill's rule exactly (setup SKILL.md line 441): "derive the key by lowercasing the question's `header` field and replacing spaces with underscores." Any deviation would cause false positives (questions treated as new when they were already answered under a different key).

### Pattern 2: Presenting New Q&A Questions
**What:** Present each new question to the user using the same AskUserQuestion format as setup's Step 2b.5.
**When to use:** When Q&A gap detection finds unanswered questions.

**Flow:**
1. For each new question from the `.qa.md` file, present it via AskUserQuestion:
   - Use the `header`, `question`, and `options` fields from the `.qa.md` question section
   - If the question has `multiSelect: true`, set multiSelect on the AskUserQuestion
   - Every question MUST have "Type something else" and "Chat about this" as trailing options
2. After all new questions are answered, persist the new answers to `qa_answers` in config.yaml using the same key derivation rule
3. Record for the summary: "Asked {N} new Q&A question(s): {list of headers}"

**Note on detection context:** The setup skill's Step 2b.5 uses framework config detection (`detect_context`, `recommend_if`) to pre-select recommended options. The upgrade skill should do the same: if a framework config file exists, run detection and use it for recommendations. This matches the setup behavior and gives the user context-aware defaults.

### Pattern 3: Conditional Researcher Re-Run
**What:** Spawn `doc-researcher` agent to regenerate `context.md` only when there are actual changes to reflect.
**When to use:** When Step 2 added new config fields OR the Q&A gap step collected new answers.

**Trigger condition:**
```
IF (Step 2 added any new config fields) OR (Q&A gap step collected any new answers)
THEN spawn doc-researcher
ELSE skip researcher re-run
```

**Agent invocation:** Use the Agent tool with the same message format as setup Step 5:

```
Use the Agent tool to spawn `doc-researcher` with this message:

> Enrich the project configuration. Read `.doc-writer/config.yaml` for user personas, tone, and doc system. Scan the codebase (README, source files, framework config) and produce `.doc-writer/context.md` with expanded persona guidance, project domain summary, tone-specific writing rules, and framework usage preferences.
>
> Framework Q&A answers: {all qa_answers from config.yaml, including newly added ones}
```

**Key detail:** The framework Q&A answers passed to the researcher should include ALL answers (existing + new), not just the new ones. The researcher regenerates `context.md` from scratch every time -- it is not incremental.

### Pattern 4: Upgrade Flow with New Steps
**What:** The complete upgrade flow after Phase 21 modifications.
**Structure:**
```
Step 1: Version Detection (unchanged)
Step 2: Config Format Migration (unchanged, but track whether changes were made)
Step 3: File Merge (unchanged)
Step 3.5: Q&A Gap Detection (NEW)
  - Read .qa.md, compare headers against qa_answers
  - Present new questions via AskUserQuestion
  - Persist new answers to qa_answers in config.yaml
Step 4: Context Refresh (NEW -- conditional)
  - IF Step 2 or Step 3.5 produced changes: spawn doc-researcher
  - ELSE skip
Step 5: Finalize (renumbered from Step 4, updated summary template)
```

Alternatively, the steps could be numbered differently (e.g., keeping Step 4 as Finalize and inserting the new steps within Step 3). The key constraint is that Q&A gap detection must happen AFTER file merge (Step 3) but BEFORE finalize writes plugin_version and displays the summary. The researcher re-run must also complete before finalize so its results can be reflected in the summary.

### Anti-Patterns to Avoid
- **Re-asking existing questions:** The entire point of QA-01 is gap detection. Presenting questions whose keys already exist in `qa_answers` is a requirements violation.
- **Running researcher when nothing changed:** QA-02 specifies "after config field additions or new Q&A answers." If the upgrade only touched file merges (Step 3) with no config or Q&A changes, the researcher should NOT be re-run. Context.md would not benefit from regeneration.
- **Using a different key derivation than setup:** Setup derives keys by lowercasing the header and replacing spaces with underscores. The upgrade must use the identical rule. If a future `.qa.md` file uses a header like "API docs", setup stores it as `api_docs`. The upgrade must derive `api_docs` too, not `api-docs` or `apidocs`.
- **Spawning researcher without Agent tool:** The upgrade SKILL.md currently has `allowed-tools: Read, Write, Bash, Glob, Grep`. The Agent tool is NOT included. It must be added to the frontmatter for the researcher re-run to work.
- **Forgetting to include ALL Q&A answers in researcher invocation:** The researcher uses Q&A answers to generate framework preferences in context.md. It needs all answers, not just the new ones.
- **Attempting Q&A gap detection for FALLBACK frameworks:** FALLBACK frameworks have their `.qa.md` file in `.doc-writer/` (project-local), not in plugin defaults. The upgrade skill should NOT read from `.doc-writer/{doc_system}.qa.md` for gap detection -- these files were generated by the researcher at setup time and do not represent "upstream" question changes. Only plugin-shipped `.qa.md` files at `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.qa.md` are valid sources for gap detection.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Key derivation from headers | Custom algorithm | Same rule as setup: lowercase + replace spaces with underscores | Must match exactly or gap detection produces false positives |
| Q&A presentation | New question format | Reuse setup's Step 2b.5 AskUserQuestion format | Consistency with setup UX; .qa.md files already have the right structure |
| Researcher invocation | Custom agent message | Copy setup's Step 5 Agent tool pattern | Same agent, same input requirements, same output |
| Checking for changes | Complex state tracking | Simple boolean flags set during Steps 2 and 3.5 | Only need to know "did anything change?" not "what changed?" |

**Key insight:** Phase 21 reuses existing patterns wholesale. The Q&A question presentation is the same as setup. The key derivation is the same as setup. The researcher invocation is the same as setup. The only new logic is the gap detection comparison itself (set difference of keys).

## Common Pitfalls

### Pitfall 1: Key derivation mismatch between setup and upgrade
**What goes wrong:** Setup stores a Q&A answer under key `api_docs` but upgrade derives the key as `api-docs` (using hyphens instead of underscores). The question appears to be "new" even though it was already answered.
**Why it happens:** The key derivation rule is stated in prose in setup SKILL.md, not in code. Easy to paraphrase incorrectly.
**How to avoid:** The SKILL.md must state the exact rule: "lowercase the header field and replace spaces with underscores." Reference setup SKILL.md Step 2b.5 item 4 explicitly.
**Warning signs:** Users being re-asked questions they already answered during setup.

### Pitfall 2: Forgetting to add Agent to allowed-tools
**What goes wrong:** The upgrade skill tries to spawn `doc-researcher` but the Agent tool is not available. Claude silently skips the researcher or errors.
**Why it happens:** Phase 19 explicitly excluded Agent from allowed-tools because it was not needed. Phase 21 adds the need.
**How to avoid:** Update frontmatter: `allowed-tools: Read, Write, Bash, Glob, Grep, Agent`
**Warning signs:** `allowed-tools` line in SKILL.md does not contain `Agent`.

### Pitfall 3: Running researcher re-run unconditionally
**What goes wrong:** Every upgrade triggers a researcher re-run, even when the upgrade only performed file merges with no config or Q&A changes. This wastes time and context.
**Why it happens:** The design decision says "re-run only triggers when there are actual changes" but the implementation does not check.
**How to avoid:** Track a boolean flag: `changes_made = false`. Set to `true` in Step 2 if any config fields were added, and in Step 3.5 if any new Q&A answers were collected. Only spawn researcher if `changes_made` is true.
**Warning signs:** Researcher re-run happening on every upgrade regardless of whether anything changed.

### Pitfall 4: Attempting Q&A gap detection for FALLBACK frameworks
**What goes wrong:** The upgrade skill tries to read `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/custom-framework.qa.md` which does not exist, causing an error or false "no new questions" result.
**Why it happens:** FALLBACK frameworks have their `.qa.md` in `.doc-writer/` (project-local), not in plugin defaults. The upgrade should only check plugin-shipped `.qa.md` files.
**How to avoid:** Check if `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.qa.md` exists. If not, skip Q&A gap detection with a note: "Q&A gap detection skipped -- {doc_system} is not a built-in framework." This matches the FALLBACK skip behavior already used in Step 3 for file merge.
**Warning signs:** Error when reading non-existent `.qa.md` file from plugin defaults.

### Pitfall 5: Not handling odoc's dynamic follow-on questions
**What goes wrong:** Odoc's `.qa.md` has follow-on sub-topic questions that are generated dynamically at setup time (headers like "Tutorial topics", "How-to topics"). These questions have dynamically derived keys. The gap detection needs to handle these correctly.
**Why it happens:** Most frameworks have static questions with fixed headers. Odoc is unique in having questions whose existence depends on the answers to prior questions.
**How to avoid:** Two approaches: (a) Only check static `## Question N:` sections in the `.qa.md` file, not follow-on sections. Follow-on questions are extensions of their parent question -- if the parent is already answered, the follow-on was too. Or (b) accept that follow-on keys like `tutorial_topics` may or may not exist in `qa_answers` and only present the follow-on if the parent question's answer includes the corresponding guide type. Approach (a) is simpler and recommended.
**Warning signs:** Dynamic sub-topic questions being re-asked even though the user answered them during setup.

### Pitfall 6: Writing plugin_version before researcher completes
**What goes wrong:** The finalize step writes plugin_version and then the researcher runs and fails partway through. The plugin_version is already updated, so re-running upgrade shows "already up to date" even though context.md was not regenerated.
**Why it happens:** The researcher re-run is placed after finalize instead of before.
**How to avoid:** The researcher re-run step MUST come before the finalize step that writes plugin_version. The existing rule from Phase 19 (Pitfall 6) applies: plugin_version is the LAST write.
**Warning signs:** Researcher re-run step appearing after plugin_version write in the SKILL.md.

### Pitfall 7: Forgetting to update the Notes section
**What goes wrong:** The SKILL.md still says "Q&A gap detection is handled by a separate future upgrade to this command" even though this phase implements it.
**Why it happens:** Copy-paste oversight -- the note was updated in Phase 20 to remove the merge reference but left the Q&A reference.
**How to avoid:** Remove or update the note in the `## Notes` section at the bottom of SKILL.md. The upgrade command now delivers the complete flow: version detection, config migration, file merge, Q&A gap detection, context refresh, and summary.
**Warning signs:** SKILL.md Notes section still references "future upgrade" for Q&A gap detection.

### Pitfall 8: Not persisting new Q&A answers before researcher re-run
**What goes wrong:** New Q&A answers are collected but not written to config.yaml before the researcher is spawned. The researcher reads config.yaml and does not see the new answers.
**Why it happens:** The answers are held in memory but the config.yaml write is deferred.
**How to avoid:** After all new Q&A questions are answered in the gap detection step, immediately write the new `qa_answers` entries to config.yaml. Then the researcher re-run reads the updated config.yaml.
**Warning signs:** Researcher invocation happening before qa_answers are written to config.yaml.

## Integration with Existing SKILL.md

The current upgrade SKILL.md (~280 lines) has a 4-step flow with the Notes section at the end. Phase 21 adds two new logical steps.

### Current Structure (After Phase 20)
```
Frontmatter (allowed-tools: Read, Write, Bash, Glob, Grep)
# Doc Writer Upgrade
## User Interaction Pattern
## Instructions
  ### Step 1: Version Detection
  ### Step 2: Config Format Migration
  ### Step 3: File Merge
    Section Parsing Rules
    Step 3.1: 2-way diff bootstrap (no .originals/)
    Step 3.2: Read doc_system
    Step 3.3: For each file (3-way merge)
  ### Step 4: Finalize
    Write plugin_version
    Display summary
## Notes
```

### Phase 21 Modification

```
Frontmatter (allowed-tools: Read, Write, Bash, Glob, Grep, Agent)  <-- ADD Agent
# Doc Writer Upgrade
## User Interaction Pattern
## Instructions
  ### Step 1: Version Detection (UNCHANGED)
  ### Step 2: Config Format Migration (UNCHANGED, but track changes_made flag)
  ### Step 3: File Merge (UNCHANGED)
  ### Step 3.5: Q&A Gap Detection (NEW -- QA-01)
    Read .qa.md from plugin defaults
    Skip if FALLBACK framework (.qa.md not in plugin defaults)
    Extract question headers, derive keys
    Compare against qa_answers in config.yaml
    Present new questions via AskUserQuestion
    Persist new answers to qa_answers in config.yaml
    Track whether new answers were collected
  ### Step 4: Context Refresh (NEW -- QA-02, conditional)
    IF Step 2 added config fields OR Step 3.5 collected new answers
    THEN spawn doc-researcher (same invocation as setup Step 5)
    ELSE skip
  ### Step 5: Finalize (RENUMBERED from Step 4, summary template updated)
    Write plugin_version (LAST write -- unchanged rule)
    Display summary with new sections for Q&A and context refresh
## Notes (UPDATED -- remove "future upgrade" reference)
```

### Step Numbering Decision

The current SKILL.md uses `### Step 1` through `### Step 4`. Phase 21 adds two steps. Options:

**Option A: Insert as Step 3.5 and Step 4, renumber old Step 4 to Step 5**
- Pro: Minimal disruption to existing step references
- Con: Step 3.5 is an unusual numbering

**Option B: Renumber to Steps 1-6**
- Pro: Clean sequential numbering
- Con: Every step reference in plans/summaries shifts

**Recommendation:** Option A (Step 3.5 for Q&A gap detection, then renumber only Finalize from Step 4 to Step 5, and insert Step 4 for Context Refresh). This keeps the merge between Step 3 and finalization, and Step 4 (Context Refresh) precedes Step 5 (Finalize). Alternatively, the planner can use Option B for cleaner numbering since this is the final phase and no future phases reference these step numbers.

### Frontmatter Update

The only frontmatter change is adding `Agent` to `allowed-tools`:

```yaml
---
name: doc-writer:upgrade
description: Upgrade doc-writer configuration after a plugin update. Detects version changes, migrates config fields, updates unchanged files, and reports all changes.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
argument-hint: ""
---
```

The `description` field could optionally be expanded to mention Q&A and context refresh, but this is at the planner's discretion.

### Summary Template Update

The Step 5 (Finalize) summary template needs new sections:

```
## Upgrade Summary

**Version:** {old_version} -> {new_version}

### Config Changes
- {existing format}

### File Updates
- {existing format}

### File Merges
- {existing format}

### Q&A Updates
- {list each new question asked with the answer given}
- {or "No new Q&A questions"}
- {or "Q&A gap detection skipped -- {doc_system} is not a built-in framework"}

### Context Refresh
- {context.md regenerated via researcher re-run}
- {or "Skipped -- no config or Q&A changes to reflect"}

### Warnings
- {existing format}
```

## Q&A File Analysis

### Built-In Frameworks and Their Questions

| Framework | Questions | Headers (Keys) |
|-----------|-----------|----------------|
| mkdocs-material | 3 | navigation, api_docs, features |
| sphinx-shibuya | 3 | navigation, api_docs, features |
| odoc | 3 + dynamic follow-ons | structure, scope, guides, {guide_type}_topics |
| plain-markdown | 3 | callouts, headings, toc |

### Key Derivation Examples

| Header Field | Derived Key |
|-------------|-------------|
| "Navigation" | `navigation` |
| "API docs" | `api_docs` |
| "Features" | `features` |
| "Structure" | `structure` |
| "Scope" | `scope` |
| "Guides" | `guides` |
| "Tutorial topics" | `tutorial_topics` |
| "How-to topics" | `how-to_topics` |
| "Callouts" | `callouts` |
| "Headings" | `headings` |
| "TOC" | `toc` |

Note: "How-to topics" derives to `how-to_topics` (hyphen preserved, only spaces become underscores). This matches the setup behavior since the rule only specifies "replace spaces with underscores" -- hyphens are untouched.

### Handling Dynamic Follow-On Questions (odoc)

The odoc `.qa.md` has a `### Follow-on: Sub-topic questions` section that generates dynamic follow-on questions based on the user's answer to Question 3 (Guides). For example, if the user selects "Getting started / Tutorial" and "How-to guides", follow-on questions are generated for tutorial topics and how-to topics.

**For Q&A gap detection:** The static questions (## Question 1/2/3) have predictable headers. The follow-on questions have headers derived from the user's prior answers. Detecting "new follow-on questions" would require knowing what the user selected for the parent question -- this is complex and fragile.

**Recommendation:** Q&A gap detection should only process `## Question N:` sections (static questions). Follow-on sub-topic questions are tied to their parent question's answer. If the parent question is already answered, the follow-ons were handled during that same setup session. If a new static question is added to `.qa.md`, it will be detected. If a new follow-on pattern is added, it would require a different detection mechanism that is out of scope for the current design.

## Code Examples

### Example 1: Q&A Gap Detection Step (for SKILL.md prose)

```markdown
### Step 3.5: Q&A Gap Detection

Detect whether the plugin has added new framework Q&A questions since the user last ran setup.

1. Read the `doc_system` value from config.yaml (already read in Step 1).

2. Check if `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.qa.md` exists.

   **If the file does not exist:** This is a FALLBACK framework (researcher-generated, not built-in). Q&A gap detection only applies to built-in frameworks with plugin-shipped Q&A files. Display: "Q&A gap detection skipped -- {doc_system} uses researcher-generated Q&A." Skip to Step 4. Record for summary.

3. Read the `.qa.md` file. Parse each `## Question N:` section (ignore `### Follow-on:` sub-sections). Extract the `header` field from each question.

4. For each question header, derive the expected qa_answers key: lowercase the header and replace spaces with underscores (e.g., "API docs" becomes `api_docs`).

5. Read the `qa_answers` section from config.yaml.

6. For each derived key: check if the key exists in `qa_answers`.
   - If the key exists: this question was already answered. Skip it.
   - If the key is absent: this is a new question. Add to the list of questions to ask.

7. **If no new questions found:** Record "No new Q&A questions" for summary. Skip to Step 4.

8. **If new questions found:**
   a. Display: "The plugin update includes {N} new framework question(s) for {doc_system}."
   b. For each new question, present it via AskUserQuestion using the question's header, question text, and options from the `.qa.md` file (same format as setup Step 2b.5).
   c. After all new questions are answered, persist the answers to config.yaml under `qa_answers` using the derived key for each answer. Write config.yaml now (before the researcher re-run reads it).
   d. Record for summary: "Asked {N} new Q&A question(s): {list of question headers}"
```

### Example 2: Conditional Researcher Re-Run (for SKILL.md prose)

```markdown
### Step 4: Context Refresh

Regenerate `context.md` if the upgrade produced changes that downstream agents should reflect.

1. Determine if a context refresh is needed:
   - Did Step 2 add any new config fields? (If yes, refresh needed.)
   - Did Step 3.5 collect any new Q&A answers? (If yes, refresh needed.)

2. **If no refresh needed:** Record "Context refresh skipped -- no config or Q&A changes" for summary. Skip to Step 5.

3. **If refresh needed:**
   a. Display: "Refreshing context.md to reflect updated configuration..."
   b. Use the Agent tool to spawn `doc-researcher` with this message:

   > Enrich the project configuration. Read `.doc-writer/config.yaml` for user personas, tone, and doc system. Scan the codebase (README, source files, framework config) and produce `.doc-writer/context.md` with expanded persona guidance, project domain summary, tone-specific writing rules, and framework usage preferences.
   >
   > Framework Q&A answers: {all qa_answers from config.yaml}

   c. After the researcher completes, record for summary: "context.md regenerated via researcher re-run"
```

### Example 3: Frontmatter Update

```yaml
---
name: doc-writer:upgrade
description: Upgrade doc-writer configuration after a plugin update. Detects version changes, migrates config fields, updates unchanged files, and reports all changes.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
argument-hint: ""
---
```

### Example 4: Setup Step 2b.5 Framework Q&A Pattern (reference for reuse)

```markdown
# Source: doc-writer/skills/setup/SKILL.md lines 428-447

1. Check for Q&A data file:
   - Use Glob to check if `{framework_root}/{doc_system}.qa.md` exists.
   - If found: Read the file. Parse the `## Question N:` sections.
   - If NOT found: Skip framework Q&A.

3. Present each question from the .qa.md file as an AskUserQuestion:
   - Use the `header`, `question`, and `options` fields from each `## Question` section.
   - If the question has `multiSelect: true`, set multiSelect on the AskUserQuestion.
   - Every question MUST have "Type something else" and "Chat about this" as trailing options.

4. Record all answers. Derive the key by lowercasing the question's `header` field and replacing spaces with underscores. Store the selected label as the value.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No Q&A persistence | `qa_answers` in config.yaml | Phase 18 (v1.5.0) | Enables gap detection by storing what was answered |
| No Q&A gap detection during upgrade | Detect new questions, ask only those | Phase 21 (this phase) | Users are not re-asked existing questions; only new plugin questions appear |
| No researcher re-run during upgrade | Conditional re-run after config/Q&A changes | Phase 21 (this phase) | context.md stays current after upgrade changes |
| "Q&A gap detection is handled by a separate future upgrade" | Complete upgrade flow | Phase 21 (this phase) | Upgrade command delivers the full experience |

## Open Questions

1. **Should the upgrade detect feature changes in framework config for recommend_if?**
   - What we know: Setup's Step 2b.5 uses `detect_context` and `recommend_if` to pre-select recommended options based on the framework config file (e.g., detecting `navigation.tabs` in mkdocs.yml). The upgrade's Q&A gap detection could do the same for new questions.
   - What's unclear: Whether this detection adds value during upgrade (the user already has a framework config) or is unnecessary complexity.
   - Recommendation: Include detection for consistency with setup. The detection code is simple (Grep on the config file) and gives the user context-aware defaults for new questions. The `.qa.md` already has `detect_context` and `recommend_if` fields -- the upgrade should honor them.

2. **Should context refresh also trigger for file merge changes?**
   - What we know: The design decision says "re-run only triggers when there are actual changes (new Q&A answers OR config field changes in Step 2)." File merge changes (Step 3) are not mentioned.
   - What's unclear: Whether file merge changes (e.g., updated guidance file content) affect what the researcher should produce in context.md.
   - Recommendation: Follow the design decision as stated. File merges change guidance/rules files that are consumed directly by agents, not through context.md. The researcher reads config.yaml, not guidance files. Only config and Q&A changes warrant a re-run.

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
| QA-01 | Only new Q&A questions asked during upgrade | manual-only | Add a new question to a `.qa.md` file, run `/doc-writer:upgrade`, verify only the new question is presented | N/A |
| QA-02 | context.md refreshed after config/Q&A changes | manual-only | Run `/doc-writer:upgrade` after adding a new config field or Q&A question, verify context.md is regenerated | N/A |

**Justification for manual-only:** Same as Phases 19-20 -- the deliverable is a markdown instruction file. The "test" is Claude interpreting the SKILL.md and performing the Q&A gap detection and researcher re-run correctly.

### Sampling Rate
- **Per task commit:** Content review of SKILL.md changes
- **Per wave merge:** N/A
- **Phase gate:** Manual run of `/doc-writer:upgrade` against a test project with a modified `.qa.md` file

### Wave 0 Gaps
None -- no test infrastructure needed.

## Sources

### Primary (HIGH confidence)
- `doc-writer/skills/upgrade/SKILL.md` -- ~280 lines, current upgrade flow that Phase 21 extends (read in full)
- `doc-writer/skills/setup/SKILL.md` -- 591 lines, canonical Q&A presentation pattern (Step 2b.5 lines 427-447), Agent/researcher invocation (Step 5 lines 550-579)
- `doc-writer/skills/setup/defaults/mkdocs-material.qa.md` -- Q&A question format with 3 questions, headers: Navigation, API docs, Features
- `doc-writer/skills/setup/defaults/odoc.qa.md` -- Q&A question format with 3 questions + dynamic follow-ons, headers: Structure, Scope, Guides
- `doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md` -- Q&A question format with 3 questions, headers: Navigation, API docs, Features
- `doc-writer/skills/setup/defaults/plain-markdown.qa.md` -- Q&A question format with 3 questions, headers: Callouts, Headings, TOC
- `doc-writer/skills/setup/defaults/config-template.yaml` -- qa_answers structure (empty `{}` in template)
- `doc-writer/agents/doc-researcher.md` -- 412 lines, researcher agent definition showing enrichment mode invocation
- `.planning/REQUIREMENTS.md` -- QA-01 and QA-02 acceptance criteria
- `.planning/ROADMAP.md` -- Phase 21 success criteria
- `.planning/phases/19-upgrade-skill/19-RESEARCH.md` -- Phase 19 patterns and conventions (skill authoring reference)
- `.planning/phases/20-3-way-merge/20-RESEARCH.md` -- Phase 20 patterns (SKILL.md modification approach)
- `.planning/STATE.md` -- accumulated decisions including qa_answers design and FALLBACK handling

### Secondary (MEDIUM confidence)
None needed -- all findings from reading existing codebase.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- fully constrained by Claude Code plugin format, no choices to make
- Architecture: HIGH -- Q&A gap detection is a simple set difference; researcher re-run reuses existing setup pattern; all integration points are well-understood from prior phases
- Pitfalls: HIGH -- derived from careful analysis of the Q&A file structures, key derivation rules, FALLBACK edge case, and dynamic follow-on handling

**Research date:** 2026-03-26
**Valid until:** Indefinite -- internal project architecture, not external library versions
