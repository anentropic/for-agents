# Phase 9: Enhanced Setup Q&A, Tone, User Persona, and Researcher Agent - Research

**Researched:** 2026-03-17
**Domain:** Setup skill enhancement, researcher agent, context enrichment pipeline
**Confidence:** HIGH

## Summary

Phase 9 enhances the existing doc-writer setup skill by converting freeform audience questions into infer+suggest AskUserQuestion interactions, adding tone selection, adding user persona task Q&A, adding framework-specific follow-up questions, and creating a researcher agent that enriches all setup inputs into a persisted `.doc-writer/context.md` file. All three downstream agents (Author, Editor, Persona) will read `context.md` at run start alongside `config.yaml`.

The work is purely prompt engineering and YAML/markdown file authoring within the existing Claude Code plugin system. No new runtime dependencies, no new tools, no new scripts. The existing AskUserQuestion pattern from Phase 8 (with mandatory trailing options) is the foundation for all new interactive questions. The researcher agent is a new `.md` agent file in `doc-writer/agents/` that reads config + codebase and produces `context.md`.

**Primary recommendation:** Decompose into four logical plans: (1) config schema + tone + researcher agent definition, (2) setup skill Q&A enhancements (infer+suggest audience fields, tone question, user persona tasks), (3) framework Q&A question sets + setup integration, (4) downstream agent updates to read context.md.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Setup Q&A: infer+suggest pattern**
- Every audience sub-field becomes its own AskUserQuestion (not a single freeform block)
- Researcher infers 2-4 suggestions per field using README, dependencies, and code patterns; one marked Recommended
- Fields that get infer+suggest: skill level, assumed knowledge, never-assume, domain context
- Fields that stay freeform: audience name, discovery story (too specific to infer)
- Assumed knowledge and never-assume use `multiSelect: true` -- researcher infers 3-5 likely items as checkboxes; user picks, deselects, or adds via Other
- All setup AskUserQuestion blocks follow the Phase 8 mandatory trailing options pattern: "Type something else" (before divider) + "Chat about this" (final option)

**Tone field**
- Three options (no library name references in labels):
  - "Just the facts" -- minimal, no preamble, direct definitions, one example max. Like NumPy docs.
  - "Helpful and comprehensive, warm but businesslike" -- clear explanations, multiple examples, structured. Like Django docs.
  - "Helpful and comprehensive, with personality and occasional humour" -- same depth as above but with personality. Like FastAPI docs.
- Each option has a one-line description explaining what it means in practice
- Tone question uses the mandatory trailing options pattern: "Type something else" + "Chat about this"
- Researcher expands chosen tone into concrete writing rules stored in `context.md`
- Tone lives in `config.yaml` as a label; the expanded rules live in `context.md`

**User persona task Q&A**
- Added within the audience definition flow, after skill level and assumed knowledge questions
- Researcher infers 3-5 likely user tasks from the codebase
- Presented as `multiSelect: true` AskUserQuestion -- user picks, deselects, or adds via Other
- Follows the mandatory trailing options pattern
- Tasks become part of the audience profile in `context.md`

**Framework Q&A**
- After doc system selection, researcher scans the framework config file and auto-answers what it can detect
- Framework-specific question sets are pre-authored (not dynamic runtime research)
- Questions cover important usage-preference choices that can't be inferred from config alone
- Both mkdocs-material and plain-markdown get question sets in Phase 9
- Framework Q&A follows the mandatory trailing options pattern
- mkdocs-material reference config: `../cookiecutter-python-uv-library/{{ cookiecutter.project_slug }}/mkdocs.yml`

**Researcher agent**
- Runs automatically at the end of `/doc-writer:setup` (and `--reset`)
- Also re-triggerable via `/doc-writer:setup --refresh-context` -- re-runs researcher only, skips Q&A
- Reads: config.yaml (audiences, tone, doc system) + codebase (README, source files, framework config)
- Produces: `.doc-writer/context.md` -- persisted, user-editable
- All agents (Author, Editor, Persona) read `context.md` at the start of each run. Graceful fallback if file missing.

**context.md contents**
- Audience-expanded instructions
- Project domain summary
- Tone-specific writing rules
- Framework usage preferences

