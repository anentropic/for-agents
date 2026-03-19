# Roadmap: Doc Writer Agent

## Overview

Five phases, each delivering one complete, testable capability. The sequence is dictated by hard architectural dependencies: config must exist before agents can run, Doc Author must produce real drafts before Editor can review them, and User Persona must be built last when the full pipeline is stable enough to validate against. The final phase wires up the user-facing commands and GSD integration that turn the proven pipeline into a distributable plugin.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation and Setup** - Config system, skill files, and plugin structure — the prerequisite everything else depends on (completed 2026-03-03)
- [x] **Phase 2: Doc Author Agent** - The content generator: diataxis-structured, audience-calibrated, internal-detail-free docs with working code examples (completed 2026-03-03)
- [x] **Phase 3: Editor Agent** - Quality enforcement: humanizer pass, terminology consistency, structured feedback, doc-system formatting (completed 2026-03-03)
- [x] **Phase 4: User Persona and Full Pipeline** - Perspective-shifted validation, full Author > Editor > Persona pipeline with revision loop and exit conditions (completed 2026-03-03)
- [x] **Phase 5: Integration and Commands** - User-facing commands (/doc:write, /doc:review, /doc:edit), GSD integration, and gap detection (completed 2026-03-04)
- [ ] **Phase 6: Cross-Phase Integration Cleanup** - Close integration gaps and tech debt from v1.0 milestone audit (INT-01 through INT-07)

## Phase Details

### Phase 1: Foundation and Setup
**Goal**: Project authors can configure the plugin for their project and everything the agents need to function is in place
**Depends on**: Nothing (first phase)
**Requirements**: SETUP-01, SETUP-02, SETUP-03, SETUP-04, SETUP-05
**Success Criteria** (what must be TRUE):
  1. Project author runs `/doc:setup` and answers Q&A prompts about their audience(s); a valid `doc-writer.config.json` is written to their project
  2. Config persists across sessions — re-running setup on the same project updates rather than overwrites audience definitions and custom rules
  3. Universal quality rules are in place as shared skill files; doc-system-specific guidance exists as separate editable `.md` files selectable during setup
  4. Project author can add custom quality rules to `doc-writer.config.json` and the config schema validates them
  5. Audience Q&A answer determines how many End-User Persona agents will be instantiated (one per configured audience)
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md -- Plugin scaffold, manifest, quality-rules skill, diataxis skill, agent stubs
- [x] 01-02-PLAN.md -- Setup skill with Q&A, auto-detection, config template, guidance files, default rules

### Phase 2: Doc Author Agent
**Goal**: The Doc Author agent produces diataxis-structured, audience-calibrated, internal-detail-free library documentation with working code examples
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, AUTH-07, AUTH-08, AUTH-09
**Success Criteria** (what must be TRUE):
  1. Doc Author classifies each page as tutorial, how-to, reference, or explanation before writing and applies the correct structural template for that type
  2. All pages of the same doc type use consistent structure — a reader opening two how-to guides sees the same section layout
  3. Generated docs contain no references to test utilities, CI config, dev scripts, justfile recipes, or other maintainer-internal concerns
  4. Doc Author reads the selected doc-system guidance file and produces output using that system's syntax (admonitions, frontmatter, directives)
  5. README.md and MAINTAINER.md are generated from their own templates with appropriate audience framing; code examples are working and realistic, not pseudocode stubs
**Plans:** 1 plan

Plans:
- [x] 02-01-PLAN.md -- Complete Doc Author agent system prompt (scan, plan, write workflow, templates, filtering, examples, calibration)

### Phase 3: Editor Agent
**Goal**: The Editor agent reviews Doc Author output and produces humanized, terminology-consistent, publication-quality docs with structured feedback
**Depends on**: Phase 2
**Requirements**: EDIT-01, EDIT-02, EDIT-03, EDIT-04
**Success Criteria** (what must be TRUE):
  1. All inline `code` mentions in prose are linked to the relevant API Reference entry after an Editor pass
  2. Editor's humanizer pass removes recognizable AI-writing patterns — prose reads as if written by a senior developer, not a language model
  3. Editor identifies and corrects terminology inconsistencies across files — the same concept uses the same name everywhere in the doc set
  4. Editor produces structured feedback in BLOCKING / SUGGESTION / NITPICK format with page, section, description, and fix for every issue
**Plans:** 1/1 plans complete

Plans:
- [x] 03-01-PLAN.md -- Complete Doc Editor agent system prompt (three-pass workflow: terminology, humanizer, cross-references, structured feedback, accuracy verification)

