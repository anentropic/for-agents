---
phase: 9
slug: enhanced-setup-q-a-tone-user-persona-and-new-planner-researcher-agents
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — prompt/markdown changes only; manual validation via Claude Code |
| **Config file** | none |
| **Quick run command** | `cat .doc-writer/context.md` (verify file exists and has content) |
| **Full suite command** | Manual: run `/doc-writer:setup` in a test project and verify output |
| **Estimated runtime** | ~2 minutes (manual) |

---

## Sampling Rate

- **After every task commit:** Verify modified files exist and contain expected patterns
- **After every plan wave:** Manual run of `/doc-writer:setup` in a test project
- **Before `/gsd:verify-work`:** Full manual walkthrough of setup flow
- **Max feedback latency:** N/A (prompt changes, no automated test suite)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 9-xx-01 | 01 | 1 | Setup Q&A infer+suggest | manual | `grep -n "AskUserQuestion" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 9-xx-02 | 01 | 1 | Tone selection | manual | `grep -n "tone" doc-writer/skills/setup/defaults/config-template.yaml` | ✅ | ⬜ pending |
| 9-xx-03 | 01 | 1 | User persona tasks | manual | `grep -n "user_tasks" doc-writer/skills/setup/defaults/config-template.yaml` | ✅ | ⬜ pending |
| 9-xx-04 | 01 | 1 | Framework Q&A | manual | `grep -n "mkdocs-material" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 9-xx-05 | 02 | 2 | Researcher agent | manual | `ls doc-writer/agents/doc-researcher.md` | ❌ W0 | ⬜ pending |
| 9-xx-06 | 02 | 2 | context.md generation | manual | `cat .doc-writer/context.md` | ❌ W0 | ⬜ pending |
| 9-xx-07 | 03 | 3 | Agent context.md consumption | manual | `grep -n "context.md" doc-writer/agents/doc-author.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `doc-writer/agents/doc-researcher.md` — new researcher agent file (created in Wave 2)

*No test framework needed — all changes are prompt/markdown files validated via grep and manual runs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| AskUserQuestion infer+suggest for audience fields | Setup Q&A pattern | Requires interactive Claude Code session | Run `/doc-writer:setup` in a test project; verify each audience field shows 2-4 inferred suggestions with Recommended marker |
| Tone selection Q&A | Tone field | Requires interactive session | Verify 3 tone options appear with one-line descriptions |
| User persona task selection | Persona tasks | Requires interactive session | Verify 3-5 inferred tasks shown as multiSelect after assumed knowledge Q&A |
| Framework Q&A (mkdocs-material) | Framework question set | Requires interactive session | Select mkdocs-material in setup; verify 3 framework-specific questions appear |
| Framework Q&A (plain-markdown) | Framework question set | Requires interactive session | Select plain-markdown in setup; verify 2-3 questions appear |
| context.md generation | Researcher agent | Requires full setup run | After setup completes, verify `.doc-writer/context.md` exists with audience, tone, and project sections |
| --refresh-context flag | Re-run flow | Requires interactive session | Run `/doc-writer:setup --refresh-context`; verify Q&A is skipped, researcher reruns, context.md updated |
| Downstream agent reads context.md | Agent integration | Requires agent run | Run doc-author agent; verify it reads context.md gracefully (no error if missing) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s (manual)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
