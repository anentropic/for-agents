# Editor Report

**Generated:** 2026-03-16
**Files reviewed:** 3 (README.md, docs/doc-writer.md, docs/copilot-review.md)
**Changes made:** 12
  - BLOCKING: 2
  - SUGGESTION: 3
  - NITPICK: 7

## Summary

Both documentation files are well-structured and largely clean. Two accuracy mismatches with source required correction: a stage count error in doc-writer.md and mismatched severity labels in copilot-review.md. Prose em dashes were the most prevalent style issue, appearing in seven locations across the two files.

---

## Pre-Processing: Accuracy Verification

### docs/doc-writer.md

Source references were found at `/Users/paul/.claude/plugins/cache/doc-writer-plugins/doc-writer/1.0.0/`. The referenced doc-writer source files exist at that location.

### docs/copilot-review.md

`copilot-review/SKILL.md` was found at `/Users/paul/Documents/Dev/Personal/for-agents/copilot-review/SKILL.md`. `copilot-review/references/review-prompts.md` was also found.

**Note:** The `src/` source root specified in config does not exist. No symbols were available for gap detection. The Author's note that "No API reference is configured" is confirmed by `api_reference: ""` in config.

---

## README.md

No changes made. The file is clean and accurate.

---

## docs/doc-writer.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Tutorial: Step 2 | Accuracy mismatch: doc said "The pipeline runs three stages automatically" but write/SKILL.md defines four distinct stages (Gap Detection, Author, Editor, Persona). The numbered list immediately following also lists four items. | Changed "three stages" to "four stages". |

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| How to make targeted fixes | Em dash in running prose: "from a previous review or review report — faster than regenerating all pages." Not an inline-header list context. | Replaced em dash with comma: "from a previous review or review report, faster than regenerating all pages." |
| Configuration files: `.doc-writer/rules.md` | Em dash in running prose: "Edit directly — no special syntax required". | Replaced em dash with semicolon: "Edit directly; no special syntax required". |
| How the pipeline works: Why three agents | Em dash in running prose: "writes from the builder's viewpoint — referencing implementation details". | Replaced em dash with comma: "writes from the builder's viewpoint, referencing implementation details". |

### NITPICK

| Section | Description | Fix |
|---------|-------------|-----|
| Reference: persona-report.md | Em dash in table cell: "User cannot accomplish the goal — required information is missing". | Replaced em dash with comma: "User cannot accomplish the goal, required information is missing or critically wrong." |
| How to audit: Note callout | Em dash in prose: "this is by design — the review command's value is the Persona verdicts". | Replaced em dash with semicolon: "this is by design; the review command's value is the Persona verdicts on top of already-edited pages". |
| Internal notes | Stripped `<!-- INTERNAL NOTES FOR EDITOR -->` comment block (212 lines). | Removed. |

---

## docs/copilot-review.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Tutorial Step 2 + Reference: Issue format | Accuracy mismatch: doc showed severity labels `Critical \| High \| Medium` and tutorial example showed `**Severity**: High`. The SKILL.md Step 5 (CONSOLIDATE & RATE) specifies Claude re-rates all issues to `Critical / Major / Minor` in the consolidated output. The raw Copilot sub-review prompts use `Critical \| High \| Medium` internally, but the consolidated output (which is what users see) uses `Critical / Major / Minor`. | Changed tutorial example from `**Severity**: High` to `**Severity**: Major`. Changed tutorial body text from "sorted by severity (Critical → High → Medium)" to "sorted by severity (Critical → Major → Minor)". Changed tutorial Step 3 from "Issues marked Medium are worth noting" to "Issues marked Minor are worth noting". Changed Reference issue format from `**Severity**: Critical \| High \| Medium` to `**Severity**: Critical \| Major \| Minor`. |

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Page description (line 3) | Term inconsistency: copilot-review.md described itself as "A Claude Code skill" while README.md groups it under "## Plugins" and doc-writer.md describes itself as "A Claude Code plugin". The install mechanism is `/plugin install`. | Changed "A Claude Code skill" to "A Claude Code plugin". Added to terminology.yaml. |

### NITPICK

| Section | Description | Fix |
|---------|-------------|-----|
| How the review works: reinvented wheel | Em dash in prose: "a bespoke config file loader — all of which have well-maintained library equivalents." | Replaced em dash with comma: "a bespoke config file loader, all of which have well-maintained library equivalents." |
| Internal notes | Stripped `<!-- INTERNAL NOTES FOR EDITOR -->` comment block (26 lines). | Removed. |

---

## Pass 4: Cross-Reference Linking

Skipped. `api_reference` is empty in `.doc-writer/config.yaml`. No API reference location is configured or detected in the project.

> **Note for Author:** No API reference is configured. Cross-reference linking cannot run until an API reference is generated (typedoc, pdoc, mkdocstrings, or similar) and the path is set in `api_reference` in `.doc-writer/config.yaml`.

---

## Terminology Changes

| Term | Before | After | Authority |
|------|--------|-------|-----------|
| plugin vs. skill | "A Claude Code skill" (copilot-review.md line 3) | "A Claude Code plugin" | README.md groups both as plugins; `/plugin install` is the install mechanism; doc-writer.md uses "plugin" |