### Claude's Discretion
- Exact structure and headings of `context.md`
- Whether to split context.md into multiple files (universal vs agent-specific)
- Which specific questions to include in the plain-markdown question set
- How the researcher handles projects with no README or minimal codebase signals
- Re-run update behaviour for context.md (overwrite vs merge with user edits)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

## Standard Stack

### Core

This phase involves no external libraries. All work is prompt engineering within the existing Claude Code plugin framework.

| Asset | Type | Purpose | Why Standard |
|-------|------|---------|--------------|
| AskUserQuestion | CC tool | Structured user interaction | Built into all skill/agent contexts |
| Agent tool | CC tool | Spawning researcher agent | Used by write, review, edit skills already |
| Read/Write/Glob/Grep/Bash | CC tools | Codebase scanning by researcher | Standard tool set for agents |
| YAML config | Data format | `config.yaml` schema | Already established in Phase 1 |
| Markdown | Data format | `context.md`, agent prompts, guidance files | Universal project format |

### Supporting

| Asset | Location | Purpose | When to Use |
|-------|----------|---------|-------------|
| config-template.yaml | `doc-writer/skills/setup/defaults/` | Config schema template | Extend with `tone` field |
| detect-project.sh | `doc-writer/skills/setup/scripts/` | Auto-detection at setup start | Feeds researcher inference suggestions |
| mkdocs-material.md | `doc-writer/skills/setup/defaults/` | MkDocs guidance file | Extend with framework Q&A answers |
| plain-markdown.md | `doc-writer/skills/setup/defaults/` | Plain MD guidance file | Extend with framework Q&A answers |
| cookiecutter mkdocs.yml | External reference | Default mkdocs-material preferences | Baseline for framework Q&A defaults |

## Architecture Patterns

### Recommended File Structure (New and Modified Files)

```
doc-writer/
  agents/
    doc-author.md          # MODIFY: add context.md reading
    doc-editor.md          # MODIFY: add context.md reading
    doc-persona.md         # MODIFY: add context.md reading
    doc-researcher.md      # NEW: researcher agent definition
  skills/
    setup/
      SKILL.md             # MODIFY: infer+suggest Q&A, tone, persona tasks, framework Q&A, --refresh-context, researcher invocation
      defaults/
        config-template.yaml  # MODIFY: add tone field
        mkdocs-material.md    # NO CHANGE (guidance stays static; framework preferences go to context.md)
        plain-markdown.md     # NO CHANGE (same reasoning)

.doc-writer/               # Per-project output (created at runtime)
  config.yaml              # MODIFY: now includes tone field
  context.md               # NEW: researcher output, persisted, user-editable
```

### Pattern 1: Infer+Suggest AskUserQuestion

**What:** For each audience sub-field (skill_level, assumed_knowledge, never_assume, domain_context), the setup skill first runs codebase inference to generate 2-4 suggestions, then presents them via AskUserQuestion with one marked "Recommended". User picks, modifies, or enters freeform.

**When to use:** For fields where the codebase provides meaningful signal (dependencies, README content, code patterns) but the user has final authority.

**Example flow for skill_level:**
```
# Setup skill detects: Python library, README mentions "advanced usage patterns",
# dependencies include typing-extensions, mypy

AskUserQuestion:
  header: "Skill level"
  question: "What skill level should docs target? Based on your README and code patterns:"
  options:
    - { label: "Intermediate (Recommended)", description: "Knows Python basics, familiar with pip and virtual environments" }
    - { label: "Advanced", description: "Expects type hints, async patterns, and advanced Python idioms" }
    - { label: "Beginner", description: "New to Python, needs everything explained" }
    - { label: "Type something else", description: "Describe a different skill level" }
    - { label: "Chat about this", description: "Discuss what skill levels mean for docs" }
```

**Example flow for assumed_knowledge (multiSelect):**
```
AskUserQuestion:
  header: "Assumed"
  question: "What can this audience be assumed to already know?"
  multiSelect: true
  options:
    - { label: "Python basics (Recommended)", description: "Variables, functions, classes, imports" }
    - { label: "pip and virtual environments", description: "Package installation and environment management" }
    - { label: "REST APIs", description: "HTTP methods, status codes, request/response patterns" }
    - { label: "Type hints", description: "Python typing module, type annotations" }
    - { label: "Type something else", description: "Add a different knowledge area" }
    - { label: "Chat about this", description: "Discuss what assumed knowledge means" }
```

