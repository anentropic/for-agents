# Phase 19: Upgrade Skill - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Create a new `/doc-writer:upgrade` command (`doc-writer/skills/upgrade/SKILL.md`) that: detects version mismatches between the installed plugin and the user's config, migrates new config fields with semantically inferred values, silently updates unmodified guidance/rules files to the new plugin version, removes deprecated config fields, and reports all changes in a summary. Three-way merge for customized files (Phase 20), Q&A gap detection (Phase 21), and researcher re-run (Phase 21) are explicitly out of scope.

</domain>

<decisions>
## Implementation Decisions

### Skill structure
- **D-01:** New file `doc-writer/skills/upgrade/SKILL.md` — separate skill, not an extension of setup SKILL.md (settled in Phase 18 architecture research)
- **D-02:** Bump `plugin.json` version from `1.4.0` to `1.5.0` as part of this phase — required for UPGRADE-01 to be testable (fresh-setup projects will be at 1.5.0; older projects will show a mismatch)
- **D-03:** Phase 19 delivers a minimal complete command covering Steps 1, 2, and 6 of the full upgrade flow. No placeholder/stub steps for Phase 20/21 work — the command stops after what's implemented.

### Config migration UX (UPGRADE-02)
- **D-04:** Infer new config field values silently when confident (single obvious source field, unambiguous mapping). Write the inference and note it in the summary.
- **D-05:** Pause and ask the user via `AskUserQuestion` whenever any ambiguity exists — i.e., when more than one interpretation seems plausible, even if Claude could pick one. Don't guess when uncertain.
- **D-06:** When asking about an ambiguous field, use `AskUserQuestion` with the field's valid values as options — same pattern as setup Q&A, not a plain text question.
- **D-07:** After all migration changes, display a consolidated summary of every field added (with inferred value noted) and every field removed.

### Deprecation handling (UPGRADE-04)
- **D-08:** Phase 19's UPGRADE-04 scope is limited to **config fields only** — fields present in `config.yaml` that are absent from the new `config-template.yaml`. Guidance file section removals are a Phase 20 concern (handled by 3-way merge logic where customization context is available).
- **D-09:** Auto-remove deprecated config fields without prompting. List removed fields in the upgrade summary. User can restore via git if needed.

### Unchanged-file update (UPGRADE-03)
- **D-10:** For each file in `.originals/` — compare user's `.doc-writer/{file}` to `.originals/{file}`. If identical (user made no customizations), silently overwrite with the new plugin defaults. Note in summary.
- **D-11:** If user's file differs from `.originals/` (customized), skip it in Phase 19 — Phase 20 handles 3-way merge. Inform user in summary: "Customized files skipped — merge coming in a future upgrade."

### Claude's Discretion
- Exact wording and formatting of the upgrade summary output
- How to structure the "already up to date" message (UPGRADE-01 fast path)
- How to handle edge case: `.originals/` is absent (pre-v1.5.0 project with no Phase 18 setup) — acceptable to warn and skip file-update steps

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Upgrade skill design
- `.planning/research/ARCHITECTURE.md` §"Question 3: Upgrade Skill Structure" — settled decision: separate skill, skill metadata, full 6-step upgrade flow design, integration with existing skills table
- `.planning/research/ARCHITECTURE.md` §"Question 1: Plugin Version Tracking" — plugin_version field format, pre-1.5.0 handling rules

### Requirements
- `.planning/REQUIREMENTS.md` — UPGRADE-01 through UPGRADE-04 acceptance criteria (with Phase 19 scope clarification: UPGRADE-04 = config fields only)

### Existing skill patterns (for consistency)
- `doc-writer/skills/setup/SKILL.md` — reference for skill structure, AskUserQuestion usage, `${CLAUDE_PLUGIN_ROOT}` path conventions, config.yaml read/write patterns
- `doc-writer/skills/setup/defaults/config-template.yaml` — canonical schema; new fields present here but absent from user's config.yaml are the migration targets

### Phase 18 output (what Phase 19 depends on)
- `.planning/phases/18-setup-foundation/18-VERIFICATION.md` — confirms plugin_version, .originals/, and qa_answers are written by setup; Phase 19 depends on these existing

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `doc-writer/skills/setup/SKILL.md`: Canonical example for skill structure, frontmatter, AskUserQuestion patterns, `${CLAUDE_PLUGIN_ROOT}` usage — upgrade SKILL.md should follow the same conventions
- `doc-writer/skills/setup/defaults/config-template.yaml`: The "THEIRS" schema for config migration — diff this against user's config.yaml to find new and removed fields

### Established Patterns
- All skills use `disable-model-invocation: true` with explicit `allowed-tools`
- Config is read/written by Claude directly (YAML parsing, not bash tools) — upgrade migration follows the same approach
- File copies use `${CLAUDE_PLUGIN_ROOT}` for plugin-side paths and relative paths for project-side paths

### Integration Points
- `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` → version source (THEIRS version)
- `.doc-writer/config.yaml` → current state (plugin_version field = OURS version)
- `.doc-writer/.originals/{file}` → merge base for UPGRADE-03 file comparison
- `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{file}` → new plugin defaults (THEIRS for file comparison)

</code_context>

<specifics>
## Specific Ideas

- Deprecation question clarified during discussion: guidance file section removals are NOT Phase 19 deprecation warnings — they're Phase 20 merge-with-deletion. Phase 19 only warns on config field removals.
- The "infer + confirm if uncertain" config migration UX: threshold is "any ambiguity at all" — if multiple interpretations are plausible, ask rather than guess.

</specifics>

<deferred>
## Deferred Ideas

- Phase 19/20/21 stub steps in SKILL.md — not needed; command delivers minimal complete slice, Phase 20/21 extend it naturally
- Guidance file section deprecation warnings — belongs in Phase 20's merge logic
- `--dry-run` flag — mentioned in ARCHITECTURE.md skill metadata but not scoped to Phase 19

</deferred>

---

*Phase: 19-upgrade-skill*
*Context gathered: 2026-03-26*
