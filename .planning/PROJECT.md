# Doc Writer Agent

## What This Is

A Claude Code plugin (multi-agent team) that writes and reviews library/package documentation to publication quality. Three specialized agents — Author, Editor, and User Persona — collaborate to produce docs that solve the fundamental problem: the agent that built a feature has too much insider context to document it well for users.

## Core Value

Produce library documentation that a maintainer can publish with minimal tweaks — docs written from the user's perspective, not the builder's.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Three-agent architecture: Doc Author, Editor, User Persona
- [ ] Doc Author writes content guided by diataxis framework and quality rules
- [ ] Editor reviews for consistency, gaps, accuracy, and applies humanizer
- [ ] User Persona reviews from target audience perspective with self-generated test scenarios
- [ ] Layered quality rules: universal defaults baked into agents + project-specific overrides in config
- [ ] Universal rule: no internal/maintainer details (test utils, dev scripts, CI config, justfile recipes)
- [ ] Universal rule: every feature/API must include a working code example
- [ ] Universal rule: consistent structure for same-type pages (same template)
- [ ] Universal rule: all inline `code` mentions linked to relevant API Reference item
- [ ] Per-project audience configuration via setup Q&A (remembered across sessions)
- [ ] Default audience guidance for single-audience and two-audience (users vs contributors) scenarios
- [ ] User Persona generates test scenarios from project context without manual authoring
- [ ] Content-first output — doc-system-agnostic with optional system-specific rules
- [ ] Works as standalone CC plugin (invokable by any CC user)
- [ ] Works as GSD integration (invokable at milestone boundaries)
- [ ] On-demand invocation (user triggers when they want)
- [ ] Agent input: source code + existing docs + project context (everything available)
- [ ] Extensible quality rules — user can add custom rules to project config
- [ ] Per-project config for doc system specifics (mkdocs-material, docusaurus, etc.)

### Out of Scope

- Auto-generating API reference from code (tools like typedoc/pydoc handle this) — focus is on narrative docs
- Doc site hosting or deployment — this writes content, not infrastructure
- Non-library docs (blog posts, marketing pages, internal wikis) — scoped to library/package documentation
- Automated publishing — the maintainer decides when to publish

## Context

- Built to solve a specific pain observed across multiple GSD projects: AI-generated docs read like maintainer notes rather than user documentation
- The perspective problem is structural — agents that build features document from the builder's viewpoint, including irrelevant internal details and missing the user's mental model
- Existing CC skills (diataxis-documentation, humanizer) help with tone and structure individually but don't solve the perspective or consistency problems
- The multi-agent approach separates concerns: writing, quality enforcement, and audience validation
- Distribution target is CC marketplace plugin (exact format TBD from research)
- Primary test environment: mkdocs-material projects, but designed to be doc-system-agnostic

## Constraints

- **Platform**: Claude Code plugin — must work within CC's agent/skill system
- **Dependencies**: Builds on existing diataxis-documentation and humanizer skills (or incorporates their guidance)
- **Quality bar**: Docs should need only minimal manual tweaks before publishing — structure and content must be solid
- **Agent workflow**: Pipeline order (Author > Editor > User, parallel review, user-first) is an open design question — start with one, make configurable

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Three-agent architecture over single-agent | Separates writing, quality, and audience validation — mirrors how good doc teams work | — Pending |
| Content-first, doc-system-agnostic | Maximizes reuse across projects with different doc systems | — Pending |
| Layered rules (universal + project config) | Universal rules enforce baseline quality; project config handles audience, system, custom needs | — Pending |
| User Persona generates own test scenarios | Maintainer shouldn't have to author test cases — agent reads project context and creates realistic user journeys | — Pending |
| Agent workflow order TBD | All pipeline approaches (serial, parallel, user-first) are plausible — needs experimentation | — Pending |

---
*Last updated: 2026-03-02 after initialization*