### Phase 4: User Persona and Full Pipeline
**Goal**: User Persona agents validate docs from the end user's perspective and the full Author > Editor > Persona pipeline runs with a bounded revision loop
**Depends on**: Phase 3
**Requirements**: PERS-01, PERS-02, PERS-03, PERS-04, PERS-05
**Success Criteria** (what must be TRUE):
  1. User Persona generates 3-5 concrete, goal-oriented user journey scenarios from project context without any manual authoring by the project author
  2. Each scenario is tested by attempting to accomplish a goal using only the generated docs — not by checking a criteria list
  3. Every scenario produces a clear PASS, FAIL, or PARTIAL verdict with specific gap identification; FAIL means a user goal cannot be achieved, not merely that something is imperfect
  4. The pipeline revision loop terminates: only BLOCKING issues trigger revision passes, a maximum of 2-3 passes runs before convergence failure is escalated to the user
  5. When two or more audiences are configured, a separate User Persona agent runs for each audience in parallel, producing independent verdicts
**Plans:** 1/1 plans complete

Plans:
- [x] 04-01-PLAN.md -- Complete User Persona agent system prompt (scenario generation, step-by-step simulation, verdict reporting, revision loop protocol, multi-audience support) and config template extension

### Phase 5: Integration and Commands
**Goal**: Project authors can invoke the full pipeline on demand, review existing docs, make targeted edits, and use the plugin from a GSD workflow
**Depends on**: Phase 4
**Requirements**: INTG-01, INTG-02, INTG-03, INTG-04, INTG-05
**Success Criteria** (what must be TRUE):
  1. Project author runs `/doc:write` and the full Author > Editor > Persona pipeline executes and writes publication-ready docs to the doc root
  2. Project author runs `/doc:review` on an existing doc set and receives a structured report of issues from Editor and User Persona without generating new content
  3. Project author runs `/doc:edit` targeting a specific page or issue and receives a revised version of only that scope
  4. Plugin is invokable at GSD milestone boundaries — project authors using GSD can trigger doc generation as part of their milestone workflow
  5. Gap detection runs as part of `/doc:write` and reports public API surface items that have no corresponding documentation
**Plans:** 2 plans

Plans:
- [x] 05-01-PLAN.md -- Full pipeline orchestration skill (/doc-writer:write) with gap detection script and revision loop
- [x] 05-02-PLAN.md -- Audit skill (/doc-writer:review) and targeted edit skill (/doc-writer:edit)

### Phase 6: Cross-Phase Integration Cleanup
**Goal**: Close all integration gaps and tech debt identified in the v1.0 milestone audit — stale delegation messages, missing config collection, filename inconsistencies, and minor wiring fixes
**Depends on**: Phase 5
**Requirements**: SETUP-01, EDIT-04, INTG-01, INTG-02, INTG-03, PERS-01, PERS-02 (hardening — all already satisfied, this phase improves integration quality)
**Gap Closure**: Addresses INT-01 through INT-07 from v1.0-MILESTONE-AUDIT.md
**Success Criteria** (what must be TRUE):
  1. All three orchestrator skills (write, review, edit) delegate to Editor with four named passes including Diataxis Type Integrity
  2. Setup Q&A collects domain_context and discovery_story for each audience
  3. Persona report filenames use consistent slug transformation across write and review flows
  4. Write skill reads editor-report.md before presenting summary counts
  5. Review skill uses consistent `{paths.docs_root}` variable naming
  6. Editor reads doc_system guidance file for formatting context
  7. Config template includes api_reference field
**Plans:** 1 plan

Plans:
- [ ] 06-01-PLAN.md -- Close INT-01 through INT-07: fix delegation messages, setup Q&A, filename slugs, editor-report read, variable naming, guidance file read, config template

### Phase 7: Doc-Writer Plugin Packaging
**Goal**: Reorganise skills/ and agents/ into a doc-writer/ subdirectory and configure it as a proper Claude Code plugin, ready for multi-plugin repo expansion in future milestones
**Depends on**: Phase 6
**Requirements**: PKG-01, PKG-02, PKG-03, PKG-04, PKG-05, PKG-06, PKG-07, PKG-08
**Plans:** 3/3 plans complete

Plans:
- [x] 07-01-PLAN.md -- Phase 7 bats test scaffold (PKG-01 through PKG-08) written in RED state before file moves (completed 2026-03-15)
- [ ] 07-02-PLAN.md -- Create plugin.json and marketplace.json manifests, git mv skills/ and agents/ into doc-writer/
- [ ] 07-03-PLAN.md -- Update hardcoded paths in phase-01-validation.bats and test_auth_requirements.sh; full suite GREEN

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and Setup | 2/2 | Complete | 2026-03-03 |
| 2. Doc Author Agent | 1/1 | Complete | 2026-03-03 |
| 3. Editor Agent | 1/1 | Complete | 2026-03-03 |
| 4. User Persona and Full Pipeline | 1/1 | Complete | 2026-03-03 |
| 5. Integration and Commands | 2/2 | Complete | 2026-03-04 |
| 6. Cross-Phase Integration Cleanup | 0/1 | In Progress | - |
| 7. Doc-Writer Plugin Packaging | 3/3 | Complete    | 2026-03-15 |
| 8. Doc-Writer Skills Polish | 2/2 | Complete    | 2026-03-16 |
| 9. Enhanced Setup Q&A + Researcher | 3/3 | Complete    | 2026-03-17 |
| 10. Framework Scaffolding + Unknown Framework Research | 3/3 | Complete    | 2026-03-17 |
| 11. Sphinx/Shibuya Framework Support | 2/2 | Complete    | 2026-03-18 |
| 12. Odoc Framework for OCaml | 0/4 | Planned     | - |

