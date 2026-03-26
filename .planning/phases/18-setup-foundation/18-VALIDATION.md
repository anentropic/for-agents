---
phase: 18
slug: setup-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — skill files are markdown instructions, not executable code |
| **Config file** | none |
| **Quick run command** | manual inspection of written files |
| **Full suite command** | manual end-to-end setup run verification |
| **Estimated runtime** | N/A — manual verification |

---

## Sampling Rate

- **After every task commit:** Inspect written file contents for expected fields/sections
- **After every plan wave:** Full file read verification of all modified files
- **Before `/gsd:verify-work`:** All files must contain expected content
- **Max feedback latency:** N/A — manual

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | SETUP-01 | manual | `grep "plugin_version" doc-writer/skills/setup/defaults/config-template.yaml` | ✅ | ⬜ pending |
| 18-01-02 | 01 | 1 | SETUP-02 | manual | `grep "originals" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 18-01-03 | 01 | 1 | SETUP-04 | manual | `grep "originals" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 18-02-01 | 02 | 1 | SETUP-03 | manual | `grep "qa_answers" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 18-02-02 | 02 | 1 | SETUP-03 | manual | `grep "qa_answers" doc-writer/skills/setup/defaults/config-template.yaml` | ✅ | ⬜ pending |
| 18-02-03 | 02 | 2 | SETUP-03 | manual | `grep "qa_answers" doc-writer/agents/doc-author.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*None — no test framework required. All verification is manual file inspection using grep.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| plugin_version written to config.yaml at setup time | SETUP-01 | Claude agent behavior, not executable code | Run `/doc-writer:setup` on a test project; check `.doc-writer/config.yaml` contains `plugin_version: "1.4.0"` |
| .originals/ created with pristine copies | SETUP-02 | Claude agent behavior | Run `/doc-writer:setup`; check `.doc-writer/.originals/` contains `{doc_system}.md` and `rules.md` |
| qa_answers written to config.yaml | SETUP-03 | Claude agent behavior | Run `/doc-writer:setup`; check `.doc-writer/config.yaml` has `qa_answers:` section with framework-specific keys |
| --reset refreshes .originals/ | SETUP-04 | Claude agent behavior | Run `/doc-writer:setup --reset`; check `.originals/` reflects current plugin files |
| odoc doc-author reads from qa_answers | SETUP-03 | Claude agent behavior | Run `/doc-writer:write` on an odoc project; verify .mli enrichment behavior matches `qa_answers.scope` value |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < N/A
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
