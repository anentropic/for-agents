# Phase 2: Doc Author Agent - Research

**Researched:** 2026-03-03
**Domain:** Claude Code agent system prompt design, Diataxis-based documentation authoring, code example sourcing, internal-detail filtering
**Confidence:** HIGH -- builds on Phase 1's verified CC plugin architecture; this phase's deliverable is a single agent file (`agents/doc-author.md`) with a comprehensive system prompt

## Summary

Phase 2 delivers the Doc Author agent -- the central content generator in the three-agent pipeline. The entire deliverable is expanding the existing `agents/doc-author.md` stub (created in Phase 1) with a comprehensive system prompt that enables Claude to: (1) scan a codebase and propose a Diataxis-guided page inventory, (2) get user approval on the plan, and (3) write the full documentation set in one pass. The agent file already has correct frontmatter (`name`, `description`, `tools`, `model`, `skills` references to `doc-writer:quality-rules` and `doc-writer:diataxis`).

This phase has no runtime dependencies to install and no code to write in the traditional sense. The "implementation" is designing a detailed, structured system prompt that covers: content classification via Diataxis types, structural template application, audience calibration from config, internal-detail filtering, code example sourcing from source and test files, README and MAINTAINER template application, doc-system-specific output formatting, and internal notes for the Editor. The supporting skills (quality-rules, diataxis) and config infrastructure (.doc-writer/) already exist from Phase 1.

The key challenge is prompt architecture -- structuring a long, multi-concern system prompt so Claude follows it reliably. The prompt must encode enough specificity to produce consistent, high-quality output while remaining flexible enough to handle diverse codebases. Research into CC's subagent system confirms that the full content of skills listed in the `skills:` frontmatter field is preloaded into the agent's context at startup, meaning the quality-rules and diataxis content does NOT need to be duplicated in the agent body.

**Primary recommendation:** Structure the agent prompt as a multi-phase workflow (scan, plan, write) with explicit section headers, checklists, and self-verification steps. Use the `skills:` preloading mechanism for shared knowledge (quality rules, diataxis templates) and keep the agent body focused on the authoring workflow, filtering logic, and output formatting.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Author operates in two phases: **plan** then **write**
- Plan phase: scan codebase, propose a Diataxis-guided page inventory to the project author
- Each inventory entry includes: doc type (tutorial/how-to/reference/explanation), proposed title, and target sections/topics the page will cover
- Narrative content (tutorials, how-tos, explanations) is proposed by the Agent and refined in conversation with the project author -- not auto-decided
- Auto-generated API Reference docs exist separately (typedoc, pdoc, etc.) -- the Author does not write reference pages but must be aware of them and link to them
- README.md and MAINTAINER.md appear as proposed pages in the inventory that the user can include or exclude
- After the user approves the plan, Author writes the full doc set in one pass (no page-by-page review)
- Examples sourced from source code AND test files -- tests provide realistic usage patterns and edge cases
- First example in a section is self-contained (includes imports, setup, the call -- runnable as-is)
- Subsequent examples in the same section can build on the prior example without repeating setup code
- Happy path is the primary example; error handling and edge cases are shown in separate subsections where relevant
- All applicable format variants are shown: multiple programming languages if the library supports them, multiple config formats (INI vs TOML, JSON vs YAML), etc.
- Format variants use tabbed panels where the doc system supports it (e.g., mkdocs-material content tabs)
- Standard open-source README: title, badges, 1-paragraph description, quick start (install + first use), key features list, link to full docs near the top
- Key features list must be carefully written to avoid LLM-isms -- humanizer pass (Phase 3) will help
- Brief tech stack / architecture section near the bottom with link to MAINTAINER doc
- Docs publication URL is inferred from the doc system (mkdocs + GitHub Pages = pages URL; plain markdown = link to docs/ directory; fall back to asking if undetermined)
- MAINTAINER.md oriented toward single-contributor projects
- MAINTAINER sections: dev setup instructions, common development tasks, architecture overview, CI/CD process, release process, decision log
- MAINTAINER combines practical how-to (clone, install deps, run tests, common tasks) with architectural context
- Not a contributor guide with PR guidelines -- this is a "future you" reference document
- Author reads everything available: public API, implementation, tests, existing docs, README, changelogs
- Dedicated upfront scan pass before writing any pages -- builds an internal model of all public APIs, patterns, and behaviors
- Page writing draws from this pre-built understanding rather than reading source inline
- Internal implementation details captured as hidden metadata/internal notes for the Editor to use for accuracy-checking only
- Author detects or is configured to know where auto-generated API Reference lives
- All inline `code` mentions of symbols must link to the corresponding symbol in the API Reference

