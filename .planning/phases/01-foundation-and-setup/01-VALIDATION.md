---
phase: 1
slug: foundation-and-setup
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-03
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual CC session testing (no automated test framework) |
| **Config file** | None — this is a markdown-file plugin with no executable code |
| **Quick run command** | `claude --plugin-dir ./doc-writer-plugin` then invoke `/doc-writer:setup` |
| **Full suite command** | Manual: run setup on a sample project, verify config output, verify re-run behavior |
| **Estimated runtime** | ~60 seconds (manual session) |

---

## Sampling Rate

- **After every task commit:** Manual: load plugin with `claude --plugin-dir`, run `/doc-writer:setup` on a test project
- **After every plan wave:** Manual: full setup flow on fresh project + re-run flow on existing project
- **Before `/gsd:verify-work`:** All 5 SETUP requirements verified via manual CC session
- **Max feedback latency:** ~60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | SETUP-01 | manual (CC session) | `claude --plugin-dir ./doc-writer-plugin` then `/doc-writer:setup` | N/A — markdown plugin | ⬜ pending |
| 1-01-02 | 01 | 1 | SETUP-02 | manual (inspect files) | Read `skills/quality-rules/SKILL.md` after setup | N/A | ⬜ pending |
| 1-01-03 | 01 | 1 | SETUP-03 | manual (inspect files) | Verify guidance file exists in `.doc-writer/` after setup | N/A | ⬜ pending |
| 1-01-04 | 01 | 1 | SETUP-04 | manual (edit + re-read) | Edit `.doc-writer/rules.md`, verify agent reads updated content | N/A | ⬜ pending |
| 1-01-05 | 01 | 1 | SETUP-05 | manual (multi-audience setup) | Run setup, add 2+ audiences, verify `config.yaml` has array | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Create a sample test project directory with `mkdocs.yml` for testing auto-detection
- [ ] Create a sample test project directory with `package.json` + `tsconfig.json` for testing TypeScript detection
- [ ] Create a sample test project directory with no doc system for testing plain-markdown default

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/doc:setup` creates config with audience data | SETUP-01 | Requires interactive CC session with Q&A prompts | Load plugin, run `/doc-writer:setup`, verify `.doc-writer/config.yaml` output |
| Re-running setup updates rather than overwrites | SETUP-01 | Requires two sequential CC sessions | Run setup twice, verify second run preserves first run's data |
| Universal rules in skill, project rules in `.doc-writer/rules.md` | SETUP-02 | Requires inspecting file contents after setup | Check skill file exists, check `.doc-writer/rules.md` created |
| Guidance files copied to `.doc-writer/` | SETUP-03 | Requires inspecting file system after setup | Verify doc-system guidance file in `.doc-writer/` |
| Custom rules are freeform and additive | SETUP-04 | Requires manual edit + re-read cycle | Edit `.doc-writer/rules.md`, verify agent reads updated content |
| Audiences array supports multiple entries | SETUP-05 | Requires multi-step interactive setup | Run setup with 2+ audiences, verify config array structure |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
