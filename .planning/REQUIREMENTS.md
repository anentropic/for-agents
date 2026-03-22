# Requirements: Doc Writer v1.4.0 — Content & Navigation

**Defined:** 2026-03-21
**Core Value:** Produce library documentation that the project author can publish with minimal tweaks — docs written from the end user's perspective, not the builder's.

## v1.4.0 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### Content Types

- [ ] **CONT-01**: Setup Q&A captures use cases before user personas (skippable; infers from persona context if skipped)
- [ ] **CONT-02**: Use cases stored in config.yaml and expanded in context.md by researcher agent
- [ ] **CONT-03**: Use cases optionally promoted to a docs section at same level as diataxis quadrants, with typical and advanced cases as pages
- [x] **CONT-04**: Author proposes optional Concepts page(s) under Explanation by default, refined in page inventory Q&A
- [x] **CONT-05**: Author recommends appropriate mermaid diagram types (flowchart, sequence, state, class) based on content area

### Navigation

- [x] **NAV-01**: Setup Q&A offers three nav strategies: no top tabs, single "Docs" top tab, sections promoted to top tabs
- [x] **NAV-02**: Sections-as-tabs recommended when 12+ pages, but all three choices always available
- [x] **NAV-03**: Sphinx-shibuya sections-as-tabs uses dropdown menus with children and summary text via nav_links
- [x] **NAV-04**: Sphinx-shibuya "Docs" top tab renders as dropdown with docs sections as items
- [x] **NAV-05**: When sections promoted to top tabs, left nav starts from selected section (not full docs index)
- [x] **NAV-06**: MkDocs-material three nav strategies use navigation.tabs, navigation.tabs.sticky, navigation.indexes features
- [x] **NAV-07**: Section index pages include a short abstract beneath each sub-page link
- [x] **NAV-08**: Abstracts use framework-native metadata where supported (sphinx :description:), inline on index page elsewhere

### Mermaid

- [x] **MERM-01**: Doc-author aware of mermaid diagrams and uses them when appropriate across all four doc systems
- [x] **MERM-02**: Each framework guidance file includes mermaid syntax section with correct wrapper format
- [x] **MERM-03**: sphinxcontrib-mermaid added to sphinx-shibuya scaffold and guidance
- [x] **MERM-04**: Odoc mermaid handled as guidance-only workaround (no native support)

### OCaml/Odoc

- [x] **OCML-01**: scan-exports.sh has OCaml language case scanning .mli files for public symbols (val, type, module)
- [ ] **OCML-02**: Doc-author writes .mld files with odoc syntax when doc_system is odoc
- [ ] **OCML-03**: Doc-author registers .mld pages in doc/dune during write pass
- [ ] **OCML-04**: Doc-author proposes doc comment enrichment for undocumented public values in .mli files
- [ ] **OCML-05**: Editor handles .mld file discovery and odoc syntax in quality passes

## Future Requirements

Deferred to future release. Tracked but not in current roadmap.

### Content Types

- **CONT-06**: Glossary page generation from terminology.yaml
- **CONT-07**: Per-page diagram style configuration

### Mermaid

- **MERM-05**: Auto-generated mermaid diagrams from source code analysis

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| MyST-Parser for Sphinx | Locked decision: RST-native only, no Markdown in Sphinx |
| mkdocs-mermaid2-plugin | Redundant; pymdownx.superfences already handles mermaid in mkdocs-material |
| odoc-mermaid-extension | Experimental, not on opam stable, not production-ready |
| Multiple scaffold variants per nav strategy | Keep one scaffold per framework; handle nav strategy via variable substitution |
| Auto-generated mermaid from source code | Noisy, drift-prone, serves builder's mental model rather than reader's |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONT-01 | Phase 16 | Pending |
| CONT-02 | Phase 16 | Pending |
| CONT-03 | Phase 16 | Pending |
| CONT-04 | Phase 14 | Complete |
| CONT-05 | Phase 14 | Complete |
| NAV-01 | Phase 15 | Complete |
| NAV-02 | Phase 15 | Complete |
| NAV-03 | Phase 15 | Complete |
| NAV-04 | Phase 15 | Complete |
| NAV-05 | Phase 15 | Complete |
| NAV-06 | Phase 15 | Complete |
| NAV-07 | Phase 15 | Complete |
| NAV-08 | Phase 15 | Complete |
| MERM-01 | Phase 14 | Complete |
| MERM-02 | Phase 14 | Complete |
| MERM-03 | Phase 14 | Complete |
| MERM-04 | Phase 14 | Complete |
| OCML-01 | Phase 14 | Complete |
| OCML-02 | Phase 17 | Pending |
| OCML-03 | Phase 17 | Pending |
| OCML-04 | Phase 17 | Pending |
| OCML-05 | Phase 17 | Pending |

**Coverage:**
- v1.4.0 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after roadmap creation*
