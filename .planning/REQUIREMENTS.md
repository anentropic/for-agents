# Requirements: Doc Writer Agent

**Defined:** 2026-03-03
**Core Value:** Produce library documentation that the project author can publish with minimal tweaks — docs written from the end user's perspective, not the builder's.

**Vocabulary:** "Project author" = the maintainer who invokes the plugin. "End user" = a user of the documented library.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Setup & Config

- [x] **SETUP-01**: Project author can run a setup command that asks about target audience(s) and persists config per-project
- [x] **SETUP-02**: Quality rules are layered — universal defaults baked into agents, project-specific overrides in config file
- [x] **SETUP-03**: Universal quality rules and guidance are doc-system-agnostic; doc-system-specific guidance lives in separate editable .md files (one per system), selected during setup
- [x] **SETUP-04**: Project author can define custom quality rules in project config that Editor enforces
- [x] **SETUP-05**: Audience Q&A determines number and types of End-User Persona agents to instantiate

### Doc Author

- [x] **AUTH-01**: Doc Author classifies content type (tutorial, how-to, reference, explanation) before writing and applies correct structure
- [x] **AUTH-02**: All pages of the same doc type follow the same template structure
- [x] **AUTH-03**: Internal details are filtered out — no test utils, CI config, dev scripts, justfile recipes, or maintainer-only concerns in end-user-facing docs
- [x] **AUTH-04**: Author reads the selected doc-system guidance file and produces output using that system's syntax and conventions (admonitions, frontmatter, directives, etc.)
- [x] **AUTH-05**: README.md has its own template — end-user-focused, with quick start, installation, and key features
- [x] **AUTH-06**: MAINTAINER.md/DEVELOP.md has its own template — contributor-focused, with setup, architecture, and contribution guidelines
- [x] **AUTH-07**: Every API/feature page includes working, realistic code examples (not pseudocode or minimal stubs)
- [x] **AUTH-08**: Python/mkdocs projects support blacken-docs formatting and doctest validation where appropriate
- [x] **AUTH-09**: Vocabulary and assumed knowledge level are calibrated to the configured audience

### Editor

- [x] **EDIT-01**: All inline `code` mentions in prose are linked to the relevant API Reference entry
- [x] **EDIT-02**: Humanizer pass removes recognizable AI-writing patterns from prose
- [x] **EDIT-03**: Cross-file terminology consistency is enforced — same concept uses same name everywhere
- [x] **EDIT-04**: Agent communication uses structured feedback format with BLOCKING/SUGGESTION/NITPICK severity levels

### End-User Persona

- [x] **PERS-01**: End-User Persona agent generates 3-5 realistic end-user journey scenarios from project context without manual authoring
- [x] **PERS-02**: Scenarios are goal-oriented — agent tries to accomplish tasks using only the docs (not checklist-checking)
- [x] **PERS-03**: Each scenario gets a clear verdict: PASS, FAIL, or PARTIAL, with specific gap identification
- [x] **PERS-04**: Pipeline revision loop has a max pass limit (2-3) and convergence rules — only BLOCKING issues trigger revision
- [x] **PERS-05**: When multiple audiences are configured, a separate End-User Persona agent is instantiated for each and runs in parallel

### Integration

- [x] **INTG-01**: Project author can generate new docs on-demand via `/doc:write` command
- [x] **INTG-02**: Project author can review existing docs via `/doc:review` — runs Editor + End-User Persona pipeline on current docs, reports issues
- [x] **INTG-03**: Project author can make targeted fixes via `/doc:edit` — addresses specific pages or issues
- [x] **INTG-04**: Plugin integrates with GSD workflow — invokable at milestone boundaries
- [x] **INTG-05**: Gap detection compares public API surface against documented surface and reports undocumented features

### Framework Scaffolding & Unknown Framework Research

- [x] **P10-01**: mkdocs-material Q&A question set exists as a standalone .qa.md data file in defaults/
- [x] **P10-02**: plain-markdown Q&A question set exists as a standalone .qa.md data file in defaults/
- [x] **P10-03**: Opinionated mkdocs-material scaffold template exists in defaults/scaffolds/
- [x] **P10-04**: Setup skill reads framework Q&A from .qa.md data files instead of hardcoded questions in the skill body
- [x] **P10-05**: Setup skill has a scaffold check step that detects existing framework config vs no config and handles both modes (full scaffold + diff-against-defaults)
- [x] **P10-06**: Setup skill handles unknown framework names by spawning doc-researcher to generate guidance, Q&A, and scaffold files
- [x] **P10-07**: doc-researcher agent has a distinct "Unknown Framework Research" mode that generates guidance, Q&A, and scaffold files to plugin defaults (with project-local fallback)
- [x] **P10-08**: No framework Q&A questions remain hardcoded in the setup SKILL.md body -- all are read dynamically from .qa.md files

