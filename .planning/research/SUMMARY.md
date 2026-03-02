# Project Research Summary

**Project:** Doc Writer Agent (Claude Code multi-agent documentation plugin)
**Domain:** Multi-agent Claude Code plugin for library/package documentation
**Researched:** 2026-03-02
**Confidence:** MEDIUM

## Executive Summary

Doc Writer Agent is a Claude Code plugin that solves a fundamental problem with AI-generated documentation: docs written from the builder's perspective fail users. The recommended approach is a three-agent serial pipeline — Doc Author writes, Editor enforces quality rules, User Persona validates from the audience's perspective — coordinated by an orchestrator command that users invoke on demand. This mirrors how real technical writing teams work and creates the structural separation necessary to escape the "insider perspective" trap. The plugin requires no external dependencies beyond Claude Code itself; agent files in `.claude/` directories and CC's `Task` tool are the only primitives needed.

The core differentiator is the User Persona agent's ability to self-generate realistic user journeys from project context without requiring the maintainer to write test scenarios. Every other feature — diataxis-aware structure, humanizer prose, gap detection, doc-system formatting — is either table stakes or optimization on top of this perspective-shifted foundation. The MVP should prove the perspective shift works before adding complexity.

The primary risks are architectural, not technical. The two most dangerous: (1) the User Persona devolving into a checklist runner that provides false confidence without real user simulation, and (2) the revision loop having no exit condition, causing infinite token expenditure. Both must be designed in at the pipeline level before any agent logic is written. A third systemic risk is that web search was unavailable during research, meaning the Claude Code plugin architecture details (frontmatter conventions, marketplace format) carry MEDIUM confidence and should be verified against current Anthropic docs before Phase 1 decisions are finalized.

---

## Key Findings

### Recommended Stack

The plugin runs entirely within Claude Code's native plugin system. No external frameworks, runtimes, or package managers are required. Agent files are markdown files stored in `.claude/agents/` and commands in `.claude/commands/`; the `Task` tool is the multi-agent coordination primitive. Claude Opus 4.6 is the recommended model for all three agents given the quality-over-speed priority stated in PROJECT.md.

Documentation quality frameworks (Diátaxis, humanizer heuristics) are authoring methodologies baked into agent prompts — not versioned software dependencies. Per-project configuration lives in `doc-writer.config.json`, injected as runtime context rather than hardcoded into agent files. This is the design that makes the plugin generic and distributable.

**Core technologies:**
- Claude Code plugin system (`.claude/agents/*.md`, `.claude/commands/*.md`): runtime environment — no alternative considered
- Claude Opus 4.6: primary agent model — highest reasoning quality; appropriate for publication-quality writing
- `Task` tool: multi-agent coordination — CC-native, no external orchestration framework needed
- `doc-writer.config.json`: per-project configuration — separates variable rules from universal agent logic
- Diátaxis framework: authoring methodology baked into Doc Author prompt — industry standard since 2021
- Humanizer skill (`skills/humanizer/SKILL.md`): prose quality pass — prevents recognizable AI-pattern output

**What to avoid:** LangChain, AutoGen, CrewAI, MCP servers, vector databases, TypeDoc/pdoc (API ref generation), automated publishing, standalone Node/Python scripts. Each adds dependency and complexity that CC's native tooling makes unnecessary.

### Expected Features

Research confirms a clear priority stack. The MVP hypothesis: deliver the three-agent pipeline with universal quality rules and single-audience config. Validate the perspective shift is working before adding any of the v2 features.

**Must have (table stakes):**
- Diataxis-aware content structuring — industry standard; users expect correct doc type separation
- Working code examples with realistic context (not minimal-valid placeholders) — single most-complained-about gap in library docs
- Consistent page structure per doc type — users navigate by pattern; inconsistency forces re-learning
- Internal detail filtering — AI-generated docs routinely leak CI configs, dev scripts, test utilities
- Audience configuration persisted in project config — "developers" is not a usable audience definition
- Content-first, doc-system-agnostic output — plain markdown default; system-specific syntax only when configured
- On-demand invocation — no auto-triggers on commits; maintainer controls cadence
- Minimal-tweak publishability — the quality bar that drives the entire review pipeline

**Should have (differentiators):**
- Perspective-shifted User Persona with self-generated user journey scenarios — the core differentiator; no existing CC doc plugin does this
- Three-agent separation of concerns (Author / Editor / Persona) — prevents context contamination between roles
- Layered quality rules: universal (baked in, not bypassable) + project-specific (via config) + doc-system formatting
- Humanizer prose pass — output reads like a senior developer wrote it, not a language model
- Cross-file terminology consistency enforcement — "plugin" on one page, "extension" on another is a real problem at scale
- Gap detection (source-to-docs coverage analysis) — surfaces undocumented public APIs; requires source analysis capability

