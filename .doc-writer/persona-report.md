# Persona Report

**Generated:** 2026-03-16
**Audience:** Paul — solo developer building projects with Claude Code and open source libraries (expert)
**Scenarios tested:** 5
**Results:** 3 PASS, 2 PARTIAL, 0 FAIL

## Summary

The documentation handles the common happy-path workflows (install, first run, focused reviews, adding rules) well for an expert user. The copilot-review docs in particular are thorough and well-structured. The main friction points are around the doc-writer audit workflow: when Paul edits docs manually and wants persona-only validation, the available command (`/doc-writer:review`) also runs the Editor and applies changes to his files — a behaviour that is disclosed but not prominently flagged as a warning. Additionally, the rules.md reference does not explicitly state when new rules take effect, which the audience's `never_assume` configuration requires to be spelled out.

---

## Scenario S1: Install both plugins and get doc-writer running on a new project

**Verdict:** PASS

### Navigation Path

1. Started at: `README.md`
   - Found: Install command `/plugin install github:anentropic/for-agents`, descriptions of both plugins, link to `docs/doc-writer.md`
   - Followed: Link to `docs/doc-writer.md`
2. Navigated to: `docs/doc-writer.md`
   - Found: Tutorial "Document a project from scratch" — sequential steps with commands, expected output samples, and a clear explanation of what each step does
   - Step 1 (`/doc-writer:setup`) and Step 2 (`/doc-writer:write`) are clearly ordered with example output shown
   - No friction: the flow from README install to tutorial first-run is unbroken

---

## Scenario S2: Re-run only persona validation after manually editing a doc page, without regenerating

**Verdict:** PARTIAL

### Navigation Path

1. Started at: `README.md`
   - Found: Link to `docs/doc-writer.md`
   - Followed: Link to `docs/doc-writer.md`
2. Navigated to: `docs/doc-writer.md`
   - Found: How-to guide "How to audit documentation without regenerating" — describes `/doc-writer:review`
   - Command description: runs Gap Detection → Editor (applies fixes) → Persona
   - The how-to opens with "Runs gap detection, Editor quality checks, and Persona validation against existing docs. Does not create new pages." — the phrase "does not create new pages" could be read as "safe for manual edits"
   - A note at the bottom of the how-to clarifies: "The Editor applies fixes directly to docs during the review." But this appears after the command description, formatted as a callout note rather than a prominent warning
   - No command exists for Persona-only evaluation

### Gap Analysis

**Where:** `docs/doc-writer.md` > "How to audit documentation without regenerating"

**What:** The how-to does not prominently warn that the Editor modifies documentation files as part of `/doc-writer:review`, which means a user who has manually edited docs and wants validation-only will have their edits potentially altered by the Editor pass. The disclosure exists but is positioned as an explanatory aside ("by design") rather than as a decision-relevant warning ("your files will be changed"). There is also no "persona-only" command option documented.

**Impact:** Paul edits a doc page manually, runs `/doc-writer:review` expecting validation-only, and finds the Editor has rewritten sections of his manual work. The information to anticipate this exists but requires reading to the end of the how-to section.

**Suggested Fix:** In `docs/doc-writer.md`, section "How to audit documentation without regenerating": move the Editor-applies-fixes disclosure to the top of the how-to (before the command), and reframe it as a decision point — e.g., "Note: This command applies Editor fixes to your doc files. If you have unsaved manual edits you want to preserve, commit them first." This surfaces the behaviour where the user can act on it.

---

## Scenario S3: Understand what the 'wheels' dimension checks for and whether it applies to AI-generated code

**Verdict:** PASS

### Navigation Path

1. Started at: `README.md`
   - Found: Link to `docs/copilot-review.md`
   - Followed: Link to `docs/copilot-review.md`
2. Navigated to: `docs/copilot-review.md`
   - Found: Reference > Review dimensions table — `wheels` row describes "Hand-rolled implementations that duplicate well-known libraries; especially common in AI-generated code"
   - Found: "How the review works" > "What counts as a 'reinvented wheel'" — explicitly names AI code generation patterns as the motivation, lists concrete examples (retry logic, HTTP client wrapper, argument parser, config file loader), and specifies the threshold for not flagging (utility functions under ~20 lines)
   - Found: "What copilot-review does not flag" — clarifies scope boundaries
   - The AI-generated code angle is called out in both the table row and the dedicated explanation section

