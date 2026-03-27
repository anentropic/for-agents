# Phase 19: Upgrade Skill - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 19-upgrade-skill
**Areas discussed:** Config migration UX, Deprecation handling, plugin.json version bump timing

---

## Config migration UX

| Option | Description | Selected |
|--------|-------------|----------|
| Silent + summary at end | Claude infers all new field values without prompting, then shows a summary. | |
| Confirm each inference | For each new field, show inferred value and ask "Does this look right?" | |
| Infer + confirm only if uncertain | Silently apply confident inferences, ask when confidence is low | ✓ |

**User's choice:** Infer + confirm only if uncertain

---

### Follow-up: What makes an inference "uncertain"?

| Option | Description | Selected |
|--------|-------------|----------|
| No source field to infer from | Only pause when no related existing field exists | |
| Low-confidence + constrained type | Pause when inferred value doesn't cleanly match a constrained enum | |
| Any ambiguity at all | Pause whenever more than one interpretation seems plausible | ✓ |

**User's choice:** Any ambiguity at all — if multiple interpretations are plausible, ask rather than guess.

---

### Follow-up: Format for uncertain field prompt

| Option | Description | Selected |
|--------|-------------|----------|
| AskUserQuestion with valid options | Use AskUserQuestion with field's valid values as choices — same as setup Q&A | ✓ |
| Plain text question | Ask in plain text, user types free-form answer | |

**User's choice:** AskUserQuestion with valid options (consistent with setup Q&A pattern)

---

## Deprecation handling

**User clarification (before question was asked):** Auto-removing config fields makes sense, but for guidance files which may have been edited — how does this interact with the 3-way merge?

**Resolution:** Deprecation warnings split across phases:
- Config field deprecations → Phase 19 (self-contained, no merge needed)
- Guidance file section removals → Phase 20 (merge logic handles deletions with customization context)

| Option | Description | Selected |
|--------|-------------|----------|
| Config fields only in Phase 19 | Phase 19 warns on config.yaml field removals; guidance section removals handled by Phase 20 merge | ✓ |
| Warn on both | Phase 19 also warns on guidance section removals (warning only, no merge) | |

**User's choice:** Config fields only in Phase 19

---

### Follow-up: What to do with deprecated config fields

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-remove + note in summary | Remove silently, list in upgrade summary. User restores via git if needed. | ✓ |
| Warn only, don't remove | List in summary but leave in config.yaml. User cleans up manually. | |

**User's choice:** Auto-remove + note in summary

---

## plugin.json version bump timing

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 19 — bump now | Bump to 1.5.0 in Phase 19 plan. Makes UPGRADE-01 immediately testable. | ✓ |
| Milestone completion (Phase 21) | Wait until all v1.5.0 phases are done before bumping. | |

**User's choice:** Phase 19 — bump plugin.json to 1.5.0 now

---

## Claude's Discretion

- Exact wording and formatting of upgrade summary output
- "Already up to date" message format (UPGRADE-01 fast path)
- Pre-v1.5.0 project edge case handling (no .originals/ present)

## Deferred Ideas

- Phase 19/20/21 stub steps — not needed; minimal command approach
- Guidance file section deprecation warnings — Phase 20 merge logic
- `--dry-run` flag — mentioned in ARCHITECTURE.md but not scoped to Phase 19
