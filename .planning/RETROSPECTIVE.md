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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 13 | 28 | Established wave-based execution, Nyquist validation, gap-closure pipeline |

### Cumulative Quality

| Milestone | Bats Tests | Phases w/ Tests | Notes |
|-----------|------------|-----------------|-------|
| v1.0 | 10 (phase-13) + 31 (pkg) + 42 (setup) + 49 (auth) = 132 | 7/13 | Pre-Nyquist phases (1-6) lack bats; all content-verifiable |

### Top Lessons (Verified Across Milestones)

1. **Additive changes are safer than modifying existing files** — validated throughout v1.0 framework additions
2. **Runtime wiring bugs survive static verification** — must explicitly test end-to-end paths, not just file content
