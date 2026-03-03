# Requirements: Doc Writer Agent

**Defined:** 2026-03-03
**Core Value:** Produce library documentation that the project author can publish with minimal tweaks — docs written from the end user's perspective, not the builder's.

**Vocabulary:** "Project author" = the maintainer who invokes the plugin. "End user" = a user of the documented library.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Setup & Config

- [ ] **SETUP-01**: Project author can run a setup command that asks about target audience(s) and persists config per-project
- [x] **SETUP-02**: Quality rules are layered — universal defaults baked into agents, project-specific overrides in config file
- [ ] **SETUP-03**: Universal quality rules and guidance are doc-system-agnostic; doc-system-specific guidance lives in separate editable .md files (one per system), selected during setup
- [x] **SETUP-04**: Project author can define custom quality rules in project config that Editor enforces
- [ ] **SETUP-05**: Audience Q&A determines number and types of End-User Persona agents to instantiate

### Doc Author

- [ ] **AUTH-01**: Doc Author classifies content type (tutorial, how-to, reference, explanation) before writing and applies correct structure
- [ ] **AUTH-02**: All pages of the same doc type follow the same template structure
- [ ] **AUTH-03**: Internal details are filtered out — no test utils, CI config, dev scripts, justfile recipes, or maintainer-only concerns in end-user-facing docs
- [ ] **AUTH-04**: Author reads the selected doc-system guidance file and produces output using that system's syntax and conventions (admonitions, frontmatter, directives, etc.)
- [ ] **AUTH-05**: README.md has its own template — end-user-focused, with quick start, installation, and key features
- [ ] **AUTH-06**: MAINTAINER.md/DEVELOP.md has its own template — contributor-focused, with setup, architecture, and contribution guidelines
- [ ] **AUTH-07**: Every API/feature page includes working, realistic code examples (not pseudocode or minimal stubs)
- [ ] **AUTH-08**: Python/mkdocs projects support blacken-docs formatting and doctest validation where appropriate
- [ ] **AUTH-09**: Vocabulary and assumed knowledge level are calibrated to the configured audience

### Editor

- [ ] **EDIT-01**: All inline `code` mentions in prose are linked to the relevant API Reference entry
- [ ] **EDIT-02**: Humanizer pass removes recognizable AI-writing patterns from prose
- [ ] **EDIT-03**: Cross-file terminology consistency is enforced — same concept uses same name everywhere
- [ ] **EDIT-04**: Agent communication uses structured feedback format with BLOCKING/SUGGESTION/NITPICK severity levels

### End-User Persona

- [ ] **PERS-01**: End-User Persona agent generates 3-5 realistic end-user journey scenarios from project context without manual authoring
- [ ] **PERS-02**: Scenarios are goal-oriented — agent tries to accomplish tasks using only the docs (not checklist-checking)
- [ ] **PERS-03**: Each scenario gets a clear verdict: PASS, FAIL, or PARTIAL, with specific gap identification
- [ ] **PERS-04**: Pipeline revision loop has a max pass limit (2-3) and convergence rules — only BLOCKING issues trigger revision
- [ ] **PERS-05**: When multiple audiences are configured, a separate End-User Persona agent is instantiated for each and runs in parallel

### Integration

- [ ] **INTG-01**: Project author can generate new docs on-demand via `/doc:write` command
- [ ] **INTG-02**: Project author can review existing docs via `/doc:review` — runs Editor + End-User Persona pipeline on current docs, reports issues
- [ ] **INTG-03**: Project author can make targeted fixes via `/doc:edit` — addresses specific pages or issues
- [ ] **INTG-04**: Plugin integrates with GSD workflow — invokable at milestone boundaries
- [ ] **INTG-05**: Gap detection compares public API surface against documented surface and reports undocumented features

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
| SETUP-01 | Phase 1 | Pending |
| SETUP-02 | Phase 1 | Complete |
| SETUP-03 | Phase 1 | Pending |
| SETUP-04 | Phase 1 | Complete |
| SETUP-05 | Phase 1 | Pending |
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| AUTH-03 | Phase 2 | Pending |
| AUTH-04 | Phase 2 | Pending |
| AUTH-05 | Phase 2 | Pending |
| AUTH-06 | Phase 2 | Pending |
| AUTH-07 | Phase 2 | Pending |
| AUTH-08 | Phase 2 | Pending |
| AUTH-09 | Phase 2 | Pending |
| EDIT-01 | Phase 3 | Pending |
| EDIT-02 | Phase 3 | Pending |
| EDIT-03 | Phase 3 | Pending |
| EDIT-04 | Phase 3 | Pending |
| PERS-01 | Phase 4 | Pending |
| PERS-02 | Phase 4 | Pending |
| PERS-03 | Phase 4 | Pending |
| PERS-04 | Phase 4 | Pending |
| PERS-05 | Phase 4 | Pending |
| INTG-01 | Phase 5 | Pending |
| INTG-02 | Phase 5 | Pending |
| INTG-03 | Phase 5 | Pending |
| INTG-04 | Phase 5 | Pending |
| INTG-05 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0

---
*Requirements defined: 2026-03-03*
*Last updated: 2026-03-03 after roadmap creation — all 28 requirements mapped*
