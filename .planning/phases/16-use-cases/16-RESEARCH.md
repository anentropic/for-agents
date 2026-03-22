# Phase 16: Use Cases - Research

**Researched:** 2026-03-22
**Domain:** Agent prompt engineering (setup Q&A, researcher context expansion, doc-author page templates, editor type recognition)
**Confidence:** HIGH

## Summary

Phase 16 adds use case capture to the doc-writer setup Q&A flow and threads those use cases through the researcher into context.md, with an optional promotion path to a first-class docs section. Three files are the primary targets: setup SKILL.md (new Q&A step), doc-researcher.md (use case expansion into context.md), and doc-author.md (use-case page type template + inventory awareness). A fourth file, doc-editor.md, needs a minor addition to recognize the `(use-case)` page type in Pass 2 blur detection.

The key architectural insight is that use cases have TWO fully decoupled paths. **Path A (always):** The setup Q&A captures use cases BEFORE user personas. If the user skips the step, the researcher infers basic use cases from persona context and stores them in the agent-facing context.md. **Path B (optional, explicit):** Use cases can be promoted to a documentation section at the same level as diataxis quadrants (Tutorials, How-To Guides, Explanation, Reference). But this path REQUIRES actual user-provided cases -- the system must NOT silently promote inferred cases to docs. If the user wants a Use Cases docs section but skipped the capture step, the system redirects them to `/doc-writer:setup` to capture cases first.

The use case page type is a discovery/showcase format: "did you know you could do this?" It follows a problem-statement / what's-possible / outcome structure, NOT an instructional tutorial or how-to pattern. This distinction is critical for the editor's blur detection -- a use-case page that reads like a tutorial is type blur.

**Primary recommendation:** Implement as two plans: Plan 16-01 covers the setup Q&A step (SKILL.md changes + config.yaml schema + researcher expansion). Plan 16-02 covers the doc-author use-case page template, inventory awareness, optional docs section promotion, and editor Pass 2 recognition.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CONT-01 | Setup Q&A captures use cases BEFORE user personas (skippable; infers from persona context if skipped) | New Step 2a.0 in setup SKILL.md before the existing Step 2a (User Persona Definition); `use_cases` field added to config-template.yaml; researcher expands inferred cases when field is empty |
| CONT-02 | Use cases stored in config.yaml and expanded in context.md by researcher agent | `use_cases:` array field in config.yaml; researcher reads this and writes a "## Use Cases" section in context.md with expanded problem/capability/outcome descriptions |
| CONT-03 | Use cases optionally promoted to a docs section at same level as diataxis quadrants, with typical and advanced cases as pages | New Q&A question after use case capture asking if cases should become a docs section; `(use-case)` page type in doc-author inventory; editor recognizes `(use-case)` in Pass 2 without misclassifying as tutorial/how-to blur |
</phase_requirements>

## Standard Stack

### Core

No new runtime dependencies. Phase 16 modifies existing markdown agent prompts, YAML configuration templates, and the setup skill. There are no npm/pip packages to install for the plugin itself.

### Files Modified by This Phase

```
doc-writer/
  agents/
    doc-author.md              # Add use-case page type, inventory awareness, page template
    doc-editor.md              # Add (use-case) recognition in Pass 2 blur detection
    doc-researcher.md          # Add use case expansion in context.md output
  skills/
    setup/
      SKILL.md                 # Add Step 2a.0 (Use Cases Q&A) before persona definition
      defaults/
        config-template.yaml   # Add use_cases array field
```

### What NOT to Add

| Do Not Add | Why |
|------------|-----|
| A new diataxis quadrant for use cases | Use cases sit ALONGSIDE the four diataxis quadrants, not inside them. They are a documentation section at the same level, not a fifth diataxis type. |
| Use case inference that auto-promotes to docs | User correction: inferred cases feed context.md only (agent-facing). Docs section requires explicit user-provided cases. |
| Use cases as tutorials or how-to guides | User correction: use-case pages are discovery/showcase ("did you know?"), not instructional. Different writing template. |

## Architecture Patterns

### Pattern 1: Use Cases Q&A Step in Setup SKILL.md

**What:** A new Step 2a.0 inserted BEFORE the existing Step 2a (User Persona Definition) in the Full Q&A Flow. This step captures use cases as a skippable Q&A question.

