# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Doc Writer Plugin

**Shipped:** 2026-03-19
**Phases:** 13 | **Plans:** 28 | **Timeline:** 17 days (2026-03-02 → 2026-03-19)

### What Was Built

- Full Author > Editor > Persona multi-agent pipeline with `/doc-writer:write`, `/doc-writer:review`, `/doc-writer:edit` commands
- Claude Code plugin packaging (`doc-writer/.claude-plugin/plugin.json` + marketplace.json) with multi-plugin-ready repo structure
- doc-researcher agent that enriches project context from source code and framework config before pipeline runs
- Four built-in doc system frameworks: mkdocs-material, sphinx-shibuya, odoc (OCaml), plain-markdown — each with Q&A data files, guidance files, and scaffold templates
- Unknown framework research mode: researcher generates guidance, Q&A, and scaffold files dynamically for any framework
- Nyquist bats test suites for every phase from Phase 7 onward (static-verifiable content checks)

### What Worked

- **Wave-based parallel execution**: Wave 0 (test stubs RED) → Wave 1 (implementation GREEN) pattern caught integration issues before they accumulated
- **Gap-closure phases**: The audit → plan-milestone-gaps → Phase 13 pipeline closed the P11-03 blocker and two tech debt items cleanly without disrupting the existing 12 phases
- **Researcher-first for new frameworks**: Phase 12's approach of researching odoc before planning produced a plan with zero implementation revisions needed
- **Q&A data files (.qa.md) pattern**: Separating framework Q&A from SKILL.md body made odoc and sphinx-shibuya additions completely additive — zero SKILL.md restructuring for each new framework
- **Generic variable inference table**: Phase 13 fixed P11-03 generically rather than with a sphinx-shibuya-specific patch, future-proofing all scaffold additions

### What Was Inefficient

- **Milestone audit timing**: The v1.0 audit was run after all 12 phases, finding the P11-03 scaffold variable mismatch that had been in the code since Phase 11. Running a quick integration check after Phase 11 would have caught it earlier.
- **VALIDATION.md nyquist_compliant frontmatter**: 8 phases have `nyquist_compliant: false` because the Nyquist system was adopted mid-milestone (Phase 7). Pre-adoption phases never got their frontmatter updated. Not a functional issue but a paperwork debt.
- **Plan checkbox inconsistency in ROADMAP.md**: Several phases showed `[ ]` for plan checkboxes despite being complete — the gsd-tools `phase complete` command updates the progress table but not always the plan-level checkboxes within phase sections.

### Patterns Established

- **Directory scaffold pattern**: When a framework needs multiple output files (e.g., odoc: `doc/dune` + `doc/index.mld`), use `scaffolds/{framework}/` directory instead of a single scaffold file. SKILL.md Step 2b.3 now checks for this pattern generically.
- **Generic variable inference table**: All scaffold template variables now have a canonical inference source documented in SKILL.md. New scaffolds add rows to the table — they don't need custom substitution logic.
- **doc-researcher as context enricher**: The researcher runs during setup and writes `context.md` which all downstream agents read at startup. This pattern cleanly separates project analysis from doc generation.
- **Framework preferences conditional**: Use "has framework config file" (not named frameworks) as the gate for framework-specific enrichment in doc-researcher — naturally handles new frameworks without code changes.

### Key Lessons

1. **Integration checks should gate phase completion, not just milestone completion.** P11-03 was a wiring bug between Phase 11 (scaffold variables) and Phase 10 (substitution logic) that only appeared during the milestone audit. A mini integration check after each phase that modifies SKILL.md would have caught this immediately.
2. **Additive is better than modifying.** Every framework addition that was "additive only" (new .qa.md, new .md, new scaffolds/) went smoothly. Every change that required modifying existing SKILL.md logic needed careful regression testing. Design new features to add files rather than modify existing ones where possible.
3. **The gap between static verification and runtime wiring is the primary source of bugs.** All 12 VERIFICATION.md files passed — but the P11-03 bug only appeared during integration checking because static verification confirmed the scaffold file existed and had correct content, but didn't trace the variable substitution path end-to-end. Runtime path coverage needs explicit integration tests.
4. **Bats for prompt/markdown files works well.** Grep-based bats tests (does the file contain this string?) are fast, deterministic, and catch the most common mistakes in prompt engineering. The ~5-second suite runtime means they're always run after every commit.

### Cost Observations

- Model mix: ~70% opus (researcher + planner + executor), ~30% sonnet (plan-checker + verifier)
- Notable: Opus was worth it for researcher and planner agents — plan quality directly determines execution quality. Sonnet plan-checker caught real issues (checked all 8 Nyquist dimensions) without requiring opus.

---

## Milestone: v1.4.0 — Content & Navigation

**Shipped:** 2026-03-22
**Phases:** 4 | **Plans:** 8 | **Timeline:** 2 days (2026-03-21 → 2026-03-22)

### What Was Built

