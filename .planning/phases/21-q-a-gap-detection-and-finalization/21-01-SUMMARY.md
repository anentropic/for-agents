---
phase: 21-q-a-gap-detection-and-finalization
plan: 01
subsystem: upgrade
tags: [qa-gap-detection, researcher-rerun, upgrade-skill, agent-tool]

# Dependency graph
requires:
  - phase: 20-3-way-merge
    provides: upgrade SKILL.md with Steps 1-4 (version detection, config migration, file merge, finalize)
  - phase: 18-setup-foundation
    provides: qa_answers section in config.yaml and AskUserQuestion Q&A pattern
provides:
  - Step 3.5 Q&A gap detection in upgrade SKILL.md
  - Step 4 conditional researcher re-run in upgrade SKILL.md
  - Complete 6-step upgrade flow (1, 2, 3, 3.5, 4, 5)
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: [qa-gap-detection-via-key-derivation-comparison, conditional-researcher-rerun]

key-files:
  created: []
  modified: [doc-writer/skills/upgrade/SKILL.md]

key-decisions:
  - "Step 3.5 uses same key derivation as setup (lowercase + replace spaces with underscores) for exact compatibility"
  - "FALLBACK frameworks skip Q&A gap detection entirely -- only plugin-shipped .qa.md files are valid sources"
  - "Follow-on sub-sections ignored during gap detection -- tied to parent question answer, handled during original setup"
  - "Researcher re-run conditional on Step 2 config changes OR Step 3.5 Q&A changes, not file merges"
  - "Updated Step 1 and Step 3.1 references from Step 4 to Step 5/Step 3.5 to match new numbering"

patterns-established:
  - "Q&A gap detection: read .qa.md headers, derive keys, compare against qa_answers, present only absent keys"
  - "Conditional agent spawning: track change flags across steps, only spawn when changes warrant re-run"

requirements-completed: [QA-01, QA-02]

# Metrics
duration: 2min
completed: 2026-03-27
---

# Phase 21 Plan 01: Q&A Gap Detection and Finalization Summary

**Q&A gap detection (Step 3.5) and conditional researcher re-run (Step 4) added to upgrade SKILL.md, completing the 6-step upgrade flow**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-27T11:05:20Z
- **Completed:** 2026-03-27T11:08:14Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Added Step 3.5: Q&A Gap Detection -- detects new framework questions by comparing .qa.md headers against stored qa_answers keys, asks only unanswered questions, persists new answers before researcher re-run
- Added Step 4: Context Refresh -- conditionally spawns doc-researcher agent when Step 2 config changes or Step 3.5 Q&A changes occurred
- Renumbered Finalize from Step 4 to Step 5 with updated summary template including Q&A Updates and Context Refresh sections
- Added Agent to allowed-tools frontmatter for researcher spawning capability
- Removed stale "separate future upgrade" note, replaced with "complete upgrade flow" in Notes section
- Fixed Step 1 and Step 3.1 cross-references to match new step numbering

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Q&A gap detection step and Agent to allowed-tools** - `1c3cce8` (feat)
2. **Task 2: Add context refresh step, renumber finalize, update summary and Notes** - `49cb17c` (feat)

## Files Created/Modified
- `doc-writer/skills/upgrade/SKILL.md` - Extended from 4 steps to 6 steps (1, 2, 3, 3.5, 4, 5) with Q&A gap detection, conditional researcher re-run, and updated summary template

## Decisions Made
- Step 3.5 uses identical key derivation rule as setup SKILL.md Step 2b.5 (lowercase header, replace spaces with underscores) -- any deviation would cause false positives
- FALLBACK frameworks skip Q&A gap detection entirely since their .qa.md files are researcher-generated and not shipped by the plugin
- Follow-on sub-sections (### Follow-on:) are ignored during gap detection -- they are tied to parent question answers and were handled during the original setup session
- Researcher re-run is conditional on config or Q&A changes only, not file merge changes -- file merges change guidance files consumed directly by agents, not through context.md
- Updated stale step references in Step 1 (Step 4 -> Step 5) and Step 3.1 (Skip to Step 4 -> Skip to Step 3.5) as a deviation fix

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed stale step references in Steps 1 and 3.1**
- **Found during:** Task 2 (renumbering)
- **Issue:** Step 1 line 44 referenced "Step 4 summary" and Step 3.1 line 165 referenced "Skip to Step 4" -- both should point to new step numbers after renumbering
- **Fix:** Updated Step 1 references from "Step 4" to "Step 5", updated Step 3.1 from "Skip to Step 4" to "Skip to Step 3.5"
- **Files modified:** doc-writer/skills/upgrade/SKILL.md
- **Verification:** grep confirmed no remaining "Step 4" references outside the new Step 4: Context Refresh heading
- **Committed in:** 49cb17c (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Essential for correctness -- stale step references would confuse the agent following the skill instructions. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 21 is the final phase of the v1.5.0 milestone
- The upgrade SKILL.md now delivers the complete upgrade flow: version detection, config migration, file merge, Q&A gap detection, context refresh, and summary
- No further phases are planned -- v1.5.0 is ready for milestone completion

---
*Phase: 21-q-a-gap-detection-and-finalization*
*Completed: 2026-03-27*

## Self-Check: PASSED
- All files exist: doc-writer/skills/upgrade/SKILL.md, 21-01-SUMMARY.md
- All commits exist: 1c3cce8, 49cb17c
