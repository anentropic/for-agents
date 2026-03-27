---
phase: 20
slug: 3-way-merge
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-27
---

# Phase 20 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual Claude Code skill testing (no compiled test framework — skill is a SKILL.md prompt file) |
| **Config file** | none — no test runner config |
| **Quick run command** | `grep -c "##" doc-writer/skills/upgrade/SKILL.md` (verify structure sections present) |
| **Full suite command** | `grep -cE "^### Step" doc-writer/skills/upgrade/SKILL.md` (verify all steps present) |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run quick run command to verify file integrity
- **After every plan wave:** Run full suite command to verify structure
- **Before `/gsd:verify-work`:** Full manual UAT walkthrough required
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 01 | 1 | MERGE-01 | manual | `grep "section-level" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |
| 20-01-02 | 01 | 1 | MERGE-02 | manual | `grep "rules.md" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |
| 20-01-03 | 01 | 1 | MERGE-03 | manual | `grep "AskUserQuestion" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |
| 20-01-04 | 01 | 1 | MERGE-04 | manual | `grep "pre-v1.5.0\|2-way\|bootstrap" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements — this phase modifies a single SKILL.md file. No test framework needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Non-conflicting upstream changes auto-applied to customized guidance file | MERGE-01 | Requires running skill with customized doc_system.md, modified plugin defaults, and .originals/ baseline | Customize a section in .doc-writer/{doc_system}.md, update plugin default with changes in a different section, run `/doc-writer:upgrade` |
| Project-specific rules preserved during rules.md merge | MERGE-02 | Requires running skill with customized rules.md | Add custom rules to .doc-writer/rules.md, update plugin defaults/rules.md with new default rules, run upgrade |
| Conflicts presented one at a time via AskUserQuestion | MERGE-03 | Requires running skill where same section modified in both user and plugin | Modify same `##` section in both user file and plugin default, run upgrade, verify AskUserQuestion appears |
| Pre-v1.5.0 2-way diff with .originals/ bootstrapping | MERGE-04 | Requires running skill without .originals/ directory | Remove .doc-writer/.originals/, run `/doc-writer:upgrade`, verify per-change accept/reject flow and .originals/ creation |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
