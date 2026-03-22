# Roadmap: Doc Writer Agent

## Milestones

- ✅ **v1.0 Doc Writer Plugin** — Phases 1-13 (shipped 2026-03-19)
- 🚧 **v1.4.0 Content & Navigation** — Phases 14-17 (in progress)

## Phases

<details>
<summary>✅ v1.0 Doc Writer Plugin (Phases 1-13) — SHIPPED 2026-03-19</summary>

- [x] Phase 1: Foundation and Setup (2/2 plans) — completed 2026-03-03
- [x] Phase 2: Doc Author Agent (1/1 plans) — completed 2026-03-03
- [x] Phase 3: Editor Agent (1/1 plans) — completed 2026-03-03
- [x] Phase 4: User Persona and Full Pipeline (1/1 plans) — completed 2026-03-03
- [x] Phase 5: Integration and Commands (2/2 plans) — completed 2026-03-04
- [x] Phase 6: Cross-Phase Integration Cleanup (1/1 plans) — completed 2026-03-15
- [x] Phase 7: Doc-Writer Plugin Packaging (3/3 plans) — completed 2026-03-15
- [x] Phase 8: Doc-Writer Skills Polish (2/2 plans) — completed 2026-03-16
- [x] Phase 9: Enhanced Setup Q&A + Researcher (3/3 plans) — completed 2026-03-17
- [x] Phase 10: Framework Scaffolding + Unknown Framework Research (3/3 plans) — completed 2026-03-17
- [x] Phase 11: Sphinx/Shibuya Framework Support (2/2 plans) — completed 2026-03-18
- [x] Phase 12: Odoc Framework for OCaml (4/4 plans) — completed 2026-03-19
- [x] Phase 13: Scaffold Variable Fix + Doc-Researcher Improvements (3/3 plans) — completed 2026-03-19

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### 🚧 v1.4.0 Content & Navigation (In Progress)

**Milestone Goal:** Richer content types (Use Cases, Concepts), smarter nav structure for sphinx-shibuya and mkdocs-material, close OCaml/odoc gaps, and mermaid diagram support.

**Phase Numbering:**
- Integer phases (14, 15, 16, 17): Planned milestone work
- Decimal phases (14.1, 15.1): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 14: Foundations** - Concepts pages, mermaid diagram awareness, OCaml scan-exports (completed 2026-03-21)
- [x] **Phase 15: Navigation Strategies** - Three-strategy nav for sphinx-shibuya and mkdocs-material with section indexes (completed 2026-03-22)
- [x] **Phase 16: Use Cases** - Use Cases Q&A capture in setup and optional docs section (completed 2026-03-22)
- [ ] **Phase 17: OCaml .mld/.mli Output** - Doc-author writes odoc-native .mld files, editor handles .mld discovery

## Phase Details

### Phase 14: Foundations
**Goal**: Doc-author can recommend Concepts pages and mermaid diagrams, and scan-exports detects OCaml public symbols
**Depends on**: Nothing (first phase of v1.4.0; builds on shipped v1.0)
**Requirements**: CONT-04, CONT-05, MERM-01, MERM-02, MERM-03, MERM-04, OCML-01
**Success Criteria** (what must be TRUE):
  1. Doc-author proposes Concepts page(s) under Explanation during page inventory, with the proposal refinable in Q&A
  2. Doc-author recommends appropriate mermaid diagram types (flowchart, sequence, state, class) based on the content area being documented
  3. Each framework guidance file (mkdocs-material, sphinx-shibuya, odoc, plain-markdown) contains a mermaid syntax section with the correct wrapper format for that framework
  4. Sphinx-shibuya scaffold includes sphinxcontrib-mermaid dependency and configuration
  5. Running scan-exports.sh on an OCaml project scans .mli files and extracts public symbols (val, type, module declarations)
**Plans**: 2 plans

Plans:
- [x] 14-01-PLAN.md — Mermaid diagram support: guidance files, scaffold, and doc-author awareness
- [x] 14-02-PLAN.md — Concepts page awareness and OCaml scan-exports

### Phase 15: Navigation Strategies
**Goal**: Project authors choose from three nav strategies during setup, and both sphinx-shibuya and mkdocs-material render the chosen strategy correctly with section index pages
**Depends on**: Phase 14
**Requirements**: NAV-01, NAV-02, NAV-03, NAV-04, NAV-05, NAV-06, NAV-07, NAV-08
**Success Criteria** (what must be TRUE):
  1. Setup Q&A presents three nav strategy choices (no top tabs, single "Docs" tab, sections as top tabs) with a recommendation of sections-as-tabs when 12+ pages
  2. Sphinx-shibuya sections-as-tabs strategy renders dropdown menus with children and summary text via nav_links in conf.py
  3. Sphinx-shibuya "Docs" tab strategy renders as a dropdown with docs sections as items
  4. MkDocs-material nav strategies use the correct feature flags (navigation.tabs, navigation.tabs.sticky, navigation.indexes) in mkdocs.yml
  5. When sections are promoted to top tabs, the left nav shows only the selected section's children (not the full docs tree)
  6. Section index pages include a short abstract beneath each sub-page link, using framework-native metadata where supported
