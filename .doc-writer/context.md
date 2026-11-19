# Doc Writer Context

**Generated:** 2026-11-19
**Source:** /doc-writer:setup researcher
**Editable:** Yes -- manual edits are preserved until the next --refresh-context run. To make permanent changes, edit config.yaml and re-run setup.

## Project Summary

doc-writer is a Claude Code plugin (version 1.8.0, MIT) that writes, audits and fixes library documentation. It runs a pipeline of agents: a Doc Author plans and drafts Diataxis-structured pages, a Doc Editor normalizes terminology, fixes type blur, removes AI-writing patterns (measured with a vendored deslop scanner) and checks cross-references, and a Doc Persona tries to complete real tasks using only the docs, so gaps the builders cannot see get caught. It supports mkdocs-material, sphinx-shibuya, odoc and plain Markdown, and keeps its per-project state in a `.doc-writer/` folder.
Inferred from: README.md, `doc-writer/.claude-plugin/plugin.json`, the SKILL.md and agent files, `doc-writer/deslop/README.md`, the existing `docs/src/` pages.

The plugin is distributed from a marketplace repository that may hold other plugins; the docs site's front page lists plugins and `doc-writer.md` documents this one.

**What the reader actually touches** (document these, nothing deeper):
- Commands: `/doc-writer:setup` (flags `--reset`, `--refresh-context`), `/doc-writer:write` (flag `--skip-gap-scan`; auto-detects create mode vs update mode), `/doc-writer:review` (flag `--edit`), `/doc-writer:edit` (takes an issue description or page path), `/doc-writer:upgrade` (after a plugin update).
- Interactive prompts: structured multiple-choice questions, always with "Type something else" and "Chat about this" escape options; a page-inventory approval gate before writing; a PARTIAL-verdict decision step.
- Files in `.doc-writer/`: user-owned and safe to edit -- `config.yaml`, `rules.md`, `terminology.yaml`, `{doc_system}.md`, `context.md` (regenerated on refresh). Generated outputs to read, not edit -- `page-inventory.md`, `gap-report.md`, `editor-report.md`, `persona-report*.md`, `scenarios.yaml`, `author-notes.md`, `mli-enrichment.md` (odoc only). Internal working folders -- `.originals/` (upgrade baselines) and `.deslop/` (scanner snapshots).
- Outcome guarantees: generated docs are left uncommitted for review; `review` without `--edit` changes no doc files; `--edit` asks before changing anything.
- Requirement: the humanizer measurement needs `python3`; without it the Editor still runs and notes that measurements were skipped.

**Not for user docs:** the internals of `docs_scan.py` (its functions, view-building rules), `detect-project.sh`, `scan-exports.sh`, the vendored deslop files, agent prompt wording, and this repository's own tests, CI or docs build. Mention the deslop scanner by what it does for the user, credit it, and stop there.

## User Persona: Library maintainer using Claude Code

### Profile
- **Skill level:** advanced
- **What they know:** Uses Claude Code daily: starts sessions, runs slash commands, adds marketplaces and installs plugins with `/plugin`, and understands that agents act on the working tree. Reviews changes with `git diff`/`git status` and is comfortable discarding or keeping hunks before committing. Already knows their own project's documentation system (MkDocs Material, Sphinx, odoc or plain Markdown): its config file, how nav is declared, how to build and preview the site.
- **What to always explain:**
  - What each doc-writer command does, what it changes on disk, and which to run first (setup before anything else; write for creation or catch-up; review for a read-only audit; edit for targeted fixes; upgrade after updating the plugin).
  - The pipeline order -- gap detection, Author plan, inventory approval, Author write, Editor, Persona evaluation, revision loop, summary -- and which file each stage writes.
  - Every file in `.doc-writer/`: who writes it, when it is regenerated, and whether hand edits survive.
  - What the verdicts (PASS / PARTIAL / FAIL) mean and what the user is expected to decide.
  - Terms of art the plugin introduces: Diataxis types, "type blur", "persona", "gap report", "humanizer pass". Define on first use or link to the explanation section.
