---
phase: 3
slug: editor-agent
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-03
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual CC session testing (no automated test framework) |
| **Config file** | None -- this is a markdown-file plugin with no executable code |
| **Quick run command** | `claude --plugin-dir .` then invoke Editor via Agent tool on sample doc files |
| **Full suite command** | Manual: run full Author + Editor pipeline on a sample project, verify all EDIT requirements |
| **Estimated runtime** | ~5 minutes (manual session) |

---

## Sampling Rate

- **After every task commit:** Manual: load plugin with `claude --plugin-dir .`, run Editor on test doc files
- **After every plan wave:** Manual: run full Author + Editor pipeline on a sample project, verify all 4 EDIT requirements
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 minutes

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | EDIT-01 | manual | Grep edited docs for unlinked `code` mentions of known API symbols | N/A | ⬜ pending |
| 03-01-02 | 01 | 1 | EDIT-02 | manual | Compare Author output vs Editor output for AI patterns; check for em dashes, filler phrases | N/A | ⬜ pending |
| 03-01-03 | 01 | 1 | EDIT-03 | manual | Grep all edited docs for known term variants; verify terminology.yaml is generated | N/A | ⬜ pending |
| 03-01-04 | 01 | 1 | EDIT-04 | manual | Verify `.doc-writer/editor-report.md` exists with correct structure, severity levels | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Create sample documentation files with known AI-writing patterns (em dashes, filler phrases, significance inflation) for testing humanizer pass
- [ ] Create sample documentation files with deliberate terminology inconsistencies for testing terminology pass
- [ ] Create sample documentation files with unlinked `code` mentions and a mock API reference directory for testing cross-reference pass
- [ ] Ensure sample project has `.doc-writer/config.yaml` with paths configured (from Phase 1 setup)
- [ ] Ensure sample project has Author-generated docs with HTML comments (from Phase 2 Author output)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| All inline `code` mentions linked to API Reference | EDIT-01 | Markdown plugin -- no executable test framework | Inspect edited docs for unlinked code mentions of known API symbols |
| Humanizer removes AI-writing patterns | EDIT-02 | Subjective quality assessment of prose | Compare Author output vs Editor output; check for em dashes, filler, inflation |
| Cross-file terminology consistency | EDIT-03 | Requires semantic understanding of term equivalence | Inspect edited docs + terminology.yaml for consistent naming |
| Structured feedback format | EDIT-04 | Report structure inspection | Verify editor-report.md has BLOCKING/SUGGESTION/NITPICK items with required fields |

---

## Validation Sign-Off

- [ ] All tasks have manual verification procedures documented
- [ ] Sampling continuity: every task has a verification step
- [ ] Wave 0 covers all test fixture requirements
- [ ] No watch-mode flags
- [ ] Feedback latency < 5 minutes
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