**Where in SKILL.md:** Between the `### Step 2: Full Q&A Flow (First-Time Setup)` heading and the `#### 2a: User Persona Definition` section. The new step becomes `#### 2a.0: Use Cases`.

**Flow:**

1. Display introduction explaining what use cases are and why they help
2. Ask the user to describe 1-3 typical things someone would accomplish with this library
3. For each use case, capture: a short title, the problem it solves, what the library makes possible, the outcome
4. Offer "Add another" or "Skip / Continue"
5. If skipped entirely: store empty `use_cases: []` in config.yaml. The researcher will infer basic use cases from persona context and README analysis for internal context.md only.

**Why BEFORE personas:** Use cases establish what the library does in the user's world. Personas then describe who those users are. This ordering lets the persona definition benefit from use case context -- the user has already articulated what their library enables before describing who uses it.

**Skippable behavior:** The Q&A presents a "Skip" option. If skipped, config.yaml stores `use_cases: []` (empty array). The researcher sees the empty array and infers basic use cases from the persona fields + README content. These inferred use cases go into context.md ONLY (agent-facing context) and are NOT eligible for docs section promotion.

**Example Q&A interaction:**

```
## Use Cases

Before defining who reads your docs, let's capture what they do with
your library. Use cases help calibrate the docs to real-world scenarios.

You can skip this if you prefer -- the system will infer use cases
from your persona descriptions later.
```

Then use AskUserQuestion:
- header: "Use Cases"
- question: "Describe a typical use case -- what problem does someone solve with this library?"
- options:
  - { label: "Describe a use case", description: "Write a freeform description of what someone accomplishes" }
  - { label: "Skip", description: "Infer use cases from persona context later" }
  - { label: "Chat about this", description: "Discuss what makes a good use case description" }

For each provided use case, extract structured fields:
- `title`: short label (e.g., "Rate-limit API endpoints")
- `problem`: what problem the user faces without this library
- `capability`: what the library makes possible
- `outcome`: the end result when the use case is accomplished

After each use case, offer:
- { label: "Add another", description: "Describe another use case" }
- { label: "Done", description: "Continue to persona definition" }

### Pattern 2: Config YAML Schema Extension

**What:** Add a `use_cases` array field to the config-template.yaml and to the config writing logic in setup SKILL.md Step 3.

**Config template addition:**

```yaml
use_cases:
  - title: ""
    problem: ""
    capability: ""
    outcome: ""
```

**When empty (user skipped):**

```yaml
use_cases: []
```

**When populated:**

```yaml
use_cases:
  - title: "Rate-limit API endpoints"
    problem: "Unprotected endpoints get hammered by bots and abusive clients"
    capability: "Middleware that enforces per-route rate limits with configurable backends"
    outcome: "API stays responsive under load; abusive clients get 429 responses"
  - title: "Protect login endpoints"
    problem: "Brute-force attacks on authentication endpoints"
    capability: "Stricter rate limits on auth routes with exponential backoff"
    outcome: "Login attacks are throttled without affecting legitimate users"
```

**Storage location:** Top-level field in config.yaml, between `tone` and `doc_system`:

```yaml
user_personas:
  - ...

tone: ""

use_cases:
  - title: ""
    ...

doc_system: ""
```

### Pattern 3: Researcher Use Case Expansion in context.md

**What:** The doc-researcher agent reads `use_cases` from config.yaml and writes an expanded "## Use Cases" section in context.md. This section provides rich context for the doc-author and other downstream agents.

**Addition to doc-researcher.md Step 1 (Read Inputs):** Read `use_cases` array from config.yaml. Note whether it is empty (user skipped) or populated.

**Addition to doc-researcher.md Step 3 (Analyze and Expand):** New subsection "### Use Case Expansion" added after the existing "### Persona Expansion" subsection.

**Two modes:**

1. **User-provided cases (use_cases array is non-empty):** Expand each use case into a rich description:
   - Expand `problem` into a concrete description of the pain point with real-world context
   - Expand `capability` into what the library specifically enables
   - Expand `outcome` into the measurable or observable result
   - Cross-reference with persona context: which persona(s) would encounter this use case?
   - Flag each case with `source: user-provided` -- eligible for docs section promotion

