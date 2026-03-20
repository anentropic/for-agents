---
phase: 4
slug: user-persona-and-full-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-03
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual CC session testing (no automated test framework) |
| **Config file** | None — markdown plugin with no executable code |
| **Quick run command** | `claude --plugin-dir .` then invoke Persona via Agent tool on sample doc set |
| **Full suite command** | Manual: run full Author > Editor > Persona pipeline on sample project, verify all PERS requirements |
| **Estimated runtime** | ~5-10 minutes per manual verification session |

---

## Sampling Rate

- **After every task commit:** Manual: load plugin with `claude --plugin-dir .`, run Persona on test doc set
- **After every plan wave:** Manual: run full Author > Editor > Persona pipeline on a sample project, verify all 5 PERS requirements
- **Before `/gsd:verify-work`:** Full pipeline verification must pass all PERS requirements
- **Max feedback latency:** ~5 minutes per manual verification

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | PERS-01 | manual (CC session) | Run Persona on sample project with audience config; verify `.doc-writer/scenarios.yaml` contains 3-5 goal-oriented scenarios | N/A — markdown plugin | ⬜ pending |
| 04-01-02 | 01 | 1 | PERS-02 | manual (inspect report) | Verify persona report shows navigation paths and goal-based evaluation, not checklist items | N/A | ⬜ pending |
| 04-01-03 | 01 | 1 | PERS-03 | manual (inspect report) | Verify `.doc-writer/persona-report.md` has per-scenario verdicts with gap details for non-PASS scenarios | N/A | ⬜ pending |
| 04-01-04 | 01 | 1 | PERS-04 | manual (multi-pass test) | Run Persona twice: once to get FAIL, then after Author revision to verify re-evaluation; check only FAIL triggers revision | N/A | ⬜ pending |
| 04-01-05 | 01 | 1 | PERS-05 | manual (multi-audience test) | Run Persona with two audiences configured; verify each produces independent scenarios and verdicts | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Ensure sample project has Editor-cleaned docs in `paths.docs_root` (from Phase 3 output — no HTML comments)
- [ ] Ensure sample project has `.doc-writer/config.yaml` with audience data (from Phase 1 setup)
- [ ] Optionally add `domain_context` and `discovery_story` fields to test audience config for richer scenario generation
- [ ] Prepare a doc set with a known gap (e.g., missing error handling page) to verify FAIL detection
- [ ] Prepare a doc set with known friction (e.g., unclear steps) to verify PARTIAL detection
- [ ] Configure a second audience to test multi-audience scenario generation (PERS-05)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Scenario generation from audience context | PERS-01 | Agent generates scenarios via LLM reasoning — no deterministic output to assert | Run Persona on sample project; verify 3-5 scenarios in scenarios.yaml; check goals are concrete and audience-appropriate |
| Goal-oriented simulation (not checklist) | PERS-02 | Simulation quality is qualitative — requires human judgment | Inspect persona-report.md; verify navigation paths show page-by-page tracing; verify verdicts based on goal achievability |
| Verdict accuracy (PASS/PARTIAL/FAIL) | PERS-03 | Verdict calibration requires judgment about goal achievability | Prepare doc set with known gaps; verify FAIL for missing content, PARTIAL for friction, PASS for smooth paths |
| Revision loop protocol in prompt | PERS-04 | Protocol is documented in prompt, not executed as code | Read agent prompt; verify revision rules are stated; run multi-pass test to verify Persona reuses scenarios and tracks convergence |
| Multi-audience parallel execution | PERS-05 | Parallel spawning is Phase 5 orchestrator concern; Phase 4 verifies agent supports audience parameter | Configure two audiences; run Persona for each; verify independent scenarios and verdicts |

---

## Validation Sign-Off

- [ ] All tasks have manual verification instructions
- [ ] Sampling continuity: each task has clear test instructions
- [ ] Wave 0 covers all preparation needed for manual testing
- [ ] No watch-mode flags
- [ ] Feedback latency < 10 minutes per verification session
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
