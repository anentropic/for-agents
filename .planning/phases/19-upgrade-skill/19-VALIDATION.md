---
phase: 19
slug: upgrade-skill
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual Claude Code skill testing (no compiled test framework — skill is a SKILL.md prompt file) |
| **Config file** | none — no test runner config |
| **Quick run command** | `cat doc-writer/skills/upgrade/SKILL.md | head -5` (verify file exists and has frontmatter) |
| **Full suite command** | `grep -c "##" doc-writer/skills/upgrade/SKILL.md` (verify structure sections present) |
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
| 19-01-01 | 01 | 1 | UPGRADE-01 | manual | `grep "already up to date" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |
| 19-01-02 | 01 | 1 | UPGRADE-02 | manual | `grep "config" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |
| 19-01-03 | 01 | 1 | UPGRADE-03 | manual | `grep ".originals" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |
| 19-01-04 | 01 | 1 | UPGRADE-04 | manual | `grep "deprecat" doc-writer/skills/upgrade/SKILL.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements — this phase creates a single SKILL.md file and updates plugin.json. No test framework needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Up-to-date detection shows correct message | UPGRADE-01 | Requires running skill in Claude Code with matching versions | Run `/doc-writer:upgrade` when plugin_version matches plugin.json version |
| New config fields get semantically inferred values | UPGRADE-02 | Requires running skill after plugin update with new template fields | Update plugin template, run `/doc-writer:upgrade`, check config.yaml for inferred values |
| Unchanged files silently updated | UPGRADE-03 | Requires .originals/ directory and file comparison | Ensure unchanged files match .originals/, run upgrade, verify files updated without prompt |
| Deprecation warnings shown for removed fields | UPGRADE-04 | Requires running skill with config containing deprecated fields | Add deprecated field to config.yaml, run `/doc-writer:upgrade`, verify warning shown |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