### Claude's Discretion
- Internal structure of the upfront scan pass (what gets indexed, how it's organized)
- How to detect auto-generated API Reference location (config field vs inference)
- Exact heuristics for filtering internal details from source code scan
- Format of internal notes passed to Editor (comments, metadata section, separate file)
- How to handle projects where no auto-generated API Reference exists yet (warn, skip linking, suggest setup)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | Doc Author classifies content type (tutorial, how-to, reference, explanation) before writing and applies correct structure | Diataxis skill (preloaded via `skills:` field) provides classification decision guide and structural templates; agent prompt includes explicit "classify before write" workflow step |
| AUTH-02 | All pages of the same doc type follow the same template structure | Diataxis skill provides structural templates per type; agent prompt enforces "apply template from diataxis skill" as a mandatory step; quality-rules skill Rule 3 (Consistent Structure) preloaded |
| AUTH-03 | Internal details are filtered out -- no test utils, CI config, dev scripts, justfile recipes, or maintainer-only concerns in end-user-facing docs | Agent prompt includes explicit internal-detail filter with blocklist patterns; quality-rules Rule 1 (No Internal Details) preloaded; scan pass separates public API from internal implementation |
| AUTH-04 | Author reads the selected doc-system guidance file and produces output using that system's syntax and conventions | Agent prompt reads `.doc-writer/{doc_system}.md` guidance file at startup; output formatting follows guidance directives |
| AUTH-05 | README.md has its own template -- end-user-focused, with quick start, installation, and key features | Agent prompt includes explicit README template with locked sections (title, badges, description, quick start, features, docs link, tech stack, license) |
| AUTH-06 | MAINTAINER.md has its own template -- contributor-focused, with setup, architecture, and contribution guidelines | Agent prompt includes explicit MAINTAINER template with locked sections (dev setup, common tasks, architecture, CI/CD, release, decision log) |
| AUTH-07 | Every API/feature page includes working, realistic code examples (not pseudocode or minimal stubs) | Agent prompt mandates sourcing examples from source code and test files; quality-rules Rule 2 (Working Code Examples) preloaded; first-example-self-contained rule encoded |
| AUTH-08 | Python/mkdocs projects support blacken-docs formatting and doctest validation where appropriate | Agent prompt includes conditional logic: if language=Python and doc_system=mkdocs-material, apply Black-compatible formatting to Python code blocks and use doctest-compatible patterns where appropriate |
| AUTH-09 | Vocabulary and assumed knowledge level are calibrated to the configured audience | Agent prompt reads audience config from `.doc-writer/config.yaml`; quality-rules Rule 5 (Audience-Calibrated Language) preloaded; prompt includes explicit calibration checklist |
</phase_requirements>

## Standard Stack

### Core

| Component | Format | Purpose | Why Standard |
|-----------|--------|---------|--------------|
| Agent file (`agents/doc-author.md`) | YAML frontmatter + markdown body | Doc Author subagent definition with full system prompt | CC subagent format -- frontmatter for metadata, body for system prompt; already established in Phase 1 |
| Skills preloading (`skills:` field) | Frontmatter array | Injects quality-rules and diataxis content into agent context | CC subagent feature -- full skill content loaded at agent startup; no runtime discovery needed |
| Config reading (`.doc-writer/config.yaml`) | YAML via Read tool | Audience definitions, doc system, paths | Established in Phase 1; agent reads at runtime using Read tool |
| Guidance file (`.doc-writer/{doc_system}.md`) | Markdown via Read tool | Doc-system-specific output preferences | Established in Phase 1; agent reads at runtime |
| Project rules (`.doc-writer/rules.md`) | Markdown via Read tool | Project-specific quality rules | Established in Phase 1; additive to universal rules |

### Supporting

| Component | Format | Purpose | When to Use |
|-----------|--------|---------|-------------|
| `blacken-docs` awareness | Conditional formatting guidance | Black-compatible Python code blocks | When `detected.language == python` and `doc_system == mkdocs-material` |
| Internal notes for Editor | HTML comments or metadata block | Implementation details for accuracy-checking | Every page -- hidden from rendered output but readable by Editor agent |
| Page inventory format | Markdown table/list | Plan phase output for user review | During the plan phase before writing |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Single monolithic prompt | Multiple skills/files | Monolithic keeps all logic in one place for this agent; skills are for shared knowledge (already used for quality-rules and diataxis) |
| HTML comments for internal notes | Separate `.notes/` directory | HTML comments keep notes co-located with content; separate files add complexity but provide cleaner separation |
| Scan-then-write workflow | Interleaved read-write | Upfront scan builds a complete model before writing, producing more consistent cross-references; interleaved risks inconsistency |

## Architecture Patterns

### Agent File Structure

The `agents/doc-author.md` file has this structure:

```markdown
---
name: doc-author
description: Writes draft library documentation...
tools: Read, Write, Glob, Grep, Bash
model: inherit
skills:
  - doc-writer:quality-rules
  - doc-writer:diataxis
---

[System prompt body -- the Phase 2 deliverable]
```

The frontmatter is already correct from Phase 1. Phase 2 replaces the placeholder body with the full authoring system prompt.

### Pattern 1: Two-Phase Agent Workflow (Plan then Write)

**What:** The agent operates in two distinct phases -- first proposing a page inventory, then writing all pages after user approval. This is a locked user decision.

**When to use:** Always -- this is the Doc Author's core workflow.

**Prompt structure:**
```markdown
## Phase 1: Scan and Plan

### Step 1: Read Configuration
Read `.doc-writer/config.yaml` to load:
- Target audience(s) and their skill levels
- Doc system and paths
- Project-specific rules from `.doc-writer/rules.md`
- Doc-system guidance from `.doc-writer/{doc_system}.md`

### Step 2: Codebase Scan
[Detailed scan instructions -- see Pattern 2]

### Step 3: Propose Page Inventory
Present to the user as a table:

| # | Type | Title | Sections/Topics |
|---|------|-------|-----------------|
| 1 | tutorial | Getting Started with {Library} | Prerequisites, installation, first use, what you learned |
| 2 | how-to | How to Configure Authentication | Prerequisites, steps, troubleshooting |
| ... | ... | ... | ... |
| N | (readme) | README.md | Title, badges, description, quick start, features, docs link |
| N+1 | (maintainer) | MAINTAINER.md | Dev setup, tasks, architecture, CI/CD, release |

Wait for user to approve, modify, add, or remove pages.

## Phase 2: Write

### For each approved page:
1. Classify type (already determined in plan)
2. Apply structural template from diataxis skill
3. Write content using scan results
4. Add internal notes as HTML comments
5. Apply doc-system formatting from guidance file
6. Link all inline `code` symbols to API Reference

### Write all pages to the configured docs_root
```

**Confidence:** HIGH -- workflow is a locked user decision; prompt structure follows CC subagent best practices.

### Pattern 2: Upfront Codebase Scan Pass

**What:** Before writing any pages, the agent performs a comprehensive scan of the codebase to build an internal model. This prevents inconsistent or incomplete documentation.

**When to use:** Always -- at the start of every Doc Author invocation.

**Scan targets:**
```markdown
## Codebase Scan

Scan the project systematically using Glob, Grep, and Read tools:

### Public API Surface
- Exported functions, classes, methods, constants
- Type definitions and interfaces
- Configuration options and parameters
- CLI commands and arguments (if applicable)

### Implementation Patterns
- Common usage patterns visible in source
- Error handling approaches
- Extension/plugin mechanisms
- Configuration loading and validation

### Test Files
- Test files reveal realistic usage patterns
- Integration tests show end-to-end workflows
- Edge cases and error scenarios tested
- Fixtures and test data show expected formats

### Existing Documentation
- README.md content and structure
- Inline docstrings and JSDoc/pydoc comments
- Changelogs and release notes
- Any existing docs/ directory content

### Internal Details (filter out of user docs)
- Test utilities and test-only helpers
- CI/CD configuration files
- Development scripts (Makefile, justfile, etc.)
- Internal modules not exposed in public API
- Build configuration and tooling
```

**Confidence:** HIGH -- scan approach is derived from locked user decisions (read everything, filter internals).

### Pattern 3: Internal-Detail Filtering

**What:** A systematic approach to separating public-facing content from internal implementation details during the scan pass. Internal details are captured as notes for the Editor but never appear in user-facing output.

**Implementation in prompt:**
```markdown
## Internal Detail Filter

### ALWAYS filter out (never appears in user docs):
- File paths to test directories (tests/, __tests__/, spec/)
- CI/CD config mentions (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`)
- Build tool config (webpack.config.*, vite.config.*, rollup.config.*)
- Dev scripts (justfile recipes, Makefile targets for dev tasks)
- Internal module names prefixed with `_` or marked `@internal`
- Test fixtures, mocks, and test utilities
- Pre-commit hooks and linter config
- Docker files used only for development
- Environment variable names used only in CI

