---
phase: 12
slug: add-odoc-framework-for-ocaml-projects
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bats (Bash Automated Testing System) |
| **Config file** | none — tests use PROJECT_ROOT variable |
| **Quick run command** | `bats tests/phase-12-validation.bats` |
| **Full suite command** | `bats tests/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bats tests/phase-12-validation.bats`
- **After every plan wave:** Run `bats tests/`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 0 | P12-01..P12-08 | unit | `bats tests/phase-12-validation.bats` | ❌ W0 | ⬜ pending |
| 12-02-01 | 02 | 1 | P12-01 | unit | `bats tests/phase-12-validation.bats -f "P12-01"` | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 1 | P12-07 | unit | `bats tests/phase-12-validation.bats -f "P12-07"` | ❌ W0 | ⬜ pending |
| 12-03-01 | 03 | 1 | P12-02 | unit | `bats tests/phase-12-validation.bats -f "P12-02"` | ❌ W0 | ⬜ pending |
| 12-03-02 | 03 | 1 | P12-05 | unit | `bats tests/phase-12-validation.bats -f "P12-05"` | ❌ W0 | ⬜ pending |
| 12-03-03 | 03 | 1 | P12-06 | unit | `bats tests/phase-12-validation.bats -f "P12-06"` | ❌ W0 | ⬜ pending |
| 12-04-01 | 04 | 1 | P12-03 | unit | `bats tests/phase-12-validation.bats -f "P12-03"` | ❌ W0 | ⬜ pending |
| 12-05-01 | 05 | 2 | P12-04 | unit | `bats tests/phase-12-validation.bats -f "P12-04"` | ❌ W0 | ⬜ pending |
| 12-05-02 | 05 | 2 | P12-08 | unit | `bats tests/phase-12-validation.bats -f "P12-08"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase-12-validation.bats` — stubs for P12-01 through P12-08
- [ ] `brew install bats-core` — if not already installed (likely present from Phase 7)

*Wave 0 must exist before any Wave 1 tasks execute.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Q3 dynamic sub-topic options generated from project scanning | P12-07 | Requires live OCaml project with dune files to verify runtime scanning behavior | Run setup skill against `ocaml-spectrum` or `ocaml-oktree`; verify Q3 presents module-derived sub-topic suggestions |
| Multi-library scaffold generates per-package files | P12-03 | Requires multi-package dune-project to verify loop behavior | Apply scaffold to `ocaml-spectrum` (5 packages); verify 5 secondary template instantiations |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
