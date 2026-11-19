# Editor Report

**Generated:** 2026-11-19
**Files reviewed:** 16
**Changes made:** 27
  - BLOCKING: 4
  - SUGGESTION: 20
  - NITPICK: 3

## Summary

The docs were accurate, well structured by Diataxis type, and close to the source. Four accuracy mismatches were fixed. Prose edits were light, mostly wh-headings, meta openings and a few Claude-typical constructions. The `npx skills` note was removed at the project author's request, and all Author notes were stripped.

---

## docs/src/index.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Plugins > doc-writer | Agent names used generic forms ("an Author", "an Editor", "a Persona") | Normalized to Doc Author, Doc Editor, Doc Persona |
| Installation | `!!! note "Installing with npx skills"` removed at the project author's request | Deleted the admonition; no other `npx skills` mention exists in docs/src |

### NITPICK

| Section | Description | Fix |
|---------|-------------|-----|
| (end of page) | Author's internal notes comment | Removed |

---

## docs/src/doc-writer/index.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| What makes it different | Wh-heading | Renamed to "Differences from prompting Claude directly" |
| Differences list | Filler tail "along the way" | Removed |

---

## docs/src/doc-writer/tutorial.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Step 2 > Doc system and framework questions | Type blur toward how-to: the API docs answer offered an alternative ("or mkdocstrings if...") | Tutorial now makes the decision: **None** |

---

## docs/src/doc-writer/how-to/update-docs.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Read the gap report | Accuracy mismatch: doc said that with empty gap lists the pipeline "runs only the Doc Editor". write/SKILL.md Step 2a skips Steps 2a-2c and goes to Step 3, then Step 4 (Persona) still runs | Now says it skips the Doc Author and runs the Doc Editor over all existing pages before the Doc Persona evaluates them |

---

## docs/src/doc-writer/how-to/configure.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Change one area | Accuracy mismatch: **Done** was described as "Ends the session". setup/SKILL.md: "Done: Stop. Display current config summary." (ends setup, not the Claude Code session) | "Ends setup and prints the current configuration" |

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Opening | Meta reference "This guide covers" | Rewritten as the reader's three options |
| Change one area | "keeps every other field as it was, then asks whether" | Tightened |

Accuracy check (Author asked to verify): the "Re-run the researcher" warning is correct. Step 4 handlers write config only, and the researcher runs only on first-time setup, `--reset`, `--refresh-context` and **Re-run researcher**.

---

## docs/src/doc-writer/how-to/resolve-verdicts.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Choose which PARTIAL fixes to apply | Accuracy mismatch: **Type something else** was described as applied "in place of or alongside the suggestions". write/SKILL.md Step 6 labels it "Describe additional changes" and applies them directly | "describe additional changes, which are applied directly to the pages" |

---

## docs/src/doc-writer/how-to/upgrade.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Troubleshooting > already up to date | Inconsistent with the verified install guidance: said "Start a new session", while the update step (verified against the CLI) says to restart Claude Code | "Restart Claude Code and run the command again" |

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| 1. Config migration | Claude tell "rather than an empty default" | ", not an empty default" |

Update commands (`claude plugin marketplace update`, `claude plugin update`) kept as written.

---

## docs/src/doc-writer/how-to/targeted-fixes.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| What runs | Wh-heading | Renamed to "Stages of an edit run" |
| Stages | Vague reference "others" | "other pages" |
| Describe the fix yourself | "is not a number selection is used as" | "other than a number selection becomes" |

---

## docs/src/doc-writer/how-to/audit.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Apply the Editor's fixes | Intensifier "entirely" | Removed |

---

## docs/src/doc-writer/explanation/pipeline.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Opening | Repeated "its own" stack | Split into two sentences |
| A write run | Inanimate agent ("agents themselves cannot ask") | States the mechanism: the command starts each agent and handles every question |
| Why separate agents | Wh-heading | Renamed to "Separate agents" |
| Separate agents | "structural rather than a matter of instructions", "rather than turning into a second draft", "knows things" | Rewritten plainly |
| Create mode and update mode | Summary closer "That keeps a docs set..." | Folded into the preceding sentence |
| The revision loop | Long "whether that friction is worth fixing" sentence | Split and shortened |