- **Their world:** They maintain an open source library, usually alone or with a few collaborators, and documentation lags behind the code. They want a published site that reads like a careful human wrote it, but they do not have the hours to write tutorials, how-tos and reference pages by hand, and generic "generate docs" prompts produce builder-centric pages full of AI tells. They will judge the plugin by the quality of a diff they review before committing.
- **How they found this library:** Searching for a Claude Code plugin that writes documentation, they landed on the repository. Alternatives they likely weighed: prompting Claude directly, API-reference generators (mkdocstrings, autodoc) that cover reference but not tutorials or guides, and hand-writing. The differentiators to make clear early: the Persona tests docs without reading source, the Editor enforces terminology and de-slops prose, and nothing is committed for them.

### Common Tasks
- **Install doc-writer and configure it for an existing project:** add the marketplace, install the plugin, run `/doc-writer:setup`, answer questions on personas, tone, doc system, navigation and use cases, and check the generated `.doc-writer/` files.
- **Generate documentation for a project that has none:** run `/doc-writer:write` in create mode, approve or trim the proposed page inventory, let the revision loop run, resolve PARTIAL issues, then review the uncommitted pages and build the site.
- **Update existing documentation after code changes:** run `/doc-writer:write` again; update mode runs gap detection, proposes new pages and `(refresh)` pages for stale content; `--skip-gap-scan` skips detection.
- **Audit existing documentation without changing it:** run `/doc-writer:review` and read the combined summary plus `gap-report.md`, `editor-report.md` and the persona reports; add `--edit` to apply Editor fixes after confirmation.
- **Fix specific issues from an audit:** run `/doc-writer:edit`, pick findings from existing reports or describe the change; only the affected pages change.
- **Add project-specific documentation rules:** edit `.doc-writer/rules.md` (additive to the non-overridable universal quality rules) and `.doc-writer/terminology.yaml` (canonical terms, variants, proper nouns); explain how agents pick these up on the next run.

### Writing Guidance for This Persona
- Assume they know Claude Code and git; do not explain how slash commands or `/plugin` work, but do state exactly which command to type and what appears next.
- Spell out the side effects of each command on files, especially what is overwritten, what is preserved, and what is left uncommitted.
- Use Claude Code's own vocabulary (session, slash command, plugin, marketplace, agent). Say "plugin" for doc-writer, not "skill" (see terminology.yaml).
- Examples should show a realistic library project (a small Python or TypeScript package with an MkDocs or Sphinx site), never doc-writer documenting itself.
- Show excerpts of real prompts, summaries and report sections where they help the reader recognize what they are looking at; keep them short and accurate to the current skill output formats.

## Use Cases

### Bootstrap a docs site for an undocumented library

**Problem:** A maintainer has a working library with a README and docstrings but no tutorials, how-tos or conceptual pages. Writing a full Diataxis set by hand takes days, and unguided AI drafts read as builder-centric and generic.
**What's possible:** `/doc-writer:setup` captures who the readers are and how the project's doc system is configured; `/doc-writer:write` proposes a page inventory for approval, drafts every type of page, edits them, and has a persona attempt real tasks with only the docs.
**Outcome:** A set of uncommitted pages in the docs folder, organized by Diataxis type, plus a summary with persona verdicts and editor changes, ready to review as a diff and build.
**Relevant persona(s):** Library maintainer using Claude Code
**Source:** inferred

### Keep docs in step with the code

**Problem:** After several releases, new public functions are undocumented and some pages describe old behavior. Finding which is which means cross-reading the code and every page.
**What's possible:** Re-running `/doc-writer:write` detects existing docs, produces a gap report of undocumented symbols and stale pages, and writes new pages or refreshes existing ones in place.
**Outcome:** New coverage for the missing symbols, refreshed pages where source changed, and a gap report showing what was covered.
**Relevant persona(s):** Library maintainer using Claude Code
**Source:** inferred

### Audit before a release, then fix only what matters