### Capture as internal notes for Editor (hidden metadata):
- Implementation details that explain WHY something works a certain way
- Performance characteristics derived from implementation reading
- Known limitations visible in source but not documented
- Edge cases that tests cover but users might encounter
```

**Confidence:** HIGH -- filtering rules directly implement quality-rules Rule 1 (No Internal Details) and locked user decision about internal notes for Editor.

### Pattern 4: Code Example Sourcing Strategy

**What:** How the agent finds, selects, and presents code examples. Locked user decision: source from both code and test files.

**Implementation in prompt:**
```markdown
## Code Example Rules

### Sourcing
1. Scan source code for usage patterns, API signatures, and common configurations
2. Scan test files for realistic usage, edge cases, and expected behavior
3. Prefer test-derived examples when they demonstrate real-world use cases
4. Adapt and simplify test code for documentation (remove test assertions,
   add context)

### First Example Rule
The FIRST example in any section MUST be self-contained:
- Include all necessary imports
- Include any required setup (initialization, configuration)
- Show the actual API call
- Show expected output or result
- Runnable as-is if copy-pasted

### Subsequent Examples
Examples after the first in the same section MAY build on prior examples:
- Can omit imports and setup already shown
- Reference variables and objects from the first example
- Use comments like "# Using client from above" to indicate continuity

### Happy Path First
- Primary example demonstrates the happy path (normal, successful usage)
- Error handling shown in separate "Error Handling" or "Edge Cases" subsection
- Do not mix error handling into the primary example

