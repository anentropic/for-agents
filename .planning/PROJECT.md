# Doc Writer Agent

## What This Is

A Claude Code plugin (multi-agent team) that writes and reviews library/package documentation to publication quality. Three specialized agents — Author, Editor, and User Persona — collaborate to produce docs that solve the fundamental problem: the agent that built a feature has too much insider context to document it well for users. Supports mkdocs-material, sphinx-shibuya, odoc (OCaml), and plain-markdown doc systems out of the box, with unknown framework support via dynamic research.

## Vocabulary

- **Project author**: the maintainer who invokes the plugin (i.e. the CC user)
- **End user**: a user of the documented library/package

## Core Value

Produce library documentation that the project author can publish with minimal tweaks — docs written from the end user's perspective, not the builder's.

## Requirements

### Validated

- ✓ Three-agent architecture: Doc Author, Editor, User Persona — v1.0
- ✓ Doc Author writes content guided by diataxis framework and quality rules — v1.0
- ✓ Editor reviews for consistency, gaps, accuracy, and applies humanizer — v1.0
- ✓ User Persona reviews from target audience perspective with self-generated test scenarios — v1.0
- ✓ Layered quality rules: universal defaults baked into agents + project-specific overrides in config — v1.0
- ✓ Universal rule: no internal/maintainer details (test utils, dev scripts, CI config, justfile recipes) — v1.0
- ✓ Universal rule: every feature/API must include a working code example — v1.0
- ✓ Universal rule: consistent structure for same-type pages (same template) — v1.0
- ✓ Universal rule: all inline `code` mentions linked to relevant API Reference item — v1.0
- ✓ Per-project audience configuration via setup Q&A (remembered across sessions) — v1.0
- ✓ User Persona generates test scenarios from project context without manual authoring — v1.0
- ✓ Content-first output with doc-system-specific rules (mkdocs-material, sphinx-shibuya, odoc, plain-markdown) — v1.0
- ✓ Works as standalone CC plugin (invokable by any CC user) — v1.0 (packaged with plugin.json + marketplace.json)
- ✓ Works as GSD integration (invokable at milestone boundaries) — v1.0
- ✓ On-demand invocation via /doc-writer:write, /doc-writer:review, /doc-writer:edit — v1.0
- ✓ Extensible quality rules — user can add custom rules to project config — v1.0
- ✓ Per-project config for doc system (mkdocs-material, sphinx-shibuya, odoc, plain-markdown) — v1.0
- ✓ Doc-researcher agent enriches project context from source code and framework config — v1.0
- ✓ Unknown framework support: researcher generates guidance, Q&A, and scaffold files dynamically — v1.0
- ✓ OCaml/odoc first-class support with .mld scaffolds, cross-reference rules, dune wiring — v1.0
- ✓ Scaffold variable substitution covers all frameworks generically (9-variable inference table) — v1.0

### Active

## Current Milestone: v1.4.0 Content & Navigation

**Goal:** Richer content types (Use Cases, Concepts), smarter nav structure for sphinx-shibuya and mkdocs-material, close OCaml/odoc gaps, and mermaid diagram support.

**Target features:**
- Use Cases setup Q&A context capture (before User Personas), optional promotion to docs section
- Default Concepts page proposal under Explanation
- Sphinx-shibuya nav: three top-tab strategies (none, "Docs" tab, sections-as-tabs with dropdowns), section index abstracts
- MkDocs-material nav: same top-tab strategies (without dropdowns), section index abstracts
- Mermaid diagram awareness in doc-author across all frameworks
- OCaml/odoc: scan-exports.sh language case, doc-author .mld/.mli handling

### Out of Scope

- Auto-generating API reference from code (tools like typedoc/pydoc handle this) — focus is on narrative docs
- Doc site hosting or deployment — this writes content, not infrastructure
- Non-library docs (blog posts, marketing pages, internal wikis) — scoped to library/package documentation
- Automated publishing — the maintainer decides when to publish
- ~~OCaml doc-author .mld/.mli file handling~~ — moved to v1.4.0 Active scope

## Context

**Shipped v1.0:** 13 phases, 28 plans, 164 commits. 34 files in `doc-writer/`, 8,167 lines inserted. 2026-03-02 → 2026-03-19 (17 days).

Tech stack: Markdown skill files, bash test scripts (bats), YAML config templates, Python conf.py scaffold, Sexp dune templates.

**Architecture shipped:**
- `doc-writer/agents/`: doc-author.md, doc-editor.md, doc-persona.md, doc-researcher.md
- `doc-writer/skills/`: setup/SKILL.md, write/SKILL.md, review/SKILL.md, edit/SKILL.md
- `doc-writer/skills/setup/defaults/`: guidance files (mkdocs-material.md, sphinx-shibuya.md, odoc.md, plain-markdown.md), Q&A files (*.qa.md), scaffold templates
- `doc-writer/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`
- `tests/`: bats test suites covering all phases

**Known issues / v2 candidates:**
- doc-author has no .mld/.mli file handling for odoc projects (writes .md to docs_root instead of .mld to doc/)
- scan-exports.sh has no OCaml language case (unstructured gap detection for OCaml projects)
- 8 phases have `nyquist_compliant: false` in VALIDATION.md (pre-dates Nyquist adoption; tests pass, frontmatter not updated)

## Constraints

- **Platform**: Claude Code plugin — must work within CC's agent/skill system
- **Dependencies**: Incorporates diataxis-documentation and humanizer guidance into agent system prompts
- **Quality bar**: Docs should need only minimal manual tweaks before publishing
- **Agent workflow**: Author > Editor > Persona pipeline (serial); multi-audience Personas run in parallel

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Three-agent architecture over single-agent | Separates writing, quality, and audience validation — mirrors how good doc teams work | ✓ Good — clean separation of concerns, each agent has a single job |
| Content-first, doc-system-agnostic with system-specific guidance files | Maximizes reuse; framework specifics in separate .md files loaded at runtime | ✓ Good — added sphinx-shibuya and odoc with zero core changes |
| Layered rules (universal + project config) | Universal rules enforce baseline quality; project config handles audience, system, custom needs | ✓ Good — extensible without touching agent system prompts |
| User Persona generates own test scenarios | Maintainer shouldn't have to author test cases | ✓ Good — validated in design, enables true perspective-shifted validation |
| Author > Editor > Persona pipeline order | Most natural: write first, then review, then validate from user perspective | ✓ Good — pipeline converges with BLOCKING-only revision triggers |
| Plugin packaged in doc-writer/ subdirectory with marketplace.json | Enables multi-plugin repo expansion without restructuring | ✓ Good — clean isolation, marketplace-ready |
| Q&A data files (.qa.md) separate from skill body | Enables framework-specific Q&A without editing SKILL.md for each framework | ✓ Good — added odoc Q&A with zero SKILL.md core changes |
| Generic variable inference table in scaffold substitution | Covers all frameworks without framework-specific substitution logic | ✓ Good — closed P11-03 blocker and future-proofed scaffold additions |
| doc-researcher agent for context enrichment | Separate agent reads source + framework config, writes context.md before pipeline | ✓ Good — downstream agents get enriched context without doing their own scanning |

---
## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-21 after Phase 14 (Foundations) complete*