**Problem:** The maintainer wants to know whether the docs are good enough to ship without letting a tool rewrite them.
**What's possible:** `/doc-writer:review` runs gap detection, an Editor audit and persona evaluation without touching doc files; `/doc-writer:edit` then applies selected findings to only the affected pages.
**Outcome:** A combined audit summary with severity-tagged findings and per-persona verdicts, followed by small, targeted diffs.
**Relevant persona(s):** Library maintainer using Claude Code
**Source:** inferred

> These use cases were inferred from persona context and codebase analysis. To promote use cases to a documentation section, run `/doc-writer:setup` and provide explicit use cases.

## Tone: warm-businesslike

### Writing Rules
- Open each page with a 1-2 sentence introduction saying what the page covers and why the reader would want it.
- Give multiple examples per concept where it helps: the basic command first, then common variations (flags, update mode vs create mode, `--edit`).
- Include "Common mistakes" or "Troubleshooting" sections where relevant: running write before setup, editing generated reports expecting them to persist, missing `python3`, docs root path mismatches, non-converging revision loops.
- Use transition sentences between major sections so the page reads as a flow.
- Use admonitions for tips, warnings and important notes (for example: "nothing is committed", "context.md is regenerated on refresh").
- Warm but professional: no jokes, no first person, no casual asides. Address the reader as "you".

## Framework Preferences: mkdocs-material

Detailed mkdocs-material style preferences live in `.doc-writer/mkdocs-material.md`; the notes below are what this project's `mkdocs.yml` actually enables.

### Navigation Strategy
- Strategy: not recorded in config.yaml. Inferred **Sidebar only**: theme features include `navigation.sections` but not `navigation.tabs` or `navigation.indexes`. (Choice made by the researcher; re-run setup to set it explicitly.)
- All pages appear in the left sidebar; sections render as expandable groups. No tabs configuration needed.
- `docs_dir` is `docs/src`; nav is declared explicitly in `mkdocs.yml`, so any new page must be added to `nav:` or it will not appear.
- Current nav has two entries (front page and `doc-writer.md`); `doc-writer.md` is a single long page holding tutorial, how-to, reference and explanation sections. If the Author splits it into per-type pages, group them under a `doc-writer` nav section with an index page listing children with 1-sentence abstracts.
- Section index pages: include 1-sentence abstracts for each child.
- Front page (index.md / index.rst) is linked as "Overview" at the same level as the main docs sections (tabs or sidebar headings depending on nav strategy). Use "Overview" not "Home". (The current nav labels it "Home"; flag rather than silently change, since the front page covers the whole marketplace.)

### Features to Use
- **Admonitions** (`admonition`, `pymdownx.details`): `tip`, `warning`, `danger`, `info`, `example` per the guidance file; collapsible `???` blocks for optional detail such as full config field listings.
- **Code blocks** (`pymdownx.highlight`, `inlinehilite`, `content.code.copy`, `content.code.annotate`): always give a language; use `text` for Claude Code prompts and slash commands, `yaml` for `.doc-writer/` config, `bash` for shell; use `title=` for file paths like `.doc-writer/config.yaml`; annotations for explaining config fields.
- **Content tabs** (`pymdownx.tabbed`, alternate style): for the same task across doc systems (MkDocs Material / Sphinx / odoc / plain Markdown) or create vs update mode.
- **Mermaid diagrams** (superfences custom fence): good fit for the pipeline flow and revision loop in explanation pages.
- **attr_list / md_in_html**: available for small layout needs; use sparingly.
- **Permalinked TOC** (`toc` with `permalink`, `toc.follow`): keep headings stable and descriptive so deep links work.
- **Search** (`search.suggest`, `search.highlight`): favor headings containing the command names users will search for.

### Features NOT to Use
- `navigation.tabs` / `navigation.tabs.sticky` / `navigation.indexes`: not enabled.
- mkdocstrings / API autodoc: no plugin installed; there is no Python API to document. The "reference" is commands and config files, written by hand.
- `pymdownx.snippets`, `pymdownx.emoji`, `pymdownx.tasklist`, `pymdownx.keys`, `pymdownx.critic`, `footnotes`, `def_list`, `abbr`, `content.tabs.link`, blog, tags or social plugins: not enabled.
- Grid cards: the `md_in_html` extension is on but no card styling is configured; do not generate `grid cards` markup.
