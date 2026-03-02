# Technology Stack

**Project:** Doc Writer Agent (Claude Code multi-agent documentation plugin)
**Researched:** 2026-03-02
**Confidence:** MEDIUM — Claude Code agent/plugin system research is based on training data (cutoff August 2025) plus live GSD system inspection. Web search and WebFetch were unavailable in this environment. Verify CC agent spec details against current Anthropic docs before implementation.

---

## Recommended Stack

### Core Platform: Claude Code Agent System

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Claude Code | Current (CLI) | Plugin host / execution environment | This is the target runtime — all agents run as CC subagents invoked via slash commands or the Task tool |
| Claude Opus 4.6 | API current | Primary agent model | Highest reasoning quality; the PROJECT.md `model_profile: "quality"` confirms quality-over-speed is the priority for this writing task |
| Claude Sonnet 4.x | API current | Fallback / faster passes | Suitable for structured review tasks where reasoning depth matters less |

**Confidence:** MEDIUM — Model names confirmed from system context; CC CLI version pinning is not meaningful (auto-updates).

---

### Claude Code Plugin Architecture: Agent Files

The CC plugin system as of 2025 uses **markdown prompt files** stored in `.claude/` directories. There are two scopes:

| Scope | Path | Purpose |
|-------|------|---------|
| Global agents | `~/.claude/agents/*.md` | Available in any project for any user |
| Project agents | `.claude/agents/*.md` | Available only in the current project |
| Global commands | `~/.claude/commands/*.md` | Invokable via `/command-name` slash commands |
| Project commands | `.claude/commands/*.md` | Project-scoped slash commands |

**Agent file format** (HIGH confidence from system prompt context showing real GSD agent files):

```markdown
---
name: agent-name
description: What this agent does and when to invoke it
---

[Agent role and instructions in markdown prose]
```

Agents are invoked by the orchestrator using the `Task` tool, which spawns a subagent with the agent's system prompt prepended. The agent runs with its own context window.

**Command file format** for slash-command entry points:

```markdown
# /gsd:write-docs

[Instructions for what happens when user runs this command]
[Can spawn subagents via Task tool]
```

**Confidence:** HIGH for `.claude/agents/*.md` and `.claude/commands/*.md` format — confirmed via GSD system inspection (this researcher itself is loaded from `~/.claude/agents/gsd-project-researcher.md`). HIGH for `Task` tool as the multi-agent coordination primitive.

---

### Multi-Agent Coordination Pattern

The doc-writer plugin will use the **orchestrator + subagent pattern** already established in GSD:

| Component | Role | Implementation |
|-----------|------|----------------|
| Entry command | `/write-docs` slash command | `.claude/commands/write-docs.md` |
| Orchestrator agent | Coordinates the three doc agents, manages workflow order, collects output | Can be the command file itself or a dedicated `.claude/agents/doc-writer.md` |
| Doc Author agent | Writes documentation using diataxis + humanizer guidance | `.claude/agents/doc-author.md` |
| Editor agent | Reviews for consistency, gaps, accuracy | `.claude/agents/doc-editor.md` |
| User Persona agent | Validates from audience perspective | `.claude/agents/doc-user-persona.md` |

**Coordination mechanism:** The orchestrator uses CC's `Task` tool to spawn each subagent, passing:
- Project context (source code, existing docs, CLAUDE.md)
- Agent-specific instructions
- Output from prior agents (for serial pipeline)

**Workflow options** (from PROJECT.md — design question):
- **Serial (Author → Editor → Persona):** Simplest; each agent sees prior work. Highest latency.
- **Parallel (Editor + Persona simultaneously):** Faster; Editor and Persona review Author's draft in parallel. Requires orchestrator to merge feedback.
- **Persona-first:** Persona sets acceptance criteria before Author writes. Most rigorous; most complex.

**Recommendation:** Start with serial pipeline. It's simplest to implement, debug, and iterate. Make order configurable via project config once the pattern is proven.

**Confidence:** HIGH for Task tool as coordination primitive. MEDIUM for specific workflow recommendation (based on GSD pattern observation, not CC-specific guidance).

---

### Project Configuration System

| Config Mechanism | Path | Purpose |
|------------------|------|---------|
| Project CLAUDE.md | `CLAUDE.md` (project root) | CC-standard context file; agents read this automatically |
| Plugin config | `.claude/doc-writer.yml` or `CLAUDE.md` section | Audience, doc system, custom rules, project-specific overrides |
| Global defaults | Baked into agent prompts | Universal rules (diataxis, humanizer, no internals) |

**Recommended config approach:** A dedicated `doc-writer` section in `CLAUDE.md` is the most idiomatic CC pattern — no additional files, no extra tooling. Users add a `## Doc Writer` section to their existing CLAUDE.md. The agents read CLAUDE.md as part of their standard context.

Alternative: a `.claude/doc-writer.yml` config file. More structured but requires agents to explicitly parse it. Lower friction for complex configs (audiences, doc system specifics).

**Recommendation:** Start with a CLAUDE.md section. Add YAML config support if the section format proves limiting.

**Confidence:** MEDIUM — CLAUDE.md as project context is HIGH confidence CC standard; the specific "section within CLAUDE.md" pattern is a design recommendation, not a documented CC API.

---

### Documentation Frameworks (What Agents Must Understand)

