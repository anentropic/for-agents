---
phase: 16
slug: use-cases
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bats-core (existing) |
| **Config file** | tests/ directory (existing) |
| **Quick run command** | `bats tests/test_setup.bats` |
| **Full suite command** | `bats tests/` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bats tests/test_setup.bats`
- **After every plan wave:** Run `bats tests/`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | CONT-01 | integration | `bats tests/test_setup.bats` | ❌ W0 | ⬜ pending |
| 16-01-02 | 01 | 1 | CONT-02 | integration | `bats tests/test_researcher.bats` | ❌ W0 | ⬜ pending |
| 16-02-01 | 02 | 2 | CONT-03 | integration | `bats tests/test_author.bats` | ❌ W0 | ⬜ pending |
| 16-02-02 | 02 | 2 | CONT-03 | integration | `bats tests/test_editor.bats` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_setup.bats` — add use cases Q&A validation tests (CONT-01)
- [ ] `tests/test_researcher.bats` — add use case expansion tests (CONT-02)
- [ ] `tests/test_author.bats` — add use-case page type tests (CONT-03)
- [ ] `tests/test_editor.bats` — add use-case blur detection tests (CONT-03)

*Existing bats infrastructure covers framework; new test cases needed for use case features.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Use Cases Q&A presents skippable step before personas | CONT-01 | AskUserQuestion interaction cannot be automated | Run `/doc-writer:setup` on a fresh project, verify Use Cases step appears before persona step and can be skipped |
| Promoted use cases appear as docs section at diataxis level | CONT-03 | Requires full pipeline run with page inventory review | Run `/doc-writer:write` on a project with use cases promoted, verify section appears in inventory |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