2. **Inferred cases (use_cases array is empty):** Infer 2-3 basic use cases from:
   - Persona `user_tasks` fields
   - README features and quick start content
   - Public API surface patterns
   - Flag each case with `source: inferred` -- NOT eligible for docs section promotion
   - Add a note: "These use cases were inferred from persona context and codebase analysis. To promote use cases to a documentation section, run `/doc-writer:setup` and provide explicit use cases."

**Addition to doc-researcher.md Step 4 (Write context.md):** New section in the context.md template:

```markdown
## Use Cases

{For each use case:}

### {title}

**Problem:** {expanded problem description}
**What's possible:** {expanded capability description}
**Outcome:** {expanded outcome description}
**Relevant persona(s):** {which persona(s) this applies to}
**Source:** {user-provided | inferred}
```

### Pattern 4: Optional Use Cases Docs Section Promotion

**What:** After use cases are captured in the setup Q&A (Pattern 1), a follow-up question asks if use cases should become a documentation section. This is a SEPARATE decision from capture.

**Placement in setup flow:** After the use case capture loop (Pattern 1), before persona definition (Step 2a). Only asked if the user actually provided at least one use case (not skipped).

**Guard clause:** If `use_cases` is empty (user skipped capture), do NOT ask this question. The skip-and-infer path and the docs-section path are fully decoupled.

**Q&A:**

```
Use AskUserQuestion:
- header: "Use Cases Section"
- question: "Should use cases become a documentation section alongside Tutorials, How-To Guides, Explanation, and Reference?"
- options:
  - { label: "Yes, add Use Cases section", description: "Typical and advanced cases become pages readers can browse" }
  - { label: "No, context only", description: "Use cases inform doc writing but don't appear as their own section" }
  - { label: "Chat about this", description: "Discuss what a Use Cases documentation section looks like" }
```

**Storage:** Add a `use_cases_section: true|false` boolean to config.yaml. Default: `false`.

**Re-entry guard:** If the user runs setup later and has empty `use_cases` but asks for the docs section (via the re-run update flow), the system should say: "A Use Cases documentation section requires explicit use cases. Run `/doc-writer:setup` to capture use cases first." and redirect to the capture step.

### Pattern 5: Doc-Author Use Case Page Template

**What:** When `use_cases_section: true` in config.yaml, the doc-author proposes a "Use Cases" section in the page inventory at the same level as the four diataxis sections. Each use case becomes a page using the `(use-case)` page type.

**Classification:** The `(use-case)` type is NOT a diataxis type. It sits alongside the four quadrants, not inside them. Similar to how `(readme)` and `(maintainer)` are non-diataxis types that the doc-author already handles.

**Page structure (discovery/showcase format):**

The template follows a "did you know you could do this?" pattern:

```markdown
# {Use Case Title}

## The Problem

{What challenge or situation the reader faces. Paint the scenario.
This is NOT "you need to install X" -- it's "your API is getting
hammered by bots and your response times are spiking."}

## What's Possible

{What the library makes achievable. Show the solution at a high level.
Include a brief code snippet showing the key configuration or API call,
but this is NOT a step-by-step tutorial. The reader should think
"oh, I didn't know it could do that."}

## The Outcome

{What changes after adopting this approach. Concrete, observable results.
"API response times stay under 200ms during traffic spikes. Abusive
clients receive 429 responses after 100 requests per minute."}

## Learn More

{Links to the relevant tutorial, how-to guide, or explanation page
that covers the implementation details.}
```

**Key distinctions from other types:**

| Aspect | Use Case Page | Tutorial | How-To Guide |
|--------|--------------|----------|--------------|
| Goal | Inspire discovery | Teach by doing | Solve a specific problem |
| Tone | "Did you know?" | "Let me show you" | "Here's how to" |
| Code | Illustrative snippet | Full walkthrough | Targeted steps |
| Reader state | Exploring possibilities | Learning | Working |
| Links out to | Tutorials + How-Tos | Explanations | Reference |

**Inventory proposal:** When `use_cases_section: true`, the doc-author adds a "Use Cases" section to the page inventory. Each user-provided use case maps to a page. The author may also add an "Advanced" sub-section for complex or multi-step use cases.

