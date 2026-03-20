# Phase 3: Editor Agent - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

The Editor agent reviews Doc Author output and produces humanized, terminology-consistent, publication-quality docs with structured feedback. It edits files directly and produces an audit report of all changes. User Persona validation, pipeline orchestration, and revision loops are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Review workflow
- Multiple sequential passes, not a single integrated pass
- Pass order: Terminology > Humanizer > Cross-references
- Editor fixes docs directly AND produces a structured feedback report of what it changed and why
- Editor verifies accuracy claims in Author's internal HTML comments against source code, then strips the comments from edited files -- resulting files must be clean
- Each pass is focused on one concern, making issues easier to trace

### Humanizer strategy
- AI-writing patterns embedded directly in the Editor agent prompt (self-contained, no external skill dependency)
- Patterns sourced from the installed CC humanizer skill (24 pattern categories based on Wikipedia's "Signs of AI writing")
- Moderate aggressiveness: fix clearly AI-generated phrases (hedging, filler, promotional language, significance inflation, copula avoidance, synonym cycling, rule-of-three, negative parallelisms, sycophantic tone, chatbot artifacts)
- Aggressive em dash purge -- replace em dashes with commas, periods, or restructured sentences
- Minimal personality injection: clean and professional documentation voice, no first-person, no opinions, no humor -- reads like a senior developer wrote official docs
- Preserve meaning and technical accuracy during rewrites

### Terminology consistency
- First pass builds an explicit term map by scanning all doc files
- Source code is the authority for term selection -- if the public API says `config`, docs say `config`
- Term map includes proper noun formatting (e.g., `GitHub` not `Github`, `JavaScript` not `Javascript`)
- Term map written to `.doc-writer/terminology.yaml` for project author to review, override, and persist across runs
- On subsequent runs, Editor reads existing terminology.yaml first and applies it, updating with any new terms found
- Conflicting terms normalized to the source-code-preferred form

### Cross-reference linking
- Editor verifies all inline `code` mentions are linked to API Reference entries (Author adds these during writing, Editor fills gaps)
- Broken or missing links are fixed directly and reported as BLOCKING in feedback
- This runs as the final pass since humanizer rewrites may change text around code mentions

### Feedback format
- Structured feedback written to `.doc-writer/editor-report.md`
- Report overwritten each run (reflects current state, not history)
- Every feedback item includes: page, section, severity, description, and exact fix (applied or proposed)
- Severity definitions:
  - **BLOCKING**: factual error, broken link, missing cross-reference, leaked internal detail, accuracy mismatch with source code
  - **SUGGESTION**: AI-pattern detected and fixed, inconsistent term normalized, unclear wording rewritten
  - **NITPICK**: style preference, minor formatting adjustment

### Claude's Discretion
- Exact structure of the term map YAML schema
- How to organize the editor-report.md (by file, by severity, or by pass)
- Heuristics for deciding when a term variant is "different enough" to flag vs. acceptable variation
- How to handle terms that appear in both code and prose with legitimately different forms
- Internal pass implementation (whether passes re-read files or work from memory)

</decisions>

<specifics>
## Specific Ideas

- Humanizer patterns adapted from CC humanizer skill v2.1.1 (all 24 categories), tailored for documentation context rather than general prose
- Em dash treatment is strict -- near-zero tolerance, replace with commas or sentence restructuring
- terminology.yaml is a "copy and customize" artifact similar to .doc-writer/rules.md -- Editor generates it, project author can edit it
- Editor strips Author's internal HTML comments after verification -- the edited files User Persona receives in Phase 4 are clean, publication-ready

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `agents/doc-editor.md`: Stub agent with frontmatter (name, tools: Read/Write/Glob/Grep, skills: quality-rules). Needs full editing logic added.
- `skills/quality-rules/SKILL.md`: 5 universal rules the Editor must enforce. Rules 1 (no internal details) and 4 (cross-reference linking) are especially relevant to Editor verification.
- CC humanizer skill (`~/.claude/skills/humanizer/SKILL.md`): 24 AI-pattern categories with before/after examples. Source material for embedding patterns into Editor prompt.

### Established Patterns
- Agent file format: YAML frontmatter + markdown body (confirmed Phase 1)
- Skills referenced via `doc-writer:quality-rules` namespace
- Config at `.doc-writer/config.yaml` with audiences, doc_system, paths
- Author adds internal notes as HTML comments at end of each page (confirmed Phase 2)
- Author links inline code to API Reference during writing (confirmed Phase 2)

### Integration Points
- Editor reads Author's output files from `paths.docs_root`
- Editor reads `.doc-writer/config.yaml` for audience and doc system context
- Editor reads `.doc-writer/rules.md` for project-specific rules to enforce
- Editor reads/writes `.doc-writer/terminology.yaml` for term consistency
- Editor writes `.doc-writer/editor-report.md` as feedback artifact
- Editor's edited files are the input for User Persona (Phase 4)
- Editor report is consumed by the pipeline revision loop (Phase 4)

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 03-editor-agent*
*Context gathered: 2026-03-03*