These are the doc systems the plugin outputs should support. Agents need system-specific rules in their config.

| Doc System | Format | Key Rules | Priority |
|------------|--------|-----------|----------|
| mkdocs-material | Markdown + mkdocs.yml | Admonitions (`!!! note`), tabs, code blocks with language hints, `nav` structure | HIGH — primary test environment per PROJECT.md |
| Docusaurus | MDX + sidebar.js | JSX in markdown (MDX), `:::note` admonitions, frontmatter with `id`/`title`/`sidebar_label` | MEDIUM — widely used in JS ecosystem |
| Sphinx | RST or MyST Markdown | Cross-references (`:ref:`), directives (`.. code-block::`), docstring integration | LOW — Python ecosystem, less common for new projects |
| Plain Markdown | Markdown | No system-specific syntax; output works anywhere | HIGH — default when no system specified |
| VitePress | Markdown + Vue | Frontmatter, custom containers (`:::tip`), Vue components in markdown | LOW — growing but niche |

**Agents should NOT bake in doc-system rules** — these belong in per-project config so the plugin stays doc-system-agnostic (explicit requirement in PROJECT.md). Agents read the config to apply the correct syntax rules.

**Confidence:** HIGH for mkdocs-material and Docusaurus patterns. MEDIUM for Sphinx/VitePress (training data, verify current syntax). HIGH for the "config-driven, not baked-in" principle (from PROJECT.md requirements).

---

### Documentation Quality Frameworks

The agents need to internalize these frameworks. They are not software dependencies — they are authoring methodologies the agents apply as knowledge.

| Framework | What It Is | Usage in Plugin |
|-----------|-----------|----------------|
| Diátaxis | Four-quadrant doc framework: tutorials, how-to guides, reference, explanations | Doc Author primary framework for structure and content decisions |
| Every Doc Needs a Purpose (Google) | Each page serves one job | Editorial principle baked into Editor agent |
| Humanizer heuristics | Tone, active voice, concrete examples, no jargon | Applied by Editor agent post-draft |

**Confidence:** HIGH — these are authoring principles, not versioned software.

---

### What NOT to Use

| Technology | Why Not |
|------------|---------|
| LangChain / LangGraph | External Python orchestration framework — adds a runtime dependency and deployment complexity for what is natively a Claude Code plugin. CC's Task tool covers multi-agent coordination natively. |
| AutoGen / CrewAI | Same problem as LangChain. These are alternatives to CC, not additions. |
| TypeDoc / PyDoc / JSDoc | API reference auto-generation — explicitly out of scope per PROJECT.md. These generate API refs; this plugin writes narrative docs. |
| Standalone Node.js or Python script | Would require users to have a separate runtime, manage dependencies, and invoke outside CC. The plugin must work within CC's environment. |
| Vector databases / RAG pipelines | Overkill for this use case. Agents receive source code + docs directly as context. No retrieval step needed. |
| Custom MCP server | Nothing about this plugin requires new MCP tools. CC's built-in tools (Read, Glob, Grep, Task) are sufficient. Add MCP only if a specific capability gap emerges. |
| Hardcoded doc-system syntax in agents | Violates the content-first, doc-system-agnostic requirement. Doc-system rules belong in project config. |

**Confidence:** HIGH for all exclusions — each is justified by either explicit PROJECT.md requirements or architectural simplicity principles.

---

## Distribution Model

| Option | Mechanism | Pros | Cons |
|--------|-----------|------|------|
| Global install (copy to `~/.claude/`) | User copies agent files to `~/.claude/agents/` and `~/.claude/commands/` | Works today, no marketplace needed | Manual installation; no versioning |
| Project install (copy to `.claude/`) | Files live in the repo; automatically available to all contributors | Zero install friction for collaborators; version-controlled with the project | Not shareable across unrelated projects |
| CC Marketplace | Future official distribution channel | First-class discovery and installation | Exact format TBD from research; PROJECT.md notes this explicitly |

**Recommendation:** Build for global install (files in `~/.claude/`) as the primary distribution target. Structure the project so files can be copied with a single command. Once the CC Marketplace format is documented, add support without changing the agent file format.

**Confidence:** MEDIUM — CC Marketplace is mentioned in PROJECT.md as "TBD from research"; the global `~/.claude/` install pattern is confirmed from GSD system inspection.

---

## Installation Pattern (Global)

```bash
# Copy agent files to global ~/.claude/
cp .claude/agents/doc-author.md ~/.claude/agents/
cp .claude/agents/doc-editor.md ~/.claude/agents/
cp .claude/agents/doc-user-persona.md ~/.claude/agents/

# Copy entry command
cp .claude/commands/write-docs.md ~/.claude/commands/

# Verify
ls ~/.claude/agents/ | grep doc-
ls ~/.claude/commands/ | grep write-docs
```

No package manager. No runtime dependencies. No build step.

---

## Sources

- PROJECT.md — authoritative requirements source for this project
- System prompt context — GSD agent system inspection (agent file format, `.claude/agents/*.md` convention, Task tool coordination)
- Training knowledge (cutoff August 2025) — Claude Code CLI architecture, CLAUDE.md convention, diátaxis framework
- **Note:** WebSearch and WebFetch were unavailable during this research session. Findings marked MEDIUM confidence should be verified against current Anthropic Claude Code documentation before implementation.
