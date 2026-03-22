---
phase: 17-ocaml-mld-mli-output
plan: 01
subsystem: agents
tags: [odoc, mld, ocaml, dune, doc-author, doc-editor, doc-user-tester]

# Dependency graph
requires:
  - phase: 14-foundations
    provides: OCaml scan-exports.sh language case, mermaid diagram syntax in guidance files
provides:
  - Odoc-native .mld output mode in doc-author with dune registration and external author-notes
  - .mld file discovery and odoc syntax handling in doc-editor
  - .mld file discovery and odoc homepage fallback in doc-user-tester
  - .mld mode detection in write SKILL.md
affects: [17-02-PLAN, doc-author, doc-editor, doc-user-tester, write-skill]

# Tech tracking
tech-stack:
  added: []
  patterns: [conditional doc_system branches for odoc output, external author-notes file pattern, dune mld_files registration step]

key-files:
  created: []
  modified:
    - doc-writer/agents/doc-author.md
    - doc-writer/agents/doc-editor.md
    - doc-writer/agents/doc-user-tester.md
    - doc-writer/skills/write/SKILL.md

key-decisions:
  - "External author-notes.md file for odoc instead of HTML comments -- .mld files have no comment mechanism"
  - "Odoc Output Mode section placed after General Writing Workflow, before Code Example Rules -- parallels Section 6 Python/MkDocs pattern"
  - "Odoc syntax adjustments as a separate subsection in editor, not inline in each pass -- cleaner separation"

patterns-established:
  - "Conditional doc_system branch pattern: When doc_system is odoc / When doc_system is NOT odoc"
  - "External notes file pattern: .doc-writer/author-notes.md organized by page name for odoc projects"
  - "Dune registration step: mandatory post-write step for every .mld file"

requirements-completed: [OCML-02, OCML-03, OCML-05]

# Metrics
duration: 3min
completed: 2026-03-22
---

# Phase 17 Plan 01: OCaml .mld/.mli Output Summary

**Odoc-native .mld output mode with conditional write workflow, dune registration, external author-notes, and .mld discovery across editor/tester/SKILL**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T02:07:14Z
- **Completed:** 2026-03-22T02:10:15Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Doc-author has complete odoc output mode with .mld file output rules, dune registration step, external author-notes, and 5 new checklist items
- Doc-editor discovers .mld files, reads external author-notes, recognizes odoc syntax in Pass 2/4, and skips HTML comment stripping for odoc
- Doc-user-tester discovers .mld files with odoc-specific homepage fallback chain (README > doc/index.mld > first .mld)
- Write SKILL mode detection scans .mld files for odoc projects with scaffold filtering

## Task Commits

Each task was committed atomically:

1. **Task 1: Add odoc output mode to doc-author Phase 2 write workflow** - `75e25bd` (feat)
2. **Task 2: Add .mld discovery and odoc syntax handling to editor, user-tester, and write SKILL** - `12a7cde` (feat)

## Files Created/Modified
- `doc-writer/agents/doc-author.md` - Odoc Output Mode section, Phase 2 checklist items, Phase 1 odoc file paths note
- `doc-writer/agents/doc-editor.md` - Conditional .mld discovery, external author-notes, odoc syntax adjustments, HTML comment bypass
- `doc-writer/agents/doc-user-tester.md` - Conditional .mld discovery, odoc homepage fallback chain
- `doc-writer/skills/write/SKILL.md` - Conditional .mld glob in mode detection with scaffold filtering

## Decisions Made
- External author-notes.md file for odoc instead of HTML comments -- .mld files have no invisible comment mechanism
- Odoc Output Mode section placed after General Writing Workflow, before Code Example Rules -- parallels Section 6 Python/MkDocs conditional formatting pattern
- Odoc syntax adjustments as a standalone subsection in editor rather than inline modifications to each pass -- cleaner separation of concerns

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 17-02 (.mli enrichment proposals) can proceed -- doc-author now has the odoc output mode foundation
- All four modified files have consistent conditional branching pattern for doc_system == odoc

## Self-Check: PASSED

All files verified present. All commits verified in git log.

---
*Phase: 17-ocaml-mld-mli-output*
*Completed: 2026-03-22*
