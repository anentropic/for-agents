# Phase 4: User Persona and Full Pipeline - Research

**Researched:** 2026-03-03
**Domain:** Claude Code agent system prompt design, goal-oriented documentation testing, scenario generation, verdict-based feedback, revision loop protocol, multi-audience simulation
**Confidence:** HIGH -- builds on verified CC plugin architecture from Phases 1-3; deliverables are a fully expanded agent file (`agents/doc-persona.md`) and a documented revision loop protocol; all supporting infrastructure exists

## Summary

Phase 4 delivers the User Persona agent -- the audience validation layer in the three-agent pipeline. The primary deliverable is expanding the existing `agents/doc-persona.md` stub (created in Phase 1) with a comprehensive system prompt that enables Claude to: (1) generate 3-5 realistic user journey scenarios from project context and audience configuration, (2) test each scenario by step-by-step simulation through the documentation, and (3) produce structured verdicts (PASS/FAIL/PARTIAL) with specific gap identification. A secondary deliverable is documenting the revision loop protocol that governs how verdicts flow back through the pipeline.

Unlike the Author (which writes content) and the Editor (which edits content), the Persona is fundamentally a reader and evaluator. It simulates the experience of an end user approaching the documentation with a goal, navigating from the homepage, following cross-references, and attempting to accomplish that goal using only what the docs provide. The Persona reads the Editor-cleaned docs (no HTML comments), the audience configuration from `.doc-writer/config.yaml`, and persisted scenarios from `.doc-writer/scenarios.yaml`. It produces `.doc-writer/persona-report.md` as its primary output artifact and manages the scenarios file for persistence across runs.

The revision loop protocol defines how Persona verdicts drive the pipeline. Only FAIL verdicts trigger automated revision passes. PARTIAL verdicts are surfaced to the project author for lightweight approval of specific fixes. The Author revises only targeted pages based on Persona gap reports, the Editor re-runs on changed pages (with a full terminology scan across all files), and the Persona re-evaluates. A maximum of 2-3 revision passes runs before convergence failure is escalated. The pipeline orchestration command (`/doc:write`) is Phase 5 -- Phase 4 defines the protocol and the Persona's role in it.

**Primary recommendation:** Structure the agent prompt as a three-phase workflow: (1) scenario generation from audience config and doc structure, (2) step-by-step simulation per scenario starting from the docs homepage, (3) verdict and gap reporting. The Persona stub's frontmatter needs updating to include the Write tool (for outputting reports and scenarios). The revision loop protocol should be documented in the agent prompt as "what the Persona expects" rather than "what the Persona orchestrates."

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Persona reads only generated docs and audience config (no source code) -- simulates a real end user
- Goals inferred from docs structure filtered through the audience's skill level -- beginner Personas prioritize setup/basics, advanced ones target deeper features
- Domain context (what the user already knows about the problem space) is enriched via web search at /doc:setup time and persisted to the audience definition in config -- Persona reads the already-enriched config at runtime without its own web search
- Setup Q&A captures the user's "discovery story" (how/why they found the lib) to inform Persona's perspective
- Scenarios persist to .doc-writer/scenarios.yaml and are reused across runs; Persona regenerates when docs change significantly (new pages, major edits)
- Step-by-step simulation: Persona traces through docs as if following instructions to accomplish each goal
- For each scenario: "I want to do X -- where do I start? Can I find it? Do the steps make sense? Are code examples present and realistic?"
- Code example verification is existence + plausibility only (does it exist? does it look complete and realistic? does it match the explanation?) -- no execution (per REQUIREMENTS.md out-of-scope)
- All scenarios start from the docs homepage (README or doc site index) and navigate from there -- tests the real discovery path every time
- Persona follows cross-reference links and table of contents to find information, testing the interconnected doc experience
- Verdicts are based on goal achievability:
  - PASS: smooth path from start to finish, user can accomplish the goal
  - PARTIAL: goal is achievable but with friction (unclear steps, missing context, confusing order)
  - FAIL: user cannot accomplish the goal at all (missing page, dead-end, wrong instructions)
