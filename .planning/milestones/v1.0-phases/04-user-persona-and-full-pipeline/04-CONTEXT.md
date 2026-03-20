# Phase 4: User Persona and Full Pipeline - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

User Persona agents validate documentation from the end user's perspective by generating goal-oriented scenarios and testing whether real goals can be accomplished using only the docs. The full Author > Editor > Persona pipeline runs with a bounded revision loop. Pipeline orchestration commands (/doc:write, /doc:review) are Phase 5 -- this phase builds the Persona agent and defines the revision protocol.

</domain>

<decisions>
## Implementation Decisions

### Scenario generation
- Persona reads only generated docs and audience config (no source code) -- simulates a real end user
- Goals inferred from docs structure filtered through the audience's skill level -- beginner Personas prioritize setup/basics, advanced ones target deeper features
- Domain context (what the user already knows about the problem space) is enriched via web search at /doc:setup time and persisted to the audience definition in config -- Persona reads the already-enriched config at runtime without its own web search
- Setup Q&A captures the user's "discovery story" (how/why they found the lib) to inform Persona's perspective
- Scenarios persist to .doc-writer/scenarios.yaml and are reused across runs; Persona regenerates when docs change significantly (new pages, major edits)

### Testing methodology
- Step-by-step simulation: Persona traces through docs as if following instructions to accomplish each goal
- For each scenario: "I want to do X -- where do I start? Can I find it? Do the steps make sense? Are code examples present and realistic?"
- Code example verification is existence + plausibility only (does it exist? does it look complete and realistic? does it match the explanation?) -- no execution (per REQUIREMENTS.md out-of-scope)
- All scenarios start from the docs homepage (README or doc site index) and navigate from there -- tests the real discovery path every time
- Persona follows cross-reference links and table of contents to find information, testing the interconnected doc experience

### Verdict and gap reporting
- Verdicts are based on goal achievability:
  - **PASS**: smooth path from start to finish, user can accomplish the goal
  - **PARTIAL**: goal is achievable but with friction (unclear steps, missing context, confusing order)
  - **FAIL**: user cannot accomplish the goal at all (missing page, dead-end, wrong instructions)
- Structured per-scenario report written to .doc-writer/persona-report.md (overwritten each run)
- Each scenario report includes: verdict, steps attempted, where it got stuck (page + section), what was missing/wrong, suggested fix
- Only FAIL verdicts trigger automated revision passes
- PARTIAL verdicts: Persona suggests specific fixes, presents them to project author for approval; approved fixes are applied directly without going back through the full pipeline

### Revision loop protocol
- Only FAIL verdicts trigger revision -- PARTIALs handled separately via project author approval
- Author revises targeted pages only (not full doc set re-generation) based on specific gaps from Persona report
- Editor re-runs on changed pages for humanizer and cross-reference passes, plus a full terminology scan across all files (term changes can ripple)
- Maximum 2-3 revision passes; if FAILs remain after max passes, escalate to project author with full context (what was tried, why it didn't converge)
- Pipeline command (Phase 5's /doc:write) orchestrates the Author > Editor > Persona sequence and revision routing; Persona just reports verdicts and gaps

### Multi-audience parallel execution
- When multiple audiences are configured, a separate Persona agent runs for each audience in parallel (from PERS-05)
- Each Persona uses its own audience definition (skill level, assumed knowledge, domain context) to generate audience-specific scenarios
- Independent verdicts per audience -- a PASS for advanced users doesn't excuse a FAIL for beginners

### Claude's Discretion
- Exact format of scenarios.yaml schema (how scenarios are stored and diffed for staleness)
- How to detect "significant" doc changes that trigger scenario regeneration
- Internal mechanics of step-by-step simulation (how Persona tracks its navigation path)
- Exact threshold for what counts as "plausible" in code example checks
- How to structure the PARTIAL fix suggestions for project author presentation

</decisions>

<specifics>
## Specific Ideas

- Domain context enrichment at setup time is key -- a user searching for "the ORM for your Semantic Layer" already knows what a semantic layer is; the docs don't need to explain the whole field, and the Persona shouldn't penalize docs for not explaining it
- The audience config's assumed_knowledge and never_assume fields are the primary inputs for Persona's perspective calibration
- Scenarios should test real user journeys, not checkbox requirements -- "can I set up the project and make my first query?" not "does the getting-started page exist?"
- PARTIAL verdicts with project-author-approved fixes create a lightweight path for subjective improvements without triggering the heavyweight revision loop

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `agents/doc-persona.md`: Stub agent with frontmatter (name, tools: Read/Glob/Grep, skills: quality-rules). Needs full scenario generation and testing logic added.
- `agents/doc-author.md`: Complete Author agent (428 lines). Persona's revision requests must match the format Author expects for targeted rewrites.
- `agents/doc-editor.md`: Complete Editor agent (390 lines). Revision loop needs to invoke Editor with a "changed pages only + full terminology" mode.
- `skills/quality-rules/SKILL.md`: 5 universal rules. Persona validates Rule 4 (cross-references) and Rule 5 (audience calibration) from the end-user perspective.

### Established Patterns
- Agent file format: YAML frontmatter + markdown body (confirmed Phase 1, 2, 3)
- Skills referenced via `doc-writer:quality-rules` namespace
- Config at `.doc-writer/config.yaml` with audiences array, doc_system, paths
- Editor outputs: `.doc-writer/editor-report.md` (structured feedback), `.doc-writer/terminology.yaml` (term map)
- Author outputs: doc pages to `paths.docs_root`, internal HTML comments (stripped by Editor before Persona sees them)
- Persona tools are Read/Glob/Grep only (no Write) -- read-only agent that reports but doesn't modify

### Integration Points
- Persona reads Editor-cleaned docs from `paths.docs_root` (no HTML comments)
- Persona reads `.doc-writer/config.yaml` for audience definition and enriched domain context
- Persona writes `.doc-writer/persona-report.md` as its output artifact
- Persona writes/reads `.doc-writer/scenarios.yaml` for scenario persistence
- Persona report is consumed by the pipeline orchestrator (Phase 5) for revision routing
- Revision loop sends gaps back to Author for targeted rewrites, then through Editor

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 04-user-persona-and-full-pipeline*
*Context gathered: 2026-03-03*
