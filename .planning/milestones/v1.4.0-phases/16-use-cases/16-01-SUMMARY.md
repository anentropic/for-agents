---
phase: 16-use-cases
plan: 01
subsystem: setup
tags: [use-cases, setup-qa, config-yaml, researcher, context-md]

# Dependency graph
requires:
  - phase: 15-navigation-strategies
    provides: Navigation strategy expansion pattern in doc-researcher.md
provides:
  - Use Cases Q&A step (Step 2a.0) in setup SKILL.md before persona definition
  - use_cases array and use_cases_section boolean in config-template.yaml
  - Use Case Expansion subsection in doc-researcher.md with dual-mode handling
  - Use Cases section in context.md template with source provenance tagging
affects: [16-02 (doc-author use-case page type, editor Pass 2 recognition)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Use cases Q&A before personas (Step 2a.0 numbering convention)"
    - "Dual-mode expansion: user-provided vs inferred with source provenance"
    - "Guard clause pattern: promotion question skipped when use_cases empty"

key-files:
  created: []
  modified:
    - doc-writer/skills/setup/SKILL.md
    - doc-writer/skills/setup/defaults/config-template.yaml
    - doc-writer/agents/doc-researcher.md

key-decisions:
  - "Use Cases Q&A step numbered 2a.0 to slot before existing 2a (User Persona Definition) without renumbering"
  - "Promotion question fully decoupled from inference path via guard clause"
  - "Re-run toggle handler prevents enabling docs section when use_cases array is empty"

patterns-established:
  - "Step 2a.0 numbering: new pre-persona steps use 2a.N where N < existing step numbers"
  - "Config field ordering: use_cases and use_cases_section sit between tone and doc_system"
  - "Source provenance tagging: user-provided vs inferred tracked in context.md output"

requirements-completed: [CONT-01, CONT-02]

# Metrics
duration: 3min
completed: 2026-03-22
---

# Phase 16 Plan 01: Use Cases Q&A & Researcher Expansion Summary

**Use Cases capture in setup Q&A (Step 2a.0) with skip/infer path, promotion question, re-run editing, and researcher dual-mode expansion into context.md**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T01:19:08Z
- **Completed:** 2026-03-22T01:22:20Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Setup SKILL.md has new Step 2a.0 (Use Cases) BEFORE persona definition with capture, skip, and chat paths
- Promotion question guarded by non-empty use_cases array; skip path fully decoupled from docs section path
- Re-run menu supports use case editing with add/edit/remove/toggle capabilities including empty-array guard on toggle
- config-template.yaml extended with use_cases array (title/problem/capability/outcome) and use_cases_section boolean
- doc-researcher.md reads use_cases from config, expands user-provided cases with persona cross-refs, infers from tasks/README/API when empty
- context.md template has Use Cases section with source provenance tagging (user-provided vs inferred)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Use Cases Q&A step, promotion question, and re-run support to setup SKILL.md + extend config-template.yaml** - `4f6fd1d` (feat)
2. **Task 2: Add Use Case Expansion to doc-researcher agent** - `0a73a55` (feat)

## Files Created/Modified
- `doc-writer/skills/setup/SKILL.md` - New Step 2a.0 Use Cases Q&A, re-run display/menu/handler, Step 3 config instruction update
- `doc-writer/skills/setup/defaults/config-template.yaml` - Added use_cases array and use_cases_section boolean fields
- `doc-writer/agents/doc-researcher.md` - Step 1 input reading, Use Case Expansion subsection, context.md template Use Cases section

## Decisions Made
- Use Cases Q&A step numbered 2a.0 to slot before existing 2a (User Persona Definition) without renumbering any existing steps
- Promotion question fully decoupled from inference path via guard clause -- skip path never sees the promotion question
- Re-run toggle handler prevents enabling docs section when use_cases array is empty, displaying explicit redirect message

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 16-02 can now build on these foundations: doc-author use-case page type template, inventory awareness, and editor Pass 2 recognition
- config-template.yaml schema is stable for downstream consumption
- Researcher expansion pattern established for use cases, ready for doc-author to read from context.md

---
*Phase: 16-use-cases*
*Completed: 2026-03-22*
