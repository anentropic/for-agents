# Page Inventory — Update Run

**Generated:** 2026-03-25
**Mode:** Update (targeted additions and corrections to existing pages only)

## Scope

`docs/copilot-review.md` is accurate and complete — no changes proposed.

All six items from the gap report fall inside `docs/doc-writer.md`. This inventory
describes exactly which sections within that file need additions or corrections.
No new pages are proposed.

---

## Proposed Changes to `docs/doc-writer.md`

| # | Location in file | Change type | Gap addressed |
|---|-----------------|-------------|---------------|
| 1 | **Tutorial > Step 1: Run setup** — paragraph describing the four setup questions | Addition | `user_tasks` persona field is not mentioned anywhere in the tutorial; readers who follow Step 1 will not see it captured during setup |
| 2 | **How-to > How to set up doc-writer for a project > "First-time setup"** | Addition | Add `--refresh-context` as a distinct operation with its own sub-heading, description, and usage; currently absent |
| 3 | **How-to > How to audit documentation without regenerating** — the prose description of Step 2 and the blockquote Note at the end of the section | Correction | Both the prose ("applies fixes directly to doc files") and the Note ("The Editor applies fixes directly to docs during the review") are factually wrong; the current default is report-only; `--edit` enables edits after a confirmation gate |
| 4 | **Reference > `doc-writer:setup` — Argument table** | Addition | Add `--refresh-context` row; currently the table only shows `--reset` |
| 5 | **Reference > `doc-writer:review` — Argument section** | Correction + Addition | Currently reads "Argument: none"; must be corrected to show `[--edit]`; add an argument table explaining the default (report-only) and the `--edit` behaviour (apply fixes after confirmation) |
| 6 | **Reference > `.doc-writer/config.yaml` — schema block** | Addition | Three new top-level fields missing from the schema: `tone`, `use_cases`, `use_cases_section`; also the persona entry is missing `user_tasks` |
| 7 | **Reference > `.doc-writer/config.yaml` — Field notes** | Addition | Add bullet entries explaining `tone` (label stored here; expanded writing rules live in `context.md`), `use_cases` (array of structured use case objects; empty array if user skipped), `use_cases_section` (boolean; promotes use cases to a documentation section alongside the four diataxis quadrants), and `user_tasks` (list of common tasks per persona; expanded task descriptions live in `context.md`) |

---

## Change Details

### Change 1 — Tutorial Step 1: mention `user_tasks` during persona capture

**Where:** Paragraph beginning "doc-writer will auto-detect your project's language and doc system, then ask four questions:"

**What to add:** The four-question list currently omits that the persona capture also collects common tasks (`user_tasks`). The tutorial should mention that setup asks about typical tasks the persona performs with the library. This keeps the tutorial accurate to the actual setup flow (which asks "common tasks they perform with this library" as part of persona description).

**Suggested addition:** Extend or note after question 4 that setup also infers or asks about common tasks the persona performs — and that all of this is stored per-persona in `config.yaml`.

---

### Change 2 — How-to: document `--refresh-context`

**Where:** Section "How to set up doc-writer for a project", after the `--reset` sub-section.

**What to add:** New sub-section:

**Re-run context enrichment only:**

```
/doc-writer:setup --refresh-context
```

Requires an existing `.doc-writer/config.yaml`. Skips all Q&A and jumps directly to the researcher agent (Step 5 of the setup flow) to regenerate `.doc-writer/context.md` from the current config. Use this after manually editing `config.yaml` (e.g., adding a persona or changing the tone) without wanting to step through the full interactive setup again.

If no config exists, setup will tell you to run `/doc-writer:setup` first.

---

### Change 3 — How-to: correct the `doc-writer:review` description

**Where:** Section "How to audit documentation without regenerating", Step 2 description and the blockquote Note.

**Current text (wrong):**
- Prose: "Editor audit — runs all four passes … and applies fixes directly to doc files"
- Note: "The Editor applies fixes directly to docs during the review (this is by design; the review command's value is the Persona verdicts on top of already-edited pages). Use `git diff` to see what changed."

