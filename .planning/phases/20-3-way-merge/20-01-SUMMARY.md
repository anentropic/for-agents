---
phase: 20-3-way-merge
plan: 01
subsystem: upgrade
tags: [merge, 3-way-merge, 2-way-diff, section-parsing, AskUserQuestion, upgrade]

# Dependency graph
requires:
  - phase: 19-upgrade-skill
    provides: "Step 3 with placeholder merge skip logic, .originals/ read/write infrastructure"
provides:
  - "Section-level 3-way merge algorithm in Step 3 for guidance and rules files"
  - "2-way diff bootstrap path for pre-v1.5.0 projects without .originals/"
  - "Conflict resolution via AskUserQuestion with 4 options per conflict"
  - "File Merges sub-section in upgrade summary template"
affects: [21-qa-gap-detection]

# Tech tracking
tech-stack:
  added: []
  patterns: ["section-level merge by ## headings", "3-way classification table (13 cases)", "2-way diff bootstrap for legacy projects"]

key-files:
  created: []
  modified: ["doc-writer/skills/upgrade/SKILL.md"]

key-decisions:
  - "Section parsing treats preamble (content before first ##) as __preamble__ section"
  - "13-row classification table covers all merge cases including convergent and removal conflicts"
  - "Removal conflicts (user customized, upstream removed) get dedicated AskUserQuestion format"
  - "2-way diff bootstrap writes NEW (not merged) content to .originals/ to establish correct baseline"

patterns-established:
  - "Section-level merge by ## headings: files parsed into preamble + named sections, compared as atomic units"
  - "Code-block-aware section parsing: ## inside fenced code blocks ignored"
  - "NEW-defines-order: merged output follows NEW section ordering, user additions appended"

requirements-completed: [MERGE-01, MERGE-02, MERGE-03, MERGE-04]

# Metrics
duration: 3min
completed: 2026-03-27
---

# Phase 20 Plan 01: 3-Way Merge Summary

**Section-level 3-way merge algorithm with 13-case classification table, conflict resolution via AskUserQuestion, and 2-way diff bootstrap for pre-v1.5.0 projects**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-27T00:16:35Z
- **Completed:** 2026-03-27T00:19:34Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Replaced Step 3 placeholder skip logic with complete section-level 3-way merge algorithm covering 13 classification cases
- Added 2-way diff bootstrap path for pre-v1.5.0 projects that lack .originals/ baseline files
- Added conflict resolution presenting each conflict one at a time via AskUserQuestion with keep-mine, take-plugin, custom, and chat options
- Added File Merges sub-section to Step 4 upgrade summary template with auto-merge counts and conflict resolution stats

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite Step 3 with section-level 3-way merge and 2-way bootstrap** - `bece6fa` (feat)
2. **Task 2: Update Step 4 summary format with merge statistics** - `bceb928` (feat)

## Files Created/Modified
- `doc-writer/skills/upgrade/SKILL.md` - Complete upgrade skill with 3-way merge in Step 3, 2-way bootstrap in Step 3.1, File Merges in Step 4 summary

## Decisions Made
- Section parsing rules placed once at the top of Step 3 and referenced by both 2-way and 3-way paths -- avoids duplication
- Removal conflict gets its own AskUserQuestion format (Remove it / Keep mine / Chat) since "Take plugin update" doesn't make sense when upstream removed the section
- 2-way diff bootstrap uses "Section Difference" and "New Section" headers (not "Merge Conflict") since there is no true 3-way conflict without a BASE

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Merge algorithm complete; upgrade skill now handles all file merge scenarios
- Q&A gap detection (Phase 21) is the remaining upgrade feature, as noted in the updated Notes section
- All 4 MERGE requirements (MERGE-01 through MERGE-04) satisfied

---
*Phase: 20-3-way-merge*
*Completed: 2026-03-27*