### Pattern 2: Researcher Agent as Post-Setup Enrichment

**What:** The researcher is a separate agent (not inline in the setup skill) that runs after Q&A completes. It reads the populated `config.yaml` + codebase and produces `context.md`.

**When to use:** Always -- invoked at the end of setup, reset, or via `--refresh-context`.

**Why a separate agent, not inline logic:** The researcher needs to do substantive codebase analysis (read source files, README, framework config, infer domain patterns). This is too complex for inline setup skill instructions and benefits from focused agent context. The setup skill uses the Agent tool to spawn it, same pattern as write/review/edit spawning Author/Editor/Persona.

**Agent invocation pattern:**
```
# In setup SKILL.md, after Step 3 (File Creation):
# Step 4: Context Enrichment

Use the Agent tool to spawn `doc-researcher` with this message:

> Enrich the project configuration. Read `.doc-writer/config.yaml` for audiences,
> tone, and doc system. Scan the codebase (README, source files, framework config)
> and produce `.doc-writer/context.md` with expanded audience guidance, project
> domain summary, tone-specific writing rules, and framework usage preferences.
```

### Pattern 3: --refresh-context as a Re-Run Branch

**What:** When `$ARGUMENTS` contains `--refresh-context`, the setup skill skips all Q&A and jumps directly to the researcher invocation step.

**When to use:** After library changes, or when the user has edited config.yaml manually and wants context.md regenerated.

**Integration into Step 1 (Re-Run Detection):**
```
# Add as a new check before existing re-run logic:

If $ARGUMENTS contains --refresh-context:
  1. Verify .doc-writer/config.yaml exists (if not, tell user to run setup first)
  2. Skip to Step 4 (Context Enrichment) -- spawn researcher
  3. Stop after researcher completes
```

### Pattern 4: Downstream Agent Context Reading

**What:** Each agent (Author, Editor, Persona) adds a step to read `.doc-writer/context.md` at startup, alongside the existing config.yaml reading.

**When to use:** Every agent run. Graceful fallback if file missing.

