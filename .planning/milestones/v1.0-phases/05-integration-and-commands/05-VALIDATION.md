---
phase: 5
slug: integration-and-commands
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-04
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual CC session testing (no automated test framework) |
| **Config file** | None — markdown plugin with no executable code |
| **Quick run command** | `claude --plugin-dir .` then invoke `/doc-writer:write` on sample project |
| **Full suite command** | Manual: run all three commands on a sample project, verify all 5 INTG requirements |
| **Estimated runtime** | ~5-10 minutes per manual verification session |

---

## Sampling Rate

- **After every task commit:** Manual: load plugin with `claude --plugin-dir .`, run the specific command being implemented
- **After every plan wave:** Manual: run all three commands in sequence on a sample project, verify all INTG requirements
- **Before `/gsd:verify-work`:** Full pipeline verification must pass all INTG requirements
- **Max feedback latency:** ~5 minutes per manual verification

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | INTG-01, INTG-05 | manual (CC session) | Invoke `/doc-writer:write` on sample project; verify full pipeline runs, docs produced, gap-report.md generated | N/A — markdown plugin | ⬜ pending |
| 05-01-02 | 01 | 1 | INTG-02 | manual (CC session) | Invoke `/doc-writer:review` on project with existing docs; verify reports produced, no doc files modified | N/A | ⬜ pending |
| 05-01-03 | 01 | 1 | INTG-03 | manual (CC session) | Invoke `/doc-writer:edit` after a review; verify issues presented, targeted pages modified | N/A | ⬜ pending |
| 05-01-04 | 01 | 1 | INTG-04 | manual (GSD + CC session) | From a GSD session, invoke `/doc-writer:write`; verify command is available and runs | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Ensure sample project has `.doc-writer/config.yaml` (from Phase 1 setup)
- [ ] Ensure sample project has existing docs in `paths.docs_root` (for /doc:review and /doc:edit testing)
- [ ] Ensure sample project has source code with exported symbols (for gap detection testing)
- [ ] Ensure gap detection script is executable if applicable
- [ ] Prepare a sample project where at least one exported function has no documentation (for INTG-05 verification)
- [ ] Prepare editor-report.md and persona-report.md from a prior run (for /doc:edit testing)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full pipeline execution (Author > Editor > Persona) | INTG-01 | Pipeline orchestration via Agent tool requires interactive CC session | Run `/doc-writer:write` on sample project; verify all three agents run; verify docs in docs_root; verify summary report |
| Review-only audit (no content generation) | INTG-02 | Must verify NO doc files were modified | Run `/doc-writer:review` on existing docs; diff docs_root before/after; verify reports produced |
| Targeted edit with issue selection | INTG-03 | Issue presentation UX requires human interaction | Run `/doc-writer:edit` after review; verify issues from reports presented; select issues; verify only targeted pages changed |
| GSD session availability | INTG-04 | Requires running within a GSD workflow context | Start GSD session; invoke `/doc-writer:write`; verify command resolves and runs |
| Gap detection accuracy | INTG-05 | Must verify exported symbols correctly identified and compared against docs | Run `/doc-writer:write` on project with known undocumented exports; verify gap-report.md lists them |

---

## Validation Sign-Off

- [ ] All tasks have manual verification instructions
- [ ] Sampling continuity: each task has clear test instructions
- [ ] Wave 0 covers all preparation needed for manual testing
- [ ] No watch-mode flags
- [ ] Feedback latency < 10 minutes per verification session
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
