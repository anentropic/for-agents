# Phase 9: enhanced setup Q&A, tone, user persona, and new planner/researcher agents - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Deepen the setup experience in three ways: (1) convert per-field audience questions from freeform prompts to infer+suggest AskUserQuestion interactions, (2) add tone selection and a user persona task Q&A, and (3) add a researcher agent that enriches config inputs into `.doc-writer/context.md` — a persisted file that all downstream agents read at runtime. Framework-specific follow-up Q&A (starting with mkdocs-material and plain-markdown) is also in scope as part of the enhanced setup flow. No changes to the core writing/review/edit pipeline logic.

</domain>

<decisions>
## Implementation Decisions

### Setup Q&A: infer+suggest pattern
- Every audience sub-field becomes its own AskUserQuestion (not a single freeform block)
- Researcher infers 2–4 suggestions per field using README, dependencies, and code patterns; one marked Recommended
- Fields that get infer+suggest: skill level, assumed knowledge, never-assume, domain context
- Fields that stay freeform: audience name, discovery story (too specific to infer)
- Assumed knowledge and never-assume use `multiSelect: true` — researcher infers 3–5 likely items as checkboxes; user picks, deselects, or adds via Other
- All setup AskUserQuestion blocks follow the Phase 8 mandatory trailing options pattern: "Type something else" (before divider) + "Chat about this" (final option)

### Tone field
- Three options (no library name references in labels):
  - "Just the facts" — minimal, no preamble, direct definitions, one example max. Like NumPy docs.
  - "Helpful and comprehensive, warm but businesslike" — clear explanations, multiple examples, structured. Like Django docs.
  - "Helpful and comprehensive, with personality and occasional humour" — same depth as above but with personality. Like FastAPI docs.
- Each option has a one-line description explaining what it means in practice
- Tone question uses the mandatory trailing options pattern: "Type something else" + "Chat about this"
- Researcher expands chosen tone into concrete writing rules stored in `context.md` (e.g. for "just the facts": no motivational intros, skip background sections, lead with function signature, one example max)
- Tone lives in `config.yaml` as a label; the expanded rules live in `context.md`

### User persona task Q&A
- Added within the audience definition flow, after skill level and assumed knowledge questions
- Researcher infers 3–5 likely user tasks from the codebase (e.g. for a rate-limiting library: "set up rate limiting", "configure per-route limits", "debug 429 errors")
- Presented as `multiSelect: true` AskUserQuestion — user picks, deselects, or adds via Other
- Follows the mandatory trailing options pattern: "Type something else" + "Chat about this"
- Tasks become part of the audience profile in `context.md` — used to inform Persona agent scenario generation

### Framework Q&A
- After doc system selection, researcher scans the framework config file (e.g. `mkdocs.yml`, `docusaurus.config.js`) and auto-answers what it can detect
- Framework-specific question sets are pre-authored as part of this phase (not dynamic runtime research)
- Questions cover important usage-preference choices that can't be inferred from config alone
- Both mkdocs-material and plain-markdown get question sets in Phase 9
- Framework Q&A follows the mandatory trailing options pattern
- **mkdocs-material reference config:** `../cookiecutter-python-uv-library/{{ cookiecutter.project_slug }}/mkdocs.yml` — use this as the default preferences baseline:
  - 2-level nav (navigation.sections, no navigation.tabs)
  - literate-nav + SUMMARY.md for nav generation
  - mkdocstrings for API reference (Google docstring style)
  - content tabs, Mermaid diagrams, code annotations, admonitions + collapsible details available
  - dark/light mode with system preference
  - No Blog plugin, no versioning (mike)

### Researcher agent
- Runs automatically at the end of `/doc-writer:setup` (and `--reset`)
- Also re-triggerable via `/doc-writer:setup --refresh-context` — re-runs researcher only, skips Q&A (for existing projects or after library changes)
- Reads: config.yaml (audiences, tone, doc system) + codebase (README, source files, framework config)
- Produces: `.doc-writer/context.md` — persisted, user-editable
- All agents (Author, Editor, Persona) read `context.md` at the start of each run, same as they read `config.yaml`. Graceful fallback if file missing.

