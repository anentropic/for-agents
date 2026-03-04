---
phase: 1
slug: foundation-and-setup
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-03
validated: 2026-03-04
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | BATS (Bash Automated Testing System) v1.8.2 |
| **Config file** | None — tests use direct file assertions |
| **Quick run command** | `bats tests/phase-01-validation.bats` |
| **Full suite command** | `bats tests/phase-01-validation.bats` |
| **Estimated runtime** | < 2 seconds (42 file-system assertions) |

---

## Sampling Rate

- **After every task commit:** Run `bats tests/phase-01-validation.bats` (~2s)
- **After every plan wave:** Full suite + manual CC session for interactive behaviors
- **Before `/gsd:verify-work`:** All 5 SETUP requirements covered by automated suite + manual items documented below
- **Max feedback latency:** ~2 seconds (automated); ~60 seconds (manual CC session)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File | Status |
|---------|------|------|-------------|-----------|-------------------|------|--------|
| 1-01-01 | 01 | 1 | SETUP-01 | integration | `bats tests/phase-01-validation.bats` | `tests/phase-01-validation.bats` | ✅ green |
| 1-01-02 | 01 | 1 | SETUP-02 | integration | `bats tests/phase-01-validation.bats` | `tests/phase-01-validation.bats` | ✅ green |
| 1-01-03 | 01 | 1 | SETUP-03 | integration | `bats tests/phase-01-validation.bats` | `tests/phase-01-validation.bats` | ✅ green |
| 1-01-04 | 01 | 1 | SETUP-04 | integration | `bats tests/phase-01-validation.bats` | `tests/phase-01-validation.bats` | ✅ green |
| 1-01-05 | 01 | 1 | SETUP-05 | integration | `bats tests/phase-01-validation.bats` | `tests/phase-01-validation.bats` | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Test Coverage by Requirement

### SETUP-01 (12 tests)
| Test | Assertion |
|------|-----------|
| setup SKILL.md exists | File at `skills/setup/SKILL.md` |
| config-template.yaml exists | File at `skills/setup/defaults/config-template.yaml` |
| config-template has audiences as array | `audiences:` key present in config-template |
| config-template has skill_level field | `skill_level` in config-template |
| config-template has assumed_knowledge field | `assumed_knowledge` in config-template |
| config-template has never_assume field | `never_assume` in config-template |
| setup SKILL.md asks for audience name | name field mentioned in Q&A flow |
| setup SKILL.md includes skill_level question | skill_level keyword in SKILL.md |
| setup SKILL.md includes assumed_knowledge question | assumed_knowledge keyword in SKILL.md |
| setup SKILL.md includes never_assume question | never_assume keyword in SKILL.md |
| setup SKILL.md has re-run detection logic | config.yaml / re-run keywords in SKILL.md |
| setup SKILL.md instructs single audience as array | "array" / "single-element" keyword in SKILL.md |

### SETUP-02 (12 tests)
| Test | Assertion |
|------|-----------|
| quality-rules SKILL.md exists | File at `skills/quality-rules/SKILL.md` |
| quality-rules has user-invocable: false | Frontmatter value verified |
| quality-rules contains exactly 5 rules | Exactly 5 `## Rule ` headings |
| quality-rules has Rule 1 | "No Internal Details" present |
| quality-rules has Rule 2 | "Working Code Examples" present |
| quality-rules has Rule 3 | "Consistent Structure" present |
| quality-rules has Rule 4 | "Cross-Reference" present |
| quality-rules has Rule 5 | "Audience-Calibrated" present |
| rules.md exists | File at `skills/setup/defaults/rules.md` |
| rules.md describes additive relationship | "additive" / "extend" keyword present |
| doc-author references quality-rules | skill reference in agent frontmatter |
| doc-editor references quality-rules | skill reference in agent frontmatter |

