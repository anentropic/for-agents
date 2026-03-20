---
phase: 11
slug: sphinx-shibuya-doc-framework-support-with-top-tabs-3-level-nav-sphinx-design-and-sphinx-autoapi-extensions
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-18
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — prompt/markdown changes only; manual validation via Claude Code |
| **Config file** | none |
| **Quick run command** | `ls doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md doc-writer/skills/setup/defaults/sphinx-shibuya.md doc-writer/skills/setup/defaults/scaffolds/conf.py` |
| **Full suite command** | Manual: run `/doc-writer:setup` selecting sphinx-shibuya in a test project |
| **Estimated runtime** | ~3 minutes (manual) |

> **Note:** This phase modifies only prompt/markdown files (guidance file, Q&A data, scaffold template, skill update). There is no executable code to unit-test. Validation is intentionally manual: grep commands confirm structural presence, and live `/doc-writer:setup` runs confirm behavioral correctness. This manual-only approach has been reviewed and accepted.

---

## Sampling Rate

- **After every task commit:** Verify modified/created files exist and contain expected patterns via grep
- **After every plan wave:** Manual spot-check comparing new files to mkdocs-material equivalents
- **Before `/gsd:verify-work`:** Full manual walkthrough of sphinx-shibuya setup flow
- **Max feedback latency:** N/A (prompt changes; no automated test suite)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-xx-01 | 01 | 1 | Q&A data file created | manual | `ls doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md` | ❌ W0 | ⬜ pending |
| 11-xx-02 | 01 | 1 | Q&A has Detection section | manual | `grep -n "Config file: conf.py" doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md` | ❌ W0 | ⬜ pending |
| 11-xx-03 | 01 | 1 | Q&A has 3 questions | manual | `grep -c "^## Q" doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md` | ❌ W0 | ⬜ pending |
| 11-xx-04 | 02 | 1 | Guidance file created | manual | `ls doc-writer/skills/setup/defaults/sphinx-shibuya.md` | ❌ W0 | ⬜ pending |
| 11-xx-05 | 02 | 1 | Guidance covers Admonitions | manual | `grep -n "## Admonitions" doc-writer/skills/setup/defaults/sphinx-shibuya.md` | ❌ W0 | ⬜ pending |
| 11-xx-06 | 02 | 1 | Guidance covers Navigation | manual | `grep -n "## Navigation" doc-writer/skills/setup/defaults/sphinx-shibuya.md` | ❌ W0 | ⬜ pending |
| 11-xx-07 | 03 | 2 | conf.py scaffold created | manual | `ls doc-writer/skills/setup/defaults/scaffolds/conf.py` | ❌ W0 | ⬜ pending |
| 11-xx-08 | 03 | 2 | Scaffold has template vars | manual | `grep -n "{project_name}" doc-writer/skills/setup/defaults/scaffolds/conf.py` | ❌ W0 | ⬜ pending |
| 11-xx-09 | 04 | 2 | Setup skill lists sphinx-shibuya | manual | `grep -n "sphinx-shibuya" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |
| 11-xx-10 | 04 | 2 | Setup skill detects conf.py | manual | `grep -n "conf.py" doc-writer/skills/setup/SKILL.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md` — Q&A data file for sphinx-shibuya (created in Plan 01)
- [ ] `doc-writer/skills/setup/defaults/sphinx-shibuya.md` — Guidance file (created in Plan 02)
- [ ] `doc-writer/skills/setup/defaults/scaffolds/conf.py` — conf.py scaffold template (created in Plan 03)

*No automated test framework — all changes are prompt/markdown files validated via grep and manual runs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Top tabs wired via nav_links | Scaffold conf.py produces correct Shibuya nav | Requires live Sphinx build | Run `/doc-writer:setup` in sphinx project; verify nav_links in conf.py point to Diataxis section indexes |
| autoapi replaces Reference tab | Author agent skips manual reference pages | Requires live agent run | Run `/doc-writer:setup` with autoapi selected; verify Author agent guidance shows Reference tab as autoapi-owned |
| sphinx-design components guidance | Agent pro-actively suggests grid/tabs/dropdowns | Requires live agent run | Run `/doc-writer:write`; verify agent suggests sphinx-design components for landing pages and code examples |
| Q&A detect_context pre-selects | nav_links/autoapi/sphinx_design detected from conf.py | Requires live setup run | Run `/doc-writer:setup` in project with conf.py already configured; verify Q&A pre-selects detected options |
| scaffold structure complete | index.rst + 4 section dirs with stub index.rst | Requires live setup run | Run `/doc-writer:setup` with sphinx-shibuya in unconfigured project; verify full docs/ tree created |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s (manual)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** accepted (manual-only validation — intentional for prompt/markdown-only phase)