```
| N | (use-case) | {Use Case Title} | Problem, what's possible, outcome, learn more | docs/use-cases/{slug}.md |
```

The section also gets an index page:

```
| N | (use-case-index) | Use Cases | Section overview, typical cases, advanced cases | docs/use-cases/index.md |
```

**When `use_cases_section: false` or missing:** The doc-author does NOT propose a Use Cases section. Use case context is still available in context.md for enriching other page types (e.g., tutorials can reference use case scenarios).

### Pattern 6: Editor Pass 2 Recognition of (use-case) Type

**What:** The editor's Pass 2 (Diataxis Type Integrity) must recognize `(use-case)` as a valid page type in the Author's internal notes. Without this, the editor would see a page classified as `(use-case)` and flag it as an unknown type or attempt to reclassify it.

**Where in doc-editor.md:** In the Pass 2 Step 2 (Classify Each Page) section, which currently says:

> 1. Check the Author's internal notes for the `## Page Classification` section. The Author declares the type (tutorial, how-to, explanation) and which reference file was used.

This must be updated to include `(use-case)` in the recognized non-diataxis types alongside `(readme)` and `(maintainer)`.

**Blur detection for use-case pages:**

The editor should check for these blur signals:

- **Blur toward tutorial:** Step-by-step instructions, "let's build" framing, sequential tasks with expected output after each step
- **Blur toward how-to:** Goal-oriented "How to X" framing, prerequisite lists, troubleshooting sections
- **Blur toward explanation:** Extended "why" discussions without connecting back to the problem/capability/outcome structure

A clean use-case page is discovery-oriented: it presents a problem, shows what is possible, and describes the outcome. It links OUT to tutorials and how-to guides for implementation details rather than embedding them.

### Anti-Patterns to Avoid

- **Do NOT store use cases in context.md without config.yaml:** Use cases go into config.yaml first (structured data), then the researcher expands them into context.md (prose). This matches the existing pattern for personas (config stores labels, context.md stores expanded guidance).
- **Do NOT auto-promote inferred cases to docs:** The user explicitly stated that inferred cases feed only agent context. Docs section requires real user-provided cases.
- **Do NOT make use-case pages instructional:** They are discovery/showcase pages. "Did you know?" not "Here's how to."
- **Do NOT place use cases AFTER personas in the Q&A flow:** The user explicitly corrected the roadmap text. Use cases go BEFORE user personas (CONT-01).
- **Do NOT create a fifth diataxis quadrant:** Use cases sit alongside the four quadrants as a separate section. The `(use-case)` type marker uses parentheses like `(readme)` and `(maintainer)` to signal it is not a diataxis type.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Use case page writing template | Custom template engine | Inline guidance in doc-author.md prompt | Follows existing README/MAINTAINER template pattern |
| Use case inference from personas | ML/NLP extraction | Researcher agent's existing analysis capabilities | The researcher already infers tasks from persona context; use cases follow the same pattern |
| Use case data storage | Separate use-cases.yaml file | `use_cases` field in existing config.yaml | One config file; follows existing pattern for all setup data |
| Use cases section in nav | Custom nav plugin | Same level as diataxis quadrants in page inventory | The doc-author already handles section index pages; use cases section follows the same pattern |

## Common Pitfalls

### Pitfall 1: Use Case Pages Reading Like Tutorials

**What goes wrong:** A use-case page starts with "Step 1: Install...", includes sequential tasks with expected output, and walks the reader through building something.

**Why it happens:** The natural instinct is to show HOW to do something, not WHAT is possible. Use cases share surface similarity with tutorials (both involve a user goal).

**How to avoid:** The doc-author template emphasizes the problem/possibility/outcome structure. The "Learn More" section explicitly links to tutorials and how-to guides for implementation. The editor's blur detection flags step-by-step instructions in use-case pages.

**Warning signs:** Pages with "Step 1", "Step 2" structure; "Prerequisites" sections; "Expected output" blocks; "let's" or "we'll" framing.

### Pitfall 2: Inferred Use Cases Leaking into Docs Section

**What goes wrong:** The user skipped use case capture, the researcher inferred some cases, and those inferred cases appear as a Use Cases docs section.

**Why it happens:** No guard between the inference path and the promotion path.

