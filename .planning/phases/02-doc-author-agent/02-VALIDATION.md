---
phase: 2
slug: doc-author-agent
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-03
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual CC session testing (no automated test framework) |
| **Config file** | None — this is a markdown-file plugin with no executable code |
| **Quick run command** | `claude --plugin-dir .` then invoke Doc Author via natural language |
| **Full suite command** | Manual: run Doc Author on a sample project, verify all AUTH requirements |
| **Estimated runtime** | ~5 minutes (manual verification) |

---

## Sampling Rate

- **After every task commit:** Manual: load plugin with `claude --plugin-dir .`, run Doc Author on test project
- **After every plan wave:** Manual: full plan-then-write cycle on a sample project, verify all 9 AUTH requirements
- **Before `/gsd:verify-work`:** All 9 AUTH requirements verified via manual CC session
- **Max feedback latency:** ~5 minutes

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | AUTH-01 | manual (CC session) | Run Author on sample project, verify page inventory shows types | N/A | ⬜ pending |
| 02-01-02 | 01 | 1 | AUTH-02 | manual (compare output) | Write 2+ how-to guides, compare section structure | N/A | ⬜ pending |
| 02-01-03 | 01 | 1 | AUTH-03 | manual (search output) | Grep output docs for test utils, CI config, dev scripts | N/A | ⬜ pending |
| 02-01-04 | 01 | 1 | AUTH-04 | manual (inspect output) | Verify mkdocs-material admonitions/tabs or plain-markdown callouts | N/A | ⬜ pending |
| 02-01-05 | 01 | 1 | AUTH-05 | manual (inspect output) | Verify README has: title, badges, description, quick start, features, docs link, license | N/A | ⬜ pending |
| 02-01-06 | 01 | 1 | AUTH-06 | manual (inspect output) | Verify MAINTAINER has: dev setup, tasks, architecture, CI/CD, release, decision log | N/A | ⬜ pending |
| 02-01-07 | 01 | 1 | AUTH-07 | manual (inspect output) | Verify each page has at least one realistic code example, first example is self-contained | N/A | ⬜ pending |
| 02-01-08 | 01 | 1 | AUTH-08 | manual (run blacken-docs) | Run `blacken-docs docs/*.md` on output — should produce no changes | N/A | ⬜ pending |
| 02-01-09 | 01 | 1 | AUTH-09 | manual (read output) | Verify no jargon used without explanation for configured audience | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Create or identify a sample library project for testing Doc Author output (needs: source code, tests, existing docs or README, config via `/doc-writer:setup`)
- [ ] Run `/doc-writer:setup` on the sample project to create `.doc-writer/config.yaml` with audience data
- [ ] Verify that the test project's `.doc-writer/` directory has config, guidance file, and rules file before testing Doc Author

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Classifies pages as tutorial/how-to/reference/explanation | AUTH-01 | LLM classification — no executable assertions | Run Author, verify inventory shows doc types |
| Same-type pages follow same structure | AUTH-02 | Structural comparison requires human judgment | Compare 2+ how-to guides section-by-section |
| No internal details in output | AUTH-03 | Semantic filtering — grep catches obvious leaks only | Search output for test utils, CI config, dev scripts, justfile |
| Uses selected doc-system syntax | AUTH-04 | Syntax correctness requires domain knowledge | Verify admonitions, frontmatter, directives match guidance file |
| README follows template | AUTH-05 | Template adherence is qualitative | Check all required sections present with correct framing |
| MAINTAINER follows template | AUTH-06 | Template adherence is qualitative | Check all required sections present with correct framing |
| Working code examples | AUTH-07 | Code realism requires human evaluation | Verify examples are self-contained and realistic |
| blacken-docs compatible | AUTH-08 | Requires running external tool | Run `blacken-docs docs/*.md` — should produce no changes |
| Vocabulary calibrated to audience | AUTH-09 | Audience calibration is qualitative | Read output for unexplained jargon at configured level |

---

## Validation Sign-Off

- [ ] All tasks have manual verification instructions
- [ ] Sampling continuity: every AUTH requirement has a verification step
- [ ] Wave 0 covers sample project setup for testing
- [ ] No watch-mode flags
- [ ] Feedback latency < 5 minutes
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