### Phase 8: doc-writer skills polish

**Goal:** Add argument-hint frontmatter to the review skill and convert plain-text list questions across all skills and the doc-author agent to native AskUserQuestion multi-choice UI
**Requirements**: P8-01, P8-02, P8-03, P8-04, P8-05, P8-06, P8-07, P8-08, P8-09
**Depends on:** Phase 7
**Plans:** 2/2 plans complete

Plans:
- [ ] 08-01-PLAN.md -- Add argument-hint to review skill; convert review, write, and edit skills to AskUserQuestion
- [ ] 08-02-PLAN.md -- Convert setup skill and doc-author agent to AskUserQuestion

### Phase 9: Enhanced Setup Q&A, Tone, User Persona Tasks, and Researcher Agent

**Goal:** Deepen the setup experience with infer+suggest AskUserQuestion for audience fields, tone selection, user persona task Q&A, framework-specific follow-up Q&A, and a researcher agent that enriches config inputs into a persisted context.md consumed by all downstream agents
**Requirements**: P9-01, P9-02, P9-03, P9-04, P9-05, P9-06, P9-07, P9-08, P9-09, P9-10
**Depends on:** Phase 8
**Plans:** 3/3 plans complete

Plans:
- [x] 09-01-PLAN.md -- Config template extension (tone, user_tasks) and doc-researcher agent definition (completed 2026-03-17)
- [x] 09-02-PLAN.md -- Downstream agent updates: doc-author, doc-editor, doc-persona read context.md (completed 2026-03-17)
- [x] 09-03-PLAN.md -- Setup skill rewrite: infer+suggest Q&A, tone, persona tasks, framework Q&A, researcher invocation (completed 2026-03-17)

### Phase 10: Framework Scaffolding and Unknown Framework Research+Guidance Generation

**Goal:** Extract framework Q&A into data files, add smart scaffolding for known frameworks (diff-against-defaults for existing configs, full scaffold for new projects), and enable dynamic unknown framework support via researcher-generated guidance and Q&A that persist globally in plugin defaults
**Requirements**: P10-01, P10-02, P10-03, P10-04, P10-05, P10-06, P10-07, P10-08
**Depends on:** Phase 9
**Plans:** 3/3 plans complete

Plans:
- [ ] 10-01-PLAN.md -- Extract Q&A data files for mkdocs-material and plain-markdown, create mkdocs-material scaffold template
- [ ] 10-02-PLAN.md -- Add Unknown Framework Research mode to doc-researcher agent
- [ ] 10-03-PLAN.md -- Rewrite setup skill: dynamic Q&A reading, scaffold check step, unknown framework detection

### Phase 11: Sphinx/Shibuya Doc Framework Support

**Goal:** Add Sphinx + Shibuya theme as a built-in supported framework in the doc-writer plugin with RST-native guidance, sphinx-design component rules, sphinx-autoapi integration, and conf.py scaffolding -- on equal footing with mkdocs-material
**Requirements**: P11-01, P11-02, P11-03, P11-04, P11-05, P11-06
**Depends on:** Phase 10
**Plans:** 2/2 plans complete

Plans:
- [ ] 11-01-PLAN.md -- Q&A data file (sphinx-shibuya.qa.md) and conf.py scaffold template (sphinx-shibuya.py)
- [ ] 11-02-PLAN.md -- Guidance file (sphinx-shibuya.md) and setup skill integration (SKILL.md update)

### Phase 12: Odoc Framework for OCaml Projects

**Goal:** Add odoc as a built-in supported framework in the doc-writer plugin -- on equal footing with mkdocs-material and sphinx-shibuya. Delivers odoc.qa.md (Q&A with follow-on sub-topic questions), odoc.md (comprehensive guidance absorbing ocaml-odoc-guide skill), scaffolds/odoc/ (directory-based dune + .mld templates), and SKILL.md updated to list odoc as a selectable doc system.
**Requirements**: P12-01, P12-02, P12-03, P12-04, P12-05, P12-06, P12-07, P12-08
**Depends on:** Phase 11
**Plans:** 4 plans

Plans:
- [ ] 12-01-PLAN.md -- Bats test scaffold (P12-01 through P12-08) in RED state
- [ ] 12-02-PLAN.md -- Q&A data file (odoc.qa.md) and directory-based scaffold templates (scaffolds/odoc/)
- [ ] 12-03-PLAN.md -- Comprehensive guidance file (odoc.md) absorbing ocaml-odoc-guide skill content
- [ ] 12-04-PLAN.md -- Setup skill integration (SKILL.md: option, handler, built-in list, directory scaffold support) and full validation