**How to avoid:** Two guards: (1) The `use_cases_section` promotion question is only asked if the user provided at least one case. (2) The doc-author checks `use_cases_section: true` AND verifies `use_cases` is non-empty before proposing the section. If config has `use_cases_section: true` but `use_cases: []`, the author should warn and skip the section.

**Warning signs:** `use_cases_section: true` with `use_cases: []` in config.yaml.

### Pitfall 3: Editor Misclassifying Use Case Pages

**What goes wrong:** The editor's Pass 2 sees a `(use-case)` page and tries to load `skills/diataxis/references/use-case.md` (which does not exist), or flags it as an unknown type.

**Why it happens:** The editor's type classification assumes all pages are one of the four diataxis types plus readme/maintainer.

**How to avoid:** Explicitly add `(use-case)` to the list of recognized non-diataxis types in the editor's Pass 2. Define use-case-specific blur signals inline in the editor prompt (no separate reference file needed). The blur signals are simple: check for tutorial-like step-by-step patterns or how-to-like goal-oriented framing.

**Warning signs:** Editor report showing "unknown type: use-case" or attempting to load a non-existent reference file.

### Pitfall 4: Q&A Step Ordering Confusion

**What goes wrong:** The use cases step is placed after personas instead of before them.

**Why it happens:** The roadmap success criteria text incorrectly says "after user personas." The user explicitly corrected this.

**How to avoid:** The SKILL.md must have the use cases step as `#### 2a.0: Use Cases` BEFORE `#### 2a: User Persona Definition`. The numbering makes the ordering unambiguous.

**Warning signs:** SKILL.md showing use cases after persona definition; step numbered 2a.6 or similar (after tone selection).

### Pitfall 5: Use Cases Section Competing with Diataxis

**What goes wrong:** The Use Cases section is treated as a diataxis type, leading to confusion about where content belongs and the editor flagging "blur" between use cases and the diataxis quadrants.

**Why it happens:** The section sits at the same level as Tutorials, How-To Guides, etc., which are diataxis quadrants.

**How to avoid:** The `(use-case)` type marker uses parentheses (like `(readme)` and `(maintainer)`) to signal it is NOT a diataxis type. The doc-author guidance explains that use cases are a discovery/showcase format distinct from all four diataxis types. The editor recognizes `(use-case)` as a non-diataxis type and does NOT attempt to apply diataxis blur rules.

**Warning signs:** Doc-author proposing use cases as `explanation` type; editor flagging use-case pages as "explanation blur."

## Code Examples

### Config YAML with Use Cases

```yaml
# Source: extension of existing config-template.yaml pattern
version: 1

user_personas:
  - name: "Backend developers building REST APIs"
    skill_level: "intermediate"
    assumed_knowledge:
      - "HTTP/REST APIs"
      - "Python basics"
    never_assume:
      - "rate limiting concepts"
      - "middleware patterns"
    domain_context: "Building web services that handle external traffic"
    discovery_story: "Found the library while searching for Python rate limiting"
    user_tasks:
      - "Set up rate limiting"
      - "Configure per-route limits"

tone: "warm-businesslike"

use_cases:
  - title: "Rate-limit API endpoints"
    problem: "Unprotected endpoints get hammered by bots and abusive clients"
    capability: "Middleware that enforces per-route rate limits with configurable backends"
    outcome: "API stays responsive under load; abusive clients get 429 responses"
  - title: "Protect login endpoints"
    problem: "Brute-force attacks on authentication endpoints"
    capability: "Stricter rate limits on auth routes with exponential backoff"
    outcome: "Login attacks are throttled without affecting legitimate users"

use_cases_section: true

doc_system: "mkdocs-material"
```

### Use Case Page Template (for doc-author.md)

```markdown
# {Use Case Title}

## The Problem

{Concrete scenario the reader faces. Paint the picture. This is about
the reader's world, not the library's API.}

## What's Possible

{What the library enables for this scenario. Show the key insight --
a brief code snippet demonstrating the core capability, not a full
walkthrough. The reader should think "I didn't know it could do that."}

## The Outcome

{Observable, concrete results after applying this approach.
Specific numbers, behaviors, or states -- not vague "improved performance."}

## Learn More

- [Getting Started with Rate Limiting](../tutorials/rate-limiting.md) -- Full tutorial
- [How to Configure Per-Route Limits](../how-to/per-route-limits.md) -- Step-by-step guide
- [Understanding the Rate Limiting Algorithm](../explanation/algorithm.md) -- How it works under the hood
```

