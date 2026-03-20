# Phase 1: Foundation and Setup - Research

**Researched:** 2026-03-03
**Domain:** Claude Code plugin architecture, config systems, skill/agent file formats
**Confidence:** HIGH — verified against current official CC documentation (code.claude.com/docs/en/skills, /plugins, /sub-agents)

## Summary

Phase 1 builds the foundation that every subsequent phase depends on: the plugin file structure, the `/doc:setup` skill, the per-project `.doc-writer/` config directory, universal quality rule skills, and doc-system guidance files. The entire plugin is composed of markdown files (skills, agents, commands) with no runtime dependencies beyond Claude Code itself.

The CC plugin architecture has matured significantly since the project's initial research. Key updates: (1) **skills have replaced commands** as the recommended format — skills support directories with supporting files, invocation control, and subagent execution; (2) **plugins use `.claude-plugin/plugin.json` manifests** with a defined directory structure; (3) **subagents use frontmatter with `name`, `description`, `tools`, `model`, and other fields** — confirmed HIGH confidence from official docs. The earlier MEDIUM-confidence concerns from project research are now resolved.

**Primary recommendation:** Structure this as a proper CC plugin with `.claude-plugin/plugin.json` manifest. Use skills (not bare commands) for `/doc:setup`. Store per-project config as `.doc-writer/config.yaml`. Ship universal quality rules and doc-system guidance as skill supporting files.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Config lives in `.doc-writer/config.yaml` in the target project root (YAML format)
- `.doc-writer/` directory is committed to git — shared across team members
- `.doc-writer/` also contains guidance files and rules file
- `/doc:setup` uses structured prompts with specific fields: audience name, skill level, assumed knowledge, never-assume list
- Multi-audience: start with primary audience, then offer "Do you have a secondary audience?" — repeat for additional audiences
- Auto-detection: scan project for doc system (mkdocs.yml, docusaurus.config.js, etc.), source language, existing docs; present findings for user to confirm or override
- Re-run behavior: show current config, offer to edit specific fields (not full re-run of Q&A)
- v1 ships two guidance files: mkdocs-material and plain markdown
- Guidance files are about opinionated preferences for feature usage, not syntax reference
- During setup, selected guidance file is copied to `.doc-writer/` — user can edit it per-project
- Users can add entirely new doc-system guidance files to `.doc-writer/` and they are auto-detected at runtime
- Active doc system is a project preference stored in config.yaml
- Universal quality rules are baked into agent prompts — non-overridable
- A default rules file ships with the plugin and is copied to `.doc-writer/rules.md` during setup
- The rules file is additive — project-specific rules that extend (not override) universal rules
- Rules are written as freeform markdown — natural language rules that agents interpret

### Claude's Discretion
- Config YAML schema structure (field names, nesting)
- Guidance file internal format and naming convention
- Plugin file structure (agents/, commands/, skills/ layout)
- How auto-detection scans work internally
- Default rules file content and format

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SETUP-01 | Project author can run a setup command that asks about target audience(s) and persists config per-project | CC skill format with `disable-model-invocation: true` for `/doc:setup`; YAML config written to `.doc-writer/config.yaml` via Write tool; audience fields defined in schema |
| SETUP-02 | Quality rules are layered — universal defaults baked into agents, project-specific overrides in config file | Universal rules as skill content baked into agent system prompts; project rules in `.doc-writer/rules.md` (freeform markdown); agents read both at runtime |
| SETUP-03 | Universal quality rules and guidance are doc-system-agnostic; doc-system-specific guidance lives in separate editable .md files, selected during setup | Quality rules skill is doc-system-agnostic; guidance files (`mkdocs-material.md`, `plain-markdown.md`) shipped as skill supporting files, copied to `.doc-writer/` during setup |
| SETUP-04 | Project author can define custom quality rules in project config that Editor enforces | `.doc-writer/rules.md` is freeform markdown; agents read this file and apply rules additively on top of universal rules |
| SETUP-05 | Audience Q&A determines number and types of End-User Persona agents to instantiate | Config schema stores audiences array; each audience entry has name, skill_level, assumed_knowledge, never_assume fields; downstream phases use audience count to spawn persona agents |
</phase_requirements>

## Standard Stack

### Core

