---
phase: 18-setup-foundation
plan: 01
subsystem: setup
tags: [plugin-version, originals, config-template, upgrade-foundation]

# Dependency graph
requires:
  - phase: 17-ocaml-mld-mli-output
    provides: "Shipped v1.4.0 with current setup skill and config template"
provides:
  - "plugin_version field in config-template.yaml for version tracking"
  - ".originals/ directory creation in setup Step 3 for merge base storage"
  - "qa_answers field in config-template.yaml for Q&A answer persistence"
  - "FALLBACK framework path handling for .originals/ copy"
affects: [18-02, 19-upgrade-skill, 20-3-way-merge]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "plugin.json as canonical version source read at setup time"
    - ".originals/ as merge base directory alongside user-facing copies"

key-files:
  created: []
  modified:
    - "doc-writer/skills/setup/defaults/config-template.yaml"
    - "doc-writer/skills/setup/SKILL.md"

key-decisions:
  - "plugin_version placed immediately after version: 1 in config template for visual grouping"
  - "qa_answers as empty object {} rather than empty array [] since answers are keyed by question ID"
  - "odoc_author_scope removed from template (migration to qa_answers handled in plan 02)"

patterns-established:
  - "Step 3 reads plugin.json before writing config.yaml -- version extraction pattern"
  - ".originals/ created as sibling to user-facing files in Step 3 -- pristine copy pattern"

requirements-completed: [SETUP-01, SETUP-02, SETUP-04]

# Metrics
duration: 2min
completed: 2026-03-26
---

# Phase 18 Plan 01: Plugin Version Tracking and Originals Storage Summary

**Setup skill now writes plugin_version from plugin.json and creates .originals/ with pristine guidance/rules copies for future upgrade 3-way merge**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-26T22:26:29Z
- **Completed:** 2026-03-26T22:29:12Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- config-template.yaml has plugin_version and qa_answers fields, odoc_author_scope removed
- SKILL.md Step 3 reads plugin.json version and writes it to config.yaml as plugin_version
- SKILL.md Step 3 creates .originals/ directory with pristine copies of guidance and rules files
- FALLBACK framework path correctly handled -- researcher-generated files used as baseline
- --reset confirmation message updated to mention .originals/ refresh
- Setup completion display updated with .originals/ and plugin version info

## Task Commits

Each task was committed atomically:

1. **Task 1: Add plugin_version to config-template.yaml** - `a91f0be` (feat)
2. **Task 2: Update SKILL.md Step 3 for plugin_version and .originals/** - `85dab29` (feat)

## Files Created/Modified
- `doc-writer/skills/setup/defaults/config-template.yaml` - Added plugin_version field after version: 1, added qa_answers: {} at end, removed odoc_author_scope
- `doc-writer/skills/setup/SKILL.md` - Step 3 item 2 reads plugin.json; new items 5-6 create .originals/ and copy pristine files; --reset and confirmation messages updated

## Decisions Made
None - followed plan as specified

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- config-template.yaml ready for plan 02 to add qa_answers persistence logic
- .originals/ creation pattern established for Phase 20 (3-Way Merge) to use as merge base
- plugin_version field ready for Phase 19 (Upgrade Skill) version comparison
- odoc_author_scope removal in template prepares for plan 02 migration to qa_answers

---
*Phase: 18-setup-foundation*
*Completed: 2026-03-26*
