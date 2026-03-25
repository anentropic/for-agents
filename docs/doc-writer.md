# doc-writer

A Claude Code plugin that writes and reviews library documentation using a three-agent pipeline.

- [Tutorial: Document a project from scratch](#tutorial-document-a-project-from-scratch)
- [How-to guides](#how-to-guides)
- [Reference](#reference)
- [How the pipeline works](#how-the-pipeline-works)

---

## Tutorial: Document a project from scratch

In this tutorial you will configure doc-writer for an existing project and run the full pipeline to produce a complete set of documentation files. By the end you will have a working `docs/` directory with authored, edited, and persona-validated pages ready to review before committing.

**Prerequisites:**
- doc-writer installed via `/plugin install github:anentropic/for-agents`
- An existing project open in Claude Code

### Step 1: Run setup

In your Claude Code session:

```
/doc-writer:setup
```

doc-writer will auto-detect your project's language and doc system, then ask four questions:

1. **Audience name** — describe who reads your docs (e.g. "Python developers building REST APIs")
2. **Skill level** — `beginner`, `intermediate`, or `advanced`
3. **Assumed knowledge** — what they already know, comma-separated
4. **Never assume** — what must always be explained, comma-separated

Setup also asks about common tasks the persona performs with the library. These are stored as `user_tasks` per persona in `config.yaml` and used by the Persona agent to generate realistic test scenarios.

Answer each question and press Enter. When asked about a secondary audience, select "No, continue" for a single-audience project.

When asked about the doc system, select the auto-detected default or choose `plain-markdown` from the list.

When asked about paths, press Enter to accept `docs/` and `src/`.

You should see:

```
## Setup Complete

Created `.doc-writer/` with:
- config.yaml — 1 audience(s), doc system: plain-markdown, paths configured
- plain-markdown.md — Documentation system guidance (editable)
- rules.md — Project-specific rules template (editable)
```

### Step 2: Run the full pipeline

```
/doc-writer:write
```

The pipeline runs four stages automatically. You will see progress output as each stage completes:

1. **Gap detection** — scans exported symbols and reports how many lack documentation coverage
2. **Author** — writes draft pages for all gaps
3. **Editor** — normalises terminology, fixes type blur, removes AI writing patterns, verifies cross-references
4. **Persona** — simulates your configured audience attempting real goals in the docs

### Step 3: Handle persona verdicts

After the Persona stage, one of three things happens:

**All PASS** — pipeline completes and shows the Summary Report. Skip to Step 4.

**Any FAIL** — the pipeline automatically triggers a revision pass (up to 3 passes total). You will see which pages failed and why. The pipeline reruns the Author, Editor, and Persona stages on the failing pages automatically. If FAILs persist after 3 passes, you see an escalation report listing what could not be resolved.

**Only PARTIAL verdicts** — the pipeline presents a numbered list of friction points for your approval:

```
## PARTIAL Issues Requiring Your Decision

1. [Paul, S2] docs/getting-started.md > "Installation"
   Issue: Installation section references pip but project uses poetry
   Suggested fix: Replace pip install with poetry add example

Enter numbers to approve (e.g., "1,3"), "all", or "none":
```

Type `all` to apply all suggestions, `none` to skip them, or specific numbers like `1,3`.

### Step 4: Review the output

```
git diff docs/
```

The pipeline never commits. Review the generated files and commit when satisfied.

**What you learned:**
- How to configure doc-writer for an audience
- What the four pipeline stages do
- How to handle PARTIAL and FAIL verdicts
- How to review generated output before committing

**Next steps:**
- [How to make targeted fixes after a review](#how-to-make-targeted-fixes)
- [How to audit without regenerating](#how-to-audit-documentation-without-regenerating)
- [How the pipeline works](#how-the-pipeline-works)

---

## How-to guides

### How to run the full documentation pipeline

**Prerequisites:** `.doc-writer/config.yaml` exists. Run `/doc-writer:setup` if not.

```
/doc-writer:write
```

To skip gap detection (useful when re-running after manual edits):

```
/doc-writer:write --skip-gap-scan
```

The pipeline runs Author → Editor → Persona in sequence. If any Persona scenario returns FAIL, the pipeline reruns targeted pages automatically (up to 3 total passes). PARTIAL verdicts pause for your approval before the Summary Report.

The Summary Report lists every page created or modified, Editor change counts, and per-scenario Persona verdicts.

**Nothing is committed.** Review with `git diff {docs_root}` and commit manually.

---

### How to set up doc-writer for a project

**First-time setup:**

```
/doc-writer:setup
```

Answer the interactive questions for audience, doc system, and paths. Setup creates three files in `.doc-writer/`:

- `config.yaml` — audience definitions and paths
- `{doc_system}.md` — formatting guidance (editable)
- `rules.md` — project-specific quality rules (editable)

**Update an existing configuration:**

```
/doc-writer:setup
```

If `config.yaml` already exists, setup shows the current configuration and asks what to update: `audiences`, `doc system`, `paths`, `rules`, or `guidance file`. Select an option and follow the prompts. Only the selected field is changed; all others are preserved.

**Reset configuration from scratch:**

```
/doc-writer:setup --reset
```

Prompts for confirmation before overwriting existing config, guidance, and rules files.

**Re-run context enrichment only:**

```
/doc-writer:setup --refresh-context
```

Requires an existing `.doc-writer/config.yaml`. Skips all Q&A and jumps directly to the researcher agent to regenerate `.doc-writer/context.md` from the current config. Use this after manually editing `config.yaml` (e.g., adding a persona or changing the tone) without wanting to step through the full interactive setup again.

If no config exists, setup will tell you to run `/doc-writer:setup` first.

**After setup,** edit `.doc-writer/rules.md` to add any project-specific documentation rules (e.g. "always show error handling in code examples"). Edit `.doc-writer/{doc_system}.md` to customise formatting preferences.

---

### How to make targeted fixes

Use this when you have specific issues to fix from a previous review or review report, faster than regenerating all pages.

**From existing report issues:**

```
/doc-writer:edit
```

If `.doc-writer/editor-report.md` or any persona report exists, the command displays a numbered list of issues grouped by source (Editor, Persona). Select by number:

```
Select issues to fix (e.g., "1,3" or "all" or just type a description):
```

Type `1,3` to fix specific issues, `all` to fix all listed issues, or type a freeform description.

**From a freeform instruction (no report needed):**

```
/doc-writer:edit fix the installation steps in getting-started.md
```

Any non-numeric argument is treated as a freeform instruction. The command passes it directly to the Author agent without showing a selection prompt.

The edit workflow runs Author (targeted revision) → Editor (quality pass on changed pages only). Persona evaluation does not run after edit. Use `/doc-writer:review` afterwards if you want persona validation.

**Nothing is committed.** Review with `git diff {docs_root}` and commit manually.

---

### How to audit documentation without regenerating

Runs gap detection, Editor quality checks, and Persona validation against existing docs. Does not create new pages.

**Prerequisites:** Documentation files must exist in `paths.docs_root`. Run `/doc-writer:write` first if the directory is empty.

```
/doc-writer:review
```

The command runs three steps:

1. **Gap detection** — compares exported symbols against documentation coverage, writes `.doc-writer/gap-report.md`
2. **Editor audit** — runs all four passes (terminology, Diataxis type integrity, humanizer, cross-reference linking) and reports issues in `.doc-writer/editor-report.md` (no files edited by default)
3. **Persona evaluation** — simulates your configured audience(s) attempting goals, writes `.doc-writer/persona-report.md`

The command presents a combined summary on completion:

```
## Documentation Audit Summary

### Gap Detection
- Total exported symbols: 12
- Documented: 9 (75%)
- Undocumented: 3

### Editor Findings
- BLOCKING issues: 1
- SUGGESTION issues: 4
- NITPICK issues: 2

### Persona Verdicts
**Paul:** S1: PASS, S2: PARTIAL, S3: PASS

### Overall Assessment
Documentation covers core workflows but the configuration reference is missing ...

Next steps:
- Run /doc-writer:edit to fix specific issues
- Run /doc-writer:write for full regeneration
```

> **Note:** By default, `doc-writer:review` is read-only — the Editor audits docs and writes findings to `.doc-writer/editor-report.md` without editing any files. Pass `--edit` to apply Editor fixes (a confirmation gate lists affected files before any changes are made).

---

## Reference

### Commands

#### `doc-writer:setup`

Configures doc-writer for a project. Creates `.doc-writer/` with config, guidance, and rules files.

**Argument:** `[--reset | --refresh-context]`

| Argument | Description |
|----------|-------------|
| *(none)* | First-time setup if no config exists; update flow if config exists |
| `--reset` | Overwrite existing config after confirmation prompt |
| `--refresh-context` | Re-run the researcher agent to regenerate `context.md`; skips all Q&A; requires existing config |

**Output files created:**

| File | Description |
|------|-------------|
| `.doc-writer/config.yaml` | Audience definitions, doc system, paths |
| `.doc-writer/{doc_system}.md` | Formatting guidance for the selected doc system |
| `.doc-writer/rules.md` | Project-specific quality rules (additive to universal rules) |

---

#### `doc-writer:write`

Runs the full Author → Editor → Persona pipeline with gap detection and revision loop.

**Argument:** `[--skip-gap-scan]`

| Argument | Description |
|----------|-------------|
| *(none)* | Run gap detection, then Author → Editor → Persona pipeline |
| `--skip-gap-scan` | Skip gap detection; go straight to Author stage |

**Pipeline stages:**

| Stage | What happens | Output |
|-------|-------------|--------|
| Gap Detection | Scans `paths.source_root` for exported symbols not covered by existing docs | `.doc-writer/gap-report.md` |
| Author | Writes draft documentation pages for all undocumented symbols | New/updated files in `paths.docs_root` |
| Editor | Runs terminology, Diataxis type, humanizer, and cross-reference passes | Updates doc files in place; `.doc-writer/editor-report.md` |
| Persona | Simulates audience(s) attempting goals | `.doc-writer/persona-report.md` (or per-audience variants) |
| Verdict | Routes FAIL verdicts back to Author for revision (max 3 passes); presents PARTIAL issues for approval | Summary report |

**Revision loop:** FAIL verdicts trigger targeted revision passes (max 3). PARTIAL verdicts pause for project author approval. After max passes, unresolved FAILs are escalated in an escalation report.

**Nothing is committed.** All output files are left uncommitted for review.

---

#### `doc-writer:edit`

Makes targeted fixes to specific documentation pages. Does not regenerate unaffected pages.

**Argument:** `[issue description or page path]`

| Argument | Description |
|----------|-------------|
| *(none)* | Interactive: displays issues from existing reports for selection |
| Freeform text | Passes instruction directly to Author; skips selection prompt |
| Number selection | Valid only in interactive mode response |

**Stages:** Author (targeted revision) → Editor (changed pages only). Persona does not run.

**Nothing is committed.**

---

#### `doc-writer:review`

Audits existing documentation without generating new content.

**Argument:** `[--edit]`

| Argument | Description |
|----------|-------------|
| *(none)* | Report-only mode (default): Editor audits docs but does not edit any files |
| `--edit` | Apply Editor fixes; shows a confirmation gate listing files before any changes are made |

**Stages:** Gap Detection → Editor (reports issues; applies fixes only with `--edit`) → Persona (evaluation only).

**Output files:**

| File | Description |
|------|-------------|
| `.doc-writer/gap-report.md` | Undocumented exported symbols |
| `.doc-writer/editor-report.md` | Editor findings (BLOCKING, SUGGESTION, NITPICK) |
| `.doc-writer/persona-report.md` | Persona verdicts and gap analysis |

**Nothing is committed.**

---

### Configuration files

#### `.doc-writer/config.yaml`

Created by `doc-writer:setup`. Read by all pipeline commands at startup.

```yaml
version: 1

user_personas:
  - name: "Python developers building REST APIs"
    skill_level: "intermediate"        # beginner | intermediate | advanced | expert
    assumed_knowledge:
      - "Python basics"
      - "HTTP fundamentals"
    never_assume:
      - "async/await patterns"
      - "virtual environment setup"
    user_tasks:                         # common tasks this persona performs with the library
      - "Make API requests"
      - "Handle authentication"
    domain_context: "building REST APIs for web applications"   # optional
    discovery_story: "searching for a Python HTTP client"       # optional

tone: "warm-businesslike"              # just-the-facts | warm-businesslike | personality

doc_system: "plain-markdown"           # plain-markdown | mkdocs-material | sphinx-shibuya | odoc

api_reference: ""                      # path to auto-generated API reference, if any

use_cases:                             # structured use cases (empty array if skipped during setup)
  - title: "Rate-limit API endpoints"
    problem: "API is hammered by bots, response times spike"
    capability: "Per-route request limits with automatic 429 responses"
    outcome: "Legitimate users stay under 200ms; abusive clients are blocked"

use_cases_section: true                # true = Use Cases becomes a docs section; false = context only

paths:
  docs_root: "docs/"
  source_root: "src/"

detected:
  language: "python"
  doc_system: "plain-markdown"
  existing_docs: true
```

**Field notes:**

- `user_personas` is always an array, even for a single persona.
- `domain_context` and `discovery_story` are optional. They are used by the Persona agent to generate more realistic test scenarios.
- `api_reference` is optional. When set, the Editor agent links inline code mentions to the reference location.
- `doc_system` must match an existing guidance file in `.doc-writer/`. Built-in options: `plain-markdown`, `mkdocs-material`, `sphinx-shibuya`, `odoc`. Custom names are allowed but require you to create the guidance file manually.
- `tone` controls the writing voice across all generated pages. The label (`just-the-facts`, `warm-businesslike`, `personality`) is stored here; expanded per-tone writing rules are generated into `.doc-writer/context.md` by the researcher. Update via `/doc-writer:setup` (select "Tone").
- `user_tasks` on each persona entry lists common tasks that persona performs with the library. The Persona agent uses these tasks to generate realistic test scenarios. Update via `/doc-writer:setup` (select "User Personas" → "Edit persona").
- `use_cases` is an array of structured use case objects (`title`, `problem`, `capability`, `outcome`). It is empty if the user skipped use case capture during setup. Use cases inform documentation writing context and, when `use_cases_section` is `true`, generate a Use Cases documentation section.
- `use_cases_section` is a boolean. When `true`, the Author agent proposes a Use Cases section alongside the four Diataxis quadrants (Tutorials, How-To Guides, Explanation, Reference). When `false`, use cases inform writing context only and do not appear as a visible docs section. Toggle via `/doc-writer:setup` (select "Use Cases" → "Toggle section").

---

#### `.doc-writer/rules.md`

Project-specific quality rules. These are additive to the five universal rules enforced by all agents. Edit directly; no special syntax required, agents interpret natural language. This file is read at the start of every Author, Editor, and Persona run.

**Example rules:**

```markdown
## Project Rules

- Always include a "Requirements" section in how-to guides listing minimum versions
- Code examples must show error handling, not just the happy path
- Use American English spelling throughout
```

---

#### `.doc-writer/{doc_system}.md`

Formatting guidance for the active documentation system. Created by `doc-writer:setup` from a built-in template. Edit to customise preferences (heading style, callout syntax, link format, etc.).

---

#### `.doc-writer/terminology.yaml`

Written automatically by the Editor after its first run. Stores the canonical form of project-specific terms resolved from source code. Contains an `overrides` section where you can force specific term choices that take highest precedence over auto-detected forms.

---

#### `.doc-writer/gap-report.md`

Written by `doc-writer:write` (Step 1) and `doc-writer:review` (Step 1). Lists exported symbols from `paths.source_root` that have no documentation coverage. Used by the Author agent to prioritise what to write.

---

#### `.doc-writer/editor-report.md`

Written by the Editor agent after each pass. Contains per-file findings at three severity levels:

| Severity | Meaning |
|----------|---------|
| BLOCKING | Factual error, broken link, accuracy mismatch with source, leaked internal detail |
| SUGGESTION | AI-writing pattern fixed, inconsistent term normalised, unclear wording rewritten |
| NITPICK | Style adjustment (em dash replaced, curly quote fixed) |

---

#### `.doc-writer/persona-report.md`

Written by the Persona agent. For multiple audiences, written as `.doc-writer/persona-report-{audience-name-slug}.md`.

Contains per-scenario verdicts:

| Verdict | Meaning |
|---------|---------|
| PASS | User can accomplish the goal from start to finish |
| PARTIAL | Goal is achievable but with friction or confusion |
| FAIL | User cannot accomplish the goal, required information is missing or critically wrong |

Only FAIL verdicts trigger automatic revision passes. PARTIAL verdicts are presented to the project author for optional approval.

---

## How the pipeline works

### The three-agent architecture

doc-writer uses three specialised agents that run in sequence. Each agent has a distinct role and cannot perform the others' functions.

**Doc Author** writes documentation from the end user's perspective. It scans source code, reads test files for realistic usage patterns, classifies each page by Diataxis type (tutorial, how-to, explanation), and writes accordingly. It explicitly excludes test utilities, CI configuration, development scripts, and internal modules from user-facing content.

**Doc Editor** reviews and edits what the Author produced. It runs four passes in strict order: terminology consistency (using source code as the canonical authority for symbol names), Diataxis type integrity (detecting and fixing pages that mix documentation purposes), humanizer (removing AI writing patterns like em dashes, significance inflation, copula avoidance, and filler phrases), and cross-reference linking (adding links from inline code mentions to API reference entries when a reference location is configured). The Editor does not write new documentation content; gaps are recorded as BLOCKING feedback items for the Author.

**Doc Persona** validates the output by simulating real user journeys. It reads only the documentation files (not source code), generates 3-5 goal-oriented scenarios filtered through the configured audience's skill level, then attempts to accomplish each goal using only the docs and their navigation. It assigns PASS, PARTIAL, or FAIL verdicts and identifies the specific page and section responsible for each gap.

### The revision loop

The pipeline runs a maximum of three passes. On each pass, the Author, Editor, and Persona stages all execute. The routing logic after each Persona evaluation:

- All scenarios PASS → done, proceed to Summary Report
- Any FAIL exists and pass count < 3 → Author revises only the failing pages, Editor re-runs on changed pages, Persona re-evaluates all scenarios
- Any FAIL exists and pass count = 3 → escalation report listing unresolved issues for manual intervention
- Only PARTIAL verdicts remain → pause for project author approval of specific fix suggestions

On revision passes, the Author receives a targeted list of failing pages and the specific gaps identified. It does not regenerate passing pages. The Persona reuses the same scenarios across all passes (it does not regenerate) so convergence tracking is consistent.

### Quality rule layers

Quality is enforced at two layers:

**Universal rules** are baked into all three agents and cannot be overridden:

1. No internal details — test utilities, CI config, dev scripts, and internal modules never appear in user-facing docs
2. Working code examples required — every documented feature has at least one realistic, runnable example
3. Consistent structure — all pages of the same Diataxis type follow the same template
4. Cross-reference code mentions — inline code mentions link to API reference entries when a reference is configured
5. Audience-calibrated language — vocabulary and explanation depth match the configured audience; nothing from the `never_assume` list appears without explanation

**Project rules** in `.doc-writer/rules.md` are additive. They extend the universal baseline but cannot weaken or bypass it. Write them as natural language instructions; agents interpret them directly.

### Why three agents instead of one

A single agent writing documentation has a perspective problem: it knows the codebase internals, so it naturally writes from the builder's viewpoint, referencing implementation details, skipping user-facing context, and assuming knowledge the reader does not have.

Separating writing, editing, and audience validation into three agents with distinct file access rules enforces perspective separation structurally. The Persona agent has no access to source code by design. It can only navigate documentation the way a real user would, so its verdicts reflect the actual end-user experience rather than an insider's assessment.