### Use Case Inventory Entry (for doc-author.md Phase 1)

```markdown
## Proposed Documentation

| # | Type | Title | Key Sections | File Path |
|---|------|-------|--------------|-----------|
| ... | ... | ... | ... | ... |
| 8 | (use-case-index) | Use Cases | Overview, typical cases, advanced cases | docs/use-cases/index.md |
| 9 | (use-case) | Rate-Limit API Endpoints | Problem, what's possible, outcome, learn more | docs/use-cases/rate-limit-api.md |
| 10 | (use-case) | Protect Login Endpoints | Problem, what's possible, outcome, learn more | docs/use-cases/protect-login.md |
```

### Editor Pass 2 Use Case Blur Signals (for doc-editor.md)

```markdown
**(use-case) blur signals:**
- Step-by-step instructions with sequential numbered tasks (blur toward tutorial)
- "How to" or goal-oriented task framing with prerequisites (blur toward how-to)
- Extended conceptual discussion without problem/capability/outcome structure (blur toward explanation)
- Missing "Learn More" section linking to tutorials/how-to guides (use-case pages should always link out for implementation details)
```

### Researcher context.md Use Case Section

```markdown
## Use Cases

### Rate-Limit API Endpoints

**Problem:** Web APIs exposed to the internet face constant automated traffic -- bots scraping data, credential stuffing attacks, and misconfigured client retries that create thundering-herd patterns. Without rate limiting, a single abusive client can degrade performance for all legitimate users.

**What's possible:** The library provides middleware that sits between the HTTP server and route handlers. It enforces configurable rate limits per endpoint, per client IP, or per API key. Storage backends (Redis, in-memory, database) handle distributed deployments where multiple server instances share rate limit state.

**Outcome:** API response times remain stable under traffic spikes. Abusive clients receive HTTP 429 (Too Many Requests) responses with Retry-After headers. Legitimate users experience no impact. Operations teams get visibility into rate limit hits via structured logging.

**Relevant persona(s):** Backend developers building REST APIs
**Source:** user-provided
```

## State of the Art

| Old Approach (current) | New Approach (Phase 16) | Impact |
|------------------------|-------------------------|--------|
| No use case capture in setup | Use cases captured before personas with skip option | Docs calibrated to real-world scenarios from the start |
| No use case section in docs | Optional Use Cases section alongside diataxis quadrants | Readers can discover what the library enables before diving into tutorials |
| Only four page types + readme + maintainer | `(use-case)` page type with discovery/showcase template | New content format distinct from all diataxis types |
| Editor recognizes tutorial/how-to/explanation/readme/maintainer | Editor also recognizes `(use-case)` with dedicated blur signals | No false positives on use-case pages |

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | grep-based content verification + manual review |
| Config file | none |
| Quick run command | `grep -c "use_cases\|use-case\|Use Cases" doc-writer/skills/setup/SKILL.md doc-writer/agents/doc-researcher.md doc-writer/agents/doc-author.md doc-writer/agents/doc-editor.md doc-writer/skills/setup/defaults/config-template.yaml` |
| Full suite command | Manual: verify each success criterion against modified files |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONT-01 | Setup Q&A captures use cases before personas | smoke | `grep -n "2a.0.*Use Cases\|Use Cases.*2a.0" doc-writer/skills/setup/SKILL.md` | Wave 0 |
| CONT-01 | Use cases step is skippable | smoke | `grep -c "Skip" doc-writer/skills/setup/SKILL.md` (in the use cases section context) | Wave 0 |
| CONT-02 | Use cases stored in config.yaml | smoke | `grep "use_cases" doc-writer/skills/setup/defaults/config-template.yaml` | Wave 0 |
| CONT-02 | Researcher expands use cases in context.md | smoke | `grep -c "Use Case Expansion\|use_cases" doc-writer/agents/doc-researcher.md` | Wave 0 |
| CONT-03 | Use cases optionally promoted to docs section | smoke | `grep -c "use_cases_section\|Use Cases.*section" doc-writer/skills/setup/SKILL.md doc-writer/agents/doc-author.md` | Wave 0 |
| CONT-03 | Doc-author has (use-case) page type template | smoke | `grep -c "use-case.*template\|use-case.*page" doc-writer/agents/doc-author.md` | Wave 0 |
| CONT-03 | Editor recognizes (use-case) in Pass 2 | smoke | `grep -c "use-case" doc-writer/agents/doc-editor.md` | Wave 0 |