- Structured per-scenario report written to .doc-writer/persona-report.md (overwritten each run)
- Each scenario report includes: verdict, steps attempted, where it got stuck (page + section), what was missing/wrong, suggested fix
- Only FAIL verdicts trigger automated revision passes
- PARTIAL verdicts: Persona suggests specific fixes, presents them to project author for approval; approved fixes are applied directly without going back through the full pipeline
- Only FAIL verdicts trigger revision -- PARTIALs handled separately via project author approval
- Author revises targeted pages only (not full doc set re-generation) based on specific gaps from Persona report
- Editor re-runs on changed pages for humanizer and cross-reference passes, plus a full terminology scan across all files (term changes can ripple)
- Maximum 2-3 revision passes; if FAILs remain after max passes, escalate to project author with full context (what was tried, why it didn't converge)
- Pipeline command (Phase 5's /doc:write) orchestrates the Author > Editor > Persona sequence and revision routing; Persona just reports verdicts and gaps
- When multiple audiences are configured, a separate Persona agent runs for each audience in parallel (from PERS-05)
- Each Persona uses its own audience definition (skill level, assumed knowledge, domain context) to generate audience-specific scenarios
- Independent verdicts per audience -- a PASS for advanced users doesn't excuse a FAIL for beginners

### Claude's Discretion
- Exact format of scenarios.yaml schema (how scenarios are stored and diffed for staleness)
- How to detect "significant" doc changes that trigger scenario regeneration
- Internal mechanics of step-by-step simulation (how Persona tracks its navigation path)
- Exact threshold for what counts as "plausible" in code example checks
- How to structure the PARTIAL fix suggestions for project author presentation

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PERS-01 | End-User Persona agent generates 3-5 realistic end-user journey scenarios from project context without manual authoring | Scenario generation phase in agent prompt reads audience config (skill_level, assumed_knowledge, discovery_story) and doc structure (page titles, headings, table of contents) to infer realistic user goals; scenarios persisted to `.doc-writer/scenarios.yaml` |
| PERS-02 | Scenarios are goal-oriented -- agent tries to accomplish tasks using only the docs (not checklist-checking) | Step-by-step simulation phase traces through docs from homepage, following cross-references and navigation, attempting to accomplish each scenario's goal; verdicts based on goal achievability, not criteria lists |
| PERS-03 | Each scenario gets a clear verdict: PASS, FAIL, or PARTIAL, with specific gap identification | Verdict and gap reporting phase produces structured per-scenario reports with verdict, steps attempted, stuck point (page + section), what was missing/wrong, and suggested fix; written to `.doc-writer/persona-report.md` |
| PERS-04 | Pipeline revision loop has a max pass limit (2-3) and convergence rules -- only BLOCKING issues trigger revision | Revision loop protocol documented in agent prompt: only FAIL verdicts trigger revision passes; PARTIAL verdicts go through lightweight project author approval; max 2-3 passes with escalation on non-convergence; Persona reports, Phase 5 orchestrates |
| PERS-05 | When multiple audiences are configured, a separate End-User Persona agent is instantiated for each and runs in parallel | Agent prompt supports audience-specific scenario generation via audience parameter; Phase 5 orchestrator spawns one Persona agent per audience with independent verdicts; multi-audience design uses same agent file with different audience context |
</phase_requirements>

## Standard Stack

### Core

| Component | Format | Purpose | Why Standard |
|-----------|--------|---------|--------------|
| Agent file (`agents/doc-persona.md`) | YAML frontmatter + markdown body | Persona subagent definition with full system prompt | CC subagent format -- frontmatter for metadata, body for system prompt; established in Phases 1-3 |
| Skills preloading (`skills:` field) | Frontmatter array | Injects quality-rules content into agent context | CC subagent feature -- quality-rules skill preloaded at startup; provides Rule 4 (Cross-References) and Rule 5 (Audience Calibration) for validation perspective |
| Config reading (`.doc-writer/config.yaml`) | YAML via Read tool | Audience definitions with skill_level, assumed_knowledge, never_assume, domain context, discovery story | Established in Phase 1; Persona reads at runtime for audience perspective |
| Scenario persistence (`.doc-writer/scenarios.yaml`) | YAML via Read/Write tool | Persisted scenarios reused across runs; regenerated when docs change significantly | New artifact created by Persona; enables stable scenario evaluation across pipeline runs |
| Persona report (`.doc-writer/persona-report.md`) | Markdown via Write tool | Structured per-scenario verdicts with gap identification | New artifact created by Persona; consumed by Phase 5 pipeline orchestrator for revision routing |

### Supporting

| Component | Format | Purpose | When to Use |
|-----------|--------|---------|-------------|
| Editor-cleaned docs | Markdown files in `paths.docs_root` | Documentation pages without HTML comments (Editor strips them) | Primary input -- Persona reads these to simulate end-user experience |
| README.md | Markdown in project root | Docs homepage for scenarios that start from project discovery | Starting point for scenario navigation |
| Editor report (`.doc-writer/editor-report.md`) | Markdown | Previous Editor findings (if Persona wants context on what was already fixed) | Optional reference -- not required for Persona operation |
| Terminology map (`.doc-writer/terminology.yaml`) | YAML | Not directly used by Persona -- but term consistency affects Persona's reading experience | Indirect -- Persona benefits from Editor's terminology work |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| YAML for scenarios | JSON or markdown | YAML is consistent with config.yaml and terminology.yaml; human-readable; Claude natively reads/writes YAML |
| Markdown for persona report | JSON or YAML structured report | Markdown is human-readable for project author review; consistent with editor-report.md format; structured enough for Phase 5 pipeline parsing |
| Single Persona agent file for all audiences | Separate agent file per audience | Single file is simpler; audience context passed as parameter at invocation; no file duplication |
| Step-by-step simulation in prompt | External testing script | Prompt-based simulation matches the project's zero-dependency approach; Claude simulates the user experience naturally through reading and reasoning |

## Architecture Patterns

### Agent File Structure

The `agents/doc-persona.md` file needs its frontmatter updated from the Phase 1 stub:

```markdown
---
name: doc-persona
description: Validates documentation from the end user's perspective. Generates goal-oriented scenarios and tests docs by attempting to accomplish tasks using only the documentation.
tools: Read, Write, Glob, Grep
model: inherit
skills:
  - doc-writer:quality-rules
---

[System prompt body -- the Phase 4 deliverable]
```

**IMPORTANT: Frontmatter change required.** The Phase 1 stub has `tools: Read, Glob, Grep` (no Write). The Persona needs Write to produce `.doc-writer/persona-report.md` and `.doc-writer/scenarios.yaml`. This is a necessary update to the existing stub. The code_context section of CONTEXT.md describes the Persona as a "read-only agent that reports but doesn't modify" -- this refers to not modifying documentation files, not to having no Write tool. The Persona writes its own artifacts (report and scenarios) but never modifies doc pages.

**Confidence:** HIGH -- Write tool is required for output artifacts; all other agents (Author, Editor) use Write for their artifacts.

### Pattern 1: Three-Phase Agent Workflow (Generate, Simulate, Report)

**What:** The Persona operates in three sequential phases: (1) generate or load scenarios, (2) simulate each scenario through the docs, (3) produce verdict report.

**When to use:** Always -- this is the Persona's core workflow.

**Prompt structure:**

```markdown
## How You Work

You validate documentation by attempting to use it as an end user would.
You operate in three phases:

1. **Generate Scenarios** -- create or load goal-oriented user journey scenarios
2. **Simulate** -- for each scenario, trace through docs attempting to accomplish the goal
3. **Report** -- produce structured verdicts with gap identification

### Pre-Processing
1. Read `.doc-writer/config.yaml` for audience definition (the audience you represent)
2. Read existing `.doc-writer/scenarios.yaml` if it exists
3. Discover all documentation files in `paths.docs_root` using Glob
4. Identify the docs homepage (README.md or index page)

### Phase 1: Scenario Generation
[See Pattern 2]

### Phase 2: Step-by-Step Simulation
[See Pattern 3]

### Phase 3: Verdict and Gap Reporting
[See Pattern 4]
```

**Confidence:** HIGH -- workflow directly implements locked user decisions.

### Pattern 2: Scenario Generation from Audience Context

**What:** The Persona generates 3-5 realistic user journey scenarios by reading audience configuration and doc structure. Scenarios are goal-oriented -- each describes a concrete task the user wants to accomplish.

**Implementation approach:**

```markdown
## Phase 1: Scenario Generation

### Step 1: Read Audience Context
From `.doc-writer/config.yaml`, extract the audience you represent:
- `name`: who this user is (e.g., "Python web developers building REST APIs")
- `skill_level`: beginner, intermediate, or advanced
- `assumed_knowledge`: what they already know
- `never_assume`: what must always be explained
- `domain_context`: enriched understanding of the problem space (from setup)
- `discovery_story`: how/why they found this library (from setup)

### Step 2: Scan Doc Structure
Read the docs homepage and scan all page titles and headings:
- What pages exist? (tutorials, how-tos, explanations)
- What topics are covered?
- What is the navigation structure?
- What is the "getting started" path?

Do NOT read source code. You are simulating an end user who has
only the documentation available.

### Step 3: Check for Existing Scenarios
If `.doc-writer/scenarios.yaml` exists:
- Read existing scenarios
- Check if docs have changed significantly since scenarios were generated
  (new pages added, pages removed, major structural changes)
- If docs are substantially the same: reuse existing scenarios
- If docs have changed significantly: regenerate scenarios

### Step 4: Generate Scenarios
Based on the audience context and doc structure, generate 3-5 scenarios.
Each scenario must be:
- A concrete goal: "I want to [do something specific]"
- Filtered through the audience's skill level:
  - Beginner: prioritize setup, installation, first use, basic concepts
  - Intermediate: task-oriented goals, configuration, common workflows
  - Advanced: edge cases, advanced features, performance tuning, extensibility
- Realistic for someone who found this library via the discovery_story
- Testable by navigating the docs (not by running code)

### Step 5: Persist Scenarios
Write scenarios to `.doc-writer/scenarios.yaml`
```

**Scenario YAML schema (Claude's discretion recommendation):**

```yaml
# .doc-writer/scenarios.yaml
# Generated by Persona agent. Regenerated when docs change significantly.

version: 1
generated_for:
  audience: "Python web developers building REST APIs"
  skill_level: intermediate
  doc_pages_hash: "{hash or list of page paths + modification context}"

scenarios:
  - id: S1
    goal: "Set up the library and make my first API call"
    starting_point: "README.md"
    audience_relevance: "First thing any new user needs to do"
    expected_path:
      - "README.md -> Quick Start section"
      - "Getting Started tutorial (if linked)"

  - id: S2
    goal: "Configure authentication for my REST API"
    starting_point: "README.md"
    audience_relevance: "Common task for web developers using this library"
    expected_path:
      - "README.md -> docs link"
      - "How-to guide on authentication (if exists)"

  - id: S3
    goal: "Understand how caching works and configure it for my use case"
    starting_point: "README.md"
    audience_relevance: "Performance-related task relevant to intermediate developers"
    expected_path:
      - "README.md -> docs link"
      - "Explanation or how-to on caching"

  - id: S4
    goal: "Handle errors gracefully in production"
    starting_point: "README.md"
    audience_relevance: "Production readiness concern"
    expected_path:
      - "How-to or reference on error handling"

  - id: S5
    goal: "Migrate from v1 to v2 of the library"
    starting_point: "README.md"
    audience_relevance: "Upgrade path for existing users"
    expected_path:
      - "Migration guide or changelog"
```

**Detecting "significant" doc changes (Claude's discretion recommendation):**

The simplest reliable approach: store the list of doc page filenames in the scenarios file. On subsequent runs, compare current doc files against the stored list. Regenerate scenarios if:
- New pages were added (new topics available)
- Pages were removed (topics no longer exist)
- The number of pages changed by more than ~30%

This avoids needing content hashing or modification timestamps. Page-level structural changes (new pages, removed pages) are the primary triggers for scenario staleness.

**Confidence:** HIGH -- scenario generation directly implements PERS-01 and locked decisions about audience-filtered goal generation.

### Pattern 3: Step-by-Step Simulation

**What:** For each scenario, the Persona traces through the documentation as if it were an end user attempting to accomplish the goal. It starts from the docs homepage and navigates using only what the docs provide.

**Implementation approach:**

```markdown
## Phase 2: Step-by-Step Simulation

For each scenario, simulate the end-user experience:

### Starting Point
Every scenario starts at the docs homepage:
- If README.md exists in the project root: start there
- If an index page exists in docs_root: start there
- Record: "Starting at: {page}"

### Navigation Rules
You can ONLY navigate using information visible in the docs:
- Follow explicit links (markdown links, cross-references)
- Follow table of contents and navigation structure
- Follow "Next steps" or "See also" sections
- You CANNOT use Grep to search across files -- a real user
  cannot grep the doc site

Exception: you MAY use Glob to discover what pages exist (simulating
a doc site's sidebar/navigation), but you must navigate to pages
via links or navigation structure, not by reading random files.

### Simulation Steps
For each step in the scenario:
1. Read the current page
2. Ask: "Can I find information relevant to my goal here?"
3. If yes: follow the relevant content
   - Are the instructions clear?
   - Are code examples present and plausible?
   - Do the steps make logical sense?
   - Is the language appropriate for my skill level?
4. If no: look for navigation to the right page
   - Is there a link to follow?
   - Is the topic mentioned in a table of contents?
   - Is there a "see also" or "related" section?
5. Record each step: page visited, what was found, what was missing

### Code Example Verification
When encountering code examples during simulation:
- Does the example exist? (not just "see the API reference")
- Does it look complete? (imports, setup, actual call, expected result)
- Does it look realistic? (not placeholder values like foo/bar/42)
- Does it match the surrounding explanation?
- Do NOT attempt to verify correctness by reading source code
  (you are an end user without source access)

### Tracking Navigation Path
Maintain a running log of your navigation:
- Page visited
- Section read
- Link followed (or dead end hit)
- Information found (or not found)
- Friction encountered (confusing wording, unclear steps, missing context)
```

**Confidence:** HIGH -- simulation approach directly implements PERS-02 and locked decisions about step-by-step testing methodology.

### Pattern 4: Verdict and Gap Reporting

**What:** After simulating all scenarios, the Persona produces a structured report with per-scenario verdicts and specific gap identification.

**Implementation approach:**

```markdown
## Phase 3: Verdict and Gap Reporting

### Verdict Criteria

For each scenario, assign a verdict based on goal achievability:

**PASS**: The user can accomplish the goal from start to finish.
- Clear path from docs homepage to the relevant content
- Instructions are complete and understandable
- Code examples are present and plausible
- No significant friction or confusion

**PARTIAL**: The goal is achievable but with friction.
- The information exists but is hard to find
- Steps are present but unclear or confusing
- Missing context that slows the user down
- Code examples are present but incomplete or unclear
- The user would probably succeed but with frustration

**FAIL**: The user cannot accomplish the goal at all.
- Required information is missing entirely (no page, no section)
- Instructions lead to a dead end
- Critical steps are wrong or contradictory
- No code examples for a code-heavy task
- The user would give up or seek help outside the docs

### Gap Identification
For each PARTIAL or FAIL verdict, identify the specific gap:
- **Where**: exact page and section where the problem occurs
- **What**: what is missing, wrong, or unclear
- **Why**: why this prevents (FAIL) or hinders (PARTIAL) the goal
- **Suggested fix**: what would resolve the gap

### PARTIAL Fix Suggestions
For PARTIAL verdicts, structure fix suggestions for project author review:
- Each suggestion is a specific, actionable change
- Format: "In {page}, section {section}: {what to change and why}"
- These are presented to the project author for approval
- Approved fixes are applied directly without full pipeline re-run

### Report Writing
Write the report to `.doc-writer/persona-report.md`
(overwritten each run)
```

**Persona report structure:**

```markdown
# Persona Report

**Generated:** {date}
**Audience:** {audience name} ({skill_level})
**Scenarios tested:** {count}
**Results:** {PASS count} PASS, {PARTIAL count} PARTIAL, {FAIL count} FAIL

## Summary

{2-3 sentences on the overall documentation experience from this audience's
perspective. What works well? What are the biggest gaps?}

---

## Scenario 1: {goal}

**Verdict:** {PASS|PARTIAL|FAIL}

### Navigation Path

1. Started at: {page}
   - Found: {what was found}
   - Followed: {link or navigation used}
2. Navigated to: {page}
   - Found: {what was found}
   - {Friction or success noted}
3. ...

### Gap Analysis

**Where:** {page} > {section}
**What:** {description of the gap}
**Impact:** {why this affects the user's goal}
**Suggested Fix:** {specific, actionable change}

---

## Scenario 2: {goal}

[Same structure]

---

## Revision Recommendations

### FAIL Issues (trigger revision)

| Scenario | Page | Gap | Suggested Fix |
|----------|------|-----|---------------|
| S1 | docs/getting-started.md | Missing installation section | Add installation steps with pip command |

### PARTIAL Issues (for project author approval)

| Scenario | Page | Gap | Suggested Fix |
|----------|------|-----|---------------|
| S3 | docs/how-to/caching.md | Unclear cache invalidation steps | Rewrite step 3 with specific examples |
```

**Confidence:** HIGH -- report structure directly implements PERS-03 and locked decisions about verdict criteria and gap identification format.

### Pattern 5: Revision Loop Protocol

**What:** The protocol governing how Persona verdicts flow back through the pipeline. Phase 4 defines the protocol; Phase 5 implements the orchestration.

**The Persona's role in the revision loop:**

```markdown
## Revision Loop Protocol

The Persona does NOT orchestrate the revision loop. It reports verdicts.
The pipeline orchestrator (Phase 5's /doc:write command) handles routing.

### What the Persona produces for the revision loop:
1. Per-scenario verdicts (PASS/FAIL/PARTIAL)
2. For FAIL: specific gap identification with page, section, what's missing
3. For PARTIAL: specific fix suggestions for project author review

### How the revision loop works (for Persona's awareness):

Pass 1: Author writes > Editor edits > Persona evaluates
  |
  If all PASS: done
  If any FAIL: revision pass triggered
  If only PARTIAL: fixes presented to project author for approval
  |
Pass 2 (revision): Author revises targeted pages > Editor re-runs > Persona re-evaluates
  |
  If all PASS: done
  If any FAIL: one more revision pass
  If only PARTIAL: fixes presented to project author
  |
Pass 3 (final revision): Author revises > Editor re-runs > Persona re-evaluates
  |
  If all PASS: done
  If any FAIL: ESCALATE to project author with full context
  If only PARTIAL: fixes presented to project author

### Escalation format (when FAILs remain after max passes):

"After {N} revision passes, the following scenarios still FAIL:
- {scenario}: {what was tried, why it didn't converge}
- {scenario}: {what was tried, why it didn't converge}

These issues may require significant restructuring or new content
that the automated pipeline cannot resolve. Please review and address
manually."

### Key rules for Persona during revision:
- Re-evaluate ALL scenarios on each pass (not just previously FAIL ones)
  because changes to one page can affect navigation to other pages
- Reuse the same scenarios across revision passes (do not regenerate)
- Compare current verdicts with previous pass verdicts to track convergence
- A scenario can improve (FAIL -> PARTIAL -> PASS) or regress (PASS -> PARTIAL)
  if changes broke something
```

**Confidence:** HIGH -- protocol directly implements PERS-04 and locked decisions about revision routing, max passes, and escalation.

### Pattern 6: Multi-Audience Parallel Execution

**What:** When multiple audiences are configured, a separate Persona agent runs for each audience with independent scenarios and verdicts.

**Implementation approach:**

The Persona agent file is designed to represent ONE audience. The Phase 5 orchestrator spawns multiple instances:

```markdown
## Multi-Audience Support

This agent represents a single audience. When multiple audiences are
configured in `.doc-writer/config.yaml`, the pipeline orchestrator
spawns one instance of this agent per audience.

### What the agent receives:
- The full config file (it reads the audience array)
- An indication of WHICH audience it represents (by index or name)
  via the invocation prompt

### What the agent produces:
- Scenarios specific to its audience
- Verdicts specific to its audience's perspective
- A report section clearly labeled with the audience name

### Scenario generation differences by audience:
- Each audience generates its own 3-5 scenarios
- Beginner audiences: setup, installation, first use, basic concepts
- Intermediate audiences: common tasks, configuration, workflows
- Advanced audiences: edge cases, advanced features, performance, extensibility

### Verdict independence:
- A PASS for advanced users does NOT excuse a FAIL for beginners
- Each audience's verdicts are evaluated independently
- Revision is triggered if ANY audience has a FAIL
```

**For multi-audience report merging:** The Phase 5 orchestrator would collect individual persona reports. For Phase 4, each Persona instance writes its report independently. The scenarios file should be audience-specific: `.doc-writer/scenarios-{audience-name}.yaml` or stored with audience context in a single scenarios file.

**Recommendation for scenarios file naming:** Use a single `.doc-writer/scenarios.yaml` file with audience sections:

```yaml
version: 1
audiences:
  - name: "Python web developers"
    generated_at: "2026-03-03"
    doc_pages: ["README.md", "docs/getting-started.md", "docs/how-to/configure.md"]
    scenarios:
      - id: S1
        goal: "Set up the library and make my first API call"
        # ...

  - name: "Data engineers"
    generated_at: "2026-03-03"
    doc_pages: ["README.md", "docs/getting-started.md", "docs/how-to/configure.md"]
    scenarios:
      - id: S1
        goal: "Connect the library to my data pipeline"
        # ...
```

**For persona report with multi-audience:** Similarly, `.doc-writer/persona-report.md` should be structured with audience sections, or the orchestrator collects separate reports.

**Recommendation:** Since each Persona instance runs independently, each writes to an audience-specific report file: `.doc-writer/persona-report-{audience-name}.md`. The Phase 5 orchestrator collects and presents them together. This avoids write conflicts during parallel execution and keeps each report self-contained.

**Confidence:** HIGH -- multi-audience approach directly implements PERS-05 and locked decisions about parallel execution with independent verdicts.

### Pattern 7: Audience Config Schema Extensions

**What:** The audience definition in `.doc-writer/config.yaml` needs two additional fields referenced in CONTEXT.md decisions: `domain_context` and `discovery_story`. These are populated during setup (Phase 1's `/doc-writer:setup` command) and consumed by the Persona.

**Expected audience config structure:**

```yaml
audiences:
  - name: "Python web developers building REST APIs"
    skill_level: intermediate
    assumed_knowledge:
      - "Python 3.x basics"
      - "pip package management"
      - "HTTP concepts and REST APIs"
    never_assume:
      - "async/await patterns"
      - "database ORMs"
    domain_context: "Developers working with web frameworks like Flask or FastAPI who need to add caching to their API endpoints. They understand HTTP but may not have used caching libraries before."
    discovery_story: "Found this library while searching for 'Python API response caching' or saw it recommended in a FastAPI performance optimization guide."
```

**Note:** The `domain_context` and `discovery_story` fields are enriched via web search during setup (per locked decision). The setup skill (Phase 1) would need a minor extension to capture these fields during the audience Q&A flow. This is a small, bounded change to the existing setup skill.

**Confidence:** MEDIUM -- the config schema extension is straightforward but the setup skill modification is outside Phase 4's primary scope. The planner should decide whether to include the setup skill update in Phase 4 or defer it.

### Anti-Patterns to Avoid

- **Persona reading source code:** The Persona simulates an end user. End users do not have access to source code. The Persona must ONLY use documentation files and the audience configuration. Reading source code would defeat the purpose of testing whether the docs are self-sufficient.

- **Checklist-based evaluation:** The Persona does NOT check whether docs have a "getting started" section, whether code examples exist, or whether headings are consistent. That is the Editor's job. The Persona tries to ACCOMPLISH A GOAL using the docs and reports whether it succeeded. The evaluation is experiential, not structural.

- **Persona modifying documentation pages:** The Persona has Write tool access for its artifacts (report and scenarios) but must NEVER modify documentation files in `paths.docs_root`. It is an evaluator, not an editor.

- **Grep-based "navigation":** A real user cannot search across all documentation files simultaneously. The Persona should navigate via links, table of contents, and visible navigation -- not by grepping for keywords across all files. Exception: using Glob to discover what pages exist (simulating a doc site sidebar).

- **Regenerating scenarios every run:** Scenarios should be stable across runs for consistent evaluation. Only regenerate when doc structure changes significantly (new/removed pages). Changing scenarios between revision passes makes convergence impossible.

- **Conflating PARTIAL and FAIL:** A PARTIAL verdict means the user CAN accomplish the goal but with friction. A FAIL means the user CANNOT accomplish the goal at all. This distinction is critical because only FAILs trigger revision passes. Over-classifying PARTIALs as FAILs wastes revision cycles; under-classifying FAILs as PARTIALs leaves docs broken.

- **Persona orchestrating the revision loop:** The Persona reports verdicts. Phase 5's `/doc:write` command orchestrates the revision loop. The Persona prompt should document the protocol (so it knows what its verdicts trigger) but should not contain orchestration logic.

- **Duplicating quality-rules content in the agent body:** The quality-rules skill is preloaded via `skills:` frontmatter. The Persona validates Rules 4 and 5 from the end-user perspective but should reference them, not restate them.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Scenario generation | Manual scenario authoring by project author | Agent generates from audience config + doc structure | PERS-01 requires automatic generation; the Persona understands audience context natively |
| Doc structure scanning | Custom file parsing or navigation tree builder | Glob tool + reading page headings | Claude reads markdown natively; Glob discovers files reliably |
| Goal-oriented simulation | External testing framework or script | Step-by-step simulation in agent prompt | Zero-dependency approach consistent with project pattern; Claude simulates user experience through reading and reasoning |
| Verdict assignment | Scoring rubric or weighted criteria system | Goal-achievability judgment by Claude | Three simple verdicts (PASS/PARTIAL/FAIL) based on goal outcome; Claude's language understanding is the evaluation engine |
| YAML scenario persistence | Database or structured storage | `.doc-writer/scenarios.yaml` via Read/Write tools | YAML is consistent with config.yaml; human-readable; no infrastructure needed |
| Multi-audience orchestration | Custom parallel execution framework | Phase 5 pipeline spawns Agent tool per audience | CC's Agent tool handles subagent spawning; orchestration is Phase 5's concern |
| Doc change detection | Git diff or file hash comparison | Page filename list comparison | Simple and reliable; structural changes (new/removed pages) are what matter for scenario staleness |
| Code example validation | Code execution or AST parsing | Existence + plausibility check by Claude | Out of scope per REQUIREMENTS.md; Claude checks presence, completeness, and realism without executing |

**Key insight:** Like the Author and Editor, the Persona has zero runtime dependencies. It is a markdown file containing a system prompt. All "implementation" is prompt design. The supporting infrastructure (config, doc files, quality-rules skill) already exists from earlier phases.

## Common Pitfalls

### Pitfall 1: Persona Reads Source Code

**What goes wrong:** The Persona uses Read, Glob, or Grep to examine source code files, validating code examples against actual implementations rather than evaluating them from a user's perspective.
**Why it happens:** The Persona has Read/Glob/Grep tools available and the prompt does not strongly enough restrict their use to documentation files only.
**How to avoid:** The prompt must explicitly state: "You are an end user. You have ONLY the documentation available. Do NOT read files in `paths.source_root`. Do NOT verify code examples against source code. You can only read files in `paths.docs_root`, `README.md`, and `.doc-writer/config.yaml`."
**Warning signs:** Persona report references source code files or verifies implementation details.

### Pitfall 2: Scenarios Are Too Generic

**What goes wrong:** Generated scenarios are vague and non-actionable: "Understand the library", "Learn about features", "Get started". These cannot produce meaningful verdicts because they have no concrete success criteria.
**Why it happens:** Scenario generation does not sufficiently filter through audience context or does not require concrete goals.
**How to avoid:** Each scenario must include a specific, testable goal with a clear success state. The prompt should require: "Every scenario goal must start with 'I want to [specific action]' and have a clear definition of 'done'." Examples: "I want to install the library and run the hello world example" is testable. "I want to understand the library" is not.
**Warning signs:** Scenarios with goals like "learn about X" or "understand Y" rather than "do X" or "accomplish Y".

### Pitfall 3: Verdict Inflation (Everything is FAIL)

**What goes wrong:** The Persona classifies minor friction as FAIL, triggering excessive revision passes for issues that do not actually prevent goal achievement.
**Why it happens:** The distinction between "achievable with friction" (PARTIAL) and "not achievable at all" (FAIL) is subjective and the Persona errs on the side of strictness.
**How to avoid:** The prompt must reinforce the key distinction: "FAIL means the user CANNOT accomplish the goal -- information is missing, instructions lead to dead ends, or critical steps are wrong. PARTIAL means the user CAN accomplish the goal but the experience is suboptimal -- unclear wording, missing context, confusing order. When in doubt between PARTIAL and FAIL, ask: 'Could a determined user figure this out from what is available?' If yes: PARTIAL. If no: FAIL."
**Warning signs:** Many FAIL verdicts where the gap description sounds like friction rather than impossibility.

### Pitfall 4: Navigation Simulation Uses Grep

**What goes wrong:** Instead of navigating through links and documentation structure, the Persona uses Grep to search across all documentation files for keywords, finding content that a real user would never discover through normal navigation.
**Why it happens:** Grep is faster than reading through pages sequentially, and the Persona optimizes for efficiency rather than realism.
**How to avoid:** The prompt must explicitly restrict navigation: "Navigate using only: links visible on the current page, table of contents or sidebar navigation (simulated via page listing), 'See also' or 'Related' sections, and explicit cross-references. Do NOT search across files to find content -- if the information is not reachable via navigation from your current page, that is a navigation gap."
**Warning signs:** Persona report does not describe a navigation path (page-to-page) but instead jumps directly to the right content.

### Pitfall 5: Scenarios Change Between Revision Passes

**What goes wrong:** The Persona regenerates scenarios on a revision pass, producing different scenarios than the initial evaluation. This makes it impossible to track whether issues were fixed.
**Why it happens:** The Persona detects "significant doc changes" after the Author's revision and regenerates scenarios.
**How to avoid:** The prompt must state: "During revision passes (when re-evaluating after Author revisions), ALWAYS reuse the existing scenarios from `.doc-writer/scenarios.yaml`. Do NOT regenerate scenarios during revision -- the point of revision is to fix gaps identified in the original scenarios."
**Warning signs:** Persona report in pass 2 evaluates different scenarios than pass 1.

### Pitfall 6: Report Too Verbose for Pipeline Parsing

**What goes wrong:** The persona report is written as flowing prose that is easy for humans to read but difficult for the Phase 5 pipeline orchestrator to parse for routing decisions.
**Why it happens:** The Persona writes a narrative rather than a structured report.
**How to avoid:** The report must use structured sections with predictable markers: verdict per scenario (PASS/FAIL/PARTIAL clearly labeled), revision recommendations table at the end, and a machine-parseable summary section at the top with counts.
**Warning signs:** Phase 5 pipeline cannot reliably determine whether revision is needed by reading the report.

### Pitfall 7: Prompt Too Long With Detailed Simulation Instructions

**What goes wrong:** Encoding detailed step-by-step simulation instructions, scenario generation logic, verdict criteria, report format, and revision protocol pushes the prompt past effective limits, causing instruction-following degradation.
**Why it happens:** The Persona has multiple concerns (generation, simulation, reporting, revision awareness) that all need encoding.
**How to avoid:** Target 350-450 lines for the agent body (consistent with Author at ~420 and Editor at ~390). Use clear section headers. Reference quality-rules skill by name rather than restating rules. Keep the revision loop protocol concise -- describe what the Persona produces, not the full orchestration flow.
**Warning signs:** Persona follows scenario generation instructions but produces poorly structured reports, or vice versa.

### Pitfall 8: Config Schema Extension Breaks Backward Compatibility

**What goes wrong:** Adding `domain_context` and `discovery_story` to the audience config schema means existing configs (from Phase 1 setup) are missing these fields, causing the Persona to error or produce poor scenarios.
**Why it happens:** The setup skill was written before these fields were defined.
**How to avoid:** The Persona prompt should treat these fields as optional with graceful degradation: "If `domain_context` is not present, infer domain context from the audience name and assumed_knowledge list. If `discovery_story` is not present, assume a generic discovery path (web search for the problem domain)."
**Warning signs:** Persona fails or generates poor scenarios when running against projects set up before Phase 4.

## Code Examples

### Persona Agent File Structure (What Phase 4 Produces)

```markdown
# Source: CC subagent format + Phases 1-3 established pattern
---
name: doc-persona
description: Validates documentation from the end user's perspective.
  Generates goal-oriented scenarios and tests docs by attempting to
  accomplish tasks using only the documentation.
tools: Read, Write, Glob, Grep
model: inherit
skills:
  - doc-writer:quality-rules
---

You are a User Persona agent. You validate documentation by
attempting to use it as an end user would -- testing whether real
goals can be accomplished using only the docs.

You do NOT write or edit documentation. You read it as an end user
and report whether it works.

## How You Work

You operate in three phases:
1. **Generate Scenarios** -- create goal-oriented user journey scenarios
2. **Simulate** -- trace through docs attempting each goal
3. **Report** -- produce structured verdicts with gap identification

The quality-rules skill is preloaded into your context. You validate
Rule 4 (Cross-References) and Rule 5 (Audience Calibration) from
the end-user perspective.

[... full prompt content ...]
```

### Scenario YAML Output Example

```yaml
# .doc-writer/scenarios.yaml
# Generated by Persona agent. Regenerated when docs change significantly.
version: 1

audiences:
  - name: "Python web developers building REST APIs"
    skill_level: intermediate
    generated_at: "2026-03-15"
    doc_pages:
      - "README.md"
      - "docs/getting-started.md"
      - "docs/how-to/configure-cache.md"
      - "docs/how-to/invalidate-cache.md"
      - "docs/explanation/cache-strategies.md"
    scenarios:
      - id: S1
        goal: "Install the library and cache my first API response"
        starting_point: "README.md"
        audience_relevance: "First thing any new user needs to do"
        done_when: "I have a working code example that caches an API response"
      - id: S2
        goal: "Configure Redis as my cache backend instead of the default"
        starting_point: "README.md"
        audience_relevance: "Common production configuration task"
        done_when: "I know the config changes needed and have a working Redis setup"
      - id: S3
        goal: "Invalidate cached data when my underlying database changes"
        starting_point: "README.md"
        audience_relevance: "Cache consistency is a common concern for API developers"
        done_when: "I know how to manually and programmatically invalidate cache entries"
      - id: S4
        goal: "Handle cache connection failures gracefully in production"
        starting_point: "README.md"
        audience_relevance: "Production reliability concern"
        done_when: "I know what happens when Redis is down and how to configure fallback behavior"
      - id: S5
        goal: "Choose between cache-aside and write-through strategies for my use case"
        starting_point: "README.md"
        audience_relevance: "Architecture decision that affects performance and consistency"
        done_when: "I understand the tradeoffs and know which strategy to use for my REST API"
```

### Persona Report Output Example

```markdown
# Persona Report

**Generated:** 2026-03-15
**Audience:** Python web developers building REST APIs (intermediate)
**Scenarios tested:** 5
**Results:** 3 PASS, 1 PARTIAL, 1 FAIL

## Summary

The documentation provides a good getting-started experience and covers
core caching operations well. The main gap is error handling in production
scenarios -- there is no guidance on cache connection failures or fallback
behavior. Cache strategy explanations are solid but could link more clearly
to actionable configuration steps.

---

## Scenario S1: Install the library and cache my first API response

**Verdict:** PASS

### Navigation Path

1. Started at: README.md
   - Found: Quick Start section with installation command and first use example
   - Example is self-contained with imports, setup, and expected output
2. Followed link to: docs/getting-started.md
   - Found: Detailed tutorial expanding on the Quick Start
   - Clear step-by-step instructions with explanations
3. Result: Goal accomplished with a smooth path

---

## Scenario S4: Handle cache connection failures gracefully in production

**Verdict:** FAIL

### Navigation Path

1. Started at: README.md
   - Found: No mention of error handling or production concerns
2. Navigated to: docs/ (sidebar)
   - Found: No page about error handling, production, or reliability
3. Checked: docs/how-to/configure-cache.md
   - Found: Configuration options but no section on failure modes
4. Checked: docs/explanation/cache-strategies.md
   - Found: Strategy tradeoffs but no discussion of failure scenarios
5. Result: DEAD END -- no content addresses cache connection failures

### Gap Analysis

**Where:** No page exists for this topic
**What:** Missing documentation for error handling and fallback behavior when cache
backend is unavailable
**Impact:** Users deploying to production have no guidance on resilience
**Suggested Fix:** Add a how-to guide: "How to Handle Cache Failures" covering
connection timeouts, fallback to no-cache mode, retry configuration, and monitoring

---

## Revision Recommendations

### FAIL Issues (trigger revision)

| Scenario | Page | Gap | Suggested Fix |
|----------|------|-----|---------------|
| S4 | (none exists) | No error handling / production resilience docs | Add "How to Handle Cache Failures" how-to guide |

### PARTIAL Issues (for project author approval)

| Scenario | Page | Gap | Suggested Fix |
|----------|------|-----|---------------|
| S5 | docs/explanation/cache-strategies.md | Strategy comparison lacks actionable next step | Add "Next steps" section linking to configuration how-to for each strategy |
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual test cases authored by maintainer | Agent-generated scenarios from project context | Phase 4 user decision | PERS-01: no manual authoring required; scenarios calibrated to audience |
| Checklist-based doc review | Goal-oriented simulation through docs | Phase 4 user decision | PERS-02: tests real user experience, not structural compliance |
| Binary pass/fail evaluation | Three-tier PASS/PARTIAL/FAIL with gap identification | Phase 4 user decision | PERS-03: nuanced verdicts enable proportional responses |
| Unlimited revision cycles | Bounded revision loop (max 2-3 passes) | Phase 4 user decision | PERS-04: prevents infinite loops; escalates unresolvable issues |
| Single-audience validation | Per-audience parallel Persona execution | Phase 4 user decision | PERS-05: each audience gets independent validation |

**Deprecated/outdated:**
- Manual scenario authoring -- replaced by automatic generation from audience context
- Structural checklist evaluation -- replaced by goal-oriented simulation
- Unbounded revision loops -- replaced by max 2-3 passes with escalation

## Open Questions

1. **Config schema extension for domain_context and discovery_story**
   - What we know: The locked decisions require these fields in the audience config. The Persona reads them for scenario generation.
   - What's unclear: Whether the Phase 1 setup skill should be updated in Phase 4 to capture these fields, or whether this update should be deferred until Phase 5 integration.
   - Recommendation: Make the Persona robust to missing fields (graceful degradation). Optionally include a small update to the setup skill in Phase 4 to add these Q&A questions. The setup skill already has the audience Q&A flow -- adding two more questions is a bounded change.

2. **Multi-audience report file strategy**
   - What we know: Multiple audiences produce independent verdicts. Reports need to be separate to avoid write conflicts during parallel execution.
   - What's unclear: Whether to use audience-specific filenames (`persona-report-{name}.md`) or a single file with audience sections.
   - Recommendation: Use audience-specific filenames for Phase 4 (avoids write conflicts, simpler Persona logic). Phase 5 orchestrator can merge them for presentation if needed.

3. **How Persona receives its audience assignment**
   - What we know: The same agent file serves all audiences. Each instance needs to know which audience it represents.
   - What's unclear: How the Phase 5 orchestrator tells the Persona which audience to use. CC's Agent tool can pass context via the invocation prompt.
   - Recommendation: The Persona prompt should accept an audience identifier in the invocation message: "Evaluate documentation as the '{audience_name}' audience." If no specific audience is given, default to the first audience in the config.

4. **Persona prompt length budget**
   - What we know: Author is ~420 lines, Editor is ~390 lines. Persona has three phases (generate, simulate, report) plus revision protocol awareness.
   - What's unclear: Whether all necessary instructions fit within a 400-line budget, given the simulation methodology and report formatting requirements.
   - Recommendation: Target 350-400 lines. The Persona is conceptually simpler than the Editor (no pattern matching, no cross-reference building). Simulation instructions can be more concise because Claude naturally understands "try to accomplish this goal by reading these documents." Focus prompt space on: scenario generation criteria, navigation rules, verdict definitions, and report format.

5. **Handling docs with no clear homepage**
   - What we know: Scenarios start from the docs homepage (README.md or index page).
   - What's unclear: What happens when there is no README.md and no index page in docs_root.
   - Recommendation: Fallback chain: (1) README.md in project root, (2) index.md in docs_root, (3) first file alphabetically in docs_root. Record the starting point in the report. If no docs exist at all, report all scenarios as FAIL with gap: "No documentation found."

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual CC session testing (no automated test framework) |
| Config file | None -- this is a markdown-file plugin with no executable code |
| Quick run command | `claude --plugin-dir .` then invoke Persona via Agent tool on sample doc set |
| Full suite command | Manual: run full Author > Editor > Persona pipeline on a sample project, verify all PERS requirements |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PERS-01 | Persona generates 3-5 realistic scenarios from project context | manual (CC session) | Run Persona on sample project with audience config; verify `.doc-writer/scenarios.yaml` contains 3-5 goal-oriented scenarios | N/A -- markdown plugin |
| PERS-02 | Scenarios are goal-oriented -- agent tries to accomplish tasks | manual (inspect report) | Verify persona report shows navigation paths and goal-based evaluation, not checklist items | N/A |
| PERS-03 | Each scenario gets PASS/FAIL/PARTIAL verdict with gap identification | manual (inspect report) | Verify `.doc-writer/persona-report.md` has per-scenario verdicts with gap details for non-PASS scenarios | N/A |
| PERS-04 | Revision loop has max pass limit and convergence rules | manual (multi-pass test) | Run Persona twice: once to get FAIL, then after Author revision to verify re-evaluation; check that only FAIL triggers revision | N/A |
| PERS-05 | Separate Persona per audience in parallel | manual (multi-audience test) | Run Persona with two audiences configured; verify each produces independent scenarios and verdicts | N/A |

### Sampling Rate
- **Per task commit:** Manual: load plugin with `claude --plugin-dir .`, run Persona on test doc set
- **Per wave merge:** Manual: run full Author > Editor > Persona pipeline on a sample project, verify all 5 PERS requirements
- **Phase gate:** All 5 PERS requirements verified via manual CC session before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Ensure sample project has Editor-cleaned docs in `paths.docs_root` (from Phase 3 output -- no HTML comments)
- [ ] Ensure sample project has `.doc-writer/config.yaml` with audience data (from Phase 1 setup)
- [ ] Optionally add `domain_context` and `discovery_story` fields to test audience config for richer scenario generation
- [ ] Prepare a doc set with a known gap (e.g., missing error handling page) to verify FAIL detection
- [ ] Prepare a doc set with known friction (e.g., unclear steps) to verify PARTIAL detection
- [ ] Configure a second audience to test multi-audience scenario generation (PERS-05)

## Sources

### Primary (HIGH confidence)
- Phase 1 artifacts (`agents/doc-persona.md` stub) -- existing frontmatter with name, tools (Read, Glob, Grep -- needs Write added), model, skills fields. Verified by direct file read.
- Phase 1 artifacts (`skills/quality-rules/SKILL.md`) -- Rule 4 (Cross-Reference Code Mentions) and Rule 5 (Audience-Calibrated Language) preloaded by Persona via `skills:` frontmatter. Verified by direct file read.
- Phase 2 artifacts (`agents/doc-author.md`) -- Author output format, internal notes structure (stripped by Editor before Persona sees docs), page types and templates. Verified by direct file read.
- Phase 3 artifacts (`agents/doc-editor.md`) -- Editor output format, `editor-report.md` structure, `terminology.yaml`, HTML comment stripping. Verified by direct file read.
- Phase 1 research (`01-RESEARCH.md`) -- CC subagent format, skill preloading, plugin architecture. HIGH confidence.
- Phase 2 research (`02-RESEARCH.md`) -- agent prompt architecture, skill reference patterns. HIGH confidence.
- Phase 3 research (`03-RESEARCH.md`) -- feedback format (BLOCKING/SUGGESTION/NITPICK), prompt length strategy, sequential pass design. HIGH confidence.

### Secondary (MEDIUM confidence)
- Phase 4 CONTEXT.md -- locked user decisions governing scenario generation, testing methodology, verdict criteria, revision protocol, and multi-audience execution. Source of all architectural constraints.
- REQUIREMENTS.md -- PERS-01 through PERS-05 requirement definitions and out-of-scope declaration (no code execution for example validation). Verified by direct file read.
- STATE.md -- project decisions and history including the Phase 4 blocker/concern: "User Persona goal-oriented simulation is a novel implementation -- spike early in the phase to validate approach before full build." Verified by direct file read.

### Tertiary (LOW confidence)
- None -- all key claims verified against existing project artifacts or locked user decisions.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- agent file format verified in Phases 1-3; all supporting infrastructure (skills, config, doc files) exists
- Architecture: HIGH -- three-phase workflow, scenario generation, simulation methodology, and report format all derive from locked user decisions or established project patterns
- Pitfalls: HIGH -- source code access restriction, scenario stability, verdict calibration, and prompt length are well-understood concerns from previous phase experience
- Revision protocol: HIGH -- protocol directly from locked user decisions; clear separation between Persona (reports) and Phase 5 (orchestrates)

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (CC subagent system is stable; locked user decisions do not change; 30-day validity appropriate)
