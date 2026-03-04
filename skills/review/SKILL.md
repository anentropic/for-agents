---
name: review
description: Audit existing documentation without generating new content. Runs Editor quality checks, Persona validation, and gap detection.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
---

# Doc Writer Review

Audit existing documentation without regenerating content. Runs gap detection, Editor quality checks, and Persona validation, then presents a combined report.

## Instructions

Follow these steps in order. Complete each step before moving to the next.

### Pre-Flight

1. Use Read to load `.doc-writer/config.yaml`.
   - **If missing:** Tell the user: "No doc-writer configuration found. Run `/doc-writer:setup` first to configure your project." Stop.

2. Extract from config:
   - `audiences` array (each entry has `name`, `skill_level`)
   - `detected.language` (e.g., `typescript`, `python`)
   - `paths.docs_root` (e.g., `docs/`)
   - `paths.source_root` (e.g., `src/`)

3. Use Glob to check that documentation files exist in `{paths.docs_root}`:
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

Spawn the doc-editor agent to review documentation quality. The Editor will make improvements directly as it audits -- this is expected behavior per its design.

Use the Agent tool to spawn `doc-editor` with this delegation message:

> Review the documentation in {docs_root}. Run all three passes: terminology consistency, humanizer review, cross-reference verification. Focus on identifying issues and editing docs to fix them. Write your report to .doc-writer/editor-report.md.

Wait for the Editor agent to complete before proceeding.

### Step 3: Persona Evaluation

For each audience in `config.audiences`, spawn a doc-persona agent to evaluate the documentation from that audience's perspective.

For each audience entry:

Use the Agent tool to spawn `doc-persona` with this delegation message:

> Evaluate documentation as the '{audience.name}' audience. Read the docs in {docs_root} and run your full three-phase workflow: generate scenarios, simulate user journeys, and produce your report. Write your report to .doc-writer/persona-report-{audience_name_slug}.md.

Where `{audience_name_slug}` is the audience name lowercased with spaces replaced by hyphens.

If there is only one audience, also write to `.doc-writer/persona-report.md` for compatibility.

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

Note: The Editor has already applied fixes to docs as part of its review.

### Persona Verdicts

**{audience_name}** ({skill_level}):
| Scenario | Verdict | Notes |
|----------|---------|-------|
| {goal}   | {PASS/PARTIAL/FAIL} | {brief note} |

{repeat for each audience}

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
- The Editor WILL edit docs as part of its review. This is by design. The review command's value is the reports plus Persona evaluation on top of Editor improvements.
- Present results to the project author and stop. No approval gates or iterative flows.
