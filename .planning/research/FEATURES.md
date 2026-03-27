# Feature Landscape: Plugin Upgrade Helpers

**Domain:** Claude Code plugin upgrade system for doc-writer
**Researched:** 2026-03-26

## Table Stakes

Features users expect in a plugin upgrade system. Missing = broken upgrade experience.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Version detection | User runs `/doc-writer:upgrade`, system detects if upgrade is needed | Low | Compare plugin.json version vs config.yaml `plugin_version` |
| Guidance file merge | User customized {framework}.md; upgrade adds new sections without destroying customizations | Medium | diff3 3-way merge: original + user-modified + new-plugin-version |
| Rules file merge | User added project rules; upgrade adds new default content without destroying additions | Medium | Same diff3 approach as guidance files |
| Config field additions | New config template has new fields; add them to user's config with defaults | Low | Claude reads both templates, adds missing fields to user config |
| No-op on clean | If user made no customizations AND plugin has no changes for a file, skip it silently | Low | Compare original vs user copy; if identical, just overwrite with new |
| Conflict presentation | When diff3 produces conflicts, show them clearly to user for resolution | Medium | Parse conflict markers, present each via AskUserQuestion |
| Originals storage at setup | Setup skill stores copies of shipped files as merge base for future upgrades | Low | File copy to `.doc-writer/.originals/` |

## Differentiators

Features that make the upgrade experience notably better than competitors.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Q&A gap detection | Only ask NEW framework questions added since last setup; do not re-ask answered ones | Medium | Compare .qa.md question headers against stored manifest |
| Smart conflict resolution | Claude interprets diff3 conflicts and suggests resolution based on understanding of what changed | Medium | Claude reads conflict markers + knows guidance file purpose |
| Researcher re-run on config changes | After config migration adds new fields, re-run researcher to update context.md | Low | Already have `--refresh-context` flow; trigger after upgrade |
| Deprecation warnings | Warn user when config fields or guidance sections are deprecated in new version | Low | Claude reads both templates and identifies removed fields |
| Dry-run mode | Show what upgrade would change without applying anything | Low | Run diff3 and schema comparison, display results, stop |
| First-time upgrade (no originals) | Handle projects set up before v1.5.0 that have no `.originals/` directory | Medium | Fall back to 2-way diff; present all plugin changes for user review |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Automatic conflict resolution | Could silently drop user customizations; trust violation | Always present conflicts for user decision |
| Migration scripts per version | Creates combinatorial explosion (1.4->1.5, 1.4->1.6, 1.5->1.6, etc.) | Template-based comparison: always compare current originals vs current plugin defaults |
| Config.yaml 3-way merge via diff3 | Config is structured data, not prose; line-based merge could corrupt YAML structure | Claude-as-reader for structured comparison and field-by-field migration |
| Backup before upgrade | Adds complexity; user has git for this | Inform user "your files are in git; commit before upgrading if you want a rollback point" |
| Plugin auto-update | Out of scope; Claude Code handles plugin distribution | Only handle the project-side migration after plugin files have been updated |
| Undo/rollback | Complex state management for questionable value | User has git; document the "undo" as `git checkout .doc-writer/` |
| Interactive merge editor | Not available in Claude Code's tool set; would need external tool | Claude presents conflicts one at a time via AskUserQuestion |

## Feature Dependencies

```
Originals Storage (setup-time) --> Version Detection --> Guidance Merge
                                                    --> Rules Merge
                                                    --> Config Migration
                                                    --> Q&A Gap Detection

Guidance Merge --> Conflict Presentation --> User Resolution
Rules Merge    --> Conflict Presentation --> User Resolution

Config Migration --> Researcher Re-run
Q&A Gap Detection --> Researcher Re-run
```

**Critical dependency:** Originals storage must be added to the setup skill BEFORE any upgrade logic is useful. Without originals, diff3 has no base to merge against.

## MVP Recommendation

Prioritize:
1. **Originals storage at setup time** -- prerequisite for everything else; backward-compatible (setup just copies extra files)
2. **Version detection** -- the trigger for the whole upgrade flow
3. **Guidance/rules 3-way merge** -- the primary user value (preserving customizations)
4. **Config field additions** -- simple Claude-as-reader comparison
5. **Q&A gap detection** -- asks only new questions, avoids re-setup fatigue

Defer:
- **Dry-run mode**: Nice but not essential for v1.5.0; user can review changes as they are presented
- **Smart conflict resolution suggestions**: Can be added after basic conflict presentation works

## Sources

- Existing doc-writer setup skill (SKILL.md) -- defines file copy patterns and Q&A flow
- PROJECT.md v1.5.0 target features -- defines scope
- Practical testing of diff3 merge behavior with guidance-style markdown content