**Plans**: 2 plans

Plans:
- [x] 15-01-PLAN.md — Q&A nav strategy questions, scaffold template variables, and SKILL.md variable table
- [x] 15-02-PLAN.md — Guidance file nav strategies, researcher expansion, and doc-author section index pages

### Phase 16: Use Cases
**Goal**: Project authors can capture use cases during setup (optionally), and those use cases flow into researcher context and optionally become a docs section
**Depends on**: Phase 15 (Use Cases section placement requires knowing available nav strategies)
**Requirements**: CONT-01, CONT-02, CONT-03
**Success Criteria** (what must be TRUE):
  1. Setup Q&A includes a Use Cases step before user personas that is skippable (infers from persona context if skipped)
  2. Captured use cases are stored in config.yaml and expanded by the researcher agent into context.md
  3. Use cases can be optionally promoted to a docs section (at the same level as diataxis quadrants) with typical and advanced cases as pages
  4. Editor recognizes (use-case) page type in Pass 2 blur detection without misclassifying it
**Plans**: 2 plans

Plans:
- [x] 16-01-PLAN.md — Setup Q&A use cases step, config schema extension, and researcher use case expansion
- [x] 16-02-PLAN.md — Doc-author use-case page template and inventory awareness, editor Pass 2 recognition

### Phase 17: OCaml .mld/.mli Output
**Goal**: Doc-author produces odoc-native .mld files (not Markdown) for odoc projects, and the full pipeline handles .mld discovery and syntax
**Depends on**: Phase 14 (scan-exports OCaml case must exist)
**Requirements**: OCML-02, OCML-03, OCML-04, OCML-05
**Success Criteria** (what must be TRUE):
  1. When doc_system is odoc, doc-author writes .mld files with odoc syntax (headings, code blocks, cross-references) instead of Markdown
  2. Doc-author registers each .mld page in doc/dune during the write pass
  3. Doc-author proposes doc comment enrichment for undocumented public values found in .mli files
  4. Editor discovers .mld files and applies quality passes using odoc syntax rules (not Markdown rules)
**Plans**: 2 plans

Plans:
- [x] 17-01-PLAN.md — Odoc output mode: doc-author .mld write workflow, editor/tester .mld discovery, write SKILL mode detection
- [ ] 17-02-PLAN.md — .mli doc comment enrichment proposals in doc-author, pipeline summary enrichment mention

## Progress

**Execution Order:**
Phases execute in numeric order: 14 → 15 → 16 → 17

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation and Setup | v1.0 | 2/2 | Complete | 2026-03-03 |
| 2. Doc Author Agent | v1.0 | 1/1 | Complete | 2026-03-03 |
| 3. Editor Agent | v1.0 | 1/1 | Complete | 2026-03-03 |
| 4. User Persona and Full Pipeline | v1.0 | 1/1 | Complete | 2026-03-03 |
| 5. Integration and Commands | v1.0 | 2/2 | Complete | 2026-03-04 |
| 6. Cross-Phase Integration Cleanup | v1.0 | 1/1 | Complete | 2026-03-15 |
| 7. Doc-Writer Plugin Packaging | v1.0 | 3/3 | Complete | 2026-03-15 |
| 8. Doc-Writer Skills Polish | v1.0 | 2/2 | Complete | 2026-03-16 |
| 9. Enhanced Setup Q&A + Researcher | v1.0 | 3/3 | Complete | 2026-03-17 |
| 10. Framework Scaffolding + Unknown Framework | v1.0 | 3/3 | Complete | 2026-03-17 |
| 11. Sphinx/Shibuya Framework Support | v1.0 | 2/2 | Complete | 2026-03-18 |
| 12. Odoc Framework for OCaml | v1.0 | 4/4 | Complete | 2026-03-19 |
| 13. Scaffold Variable Fix + Doc-Researcher | v1.0 | 3/3 | Complete | 2026-03-19 |
| 14. Foundations | v1.4.0 | 2/2 | Complete    | 2026-03-21 |
| 15. Navigation Strategies | v1.4.0 | 2/2 | Complete    | 2026-03-22 |
| 16. Use Cases | v1.4.0 | 2/2 | Complete    | 2026-03-22 |
| 17. OCaml .mld/.mli Output | v1.4.0 | 1/2 | In Progress|  |
