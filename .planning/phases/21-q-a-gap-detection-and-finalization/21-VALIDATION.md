---
phase: 21
slug: q-a-gap-detection-and-finalization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-27
---

# Phase 21 — Validation Strategy

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
| 21-01-01 | 01 | 1 | QA-01 | manual | `grep "qa_answers" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |
| 21-01-02 | 01 | 1 | QA-02 | manual | `grep "doc-researcher\|context.md\|Context Enrichment" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements — this phase modifies a single SKILL.md file. No test framework needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Only new Q&A questions asked during upgrade | QA-01 | Requires running skill with stored qa_answers and a .qa.md file containing new questions | Add a new question to .qa.md, run `/doc-writer:upgrade`, verify only the new question is presented |
| context.md refreshed after config/Q&A changes | QA-02 | Requires running skill with config changes or new Q&A answers to trigger researcher re-run | Run upgrade with config field additions, verify context.md is refreshed via researcher |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
