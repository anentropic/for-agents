---
name: doc-writer:review
description: Audit documentation quality and coverage. Finds undocumented symbols, tests user journeys, and reports issues. Use --edit to apply quality fixes.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--edit]"
---

# Doc Writer Review

Audit existing documentation without regenerating content. Runs gap detection, Editor quality checks, and Persona validation, then presents a combined report.

**Default behaviour:** the Editor audits and reports issues but does NOT edit doc files.
Pass `--edit` to apply Editor fixes (with a confirmation gate before any files are changed).

## Instructions

Follow these steps in order. Complete each step before moving to the next.

### User Interaction Pattern

This skill uses AskUserQuestion for structured choices. When the user selects:
- **"Type something else"** or **"Other"**: Ask your follow-up as plain text. Wait for their response. Then resume the workflow.
- **"Chat about this"**: Explain the current decision in depth. Open a plain-text dialogue. After it resolves, re-present the original question or proceed based on what was discussed.

Never respond to these selections with another AskUserQuestion.

### Pre-Flight

1. Check whether `` contains `--edit`. Store as boolean `edit_mode`.

2. Use Read to load `.doc-writer/config.yaml`.
   - **If missing:** Tell the user: "No doc-writer configuration found. Run `/doc-writer:setup` first to configure your project." Stop.

3. Extract from config:
   - `user_personas` array (each entry has `name`, `skill_level`)
   - `detected.language` (e.g., `typescript`, `python`)
   - `paths.docs_root` (e.g., `docs/`)
   - `paths.source_root` (e.g., `src/`)

4. Use Glob to check that documentation files exist in `{paths.docs_root}`:
   - Pattern: `{paths.docs_root}/**/*.md`
   - **If no docs found:** Tell the user: "No documentation files found in `{paths.docs_root}`. Run `/doc-writer:write` to generate docs, or update `paths.docs_root` in `.doc-writer/config.yaml` to point to your existing docs directory." Stop.

### Step 1: Gap Detection

Identify exported symbols in the codebase that are not covered by existing documentation.

1. Run gap detection using Bash:
   ```
   bash ${CLAUDE_PLUGIN_ROOT}/skills/write/scripts/scan-exports.sh {paths.source_root} {detected.language}
   ```
   This script outputs a list of exported symbols from the source code.

2. Read the script output to get the list of exported symbols.

3. Read all documentation files in `{paths.docs_root}` and scan their content to identify which exported symbols are mentioned or documented.

4. Compile the gap -- symbols that are exported but not referenced in any documentation file.

5. Write the gap report to `.doc-writer/gap-report.md` with this structure:
   ```markdown
   # Gap Detection Report

   **Source root:** {paths.source_root}
   **Language:** {detected.language}
   **Total exported symbols:** {count}
   **Documented symbols:** {count}
   **Undocumented symbols:** {count}

   ## Undocumented Exports

   | Symbol | File | Type |
   |--------|------|------|
   | {name} | {source_file} | {function/class/const/type} |

   ## Notes

   {any observations about coverage patterns}
   ```

### Step 2: Editor Audit

Spawn the doc-editor agent to review documentation quality.

**If `edit_mode` is false (default):**

Use the Agent tool to spawn `doc-editor` with this delegation message:

> Audit the documentation in {paths.docs_root}. Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking. **Report issues only — do NOT edit any doc files.** Write your findings to .doc-writer/editor-report.md. Prose scanner: `${CLAUDE_PLUGIN_ROOT}/deslop/docs_scan.py`.

**If `edit_mode` is true (`--edit` flag was passed):**

Before spawning the Editor, confirm with the user.

Use AskUserQuestion to confirm:
- header: "Edit mode"
- question: "The Editor will rewrite docs directly. Files: {list files in paths.docs_root}. Manual edits may be overwritten."
- options:
  - { label: "Apply edits", description: "Let the Editor fix issues in doc files" }
  - { label: "Report only", description: "Skip editing, just show findings" }
  - { label: "Type something else", description: "Specify which files to edit" }
  - { label: "Chat about this", description: "Discuss what the Editor will change" }

**Handling responses:**
- **"Apply edits":** Spawn the Editor with the standard editing delegation below.
- **"Report only":** Skip the Editor entirely. Note "Editor skipped (user declined)" in the final report. Proceed to Step 3.
- **"Type something else":** Ask the user in plain text what files to scope. Wait for response. Then spawn the Editor with the standard editing delegation, scoped to the user's specified files.
- **"Chat about this":** Explain what the Editor will change (four passes: terminology, Diataxis type integrity, humanizer, cross-references). Answer questions in plain text. After discussion resolves, re-present the AskUserQuestion to get a decision.
- **"Other" (auto-added):** Ask the user in plain text what they want to do. Wait for response. Proceed based on their answer.

Standard editing delegation (only used when user confirms):

> Review the documentation in {paths.docs_root}. Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking. Edit doc files to fix issues as you find them. Write your report to .doc-writer/editor-report.md. Prose scanner: `${CLAUDE_PLUGIN_ROOT}/deslop/docs_scan.py`.

Wait for the Editor agent to complete before proceeding.

### Step 3: Persona Evaluation

For each persona in `config.user_personas`, spawn a doc-user-tester agent to evaluate the documentation from that persona's perspective.

For each persona entry:

Use the Agent tool to spawn `doc-user-tester` with this delegation message:

> Evaluate documentation as the '{persona.name}' persona. Read the docs in {paths.docs_root} and run your full three-phase workflow: generate scenarios, simulate user journeys, and produce your report. Write your report to .doc-writer/persona-report-{persona_name_slug}.md.

Where `{persona_name_slug}` is the persona name lowercased with spaces replaced by hyphens.

If there is only one persona, also write to `.doc-writer/persona-report.md` for compatibility.

Wait for all Persona agents to complete before proceeding.

### Step 4: Present Results

Read the generated reports and present a combined audit summary to the project author.

1. Read `.doc-writer/gap-report.md`.
2. Read `.doc-writer/editor-report.md`.
3. Read all `.doc-writer/persona-report*.md` files.

Present the summary in this format:

```
## Documentation Audit Summary

### Gap Detection
- **Total exported symbols:** {count}
- **Documented:** {count} ({percent}%)
- **Undocumented:** {count}
- Key undocumented symbols: {top 5 symbol names}

### Editor Findings
- **BLOCKING issues:** {count}
- **SUGGESTION issues:** {count}
- **NITPICK issues:** {count}
- Top issues: {brief list of most important findings}

Note: {If edit_mode is true and user confirmed: "The Editor has applied fixes to docs." | If edit_mode is true and user declined: "Editor was skipped (user declined confirmation)." | If edit_mode is false: "Editor ran in report-only mode. Run `/doc-writer:review --edit` to apply fixes."}

### Persona Verdicts

**{persona_name}** ({skill_level}):
| Scenario | Verdict | Notes |
|----------|---------|-------|
| {goal}   | {PASS/PARTIAL/FAIL} | {brief note} |

{repeat for each persona}

### Overall Assessment
{1-2 sentence summary of documentation health}

---

**Next steps:**
- Run `/doc-writer:edit` to fix specific issues from the reports above
- Run `/doc-writer:write` for a full documentation regeneration
```

## Constraints

- Do NOT use `context: fork` when spawning agents.
- Do NOT commit any changes -- this is an audit operation.
- Do NOT run a revision loop -- the review is purely informational.
- By default, the Editor MUST NOT edit doc files. It reports issues only.
- The `--edit` flag enables Editor edits, but ONLY after explicit user confirmation.
- Present results to the project author and stop. No approval gates or iterative flows beyond the `--edit` confirmation gate.
