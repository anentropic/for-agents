---
name: doc-writer:edit
description: Fix specific documentation issues from report findings or freeform instructions. Targeted changes only — no full pipeline.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep
argument-hint: "[issue description or page path]"
---

# Doc Writer Edit

Make targeted fixes to documentation. Select specific issues from existing review reports or describe changes freeform. Only the affected pages are modified -- no full regeneration.

## User Interaction Pattern

This skill uses AskUserQuestion for structured choices. When the user selects:
- **"Type something else"** or **"Other"**: Ask your follow-up as plain text. Wait for their response. Then resume the workflow.
- **"Chat about this"**: Explain the current decision in depth. Open a plain-text dialogue. After it resolves, re-present the original question or proceed based on what was discussed.

Never respond to these selections with another AskUserQuestion.

## Instructions

Follow these steps in order. Complete each step before moving to the next.

### Pre-Flight

1. Use Read to load `.doc-writer/config.yaml`.
   - **If missing:** Tell the user: "No doc-writer configuration found. Run `/doc-writer:setup` first to configure your project." Stop.

2. Extract from config:
   - `user_personas` array
   - `paths.docs_root`
   - `paths.source_root`

### Step 1: Collect Available Issues

Gather issues from existing reports and present them for selection.

1. Use Glob to check for report files:
   - `.doc-writer/editor-report.md`
   - `.doc-writer/persona-report.md`
   - `.doc-writer/persona-report-*.md`

2. **If NO report files exist:**

   Present this message:
   ```
   No editor or persona reports found. Run `/doc-writer:review` first to generate
   an issues report, or describe your changes below.
   ```
   Skip to freeform-only mode (proceed directly to Step 1b).

3. **If report files exist:**

   Read each report file and parse the issues. Present them using AskUserQuestion:
   - header: "Issues"
   - question: "Select issues to fix from previous reports."
   - multiSelect: true
   - options: [dynamically generated from report issues, ordered: BLOCKING first, then FAIL, then SUGGESTION, then PARTIAL, then NITPICK:]
     - { label: "[BLOCKING] {page} > {section}", description: "{description}" }
     - { label: "[FAIL] {page}", description: "{scenario_goal} -- {gap_description}" }
     - { label: "[SUGGESTION] {page} > {section}", description: "{description}" }
     - { label: "[PARTIAL] {page}", description: "{scenario_goal} -- {friction_description}" }
     - { label: "[NITPICK] {page} > {section}", description: "{description}" }
     - ... (one per issue from reports)
     - { label: "Fix all issues", description: "Select every issue above" }
     - { label: "Type something else", description: "Describe a different change to make" }
     - { label: "Chat about this", description: "Discuss these issues before choosing" }

   **Handling responses:**
   - **Individual selections (multiSelect):** Map selected issues to their full details (page, section, description, suggested fix from report) for Step 2.
   - **"Fix all issues":** Select all listed issues.
   - **"Type something else":** Ask the user in plain text what changes they want. Wait for response. Use that text as the change description for Step 2.
   - **"Chat about this":** Explain the severity levels (BLOCKING = factual/broken, FAIL = user goal impossible, SUGGESTION = improvement, PARTIAL = friction, NITPICK = style) and discuss specific issues. After conversation resolves, re-present the AskUserQuestion.
   - **"Other" (auto-added):** Ask the user in plain text what they want to do. Wait for response. Proceed based on their answer.

#### Step 1b: Process Selection

- **If `$ARGUMENTS` is provided and is NOT a numeric selection (e.g., not "1,3" or "all"):**
  Treat `$ARGUMENTS` as a freeform instruction. Skip the selection prompt entirely. Use the argument text as the change description for Step 2.
  Example: `/doc-writer:edit fix the installation steps on getting-started.md` uses "fix the installation steps on getting-started.md" as the instruction.

- **If the user enters a numeric selection (e.g., "1,3" or "2"):**
  Map the selected numbers to their full issue details (page, section, description, suggested fix from report).

- **If the user enters "all":**
  Select all listed issues.

- **If the user types a freeform description:**
  Use that text as the change description for Step 2.

### Step 2: Author Targeted Revision

Spawn the doc-author agent to make targeted fixes. Only the pages affected by selected issues should be modified.

Use the Agent tool to spawn `doc-author` with this delegation message:

> Read .doc-writer/config.yaml for project configuration. Make targeted revisions to the following documentation pages. Do NOT regenerate other pages or create new pages. Focus only on the specific issues described below.
>
> **Issues to fix:**
>
> {For each selected issue, include:}
> - **Page:** {page_path}
> - **Section:** {section_name} (if available)
> - **Issue:** {severity} -- {description}
> - **Suggested fix:** {suggestion from report, if available}
>
> {For freeform instructions:}
> - **Instruction:** {user's freeform text}
>
> Revise only the listed pages. Apply your standard quality rules and persona calibration from the config.

Wait for the Author agent to complete. Note which pages were modified.

### Step 3: Editor Quality Pass

After the Author makes revisions, spawn the doc-editor agent to verify quality on the changed pages.

Use the Agent tool to spawn `doc-editor` with this delegation message:

> Edit the following revised documentation pages: {comma-separated list of changed page paths}. Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking on these pages. For the terminology pass, scan ALL documentation files in {paths.docs_root} (not just changed pages) because terminology changes can ripple across the entire doc set. Write your report to .doc-writer/editor-report.md.

Wait for the Editor agent to complete.

### Step 4: Done

Present a summary of what was changed:

```
## Edit Complete

### Modified Pages
- **{page_path}**: {brief description of what was fixed}
- **{page_path}**: {brief description of what was fixed}

### Issues Addressed
- {issue 1 summary}
- {issue 2 summary}

---

Changes are uncommitted. Review the diff and commit when satisfied.

**Next steps:**
- Run `/doc-writer:review` to validate the changes with full audit
- Run `git diff {docs_root}` to inspect changes before committing
```

## Constraints

- Do NOT run Persona evaluation after editing. The edit workflow is Author + Editor only.
- Do NOT commit any changes -- the project author reviews and commits.
- Do NOT use `context: fork` when spawning agents.
- Do NOT regenerate pages that are not affected by the selected issues.
- Handle missing reports gracefully -- freeform mode always works even with no prior reports.
- If `$ARGUMENTS` contains freeform text (not a number selection), use it directly without prompting.