### Sampling Rate

- **Per task commit:** grep smoke tests on modified files
- **Per wave merge:** Full grep suite across all modified files
- **Phase gate:** All grep checks pass + manual review of Q&A flow ordering and template structure

### Wave 0 Gaps

None -- all validation is grep-based content verification on modified files. No test framework, config files, or fixtures needed.

## Open Questions

1. **Should use cases appear in the re-run update flow?**
   - What we know: The setup SKILL.md Step 4 (Re-Run Update Flow) provides field-by-field editing for existing configs. Use cases should be editable via this flow.
   - What's unclear: Should the update menu include "Use Cases" as a separate option, or fold it into an existing option?
   - Recommendation: Add "Use Cases" as a new option in the re-run menu alongside "User Personas", "Tone", etc. When selected, show current use cases and offer to add, edit, or remove individual cases. Also offer to toggle `use_cases_section`. This follows the same pattern as persona editing in the re-run flow.

2. **Should the use-case page template have a reference file?**
   - What we know: Diataxis types (tutorial, how-to, explanation) each have a reference file in `skills/diataxis/references/`. README and MAINTAINER templates are inline in doc-author.md.
   - What's unclear: Should `(use-case)` get its own reference file?
   - Recommendation: No. Keep the template inline in doc-author.md, following the README/MAINTAINER pattern. The use-case template is simpler and shorter than diataxis types. A separate file would add a file lookup step for minimal benefit. If the template grows in future versions, it can be extracted then.

3. **What about the `--refresh-context` flow?**
   - What we know: The `--refresh-context` flag re-runs the researcher without Q&A. The researcher reads config.yaml and regenerates context.md.
   - What's unclear: Does the researcher need special handling for use cases during refresh?
   - Recommendation: No. The researcher reads `use_cases` from config.yaml on every run. If the field is populated, it expands them. If empty, it infers. The `--refresh-context` flow works unchanged because it re-reads config.yaml (which already has the use_cases field from the previous setup run).

## Sources

### Primary (HIGH confidence)
- Existing codebase: `doc-writer/skills/setup/SKILL.md` -- current Q&A flow structure, Step 2a ordering, config writing logic
- Existing codebase: `doc-writer/skills/setup/defaults/config-template.yaml` -- current config schema
- Existing codebase: `doc-writer/agents/doc-researcher.md` -- current enrichment flow, context.md template
- Existing codebase: `doc-writer/agents/doc-author.md` -- current page type handling, inventory proposal, README/MAINTAINER templates
- Existing codebase: `doc-writer/agents/doc-editor.md` -- current Pass 2 type classification and blur detection
- User corrections in additional_context: use cases go BEFORE personas, pages are discovery/showcase format, inference only feeds agent context
- `.planning/REQUIREMENTS.md` -- CONT-01, CONT-02, CONT-03 requirement definitions
- Phase 14 and Phase 15 research and plans -- established modification patterns for these same files

### Secondary (MEDIUM confidence)
- `.planning/STATE.md` -- accumulated decisions including "Use Cases Q&A goes AFTER user personas" (which was the pre-correction state, now corrected to BEFORE by user)

### Tertiary (LOW confidence)
- None -- all findings derived from reading the actual codebase and user corrections

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies; all modifications target existing files with clear extension points
- Architecture: HIGH -- every pattern follows an established codebase pattern (Q&A step follows persona step pattern, config field follows persona field pattern, researcher expansion follows persona expansion pattern, page type follows readme/maintainer pattern)
- Pitfalls: HIGH -- all pitfalls derived from explicit user corrections and analysis of existing editor behavior
- Editor recognition: HIGH -- the change is small (add type to recognized list + inline blur signals) and follows the existing pattern for non-diataxis types

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable domain; no external dependencies or fast-moving APIs)