### SETUP-03 (8 tests)
| Test | Assertion |
|------|-----------|
| mkdocs-material.md exists | File at `skills/setup/defaults/mkdocs-material.md` |
| plain-markdown.md exists | File at `skills/setup/defaults/plain-markdown.md` |
| mkdocs-material mentions admonition preferences | "admonition" keyword present |
| plain-markdown mentions markdown conventions | ATX/heading/fenced keyword present |
| guidance files separate from quality-rules | quality-rules SKILL.md has no "admonition"/"mkdocs" content |
| quality-rules has no doc-system-specific syntax | No "mkdocs"/"docusaurus"/"vitepress"/"sphinx" in quality-rules |
| setup SKILL.md instructs copying guidance file | guidance / {doc_system}.md / defaults/ mentioned |
| setup SKILL.md references CLAUDE_PLUGIN_ROOT | CLAUDE_PLUGIN_ROOT keyword present |

### SETUP-04 (5 tests)
| Test | Assertion |
|------|-----------|
| rules.md is freeform markdown (not YAML) | First line is not `---` |
| rules.md contains commented-out examples | HTML comment markers present |
| rules.md explains natural language interpretation | "natural language" / "interpret" present |
| setup SKILL.md instructs copying rules.md | rules.md reference in SKILL.md |
| setup SKILL.md uses CLAUDE_PLUGIN_ROOT for rules path | CLAUDE_PLUGIN_ROOT in defaults/rules context |

### SETUP-05 (5 tests)
| Test | Assertion |
|------|-----------|
| config-template audiences is YAML array with dash entry | `  - name:` entry present |
| setup SKILL.md asks about secondary audience | "secondary audience" keyword present |
| setup SKILL.md has loop logic for multiple audiences | "continue" / "repeat" / "additional" keyword present |
| doc-persona reads audiences from config | "audiences" / "config.yaml" referenced in agent |
| config-template uses plural audiences key | No top-level `audience:` (singular) key |

---

## Wave 0 Requirements

Wave 0 is satisfied by the BATS test suite — all automatable structural assertions are covered without sample project fixtures.

Sample project fixtures (mkdocs.yml, package.json+tsconfig.json, no-doc-system) are only needed for testing the detect-project.sh script interactively. The script passes `bash -n` syntax check (verified in VERIFICATION.md) and its output format is validated structurally. Full functional testing of the detection script against sample projects is a manual verification item.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/doc:setup` creates config with audience data | SETUP-01 | Requires interactive CC session with Q&A prompts | Load plugin, run `/doc-writer:setup`, verify `.doc-writer/config.yaml` output |
| Re-running setup updates rather than overwrites | SETUP-01 | Requires two sequential CC sessions | Run setup twice, verify second run preserves first run's data |
| Agent loads universal rules at runtime | SETUP-02 | Requires active Claude agent execution | Invoke doc-author, verify quality-rules skill is loaded |
| Guidance files copied to `.doc-writer/` during setup | SETUP-03 | Requires running `/doc-writer:setup` in a CC session | Run setup, verify `{doc_system}.md` appears in `.doc-writer/` |
| Agent reads correct guidance file at runtime | SETUP-03 | Requires active Claude agent execution | Invoke doc-author, verify it reads `.doc-writer/{doc_system}.md` |
| Agent interprets custom rules from rules.md | SETUP-04 | Requires manual edit + agent execution | Edit `.doc-writer/rules.md`, run agent, verify rule is applied |
| Multi-audience interactive Q&A flow | SETUP-05 | Requires interactive CC session | Run setup with 2+ audiences, verify config array has multiple entries |
| Persona instantiation per audience | SETUP-05 | Requires running doc-persona agent | Invoke doc-persona with each audience, verify correct calibration |

---

## Validation Sign-Off

- [x] All tasks have automated verify command
- [x] Sampling continuity: all tasks covered by single fast suite
- [x] Wave 0 satisfied by BATS suite
- [x] No watch-mode flags
- [x] Feedback latency < 60s (suite runs in < 2s)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-03-04 by gsd-nyquist-auditor
