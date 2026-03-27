---
gsd_state_version: 1.0
milestone: v1.5.0
milestone_name: Plugin Upgrade Helpers
status: Milestone complete
stopped_at: Completed 21-01-PLAN.md
last_updated: "2026-03-27T11:17:12.571Z"
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 5
  completed_plans: 5
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-26)

**Core value:** Produce library documentation that the project author can publish with minimal tweaks -- docs written from the end user's perspective, not the builder's.
**Current focus:** Phase 21 — q-a-gap-detection-and-finalization

## Current Position

Phase: 21
Plan: Not started

## Performance Metrics

**Velocity:**

- Total plans completed: 36 (28 from v1.0, 8 from v1.4.0)
- Average duration: ~2.5 min
- Total execution time: ~1.5 hours

**By Phase:** (v1.4.0 data)

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 14 | 2 | 3 min | 1.5 min |
| Phase 15 | 2 | 5 min | 2.5 min |
| Phase 16 | 2 | 5 min | 2.5 min |
| Phase 17 | 2 | 5 min | 2.5 min |

**Recent Trend:**

- Last 4 plans (v1.4.0): 17-01 (3 min), 17-02 (2 min), 16-02 (2 min), 16-01 (3 min)
- Trend: Stable

*Updated after each plan completion*
| Phase 18 P01 | 2min | 2 tasks | 2 files |
| Phase 18 P02 | 2min | 2 tasks | 2 files |
| Phase 19 P01 | 3min | 2 tasks | 2 files |
| Phase 20 P01 | 3min | 2 tasks | 1 files |
| Phase 21 P01 | 2min | 2 tasks | 1 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Research]: .originals/ directory is the merge base -- must be created by setup before upgrade can function
- [Research]: qa_answers section in config.yaml is prerequisite for Q&A gap detection
- [Research]: Section-level merge (by ## headings) prevents silent prose corruption vs line-level diff3
- [Research]: Claude-as-reader for YAML config migration -- more reliable than bash regex for structured data
- [Research]: Pre-v1.5.0 projects need 2-way diff bootstrap path since no .originals/ exist
- [Phase 18]: qa_answers stores literal label text, not internal codes -- simpler, no translation layer
- [Phase 18]: Backward compat reads legacy odoc_author_scope as fallback when qa_answers.scope absent
- [Phase 19]: No Agent tool in upgrade skill -- Phase 19 does not spawn sub-agents
- [Phase 19]: Meta-fields (version, plugin_version, detected, qa_answers) excluded from config migration comparison
- [Phase 19]: plugin_version written LAST in Step 4 to prevent false 'already up to date' on incomplete migrations
- [Phase 20]: Section-level merge by ## headings with 13-case classification table; preamble treated as __preamble__ section
- [Phase 20]: 2-way diff bootstrap writes NEW (not merged) to .originals/ -- establishes correct baseline for future 3-way merges
- [Phase 20]: Removal conflicts get dedicated AskUserQuestion format distinct from standard content conflicts
- [Phase 21]: Step 3.5 Q&A gap detection uses same key derivation as setup (lowercase + spaces to underscores) for exact compatibility
- [Phase 21]: FALLBACK frameworks skip Q&A gap detection entirely -- only plugin-shipped .qa.md files are valid sources
- [Phase 21]: Researcher re-run conditional on config or Q&A changes only, not file merges

### Roadmap Evolution

- v1.5.0 roadmap created: 4 phases (18-21), 14 requirements

### Pending Todos

None yet.

### Blockers/Concerns

- [Research]: Section-level merge algorithm needs precise specification during Phase 20 planning
- [Research]: .originals/ vs .plugin-base/ naming decision needed before Phase 18
- [Research]: Canonical plugin version source (plugin.json vs VERSION file) to confirm before Phase 19

## Session Continuity

Last session: 2026-03-27T11:08:14Z
Stopped at: Completed 21-01-PLAN.md
Resume file: None
