# copilot-review

A Claude Code plugin that runs a multi-dimensional code review using GitHub Copilot CLI as a second opinion across six focus areas, then consolidates findings into prioritised action items.

- [Tutorial: Run your first review](#tutorial-run-your-first-review)
- [How-to guides](#how-to-guides)
- [Reference](#reference)
- [How the review works](#how-the-review-works)

---

## Tutorial: Run your first review

In this tutorial you will run a full code review on a directory and read the consolidated output. By the end you will know what a complete review looks like and how to act on the results.

**Prerequisites:**
- copilot-review installed via `/plugin install github:anentropic/for-agents`
- GitHub Copilot CLI installed and authenticated (`gh copilot` is available in your shell)
- A project directory to review

### Step 1: Run the review

In your Claude Code session, with your project open:

```
/copilot-review
```

With no arguments the review targets the current working directory and runs all six dimensions using the default model (`gpt-5.4`) at high reasoning effort.

You will see progress output as each sub-review runs:

```
## Codebase Summary

Primary language: Python
Entry points: src/main.py
Test setup: pytest, tests/ directory
Dependencies: 12 (requirements.txt)

Running 6 sub-reviews in parallel...
  [1/6] architecture ✓
  [2/6] tests ✓
  [3/6] quality ✓
  [4/6] errors ✓
  [5/6] deps ✓
  [6/6] wheels ✓

Consolidating findings...
```

### Step 2: Read the consolidated output

After all sub-reviews complete, you see a consolidated report. Each issue follows the same format:

```
## Issue: Circular dependency between auth and user modules
- **File**: src/auth/middleware.py:14
- **Severity**: Major
- **Description**: auth imports from user, user imports from auth. Changes to
  either module risk unexpected breakage in the other.
- **Evidence**: src/auth/middleware.py:14 imports User; src/user/models.py:3
  imports AuthToken
- **Suggestion**: Extract shared types to src/shared/types.py to break the cycle
```

Issues are sorted by severity (Critical → Major → Minor) across all six dimensions.

### Step 3: Act on the findings

Each issue has a specific file and line reference and a concrete suggestion. Work through them from Critical downward. Issues marked Minor are worth noting but rarely need immediate action.

If no issues are found in a dimension, that dimension reports: "No issues found."

**What you learned:**
- How to invoke a default full review
- What the output format looks like
- How issues are prioritised

**Next steps:**
- [How to review a specific directory or file](#how-to-review-a-specific-path)
- [How to filter to specific dimensions](#how-to-filter-to-specific-dimensions)
- [How to tune model and reasoning](#how-to-tune-model-and-reasoning)
- [How the review works](#how-the-review-works)

---

## How-to guides

### How to review a specific path

```
/copilot-review src/auth/
```

Pass any directory or file path as the first argument. Relative paths are resolved from the current working directory. The review targets only the specified path; it does not scan the rest of the project.

```
/copilot-review src/auth/middleware.py
```

A single file review is useful when you have made targeted changes and want a focused check before committing.

---

### How to filter to specific dimensions

```
/copilot-review --focus architecture,errors
```

The `--focus` flag accepts a comma-separated list of dimension IDs. Valid IDs: `architecture`, `tests`, `quality`, `errors`, `deps`, `wheels`.

Only the listed dimensions run; all others are skipped. This reduces review time when you already know which aspects to check.

```
/copilot-review src/ --focus deps,wheels
```

Arguments can be combined. Path comes first, flags follow.

---

### How to tune model and reasoning

**Change the model:**

```
/copilot-review --model gpt-4.1
```

The default model is `gpt-5.4`. Pass any model name supported by your Copilot CLI installation.

**Change reasoning effort:**

```
/copilot-review --reasoning medium
```

Valid values: `low`, `medium`, `high`. Default is `high`. Lower effort is faster but may miss subtler issues. Use `low` for quick sanity checks; use `high` for pre-release or pre-merge reviews.

**Combine both:**

```
/copilot-review src/ --focus quality,errors --model gpt-4.1 --reasoning medium
```

---

## Reference

### Command

```
/copilot-review [path] [--focus area1,area2] [--model name] [--reasoning level]
```

**Arguments:**

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | string | `.` (current directory) | Directory or file to review |
| `--focus` | comma-separated list | all 6 dimensions | Dimensions to run |
| `--model` | string | `gpt-5.4` | Copilot model to use |
| `--reasoning` | string | `high` | Copilot reasoning effort: `low`, `medium`, or `high` |

---

### Review dimensions

| ID | Focus area | What it examines |
|----|-----------|-----------------|
| `architecture` | Architecture | Module boundaries, dependency graph, separation of concerns, coupling/cohesion, design patterns, scalability |
| `tests` | Test coverage and correctness | Missing coverage, test quality, edge cases, assertion quality, test isolation, mocking appropriateness |
| `quality` | Code quality | Dead code, duplication, naming, idiomatic usage, cyclomatic complexity, readability |
| `errors` | Error handling and robustness | Error propagation, missing error cases, input validation, defensive coding, resource cleanup |
| `deps` | Dependency audit | Maintenance status, weight justification, redundancy, missing well-known alternatives, version constraints |
| `wheels` | Reinvented wheels | Hand-rolled implementations that duplicate well-known libraries; especially common in AI-generated code |

---

### Issue format

Every issue in the consolidated output uses this format:

```
## Issue: <concise title>
- **File**: <path:line>
- **Severity**: Critical | Major | Minor
- **Description**: <what is wrong and why it matters>
- **Evidence**: <file:line references confirming the issue>
- **Suggestion**: <concrete fix or alternative>
```

Issues are sorted by severity across all dimensions in the consolidated output. Critical issues appear first.

---

### What copilot-review does not flag

Each sub-review prompt explicitly instructs Copilot to skip:

- Style, formatting, or naming conventions
- Grammar or spelling in comments or strings
- "Consider doing X" suggestions that are not genuine problems
- Missing documentation or comments
- Theoretical edge cases that cannot realistically occur
- Reasonable abstractions that could theoretically be simpler
- Packages that are slightly outdated but have no known issues or security advisories

If Copilot is uncertain whether something is a genuine problem, it does not report it.

---

## How the review works

### Six parallel sub-reviews

copilot-review decomposes the review into six independent focus areas because a single undirected review prompt tends to produce broad, shallow findings. Focused prompts per dimension produce deeper, more actionable results in each area.

Each sub-review uses a dedicated prompt template that instructs Copilot to look only at its assigned dimension and to skip everything else. The prompts share a codebase summary generated during the discovery step, so Copilot has consistent context about the project structure, language, and dependencies.

### The discovery step

Before running any sub-reviews, copilot-review analyses the target path to build a codebase summary:

- Primary language and framework (detected from `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, etc.)
- Entry points and source directory structure
- Test setup and test directory location
- Dependency management approach and approximate dependency count
- Approximate lines of code and source file count

This summary is injected into every sub-review prompt. Without it, Copilot would need to re-discover the project context for each sub-review, producing inconsistent results.

### Consolidation

After all sub-reviews complete, findings from all six dimensions are merged into a single report. Duplicates (the same issue spotted by multiple dimensions) are deduplicated. The consolidated output sorts all issues by severity so you see the most important findings first regardless of which dimension found them.

### What counts as a "reinvented wheel"

The `wheels` dimension exists because AI-generated code has a characteristic pattern: LLMs tend to implement things from scratch rather than reaching for established libraries. A generated codebase might contain custom retry logic, a hand-rolled HTTP client wrapper, a custom argument parser, or a bespoke config file loader, all of which have well-maintained library equivalents.

The `wheels` sub-review specifically looks for these patterns. A finding is only reported when there is a well-maintained, popular library that does the same thing better. Simple utility functions under approximately 20 lines where a dependency would add more overhead than value are not flagged.
