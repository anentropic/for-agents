---
phase: 10
slug: framework-scaffolding-and-unknown-framework-research-guidance-generation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-17
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — prompt/markdown changes only; manual validation via Claude Code |
| **Config file** | none |
| **Quick run command** | `ls doc-writer/skills/setup/defaults/scaffolds/` (verify scaffold templates exist) |
| **Full suite command** | Manual: run `/doc-writer:setup` selecting mkdocs-material in a test project |
| **Estimated runtime** | ~3 minutes (manual) |

> **Note:** This phase modifies only prompt/markdown files (agent definitions, skill instructions, data files). There is no executable code to unit-test. Validation is intentionally manual: grep commands confirm structural presence, and live `/doc-writer:setup` runs confirm behavioral correctness. This manual-only approach has been reviewed and accepted.

---

## Sampling Rate

- **After every task commit:** Verify modified/created files exist and contain expected patterns via grep
- **After every plan wave:** Manual spot-check of setup skill flow in test project
- **Before `/gsd:verify-work`:** Full manual walkthrough of both scaffolding and unknown framework flows
- **Max feedback latency:** N/A (prompt changes; no automated test suite)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-xx-01 | 01 | 1 | Q&A data files extracted | manual | `ls doc-writer/skills/setup/defaults/mkdocs-material.qa.md` | ❌ W0 | ⬜ pending |
| 10-xx-02 | 01 | 1 | Scaffold template created | manual | `ls doc-writer/skills/setup/defaults/scaffolds/mkdocs-material.yml` | ❌ W0 | ⬜ pending |
| 10-xx-03 | 02 | 1 | Unknown framework agent | manual | `grep -n "Mode: Unknown Framework Research" doc-writer/agents/doc-researcher.md` | ✅ | ⬜ pending |
| 10-xx-04 | 02 | 1 | Global write logic | manual | `grep -n "CLAUDE_PLUGIN_ROOT" doc-writer/agents/doc-researcher.md` | ✅ | ⬜ pending |
| 10-xx-05 | 03 | 2 | Setup skill scaffolding | manual | `grep -n "scaffold" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 10-xx-06 | 03 | 2 | Setup skill unknown flow | manual | `grep -n "Research the documentation framework" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `doc-writer/skills/setup/defaults/mkdocs-material.qa.md` — extracted Q&A question set (created in Plan 01)
- [ ] `doc-writer/skills/setup/defaults/scaffolds/mkdocs-material.yml` — scaffold template (created in Plan 01)

*No automated test framework — all changes are prompt/markdown files validated via grep and manual runs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Scaffolding: already configured (diff mode) | Smart scaffold | Requires live setup run | Run `/doc-writer:setup` in project with mkdocs.yml; verify missing extras are surfaced as suggestions |
| Scaffolding: not configured (full mode) | Full scaffold | Requires live setup run | Run `/doc-writer:setup` in project without mkdocs.yml; verify mkdocs.yml generated, docs/ scaffolded, install commands shown |
| Unknown framework: researcher flow | Unknown framework handling | Requires live setup run | Run `/doc-writer:setup`, type unknown framework name; verify researcher spawns, Q&A runs, guidance+qa files written to defaults/ |
| Unknown framework: global write | Global persistence | Requires file inspection | After unknown framework flow, verify `defaults/{name}.md` and `defaults/{name}.qa.md` exist in plugin directory |
| Unknown framework: fallback | Graceful degradation | Requires live run with simulated failure | Verify setup continues with project-local fallback if global write fails |
| Install commands surfaced, not executed | Safety gate | Requires live run | Verify setup shows `pip install mkdocs-material` as informational text, does not auto-execute |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s (manual)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** accepted (manual-only validation — intentional for prompt/markdown-only phase)
