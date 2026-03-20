# Phase 1: Foundation and Setup - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Config system, skill files, and plugin file structure — the prerequisite everything else depends on. Project authors can configure the plugin for their project via `/doc:setup` and everything agents need to function is in place. Writing, reviewing, and persona validation are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Config format and location
- Config lives in `.doc-writer/config.yaml` in the target project root (YAML format)
- `.doc-writer/` directory is committed to git — shared across team members
- `.doc-writer/` also contains guidance files and rules file (see below)

### Setup Q&A experience
- `/doc:setup` uses structured prompts with specific fields: audience name, skill level, assumed knowledge, never-assume list
- Multi-audience: start with primary audience, then offer "Do you have a secondary audience?" — repeat for additional audiences
- Auto-detection: scan project for doc system (mkdocs.yml, docusaurus.config.js, etc.), source language, existing docs; present findings for user to confirm or override
- Re-run behavior: show current config, offer to edit specific fields (not full re-run of Q&A)

### Doc-system guidance
- v1 ships two guidance files: mkdocs-material and plain markdown
- Guidance files are about opinionated preferences for feature usage (e.g., "prefer admonition blocks over bold text for warnings"), not syntax reference — agents already understand doc-system syntax
- During setup, selected guidance file is copied to `.doc-writer/` — user can edit it per-project
- Users can add entirely new doc-system guidance files to `.doc-writer/` and they are auto-detected at runtime
- Active doc system is a project preference stored in config.yaml
- Guidance files are extensible: user creates e.g. `.doc-writer/vitepress.md` and it becomes a selectable option

### Custom rules
- Universal quality rules (no internal details, code examples required, consistent structure, inline code cross-referencing) are baked into agent prompts — non-overridable
- A default rules file ships with the plugin and is copied to `.doc-writer/rules.md` during setup
- The rules file is additive — project-specific rules that extend (not override) universal rules
- Rules are written as freeform markdown — natural language rules that agents interpret

### Claude's Discretion
- Config YAML schema structure (field names, nesting)
- Guidance file internal format and naming convention
- Plugin file structure (agents/, commands/, skills/ layout)
- How auto-detection scans work internally
- Default rules file content and format

</decisions>

<specifics>
## Specific Ideas

- Follow GSD's pattern: `.doc-writer/` directory mirrors `.planning/` as a project-local config directory
- Guidance files are a "copy and customize" model — plugin ships templates, project gets its own editable copy
- Same pattern for rules: ship defaults, copy to project, user edits

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- No source code exists yet — greenfield project

### Established Patterns
- GSD system provides the reference pattern: `.planning/config.json` for project config, `~/.claude/agents/*.md` for agent files, `~/.claude/commands/*.md` for slash commands
- CC agent file format: YAML frontmatter (name, description) + markdown body (confirmed HIGH confidence from GSD inspection)
- CC Task tool for multi-agent coordination (confirmed HIGH confidence)

### Integration Points
- Plugin installs to `~/.claude/` (agents, commands) for global availability
- Per-project config at `{project_root}/.doc-writer/`
- Agents reference skill files via `@` includes in their prompts

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-and-setup*
*Context gathered: 2026-03-03*