| Component | Format | Purpose | Why Standard |
|-----------|--------|---------|--------------|
| Claude Code plugin | `.claude-plugin/plugin.json` manifest | Plugin distribution and component discovery | Official CC plugin format — namespaced skills, structured discovery, installable via `--plugin-dir` or marketplace |
| Skills (`SKILL.md`) | YAML frontmatter + markdown body | `/doc:setup` entry point, quality rules reference, doc guidance | Skills are CC's recommended format over bare commands — support directories, supporting files, invocation control |
| Agents (`agents/*.md`) | YAML frontmatter + markdown body | Doc Author, Editor, User Persona agent definitions | Standard CC subagent format — `name`, `description`, `tools`, `model` fields in frontmatter |
| YAML config | `.doc-writer/config.yaml` | Per-project configuration | User decision — YAML for human readability; Claude natively reads/writes YAML via Read/Write tools |

### Supporting

| Component | Format | Purpose | When to Use |
|-----------|--------|---------|-------------|
| Guidance files | Plain markdown (`.md`) | Doc-system-specific preferences | Copied to `.doc-writer/` during setup; read by agents at write-time |
| Rules file | Plain markdown (`.md`) | Project-specific quality rules | Copied from plugin defaults during setup; user edits for project needs |
| Plugin scripts | Bash via `!`command`` | Auto-detection scans during setup | Dynamic context injection in skill content |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| YAML config | JSON config | JSON is more structured but less human-friendly for editing; YAML was a locked user decision |
| Skills | Bare commands (`.claude/commands/`) | Commands still work but skills are recommended — skills support supporting files and invocation control |
| Plugin manifest | Standalone files in `~/.claude/` | Standalone is simpler but loses namespacing, versioning, and marketplace distribution |

**Installation:**
```bash
# Development testing
claude --plugin-dir ./doc-writer-plugin

# Or copy to user plugins (manual install)
cp -r ./doc-writer-plugin ~/.claude/plugins/doc-writer/
```

## Architecture Patterns

### Recommended Plugin Structure
```
doc-writer-plugin/                    # Plugin root
├── .claude-plugin/
│   └── plugin.json                   # Plugin manifest (name, version, description)
├── skills/
│   ├── setup/                        # /doc-writer:setup skill
│   │   ├── SKILL.md                  # Setup Q&A orchestrator
│   │   ├── defaults/
│   │   │   ├── config-template.yaml  # Default config template
│   │   │   ├── rules.md              # Default project rules
│   │   │   ├── mkdocs-material.md    # MkDocs Material guidance
│   │   │   └── plain-markdown.md     # Plain markdown guidance
│   │   └── scripts/
│   │       └── detect-project.sh     # Auto-detection script
│   ├── quality-rules/                # Universal quality rules
│   │   └── SKILL.md                  # Rules baked into agent context
│   └── diataxis/                     # Diataxis framework reference
│       └── SKILL.md                  # Content type definitions & templates
├── agents/
│   ├── doc-author.md                 # Doc Author subagent
│   ├── doc-editor.md                 # Editor subagent
│   └── doc-persona.md                # User Persona subagent (one per audience)
└── README.md                         # Plugin documentation
```

### Per-Project Directory (created by `/doc:setup`)
```
{project_root}/
└── .doc-writer/
    ├── config.yaml                   # Project config (audiences, doc system, paths)
    ├── rules.md                      # Project-specific rules (editable, additive)
    └── mkdocs-material.md            # Selected guidance file (editable copy)
```

### Pattern 1: Plugin Manifest
**What:** The `.claude-plugin/plugin.json` file that defines plugin metadata and enables CC to discover components.
**When to use:** Required for any CC plugin.
**Example:**
```json
// Source: https://code.claude.com/docs/en/plugins
{
  "name": "doc-writer",
  "description": "Multi-agent documentation writer — Author, Editor, and User Persona agents collaborate to produce publication-quality library docs",
  "version": "1.0.0",
  "author": {
    "name": "Paul"
  },
  "keywords": ["documentation", "writing", "multi-agent", "diataxis"]
}
```
**Confidence:** HIGH — format confirmed from official CC plugin documentation.

