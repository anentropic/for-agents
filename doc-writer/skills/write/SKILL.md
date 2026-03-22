---
name: doc-writer:write
description: Generate or update documentation. Auto-detects existing docs — creates from scratch for new projects, or adds coverage for undocumented features while leaving existing pages untouched.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--skip-gap-scan]"
---

# Doc Writer: Full Pipeline

You are orchestrating the doc-writer documentation pipeline. This pipeline operates in two modes:

- **Create mode:** No existing docs found — generates documentation from scratch using the full Author > Editor > Persona pipeline with revision loops.
- **Update mode:** Existing docs detected — runs gap detection to find undocumented symbols, then generates documentation for only the new features while leaving existing pages untouched.

The mode is auto-detected based on what's in `paths.docs_root`. Follow these steps exactly in order. Do NOT use `context: fork`. Do NOT commit any generated documentation -- leave all changes uncommitted for the project author to review.

## User Interaction Pattern

This skill uses AskUserQuestion for structured choices. When the user selects:
- **"Type something else"** or **"Other"**: Ask your follow-up as plain text. Wait for their response. Then resume the workflow.
- **"Chat about this"**: Explain the current decision in depth. Open a plain-text dialogue. After it resolves, re-present the original question or proceed based on what was discussed.

Never respond to these selections with another AskUserQuestion.

## Pre-Flight

1. Read `.doc-writer/config.yaml`. If the file does not exist, tell the user:
   "No configuration found. Run `/doc-writer:setup` first to configure user personas, doc system, and paths."
   Then **stop** -- do not proceed with the pipeline.

2. Extract these values from config:
   - `user_personas` (array -- note the count for User Tester spawning)
   - `doc_system` (string)
   - `paths.source_root` (string)
   - `paths.docs_root` (string)
   - `detected.language` (string)

3. If `.planning/PROJECT.md` exists, note it as optional context the Author can use for richer project understanding. Do not treat it as a required dependency.

4. Initialize pipeline state:
   - `pass_count = 1`
   - `max_passes = 3`

---

## Step 0: Mode Detection

Determine whether this is a create or update run.

1. Use Glob to find documentation files:
   - When `doc_system` is `odoc`: glob `doc/**/*.mld` (not `{paths.docs_root}/**/*.md`)
   - When `doc_system` is NOT `odoc`: glob `{paths.docs_root}/**/*.md`

2. Filter out bare scaffold pages:
   - For .md files: an `index.md` that contains only a title and a "Welcome to..." line
   - For .mld files: an `index.mld` that contains only `{0 ...}` and TODO placeholders

3. Count remaining substantive doc pages.

4. **Determine `pipeline_mode`:**

   - **`"create"`** if:
     - 0 substantive doc pages in `docs_root`
     - OR only a bare scaffold `index.md`
     - Note: a README.md in the project root does NOT count as existing docs (unless `doc_system` is `plain-markdown` AND the README is substantial — more than 50 lines with multiple headings)

   - **`"update"`** if:
     - 2 or more substantive doc pages exist in `docs_root`

5. Display mode to user:
   - Create: `"No existing documentation found in {paths.docs_root}. Running full pipeline."`
   - Update: `"Existing documentation detected ({N} pages in {paths.docs_root}). Running incremental update — documenting new features only."`

6. Store `pipeline_mode` and `existing_page_count` for use in subsequent steps.

---

## Step 1: Gap Detection

**Skip this step if `$ARGUMENTS` contains `--skip-gap-scan`.**

1. Read `detected.language` and `paths.source_root` from the config values extracted in Pre-Flight.

2. Run the export scanner:
   ```
   bash ${CLAUDE_PLUGIN_ROOT}/skills/write/scripts/scan-exports.sh {paths.source_root} {detected.language}
   ```

3. Read existing documentation files in `paths.docs_root` to identify which exported symbols already have documentation coverage.

