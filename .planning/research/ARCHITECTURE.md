# Architecture Patterns

**Domain:** Multi-agent Claude Code plugin for library documentation
**Researched:** 2026-03-02
**Confidence:** MEDIUM — CC plugin structure inferred from Glob inspection of official plugins + GSD system, supported by training knowledge. Verify agent frontmatter conventions against current CC docs before implementation.

---

## Recommended Architecture

### System Overview

The plugin is an **orchestrated pipeline plugin**: a single entry-point command spawns three specialized agents in sequence (or selectively in parallel), each receiving structured context and producing doc artifacts or review annotations. The orchestrating command is the user-facing interface; the agents are headless workers.

```
User invokes /doc:write
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  ORCHESTRATOR COMMAND  (commands/write.md)           │
│  - Reads project config                             │
│  - Discovers source files + existing docs           │
│  - Runs audience setup Q&A if first use             │
│  - Constructs context bundles                       │
│  - Spawns agents in pipeline order                  │
└─────────────────────────────────────────────────────┘
       │               │               │
       ▼               ▼               ▼
┌──────────┐   ┌──────────────┐  ┌─────────────────┐
│  AUTHOR  │──▶│    EDITOR    │──▶│  USER PERSONA   │
│ agent    │   │    agent     │   │     agent       │
└──────────┘   └──────────────┘  └─────────────────┘
       │               │               │
       ▼               ▼               ▼
  Draft docs    Reviewed docs    Persona report
  (markdown)   (annotated/rev.)  (gap list + pass/fail)
```

---

## Component Boundaries

### Component 1: Entry Command (`commands/write.md`)

**Responsibility:** The user-facing orchestrator. Reads config, discovers context, manages agent pipeline, and produces final output.

**Does NOT:**
- Write documentation directly
- Make quality judgments
- Represent any audience perspective

**Communicates with:** All three agents (spawns each via `Task` tool). Reads `doc-writer.config.json`. Reads CLAUDE.md for project context.

**Inputs:**
- User invocation args (optional: target scope — all docs, single file, specific section)
- `doc-writer.config.json` (audience, doc system, custom rules, paths)
- Source code in project (via Read tool)
- Existing docs (via Read tool)
- CLAUDE.md (project context, if present)

**Outputs:**
- Final written/revised doc files
- (Optional) review summary printed to user

---

### Component 2: Doc Author Agent (`agents/doc-author.md`)

**Responsibility:** Write draft documentation using Diátaxis framework. Produces publication-quality prose from source code and project context — never from the builder's perspective.

**Does NOT:**
- Review its own work
- Represent user perspective
- Apply per-project style rules (that is the Editor's job)

**Quality rules baked in (universal defaults):**
- Diátaxis structure: tutorials → how-tos → reference → explanation
- No internal/maintainer details (CI config, dev scripts, test utilities, justfile recipes)
- Every API/feature must include a working code example
- Same-type pages follow consistent structure templates
- All inline `code` mentions linked to relevant API reference items

**Inputs received from orchestrator:**
- Source files (or relevant subset)
- Existing docs (if revising)
- Audience description from config
- Doc type being written (tutorial / how-to / reference / explanation)
- Scope (whole library vs specific feature)

**Outputs:**
- Draft markdown document(s)
- Self-assessment: list of any areas of uncertainty flagged for Editor

---

### Component 3: Editor Agent (`agents/doc-editor.md`)

**Responsibility:** Quality gate. Reviews Author output for consistency, gaps, accuracy, and humanized tone. Applies the "humanizer" transform. Enforces per-project style rules from config.

**Does NOT:**
- Rewrite content from scratch (edits, not replaces)
- Validate from the user's perspective (that is Persona's job)
- Make audience decisions

**Quality rules applied:**
- Universal rules (same as Author — catches violations Author missed)
- Project-specific rules from `doc-writer.config.json`
- Doc system rules (mkdocs-material admonitions, Docusaurus MDX, etc.) if configured
- Humanizer pass: remove AI-pattern prose, vary sentence structure, convert passive to active

**Inputs received from orchestrator:**
- Author's draft document(s)
- Author's self-assessment flags
- Project config (audience, doc system, custom rules)
- Source code (for accuracy cross-check)

**Outputs:**
- Revised document(s) with tracked changes summary
- Editor notes: list of changes made and rationale
- Escalations: issues Editor could not resolve (passed to User for decision)

---

### Component 4: User Persona Agent (`agents/user-persona.md`)

**Responsibility:** Audience validation. Reads the edited doc as the target user would. Generates realistic test scenarios from project context without manual authoring. Reports whether a real user of the documented library could accomplish their goals using only the documentation.

