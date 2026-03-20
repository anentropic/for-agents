---
phase: 12-add-odoc-framework-for-ocaml-projects
plan: 02
subsystem: doc-framework
tags: [odoc, ocaml, dune, qa, scaffold, mld]

# Dependency graph
requires:
  - phase: 12-01
    provides: "Phase 12 validation scaffold (bats stubs for P12-01 through P12-08)"
provides:
  - "odoc.qa.md Q&A data file with Detection section, 3 questions, and follow-on sub-topic mechanism"
  - "scaffolds/odoc/ directory with 4 template files (doc_dune.sexp, index.mld, secondary_dune.sexp, secondary_index.mld)"
affects: [12-03, 12-04]

# Tech tracking
tech-stack:
  added: []
  patterns: ["directory-based scaffold (multiple template files in scaffolds/odoc/ instead of single file)", "follow-on sub-topic Q&A pattern with dynamic scan instructions"]

key-files:
  created:
    - doc-writer/skills/setup/defaults/odoc.qa.md
    - doc-writer/skills/setup/defaults/scaffolds/odoc/doc_dune.sexp
    - doc-writer/skills/setup/defaults/scaffolds/odoc/index.mld
    - doc-writer/skills/setup/defaults/scaffolds/odoc/secondary_dune.sexp
    - doc-writer/skills/setup/defaults/scaffolds/odoc/secondary_index.mld
  modified: []

key-decisions:
  - "Config file: doc/dune (NOT dune-project) to avoid false positive detection since every OCaml project has dune-project"
  - "Follow-on sub-topic questions define scan instructions and question template but NOT static option lists -- options generated dynamically at setup time"
  - "Directory-based scaffold with 4 separate template files for primary and secondary package variants"

patterns-established:
  - "Directory scaffold pattern: scaffolds/{framework}/ directory with multiple template files (new, alongside single-file scaffold pattern)"
  - "Follow-on sub-topic Q&A: question structure with dynamic scan targets defined in .qa.md, options computed at runtime"

requirements-completed: [P12-01, P12-03, P12-07]

# Metrics
duration: 2min
completed: 2026-03-19
---

# Phase 12 Plan 02: Odoc Q&A and Scaffold Summary

**Odoc Q&A data file with 3 questions (structure/scope/guides) plus follow-on sub-topic mechanism, and directory-based scaffold with 4 dune/mld template files**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-19T11:01:16Z
- **Completed:** 2026-03-19T11:03:12Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Created odoc.qa.md with Detection section (Config file: doc/dune), 3 questions matching CONTEXT.md locked decisions, and follow-on sub-topic mechanism with dynamic scan instructions
- Created scaffolds/odoc/ directory with 4 template files using {package_name}, {library_name}, {synopsis} variables matching real OCaml project patterns from ocaml-spectrum and ocaml-oktree
- All 3 verification tests pass: P12-01, P12-03, P12-07

## Task Commits

Each task was committed atomically:

1. **Task 1: Create odoc.qa.md Q&A data file** - `932c032` (feat)
2. **Task 2: Create scaffolds/odoc/ directory with 4 template files** - `6dbf940` (feat)

## Files Created/Modified
- `doc-writer/skills/setup/defaults/odoc.qa.md` - Q&A question set: Detection section, Q1 library structure, Q2 author scope, Q3 guide pages with multiSelect, follow-on sub-topic mechanism
- `doc-writer/skills/setup/defaults/scaffolds/odoc/doc_dune.sexp` - Template for doc/dune with (documentation) stanza
- `doc-writer/skills/setup/defaults/scaffolds/odoc/index.mld` - Template for primary package doc/index.mld with full diataxis structure
- `doc-writer/skills/setup/defaults/scaffolds/odoc/secondary_dune.sexp` - Template for secondary package doc/*/dune
- `doc-writer/skills/setup/defaults/scaffolds/odoc/secondary_index.mld` - Template for secondary package doc/*/index.mld

## Decisions Made
- Used `Config file: doc/dune` instead of `dune-project` in Detection section -- avoids false positive detection since every OCaml project has dune-project (per RESEARCH.md Pitfall 2)
- Follow-on sub-topic questions define scan targets and question template structure, with explicit "NOT static" instruction -- options are generated dynamically at setup time from project scanning
- Directory-based scaffold with 4 separate template files (primary/secondary x dune/mld) rather than a combined single file, matching the multi-file nature of odoc documentation setup

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Q&A and scaffold data files are ready for Plans 12-03 (odoc.md guidance) and 12-04 (SKILL.md integration)
- The directory scaffold pattern is new and will need SKILL.md's Step 2b.3 scaffold check to support directory scaffolds (handled in Plan 12-04)

## Self-Check: PASSED

All files verified present. All commits verified in git log.

---
*Phase: 12-add-odoc-framework-for-ocaml-projects*
*Completed: 2026-03-19*
