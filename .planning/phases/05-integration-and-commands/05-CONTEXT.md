# Phase 5: Integration and Commands - Context

**Gathered:** 2026-03-04
**Status:** Ready for planning

<domain>
## Phase Boundary

User-facing commands (`/doc:write`, `/doc:review`, `/doc:edit`) that orchestrate the three-agent pipeline, plus gap detection comparing public API surface against documented surface. GSD integration is satisfied by the commands being available in any CC session. Pipeline orchestration, revision loop routing, and PARTIAL approval UX are the primary deliverables.

</domain>

<decisions>
## Implementation Decisions

### /doc:write pipeline orchestration
- Claude decides the orchestration approach (command file vs dedicated orchestrator agent) based on CC plugin architecture
- Pipeline sequence: gap detection scan > Author > Editor > Persona(s) > revision loop (if FAILs) > summary
- Revision loop uses locked decisions from Phase 4: only FAILs trigger revision, max 2-3 passes, Author revises targeted pages, Editor re-runs changed pages + full terminology, escalation on non-convergence
- Multi-audience: separate Persona per audience in parallel (from Phase 4)
- Generated docs are left uncommitted -- project author reviews diff and commits when satisfied
- Full summary report at completion showing: pages written/revised, Editor changes applied, Persona verdicts per scenario, revision passes taken, remaining PARTIALs

### PARTIAL approval UX
- Claude decides the UX for PARTIAL approval (inline during pipeline vs batch at end)
- Core requirement: project author sees PARTIAL fix suggestions and approves/rejects them
- Approved fixes applied directly without re-running the full pipeline

### /doc:review
- Runs Editor + Persona only (no Author) on existing docs
- Produces editor-report.md and persona-report.md showing issues
- Gap detection also runs during /doc:review (same exported-symbols scan)
- No content generation -- purely an audit of existing documentation

### /doc:edit
- Presents issues from existing reports (editor-report.md, persona-report.md) as multi-select options
- Includes a freeform "describe something else" option for custom instructions
- Project author selects which issues to fix
- Author agent rewrites targeted content, then Editor runs humanizer + terminology + cross-refs on changed pages
- No Persona re-run after edit -- project author can run /doc:review afterwards if they want full validation

### Gap detection
- Public API surface = exported symbols only (exported functions, classes, types, constants)
- Language-adaptive: Python's __all__, Rust's pub, TypeScript's export, etc.
- Runs during /doc:write before Author starts -- gap list handed to Author as input so it can prioritize undocumented symbols
- Also runs during /doc:review to flag undocumented symbols in existing docs
- Report appears both in the completion summary AND persisted to .doc-writer/gap-report.md
- Author reads gap-report.md from previous runs as optional input for prioritizing coverage

### GSD integration
- Commands are the integration -- /doc:write, /doc:review, /doc:edit work in any CC session including GSD sessions
- No special GSD hooks or automatic triggers
- GSD planners can naturally reference /doc:write in roadmap tasks
- INTG-04 satisfied by commands being available and invokable
- Optional: if .planning/PROJECT.md exists, Author can use it for richer project understanding (light touch, not a dependency)

### Claude's Discretion
- Orchestration architecture (command file vs orchestrator agent)
- PARTIAL approval UX approach (inline vs batch)
- How gap detection scans for exported symbols per language
- How Author prioritizes gap-report.md items vs its own scan findings
- Pipeline progress reporting during execution (verbose vs summary)
- How /doc:edit presents report issues (formatting, grouping)

</decisions>

<specifics>
## Specific Ideas

- gap-report.md feeds back into the pipeline: Author reads it on subsequent /doc:write runs to know what was previously missing
- /doc:edit issue selection is report-driven with multi-select, not just freeform -- the project author shouldn't have to re-describe issues that are already catalogued
- Leaving docs uncommitted aligns with REQUIREMENTS.md "no automated publishing" principle -- the project author is the final review gate

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `agents/doc-author.md` (428 lines): Complete Author agent with two-phase workflow (Scan+Plan > Write). Handles targeted rewrites via internal notes mechanism.
- `agents/doc-editor.md` (390 lines): Complete Editor with three-pass workflow (Terminology > Humanizer > Cross-refs). Can run on changed pages + full terminology scan.
- `agents/doc-persona.md` (403 lines): Complete Persona with three-phase workflow (Generate > Simulate > Report). Supports audience parameter for multi-audience. Writes persona-report.md and scenarios.yaml.
- `skills/quality-rules/SKILL.md`: 5 universal rules all agents reference.
- `skills/diataxis/SKILL.md`: Diataxis framework referenced by Author.
- `skills/setup/SKILL.md`: Setup Q&A skill with auto-detection.

### Established Patterns
- Agent files: YAML frontmatter (name, description, tools, model, skills) + markdown body
- Skills referenced via `doc-writer:quality-rules` and `doc-writer:diataxis` namespace
- Config at `.doc-writer/config.yaml` with audiences array, doc_system, paths
- All agent artifacts written to `.doc-writer/` directory (editor-report.md, terminology.yaml, persona-report.md, scenarios.yaml)
- Author outputs to `paths.docs_root`, internal notes as HTML comments (stripped by Editor)

### Integration Points
- Commands will live in `commands/` directory (CC plugin command format)
- Each command references agents via Task tool spawning
- Pipeline artifacts flow: Author output > Editor input > Persona input
- Revision loop routes Persona FAILs back to Author > Editor > Persona
- Gap report at `.doc-writer/gap-report.md` feeds into Author's scan phase

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 05-integration-and-commands*
*Context gathered: 2026-03-04*