### Pattern 2: Setup Skill with Disable-Model-Invocation
**What:** The `/doc:setup` skill is user-invoked only (not auto-triggered by Claude). Uses `disable-model-invocation: true` to prevent Claude from running setup automatically.
**When to use:** For workflow skills with side effects (writing config files).
**Example:**
```yaml
# Source: https://code.claude.com/docs/en/skills
---
name: setup
description: Configure doc-writer for this project. Creates .doc-writer/ directory with config, rules, and guidance files.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: "[--reset]"
---

# Doc Writer Setup

[Setup Q&A orchestrator instructions...]
```
**Confidence:** HIGH — `disable-model-invocation: true` is a documented frontmatter field.

### Pattern 3: Config File Read/Write via Claude's Native Abilities
**What:** Claude reads `.doc-writer/config.yaml` using the Read tool and writes it using the Write tool. No YAML parsing library is needed — Claude natively understands YAML syntax.
**When to use:** For all config operations. Claude's LLM capabilities handle YAML parsing/generation.
**Example config schema:**
```yaml
# .doc-writer/config.yaml
version: 1

audiences:
  - name: "Python developers building web APIs"
    skill_level: intermediate
    assumed_knowledge:
      - Python 3.x basics
      - pip and virtual environments
      - HTTP request/response concepts
    never_assume:
      - FastAPI internals
      - async/await patterns
      - database ORMs

doc_system: mkdocs-material

paths:
  docs_root: docs/
  source_root: src/

detected:
  language: python
  doc_system: mkdocs-material
  existing_docs: true
```
**Confidence:** HIGH — Claude natively reads/writes YAML; Read/Write tools confirmed from CC docs.