---

## Scenario S4: Add a project-specific rule requiring error handling in code examples, and know when it takes effect

**Verdict:** PARTIAL

### Navigation Path

1. Started at: `README.md`
   - Found: Link to `docs/doc-writer.md`
   - Followed: Link to `docs/doc-writer.md`
2. Navigated to: `docs/doc-writer.md`
   - Found: How-to "How to set up doc-writer for a project" — mentions editing `.doc-writer/rules.md` after setup, with the exact example "Code examples must show error handling, not just the happy path"
   - Found: Reference > `.doc-writer/rules.md` — explains the file's purpose, confirms it is additive to universal rules, shows an example block with the error-handling rule verbatim
   - What to edit and the format: fully clear
   - When the rule takes effect: the reference section says "agents interpret them directly" and the `config.yaml` reference says it is "Read by all pipeline commands at startup" — but this `at startup` phrasing applies to `config.yaml`, not explicitly to `rules.md`
   - No statement in the `rules.md` reference explicitly says "agents read this file at the start of each pipeline run" or "changes take effect the next time you run any command"

### Gap Analysis

**Where:** `docs/doc-writer.md` > Reference > `.doc-writer/rules.md`

**What:** The reference describes what the file does and how to write rules, but does not state when agents pick up changes. The audience's `never_assume` configuration requires that "the expected workflow" always be explained. An expert user can infer that the file is read at runtime based on context, but this crosses into assumption territory per the configured audience.

**Impact:** Minor friction. Paul edits the file and is left wondering whether he needs to re-run setup or whether it applies immediately on the next pipeline run. He would likely infer correctly, but the docs require him to infer rather than stating it.

**Suggested Fix:** In `docs/doc-writer.md`, section Reference > `.doc-writer/rules.md`: add one sentence explicitly stating when the rule applies — e.g., "Agents read this file at the start of each pipeline run; changes take effect immediately on the next `/doc-writer:write`, `/doc-writer:review`, or `/doc-writer:edit` invocation."

---

## Scenario S5: Run a focused copilot-review on src/auth/ for architecture and errors only, using a faster model

**Verdict:** PASS

### Navigation Path

1. Started at: `README.md`
   - Found: Link to `docs/copilot-review.md`
   - Followed: Link to `docs/copilot-review.md`
2. Navigated to: `docs/copilot-review.md`
   - Found: Three separate how-to guides covering exactly the three dimensions of this goal
   - "How to review a specific path": path argument pattern clear, with single-file example
   - "How to filter to specific dimensions": `--focus architecture,errors` shown directly, dimension IDs listed
   - "How to tune model and reasoning": `--reasoning medium` and `--model` flag both documented
   - Found: Combined example demonstrating all flags together: `/copilot-review src/ --focus quality,errors --model gpt-4.1 --reasoning medium`
   - Paul can directly construct: `/copilot-review src/auth/ --focus architecture,errors --reasoning medium`

---

## Revision Recommendations

### FAIL Issues (trigger revision)

No FAIL issues. No revision pass required.

### PARTIAL Issues (for project author approval)

| Scenario | Page | Gap | Suggested Fix |
|----------|------|-----|---------------|
| S2 | `docs/doc-writer.md` > "How to audit documentation without regenerating" | Editor modifies files during `/doc-writer:review` — disclosure exists but is positioned as a footnote rather than an upfront decision point. No persona-only option is documented. | Move the Editor-applies-fixes disclosure to the top of the how-to section, before the command. Reframe as a decision-relevant warning: tell the user to commit manual edits first if they want to preserve them. |
| S4 | `docs/doc-writer.md` > Reference > `.doc-writer/rules.md` | No explicit statement of when rule changes take effect. Audience `never_assume` config requires workflows to be spelled out. | Add one sentence stating that agents read `rules.md` at the start of each pipeline run and that changes take effect immediately on the next invocation. |
