---
phase: 08-doc-writer-skills-polish
plan: 01
subsystem: ui
tags: [askuserquestion, argument-hint, claude-code, skill-ux, multiselect]

# Dependency graph
requires:
  - phase: 07-doc-writer-plugin-packaging
    provides: Plugin file structure with skills in doc-writer/skills/
provides:
  - argument-hint frontmatter on review skill for CLI autocomplete
  - AskUserQuestion pattern on review, write, and edit skills for structured user interaction
  - User Interaction Pattern section in all three skills for consistent freeform handling
affects: [08-02-doc-writer-skills-polish]

# Tech tracking
tech-stack:
  added: []
  patterns: [AskUserQuestion with multiSelect for batch approvals, mandatory trailing options pattern]

key-files:
  created: []
  modified:
    - doc-writer/skills/review/SKILL.md
    - doc-writer/skills/write/SKILL.md
    - doc-writer/skills/edit/SKILL.md

key-decisions:
  - "User Interaction Pattern section added to each skill defining shared freeform handling rules (DRY approach per RESEARCH.md recommendation)"
  - "All AskUserQuestion blocks include 'Type something else' and 'Chat about this' as mandatory trailing options per CONTEXT.md decisions"

patterns-established:
  - "AskUserQuestion trailing options: every structured choice includes 'Type something else' and 'Chat about this' as final two options"
  - "User Interaction Pattern: define freeform handling rules once per skill file, reference at each AskUserQuestion call site"

requirements-completed: [P8-01, P8-02, P8-03, P8-05, P8-06, P8-08, P8-09]

# Metrics
duration: 3min
completed: 2026-03-16
---

# Phase 08 Plan 01: Argument-hint and AskUserQuestion Summary

**Added argument-hint "[--edit]" to review skill frontmatter and converted three skills (review, write, edit) from plain-text prompts to AskUserQuestion with multiSelect and mandatory trailing options**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-16T23:09:30Z
- **Completed:** 2026-03-16T23:12:06Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Review skill now has `argument-hint: "[--edit]"` in YAML frontmatter for Claude Code autocomplete
- Review skill Step 2 --edit confirmation converted from "Proceed? (yes/no)" to AskUserQuestion with four options (Apply edits, Report only, Type something else, Chat about this)
- Write skill Step 6 PARTIAL approval converted from plain-text numbered list to AskUserQuestion multiSelect
- Edit skill Step 1 issue selection converted from plain-text numbered list to AskUserQuestion multiSelect
- All three skills have a new "User Interaction Pattern" section defining shared freeform handling rules

## Task Commits

Each task was committed atomically:

1. **Task 1: Add argument-hint to review skill and convert --edit confirmation to AskUserQuestion** - `6911576` (feat)
2. **Task 2: Convert write skill PARTIAL approval and edit skill issue selection to AskUserQuestion** - `f9fa820` (feat)

## Files Created/Modified
- `doc-writer/skills/review/SKILL.md` - Added argument-hint frontmatter, User Interaction Pattern section, AskUserQuestion --edit confirmation
- `doc-writer/skills/write/SKILL.md` - Added User Interaction Pattern section, AskUserQuestion multiSelect for PARTIAL approval
- `doc-writer/skills/edit/SKILL.md` - Added User Interaction Pattern section, AskUserQuestion multiSelect for issue selection

## Decisions Made
- Added User Interaction Pattern section to each skill defining freeform handling rules once (DRY approach from RESEARCH.md open question 3)
- All AskUserQuestion blocks include mandatory "Type something else" and "Chat about this" trailing options per CONTEXT.md locked decisions

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Three of five target files converted (review, write, edit skills)
- Plan 08-02 covers remaining targets: setup skill and doc-author agent
- Patterns established here (User Interaction Pattern section, trailing options) should be replicated in 08-02

## Self-Check: PASSED

All files exist. All commits verified.

---
*Phase: 08-doc-writer-skills-polish*
*Completed: 2026-03-16*
