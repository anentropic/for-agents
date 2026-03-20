---
phase: 8
slug: doc-writer-skills-polish
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-16
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — SKILL.md/agent file verification via grep/file read |
| **Config file** | none |
| **Quick run command** | `grep -n "argument-hint" doc-writer/skills/*/SKILL.md doc-writer/agents/*.md` |
| **Full suite command** | `grep -rn "AskUserQuestion\|argument-hint" doc-writer/skills/*/SKILL.md doc-writer/agents/doc-author.md` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `grep -n "argument-hint" doc-writer/skills/*/SKILL.md doc-writer/agents/*.md`
- **After every plan wave:** Run `grep -rn "AskUserQuestion\|argument-hint" doc-writer/skills/*/SKILL.md doc-writer/agents/doc-author.md`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 8-01-01 | 01 | 1 | argument-hint for review | grep | `grep "argument-hint" doc-writer/skills/review/SKILL.md` | ✅ | ⬜ pending |
| 8-01-02 | 01 | 1 | AskUserQuestion in write | grep | `grep "AskUserQuestion" doc-writer/skills/write/SKILL.md` | ✅ | ⬜ pending |
| 8-01-03 | 01 | 1 | AskUserQuestion in setup | grep | `grep "AskUserQuestion" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 8-01-04 | 01 | 1 | AskUserQuestion in review | grep | `grep "AskUserQuestion" doc-writer/skills/review/SKILL.md` | ✅ | ⬜ pending |
| 8-01-05 | 01 | 1 | AskUserQuestion in edit | grep | `grep "AskUserQuestion" doc-writer/skills/edit/SKILL.md` | ✅ | ⬜ pending |
| 8-01-06 | 01 | 1 | AskUserQuestion in doc-author | grep | `grep "AskUserQuestion" doc-writer/agents/doc-author.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements — no test stubs needed. Verification is via grep on modified SKILL.md/agent files.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| "Type something else" + "Chat about this" options appear at bottom of every options list | CONTEXT decisions | Options presence requires reading full AskUserQuestion call context | Read each AskUserQuestion block in modified files; confirm both options present |
| --edit confirmation gate replaced with AskUserQuestion (binary choice) | CONTEXT decisions | Logic flow requires running the review skill | Read review/SKILL.md; confirm AskUserQuestion with "Proceed with edit" / "Skip" options |
| argument-hint values match CONTEXT.md spec exactly | CONTEXT decisions | Exact string match | grep frontmatter in all 4 skill files; compare to spec |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
