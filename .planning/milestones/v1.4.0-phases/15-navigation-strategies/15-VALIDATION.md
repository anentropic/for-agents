---
phase: 15
slug: navigation-strategies
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bats (existing) + grep verification |
| **Config file** | `tests/` directory |
| **Quick run command** | `grep -c "nav" doc-writer/skills/setup/defaults/sphinx-shibuya.md` |
| **Full suite command** | `bats tests/` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick grep checks on modified files
- **After every plan wave:** Run `bats tests/`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | NAV-03,NAV-04,NAV-05 | grep | `grep -c "nav_links" doc-writer/skills/setup/defaults/sphinx-shibuya.md` | ✅ | ⬜ pending |
| 15-01-02 | 01 | 1 | NAV-06 | grep | `grep -c "navigation.tabs" doc-writer/skills/setup/defaults/mkdocs-material.md` | ✅ | ⬜ pending |
| 15-01-03 | 01 | 1 | NAV-03,NAV-04 | grep | `grep -c "nav_links_config" doc-writer/skills/setup/defaults/scaffolds/sphinx-shibuya.py` | ✅ | ⬜ pending |
| 15-02-01 | 02 | 1 | NAV-01,NAV-02 | grep | `grep -c "nav.*strategy" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 15-02-02 | 02 | 1 | NAV-07,NAV-08 | grep | `grep -c "abstract" doc-writer/agents/doc-author.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test framework or fixtures needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Setup Q&A presents three nav choices with smart recommendation | NAV-01, NAV-02 | Requires running setup flow | Run `/doc-writer:setup` on a test project; verify nav strategy question appears for sphinx-shibuya/mkdocs-material |
| Shibuya dropdown menus render correctly | NAV-03, NAV-04 | Requires building Sphinx docs | Build sphinx docs with sections-as-tabs config; verify dropdowns in browser |
| MkDocs tabs render correctly | NAV-06 | Requires building MkDocs docs | Build mkdocs docs with tabs config; verify tabs in browser |
| Left nav scoped to selected section | NAV-05 | Requires browser interaction | Click a top tab; verify sidebar shows only that section's pages |

*Runtime behaviors verified during `/gsd:verify-work`*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