- Mermaid diagram awareness across all 4 doc systems (mkdocs-material, sphinx-shibuya, odoc, plain-markdown) with framework-specific wrapper syntax
- Three-strategy navigation (sections-as-tabs, single Docs tab, sidebar-only) for sphinx-shibuya and mkdocs-material with scaffold variable substitution and section index pages with dual-placement abstracts
- Use Cases Q&A capture before user personas with skip/infer path, optional promotion to docs section with discovery/showcase page template, and editor blur detection
- Odoc-native .mld output mode with conditional write workflow, dune registration, external author-notes, and .mld discovery across editor/tester/SKILL
- .mli doc comment enrichment proposal workflow with scope control, quality rules, and pipeline summary integration
- OCaml scan-exports language case for public symbol detection from .mli files

### What Worked

- **Assumptions discussion before planning**: `/gsd:list-phase-assumptions` for both phases 16 and 17 caught corrections early — ordering (use cases before personas), page template depth (discovery/showcase), and inference scope (agent-context only, not docs-section) were all corrected before a single plan was written
- **Auto-advance pipeline**: Phases 16 and 17 both ran assumptions → plan → execute → verify in a single auto chain, completing the entire milestone in one session
- **Integration checker caught a real bug**: OCML-04 scope persistence gap was invisible to per-phase verification but caught by the milestone integration check. The odoc Q&A scope answer wasn't being persisted to config.yaml — a cross-session wiring bug.
- **Inline fix for small gaps**: Instead of creating a full gap-closure phase for the OCML-04 scope persistence issue (3 files, 3 edits), the user opted to fix inline — saving an entire phase cycle for a trivial fix.

### What Was Inefficient

- **No CONTEXT.md for either phase**: Both phases 16 and 17 skipped discuss-phase and planned from research + requirements only. The assumptions discussion substituted well, but formally captured CONTEXT.md would have been passed to all downstream agents automatically.
- **Roadmap success criteria text contradicted requirements**: Phase 16 roadmap said "after user personas" but CONT-01 said "before". This was caught during assumptions but should have been caught during roadmap creation.

### Patterns Established

- **Non-diataxis page types follow README/MAINTAINER pattern**: Use-case pages get inline templates in doc-author.md (like Sections 4/5 for README/MAINTAINER) rather than diataxis reference files. Editor gets inline blur signals rather than loading a reference file.
- **External author-notes for non-HTML-compatible doc systems**: When a doc system can't contain HTML comments (.mld for odoc), internal notes go to `.doc-writer/author-notes.md`. This pattern is extensible to future doc systems.
- **Enrichment as proposals, not auto-edits**: When agents propose changes to user source files, write proposals to a review file — never edit source directly.
- **odoc scope persistence exception**: Framework Q&A answers generally stay in-memory, but cross-session values (like odoc author scope) must be persisted to config.yaml.

### Key Lessons

1. **Integration checks catch cross-session wiring bugs that phase verification misses.** The OCML-04 scope gate was correct within a session (Q&A answer in memory) but broken across sessions (no persistence). Always verify data flow across the session boundary.
2. **Assumptions discussion is cheap insurance.** Two 5-minute assumptions discussions saved hours of replanning. The user caught 3 corrections in Phase 16 and 1 in Phase 17 that would have produced incorrect plans.
3. **Small gaps don't need phases.** The 3-edit OCML-04 fix was better done inline than through the full plan→execute→verify pipeline. A full phase would have cost ~10x more tokens for the same outcome.

### Cost Observations

- Model mix: ~70% opus (researcher + planner + executor), ~30% sonnet (plan-checker + verifier + integration-checker)
- Sessions: 1 session for all 4 phases + audit + fix + milestone completion
- Notable: Auto-advance eliminated context-switching overhead between phases

---

## Milestone: v1.5.0 — Plugin Upgrade Helpers

**Shipped:** 2026-03-27
**Phases:** 4 | **Plans:** 5 | **Timeline:** 2 days (2026-03-26 → 2026-03-27)

### What Was Built

- `/doc-writer:upgrade` command: 6-step flow (version detection, config migration, file merge, Q&A gap detection, context refresh, finalize) in a standalone SKILL.md (348 lines)
- Setup foundation: `plugin_version` tracking, `.originals/` pristine file storage, `qa_answers` persistence — all integrated into existing setup SKILL.md
- Section-level 3-way merge: 13-case classification table for BASE/USER/NEW comparison, AskUserQuestion per-conflict resolution, code-block-aware `##` heading parser
- 2-way diff bootstrap for pre-v1.5.0 projects: per-section accept/reject with `.originals/` creation after completion
- Q&A gap detection: set-difference of `.qa.md` question IDs against stored `qa_answers`, FALLBACK framework skip
- Conditional researcher re-run: only triggers when config fields or Q&A answers actually changed

### What Worked