**Defer to v2+:**
- Two-audience mode (users vs contributors): additive complexity on single-audience; validate single-audience first
- GSD milestone integration: integration point, not core writing capability; add after standalone works well
- Extensible custom quality rules (user-defined DSL): universal rules cover most cases at launch
- Doc system formatting presets (mkdocs-material, Docusaurus, Sphinx, VitePress): add after content quality validated
- Persona-first pipeline variant (Persona sets criteria before Author writes): more rigorous but more complex
- Incremental mode (document only what changed): useful but requires scope design beyond MVP

### Architecture Approach

The plugin is an orchestrated pipeline: a single entry-point command (`/doc:write`) spawns three specialized agents in sequence using CC's `Task` tool. The orchestrator reads config, assembles filtered context, and routes output between agents. Agents are headless specialists — they receive structured input and produce structured output; they do not share mutable state. Files are only written to the doc root at pipeline completion, not mid-pipeline.

The build order is strictly dependency-driven: config schema and setup command must exist before any agent can be tested; Author must exist before Editor can review anything; Persona validates the full pipeline and must be built last. This is also the natural phase order for the roadmap.

**Major components:**
1. Entry command (`commands/write.md`) — orchestrator; reads config, assembles context, spawns agent pipeline, writes final output
2. Setup command (`commands/setup.md`) — first-run Q&A; populates `doc-writer.config.json`; idempotent
3. Doc Author agent (`agents/doc-author.md`) — writes draft docs using Diátaxis; applies universal quality rules; emits draft + self-assessment flags
4. Editor agent (`agents/doc-editor.md`) — reviews draft for quality, consistency, accuracy; applies humanizer pass + project custom rules + doc-system rules; emits revised docs + structured change log
5. User Persona agent (`agents/user-persona.md`) — generates 3-5 user journeys from project context; attempts goal completion using only the docs; emits per-scenario verdict (PASS/FAIL/PARTIAL) + gap list + final verdict (PUBLISH-READY / NEEDS-REVISION / MAJOR-GAPS)
6. Project config (`doc-writer.config.json`) — per-project audience, doc system, custom rules, paths; created by setup command; committed to version control
7. Skill files (`skills/diataxis/`, `skills/humanizer/`, `skills/quality-rules/`) — shared reference docs injected into agent prompts; passive reference material, not executable

### Critical Pitfalls

The six critical pitfalls identified by research, in priority order:

1. **Insider perspective never corrected** — Author defaults to implementation-first framing; User Persona must have explicit mandate to REJECT (not just annotate) docs requiring implicit source knowledge. "Can a user who has never read the source code follow this without confusion?" must be a binary test, not a suggestion.

2. **Infinite revision loop** — No exit condition means agents negotiate indefinitely; define max revision passes (2-3), distinguish BLOCKING vs SUGGESTION issues in a structured feedback format, escalate convergence failures to the user. This must be designed before the first end-to-end test run.

3. **User Persona devolves into checklist runner** — Applying criteria is not the same as simulating a user journey; Persona must generate concrete "I want to accomplish X" scenarios from project context (not from the docs themselves) and declare hard FAIL when a goal cannot be achieved. Scenarios should be saved and reused across runs.

4. **Context overload degrades output** — Passing raw source including test files, CI configs, and dev scripts causes internal details to leak into docs; orchestrator must filter to public API surface before passing to Author; Persona receives only public API surface and README, never internals.

5. **Loose natural language between agents breaks at scale** — Free-form prose feedback is ambiguous; define a structured format: severity (BLOCKING / SUGGESTION / NITPICK), location (page + section), description, fix. Author only responds to BLOCKING items in revision passes.

6. **Agent coordination via CC primitives needs validation** — The multi-pass review pipeline requires stateful handoffs; treat the filesystem as communication medium (draft passes through defined locations) and confirm CC's `Task` tool actually supports this pattern against current Anthropic docs.

---

## Implications for Roadmap

Based on research, the architecture's own build order provides the correct phase sequence. Each phase produces a testable, integrated artifact — not just components.

### Phase 1: Foundation and Setup
**Rationale:** Nothing else works without the config system. Agent prompts reference config; orchestrator reads it; User Persona behavior depends on audience definition. Config schema and setup command must be the first deliverable. This phase also defines the structured feedback format between agents — the communication contract that prevents Pitfalls 5 and 6.
**Delivers:** Working `/doc:setup` command that produces a valid `doc-writer.config.json`; defined feedback format schema; skill files for diataxis, humanizer, and quality rules; plugin file structure.
**Addresses:** Audience configuration (table stakes), content-first design principle, per-project config persistence.
**Avoids:** Pitfall 9 (config hell) by defining minimal schema with validation early; Pitfall 10 (vague audience) by requiring specificity fields and providing audience templates; Pitfall 6 (loose agent communication) by defining the structured feedback format before agents exist.
**Research flag:** MEDIUM confidence on CC plugin file format conventions — verify agent frontmatter syntax against current CC docs before committing to the format.