4. Compare the scanner output against documented symbols. For each exported symbol not found in any doc page, add it to the gap list.

5. Write the gap report to `.doc-writer/gap-report.md` with this structure:
   ```markdown
   # Gap Report

   **Generated:** {date}
   **Source root:** {paths.source_root}
   **Language:** {detected.language}
   **Total undocumented symbols:** {count}

   ## Undocumented Symbols

   ### {module/file path}
   - `symbol_name` (function/class/constant/type)
   - `symbol_name` (function/class/constant/type)

   ### {module/file path}
   - `symbol_name` (function/class/constant/type)
   ```

6. If a previous `.doc-writer/gap-report.md` exists, note which gaps are newly discovered versus persistent from the last run.

7. Display a brief summary to the user: "{N} undocumented exported symbols found across {M} modules."

---

## Step 2a: Author — Plan

Spawn the doc-author agent in **plan-only mode** to scan the codebase and propose a page inventory. The author writes the inventory to a file and exits without writing any documentation pages.

**Skip this step on revision passes** (when returning from Step 5). On revision passes, go directly to Step 2c.

**Create mode** — use the Agent tool to spawn `doc-author` with this message:

> Run Phase 1 only (plan mode). Scan the codebase and produce a page inventory. Write the inventory to `.doc-writer/page-inventory.md`. Do NOT write any documentation pages. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration. If `.doc-writer/gap-report.md` exists, read it for undocumented symbols to prioritize in your coverage.

**Update mode** — first check the gap report from Step 1:

- If gap-report shows **0 undocumented symbols**: display "All exported symbols are already documented. No new pages needed." Skip Steps 2a–2c entirely and proceed directly to Step 3 (Editor) for a quality pass on existing docs.

- If gap-report shows **undocumented symbols**: use the Agent tool to spawn `doc-author` with this message:

> Run Phase 1 only (plan mode). Existing documentation is in {paths.docs_root} ({existing_page_count} pages). Scan the codebase and produce a page inventory for ONLY the undocumented symbols listed in `.doc-writer/gap-report.md`. Do NOT propose pages for already-documented features. Write the inventory to `.doc-writer/page-inventory.md`. Do NOT write any documentation pages. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration.

Wait for the Author agent to complete before proceeding.

---

## Step 2b: Page Inventory Approval

Read `.doc-writer/page-inventory.md`. Parse the page table to extract each proposed page's number, type, title, key sections, and file path.

**Skip this step on revision passes** (when returning from Step 5).

Use AskUserQuestion to present the inventory for approval:
- header: "Pages"
- question: "Confirm the page inventory. Deselect pages to exclude, or choose an action."
- multiSelect: true
- options: [dynamically generated from the inventory file, all pre-selected:]
  - { label: "{title} ({type})", description: "{key sections}" }
  - ... (one per proposed page)
  - { label: "Type something else", description: "Add pages or modify the plan" }
  - { label: "Chat about this", description: "Discuss the page inventory" }

**Handling responses:**
- **Individual selections (multiSelect):** Build the `approved_pages` list from selected pages. Pages that were deselected are excluded.
- **"Type something else":** Ask the user in plain text what pages to add, remove, or modify. Update the inventory based on their response. Then re-present the AskUserQuestion with the updated list.
- **"Chat about this":** Read `.doc-writer/page-inventory.md` and explain why specific pages were proposed, what each page type means, and how the inventory was derived. After discussion, re-present the AskUserQuestion.
- **"Other" (auto-added):** Ask the user in plain text what they want to change. Wait for response. Update inventory if needed and re-present.

If all pages are deselected, inform the user that no documentation will be generated and stop.

Store `approved_pages` (list of page entries with number, type, title, key sections, file path) for Step 2c.

---

## Step 2c: Author — Write

Spawn the doc-author agent in **write-only mode** with the approved page list.

**Initial pass** — use the Agent tool to spawn `doc-author` with this message:

> Run Phase 2 only (write mode). The following pages have been approved by the project author. Write ONLY these pages. Do NOT scan or plan. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration.
>
> Approved pages:
> {for each page in approved_pages:}
> - [{number}] {type}: "{title}" — {key sections} → {file_path}

**Revision pass** (when returning here from Step 5):

Use the Agent tool to spawn `doc-author` with this message:

> Run Phase 2 only (write mode). This is revision pass {pass_count} of {max_passes}. Revise ONLY the following pages based on Persona FAIL verdicts: {page_list}. Read the persona report(s) in `.doc-writer/` for specific gaps identified. Do NOT regenerate pages that passed evaluation. Do NOT use AskUserQuestion.

Wait for the Author agent to complete before proceeding.

---

## Step 3: Editor

Spawn the doc-editor agent to run quality passes on the authored documentation.

**Initial pass delegation depends on `pipeline_mode`:**

**Create mode** — use the Agent tool to spawn `doc-editor` with this message:

> Edit the documentation in {paths.docs_root}. Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking.

**Update mode** — scope the Editor to new pages, but run terminology across all:

> Edit the NEW documentation pages: {new_page_list}. Run all four passes on the new pages. Run the terminology pass on ALL documentation pages in {paths.docs_root} since term changes can ripple across files.

Where `{new_page_list}` is the list of pages created by the Author in Step 2. If Author was skipped (0 gaps), run the Editor on all existing pages instead (full quality pass).

**Revision pass delegation** (when returning here from Step 5):

Use the Agent tool to spawn `doc-editor` with this message:

> Edit the revised documentation pages: {changed_pages}. Run all four passes on the changed pages. Run the terminology pass on ALL documentation pages since term changes can ripple across files.

Wait for the Editor agent to complete before proceeding.

---

## Step 4: Persona Evaluation

For each persona defined in `config.user_personas`, spawn a separate doc-user-tester agent.

**For each persona, use the Agent tool to spawn `doc-user-tester` with this message:**

> Evaluate the documentation as the '{persona_name}' persona.

If there are multiple personas, spawn each Persona agent sequentially. Each produces an independent report:
- Single persona: `.doc-writer/persona-report.md`
- Multiple personas: `.doc-writer/persona-report-{persona_name_slug}.md`

Where `{persona_name_slug}` is the persona name lowercased with spaces replaced by hyphens.

**Important on revision passes:** Do NOT instruct the Persona to generate new scenarios. It will reuse existing scenarios from `.doc-writer/scenarios.yaml` automatically.

Wait for all Persona agents to complete before proceeding.

---

## Step 5: Verdict Check and Revision Routing

After all Persona evaluations complete, read all persona report files and collect verdicts for every scenario across all personas.

### Routing Logic

**Case A: All PASS across all personas**
- If there are any PARTIAL verdicts from earlier passes that were deferred, go to Step 6 (PARTIAL Approval).
- Otherwise, go to Step 7 (Summary Report).

**Case B: Any FAIL verdict exists AND pass_count < max_passes (3)**
1. Extract FAIL details from persona reports:
   - Which pages failed
   - What specific gaps or issues were identified
   - Which persona(s) reported the failure
2. **Update mode only:** If the FAIL is on a pre-existing page (not a page created in this run), escalate it immediately instead of revising — pre-existing pages were working before and should not be modified by the update pipeline. Add these to the escalation list in Case C.
3. Increment `pass_count` by 1.
4. Compile the targeted page list from all FAIL verdicts on **new pages** across all personas.
5. If no new pages have FAILs (all FAILs were on pre-existing pages), skip revision and go to Case C or Step 6.
6. Return to **Step 2c** (Author — Write) with the revision pass delegation, passing the page list and fail details.
7. Then proceed through **Step 3** (Editor on changed pages) and **Step 4** (Persona with reused scenarios).
8. Return here to re-evaluate verdicts.

