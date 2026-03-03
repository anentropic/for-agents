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
- [ ] **Phase 4: User Persona and Full Pipeline** - Perspective-shifted validation, full Author > Editor > Persona pipeline with revision loop and exit conditions
- [ ] **Phase 5: Integration and Commands** - User-facing commands (/doc:write, /doc:review, /doc:edit), GSD integration, and gap detection

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
**Plans**: TBD

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
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and Setup | 2/2 | Complete | 2026-03-03 |
| 2. Doc Author Agent | 1/1 | Complete | 2026-03-03 |
| 3. Editor Agent | 1/1 | Complete   | 2026-03-03 |
| 4. User Persona and Full Pipeline | 0/TBD | Not started | - |
| 5. Integration and Commands | 0/TBD | Not started | - |
