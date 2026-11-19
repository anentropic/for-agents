---
name: doc-writer:write
description: Generate or update documentation. Auto-detects existing docs — creates from scratch for new projects, adds coverage for undocumented features, or refreshes existing pages with stale content.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--skip-gap-scan]"
---

# Doc Writer: Full Pipeline

You are orchestrating the doc-writer documentation pipeline. This pipeline operates in two modes:

- **Create mode:** No existing docs found — generates documentation from scratch using the full Author > Editor > Persona pipeline with revision loops.
- **Update mode:** Existing docs detected — runs gap detection to find undocumented symbols and pages with potentially stale content, then generates documentation for new features and refreshes existing pages where source code has changed.

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
   - Update: `"Existing documentation detected ({N} pages in {paths.docs_root}). Running incremental update — checking for new features and stale content."`

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

5. **Staleness detection** (update mode only — skip this sub-step if `pipeline_mode` is `"create"`):

   For each existing documentation page found in Step 0, check whether source code has changed more recently than the documentation:

   a. Get the doc page's last substantive modification date:
      ```
      git log -1 --format="%ai" -- {doc_page_path}
      ```
   b. Get the source root's last modification date:
      ```
      git log -1 --format="%ai" -- {paths.source_root}
      ```
   c. If the source root was modified more recently than the doc page, add the page to the `stale_pages` list with both timestamps.

   This is a coarse heuristic — false positives are expected (e.g., source changes that don't affect documented content). The Author will verify actual staleness during planning by comparing page content against current source code.

6. Write the gap report to `.doc-writer/gap-report.md` with this structure:
   ```markdown
   # Gap Report

   **Generated:** {date}
   **Source root:** {paths.source_root}
   **Language:** {detected.language}
   **Total undocumented symbols:** {count}
   **Potentially stale pages:** {count}

   ## Undocumented Symbols

   ### {module/file path}
   - `symbol_name` (function/class/constant/type)
   - `symbol_name` (function/class/constant/type)

   ### {module/file path}
   - `symbol_name` (function/class/constant/type)

   ## Potentially Stale Pages

   {N} doc pages are older than recent source changes:

   - `{doc_page_path}` (doc: {date}, source: {date})
   - `{doc_page_path}` (doc: {date}, source: {date})
   ```

   If `pipeline_mode` is `"create"`, omit the "Potentially Stale Pages" section entirely.

7. If a previous `.doc-writer/gap-report.md` exists, note which gaps are newly discovered versus persistent from the last run.

8. Display a brief summary to the user:
   - Create mode: "{N} undocumented exported symbols found across {M} modules."
   - Update mode: "{N} undocumented exported symbols found across {M} modules. {P} existing pages may have stale content."

---

## Step 2a: Author — Plan

Spawn the doc-author agent in **plan-only mode** to scan the codebase and propose a page inventory. The author writes the inventory to a file and exits without writing any documentation pages.

**Skip this step on revision passes** (when returning from Step 5). On revision passes, go directly to Step 2c.

**Create mode** — use the Agent tool to spawn `doc-author` with this message:

> Run Phase 1 only (plan mode). Scan the codebase and produce a page inventory. Write the inventory to `.doc-writer/page-inventory.md`. Do NOT write any documentation pages. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration. If `.doc-writer/gap-report.md` exists, read it for undocumented symbols to prioritize in your coverage.

**Update mode** — check the gap report from Step 1 for both undocumented symbols and stale pages:

- If gap-report shows **0 undocumented symbols AND 0 stale pages**: display "All exported symbols are documented and all pages are up to date." Gap detection only finds undocumented symbols and stale pages, so it can't see a missing page that the user wants (a new how-to guide, an explanation, a page a Persona FAIL asked for). Before skipping the Author, use AskUserQuestion:
  - header: "New pages"
  - question: "Gap detection found nothing to add. Do you want any new pages, or just a quality pass on the existing docs?"
  - options:
    - { label: "Quality pass only", description: "Skip the Author and run the Editor and Persona on the existing docs" }
    - { label: "Add pages", description: "Describe the pages you want; the Author plans them for your approval" }
    - { label: "Chat about this", description: "Discuss what gap detection checks and what it misses" }

  **"Quality pass only"**: skip Steps 2a–2c entirely and proceed directly to Step 3 (Editor) for a quality pass on existing docs.

  **"Add pages"** (or "Type something else"/"Other" with a description of pages): ask in plain text which pages they want, if they have not already said. Then spawn `doc-author` with this message, and continue with Step 2b (Page Inventory Approval) and Step 2c as usual:

> Run Phase 1 only (plan mode). Existing documentation is in {paths.docs_root} ({existing_page_count} pages). The project author has asked for these new pages: {user's description}. Propose inventory entries for ONLY those pages, fitting them into the existing structure. Do NOT propose pages for already-documented features. Write the inventory to `.doc-writer/page-inventory.md`. Do NOT write any documentation pages. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration.

  **"Chat about this"**: explain that gap detection compares exported symbols against the docs and compares doc dates against source dates, so pages that are not about one symbol never show up as gaps. Then re-present the question.

- If gap-report shows **undocumented symbols only** (0 stale pages): use the Agent tool to spawn `doc-author` with this message:

> Run Phase 1 only (plan mode). Existing documentation is in {paths.docs_root} ({existing_page_count} pages). Scan the codebase and produce a page inventory for ONLY the undocumented symbols listed in `.doc-writer/gap-report.md`. Do NOT propose pages for already-documented features. Write the inventory to `.doc-writer/page-inventory.md`. Do NOT write any documentation pages. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration.

- If gap-report shows **stale pages only** (0 undocumented symbols): use the Agent tool to spawn `doc-author` with this message:

> Run Phase 1 only (plan mode). Existing documentation is in {paths.docs_root} ({existing_page_count} pages). The following existing pages have been flagged as potentially stale — their source files were modified more recently than the documentation:
>
> {For each page in stale_pages from the gap report:}
> - {page_path} (doc last modified: {date}, source last modified: {date})
>
> For each flagged page: read the current page content, read the corresponding source code, and determine whether the page content is actually outdated. For pages with real discrepancies, propose an inventory entry of type `(refresh)` with specific discrepancies noted in the "Key Sections" column. For pages that are still accurate despite the timestamp difference, note them as "(refresh) — no changes needed" in the inventory.
>
> Write the inventory to `.doc-writer/page-inventory.md`. Do NOT write any documentation pages. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration.

- If gap-report shows **both undocumented symbols AND stale pages**: use the Agent tool to spawn `doc-author` with this message:

> Run Phase 1 only (plan mode). Existing documentation is in {paths.docs_root} ({existing_page_count} pages). Scan the codebase and produce a page inventory that covers TWO kinds of gaps:
>
> **New pages:** Propose pages for the undocumented symbols listed in `.doc-writer/gap-report.md`. Do NOT propose pages for already-documented features.
>
> **Content refresh:** The following existing pages have been flagged as potentially stale — their source files were modified more recently than the documentation:
>
> {For each page in stale_pages from the gap report:}
> - {page_path} (doc last modified: {date}, source last modified: {date})
>
> For each flagged page: read the current page content, read the corresponding source code, and determine whether the page content is actually outdated. For pages with real discrepancies, propose an inventory entry of type `(refresh)` with specific discrepancies noted in the "Key Sections" column. For pages that are still accurate despite the timestamp difference, note them as "(refresh) — no changes needed" in the inventory.
>
> Write both new page entries and refresh entries to `.doc-writer/page-inventory.md`. Separate them with a "## Content Refresh" heading. Do NOT write any documentation pages. Do NOT use AskUserQuestion. Read `.doc-writer/config.yaml` for persona and paths configuration.

Wait for the Author agent to complete before proceeding.

---

## Step 2b: Page Inventory Approval

Read `.doc-writer/page-inventory.md`. Parse the page table to extract each proposed page's number, type, title, key sections, and file path.

**Skip this step on revision passes** (when returning from Step 5).

Use AskUserQuestion to present the inventory for approval:
- header: "Pages"
- question: "Confirm the page inventory. Deselect pages to exclude, or choose an action."
- multiSelect: true
- options: [dynamically generated from the inventory file:]
  - **New pages** (all pre-selected):
    - { label: "{title} ({type})", description: "{key sections}" }
    - ... (one per proposed new page)
  - **Content refresh** (if any `(refresh)` entries exist — pre-selected UNLESS Author marked "no changes needed"):
    - { label: "↻ {title}", description: "{discrepancies found}" }
    - ... (one per refresh entry)
    - Entries marked "no changes needed" by the Author are shown as:
      { label: "↻ {title} ✓ current", description: "No discrepancies found with current source" }
      These are **pre-deselected** (not checked by default) since the Author confirmed they are current.
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
> {If approved_pages contains new pages (non-refresh types):}
> New pages:
> {for each page in approved_pages where type is NOT (refresh):}
> - [{number}] {type}: "{title}" — {key sections} → {file_path}
>
> {If approved_pages contains (refresh) pages:}
> Content refresh pages — these pages already exist. Read the existing page content first, then update in-place to reflect current source code. Preserve the page's existing structure, tone, and style. Update ONLY the stale content: changed signatures, parameters, schemas, examples, configuration keys, or behavioral descriptions. Do not rewrite sections that are still accurate.
>
> Refresh pages:
> {for each page in approved_pages where type is (refresh):}
> - [{number}] (refresh): "{title}" — {discrepancies} → {file_path}

**Revision pass** (when returning here from Step 5):

Use the Agent tool to spawn `doc-author` with this message:

> Run Phase 2 only (write mode). This is revision pass {pass_count} of {max_passes}. Revise ONLY the following pages based on Persona FAIL verdicts: {page_list}. Read the persona report(s) in `.doc-writer/` for specific gaps identified. Do NOT regenerate pages that passed evaluation. Do NOT use AskUserQuestion.

**Odoc projects:** The Author will also generate .mli enrichment proposals (if scope includes .mli improvements) after writing all .mld pages. The proposals file `.doc-writer/mli-enrichment.md` is a separate deliverable, not part of the page inventory.

Wait for the Author agent to complete before proceeding.

---

## Step 3: Editor

Spawn the doc-editor agent to run quality passes on the authored documentation.

**Initial pass delegation depends on `pipeline_mode`:**

**Create mode** — use the Agent tool to spawn `doc-editor` with this message:

> Edit the documentation in {paths.docs_root}. Run all four passes: terminology consistency, Diataxis type integrity, deslop, and cross-reference linking. Prose scanner: `${CLAUDE_PLUGIN_ROOT}/deslop/docs_scan.py`.

**Update mode** — scope the Editor to new and refreshed pages, but run terminology across all:

> Edit the NEW and REFRESHED documentation pages: {changed_page_list}. Run all four passes on these pages. Run the terminology pass on ALL documentation pages in {paths.docs_root} since term changes can ripple across files. Prose scanner: `${CLAUDE_PLUGIN_ROOT}/deslop/docs_scan.py`.

Where `{changed_page_list}` is the combined list of new pages and refreshed pages written by the Author in Step 2. If Author was skipped (0 gaps AND 0 stale pages), run the Editor on all existing pages instead (full quality pass).

**Revision pass delegation** (when returning here from Step 5):

Use the Agent tool to spawn `doc-editor` with this message:

> Edit the revised documentation pages: {changed_pages}. Run all four passes on the changed pages. Run the terminology pass on ALL documentation pages since term changes can ripple across files. Prose scanner: `${CLAUDE_PLUGIN_ROOT}/deslop/docs_scan.py`.

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
2. **Update mode only:** If the FAIL is on a pre-existing page that was NOT created or refreshed in this run, escalate it immediately instead of revising — untouched pre-existing pages should not be modified by the update pipeline. Add these to the escalation list in Case C. Pages that were refreshed in this run (type `(refresh)`) are treated like new pages for revision purposes.
3. Increment `pass_count` by 1.
4. Compile the targeted page list from all FAIL verdicts on **new and refreshed pages** across all personas.
5. If no new or refreshed pages have FAILs (all FAILs were on untouched pre-existing pages), skip revision and go to Case C or Step 6.
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
{Create: "Full documentation generated from scratch." | Update (new only): "Incremental update — {N} new pages added for undocumented symbols." | Update (with refresh): "Incremental update — {N} new pages added, {M} existing pages refreshed with current content."}

### Pages Written/Revised
{List each doc page that was created or modified, with status: new/refreshed/revised}

### Editor Changes Applied
- Terminology fixes: {count}
- Deslop rewrites: {count}
- Cross-reference updates: {count}

### Persona Verdicts
{For each persona:}
**{persona_name}:**
{For each scenario:}
- {scenario_id}: {verdict} -- {one-line summary}

### .mli Enrichment (odoc only)
{If `.doc-writer/mli-enrichment.md` exists:}
- **Proposals:** {N} doc comment proposals in `.doc-writer/mli-enrichment.md`
- **Action required:** Review proposals and apply to .mli files manually
{If file does not exist:}
- No enrichment proposals generated (all public values documented, or scope set to .mld only)

### Pipeline Statistics
- Total passes: {pass_count}
- Gap detection: {N} undocumented symbols found, {P} pages flagged as potentially stale
- Content refresh: {M} pages refreshed ({K} confirmed current by Author, not refreshed)
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