**Case C: Any FAIL verdict exists AND pass_count >= max_passes (3)**
- **ESCALATION.** Present the remaining failures to the project author:

```
## Escalation: Non-Converging Issues

After {pass_count} passes, the following issues could not be resolved automatically:

### Remaining FAILs

{For each FAIL verdict:}
- **Audience:** {persona_name}
- **Scenario:** {scenario_id} -- {goal}
- **Page:** {page_path}
- **Issue:** {what failed and why}
- **Attempts:** {what was tried across passes}

### Recommendation

These issues may require manual intervention. Consider:
1. Reviewing the flagged pages directly
2. Running `/doc-writer:edit` with specific instructions
3. Adjusting persona definitions in `/doc-writer:setup` if expectations are miscalibrated
```

- After presenting the escalation, proceed to Step 6 if there are PARTIAL verdicts, or Step 7 if not.

**Case D: Only PARTIAL verdicts (no FAIL across any persona)**
- Go to Step 6 (PARTIAL Approval).

---

## Step 6: PARTIAL Approval

Collect all PARTIAL fix suggestions from all persona reports across all personas.

Use AskUserQuestion to present them for approval:
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

**Handling responses:**
- **Individual selections (multiSelect):** Apply only the selected fixes by writing changes directly to the doc files. Do NOT re-run the pipeline for PARTIAL fixes.
- **"Apply all fixes":** Apply all suggested fixes directly.
- **"Skip all fixes":** Skip all PARTIAL fixes. Proceed to Summary.
- **"Type something else":** Ask the user in plain text what additional changes they want. Wait for response. Apply those changes directly to the relevant doc files.
- **"Chat about this":** Explain what each PARTIAL issue means and what the suggested fixes would change. Open a plain-text dialogue. After discussion resolves, re-present the AskUserQuestion to get a decision.
- **"Other" (auto-added):** Ask the user in plain text what they want to do. Wait for response. Proceed based on their answer.

After applying approved fixes, proceed to Step 7.

---

### Read Editor Report

Before presenting the summary, read `.doc-writer/editor-report.md` to extract change counts for the summary:
- Parse the "Changes made" section for BLOCKING, SUGGESTION, and NITPICK counts
- If the file does not exist (Editor was skipped or failed), use "N/A" for all counts

---

## Step 7: Summary Report

Present a completion summary to the project author:

```
## Documentation Pipeline Complete

### Pipeline Mode
{Create: "Full documentation generated from scratch." | Update: "Incremental update — {N} new pages added for undocumented symbols."}

### Pages Written/Revised
{List each doc page that was created or modified, with status: new/revised}

### Editor Changes Applied
- Terminology fixes: {count}
- Humanizer rewrites: {count}
- Cross-reference updates: {count}

### Persona Verdicts
{For each persona:}
**{persona_name}:**
{For each scenario:}
- {scenario_id}: {verdict} -- {one-line summary}

### Pipeline Statistics
- Total passes: {pass_count}
- Gap detection: {N} undocumented symbols found
- PARTIAL fixes approved: {count approved} of {count total}
{If escalation occurred:}
- Escalated FAILs: {count} (see above for details)

### Next Steps
Documentation files are **uncommitted**. Review the changes with `git diff` and
commit when satisfied. To re-evaluate documentation quality, run `/doc-writer:review`.
```

---

## Notes

- This skill runs in the main conversation context (no `context: fork`) so the project author can interact with PARTIAL approval prompts and see progress.
- Subagents (Author, Editor, Persona) cannot spawn other subagents. All orchestration happens here at the skill level.
- Generated documentation is never committed automatically. The project author reviews and commits manually.
- Persona scenarios are generated once (initial pass) and reused on revision passes for consistent evaluation.
- The gap detection script uses standard Unix grep and requires no additional dependencies.
- This command works in any Claude Code session, including GSD sessions. No special hooks or integration is required.