### Phase 2: Doc Author Agent
**Rationale:** The Author is the content generator that everything else depends on. It can be built and tested in isolation with a minimal orchestrator stub before Editor and Persona exist. This phase also proves the "insider perspective" prevention strategy works — the hardest authoring challenge.
**Delivers:** Working Doc Author agent that writes diataxis-structured, audience-calibrated, internal-detail-free library docs with working code examples; minimal orchestrator that invokes Author and writes output files; scope parameter (`--all`, `--file`, `--section`) designed from the start.
**Addresses:** Diataxis-aware structuring, working code examples, internal detail filtering, consistent page structure, minimal-tweak publishability (as a target bar).
**Avoids:** Pitfall 1 (insider perspective) by baking explicit perspective-test rules and user mental model context into Author prompt; Pitfall 7 (mechanical Diataxis application) by including type-mixing prohibition with concrete bad examples; Pitfall 13 (existing docs treated as ground truth) by explicitly instructing Author to extract facts but regenerate framing; Pitfall 14 (contrived code examples) by requiring realistic scenario context.
**Research flag:** Standard patterns — Diataxis framework is well-documented; no additional research needed.

### Phase 3: Editor Agent
**Rationale:** Editor can only be built and tested once Author produces real drafts. This phase completes the two-agent quality loop (Author + Editor) and produces output at a significantly higher quality bar than Author alone. The humanizer pass is implemented here.
**Delivers:** Working Editor agent that reviews Author drafts, applies humanizer pass, enforces project custom rules and doc-system formatting, and outputs structured change logs with BLOCKING / SUGGESTION / NITPICK classification; extended orchestrator running the full Author → Editor pipeline.
**Addresses:** Humanizer prose, cross-file terminology consistency, doc-system-agnostic output with optional system-specific formatting.
**Avoids:** Pitfall 3 (rules become the product) by including qualitative success criteria alongside mechanical rules; Pitfall 11 (tone inconsistency) by enforcing tone profile from project config; Pitfall 12 (doc-system syntax leaking) by defaulting to plain markdown and validating that system syntax only applies when configured.
**Research flag:** Standard patterns — editing pipeline and structured feedback formats are well-understood.

### Phase 4: User Persona Agent and Full Pipeline
**Rationale:** Persona validates the complete pipeline output and must be built last. This is the highest-risk agent — it's the core differentiator and the hardest to implement correctly. This phase also implements the pipeline loop logic (NEEDS-REVISION handling) and the exit conditions that prevent infinite loops.
**Delivers:** Working User Persona agent with genuine user journey simulation (3-5 concrete scenarios, goal-oriented testing, hard FAIL verdicts); full Author → Editor → Persona orchestrator with revision loop, max pass limit, convergence escalation; scenario persistence across runs.
**Addresses:** Perspective-shifted User Persona (the core differentiator), gap detection (partial — what Persona surfaces), minimal-tweak publishability (validated by Persona verdict).
**Avoids:** Pitfall 2 (infinite revision loop) by implementing max pass limit and BLOCKING-only revision triggers; Pitfall 5 (checklist runner) by implementing genuine goal-oriented scenario simulation with hard fail option; Pitfall 4 (context overload in Persona) by filtering to public API surface and README only.
**Research flag:** MEDIUM confidence — User Persona scenario generation at the depth required is novel; the implementation strategy (goal-oriented rather than criterion-based) should be tested early in the phase with real library docs before committing to the full design.

### Phase 5: Polish and Distribution
**Rationale:** Once the three-agent pipeline is validated against real library docs, address distribution, integration, and v2 differentiators. This phase transforms a working prototype into a distributable plugin.
**Delivers:** Plugin packaging for CC Marketplace / global `~/.claude/` install; GSD milestone integration hooks; per-project doc-system preset configurations (mkdocs-material, Docusaurus); `show active rules` command; README and installation docs.
**Addresses:** Distribution model, GSD integration (deferred feature), doc-system formatting presets (deferred feature), extensible custom rules UX improvements.
**Avoids:** Pitfall 8 (CC plugin architecture mismatches) — confirmed by Phase 1-4 implementation; Pitfall 15 (invocation too coarse-grained) — incremental/targeted modes can be added without breaking the established interface.
**Research flag:** MEDIUM confidence on CC Marketplace format — this was explicitly flagged as TBD in PROJECT.md. Needs research before Phase 5 begins.

