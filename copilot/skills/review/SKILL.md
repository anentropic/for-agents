---
name: review
description: >-
  Use this skill when the user invokes /copilot:review or asks for a code review
  using GitHub Copilot as a second opinion. Performs multi-dimensional code review
  by running parallel Copilot CLI sub-reviews across 6 focus areas (architecture,
  test coverage, code quality, error handling, dependency audit, reinvented wheels),
  then consolidates and prioritizes all findings into actionable items.
---

# Copilot-Augmented Code Review

Perform in-depth code reviews by decomposing into focused sub-reviews, getting a
second opinion from GitHub Copilot CLI on each dimension, then consolidating and
rating all findings into prioritized action items.

## Usage

```
/copilot:review [path] [--focus area1,area2] [--model gpt-5.4] [--reasoning high]
```

**Arguments:**
- `[path]` — Directory or file to review (defaults to current working directory)
- `--focus` — Comma-separated list of dimensions to review. Options: `architecture`, `tests`, `quality`, `errors`, `deps`, `wheels`. Defaults to all 6.
- `--model` — Copilot model to use (default: `gpt-5.4`)
- `--reasoning` — Copilot reasoning effort: `low`, `medium`, `high` (default: `high`)

## Review Dimensions

| # | ID | Focus Area | What It Examines |
|---|----|-----------|-----------------|
| 1 | `architecture` | Architecture | Module boundaries, dependency graph, separation of concerns, coupling/cohesion, patterns, scalability |
| 2 | `tests` | Test Coverage & Correctness | Missing coverage, test quality, edge cases, assertion quality, test isolation, mocking |
| 3 | `quality` | Code Quality | Dead code, code smells, duplication, naming, idiomatic usage, complexity, readability |
| 4 | `errors` | Error Handling & Robustness | Error propagation, missing error cases, defensive coding, logging, graceful degradation |
| 5 | `deps` | Dependency Audit | Maintenance status, popularity, weight justification, redundancy, missing deps |
| 6 | `wheels` | Reinvented Wheels | Hand-rolled code reimplementing well-known libraries, LLM "build from scratch" smell |

## Additional Resources

### Reference Files
- **`references/review-prompts.md`** — Copilot prompt templates for all 6 review dimensions. Read this file to get the exact prompts to send to Copilot.

## Workflow

Execute these 6 steps in order. Do not skip steps.

### Step 1: PARSE ARGUMENTS

Parse the user's invocation to extract:
- `TARGET_PATH` — path to review (default: `.`)
- `FOCUS_AREAS` — list of dimension IDs (default: all 6)
- `MODEL` — copilot model (default: `gpt-5.4`)
- `REASONING` — reasoning effort (default: `high`)

Validate that `TARGET_PATH` exists. Validate that all `FOCUS_AREAS` are valid dimension IDs.

### Step 2: DISCOVER

Analyze the codebase at `TARGET_PATH` to understand its structure:

1. Identify languages, frameworks, and build tools (check package.json, requirements.txt, go.mod, Cargo.toml, etc.)
2. Map entry points, source directories, and test directories
3. Note the dependency management approach (npm, pip, cargo, etc.)
4. Count approximate lines of code and number of source files

Produce a brief **Codebase Summary** (5-10 lines) capturing:
- Primary language(s) and framework(s)
- Project structure overview
- Key entry points
- Test setup
- Dependency count

This summary will be included in every Copilot prompt for context.

### Step 3: PLAN

For each selected focus area:
1. Read the corresponding prompt template from `references/review-prompts.md`
2. Substitute `{{CODEBASE_SUMMARY}}` with the summary from Step 2
3. Substitute `{{TARGET_PATH}}` with the target path
4. Substitute any other template variables

Present to the user:
- The codebase summary
- Which dimensions will be reviewed
- The model and reasoning settings

Wait for user confirmation before proceeding.

### Step 4: EXECUTE (Parallel)

Launch all selected Copilot sub-reviews **in parallel** using the Task tool with background Bash agents OR background Bash commands. Each review runs as:

```bash
copilot -p "<prompt>" \
  -s --no-ask-user \
  --model "${MODEL}" \
  --reasoning-effort "${REASONING}" \
  --allow-tool 'read' --allow-tool 'glob' --allow-tool 'grep' \
  --autopilot 2>&1
```

**Important execution details:**
- Use `run_in_background: true` for each Bash command so they run in parallel
- Each prompt comes from `references/review-prompts.md` with substitutions applied
- If a Copilot invocation fails (non-zero exit, timeout after 5 minutes, or empty output), record the failure and continue with remaining dimensions
- Collect the full stdout from each invocation

After launching all background tasks, wait for all to complete by reading their output.

### Step 5: CONSOLIDATE & RATE

Review all Copilot findings and produce a unified assessment:

1. **Parse** each Copilot response to extract individual issues (look for the structured `## Issue:` format)
2. **Deduplicate** — merge issues that describe the same underlying problem across dimensions
3. **Validate** each issue:
   - Read the referenced file:line to confirm the issue exists
   - Assess whether the severity rating from Copilot is accurate
   - Add Claude's own commentary: agree, disagree, or add nuance
4. **Rate** each validated issue:
   - **Severity**: Critical / Major / Minor (validated against Copilot's rating)
   - **Effort**: S (< 30 min) / M (30 min - 2 hours) / L (> 2 hours)
5. **Prioritize** by severity-to-effort ratio:
   - Critical + S effort = highest priority
   - Minor + L effort = lowest priority
   - Group related issues that can be fixed together

### Step 6: OUTPUT

Create the output directory and write the review file:

```bash
mkdir -p .reviews
```

Write to `.reviews/review-YYYY-MM-DD.md` (use today's date, append `-N` suffix if file exists).

#### Output Format

```markdown
# Code Review — [Project Name]
**Date**: YYYY-MM-DD
**Reviewed by**: Claude + GitHub Copilot (MODEL)
**Scope**: TARGET_PATH
**Dimensions**: list of dimensions reviewed

## Codebase Summary

[Summary from Step 2]

---

## Findings by Dimension

### 1. Architecture
[Copilot's findings with relevant quotes]
[Claude's commentary on each finding]

### 2. Test Coverage & Correctness
...

[Repeat for each reviewed dimension]

---

## Consolidated Issues

| # | Category | File | Issue | Severity | Effort | Claude's Take |
|---|----------|------|-------|----------|--------|---------------|
| 1 | ... | ... | ... | ... | ... | ... |

---

## Top Action Items

### Quick Wins (High severity, Low effort)
1. ...

### Important (High severity, Higher effort)
1. ...

### Worth Doing (Lower severity, Low effort)
1. ...

---

## Gaps

[Note any dimensions where Copilot failed or produced no findings]

---

*Generated by /copilot:review — Claude as arbiter, Copilot as second opinion*
```

After writing the file, display:
- Path to the review file
- Count of issues found by severity
- Top 3 action items as a quick summary

## Error Handling

- **Copilot not installed**: Check for `copilot` on PATH before Step 4. If missing, inform the user and abort.
- **Copilot timeout**: If a sub-review takes longer than 5 minutes, kill it and note the gap.
- **Copilot error**: If a sub-review exits non-zero, capture stderr, note the failure, and continue.
- **No issues found**: If a dimension returns no issues, note it as "No issues identified" — this is a valid outcome.
- **All dimensions fail**: If every Copilot invocation fails, report the errors and suggest the user check their Copilot CLI setup.
