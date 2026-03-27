# Milestones

## v1.5.0 Plugin Upgrade Helpers (Shipped: 2026-03-27)

**Phases completed:** 4 phases, 5 plans, 10 tasks

**Key accomplishments:**

- Setup skill now writes plugin_version from plugin.json and creates .originals/ with pristine guidance/rules copies for future upgrade 3-way merge
- Generic qa_answers persistence replaces odoc_author_scope exception; doc-author reads qa_answers.scope with backward compatibility fallback
- Created /doc-writer:upgrade command with version detection, config migration with semantic inference, unchanged file update via .originals/ comparison, and consolidated upgrade summary
- Section-level 3-way merge algorithm with 13-case classification table, conflict resolution via AskUserQuestion, and 2-way diff bootstrap for pre-v1.5.0 projects
- Q&A gap detection (Step 3.5) and conditional researcher re-run (Step 4) added to upgrade SKILL.md, completing the 6-step upgrade flow

---

## v1.4.0 Content & Navigation (Shipped: 2026-03-22)

**Phases completed:** 4 phases, 8 plans, 15 tasks

**Key accomplishments:**

- Mermaid diagram sections added to all four framework guidance files with framework-specific wrapper syntax, sphinxcontrib.mermaid in sphinx-shibuya scaffold, and content-area-to-diagram-type heuristic in doc-author agent
- Doc-author proposes Concepts pages under Explanation during inventory; scan-exports.sh detects OCaml public symbols from .mli files
- Three-strategy nav Q&A (sections-as-tabs, single Docs tab, sidebar only) for sphinx-shibuya and mkdocs-material with scaffold variable substitution
- Three-strategy nav patterns (tabs, single Docs tab, sidebar-only) with section index page guidance and dual-placement abstracts in both Sphinx-Shibuya and MkDocs-Material guidance files, researcher agent, and doc-author agent
- Use Cases capture in setup Q&A (Step 2a.0) with skip/infer path, promotion question, re-run editing, and researcher dual-mode expansion into context.md
- Use-case page type with discovery/showcase template in doc-author and dedicated blur detection in doc-editor Pass 2
- Odoc-native .mld output mode with conditional write workflow, dune registration, external author-notes, and .mld discovery across editor/tester/SKILL
- .mli doc comment enrichment proposal workflow in doc-author with scope control, quality rules, and pipeline summary integration

---

## v1.0 Doc Writer Plugin (Shipped: 2026-03-19)

**Phases completed:** 13 phases, 28 plans, 1 tasks

**Key accomplishments:**

- (none recorded)

---
