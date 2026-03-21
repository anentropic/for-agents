---
phase: 14
slug: foundations
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bats (existing) |
| **Config file** | `tests/` directory |
| **Quick run command** | `grep -c "mermaid" doc-writer/skills/setup/defaults/*.md` |
| **Full suite command** | `bats tests/` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick grep checks on modified files
- **After every plan wave:** Run `bats tests/`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | MERM-02 | grep | `grep -c "mermaid" doc-writer/skills/setup/defaults/mkdocs-material.md` | ✅ | ⬜ pending |
| 14-01-02 | 01 | 1 | MERM-02 | grep | `grep -c "mermaid" doc-writer/skills/setup/defaults/sphinx-shibuya.md` | ✅ | ⬜ pending |
| 14-01-03 | 01 | 1 | MERM-02 | grep | `grep -c "mermaid" doc-writer/skills/setup/defaults/odoc.md` | ✅ | ⬜ pending |
| 14-01-04 | 01 | 1 | MERM-02 | grep | `grep -c "mermaid" doc-writer/skills/setup/defaults/plain-markdown.md` | ✅ | ⬜ pending |
| 14-01-05 | 01 | 1 | MERM-03 | grep | `grep -c "sphinxcontrib.mermaid" doc-writer/skills/setup/defaults/scaffolds/sphinx-shibuya.py` | ✅ | ⬜ pending |
| 14-02-01 | 02 | 1 | CONT-04 | grep | `grep -c "Concepts" doc-writer/agents/doc-author.md` | ✅ | ⬜ pending |
| 14-02-02 | 02 | 1 | CONT-05 | grep | `grep -c "mermaid" doc-writer/agents/doc-author.md` | ✅ | ⬜ pending |
| 14-02-03 | 02 | 1 | OCML-01 | grep | `grep -c "ocaml" doc-writer/skills/write/scripts/scan-exports.sh` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test framework or fixtures needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Author proposes Concepts during inventory | CONT-04 | Requires running doc-writer:write pipeline | Run `/doc-writer:write` on a test project; verify Concepts appears in inventory |
| Author recommends diagram types | CONT-05 | Requires runtime author behavior | Run `/doc-writer:write`; verify mermaid diagrams appear where appropriate |
| Mermaid renders correctly per framework | MERM-01 | Requires building docs with each framework | Build docs with mkdocs/sphinx; verify mermaid renders |

*Runtime behaviors verified during `/gsd:verify-work`*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