**Corrected text:**
- Prose: "Editor audit — runs all four passes … and **reports issues** in `.doc-writer/editor-report.md` (no files edited by default)"
- Note: Remove the incorrect "applies fixes directly" Note. Replace with accurate information: the default is report-only; pass `--edit` to apply fixes (see `doc-writer:review --edit` in the Reference).

---

### Change 4 — Reference: add `--refresh-context` to `doc-writer:setup` argument table

**Where:** Reference > `doc-writer:setup` > Argument table.

**Current table:**

| Argument | Description |
|----------|-------------|
| *(none)* | First-time setup if no config exists; update flow if config exists |
| `--reset` | Overwrite existing config after confirmation prompt |

**Updated table** (add row):

| Argument | Description |
|----------|-------------|
| *(none)* | First-time setup if no config exists; update flow if config exists |
| `--reset` | Overwrite existing config after confirmation prompt |
| `--refresh-context` | Re-run the researcher agent to regenerate `context.md`; skips all Q&A; requires existing config |

---

### Change 5 — Reference: correct `doc-writer:review` argument section

**Where:** Reference > `doc-writer:review`.

**Current text:**
```
**Argument:** none
```

**Corrected text:**

```
**Argument:** `[--edit]`

| Argument | Description |
|----------|-------------|
| *(none)* | Report-only mode (default): Editor audits docs but does not edit any files |
| `--edit` | Apply Editor fixes; shows a confirmation gate listing files before any changes are made |
```

Also remove or correct the sentence in the Stages line "Editor (applies fixes)" — change to "Editor (reports issues; applies fixes only with `--edit`)".

---

### Change 6 — Reference: add missing fields to `config.yaml` schema block

**Where:** Reference > `.doc-writer/config.yaml` > fenced YAML code block.

**Fields to add:**

1. `tone` — top-level field, after `doc_system`
2. `use_cases` — top-level array field, after `tone`
3. `use_cases_section` — top-level boolean, after `use_cases`
4. `user_tasks` — inside each persona entry, after `never_assume`

**Updated schema block (additions in context):**

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

---

### Change 7 — Reference: add Field notes for new fields

**Where:** Reference > `.doc-writer/config.yaml` > Field notes bullets.

**Bullets to add:**

- `tone` controls the writing voice across all generated pages. The label (`just-the-facts`, `warm-businesslike`, `personality`) is stored here; expanded per-tone writing rules are generated into `.doc-writer/context.md` by the researcher. Update via `/doc-writer:setup` (select "Tone").
- `user_tasks` on each persona entry lists common tasks that persona performs with the library. The Persona agent uses these tasks to generate realistic test scenarios. Update via `/doc-writer:setup` (select "User Personas" → "Edit persona").
- `use_cases` is an array of structured use case objects (`title`, `problem`, `capability`, `outcome`). It is empty if the user skipped use case capture during setup. Use cases inform documentation writing context and, when `use_cases_section` is `true`, generate a Use Cases documentation section.
- `use_cases_section` is a boolean. When `true`, the Author agent proposes a Use Cases section alongside the four diataxis quadrants (Tutorials, How-To Guides, Explanation, Reference). When `false`, use cases inform writing context only and do not appear as a visible docs section. Toggle via `/doc-writer:setup` (select "Use Cases" → "Toggle section").

---

## API Reference Status

No API reference detected. This is a plugin (skill) project; there is no auto-generated symbol reference. Inline `code` mentions use plain formatting without links.

## Audience Targeting

Single persona: "Paul — solo developer building projects with Claude Code and open source libraries" (expert). All changes target this persona. No explanation of basic concepts needed; direct factual accuracy and completeness are the priorities.

## Coverage After Changes

All six items from `.doc-writer/gap-report.md` will be addressed:

| Gap | Change # |
|-----|---------|
| `--refresh-context` argument | 2 (how-to), 4 (reference) |
| `tone` configuration field | 6 (schema), 7 (field notes) |
| `use_cases` configuration field | 6 (schema), 7 (field notes) |
| `use_cases_section` configuration field | 6 (schema), 7 (field notes) |
| `user_tasks` persona field | 1 (tutorial), 6 (schema), 7 (field notes) |
| `doc-writer:review --edit` argument + factual error correction | 3 (how-to), 5 (reference) |
