# Phase 2: Doc Author Agent - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

The Doc Author agent produces diataxis-structured, audience-calibrated, internal-detail-free library documentation with working code examples. It reads source code, tests, and existing docs to understand the project, plans a page inventory in conversation with the project author, then writes the full doc set. Editor review, humanizer pass, and persona validation are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Content planning approach
- Author operates in two phases: **plan** then **write**
- Plan phase: scan codebase, propose a Diataxis-guided page inventory to the project author
- Each inventory entry includes: doc type (tutorial/how-to/reference/explanation), proposed title, and target sections/topics the page will cover
- Narrative content (tutorials, how-tos, explanations) is proposed by the Agent and refined in conversation with the project author — not auto-decided
- Auto-generated API Reference docs exist separately (typedoc, pdoc, etc.) — the Author does not write reference pages but must be aware of them and link to them
- README.md and MAINTAINER.md appear as proposed pages in the inventory that the user can include or exclude
- After the user approves the plan, Author writes the full doc set in one pass (no page-by-page review)

### Code example strategy
- Examples sourced from source code AND test files — tests provide realistic usage patterns and edge cases
- First example in a section is self-contained (includes imports, setup, the call — runnable as-is)
- Subsequent examples in the same section can build on the prior example without repeating setup code
- Happy path is the primary example; error handling and edge cases are shown in separate subsections where relevant
- All applicable format variants are shown: multiple programming languages if the library supports them, multiple config formats (INI vs TOML, JSON vs YAML), etc.
- Format variants use tabbed panels where the doc system supports it (e.g., mkdocs-material content tabs)

### README template
- Standard open-source README: title, badges, 1-paragraph description, quick start (install + first use), key features list, link to full docs near the top
- Key features list must be carefully written to avoid LLM-isms — humanizer pass (Phase 3) will help
- Brief tech stack / architecture section near the bottom with link to MAINTAINER doc
- Docs publication URL is inferred from the doc system (mkdocs + GitHub Pages = pages URL; plain markdown = link to docs/ directory; fall back to asking if undetermined)
- License section at the bottom

### MAINTAINER template
- Oriented toward single-contributor projects
- Sections: dev setup instructions, common development tasks, architecture overview, CI/CD process, release process, decision log
- Combines practical how-to (clone, install deps, run tests, common tasks) with architectural context
- Not a contributor guide with PR guidelines — this is a "future you" reference document

### Source reading depth
- Author reads everything available: public API, implementation, tests, existing docs, README, changelogs
- Dedicated upfront scan pass before writing any pages — builds an internal model of all public APIs, patterns, and behaviors
- Page writing draws from this pre-built understanding rather than reading source inline
- Internal implementation details captured as hidden metadata/internal notes for the Editor to use for accuracy-checking only — Editor must understand these are strictly for verification and must never appear in output
- Author detects or is configured to know where auto-generated API Reference lives
- All inline `code` mentions of symbols (`Class`, `Cls.method`, `function`, `module`, `GLOBAL_CONST`, etc.) must link to the corresponding symbol in the API Reference

### Claude's Discretion
- Internal structure of the upfront scan pass (what gets indexed, how it's organized)
- How to detect auto-generated API Reference location (config field vs inference)
- Exact heuristics for filtering internal details from source code scan
- Format of internal notes passed to Editor (comments, metadata section, separate file)
- How to handle projects where no auto-generated API Reference exists yet (warn, skip linking, suggest setup)

</decisions>

<specifics>
## Specific Ideas

- Diataxis framework (already in skills/diataxis/SKILL.md) guides both content classification and the page inventory structure
- "All inline code symbols link to API Reference" is a universal rule that strengthens Quality Rule 4 — every `symbol` in prose is a navigation point to the reference
- Multi-format examples are not just about programming languages — also config formats (INI vs TOML), shell commands (bash vs PowerShell), etc.
- Internal notes for Editor carry a real risk of bleeding into output — the implementation must enforce a hard boundary, not just a suggestion

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `agents/doc-author.md`: Stub agent with frontmatter (name, tools, skills references). Needs full authoring logic added.
- `skills/diataxis/SKILL.md`: Complete Diataxis framework with structural templates for all 4 doc types + classification decision guide. Author uses this directly.
- `skills/quality-rules/SKILL.md`: 5 universal rules (no internal details, working examples, consistent structure, cross-references, audience calibration). Author enforces these.
- `skills/setup/defaults/mkdocs-material.md` and `plain-markdown.md`: Doc-system guidance files. Author reads the active one from `.doc-writer/`.
- `skills/setup/defaults/rules.md`: Default project rules template. Author reads from `.doc-writer/rules.md`.

### Established Patterns
- Agent file format: YAML frontmatter (name, description, tools, model, skills) + markdown body — confirmed in Phase 1
- Skills referenced via `doc-writer:quality-rules` and `doc-writer:diataxis` namespace
- Config at `.doc-writer/config.yaml` with audiences array, doc_system, and paths
- Guidance files are opinionated preferences (not syntax references) — agents already understand doc system syntax

### Integration Points
- Author reads `.doc-writer/config.yaml` for audience definitions, doc system, and paths
- Author reads `.doc-writer/{doc_system}.md` for doc-system-specific guidance
- Author reads `.doc-writer/rules.md` for project-specific rules
- Author writes output pages to the configured `paths.docs_root`
- Author's output is the input for Editor (Phase 3) and User Persona (Phase 4)
- Internal notes from Author are consumed by Editor for accuracy checking

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-doc-author-agent*
*Context gathered: 2026-03-03*