### Pattern 4: Auto-Detection via Dynamic Context Injection
**What:** The setup skill uses `!`command`` syntax to run a detection script before the skill content is sent to Claude. Detection results are injected into the prompt.
**When to use:** During `/doc:setup` to scan the project.
**Example:**
```yaml
---
name: setup
description: Configure doc-writer for this project
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
---

## Project Detection Results
!`bash ${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/detect-project.sh`

## Setup Instructions
[Use detection results to pre-populate Q&A defaults...]
```

The detection script:
```bash
#!/bin/bash
# detect-project.sh — scan project for doc system, language, existing docs

echo "## Detected Configuration"
echo ""

# Doc system detection
if [ -f "mkdocs.yml" ] || [ -f "mkdocs.yaml" ]; then
  echo "- **Doc system:** mkdocs-material (found mkdocs.yml)"
elif [ -f "docusaurus.config.js" ] || [ -f "docusaurus.config.ts" ]; then
  echo "- **Doc system:** docusaurus (found docusaurus.config)"
elif [ -f ".vitepress/config.js" ] || [ -f ".vitepress/config.ts" ] || [ -f ".vitepress/config.mts" ]; then
  echo "- **Doc system:** vitepress (found .vitepress/config)"
elif [ -f "conf.py" ]; then
  echo "- **Doc system:** sphinx (found conf.py)"
else
  echo "- **Doc system:** plain-markdown (no doc system detected)"
fi

# Language detection
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "setup.cfg" ]; then
  echo "- **Language:** Python"
elif [ -f "package.json" ]; then
  if [ -f "tsconfig.json" ]; then
    echo "- **Language:** TypeScript"
  else
    echo "- **Language:** JavaScript"
  fi
elif [ -f "Cargo.toml" ]; then
  echo "- **Language:** Rust"
elif [ -f "go.mod" ]; then
  echo "- **Language:** Go"
else
  echo "- **Language:** Unknown"
fi

# Existing docs detection
if [ -d "docs" ] || [ -d "doc" ] || [ -d "documentation" ]; then
  DOC_COUNT=$(find docs doc documentation -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "- **Existing docs:** Yes ($DOC_COUNT markdown files)"
else
  echo "- **Existing docs:** No docs directory found"
fi
```
**Confidence:** HIGH — `!`command`` syntax is documented in CC skills docs. Shell-based detection is straightforward.

### Pattern 5: Guidance File Copy-and-Customize
**What:** During setup, the selected guidance file is copied from the plugin's `skills/setup/defaults/` to `.doc-writer/` in the project. The user gets their own editable copy.
**When to use:** For guidance files and the default rules file.
**Example flow:**
1. Setup detects (or user selects) `mkdocs-material`
2. Plugin copies `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/mkdocs-material.md` to `.doc-writer/mkdocs-material.md`
3. Plugin copies `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/rules.md` to `.doc-writer/rules.md`
4. Config records `doc_system: mkdocs-material`
5. At runtime, agents read `.doc-writer/mkdocs-material.md` for guidance and `.doc-writer/rules.md` for project rules

**Confidence:** HIGH — this is a file copy operation using Write tool. `${CLAUDE_PLUGIN_ROOT}` variable is documented for plugins.

### Pattern 6: Re-Run Update Behavior
**What:** When `/doc:setup` detects an existing `.doc-writer/config.yaml`, it reads the current config, displays it, and offers field-by-field editing rather than a full Q&A re-run.
**When to use:** Every re-run after initial setup.
**Example logic in SKILL.md:**
```markdown
## Re-Run Detection

1. Check if `.doc-writer/config.yaml` exists using Glob
2. If YES:
   - Read the current config
   - Display: "Current configuration:"
   - Show audiences, doc system, paths
   - Ask: "What would you like to update?"
   - Options: audiences, doc system, paths, rules, guidance file
   - Update only the selected fields
   - Preserve all other config values
3. If NO:
   - Run full Q&A flow (first-time setup)
```
**Confidence:** HIGH — conditional logic is natural language in the skill content; Claude handles branching.

### Anti-Patterns to Avoid

- **Baking doc-system syntax into agent prompts:** Guidance is per-project, not per-agent. Agent prompts reference the guidance file path; they don't contain guidance content directly.
- **Using JSON for the config file:** User locked YAML. Don't second-guess this.
- **Making `/doc:setup` auto-invocable:** Setup has side effects (creates files). It must be `disable-model-invocation: true` so only the user triggers it.
- **Putting supporting files inside `.claude-plugin/`:** Official docs warn against this. Only `plugin.json` goes in `.claude-plugin/`. Skills, agents, and commands go at the plugin root level.
- **Over-engineering config validation:** Claude reads YAML natively. A JSON Schema or formal validator adds complexity with little benefit for v1 — Claude can validate config structure through its own understanding.
- **Creating a separate `/doc:install` command:** The CC plugin system handles installation via `--plugin-dir` or marketplace. Don't build custom install logic.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parsing | Custom YAML parser or js-yaml dependency | Claude's native YAML reading via Read tool | Claude understands YAML natively; no runtime dependency needed |
| Plugin discovery | Custom file scanner for agent/skill loading | CC plugin manifest (`.claude-plugin/plugin.json`) | CC auto-discovers skills/, agents/, commands/ from manifest |
| Skill invocation | Custom slash command router | CC skill system (`SKILL.md` with frontmatter) | CC handles routing, namespacing, invocation control |
| Subagent spawning | Custom orchestration code | CC Agent tool with agent file definitions | CC's Agent tool (formerly Task) handles subagent lifecycle |
| Config schema validation | JSON Schema validator library | Natural language validation in skill instructions | Claude validates structure through understanding; formal schemas add overhead |
| File templating | Handlebars/Mustache/EJS | `$ARGUMENTS` substitution + Write tool | CC skills support argument substitution natively; complex templates use Claude's generation |

**Key insight:** This plugin has zero runtime dependencies. Everything is markdown files that CC interprets. The "code" is prompts, and the "runtime" is Claude Code itself.

## Common Pitfalls

### Pitfall 1: Guidance File Not Found at Runtime
**What goes wrong:** Agents reference `.doc-writer/{doc_system}.md` but the file doesn't exist because setup wasn't run or a custom doc system name was entered without a matching file.
**Why it happens:** The guidance file path is derived from config, but the file must physically exist in `.doc-writer/`.
**How to avoid:** Agents must check for guidance file existence before reading. If missing, fall back to plain-markdown guidance or warn the user. The setup skill should validate that the selected guidance file exists in the plugin's defaults before copying.
**Warning signs:** Agent errors on Read tool for missing guidance file path.

### Pitfall 2: Config Overwrite on Re-Run
**What goes wrong:** Re-running `/doc:setup` destroys existing audiences or custom rules by writing a fresh config from scratch.
**Why it happens:** The setup skill doesn't check for existing config before starting Q&A.
**How to avoid:** First action in setup: check for `.doc-writer/config.yaml`. If exists, read it and present update flow. Never generate a fresh config when one exists. This is a locked user decision — the re-run flow shows current config and offers field-by-field editing.
**Warning signs:** User complains that re-running setup lost their settings.

### Pitfall 3: Audiences Array vs Single Audience
**What goes wrong:** Config schema stores a single audience object instead of an array. When Phase 4 needs to spawn one persona per audience, the schema doesn't support it.
**Why it happens:** v1 starts with "primary audience" Q&A which feels like a single value. Multi-audience is added later.
**How to avoid:** Config schema MUST use `audiences: []` (array) from day one, even if only one audience is configured. The Q&A flow asks "Do you have a secondary audience?" and appends to the array. Phase 4's persona spawning iterates the array.
**Warning signs:** Config has `audience:` (singular) instead of `audiences:` (plural array).

### Pitfall 4: Universal Rules Scattered Across Files
**What goes wrong:** Universal quality rules are split across multiple locations (some in agent prompts, some in a skill, some in both) leading to inconsistencies when rules are updated.
**Why it happens:** Rules feel like they belong in the agent that enforces them, but they also need to be referenced by other agents.
**How to avoid:** Single source of truth: universal rules live in `skills/quality-rules/SKILL.md`. Agents reference this skill via the `skills:` frontmatter field for preloading, or read the file at runtime. Rule content is never duplicated in agent body text.
**Warning signs:** Same rule stated differently in two agent files.

### Pitfall 5: Plugin Root Path Confusion
**What goes wrong:** Skill content references files using relative paths that break when the plugin is installed in different locations.
**Why it happens:** During development, relative paths from the skill file to supporting files work. After installation, the plugin root moves.
**How to avoid:** Use `${CLAUDE_PLUGIN_ROOT}` for all references to plugin-internal files. This variable resolves to the actual plugin installation path at runtime.
**Warning signs:** "File not found" errors when plugin is installed via marketplace vs `--plugin-dir`.

### Pitfall 6: Mixing Skill and Command Formats
**What goes wrong:** Some components are created as bare commands (`commands/*.md`) and others as skills (`skills/*/SKILL.md`), creating inconsistent behavior and missing features.
**Why it happens:** Both formats work, so the choice seems arbitrary. But skills support supporting files and invocation control that commands don't.
**How to avoid:** Use skills exclusively. Commands are a legacy format. The only exception is if you need a very simple, single-file command with no supporting resources.
**Warning signs:** A component needs supporting files but was created as a bare command.

## Code Examples

Verified patterns from official sources:

### Plugin Manifest
```json
// Source: https://code.claude.com/docs/en/plugins
{
  "name": "doc-writer",
  "description": "Multi-agent documentation writer for library projects",
  "version": "1.0.0",
  "author": {
    "name": "Paul"
  },
  "keywords": ["documentation", "writing", "diataxis", "multi-agent"]
}
```

### Skill File (Setup)
```yaml
# Source: https://code.claude.com/docs/en/skills
---
name: setup
description: Configure doc-writer for this project. Creates .doc-writer/ with config, rules, and guidance.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Doc Writer Setup

## Pre-Check
!`bash ${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/detect-project.sh`

## Instructions

[Full setup Q&A logic here...]
```

### Agent File (Subagent Definition)
```markdown
# Source: https://code.claude.com/docs/en/sub-agents
---
name: doc-author
description: Writes draft library documentation using Diataxis framework. Produces audience-calibrated, internal-detail-free docs with working code examples.
tools: Read, Write, Glob, Grep
model: inherit
skills:
  - doc-writer:quality-rules
  - doc-writer:diataxis
---

You are a Doc Author agent. Your job is to write library documentation
from the end user's perspective, never from the builder's perspective.

[Full system prompt...]
```

### Quality Rules Skill (Universal, Non-Overridable)
```yaml
# Source: pattern derived from CC skills docs
---
name: quality-rules
description: Universal documentation quality rules applied by all doc-writer agents. These rules are non-overridable baseline standards.
user-invocable: false
---

# Universal Quality Rules

These rules apply to ALL documentation produced by doc-writer agents.
They cannot be overridden by project configuration.

## Rule 1: No Internal Details
Documentation must never reference:
- Test utilities or test configuration
- CI/CD pipeline configuration
- Development scripts (justfile, Makefile recipes for dev)
- Internal module names not part of the public API
- Maintainer-only concerns

## Rule 2: Working Code Examples Required
Every API feature or function documented must include at least one
realistic, working code example. Examples must:
- Demonstrate a real use case (not `doThing("example", 42)`)
- Include enough surrounding context for the reader to understand why
- Specify the language in fenced code blocks

## Rule 3: Consistent Structure
All pages of the same documentation type (tutorial, how-to, reference,
explanation) must follow the same structural template.

## Rule 4: Cross-Reference Code Mentions
All inline `code` mentions in prose must be linked to the relevant
API Reference entry where one exists.

## Rule 5: Audience-Calibrated Language
Vocabulary, assumed knowledge, and explanation depth must match the
configured audience. Never assume knowledge listed in the audience's
`never_assume` list.
```

### Config Template
```yaml
# .doc-writer/config.yaml — generated by /doc:setup
version: 1

audiences:
  - name: ""              # e.g., "Python developers building REST APIs"
    skill_level: ""        # beginner | intermediate | advanced
    assumed_knowledge: []  # what readers already know
    never_assume: []       # what must always be explained

doc_system: ""             # mkdocs-material | plain-markdown | (user-defined)

paths:
  docs_root: "docs/"
  source_root: "src/"

detected:
  language: ""
  doc_system: ""
  existing_docs: false
```

### Guidance File (MkDocs Material)
```markdown
# MkDocs Material Guidance

Opinionated preferences for writing documentation with MkDocs Material.
These are style preferences, not syntax reference — agents already
understand MkDocs Material syntax.

## Admonitions
- Prefer admonition blocks (`!!! note`, `!!! warning`) over bold text
  for callouts
- Use `!!! tip` for best practices, `!!! warning` for gotchas,
  `!!! danger` for breaking changes
- Use collapsible admonitions (`??? note`) for optional/advanced details

## Code Blocks
- Always specify language on fenced code blocks
- Use line highlighting for important lines: `hl_lines="3 4"`
- Use code annotations for complex examples

## Tabs
- Use content tabs for showing the same concept in multiple
  languages/frameworks
- Tab labels should be short: "Python", "JavaScript", not
  "Python Example Code"

## Navigation
- Keep nav depth to 3 levels maximum
- Group related pages under a single section
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.claude/commands/*.md` | `.claude/skills/*/SKILL.md` | 2025 (CC skills launch) | Skills support directories, supporting files, invocation control; commands still work but are legacy |
| `doc-writer.config.json` (from initial research) | `.doc-writer/config.yaml` (from user decision) | Phase 1 context session | Config format is YAML, lives in `.doc-writer/` directory (not project root) |
| Task tool for subagent spawning | Agent tool (renamed from Task) | CC v2.1.63 | `Task(...)` still works as alias; new code should use `Agent(...)` |
| Global install to `~/.claude/` | Plugin with `.claude-plugin/plugin.json` | 2025 (CC plugins system) | Proper namespacing, versioning, marketplace distribution |
| Agents don't know about skills | `skills:` frontmatter field preloads skill content | 2025 (CC subagents update) | Agents can preload skill content at startup — no runtime discovery needed |

**Deprecated/outdated:**
- `doc-writer.config.json` in project root — replaced by `.doc-writer/config.yaml` per user decision
- Bare command files for complex workflows — skills with supporting files are recommended
- Task tool name — renamed to Agent tool in CC v2.1.63 (Task still works as alias)

## Open Questions

1. **`${CLAUDE_PLUGIN_ROOT}` availability in agent files**
   - What we know: `${CLAUDE_PLUGIN_ROOT}` is documented for skills and commands.
   - What's unclear: Whether agent files (`agents/*.md`) can also use `${CLAUDE_PLUGIN_ROOT}` in their system prompts for reading plugin-internal files.
   - Recommendation: Test during implementation. Fallback: agents use Glob to discover plugin location, or reference skills via `skills:` frontmatter field which handles path resolution.

2. **Skill preloading namespace syntax for plugin skills**
   - What we know: Agents use `skills: [skill-name]` in frontmatter to preload skill content. Plugin skills are namespaced as `plugin-name:skill-name`.
   - What's unclear: Whether the `skills:` field in an agent within the same plugin uses the namespaced name (`doc-writer:quality-rules`) or the bare name (`quality-rules`).
   - Recommendation: Test both during implementation. Likely namespaced based on CC's consistent namespacing pattern.

3. **Custom doc system guidance files runtime discovery**
   - What we know: Users can create custom guidance files (e.g., `.doc-writer/vitepress.md`) that should be auto-detected.
   - What's unclear: How agents discover available guidance files at runtime without hardcoding filenames.
   - Recommendation: Agent reads `config.yaml` for `doc_system` value, then attempts to read `.doc-writer/{doc_system}.md`. If the file exists, use it. This is simple file-based discovery — no special mechanism needed.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual CC session testing (no automated test framework) |
| Config file | None — this is a markdown-file plugin with no executable code |
| Quick run command | `claude --plugin-dir ./doc-writer-plugin` then invoke `/doc-writer:setup` |
| Full suite command | Manual: run setup on a sample project, verify config output, verify re-run behavior |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SETUP-01 | `/doc:setup` creates `.doc-writer/config.yaml` with audience data | manual (CC session) | `claude --plugin-dir ./doc-writer-plugin` then `/doc-writer:setup` | N/A — markdown plugin |
| SETUP-02 | Universal rules in skill, project rules in `.doc-writer/rules.md` | manual (inspect files) | Read `skills/quality-rules/SKILL.md` and `.doc-writer/rules.md` after setup | N/A |
| SETUP-03 | Guidance files copied to `.doc-writer/`, doc-system-agnostic rules | manual (inspect files) | Verify guidance file exists in `.doc-writer/` after setup | N/A |
| SETUP-04 | Custom rules in `.doc-writer/rules.md` are freeform, additive | manual (edit + re-read) | Edit `.doc-writer/rules.md`, verify agent reads updated content | N/A |
| SETUP-05 | Audiences array supports multiple entries for persona spawning | manual (multi-audience setup) | Run setup, add 2+ audiences, verify `config.yaml` has array | N/A |

### Sampling Rate
- **Per task commit:** Manual: load plugin with `claude --plugin-dir`, run `/doc-writer:setup` on a test project
- **Per wave merge:** Manual: full setup flow on fresh project + re-run flow on existing project
- **Phase gate:** All 5 SETUP requirements verified via manual CC session before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Create a sample test project directory with `mkdocs.yml` for testing auto-detection
- [ ] Create a sample test project directory with `package.json` + `tsconfig.json` for testing TypeScript detection
- [ ] Create a sample test project directory with no doc system for testing plain-markdown default

## Sources

### Primary (HIGH confidence)
- [CC Skills documentation](https://code.claude.com/docs/en/skills) — skill format, frontmatter fields, invocation control, supporting files, `!`command`` syntax, `${CLAUDE_PLUGIN_ROOT}`
- [CC Plugins documentation](https://code.claude.com/docs/en/plugins) — plugin manifest format, `.claude-plugin/plugin.json`, directory structure, installation patterns
- [CC Subagents documentation](https://code.claude.com/docs/en/sub-agents) — agent file format, frontmatter fields (`name`, `description`, `tools`, `model`, `skills`, `memory`), Agent tool (renamed from Task)
- [Context7: /anthropics/claude-code](https://github.com/anthropics/claude-code) — command development skill, skill development references, plugin structure patterns
- [Context7: /websites/code_claude_en_plugins-reference](https://code.claude.com/docs/en/plugins-reference) — complete plugin manifest schema, agent configuration, skill/command component references
- GSD system inspection (`~/.claude/agents/gsd-executor.md`, `~/.claude/commands/gsd/discuss-phase.md`) — real-world agent/command file format, frontmatter conventions

### Secondary (MEDIUM confidence)
- Project's own prior research (`ARCHITECTURE.md`, `STACK.md`, `PITFALLS.md`) — architecture patterns, anti-patterns, quality rule layering; some details superseded by user decisions in CONTEXT.md

### Tertiary (LOW confidence)
- None — all key claims verified against official CC documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — CC plugin format, skill format, agent format all verified against official docs (code.claude.com)
- Architecture: HIGH — plugin directory structure follows official patterns; config schema design is well-understood YAML
- Pitfalls: HIGH — config overwrite, array-vs-singular, and path resolution are well-known patterns; CC-specific pitfalls verified against docs

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (CC plugin system is stable; 30-day validity appropriate)
