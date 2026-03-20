---
phase: 7
slug: doc-writer-plugin-packaging
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bats (existing) |
| **Config file** | tests/phase-01-validation.bats (existing) |
| **Quick run command** | `bats tests/` |
| **Full suite command** | `bats tests/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bats tests/`
- **After every plan wave:** Run `bats tests/`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 7-01-01 | 01 | 1 | plugin-manifest | file-check | `test -f doc-writer/.claude-plugin/plugin.json` | ❌ W0 | ⬜ pending |
| 7-01-02 | 01 | 1 | dir-structure | file-check | `test -d doc-writer/skills && test -d doc-writer/agents` | ❌ W0 | ⬜ pending |
| 7-01-03 | 01 | 1 | marketplace | file-check | `test -f .claude-plugin/marketplace.json` | ❌ W0 | ⬜ pending |
| 7-01-04 | 01 | 2 | test-paths | bats | `bats tests/` | ✅ | ⬜ pending |
| 7-01-05 | 01 | 2 | namespace | grep | `grep -r "doc-writer:" doc-writer/agents/` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `doc-writer/.claude-plugin/plugin.json` — plugin manifest (created in move task)
- [ ] `.claude-plugin/marketplace.json` — repo-level marketplace entry
- [ ] `doc-writer/skills/` and `doc-writer/agents/` directories (created during file moves)

*Existing bats infrastructure covers all other verification.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Plugin installs correctly | plugin-install | Requires CC CLI | Run `claude plugin install ./doc-writer` and verify skills load |
| Namespace prefix visible | namespace-ux | Requires CC runtime | Open CC, run `/doc-writer:write --help` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
