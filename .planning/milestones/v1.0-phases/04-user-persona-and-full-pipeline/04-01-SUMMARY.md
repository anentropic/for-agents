---
phase: 04-user-persona-and-full-pipeline
plan: 01
subsystem: agents
tags: [system-prompt, doc-persona, user-persona, scenario-generation, simulation, gap-analysis, revision-loop, multi-audience, config-template]

# Dependency graph
requires:
  - phase: 03-editor-agent
    provides: Doc Editor agent output format, editor-report.md structure, terminology.yaml, HTML comment stripping behavior
  - phase: 02-doc-author-agent
    provides: Doc Author two-phase workflow, docs_root output convention, internal HTML comment notes for Editor
  - phase: 01-foundation-and-setup
    provides: Quality-rules skill (Rule 4 cross-references, Rule 5 audience calibration), config schema with audiences array, agent stub frontmatter
provides:
  - Complete User Persona agent system prompt with three-phase validation workflow (Generate, Simulate, Report)
  - Scenario generation from audience config including domain_context and discovery_story
  - Step-by-step doc simulation with explicit navigation rules (no source code, no Grep)
  - PASS/FAIL/PARTIAL verdict system with structured gap identification
  - Revision loop protocol documentation (FAIL-only triggering, max 2-3 passes, escalation)
  - Multi-audience support via invocation message parameter with independent verdicts and audience-specific reports
  - Config template extended with domain_context and discovery_story audience fields
affects: [05-integration-and-commands]

# Tech tracking
tech-stack:
  added: []
  patterns: [three-phase-validation-workflow, scenario-based-doc-testing, navigation-constrained-simulation, audience-filtered-scenario-generation, verdict-driven-revision-loop]

key-files:
  created: []
  modified: [agents/doc-persona.md, skills/setup/defaults/config-template.yaml]

key-decisions:
  - "Three-phase workflow (Generate Scenarios, Simulate, Report) mirrors real user testing methodology"
  - "Navigation rules prohibit Grep and source code access -- simulates actual end-user doc experience"
  - "PASS/PARTIAL/FAIL distinction: PASS = smooth path, PARTIAL = achievable with friction, FAIL = goal impossible"
  - "Only FAIL verdicts trigger revision passes; PARTIAL issues presented to project author for approval"
  - "Scenarios reused during revision passes to ensure consistent evaluation across iterations"
  - "Multi-audience via invocation message parameter with audience-specific report filenames for parallel execution safety"
  - "domain_context and discovery_story are optional config fields with graceful degradation"

patterns-established:
  - "Three-phase validation: Generate > Simulate > Report (parallels Author's Scan > Plan > Write and Editor's three passes)"
  - "Navigation-constrained simulation: only follow explicit links, TOC, and Glob-based nav discovery"
  - "Verdict-driven revision: only FAIL triggers re-run, PARTIAL goes to project author"
  - "Scenario persistence: scenarios.yaml preserves generated scenarios across revision passes"
  - "Audience-specific output files: persona-report-{audience-name}.md avoids write conflicts"

requirements-completed: [PERS-01, PERS-02, PERS-03, PERS-04, PERS-05]

# Metrics
duration: 4min
completed: 2026-03-03
---

# Phase 4 Plan 01: User Persona Agent Summary

**User Persona agent with goal-oriented scenario generation from audience config, navigation-constrained step-by-step doc simulation, PASS/FAIL/PARTIAL verdict system with gap identification, bounded revision loop protocol, and multi-audience support via independent per-audience evaluation**

## Performance

- **Duration:** ~4 min (Task 1 execution + checkpoint approval continuation)
- **Started:** 2026-03-03T23:43:22Z (Task 1 commit time)
- **Completed:** 2026-03-03T23:47:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Wrote complete 403-line User Persona agent system prompt expanding the Phase 1 stub
- Implemented three-phase validation workflow: Generate Scenarios, Simulate, Report
- Scenario generation reads audience config (name, skill_level, assumed_knowledge, domain_context, discovery_story) and produces 3-5 goal-oriented scenarios filtered by skill level
- Step-by-step simulation with explicit navigation rules: follow links and TOC only, no Grep across files, no source code access
- Verdict system with clear PASS/PARTIAL/FAIL distinction based on goal achievability, not perfection
- Structured gap identification for each non-PASS scenario with page, section, what is missing, and suggested fix
- Revision loop protocol: FAIL-only triggering, max 2-3 passes, scenario reuse, convergence tracking, escalation on non-convergence
- Multi-audience support via invocation message with audience-specific scenario files and report filenames
- Extended config template with domain_context and discovery_story fields for richer audience context
- All 5 PERS requirements addressed with traceable sections in the prompt
- Human verification confirmed completeness and correctness

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend config template and write complete User Persona agent** - `cd3086c` (feat)
2. **Task 2: Verify User Persona agent completeness** - human-verify checkpoint (no code commit, approval only)

## Files Created/Modified
- `agents/doc-persona.md` - Complete User Persona agent with full system prompt (403 lines, frontmatter updated from Phase 1 stub)
- `skills/setup/defaults/config-template.yaml` - Added domain_context and discovery_story fields to audience definition

## Decisions Made
- Three-phase workflow (Generate Scenarios, Simulate, Report) mirrors real user testing methodology -- consistent with Author's two-phase and Editor's three-pass patterns
- Navigation rules explicitly prohibit Grep and source code access to faithfully simulate actual end-user experience with docs
- PASS/PARTIAL/FAIL distinction: PASS = smooth path to goal, PARTIAL = achievable but with friction, FAIL = goal cannot be accomplished at all
- Only FAIL verdicts trigger pipeline revision passes; PARTIAL issues are presented to project author for targeted approval rather than automatic revision
- Scenarios are reused (never regenerated) during revision passes to ensure consistent evaluation baseline
- Multi-audience support via invocation message parameter ("Evaluate documentation as the '{audience_name}' audience") with audience-specific report filenames for parallel execution safety
- domain_context and discovery_story are optional config fields -- Persona gracefully degrades by inferring from audience name and assumed_knowledge if absent

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All three pipeline agents are now complete: Author, Editor, and Persona
- Phase 5 (Integration and Commands) can now be planned to wire up the full Author > Editor > Persona pipeline
- The revision loop protocol is documented in the Persona agent -- Phase 5's /doc:write orchestrator will implement the actual loop control
- Multi-audience parallel execution is designed but orchestration logic deferred to Phase 5
- Config template supports all fields needed by all three agents

## Self-Check: PASSED

- FOUND: agents/doc-persona.md
- FOUND: skills/setup/defaults/config-template.yaml
- FOUND: 04-01-SUMMARY.md
- FOUND: commit cd3086c

---
*Phase: 04-user-persona-and-full-pipeline*
*Completed: 2026-03-03*