### Sphinx/Shibuya Framework Support

- [ ] **P11-01**: sphinx-shibuya Q&A data file exists in defaults/ with Detection section (conf.py) and 3 questions (navigation, API reference, sphinx-design features)
- [ ] **P11-02**: sphinx-shibuya guidance file exists in defaults/ with opinionated RST writing preferences mirroring mkdocs-material.md structure
- [ ] **P11-03**: conf.py scaffold template exists in defaults/scaffolds/ with Shibuya theme, nav_links for Diataxis tabs, autoapi, napoleon, intersphinx, and sphinx-design extensions
- [ ] **P11-04**: Setup skill SKILL.md lists sphinx-shibuya as a selectable built-in doc system option in Step 2b
- [ ] **P11-05**: Guidance file covers all four sphinx-design component groups (grids+cards, tab sets, dropdowns, badges+buttons) with curated use-case rules
- [ ] **P11-06**: Guidance file covers sphinx-autoapi integration: autoapi replaces Reference tab, Google docstring convention, Author agent must not write manual reference pages

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Targeting & Incremental

- **TARG-01**: Scope parameter (`--all`, `--file`, `--section`) to target specific docs
- **TARG-02**: Incremental mode — only document what changed since last run
- **TARG-03**: Persona-first pipeline variant — End-User Personas define what they need before Author writes

### Distribution

- **DIST-01**: Plugin packaged for CC Marketplace distribution
- **DIST-02**: Doc-system formatting presets (mkdocs-material, Docusaurus, Sphinx, VitePress)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| API reference auto-generation | TypeDoc, pdoc, rustdoc already handle this — focus on narrative docs |
| Doc site hosting or deployment | Infrastructure concern, not a writing concern |
| Automated publishing (commit/push) | Project author must have a review gate before docs go live |
| Non-library docs (blogs, wikis, marketing) | Different audiences and frameworks — dilutes specialized quality |
| Real-time auto-triggering on code changes | Creates noise and docs for unfinished features — on-demand only |
| Executing code examples for runtime validation | Environment complexity; verify syntax and idiom, not execution |
| Interactive questions mid-generation | Front-load config in setup Q&A, not mid-pipeline |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Complete |
| SETUP-02 | Phase 1 | Complete |
| SETUP-03 | Phase 1 | Complete |
| SETUP-04 | Phase 1 | Complete |
| SETUP-05 | Phase 1 | Complete |
| AUTH-01 | Phase 2 | Complete |
| AUTH-02 | Phase 2 | Complete |
| AUTH-03 | Phase 2 | Complete |
| AUTH-04 | Phase 2 | Complete |
| AUTH-05 | Phase 2 | Complete |
| AUTH-06 | Phase 2 | Complete |
| AUTH-07 | Phase 2 | Complete |
| AUTH-08 | Phase 2 | Complete |
| AUTH-09 | Phase 2 | Complete |
| EDIT-01 | Phase 3 | Complete |
| EDIT-02 | Phase 3 | Complete |
| EDIT-03 | Phase 3 | Complete |
| EDIT-04 | Phase 3 | Complete |
| PERS-01 | Phase 4 | Complete |
| PERS-02 | Phase 4 | Complete |
| PERS-03 | Phase 4 | Complete |
| PERS-04 | Phase 4 | Complete |
| PERS-05 | Phase 4 | Complete |
| INTG-01 | Phase 5 | Complete |
| INTG-02 | Phase 5 | Complete |
| INTG-03 | Phase 5 | Complete |
| INTG-04 | Phase 5 | Complete |
| INTG-05 | Phase 5 | Complete |
| P10-01 | Phase 10 | Planned |
| P10-02 | Phase 10 | Planned |
| P10-03 | Phase 10 | Planned |
| P10-04 | Phase 10 | Planned |
| P10-05 | Phase 10 | Planned |
| P10-06 | Phase 10 | Planned |
| P10-07 | Phase 10 | Planned |
| P10-08 | Phase 10 | Planned |
| P11-01 | Phase 11 | Planned |
| P11-02 | Phase 11 | Planned |
| P11-03 | Phase 11 | Planned |
| P11-04 | Phase 11 | Planned |
| P11-05 | Phase 11 | Planned |
| P11-06 | Phase 11 | Planned |

**Coverage:**
- v1 requirements: 42 total
- Mapped to phases: 42
- Unmapped: 0

---
*Requirements defined: 2026-03-03*
*Last updated: 2026-03-18 after Phase 11 planning -- added P11-01 through P11-06*
