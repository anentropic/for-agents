---
phase: 6
slug: cross-phase-integration-cleanup
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-03-04
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual CC session testing + grep-verify (no executable code in this project) |
| **Config file** | None -- agents are markdown prompts |
| **Quick run command** | `grep -n "three passes" skills/*/SKILL.md` (should return 0 results after INT-01) |
| **Full suite command** | Run all 7 grep-verify commands listed in Per-Task Verification Map |
| **Estimated runtime** | ~5 seconds (grep checks only) |

---

## Sampling Rate

- **After every task commit:** Run the grep-verify command for the specific INT being fixed
- **After every plan wave:** Run all 7 grep-verify commands
- **Before `/gsd:verify-work`:** All grep-verify commands must pass
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | INTG-01 | grep-verify | `grep -c "four passes" skills/write/SKILL.md skills/review/SKILL.md skills/edit/SKILL.md` (expect 4,1,1) | N/A | pending |
| 06-01-02 | 01 | 1 | SETUP-01 | manual | Verify `domain_context` and `discovery_story` prompts in `skills/setup/SKILL.md` Step 2a | N/A | pending |
| 06-01-03 | 01 | 1 | PERS-01, PERS-02 | grep-verify | `grep "audience_name_slug" skills/write/SKILL.md` (expect match) | N/A | pending |
| 06-01-04 | 01 | 1 | INTG-02 | grep-verify | `grep "editor-report.md" skills/write/SKILL.md` (expect match in summary section) | N/A | pending |
| 06-01-05 | 01 | 1 | INTG-03 | grep-verify | `grep "{docs_root}" skills/review/SKILL.md` should return only `{paths.docs_root}` forms | N/A | pending |
| 06-01-06 | 01 | 1 | EDIT-04 | grep-verify | `grep "doc_system\|guidance" agents/doc-editor.md` (expect match in Step 1) | N/A | pending |
| 06-01-07 | 01 | 1 | INTG-01 | grep-verify | `grep "api_reference" skills/setup/defaults/config-template.yaml` (expect match) | N/A | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No test framework, fixtures, or config files need to be created.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Setup Q&A collects domain_context + discovery_story | SETUP-01 | Interactive Q&A flow requires session testing | Run `/doc-writer:setup` and verify new questions appear |
| Full pipeline integration | INTG-01, INTG-02, INTG-03 | End-to-end flow requires CC session | Run `/doc-writer:write`, `/doc-writer:review`, `/doc-writer:edit` in sequence |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
