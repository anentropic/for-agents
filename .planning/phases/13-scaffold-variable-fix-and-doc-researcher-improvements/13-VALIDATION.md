---
phase: 13
slug: scaffold-variable-fix-and-doc-researcher-improvements
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bats (Bash Automated Testing System) |
| **Config file** | none — tests use PROJECT_ROOT variable |
| **Quick run command** | `bats tests/phase-13-validation.bats` |
| **Full suite command** | `bats tests/phase-13-validation.bats` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bats tests/phase-13-validation.bats`
- **After every plan wave:** Run `bats tests/phase-13-validation.bats`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 0 | P11-03, MISSING-01, MISSING-02 | unit | `bats tests/phase-13-validation.bats` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 1 | P11-03 | unit | `bats tests/phase-13-validation.bats` | ❌ W0 | ⬜ pending |
| 13-03-01 | 03 | 1 | MISSING-01, MISSING-02 | unit | `bats tests/phase-13-validation.bats` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase-13-validation.bats` — 10 stubs for P11-03 (7 tests), MISSING-01 (1 test), MISSING-02 (2 tests)
- No framework install needed — bats already available from prior phases
- No shared fixtures needed — tests use PROJECT_ROOT variable

*Wave 0 must exist before any Wave 1 tasks execute.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| conf.py generated with correct project_name / author_name / copyright_year / github_url | P11-03 | Requires running /doc-writer:setup against a real project with a sphinx-shibuya config | In a test project dir with a git remote and pyproject.toml/setup.py, run setup skill and select sphinx-shibuya; verify generated conf.py contains real values not `{project_name}` etc. |
| doc-researcher uses WebFetch for unknown framework | MISSING-01 | Requires running researcher against an unknown framework at runtime | Run setup skill with an unknown framework name; verify researcher produces HIGH (not LOW) confidence output |
| Framework Preferences populated for sphinx-shibuya in context.md | MISSING-02 | Requires running full setup flow to inspect context.md output | Run setup with sphinx-shibuya; verify context.md contains `## Framework Preferences` section |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
