---
name: doc-writer:write
description: Generate new documentation using the full Author > Editor > Persona pipeline with gap detection, revision loop, and quality validation.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--skip-gap-scan]"
---

# Doc Writer: Full Pipeline

You are orchestrating the doc-writer documentation pipeline. Follow these steps exactly in order. Do NOT use `context: fork`. Do NOT commit any generated documentation -- leave all changes uncommitted for the project author to review.

## Pre-Flight

1. Read `.doc-writer/config.yaml`. If the file does not exist, tell the user:
   "No configuration found. Run `/doc-writer:setup` first to configure audiences, doc system, and paths."
   Then **stop** -- do not proceed with the pipeline.

2. Extract these values from config:
   - `audiences` (array -- note the count for Persona spawning)
   - `doc_system` (string)
   - `paths.source_root` (string)
   - `paths.docs_root` (string)
   - `detected.language` (string)

3. If `.planning/PROJECT.md` exists, note it as optional context the Author can use for richer project understanding. Do not treat it as a required dependency.

4. Initialize pipeline state:
   - `pass_count = 1`
   - `max_passes = 3`

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

## Step 2: Author

Spawn the doc-author agent to generate documentation.

**Initial pass delegation:**

Use the Agent tool to spawn `doc-author` with this message:

> Generate documentation for this project. Read `.doc-writer/config.yaml` for audience and paths configuration. Read `.doc-writer/gap-report.md` for undocumented symbols to prioritize in your coverage.

**Revision pass delegation** (when returning here from Step 5):

Use the Agent tool to spawn `doc-author` with this message:

> This is revision pass {pass_count} of {max_passes}. Revise ONLY the following pages based on Persona FAIL verdicts: {page_list}. Read the persona report(s) in `.doc-writer/` for specific gaps identified. Do NOT regenerate pages that passed evaluation.

Wait for the Author agent to complete before proceeding.

---

## Step 3: Editor

Spawn the doc-editor agent to run quality passes on the authored documentation.

**Initial pass delegation:**

Use the Agent tool to spawn `doc-editor` with this message:

> Edit the documentation in {paths.docs_root}. Run all four passes: terminology consistency, Diataxis type integrity, humanizer, and cross-reference linking.

**Revision pass delegation** (when returning here from Step 5):

Use the Agent tool to spawn `doc-editor` with this message:

> Edit the revised documentation pages: {changed_pages}. Run all four passes on the changed pages. Run the terminology pass on ALL documentation pages since term changes can ripple across files.

Wait for the Editor agent to complete before proceeding.

---

## Step 4: Persona Evaluation

For each audience defined in `config.audiences`, spawn a separate doc-persona agent.

**For each audience, use the Agent tool to spawn `doc-persona` with this message:**

> Evaluate the documentation as the '{audience_name}' audience.

If there are multiple audiences, spawn each Persona agent sequentially. Each produces an independent report:
- Single audience: `.doc-writer/persona-report.md`
- Multiple audiences: `.doc-writer/persona-report-{audience_name_slug}.md`

Where `{audience_name_slug}` is the audience name lowercased with spaces replaced by hyphens.

**Important on revision passes:** Do NOT instruct the Persona to generate new scenarios. It will reuse existing scenarios from `.doc-writer/scenarios.yaml` automatically.

Wait for all Persona agents to complete before proceeding.

---

## Step 5: Verdict Check and Revision Routing

After all Persona evaluations complete, read all persona report files and collect verdicts for every scenario across all audiences.

### Routing Logic

**Case A: All PASS across all audiences**
- If there are any PARTIAL verdicts from earlier passes that were deferred, go to Step 6 (PARTIAL Approval).
- Otherwise, go to Step 7 (Summary Report).

**Case B: Any FAIL verdict exists AND pass_count < max_passes (3)**
1. Extract FAIL details from persona reports:
   - Which pages failed
   - What specific gaps or issues were identified
   - Which audience(s) reported the failure
2. Increment `pass_count` by 1.
3. Compile the targeted page list from all FAIL verdicts across all audiences.
4. Return to **Step 2** (Author) with the revision pass delegation, passing the page list and fail details.
5. Then proceed through **Step 3** (Editor on changed pages) and **Step 4** (Persona with reused scenarios).
6. Return here to re-evaluate verdicts.

**Case C: Any FAIL verdict exists AND pass_count >= max_passes (3)**
- **ESCALATION.** Present the remaining failures to the project author:

```
## Escalation: Non-Converging Issues

After {pass_count} passes, the following issues could not be resolved automatically:

### Remaining FAILs

{For each FAIL verdict:}
- **Audience:** {audience_name}
- **Scenario:** {scenario_id} -- {goal}
- **Page:** {page_path}
- **Issue:** {what failed and why}
- **Attempts:** {what was tried across passes}

### Recommendation

These issues may require manual intervention. Consider:
1. Reviewing the flagged pages directly
2. Running `/doc-writer:edit` with specific instructions
3. Adjusting audience definitions in `/doc-writer:setup` if expectations are miscalibrated
```

- After presenting the escalation, proceed to Step 6 if there are PARTIAL verdicts, or Step 7 if not.

**Case D: Only PARTIAL verdicts (no FAIL across any audience)**
- Go to Step 6 (PARTIAL Approval).

---

## Step 6: PARTIAL Approval

Collect all PARTIAL fix suggestions from all persona reports across all audiences. Present them as a numbered list for the project author to approve or reject.

```
## PARTIAL Issues Requiring Your Decision

The following issues were identified but do not prevent users from accomplishing
their goals. Review each and decide which to fix:

{For each PARTIAL verdict:}
{N}. [{audience_name}, {scenario_id}] {page_path} > "{section_name}"
   Issue: {description of friction or gap}
   Suggested fix: {what the Persona recommended}

---

Or describe additional changes you would like made:

Enter numbers to approve (e.g., "1,3"), "all", or "none":
```

Wait for the project author to respond.

### Processing Approval

- **Numbers (e.g., "1,3,5"):** Apply only the approved fixes by writing changes directly to the doc files. Do NOT re-run the pipeline for PARTIAL fixes.
- **"all":** Apply all suggested fixes directly.
- **"none":** Skip all PARTIAL fixes. Proceed to Summary.
- **Freeform text:** If the user describes additional changes instead of (or in addition to) selecting numbers, apply those changes directly to the relevant doc files.

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

### Pages Written/Revised
{List each doc page that was created or modified, with status: new/revised}

### Editor Changes Applied
- Terminology fixes: {count}
- Humanizer rewrites: {count}
- Cross-reference updates: {count}

### Persona Verdicts
{For each audience:}
**{audience_name}:**
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
