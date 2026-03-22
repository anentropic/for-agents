---
phase: 17
slug: ocaml-mld-mli-output
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bats-core (existing) |
| **Config file** | tests/ directory (existing) |
| **Quick run command** | `bats tests/phase-12-validation.bats` |
| **Full suite command** | `bats tests/` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run grep-based acceptance criteria checks
- **After every plan wave:** Run `bats tests/`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | OCML-02 | integration | grep-based on doc-author.md | ✅ | ⬜ pending |
| 17-01-02 | 01 | 1 | OCML-03 | integration | grep-based on doc-author.md | ✅ | ⬜ pending |
| 17-01-03 | 01 | 1 | OCML-05 | integration | grep-based on doc-editor.md | ✅ | ⬜ pending |
| 17-02-01 | 02 | 2 | OCML-04 | integration | grep-based on doc-author.md | ✅ | ⬜ pending |
| 17-02-02 | 02 | 2 | OCML-04 | integration | grep-based on write SKILL.md | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. Grep-based acceptance criteria verify against the modified agent files directly.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Doc-author writes .mld files with odoc syntax for odoc projects | OCML-02 | Requires running full doc-writer:write pipeline on an OCaml project | Run `/doc-writer:write` on an odoc project, verify .mld output |
| Doc-author registers .mld pages in doc/dune | OCML-03 | Requires full pipeline and dune file interaction | Verify doc/dune has new entries after write pass |
| Doc-author proposes .mli enrichment | OCML-04 | Requires scan-exports + undocumented value detection | Run on OCaml project with undocumented .mli values, check proposals file |
| Editor applies odoc syntax rules to .mld files | OCML-05 | Requires editor pipeline on .mld input | Run `/doc-writer:edit` on .mld files, verify odoc-aware passes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