### context.md contents
- Audience-expanded instructions: from sparse config fields, expand to concrete agent guidance — what this audience already knows, how they think, what they're trying to accomplish, what to avoid, what tone means for this audience
- Project domain summary: what the library does, who it's for, key concepts — so agents don't re-infer from source each run
- Tone-specific writing rules: concrete instructions derived from the chosen tone option
- Framework usage preferences: from framework Q&A answers — which features to use and when (e.g. "prefer content tabs for multi-language examples", "use Mermaid for architecture diagrams")
- **File splitting:** Claude's discretion — if framework or tone sections are only relevant to Author/Editor but not Persona, the planner may split into `context.md` (universal) and an agent-specific file. Decide based on content divergence.

### Claude's Discretion
- Exact structure and headings of `context.md`
- Whether to split context.md into multiple files (universal vs agent-specific) based on content divergence
- Which specific questions to include in the plain-markdown question set
- How the researcher handles projects with no README or minimal codebase signals
- Re-run update behaviour for context.md (overwrite vs merge with user edits)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing setup skill
- `doc-writer/skills/setup/SKILL.md` — Current Q&A flow, AskUserQuestion usage, re-run handling, file creation steps
- `doc-writer/skills/setup/defaults/config-template.yaml` — Config schema: audiences array, doc_system, paths, detected section
- `doc-writer/skills/setup/defaults/mkdocs-material.md` — Existing guidance file to be extended/updated
- `doc-writer/skills/setup/defaults/plain-markdown.md` — Existing guidance file to be extended/updated

### AskUserQuestion pattern (Phase 8)
- `doc-writer/skills/write/SKILL.md` — Reference implementation of Phase 8 AskUserQuestion pattern with mandatory trailing options ("Type something else" + "Chat about this") and User Interaction Pattern section
- `.planning/phases/08-doc-writer-skills-polish/08-CONTEXT.md` — Locked decisions for the trailing options pattern

### mkdocs-material reference config
- `../cookiecutter-python-uv-library/{{ cookiecutter.project_slug }}/mkdocs.yml` — Default mkdocs-material preferences; use as baseline for framework Q&A defaults and guidance file updates

### Existing agents (context.md consumers)
- `doc-writer/agents/doc-author.md` — Reads config.yaml; will need to also read context.md
- `doc-writer/agents/doc-editor.md` — Reads config.yaml; will need to also read context.md
- `doc-writer/agents/doc-persona.md` — Reads config.yaml; will need to also read context.md

### AskUserQuestion reference
- `/Users/paul/.claude/get-shit-done/references/questioning.md` — GSD's AskUserQuestion usage guide: freeform_rule, anti-patterns, option design

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 8 User Interaction Pattern section: already in all four skills — reuse exact same pattern for new setup AskUserQuestion blocks
- Auto-detection logic already in setup skill (Step 1: Project Detection Results) — feeds infer+suggest suggestions
- AskUserQuestion is available in all skill/agent contexts

### Established Patterns
- Phase 8 mandatory trailing options: every AskUserQuestion ends with "Type something else" + "Chat about this"
- freeform_rule from questioning.md: if user selects "Type something else" or types freeform — drop to plain text follow-up, never chain another AskUserQuestion
- `audiences:` stored as array even for single audience (Phase 1 locked decision)
- Guidance files are "copy and customize": plugin ships template, project gets editable copy in `.doc-writer/`

### Integration Points
- `context.md` sits alongside `config.yaml` in `.doc-writer/` — agents read both at run start
- `--refresh-context` flag added to the setup skill's re-run detection (Step 1) as a new branch
- Framework Q&A runs after doc system selection (currently Step 2b) — new Step 2b.5 or expanded Step 2b
- User persona task questions inserted into audience definition block, after assumed knowledge

</code_context>

<specifics>
## Specific Ideas

- The three tone options were inspired by NumPy (minimal), Django (warm/businesslike), FastAPI (personality) — these are good mental models for what each tone means, even though labels don't mention the libraries
- Cookiecutter template shows user's preferred mkdocs-material baseline — researcher should treat this as the default starting point for suggestions when mkdocs.yml is detected
- GSD's questioning.md is the authoritative reference for the freeform_rule — "Other" selections trigger plain-text follow-up, never another AskUserQuestion

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-enhanced-setup-q-a-tone-user-persona-and-new-planner-researcher-agents*
*Context gathered: 2026-03-17*