### Format Variants
When the library supports multiple formats or languages:
- Show ALL applicable variants
- Use tabbed panels if doc system supports it (mkdocs-material content tabs)
- Tab labels: short and consistent ("Python", "JavaScript", "YAML", "TOML")
- If doc system does not support tabs, use consecutive code blocks with clear headings
```

**Confidence:** HIGH -- all rules are locked user decisions from CONTEXT.md.

### Pattern 5: README and MAINTAINER Templates

**What:** Dedicated templates for README.md and MAINTAINER.md that differ from Diataxis-typed pages.

**README template (locked):**
```markdown
# {Project Name}

{badges}

{1-paragraph description -- what this library does and who it's for}

[Full Documentation]({docs_url})

## Quick Start

### Installation
{install command}

### First Use
{minimal working example -- self-contained, copy-paste-runnable}

## Key Features

- {Feature 1}: {brief description}
- {Feature 2}: {brief description}
- ...

## Tech Stack / Architecture

{brief overview with link to MAINTAINER.md}

## License

{license info}
```

**MAINTAINER template (locked):**
```markdown
# Maintainer Guide

> This is a "future you" reference document for project maintainers.
> It is NOT an end-user document and NOT a contributor guide with PR guidelines.

## Dev Setup

{clone, install deps, verify setup works}

## Common Development Tasks

{run tests, lint, format, build, common workflows}

## Architecture Overview

{high-level structure, key modules, data flow}

## CI/CD Process

{what CI runs, how to interpret results}

## Release Process

{version bumping, changelog, publishing steps}

## Decision Log

{key architectural decisions and their rationale}
```

**Confidence:** HIGH -- templates are locked user decisions from CONTEXT.md.

### Pattern 6: Internal Notes Format for Editor

**What:** How the Author passes internal implementation details to the Editor for accuracy-checking without those details appearing in rendered documentation.

**Recommendation (Claude's discretion):** Use HTML comments at the end of each page.

```markdown
<!-- INTERNAL NOTES FOR EDITOR - DO NOT INCLUDE IN RENDERED OUTPUT
These notes contain implementation details for accuracy verification only.

## Implementation Context
- The `connect()` method internally uses connection pooling (pool size
  defaults to 5)
- Rate limiting is implemented via token bucket algorithm in
  `_internal/rate_limiter.py`
- The retry logic uses exponential backoff with jitter (max 3 retries)

## Known Limitations (verify these are documented appropriately)
- Maximum payload size is 10MB (hardcoded in constants.py)
- WebSocket connections timeout after 30s idle

## API Reference Location
- Auto-generated reference at: docs/api/ (from typedoc/pdoc output)
- Link format: docs/api/{module}.md#{symbol}
-->
```

**Why HTML comments:** They are invisible in rendered markdown output (any doc system), they are co-located with the page content (no separate file management), the Editor agent can read them via Read tool, and they follow a clear boundary pattern that makes accidental inclusion detectable.

**Confidence:** MEDIUM -- format is Claude's discretion. HTML comments are the simplest approach but the planner could choose a separate metadata file if preferred.

### Pattern 7: API Reference Detection and Symbol Linking

**What:** How the agent detects where auto-generated API Reference lives and constructs links to symbols.

**Recommendation (Claude's discretion):**

```markdown
## API Reference Detection

### Detection priority:
1. Check `.doc-writer/config.yaml` for an `api_reference` field (if present)
2. Scan for common auto-generated reference outputs:
   - `docs/api/` directory (typedoc, pdoc)
   - `docs/reference/` directory
   - `_build/` directory (Sphinx)
   - Check mkdocs.yml for plugins like `mkdocstrings`
3. If no auto-generated reference found:
   - Add a note in the page inventory: "No API reference detected.
     Inline code mentions will use plain `code` formatting without links.
     Consider setting up typedoc/pdoc/mkdocstrings for API reference generation."
   - Continue without reference linking

### Symbol Linking
When API reference is detected:
- Every inline `code` mention of a public symbol (class, function, method,
  constant, module) in prose MUST link to its reference entry
- Link format depends on doc system:
  - mkdocs-material with mkdocstrings: `::: module.Class.method` or
    `[`method()`][module.Class.method]`
  - Plain markdown: `[`method()`](./api/module.md#method)`
- Only link public API symbols -- do not link language builtins, third-party
  library symbols, or internal symbols
```

**Confidence:** MEDIUM -- detection heuristics are Claude's discretion. The core rule (all symbols must link to API reference) is locked.

### Pattern 8: Audience Calibration Workflow

**What:** How the agent applies audience-specific language calibration.

```markdown
## Audience Calibration

At the start of writing, load audience config:
- Read `.doc-writer/config.yaml` audiences array
- For each audience, note: name, skill_level, assumed_knowledge, never_assume

### Calibration rules:
- If skill_level is "beginner":
  - Define all technical terms on first use
  - Include "why" explanations for each step in tutorials
  - Provide more context for code examples
  - Never skip prerequisite explanations
- If skill_level is "intermediate":
  - Define domain-specific terms but not general programming concepts
  - Keep explanations focused and practical
  - Examples can assume basic language familiarity
- If skill_level is "advanced":
  - Assume fluency with the technology stack
  - Focus on nuance, edge cases, and advanced patterns
  - Keep explanations minimal -- focus on specifics

### Never-assume enforcement:
For each item in the audience's `never_assume` list:
- If this concept appears in any page, it MUST be explained or linked
  to an explanation
- Never use the concept as if the reader already understands it
```

**Confidence:** HIGH -- directly implements quality-rules Rule 5 and locked config schema.

### Pattern 9: blacken-docs and Doctest Awareness (AUTH-08)

**What:** Conditional formatting for Python/mkdocs projects to support blacken-docs formatting and doctest validation.

```markdown
## Python/MkDocs Formatting (Conditional)

If detected.language is "python" AND doc_system includes "mkdocs":

### Black-compatible code formatting:
- Python code blocks must follow Black formatting conventions
- Line length: 88 characters (Black default)
- Use double quotes for strings
- Trailing commas in multi-line collections
- Consistent spacing per Black rules

### Doctest-compatible patterns:
Where appropriate, format Python examples using doctest convention:

    >>> from mylib import MyClass
    >>> obj = MyClass(name="example")
    >>> obj.process()
    'expected result'

This enables validation via `python -m doctest` or `pytest --doctest-modules`.
Use doctest format for:
- Simple, single-expression examples in reference pages
- Quick demonstrations of return values

Use standard fenced code blocks for:
- Multi-step examples
- Examples requiring setup/teardown
- Examples where output is complex or non-deterministic
```

**Confidence:** HIGH -- blacken-docs is a well-known Python tool (confirmed via web search); doctest is standard Python. The agent only needs to produce compatible formatting, not run these tools.

### Anti-Patterns to Avoid

- **Duplicating diataxis templates in the agent body:** The diataxis skill is preloaded via `skills:` field. The agent prompt should reference "Apply the structural template from the diataxis skill" not paste the templates inline. Duplication wastes context and risks inconsistency.
- **Duplicating quality rules in the agent body:** Same reason. The quality-rules skill is preloaded. The agent enforces rules by reference, not by re-stating them.
- **Writing reference pages:** The Author does NOT write API reference pages (locked decision). Auto-generated reference (typedoc, pdoc, etc.) handles this. The Author links TO reference pages.
- **Page-by-page user review:** The plan is reviewed; the writing is done in one pass (locked decision). Do not build a page-by-page approval loop.
- **Inline source reading during writing:** The scan pass happens first, building a complete model. Pages draw from this model. Do not have the agent stop mid-page to go read more source files.
- **Including internal details in prose then trying to remove them:** The filter happens at scan time, not at edit time. Source content is categorized as public or internal during the scan. Internal content goes to notes, not to docs.
- **Hardcoding doc-system syntax in the agent prompt:** The agent reads the guidance file (`.doc-writer/{doc_system}.md`) at runtime. The prompt says "follow the guidance file" not "use `!!! note` for admonitions."

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Diataxis classification logic | Custom classification algorithm in agent prompt | Diataxis skill preloaded via `skills:` field | Classification guide already exists in `skills/diataxis/SKILL.md`; duplicating it wastes tokens and risks drift |
| Quality rule enforcement | Inline rule statements in agent body | Quality-rules skill preloaded via `skills:` field | Single source of truth; rules already defined in `skills/quality-rules/SKILL.md` |
| Doc-system syntax formatting | Hardcoded formatting rules per system | `.doc-writer/{doc_system}.md` guidance file read at runtime | Guidance files are per-project editable; hardcoding limits flexibility |
| YAML config parsing | Custom parsing logic | Claude's native YAML comprehension via Read tool | Claude reads YAML natively; no parsing code needed |
| File discovery | Manual path construction | Glob and Grep tools | CC tools handle file discovery reliably |
| API reference generation | Author writing reference pages | External tools (typedoc, pdoc, mkdocstrings) | Locked decision: reference is auto-generated, Author links to it |

**Key insight:** The Doc Author agent has zero runtime dependencies. It is a markdown file containing a system prompt. The "implementation" is prompt design. All supporting infrastructure (skills, config, guidance files) exists from Phase 1.

## Common Pitfalls

### Pitfall 1: Prompt Too Long for Effective Execution
**What goes wrong:** The agent's system prompt becomes so long that Claude loses track of later instructions, producing inconsistent output.
**Why it happens:** Trying to encode every possible scenario and edge case in one prompt. Combined with preloaded skills (quality-rules ~40 lines, diataxis ~220 lines), the agent context fills up.
**How to avoid:** Structure the prompt with clear section headers and numbered steps. Put the most critical instructions (workflow phases, filtering rules) early. Use checklists at the end of each phase for self-verification. Keep the agent body under 500 lines -- reference preloaded skills for shared knowledge.
**Warning signs:** Agent produces pages that follow early instructions but ignore later ones.

### Pitfall 2: Internal Notes Leaking into Output
**What goes wrong:** HTML comments or internal notes intended for the Editor appear in rendered documentation, exposing implementation details to end users.
**Why it happens:** The boundary between "for Editor" and "for end users" is not enforced strongly enough, or the note format is not reliably invisible in all doc systems.
**How to avoid:** Use standard HTML comments (`<!-- ... -->`), which are invisible in all common markdown renderers. Include an explicit "INTERNAL NOTES FOR EDITOR" header inside the comment block. Add a self-verification step: "Verify that no content between `<!--` and `-->` markers contains user-facing documentation." The Editor phase can add additional verification.
**Warning signs:** End users see implementation details, internal module names, or "INTERNAL NOTES" text in rendered docs.

### Pitfall 3: Inconsistent Cross-File References
**What goes wrong:** Page A links to a section in Page B using a different heading than what Page B actually has, creating broken cross-references.
**Why it happens:** The agent writes pages sequentially but plans them upfront. If the actual heading text drifts from the plan during writing, previously written cross-references break.
**How to avoid:** In the scan/plan phase, establish a definitive page inventory with exact filenames and anchor-friendly section titles. During writing, use a "reference registry" pattern -- maintain a running list of actual file paths and section anchors as pages are written.
**Warning signs:** Links between pages return 404 or anchor-not-found after the doc set is built.

### Pitfall 4: Code Examples That Don't Match the Library
**What goes wrong:** Code examples use incorrect API signatures, wrong parameter names, or outdated patterns because the agent is generating from general knowledge rather than from the actual source code.
**Why it happens:** The agent writes examples from training data rather than from the codebase scan results.
**How to avoid:** The upfront scan pass extracts actual API signatures, parameter types, and usage patterns. The prompt must explicitly instruct: "Base all code examples on the actual API surface discovered during the scan. Never generate API calls that were not observed in source code or tests." Self-verification: "For each code example, verify the function name, parameters, and return type match the scanned API."
**Warning signs:** Examples use method signatures or parameter names that don't exist in the actual codebase.

### Pitfall 5: README Feature List with LLM-isms
**What goes wrong:** The README key features section reads like AI-generated marketing copy -- "Seamlessly integrate...", "Leverage the power of...", "Effortlessly manage..."
**Why it happens:** Feature lists trigger LLM tendencies toward promotional language.
**How to avoid:** The prompt should include explicit anti-patterns: "Do NOT use words like: seamlessly, effortlessly, leverage, robust, powerful, cutting-edge, state-of-the-art. Each feature bullet should be a concrete, specific capability described in plain language." The humanizer pass in Phase 3 provides additional cleanup, but the Author should minimize the problem at source.
**Warning signs:** Feature list reads like a marketing brochure rather than a technical description.

### Pitfall 6: Audience Calibration Applied Inconsistently
**What goes wrong:** Early pages are well-calibrated to the audience, but later pages drift toward a different level (usually more advanced) as the agent loses track of the calibration target.
**Why it happens:** Audience configuration is read once at the start but its effect diminishes over long writing sessions as the instruction is pushed further back in context.
**How to avoid:** Include audience reminder at the start of EACH page-writing block: "AUDIENCE REMINDER: {audience_name}, skill_level: {level}. Never assume: {never_assume_list}." This keeps calibration in working context throughout the writing phase.
**Warning signs:** A beginner-targeted tutorial suddenly uses jargon without explanation on page 5, even though pages 1-4 were well-calibrated.

### Pitfall 7: Missing `skills:` Preloading (Agent Body Duplicates Skills)
**What goes wrong:** The implementer copies quality-rules or diataxis content directly into the agent's markdown body, creating duplication and risking drift when skills are updated.
**Why it happens:** Not understanding that `skills:` in agent frontmatter preloads the full skill content at startup.
**How to avoid:** Confirmed from CC documentation: "The full content of each skill is injected into the subagent's context, not just made available for invocation." The agent body should REFERENCE skills ("Apply the structural template from the preloaded diataxis skill") not DUPLICATE their content.
**Warning signs:** The agent file exceeds 800 lines and contains content that also appears in skill files.

## Code Examples

### Agent File Structure (What Phase 2 Produces)

```markdown
# Source: CC subagent docs + Phase 1 established pattern
---
name: doc-author
description: Writes draft library documentation using Diataxis framework. Produces audience-calibrated, internal-detail-free docs with working code examples.
tools: Read, Write, Glob, Grep, Bash
model: inherit
skills:
  - doc-writer:quality-rules
  - doc-writer:diataxis
---

You are a Doc Author agent. You write library documentation from the
end user's perspective, never from the builder's perspective.

## How You Work

You operate in two phases:
1. **Plan**: Scan the codebase and propose a page inventory
2. **Write**: After user approval, write all pages in one pass

[... full prompt content ...]
```

### Page Inventory Output Format

```markdown
## Proposed Documentation

Based on my scan of the codebase, here is the proposed page inventory:

| # | Type | Title | Key Sections |
|---|------|-------|--------------|
| 1 | tutorial | Getting Started with FastAPI-Cache | Prerequisites, Install, First cached endpoint, What you learned |
| 2 | how-to | How to Configure Cache Backends | Prerequisites, Redis setup, Memcached setup, Custom backends, Troubleshooting |
| 3 | how-to | How to Invalidate Cache | Prerequisites, Manual invalidation, Pattern-based invalidation, TTL configuration |
| 4 | explanation | Understanding Cache Strategies | Context, Cache-aside pattern, Write-through pattern, Tradeoffs |
| 5 | (readme) | README.md | Title, badges, description, quick start, features, docs link, license |
| 6 | (maintainer) | MAINTAINER.md | Dev setup, tasks, architecture, CI/CD, release process |

**API Reference:** Detected at `docs/api/` (generated by mkdocstrings).
All inline code mentions will link to corresponding reference entries.

**Notes:**
- I've omitted a reference page since API reference is auto-generated
- Pages 1-4 target your configured audience: "Python web developers" (intermediate)

Would you like to modify this plan? You can add, remove, or change any entry.
```

### Internal Notes Format (HTML Comments)

```markdown
<!-- INTERNAL NOTES FOR EDITOR - DO NOT INCLUDE IN RENDERED OUTPUT

## Source References
- `connect()` implementation: src/client.py:45-89
- Connection pooling: src/_internal/pool.py (pool_size=5 default)
- Retry logic: src/_internal/retry.py (exponential backoff, max_retries=3)

## Accuracy Notes
- The timeout parameter defaults to 30s, not 60s as one might expect
- Error codes are defined in src/errors.py -- only ClientError and
  ServerError are public; InternalError is private

## API Reference Links Used
- [`Client`](../api/client.md#Client)
- [`Client.connect()`](../api/client.md#Client.connect)
- [`ClientError`](../api/errors.md#ClientError)

## Implementation Details (for accuracy checking only)
- Connection pooling uses asyncio.Queue internally
- Rate limiting implemented via token bucket (not exposed to users)
-->

# How to Connect to the Server

This guide shows you how to establish a connection...
```

### Audience Calibration in Practice

```markdown
## Per-Page Audience Reminder (included in prompt for each page)

Before writing each page, re-read the audience configuration:

**Primary audience:** Python web developers building REST APIs
**Skill level:** intermediate
**Assumed knowledge:** Python 3.x basics, pip, HTTP concepts, JSON
**Never assume:** async/await patterns, database ORMs, Docker

CALIBRATION CHECK before finalizing each page:
- [ ] No jargon used without definition (check against never_assume list)
- [ ] Explanation depth matches skill_level
- [ ] Prerequisites section lists what's needed from assumed_knowledge
- [ ] Examples use patterns appropriate for this audience level
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Agent system prompts copy skill content inline | `skills:` frontmatter preloads full skill content | CC subagents update 2025 | Agent bodies are shorter and reference skills; no duplication needed |
| Agent tool called "Task" | Agent tool (renamed from Task in CC v2.1.63) | 2025 | Use `Agent(...)` not `Task(...)` in new code; old alias still works |
| Doc generation as single pass | Two-phase plan-then-write with user approval | Phase 2 user decision | More control for project author; prevents wasted effort on unwanted pages |
| Examples from source code only | Source code AND test files | Phase 2 user decision | Tests provide realistic usage patterns and edge cases |
| Agent writes API reference | Auto-generated reference (typedoc, pdoc) + narrative docs | Phase 2 user decision | Author focuses on narrative; reference tools handle API docs |

**Deprecated/outdated:**
- Single-pass documentation generation without user plan approval -- replaced by two-phase workflow
- Writing API reference pages manually -- replaced by linking to auto-generated reference
- Task tool name -- renamed to Agent tool in CC v2.1.63 (Task still works as alias)

## Open Questions

1. **Optimal prompt length for the agent body**
   - What we know: CC subagents have full context windows. The diataxis skill (~220 lines) and quality-rules skill (~40 lines) are preloaded, consuming ~260 lines of context.
   - What's unclear: The practical upper limit for an agent system prompt before instruction-following degrades. This agent needs to encode a complex multi-phase workflow.
   - Recommendation: Target 300-400 lines for the agent body. Use clear section headers and numbered steps. If instructions are being ignored in testing, break into shorter focused sections. Monitor for instruction-following degradation during verification.

2. **`${CLAUDE_PLUGIN_ROOT}` availability in agent files**
   - What we know: This variable works in skills and commands. Phase 1 research flagged uncertainty about agent files.
   - What's unclear: Whether `${CLAUDE_PLUGIN_ROOT}` resolves in agent body text.
   - Recommendation: The agent does not need to reference plugin-internal files directly. It reads project-level files (`.doc-writer/config.yaml`, `.doc-writer/{doc_system}.md`, `.doc-writer/rules.md`) which are in the project directory. If plugin-internal file access is needed, route through a skill.

3. **How the agent handles very large codebases**
   - What we know: The scan pass reads source, tests, and existing docs. For large projects, this may exceed context limits.
   - What's unclear: Practical limits on how much source code the agent can scan before context fills up.
   - Recommendation: The scan instructions should prioritize: (1) public API surface (exports, public classes/functions), (2) test files for usage patterns, (3) existing docs. For large projects, scan summaries rather than full file contents. Add a note: "If the codebase is too large to scan completely, focus on the public API surface and test files. Note gaps in the page inventory for user awareness."

4. **Multi-audience page calibration**
   - What we know: Config supports multiple audiences. Each page targets an audience based on its type and content.
   - What's unclear: How to calibrate a single page when audiences have conflicting needs (e.g., a tutorial for beginners vs. an explanation for advanced users).
   - Recommendation: Each page targets the primary audience unless its content is explicitly aimed at a different audience level. The page inventory should note which audience each page targets. Phase 4 (User Persona) will validate from each audience's perspective.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual CC session testing (no automated test framework) |
| Config file | None -- this is a markdown-file plugin with no executable code |
| Quick run command | `claude --plugin-dir .` then invoke Doc Author via natural language |
| Full suite command | Manual: run Doc Author on a sample project, verify all AUTH requirements |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | Classifies each page as tutorial/how-to/reference/explanation before writing | manual (CC session) | Run Author on sample project, verify page inventory shows types | N/A -- markdown plugin |
| AUTH-02 | Same-type pages follow same structural template | manual (compare output) | Write 2+ how-to guides, compare section structure | N/A |
| AUTH-03 | No internal details in output | manual (search output) | Grep output docs for test utils, CI config, dev scripts | N/A |
| AUTH-04 | Output uses selected doc-system syntax | manual (inspect output) | Verify mkdocs-material admonitions/tabs or plain-markdown callouts | N/A |
| AUTH-05 | README.md follows template | manual (inspect output) | Verify README has: title, badges, description, quick start, features, docs link, license | N/A |
| AUTH-06 | MAINTAINER.md follows template | manual (inspect output) | Verify MAINTAINER has: dev setup, tasks, architecture, CI/CD, release, decision log | N/A |
| AUTH-07 | Every feature page has working code examples | manual (inspect output) | Verify each page has at least one realistic code example, first example is self-contained | N/A |
| AUTH-08 | Python/mkdocs supports blacken-docs formatting | manual (run blacken-docs) | Run `blacken-docs docs/*.md` on output -- should produce no changes | N/A |
| AUTH-09 | Vocabulary calibrated to audience | manual (read output) | Verify no jargon used without explanation for configured audience | N/A |

### Sampling Rate
- **Per task commit:** Manual: load plugin with `claude --plugin-dir .`, run Doc Author on test project
- **Per wave merge:** Manual: full plan-then-write cycle on a sample project, verify all 9 AUTH requirements
- **Phase gate:** All 9 AUTH requirements verified via manual CC session before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Create or identify a sample library project for testing Doc Author output (needs: source code, tests, existing docs or README, config via `/doc-writer:setup`)
- [ ] Run `/doc-writer:setup` on the sample project to create `.doc-writer/config.yaml` with audience data
- [ ] Verify that the test project's `.doc-writer/` directory has config, guidance file, and rules file before testing Doc Author

## Sources

### Primary (HIGH confidence)
- [CC Skills documentation](https://code.claude.com/docs/en/skills) -- skill preloading into subagents via `skills:` frontmatter field, skill content loading, invocation control
- [CC Subagents documentation](https://code.claude.com/docs/en/sub-agents) -- agent file format, frontmatter fields, system prompt as markdown body, skill preloading: "The full content of each skill is injected into the subagent's context, not just made available for invocation"
- [CC Plugins documentation](https://code.claude.com/docs/en/plugins) -- plugin structure, agents/ directory, namespace format
- [Diataxis framework](https://diataxis.fr/) -- content classification, four doc types, structural templates
- [blacken-docs](https://github.com/adamchainz/blacken-docs) -- Python code formatting in markdown files, Black-compatible output
- Phase 1 artifacts -- established plugin structure, agent stubs, skill files, config schema

### Secondary (MEDIUM confidence)
- [I'd Rather Be Writing: Diataxis review](https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework) -- practical Diataxis adoption insights
- Phase 2 CONTEXT.md -- locked user decisions governing workflow, templates, and example strategy

### Tertiary (LOW confidence)
- None -- all key claims verified against official documentation or locked user decisions

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- agent file format verified against CC docs; all supporting infrastructure exists from Phase 1
- Architecture: HIGH -- all architectural patterns derive from locked user decisions (two-phase workflow, scan-then-write, example sourcing, templates) or verified CC features (skill preloading)
- Pitfalls: HIGH -- prompt length, internal note leaking, cross-reference consistency, and LLM-ism patterns are well-documented concerns in LLM prompt engineering

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (CC subagent system is stable; locked user decisions do not change; 30-day validity appropriate)
