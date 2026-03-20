# Gap Report

**Generated:** 2026-03-16
**Source root:** src/ (not applicable — this is a skills/agents repo; scanned full project)
**Language:** Markdown/YAML (Claude Code plugin ecosystem)
**Total undocumented symbols:** 10 user-facing interfaces

## Undocumented Symbols

### doc-writer plugin (skills)
- `doc-writer:write` (skill/command) — Full documentation pipeline orchestrator
- `doc-writer:setup` (skill/command) — Project configuration wizard
- `doc-writer:edit` (skill/command) — Targeted documentation fixes
- `doc-writer:review` (skill/command) — Audit documentation without generation

### doc-writer plugin (agents — internal but worth documenting for contributors)
- `doc-author` (agent) — Writes documentation drafts
- `doc-editor` (agent) — Runs quality passes on documentation
- `doc-persona` (agent) — Validates documentation as end user

### doc-writer plugin (configuration)
- `.doc-writer/config.yaml` (configuration file) — Project configuration schema
- `.doc-writer/rules.md` (configuration file) — Project-specific quality rules
- `.doc-writer/{doc_system}.md` (configuration file) — Doc system guidance

### copilot-review plugin
- `copilot-review` (skill/command) — Multi-dimensional code review via GitHub Copilot