**Example (added to each agent's Step 1: Read Configuration):**
```
4. **`.doc-writer/context.md`** -- If this file exists, load it. It contains
   expanded audience guidance, project domain summary, tone-specific writing
   rules, and framework usage preferences produced by the researcher agent.
   Apply these enrichments alongside config.yaml values. If the file does not
   exist, proceed with config.yaml values only -- all context.md content is
   enhancement, not required.
```

### Anti-Patterns to Avoid

- **Embedding researcher logic in setup SKILL.md:** The setup skill is already long. Keep it as an orchestrator that spawns the researcher agent. Do not inline codebase analysis logic in setup.
- **Making context.md required:** All agents must gracefully degrade if context.md is missing. It is an enrichment, not a dependency.
- **Storing expanded content in config.yaml:** Config stays lean (labels, selections, arrays). Expanded prose and writing rules go to context.md.
- **Dynamic framework Q&A at runtime:** Question sets are pre-authored as part of this phase. The setup skill presents them statically, not via runtime research.
- **Modifying guidance files (mkdocs-material.md, plain-markdown.md) with framework Q&A answers:** Guidance files are static defaults shipped with the plugin. Framework preferences from Q&A go to context.md.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structured user choices | Custom prompts with "enter 1, 2, or 3" | AskUserQuestion tool | Phase 8 established this; consistency matters |
| Codebase inference for suggestions | Inline bash commands in setup skill | Researcher agent with full tool access | Complex analysis needs focused agent context |
| Framework config parsing | Custom shell scripts | Agent's Read + Grep tools | Agents can natively parse YAML/JSON/TOML |
| Tone expansion to writing rules | Manual per-tone blocks in setup | Researcher agent generates from tone label | Keeps setup lean; researcher has project context |

**Key insight:** The setup skill should remain an orchestrator (collect answers, create files, spawn researcher). All intelligence about inferring suggestions and expanding config into context belongs in the researcher agent.

## Common Pitfalls

### Pitfall 1: AskUserQuestion Header Length Overflow

**What goes wrong:** Headers exceed the 12-character hard limit, causing validation rejection.
**Why it happens:** Descriptive headers like "Skill Level" (11 chars) are fine, but "Assumed Know" or "Never Assume" (12 chars) are at the boundary.
**How to avoid:** Pre-validate every header in the plan. Use short forms: "Skill level" (11), "Assumed" (7), "Never" (5), "Domain" (6), "Tasks" (5), "Tone" (4), "Framework" (9).
**Warning signs:** Any header approaching 12 characters.

### Pitfall 2: Breaking the freeform_rule on "Type something else"

**What goes wrong:** After user selects "Type something else", the skill responds with another AskUserQuestion instead of plain text.
**Why it happens:** The infer+suggest pattern tempts the developer to present re-inferred options after freeform input.
**How to avoid:** Strict rule: "Type something else" or any freeform input always drops to plain-text follow-up. Only resume AskUserQuestion after processing the freeform response.
**Warning signs:** Any flow where AskUserQuestion follows immediately after a freeform selection.

### Pitfall 3: Researcher Agent Context Overload

**What goes wrong:** The researcher tries to read the entire codebase and runs out of context or produces overly verbose context.md.
**Why it happens:** The agent definition doesn't scope what to read.
**How to avoid:** Be explicit in the agent definition about what to scan: README, package manifest (pyproject.toml/package.json/Cargo.toml), framework config file, top-level source directory listing, and sample of public API signatures. Do NOT read test files, CI config, or deep implementation files.
**Warning signs:** context.md exceeding ~200 lines or containing implementation details.

### Pitfall 4: Config Schema Migration

**What goes wrong:** Adding `tone` to config.yaml breaks existing configs that lack the field.
**Why it happens:** No migration path for the schema change.
**How to avoid:** The `tone` field must be optional with a sensible default. Config-reading code in all agents must handle missing `tone` gracefully (default to the middle option: "Helpful and comprehensive, warm but businesslike"). The config-template.yaml adds the field with a default.
**Warning signs:** Any code that reads `config.tone` without a fallback.

### Pitfall 5: Framework Q&A Ordering in Setup Flow

**What goes wrong:** Framework Q&A runs before doc system selection is complete, or runs for the wrong doc system.
**Why it happens:** Setup flow is multi-step; inserting framework Q&A at the wrong point breaks the sequence.
**How to avoid:** Framework Q&A runs immediately after doc system selection (Step 2b) and before paths (Step 2c). The doc_system value is already known at this point. Only show questions for the selected doc system.
**Warning signs:** Framework Q&A appearing before the user has selected their doc system.

### Pitfall 6: Researcher Invocation on --reset

**What goes wrong:** `--reset` runs the full Q&A but forgets to invoke the researcher at the end.
**Why it happens:** The researcher invocation is a new step that needs to be added to the reset flow, not just the first-time flow.
**How to avoid:** Researcher invocation goes in Step 4 (after file creation), which both first-time and --reset flows converge on. Add an explicit note that both paths end at Step 4.
**Warning signs:** Reset completing without producing context.md.

## Code Examples

### config-template.yaml with tone field

```yaml
# Source: extending existing doc-writer/skills/setup/defaults/config-template.yaml
# .doc-writer/config.yaml -- generated by /doc-writer:setup
version: 1

audiences:
  - name: ""
    skill_level: ""
    assumed_knowledge: []
    never_assume: []
    domain_context: ""
    discovery_story: ""
    user_tasks: []

tone: ""

doc_system: ""
api_reference: ""

paths:
  docs_root: "docs/"
  source_root: "src/"

detected:
  language: ""
  doc_system: ""
  existing_docs: false
```

### Researcher Agent Frontmatter Pattern

```yaml
# Source: follows existing agent pattern from doc-author.md, doc-editor.md, doc-persona.md
---
name: doc-researcher
description: Enriches setup configuration into expanded context for downstream agents. Produces .doc-writer/context.md from config.yaml and codebase analysis.
tools: Read, Write, Glob, Grep, Bash
model: inherit
---
```

Note: The researcher does NOT list skills (quality-rules, diataxis) because it does not write or edit documentation. It reads the codebase and config to produce context for agents that do.

### context.md Recommended Structure

```markdown
# Doc Writer Context

**Generated:** {date}
**Source:** /doc-writer:setup researcher
**Editable:** Yes -- manual edits are preserved on --refresh-context unless structure changes

## Project Summary

{2-3 sentences: what the library does, who it's for, key capabilities}
{Inferred from: README, package manifest, public API surface}

## Audience: {audience name}

### Profile
- **Skill level:** {level}
- **What they know:** {expanded from assumed_knowledge -- concrete, specific}
- **What to always explain:** {expanded from never_assume -- concrete, specific}
- **Their world:** {expanded from domain_context -- what problems they face, what tools they use}
- **How they found this library:** {expanded from discovery_story}

### Common Tasks
{From user_tasks selections:}
- {task 1}: {brief context on what this involves}
- {task 2}: {brief context}

### Writing Guidance for This Audience
{Concrete instructions for agents:}
- When explaining {concept}, assume they already know {X} but spell out {Y}
- Use {vocabulary level} terminology
- Examples should show {real-world scenario relevant to this audience}

## Tone: {tone label}

### Writing Rules
{Concrete, actionable rules derived from the chosen tone:}

{For "Just the facts":}
- No motivational introductions or "why you should care" sections
- Skip background and history sections
- Lead with the function signature or command, then one sentence of what it does
- One code example maximum per concept
- No transition sentences between sections ("Now let's look at...")
- Admonitions only for warnings and breaking changes, never for tips or best practices

{For "Helpful and comprehensive, warm but businesslike":}
- Brief (1-2 sentence) introduction explaining what the page covers and why
- Multiple examples per concept: basic usage, then common variations
- Include "Common Mistakes" or "Troubleshooting" sections where relevant
- Transition sentences between major sections for reading flow
- Use admonitions for tips, warnings, and important notes
- Warm but professional -- no jokes, no first person, no casual asides

{For "Helpful and comprehensive, with personality and occasional humour":}
- Same depth and structure as "warm but businesslike"
- Occasional light humor in admonitions or transitions (not in code examples or critical instructions)
- Can use first person sparingly ("We'll start by...")
- Personality in analogies and explanations, not in API descriptions
- Never sacrifice clarity for humor -- if the joke obscures the point, cut it

## Framework Preferences: {doc_system}

{For mkdocs-material:}
### Navigation
- {e.g., 2-level nav with navigation.sections, no navigation.tabs}
- {literate-nav with SUMMARY.md or manual nav}

### Features to Use
- Content tabs for multi-language/multi-method examples
- Mermaid diagrams for architecture and flow visualization
- Code annotations for complex examples
- Admonitions with collapsible details for optional/advanced content
- mkdocstrings for API reference (Google docstring style)

### Features NOT to Use
- {e.g., Blog plugin, versioning with mike -- per user config}

{For plain-markdown:}
### Conventions
- {Blockquote callouts with bold labels}
- {Relative links between pages}
- {etc.}
```

### Setup Skill: --refresh-context Branch (Step 1 Addition)

```markdown
# Added to Step 1: Re-Run Detection, as the FIRST check

5. **If `$ARGUMENTS` contains `--refresh-context`:**
   - Use Glob to check if `.doc-writer/config.yaml` exists.
   - **If exists:** Skip all Q&A. Jump directly to Step 4 (Context Enrichment).
   - **If does not exist:** Tell the user: "No configuration found. Run `/doc-writer:setup` first." Stop.
```

### Setup Skill: Tone Selection (New Step 2a.5)

```markdown
#### 2a.5: Tone Selection

After audience definition is complete (all audiences collected), present tone selection.

Use AskUserQuestion:
- header: "Tone"
- question: "What writing tone should the documentation use?"
- options:
  - { label: "Just the facts", description: "Minimal, no preamble, direct definitions, one example max" }
  - { label: "Warm but businesslike", description: "Clear explanations, multiple examples, structured and approachable" }
  - { label: "With personality", description: "Same depth, but with personality and occasional humour" }
  - { label: "Type something else", description: "Describe a different tone" }
  - { label: "Chat about this", description: "See examples of each tone style" }

- **"Just the facts":** Record tone as "just-the-facts"
- **"Warm but businesslike":** Record tone as "warm-businesslike"
- **"With personality":** Record tone as "personality"
- **"Type something else":** Ask in plain text what tone they want. Record their description as a custom tone label.
- **"Chat about this":** Show example paragraphs in each tone for the same concept. After discussion, re-present the question.
```

### Framework Q&A: mkdocs-material Question Set

```markdown
#### 2b.5: Framework Configuration (mkdocs-material)

If doc_system is mkdocs-material, scan for mkdocs.yml and auto-detect what is possible.
Then present questions for preferences that cannot be inferred:

**Question 1: Navigation style**
Use AskUserQuestion:
- header: "Navigation"
- question: "How should documentation be organized? {Detected: navigation.sections enabled}"
- options:
  - { label: "Sections (Recommended)", description: "2-level nav: sections group related pages" }
  - { label: "Tabs + sections", description: "Top-level tabs with sections underneath" }
  - { label: "Flat", description: "All pages at one level, no grouping" }
  - { label: "Type something else", description: "Describe a different nav structure" }
  - { label: "Chat about this", description: "Discuss navigation options" }

**Question 2: API reference approach**
Use AskUserQuestion:
- header: "API docs"
- question: "How is API reference generated? {Detected: mkdocstrings with Google docstring style}"
- options:
  - { label: "mkdocstrings (Recommended)", description: "Auto-generated from docstrings, Google style" }
  - { label: "Manual reference pages", description: "Hand-written API reference in docs/" }
  - { label: "None", description: "No API reference -- narrative docs only" }
  - { label: "Type something else", description: "Describe a different approach" }
  - { label: "Chat about this", description: "Discuss API reference options" }

**Question 3: Rich features usage**
Use AskUserQuestion:
- header: "Features"
- question: "Which features should docs use? {Detected: admonitions, content tabs, Mermaid, code annotations}"
- multiSelect: true
- options:
  - { label: "Content tabs", description: "For multi-language or multi-method examples" }
  - { label: "Mermaid diagrams", description: "For architecture and flow diagrams" }
  - { label: "Code annotations", description: "Numbered annotations explaining code lines" }
  - { label: "Admonitions", description: "Tip/warning/info callout boxes" }
  - { label: "Collapsible details", description: "Expandable sections for optional content" }
  - { label: "Type something else", description: "Add or remove features" }
  - { label: "Chat about this", description: "See examples of each feature" }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Freeform audience input | Infer+suggest AskUserQuestion | Phase 9 | Better defaults, less user typing, more consistent configs |
| No tone control | Three-tier tone selection | Phase 9 | Agents adapt writing style; docs match project personality |
| Agents re-infer project context each run | Persisted context.md read at start | Phase 9 | Faster runs, consistent context, user-editable enrichment |
| No framework-specific preferences | Framework Q&A captures usage choices | Phase 9 | Agents know which features to use/avoid |
| Single config.yaml for all context | config.yaml (lean) + context.md (rich) | Phase 9 | Separation of data (config) from derived intelligence (context) |

## Open Questions

1. **context.md Re-Run Update Strategy**
   - What we know: `--refresh-context` re-runs the researcher. User may have manually edited context.md.
   - What's unclear: Should the researcher overwrite entirely or attempt to merge?
   - Recommendation: Overwrite entirely. Add a header comment: "This file is regenerated by the researcher agent. Manual edits will be preserved until the next --refresh-context run. To make permanent changes, edit config.yaml and re-run." This is simpler and more predictable than merge logic. If the user has permanent preferences, they go in config.yaml or rules.md.

2. **context.md File Splitting**
   - What we know: CONTEXT.md marks this as Claude's discretion.
   - What's unclear: Whether framework preferences should be in a separate file from audience guidance.
   - Recommendation: Single context.md for Phase 9. All three agents read the whole file. Splitting adds complexity with marginal benefit -- the file should be under 200 lines for any project. Revisit if context.md grows beyond 300 lines in practice.

3. **Plain-Markdown Framework Question Set**
   - What we know: Plain-markdown needs a question set. The guidance file covers basic structure, code blocks, links, emphasis, lists, tables, callouts.
   - What's unclear: Which usage preferences are worth asking about for plain-markdown (fewer knobs than mkdocs-material).
   - Recommendation: Ask about: (a) callout style (blockquote vs none), (b) heading case convention (title case vs sentence case), (c) table of contents approach (manual index.md vs filename-based). Keep it to 2-3 questions -- plain-markdown users chose simplicity.

4. **No README / Minimal Codebase Signals**
   - What we know: Researcher needs to handle projects with no README or sparse code.
   - What's unclear: How degraded should the inference be?
   - Recommendation: The researcher should have explicit fallback logic: if no README, note "No README found -- using package manifest and source code for inference." If no source code signals, use the audience answers themselves as the primary context source. context.md should always be generated, even if sparse, so downstream agents have a consistent file to check.

5. **user_tasks Field in config.yaml**
   - What we know: User persona tasks are selected during setup via AskUserQuestion.
   - What's unclear: Should tasks persist in config.yaml alongside audience data or only in context.md?
   - Recommendation: Store in config.yaml as `user_tasks: []` array on each audience entry. This keeps the config as the source of truth for user selections, with context.md containing the expanded/enriched version.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | BATS (Bash Automated Testing System) |
| Config file | None -- BATS uses convention-based test files |
| Quick run command | `bats tests/phase-09-validation.bats` |
| Full suite command | `bats tests/` |

### Phase Requirements -> Test Map

Phase 9 has no formal requirement IDs (all v1 requirements are already complete). Testing validates the structural changes:

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P9-01 | config-template.yaml has tone field | unit | `bats tests/phase-09-validation.bats -f "tone field"` | No -- Wave 0 |
| P9-02 | config-template.yaml has user_tasks field on audience | unit | `bats tests/phase-09-validation.bats -f "user_tasks"` | No -- Wave 0 |
| P9-03 | doc-researcher.md agent exists | unit | `bats tests/phase-09-validation.bats -f "researcher agent"` | No -- Wave 0 |
| P9-04 | doc-researcher.md has correct frontmatter | unit | `bats tests/phase-09-validation.bats -f "researcher frontmatter"` | No -- Wave 0 |
| P9-05 | setup SKILL.md mentions --refresh-context | unit | `bats tests/phase-09-validation.bats -f "refresh-context"` | No -- Wave 0 |
| P9-06 | setup SKILL.md has tone selection step | unit | `bats tests/phase-09-validation.bats -f "tone selection"` | No -- Wave 0 |
| P9-07 | doc-author.md reads context.md | unit | `bats tests/phase-09-validation.bats -f "author context"` | No -- Wave 0 |
| P9-08 | doc-editor.md reads context.md | unit | `bats tests/phase-09-validation.bats -f "editor context"` | No -- Wave 0 |
| P9-09 | doc-persona.md reads context.md | unit | `bats tests/phase-09-validation.bats -f "persona context"` | No -- Wave 0 |
| P9-10 | setup SKILL.md has framework Q&A step | unit | `bats tests/phase-09-validation.bats -f "framework Q&A"` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `bats tests/phase-09-validation.bats`
- **Per wave merge:** `bats tests/`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/phase-09-validation.bats` -- all P9-XX tests
- [ ] BATS framework already installed (used in Phase 1 and Phase 7 validation)

## Sources

### Primary (HIGH confidence)
- Existing codebase files: setup SKILL.md, config-template.yaml, all three agent .md files, guidance files, detect-project.sh
- Phase 8 CONTEXT.md: established the mandatory trailing options pattern
- Phase 9 CONTEXT.md: locked decisions for all implementation choices
- questioning.md: AskUserQuestion usage guide and freeform_rule
- Cookiecutter mkdocs.yml: mkdocs-material reference configuration

### Secondary (MEDIUM confidence)
- context.md structure recommendation: based on established patterns in config.yaml + guidance files, extrapolated to expanded context format

### Tertiary (LOW confidence)
- None -- all findings are directly sourced from existing codebase files and locked decisions

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies; all tools already available in the plugin system
- Architecture: HIGH -- patterns follow established precedent from Phases 1-8 (agent spawning, config reading, AskUserQuestion)
- Pitfalls: HIGH -- derived from direct analysis of current code and Phase 8 patterns
- context.md structure: MEDIUM -- recommended structure is author's discretion; will need validation during implementation

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stable -- no external dependencies that change rapidly)