---

## docs/src/doc-writer/explanation/personas.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Headings | Four wh-headings | Renamed: Personas; Navigating the docs as a reader; Verdicts; PARTIAL verdicts wait for you |
| Navigating the docs | Staged line "These limits are the point." | Removed |
| PARTIAL verdicts wait for you | Repetitive "friction" phrasing | Tightened |

---

## docs/src/doc-writer/explanation/quality.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Universal rules and project rules | "That keeps the baseline... while letting" | Rewritten plainly |
| The humanizer pass | Intensifier "deliberately" | Removed |

The deslop credit to its author is kept. It is the MIT attribution the vendored license requires, not an example name.

---

## docs/src/doc-writer/reference/configuration.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| qa_answers | Inanimate agent ("`scope` decides") | "the `scope` answer sets whether..." |

---

## docs/src/doc-writer/reference/files.md

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Opening | Vague reference "others" | "most other files" |

---

## All pages

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Cross-references | No API reference detected (`api_reference` empty, no mkdocstrings). doc-writer has no code API | Cross-reference linking skipped; internal links and anchors checked by `mkdocs build --strict` |

### NITPICK

| Section | Description | Fix |
|---------|-------------|-----|
| (end of page) | Author's internal notes comment | Removed from all 16 pages |
| Em dashes | One em dash left in update-docs.md | It is inside a code block quoting the skill's real output, so it stays |

---

## Terminology Changes

| Term | Before | After | Authority |
|------|--------|-------|-----------|
| Doc Author / Doc Editor / Doc Persona | Author, Editor, Persona (front page, generic articles) | Doc Author, Doc Editor, Doc Persona | terminology.yaml project_terms |

`terminology.yaml` now also lists the command names, Claude Code, MkDocs Material, Doc Researcher, and the project's multi-word concept names (page inventory, type blur, gap report, create mode, update mode, revision pass, docs root, and others) as protected terms.

## Humanizer Measurements

| Page | Likeness before | Likeness after | Fixed | Left on purpose |
|------|-----------------|----------------|-------|-----------------|
| index.md | 0.44 | 0.44 | — | none flagged |
| doc-writer/index.md | 0.53 | 0.53 | wording | "How-to guides" heading (Diataxis section name); bold link list (section index format) |
| doc-writer/tutorial.md | 0.37 | 0.37 | — | none flagged |
| explanation/personas.md | 0.8 | 0.69 | wh_headings | "friction" (defined verdict term); triads that list real items |
| explanation/pipeline.md | 0.86 | 0.64 | inanimate_agents, sentence_shape | H1 matches the nav label; bold agent names (inline-header list) |
| explanation/quality.md | 0.66 | 0.53 | wording | quoted pattern examples ("plays a crucial role") |
| how-to/audit.md | 0.71 | 0.64 | wording | bold option names |
| how-to/configure.md | 0.84 | 0.77 | meta_reference | menu-option table and bold labels |
| how-to/project-rules.md | 0.32 | 0.32 | — | none flagged |
| how-to/resolve-verdicts.md | 0.46 | 0.46 | — | none flagged |
| how-to/targeted-fixes.md | 0.87 | 0.88 | vague_references, wh_headings | "argument" (the command's real term) |
| how-to/update-docs.md | 0.37 | 0.37 | — | none flagged |
| how-to/upgrade.md | 0.74 | 0.52 | wording | short imperative steps |
| reference/commands.md | 0.3 | 0.3 | — | none flagged |
| reference/configuration.md | 0.77 | 0.77 | inanimate_agents | terse reference fragments ("Always a list...") |
| reference/files.md | 0.58 | 0.57 | vague_references | — |