- **Assumptions discussion for Phase 20 caught a design question early**: The "sections removed in NEW" handling was ambiguous until the user clarified: auto-remove if USER==BASE, conflict if USER!=BASE. This insight shaped the entire 13-case classification table.
- **Single-file phases are fast**: Phases 19-21 each modified only `doc-writer/skills/upgrade/SKILL.md`. The executor agents completed in 2-3 minutes each with zero file conflicts.
- **Auto-advance from plan-phase through execute**: With `--auto` flag, phases 19-21 went from research → plan → verify → execute → verify in one uninterrupted chain.
- **Worktree isolation eliminated merge conflicts**: Each executor ran in its own worktree, preventing concurrent file contention (though ROADMAP.md/STATE.md conflicts still needed manual resolution post-merge).

### What Was Inefficient

- **Worktree merge conflict resolution for STATE.md/ROADMAP.md**: Every worktree merge produced the same ROADMAP.md/STATE.md conflict pattern. The orchestrator resolves these manually each time — a predictable, automatable step.
- **VALIDATION.md created pre-execution, never updated post-execution**: All 4 phases have `nyquist_compliant: false` because the VALIDATION.md files were written before plans existed and never revisited after execution. The plans themselves had `<automated>` grep verify commands.
- **21-01-SUMMARY.md missing requirements_completed field**: The executor for Phase 21 didn't populate the `requirements_completed` frontmatter, breaking the 3-source cross-reference during audit (verified via VERIFICATION.md instead).

### Patterns Established

- **Upgrade as separate skill, not setup extension**: The upgrade workflow is complex enough (6 steps, 348 lines) to warrant its own SKILL.md. Setup stays focused on first-time configuration.
- **Claude-as-reader for structured comparison**: Section-level merge, config field diffing, and Q&A gap detection all rely on Claude reading and comparing text — no external diff tools. This works because all files are small (<400 lines) and section-structured.
- **Conditional expensive operations**: Researcher re-run only fires when config/Q&A actually changed. This pattern avoids unnecessary token spend on upgrade runs that only merge files.
- **FALLBACK framework skip pattern**: When a feature depends on upstream plugin files (`.qa.md`), FALLBACK frameworks that use project-local files instead should skip with a clear message rather than error.

### Key Lessons

1. **Worktree merge conflicts are predictable and should be automated.** Every phase execution produces the same ROADMAP.md/STATE.md conflict. The orchestrator's manual resolution is reliable but repetitive.
2. **VALIDATION.md should be created after planning, not before.** Writing VALIDATION.md before the plan exists means the task verification map can't reference real plan task IDs or `<automated>` commands. Creating it after planning would allow accurate pre-population.
3. **Single-file phases execute extremely fast.** When the entire phase modifies one file, worktree isolation, plan verification, and execution all complete in minutes. The overhead-to-work ratio is excellent.
4. **Assumptions discussion substitutes well for discuss-phase context.** Phases 20 and 21 skipped `/gsd:discuss-phase` entirely, using assumptions review feedback instead. The planner and executor had sufficient context from REQUIREMENTS.md + RESEARCH.md + the assumptions corrections.

### Cost Observations

- Model mix: ~70% opus (researcher + planner + executor), ~30% sonnet (plan-checker + verifier + integration-checker)
- Sessions: 2 sessions — Phase 18-19 in session 1, Phase 20-21 + audit + milestone completion in session 2
- Notable: Auto-advance with `--auto --no-transition` eliminated all inter-phase context switching

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 13 | 28 | Established wave-based execution, Nyquist validation, gap-closure pipeline |
| v1.4.0 | 4 | 8 | Assumptions-first planning, auto-advance pipeline, inline gap fixes |
| v1.5.0 | 4 | 5 | Worktree isolation, single-file phases, auto-advance with --no-transition |

### Cumulative Quality

| Milestone | Bats Tests | Phases w/ Tests | Notes |
|-----------|------------|-----------------|-------|
| v1.0 | 10 (phase-13) + 31 (pkg) + 42 (setup) + 49 (auth) = 132 | 7/13 | Pre-Nyquist phases (1-6) lack bats; all content-verifiable |
| v1.4.0 | grep-based acceptance criteria per task | 4/4 | All phases have VALIDATION.md; grep-based verify per task |
| v1.5.0 | grep-based acceptance criteria per task | 4/4 | All phases have VALIDATION.md; nyquist_compliant frontmatter not updated post-execution |

### Top Lessons (Verified Across Milestones)

1. **Additive changes are safer than modifying existing files** — validated throughout v1.0 framework additions
2. **Runtime wiring bugs survive static verification** — must explicitly test end-to-end paths, not just file content
3. **Integration checks catch cross-session bugs** — validated in v1.4.0 (OCML-04 scope persistence)
4. **Assumptions discussion before planning catches corrections cheaply** — validated in v1.4.0 (3 corrections in Phase 16), v1.5.0 (section removal handling in Phase 20)
5. **Single-file phases with worktree isolation execute extremely fast** — validated in v1.5.0 (3 phases at 2-3 min each)