### Phase Ordering Rationale

- Config-first ordering follows the hard architectural dependency: agents cannot function without knowing the audience, doc system, and quality rules they should apply.
- Author-before-Editor follows the serial pipeline dependency: Editor needs real drafts; cannot be tested with synthetic input without invalidating the review logic.
- Persona-last follows both the pipeline dependency (needs Editor output) and the risk management principle: the highest-risk, highest-value component is built last when the surrounding system is stable enough to test it properly.
- Distribution deferred to Phase 5 avoids premature packaging decisions before the plugin's interface is proven stable.

### Research Flags

Phases needing deeper research during planning:
- **Phase 1:** CC plugin frontmatter conventions — verify current syntax for agent files and command files against Anthropic's current documentation before implementing the file format.
- **Phase 4:** User Persona scenario generation depth — novel implementation; spike early in the phase to validate goal-oriented simulation approach before full build.
- **Phase 5:** CC Marketplace format — explicitly TBD per PROJECT.md; needs research before Phase 5 planning.

Phases with standard patterns (skip research-phase):
- **Phase 2:** Diataxis framework is well-documented and stable; no additional research needed.
- **Phase 3:** Editing pipeline, humanizer pass, and structured feedback formats are well-understood patterns.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | CC plugin file format and Task tool coordination confirmed via GSD system inspection; CC Marketplace format TBD; web search unavailable |
| Features | MEDIUM | Diataxis, Write the Docs, and documentation tooling knowledge stable and pre-cutoff; competitive landscape (post-Aug 2025 AI doc tools) not covered |
| Architecture | MEDIUM | Pipeline pattern confirmed from GSD system inspection; CC agent frontmatter conventions need verification against current docs; multi-agent coordination primitives well-established |
| Pitfalls | HIGH | Insider perspective bias, LLM context overload, revision loop failure modes, and Diataxis misapplication are well-documented and directly observed failure modes; CC-specific constraints are MEDIUM |

**Overall confidence:** MEDIUM — The architectural approach and feature decisions are well-grounded. The specific CC plugin API surface (frontmatter syntax, marketplace format, Task tool exact behavior) carries MEDIUM confidence and should be verified before Phase 1 design decisions are locked.

### Gaps to Address

- **CC Plugin frontmatter conventions:** Verify `name`, `description`, `tools` fields in agent `.md` files against current Anthropic Claude Code documentation before Phase 1. The GSD system inspection provides a working pattern but may not reflect the current spec.
- **CC Marketplace distribution format:** Explicitly TBD per PROJECT.md. Research needed before Phase 5. For Phases 1-4, target the global `~/.claude/` manual install pattern which is confirmed.
- **Competitive landscape (post-Aug 2025):** Web search was unavailable during research. Recommend a search for "AI documentation generation tools 2026" before finalizing the roadmap to identify whether the core differentiators (User Persona, perspective shift) have been addressed by new entrants.
- **Gap detection implementation:** FEATURES.md marks this as HIGH complexity and deferred. Requires source analysis capability assessment — specifically, how to compare public API surface against documented surface at scale. Needs phase-specific research when it surfaces in the roadmap.
- **Context window limits at scale:** ARCHITECTURE.md identifies that 50+ docs require scope limiting. The `scope` parameter design should be defined in Phase 1 even if only tested in Phase 2, to avoid interface breaking changes later.

---

## Sources

### Primary (HIGH confidence)
- PROJECT.md — authoritative project requirements, constraints, and scope decisions; read directly
- GSD system inspection (`.claude/agents/*.md`, `~/.claude/commands/gsd/`) — confirmed CC plugin file format convention and Task tool coordination pattern
- Diátaxis framework (Daniele Procida, 2021) — well-established framework; stable authoring methodology

### Secondary (MEDIUM confidence)
- Training knowledge (cutoff August 2025) — Claude Code CLI architecture, CLAUDE.md convention, mkdocs-material and Docusaurus feature sets, multi-agent pipeline patterns, LLM context overload behavior
- CC plugin structure — inferred from Glob inspection of `~/.claude/plugins/marketplaces/claude-plugins-official/` (paths confirmed, content not directly read)

### Tertiary (LOW-MEDIUM confidence; verify before use)
- CC agent frontmatter syntax — training knowledge; may have evolved since August 2025 cutoff
- CC Marketplace distribution format — TBD; not documented in available sources
- Post-Aug 2025 AI documentation tool landscape — not covered; web search was unavailable

---
*Research completed: 2026-03-02*
*Ready for roadmap: yes*