**Does NOT:**
- Write or edit documentation
- Apply style rules
- Know implementation details (receives only the docs + library's public API surface)

**Persona generation logic:**
- Reads project README, source public API, audience config
- Generates 3-5 realistic "I want to..." user journeys for this audience
- Attempts to follow the docs to accomplish each journey
- Reports: success / blocked / confused — with specific passage citations

**Inputs received from orchestrator:**
- Editor-revised document(s)
- Audience description from config
- Library public API surface (source headers / type signatures only — not internals)
- Project README

**Outputs:**
- Persona test report (per scenario: pass/fail/partial + evidence)
- Actionable gap list (what information was missing or unclear)
- Verdict: PUBLISH-READY / NEEDS-REVISION / MAJOR-GAPS

---

### Component 5: Project Config (`doc-writer.config.json`)

**Responsibility:** Per-project configuration that personalizes behavior without changing agent code. Stored in the project root (committed to version control so it persists across sessions).

**Structure:**
```json
{
  "audience": {
    "primary": "TypeScript developers integrating a payments SDK",
    "secondary": "Contributors to the library itself",
    "skill_level": "intermediate",
    "assumes": ["TypeScript basics", "npm ecosystem"],
    "never_assume": ["payment processing domain knowledge"]
  },
  "doc_system": "mkdocs-material",
  "doc_system_rules": [
    "Use admonition blocks for warnings (not bold text)",
    "All code blocks must specify language"
  ],
  "custom_rules": [
    "Always include error handling in code examples",
    "Reference the error catalog page for every error code mentioned"
  ],
  "paths": {
    "docs_root": "docs/",
    "source_root": "src/"
  },
  "pipeline": "serial"
}
```

**Created by:** Setup command (`/doc:setup`) during first-use Q&A. Editable manually.

---

### Component 6: Setup Command (`commands/setup.md`)

**Responsibility:** First-run experience. Asks questions to populate `doc-writer.config.json`. Idempotent — re-running refines existing config. Can be invoked standalone or automatically triggered by `write` when no config exists.

**Questions asked:**
- Who is your primary audience?
- What is their skill level and what can we assume they know?
- What doc system are you using (mkdocs-material / docusaurus / plain markdown / other)?
- Any project-specific rules the author and editor should follow?

---

### Component 7: Skills (Shared Reference Data)

**Responsibility:** Reusable reference documents injected into agent system prompts. Agents reference these rather than duplicating knowledge.

**Skills:**
- `skills/diataxis/SKILL.md` — Diátaxis framework reference (tutorial vs how-to vs reference vs explanation definitions, templates)
- `skills/humanizer/SKILL.md` — Prose style guidance (anti-patterns to remove, active voice rules, sentence variation)
- `skills/quality-rules/SKILL.md` — Universal quality rules that apply to all agents

Skills are passive reference material — they inform agent behavior but are not executable.

---

## Data Flow

### Setup Flow (first use)

```
User runs /doc:setup
    │
    ▼
Setup command runs Q&A interactively
    │
    ▼
Writes doc-writer.config.json to project root
    │
    ▼
Done — /doc:write can now be invoked
```

---

### Write Flow (main pipeline)

```
Phase 0: Context Assembly (Orchestrator)
  - Read doc-writer.config.json
  - Read source files in paths.source_root
  - Read existing docs in paths.docs_root (if revising)
  - Read project CLAUDE.md (if present)
  - Determine scope (full library vs targeted)

Phase 1: Author
  - Receives: source files, existing docs, audience description, doc type, scope
  - Produces: draft_docs[] — one or more markdown files
  - Produces: author_flags[] — uncertainties to highlight for Editor

Phase 2: Editor
  - Receives: draft_docs[], author_flags[], project config, source files
  - Produces: revised_docs[] — edited versions
  - Produces: editor_notes{} — change summary per document
  - Produces: escalations[] — decisions needing user input

Phase 3: User Persona
  - Receives: revised_docs[], audience config, public API surface, README
  - Generates: test_scenarios[] — 3-5 user journeys
  - Produces: persona_report{} — per scenario verdict + evidence
  - Produces: gap_list[] — actionable items for revision

Phase 4: Output (Orchestrator)
  - If PUBLISH-READY: write files to docs_root, print summary
  - If NEEDS-REVISION: surface gap_list to user, optionally loop
  - If MAJOR-GAPS: present gap_list + persona_report, await user decision
  - If escalations[] non-empty: present each to user before final write
```

---

### Pipeline Order Rationale

**Serial (recommended default):** Author → Editor → User Persona

This ordering is correct because:
- Editor reviews Author output (depends on Author completing)
- User Persona validates Editor output (depends on Editor completing)
- Each agent's input is the previous agent's output — true serial dependency

**Alternative: User Persona runs first (Persona-First):**
Persona generates user scenarios from source code before Author writes anything. These scenarios are passed to Author as writing targets. Produces more user-oriented first drafts. Higher complexity — Author receives more inputs. Worth experimenting with in a later phase.

**Alternative: Editor + Persona in parallel (Parallel Review):**
Both review Author's draft simultaneously. Persona cannot review Editor's improvements. Saves one round-trip but produces less refined output. Suitable if speed matters more than quality.

---

## File Structure for Plugin

```
doc-writer/                      ← plugin root (distributed as CC plugin)
├── README.md                    ← plugin description, installation, usage
├── commands/
│   ├── write.md                 ← /doc:write — main orchestrator command
│   └── setup.md                 ← /doc:setup — first-run config wizard
├── agents/
│   ├── doc-author.md            ← Doc Author agent definition
│   ├── doc-editor.md            ← Editor agent definition
│   └── user-persona.md          ← User Persona agent definition
└── skills/
    ├── diataxis/
    │   └── SKILL.md             ← Diátaxis framework reference
    ├── humanizer/
    │   └── SKILL.md             ← Prose style and humanizer rules
    └── quality-rules/
        └── SKILL.md             ← Universal quality rules

Project root (user's project, not plugin):
├── doc-writer.config.json       ← Per-project config (created by /doc:setup)
└── docs/                        ← Doc output (configured in config)
```

### Agent File Format

Agent files (`agents/*.md`) follow CC's agent markdown convention:

```markdown
---
name: doc-author
description: Writes draft library documentation using Diátaxis framework
tools: Read, Write
---

[System prompt content — role, capabilities, constraints, quality rules]

## Quality Rules (Universal)
[Rules baked in — not configurable]

## Skills Reference
@skills/diataxis/SKILL.md
@skills/humanizer/SKILL.md
```

### Command File Format

Command files (`commands/*.md`) are the orchestrator. They receive user args and coordinate agents:

```markdown
---
name: write
description: Write or revise library documentation
---

[Orchestrator instructions — how to read config, discover files, spawn agents, handle output]
```

---

## How Layered Quality Rules Are Stored and Applied

### Layer 1: Universal Rules (Baked into Agent Files)

Rules that apply to every project regardless of config. Embedded directly in the agent system prompts so they cannot be overridden.

**Location:** `agents/doc-author.md` and `agents/doc-editor.md` body text

**Examples:**
- No internal/maintainer details
- Every feature requires a working code example
- Same-type pages use consistent structure
- Inline `code` mentions link to API reference

### Layer 2: Project-Specific Rules (Per-Project Config)

Rules the user provides for their project. Passed to agents as additional context from `doc-writer.config.json`.

**Location:** `doc-writer.config.json` → `custom_rules[]` array

**Examples:**
- "Always show error handling in examples"
- "Never mention the old v1 API"
- "All examples must use async/await, not callbacks"

### Layer 3: Doc System Rules (Optional, From Config)

Markup and formatting rules specific to the user's doc system. Applied by Editor when configured.

**Location:** `doc-writer.config.json` → `doc_system` + `doc_system_rules[]`

**Examples:**
- mkdocs-material: use `!!! warning` admonition blocks
- Docusaurus: code blocks use `:::` directive syntax
- All: specify language on every fenced code block

### Rule Application Order

```
1. Agent applies universal rules (hardcoded, always active)
2. Agent reads project config rules (custom_rules[] from config)
3. Editor applies doc system rules (doc_system_rules[] from config)
4. Editor runs humanizer pass (from skills/humanizer/SKILL.md)
```

---

## Integration Points

### Standalone CC Plugin Use

User installs plugin from CC marketplace (or manually copies to `~/.claude/plugins/`). Invokes with `/doc:write` or `/doc:setup`. Works in any project with source code — no GSD dependency.

**Trigger:** `User → /doc:write [scope]`
**Config location:** `{project_root}/doc-writer.config.json`
**Output:** Writes to `doc_root` configured in config

### GSD Integration Use

At GSD milestone boundaries, orchestrator invokes `/doc:write` as part of milestone completion workflow. Alternatively, a GSD phase can include documentation as a phase step.

**Trigger options:**
1. GSD milestone orchestrator calls `/doc:write` as a step in `complete-milestone.md`
2. A GSD phase's task list includes `/doc:write` as the final task
3. User manually invokes at milestone boundary

**Context available in GSD projects:**
- `.planning/PROJECT.md` — project description and requirements (maps to audience context)
- `.planning/ROADMAP.md` — feature list (maps to doc scope)
- CLAUDE.md — codebase context

GSD integration does not require changes to the GSD system — the plugin command reads whatever project files exist.

---

## Build Order (Dependencies)

### Phase 1: Core Infrastructure (must be first)
- Config schema and `doc-writer.config.json` format
- Setup command (`/doc:setup`) — creates config, enables everything else
- Skill files: diataxis, humanizer, quality-rules — referenced by agents

**Dependency note:** Nothing else works without config. Setup command must exist before agents can be tested.

### Phase 2: Doc Author Agent (depends on Phase 1)
- Author agent with universal quality rules baked in
- Diátaxis skill injection
- Basic orchestrator write command (stub — just invokes Author)

**Dependency note:** Author can be built and tested in isolation before Editor or Persona exist. Orchestrator command can be a minimal stub at this stage.

### Phase 3: Editor Agent (depends on Phase 2)
- Editor agent with review logic and humanizer pass
- Per-project custom_rules application
- Doc system rules application
- Orchestrator extended to run Author → Editor pipeline

**Dependency note:** Editor always needs Author's output. Cannot be tested in isolation (needs real draft to review).

### Phase 4: User Persona Agent (depends on Phase 3)
- User Persona agent with scenario generation
- Persona report format and verdict logic
- Full orchestrator pipeline (Author → Editor → Persona)
- Loop logic (NEEDS-REVISION triggers another Author pass)

**Dependency note:** Persona validates the full pipeline output. Must be last.

### Phase 5: Polish and Distribution (depends on Phase 4)
- Plugin packaging (README, manifest, marketplace format)
- GSD integration hooks (if milestone-boundary invocation is desired)
- Per-project config for multiple doc system presets
- Optional: Persona-first pipeline variant

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Monolithic Single-Agent
**What:** One agent that writes, reviews, and validates in a single pass.
**Why bad:** The perspective problem is structural. An agent cannot simultaneously be the author (builder's view) and the critic (user's view). This is why multi-agent architecture is chosen.
**Instead:** Enforce strict agent separation. Author does not review. Persona does not edit.

### Anti-Pattern 2: Agents Sharing Mutable State
**What:** Agents writing intermediate results to shared files mid-pipeline, with later agents reading those files.
**Why bad:** Fragile across invocation modes. Loses parallelization options. Hard to debug failures.
**Instead:** Orchestrator command passes output from one agent as direct input context to the next. Files are only written at pipeline completion.

### Anti-Pattern 3: Config Embedded in Agent Files
**What:** Audience, doc system settings, and custom rules hardcoded in agent .md files.
**Why bad:** Forces agent file edits per project. Prevents distribution as a generic plugin.
**Instead:** Universal rules live in agents; variable rules live in `doc-writer.config.json`. Agents receive config as runtime context.

### Anti-Pattern 4: Persona Receiving Source Internals
**What:** User Persona agent receiving full source code including internal implementation.
**Why bad:** Persona is simulating a user who only sees the public API. Access to internals allows it to explain gaps using internal knowledge, defeating the purpose.
**Instead:** Orchestrator filters source to public API surface before passing to Persona (public exports, type signatures, README — not private functions or internal modules).

### Anti-Pattern 5: Revision Loops Without Exit Conditions
**What:** Orchestrator automatically loops Author → Editor → Persona until PUBLISH-READY, indefinitely.
**Why bad:** Can loop forever on ambiguous content. Costs tokens. Removes user agency.
**Instead:** Surface NEEDS-REVISION verdict to user with gap list. User decides whether to loop or accept. Maximum one automatic retry if configured.

---

## Scalability Considerations

| Concern | At 1 doc | At 50 docs | At 500+ docs |
|---------|----------|------------|--------------|
| Agent context window | Trivial | May need scope limiting | Must process section by section, not whole-library |
| Config complexity | Simple | Add more custom_rules | Consider per-section rule overrides |
| Pipeline speed | Fast | Acceptable | Need parallel sub-pipelines per doc section |
| Review accuracy | High | High | Persona needs sampled testing, not exhaustive |

**Scoping recommendation:** Add `scope` parameter to `/doc:write` from day one. `--all`, `--file path/to/doc.md`, `--section api-reference`. Avoids context window issues and lets users target specific areas.

---

## Sources

- PROJECT.md — project requirements and constraints (direct read, HIGH confidence)
- CC plugin file structure — inferred from Glob inspection of `~/.claude/plugins/marketplaces/claude-plugins-official/` (paths confirmed, content not directly read, MEDIUM confidence)
- GSD system structure — inferred from Glob of `~/.claude/commands/gsd/` and `~/.claude/agents/` (paths confirmed, MEDIUM confidence)
- CC agent/command conventions — training knowledge, August 2025 cutoff (LOW-MEDIUM confidence — verify frontmatter syntax against current CC docs)
- Diátaxis framework — well-established, stable framework (HIGH confidence on framework concepts, not implementation)
- Multi-agent pipeline patterns — general software architecture + CC agent system patterns (MEDIUM confidence)
