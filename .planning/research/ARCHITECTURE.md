# Architecture Research: v1.4.0 Feature Integration

**Domain:** Doc-writer plugin -- content & navigation milestone
**Researched:** 2026-03-21
**Confidence:** HIGH (all findings derived from reading the existing codebase; no external dependencies)

## Overview

This document answers one question: **how do the five v1.4.0 features integrate with the existing doc-writer architecture?** Each feature is analyzed for: what files change, what data flows change, what new components are needed, and what depends on what.

The existing architecture has clean extension points. Most v1.4.0 features slot into existing patterns (new Q&A sections, new guidance file sections, new config fields, new scan-exports cases). Two features require genuinely new patterns: Use Cases as a non-diataxis doc section, and doc-author format switching for .mld/.mli output.

---

## Existing Architecture (Reference)

```
Setup Flow:
  User Personas Q&A (2a) --> Tone (2a.5) --> Doc System (2b) --> Scaffold (2b.3)
  --> Framework Q&A (2b.5) --> Paths (2c) --> File Creation (3) --> Researcher (5)

Config Data Flow:
  setup SKILL.md  --(Q&A answers)-->  .doc-writer/config.yaml
                                           |
  doc-researcher  --(reads config)-->  .doc-writer/context.md
                                           |
  doc-author      --(reads both)-->    docs/ pages
  doc-editor      --(reads both)-->    edits docs/ pages
  doc-user-tester --(reads both)-->    persona reports

Write Pipeline:
  Gap Detection --> Author Plan --> Inventory Approval --> Author Write
  --> Editor (4 passes) --> Persona Eval --> Verdict/Revision Loop

Key Files:
  config-template.yaml          # schema for .doc-writer/config.yaml
  {framework}.md                # guidance files (mkdocs-material, sphinx-shibuya, odoc, plain-markdown)
  {framework}.qa.md             # framework Q&A question sets
  scaffolds/{framework}.*       # config file templates
  doc-author.md                 # agent: plans and writes docs
  doc-researcher.md             # agent: enriches config into context.md
  doc-editor.md                 # agent: 4-pass editing
  doc-user-tester.md            # agent: persona-based validation
  skills/diataxis/references/*  # structural templates per doc type
  skills/write/scripts/scan-exports.sh  # export symbol scanner
```

---

## Feature 1: Use Cases Q&A in Setup

### What It Is

A new Q&A step in the setup flow, positioned **before** User Personas (new Step 2a, pushing current 2a to 2b). Captures the project's real-world use cases -- what problems users solve with this library.

### Integration Points

**Modified files:**

| File | Change | Scope |
|------|--------|-------|
| `skills/setup/SKILL.md` | New Step 2a (Use Cases Q&A) before current Step 2a (User Personas). Renumber subsequent steps. | Medium -- new section, structural renumber |
| `skills/setup/defaults/config-template.yaml` | New top-level `use_cases:` array field | Small -- add field |
| `agents/doc-researcher.md` | Read `use_cases` from config, expand into context.md | Medium -- new section in Step 1 + Step 3 + Step 4 output |
| `agents/doc-author.md` | Consume use cases from context.md for richer page planning | Small -- already reads context.md; just uses new section |
| `agents/doc-user-tester.md` | Use cases inform scenario generation | Small -- use cases map to realistic test goals |

**No new files needed.** This is a data-flow extension through existing pipes.

### Data Flow

```
Setup Q&A (new Step 2a)
    |
    v
config.yaml { use_cases: ["Rate limiting for API endpoints", "Multi-tenant isolation", ...] }
    |
    v
doc-researcher reads use_cases, expands each into:
    - Problem statement (what the user is trying to solve)
    - Library capabilities that address it
    - Typical workflow
    |
    v
context.md ## Use Cases
    |
    v
doc-author uses for:          doc-user-tester uses for:
- Page inventory planning      - Scenario generation
- Example selection             - Goal-oriented test paths
- Tutorial topic choices        - Validation coverage
```

### Config Schema Addition

```yaml
# .doc-writer/config.yaml
use_cases:
  - "Rate limiting for API endpoints"
  - "Per-tenant request quotas"
  - "Graceful degradation under load"
```

Use cases are freeform strings. The researcher expands them. Config stays lean.

### Setup Flow Position

Use Cases goes **first** because it provides context that improves persona definition. When you know the use cases, you can better infer assumed knowledge, user tasks, and discovery stories during persona Q&A.

```
NEW ORDER:
  Use Cases (2a) --> User Personas (2b) --> Tone (2b.5) --> Doc System (2c)
  --> Scaffold (2c.3) --> Framework Q&A (2c.5) --> Paths (2d) --> File Creation (3) --> Researcher (5)
```

### Re-Run Menu Update

The existing re-run menu (Step 1, option 4: config exists) needs a new option:

```
{ label: "Use Cases", description: "Edit, add, or remove use cases" }
```

This option jumps to the use cases editing flow (similar pattern to persona editing in Step 4).

### Build Implications

- **Depends on:** Nothing -- pure additive
- **Blocks:** Feature 2 (Use Cases as docs section) benefits from this data being available
- **Risk:** Low. Follows the exact same Q&A -> config -> researcher -> context.md -> agents pattern as User Personas.

---

## Feature 2: Use Cases as Optional Docs Section

### What It Is

An optional documentation section that showcases real-world use cases. This is **not a diataxis category** -- it is a supplementary section like README or MAINTAINER that exists alongside the diataxis quadrants.

### The Core Design Decision

Use Cases pages are **not** diataxis-typed. They do not fit neatly into tutorial/how-to/explanation/reference. A use case page is a hybrid: it explains a problem (explanation), shows how to solve it (how-to), and walks through a realistic scenario (tutorial-adjacent). Forcing it into diataxis creates type blur.

**Recommendation:** Handle Use Cases the same way doc-author handles README and MAINTAINER -- as a dedicated section with its own template, **not** via the diataxis reference files.

### Integration Points

**Modified files:**

| File | Change | Scope |
|------|--------|-------|
| `agents/doc-author.md` | New "Section 7: Use Case Template" (parallel to Section 4: README Template, Section 5: MAINTAINER Template). New page type `(use-case)` in inventory classification. | Medium -- new template section |
| `skills/setup/SKILL.md` | After Use Cases Q&A (Feature 1), ask whether to generate Use Case doc pages | Small -- one additional AskUserQuestion |
| `skills/setup/defaults/config-template.yaml` | New field `use_cases_section: true/false` | Small |
| `agents/doc-researcher.md` | Context.md includes use case expansion (already from Feature 1) | Already covered by Feature 1 |
| `agents/doc-editor.md` | Recognize `(use-case)` page type; skip diataxis type integrity check for these pages | Small -- add to Pass 2 exemption list |
| `agents/doc-user-tester.md` | Test use case pages like any other page | No change needed -- already tests all pages in docs_root |

**New file needed: No.** The use case template lives inside doc-author.md as a new section (same pattern as README/MAINTAINER templates).

**Does NOT need a new diataxis reference file.** The diataxis references (`skills/diataxis/references/`) are specifically for the four diataxis types. Use Cases is outside diataxis. The template in doc-author.md is sufficient.

### Use Case Page Template (for doc-author.md Section 7)

```markdown
# Use Case: {Title}

## The Problem

{What challenge the user faces. 2-3 paragraphs establishing context.}

## Solution with {Library}

{How this library addresses the problem. Overview before code.}

### Setup

{Minimal setup required for this use case.}

### Implementation

{Step-by-step implementation with code examples. Self-contained.}

### Result

{What the user achieves. Show output or observable behavior.}

## Variations

{Common variations on this use case. Brief, with links to how-to guides for details.}

## Related

- {Link to tutorial if relevant}
- {Link to how-to guides for specific tasks within this use case}
- {Link to explanation for underlying concepts}
```

### Page Inventory Integration

The author currently classifies pages as: `tutorial`, `how-to`, `explanation`, `(readme)`, `(maintainer)`. Add `(use-case)` to this list. Parenthesized types indicate non-diataxis pages.

The page inventory table gains a new type:

```
| # | Type | Title | Key Sections | File Path |
| 5 | (use-case) | Rate Limiting for APIs | Problem, Solution, Setup, Implementation | docs/use-cases/rate-limiting.md |
```

### Guidance File Integration

Each framework's guidance file (mkdocs-material.md, sphinx-shibuya.md, etc.) needs a small section on how to handle the use-cases directory in navigation:

- **mkdocs-material:** Add `use-cases/` directory to `nav:` in mkdocs.yml, typically as a peer to the diataxis sections
- **sphinx-shibuya:** Add use-cases toctree to root index.rst or as a separate tab
- **odoc:** Use case pages would be .mld files in `doc/` with `use_case_` prefix

This is an addition to the existing guidance files, not a new file.

### Build Implications

- **Depends on:** Feature 1 (Use Cases Q&A provides the data)
- **Blocks:** Nothing
- **Risk:** Low-Medium. The main risk is doc-editor's diataxis type integrity pass (Pass 2) flagging use case pages as "type blur." The editor must be told to exempt `(use-case)` pages from diataxis classification checks, just as it exempts `(readme)` and `(maintainer)` pages.

---

## Feature 3: Nav Structure Choices in Setup Q&A

### What It Is

The existing framework Q&A files (mkdocs-material.qa.md, sphinx-shibuya.qa.md) already have a "Navigation style" question (Question 1 in both). The v1.4.0 feature expands this to offer three specific top-tab strategies with richer descriptions, plus section index abstract handling.

### The Three Strategies

1. **No tabs** -- flat sidebar only. Best for small projects (under 10 pages).
2. **"Docs" tab** -- single top-level tab labeling the entire documentation section, sidebar handles internal structure.
3. **Sections-as-tabs** -- each diataxis section is a top tab (Tutorials, How-To, Explanation, Reference). For sphinx-shibuya, each tab can have dropdown sub-items.

### Integration Points

**Modified files:**

| File | Change | Scope |
|------|--------|-------|
| `skills/setup/defaults/mkdocs-material.qa.md` | Replace Question 1 options with three explicit strategies + section index abstract question | Medium |
| `skills/setup/defaults/sphinx-shibuya.qa.md` | Replace Question 1 options with three explicit strategies (with dropdown variant) + section index abstract question | Medium |
| `skills/setup/defaults/mkdocs-material.md` | Expand Navigation section with guidance for each strategy; add section index abstract guidance | Medium |
| `skills/setup/defaults/sphinx-shibuya.md` | Expand Navigation section with guidance for each strategy; add dropdown guidance; add section index abstract guidance | Medium |
| `skills/setup/defaults/scaffolds/mkdocs-material.yml` | Update nav stanza to reflect chosen strategy (template variables or conditional sections) | Small |
| `skills/setup/defaults/scaffolds/sphinx-shibuya.py` | Update nav_links and toctree to reflect chosen strategy | Small |
| `agents/doc-researcher.md` | Context.md Framework Preferences section already covers nav -- researcher uses Q&A answers to populate it | No structural change -- just richer data |
| `agents/doc-author.md` | Already reads guidance file for nav conventions -- richer guidance means better nav output | No structural change |

**No new files needed.** All changes are expansions of existing Q&A and guidance files.

### Where Nav Config Lives

Nav strategy answers follow the existing pattern: they do **not** go into config.yaml. They are passed to the researcher via the Agent tool invocation message (Step 5 of setup), just like all other framework Q&A answers. The researcher writes them into context.md under `## Framework Preferences: {doc_system} > ### Navigation`.

This is explicitly stated in the current setup SKILL.md (Step 2b.5, point 4): "Framework Q&A answers do NOT go into config.yaml. Store them in-memory and pass them to the researcher."

No config.yaml schema change needed for nav. The existing data flow handles it.

### Section Index Abstracts

A new Q&A sub-question after nav strategy selection:

```
## Question 1b: Section index pages

- header: "Section Indexes"
- question: "Should section landing pages include abstracts for each sub-page?"
- options:
  - { label: "Yes -- brief abstract under each link", description: "Each section index shows page title + 1-2 sentence summary" }
  - { label: "No -- titles only", description: "Section indexes list page titles without descriptions" }
  - { label: "Chat about this", description: "See examples of each style" }
```

This answer flows to the researcher, which includes it in context.md navigation guidance, which the author reads when writing section index pages.

### Scaffold Changes

The scaffold templates need conditional handling based on nav strategy. Since scaffolds currently use simple variable substitution (not conditionals), the approach should be:

- **Option A (recommended):** Generate the scaffold post-substitution in the setup skill, with the nav strategy baked in. The setup skill already reads the scaffold template and processes variables -- add nav strategy as part of that processing.
- **Option B:** Multiple scaffold variants (one per strategy). Avoid this -- it multiplies files.

### Build Implications

- **Depends on:** Nothing -- pure modification of existing files
- **Blocks:** Nothing
- **Risk:** Low. The Q&A and guidance file patterns are well-established. The main care point is scaffold generation needing to account for nav strategy, but the setup SKILL.md already has template variable processing logic that can be extended.

---

## Feature 4: Mermaid Diagram Support

### What It Is

Make the doc-author aware that mermaid diagrams are available and when to use them. This is not about configuring mermaid (that is a framework-level concern already handled by Q&A) -- it is about the author knowing when and how to insert diagrams.

### Which Files Need Awareness

| File | Needs Mermaid Awareness? | Why |
|------|--------------------------|-----|
| `agents/doc-author.md` | **YES** | Primary consumer. Needs to know when to generate mermaid blocks and the syntax per framework. |
| `skills/setup/defaults/mkdocs-material.md` | **Already has it** (partially). Q&A Question 3 includes "Mermaid diagrams" as a feature. Guidance file needs a dedicated `## Mermaid Diagrams` section with syntax and usage rules. | Expand existing content |
| `skills/setup/defaults/sphinx-shibuya.md` | **Needs addition.** Currently has no mermaid section. Sphinx uses `sphinxcontrib-mermaid` extension. | New section in guidance file |
| `skills/setup/defaults/odoc.md` | **Not applicable.** odoc has no mermaid support. Use `{v ... v}` for ASCII diagrams instead. Note this in guidance. | Small note addition |
| `skills/setup/defaults/plain-markdown.md` | **Needs addition.** Plain markdown renders via GitHub/GitLab which support mermaid natively in fenced blocks. | New section in guidance file |
| `skills/diataxis/references/explanation.md` | **Yes -- gentle addition.** Already mentions "Include Diagrams and Visuals" as a best practice. Add a note that mermaid is available for architecture/flow diagrams when the framework supports it. | Small addition |
| `agents/doc-editor.md` | **No.** Editor does not generate content. It might validate mermaid syntax minimally (e.g., fenced block has `mermaid` language tag), but this falls under existing code block validation. | No change |
| `agents/doc-researcher.md` | **No.** Researcher scans for mermaid availability in framework config (already does for mkdocs via pymdownx.superfences detection). No new logic needed. | No change |
| `agents/doc-user-tester.md` | **No.** Persona tester evaluates content usefulness, not diagram syntax. | No change |

### Doc-Author Changes

Add a new subsection to doc-author.md (after Section 6: Python/MkDocs Conditional Formatting):

**Section 7: Mermaid Diagrams** (or renumber if Use Case template takes Section 7)

```
## When to Use Mermaid

Insert mermaid diagrams when:
- Showing data flow through a system (flowchart or sequence diagram)
- Illustrating component relationships (class or entity-relationship diagram)
- Depicting state machines or lifecycle transitions (state diagram)
- Showing a sequence of interactions between actors (sequence diagram)

Do NOT use mermaid for:
- Simple lists or comparisons (use tables)
- Step-by-step instructions (use numbered lists)
- Code structure (use code blocks)
- Anything that would be clearer as prose

## Syntax Per Framework

Mermaid syntax depends on the doc system. Read it from the guidance file
(.doc-writer/{doc_system}.md). Common patterns:

- mkdocs-material: fenced code block with `mermaid` language tag
- sphinx-shibuya: `.. mermaid::` directive (requires sphinxcontrib-mermaid)
- plain-markdown: fenced code block with `mermaid` language tag (GitHub/GitLab native)
- odoc: not supported -- use {v ... v} ASCII diagrams instead
```

### Guidance File Additions

**mkdocs-material.md** -- new section:

```markdown
## Mermaid Diagrams

- Use fenced code blocks with `mermaid` language identifier. Requires `pymdownx.superfences`
  with the mermaid custom fence in mkdocs.yml.
- Prefer flowcharts for data flow, sequence diagrams for API interactions, state diagrams
  for lifecycle.
- Keep diagrams focused -- under 15 nodes. Larger diagrams lose readability on mobile.
- Always include a text description before or after the diagram for accessibility and for
  readers whose rendering does not support mermaid.
- Do not use mermaid for simple relationships that a sentence or table can express.
```

**sphinx-shibuya.md** -- new section:

```markdown
## Mermaid Diagrams

- Use `.. mermaid::` directive from `sphinxcontrib-mermaid`. The extension must be in
  conf.py extensions list.
- Same usage guidance as mkdocs: prefer focused diagrams, include text description for
  accessibility.
- Example:
  .. mermaid::

     flowchart LR
         A[Client] --> B[API Gateway]
         B --> C[Service]
```

### Build Implications

- **Depends on:** Nothing
- **Blocks:** Nothing
- **Risk:** Very low. This is adding awareness/guidance to existing files. The author already defers to the guidance file for doc-system-specific syntax -- mermaid follows the same pattern.

---

## Feature 5: OCaml .mld/.mli Output Format Switching

### What It Is

Currently, doc-author writes `.md` files to `paths.docs_root` for all frameworks. For odoc projects, the author should write `.mld` files to `doc/` and optionally enrich `.mli` files with doc comments. This requires the author to detect the output format and switch writing patterns.

### Integration Points

**Modified files:**

| File | Change | Scope |
|------|--------|-------|
| `agents/doc-author.md` | Format detection + conditional writing logic for odoc. Phase 2 writing workflow branches on `doc_system`. | **Large** -- significant new section |
| `skills/write/scripts/scan-exports.sh` | New `ocaml` case for scanning `.mli` files | Medium -- new language case |
| `skills/setup/defaults/odoc.qa.md` | Already has "Author scope" question (Q2) for `.mld + .mli` vs `.mld only`. No change needed. | No change |
| `skills/setup/defaults/odoc.md` | Already has detailed `.mld` and `.mli` guidance. No structural change needed. | No change |
| `agents/doc-editor.md` | Needs to handle `.mld` files in addition to `.md`. Read/Glob patterns for doc discovery need to include `*.mld` and `*.mli`. | Medium |
| `agents/doc-user-tester.md` | Needs to discover `.mld` files. Already reads docs in `paths.docs_root` -- for odoc, also scan `doc/` for `.mld` files. | Small |

### scan-exports.sh: New OCaml Case

```bash
ocaml)
  echo "## OCaml Module Signatures"
  grep -rn '^val ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
  echo ""
  echo "## OCaml Type Definitions"
  grep -rn '^type ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
  echo ""
  echo "## OCaml Module Declarations"
  grep -rn '^module ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
  echo ""
  echo "## OCaml Exception Declarations"
  grep -rn '^exception ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
  ;;
```

This scans `.mli` files (interface files) since those define the public API surface in OCaml. The `.ml` implementation files are internal.

### Doc-Author Format Switching

The author needs a conditional branch in Phase 2 (Write):

```
IF doc_system == "odoc":
  - Write .mld files to doc/ (not docs/)
  - Use odoc markup ({0 Title}, {1 Section}, {[ code ]}, {v verbatim v})
  - Use odoc cross-references ({!Module.value}, {!page-name})
  - Register each new .mld in doc/dune (mld_files stanza)
  - If scope includes .mli: enrich public .mli files with doc comments
  - File naming: underscores only, no hyphens
ELSE:
  - Write .md files to paths.docs_root (existing behavior)
  - Use markdown syntax
```

**Key doc-author.md additions:**

1. **Format detection in Step 1** (Read Configuration): After reading `doc_system`, set `output_format` to either `"markdown"` or `"odoc"`. This drives the rest of Phase 2.

2. **New section: "Section 8: Odoc Output Format"** covering:
   - `.mld` file structure (heading levels, code blocks, cross-references)
   - Dune registration requirement (every .mld must be in `(mld_files ...)`)
   - `.mli` enrichment rules (when author scope includes .mli)
   - File naming rules (underscores only)
   - The guidance file (`odoc.md`) already documents all syntax -- the author section points to it rather than duplicating

3. **Phase 2 write workflow fork:** After loading the diataxis reference for each page type, apply the format translation. The diataxis reference provides structure (e.g., "tutorials should have Prerequisites, Steps, Verification"), and the format determines how that structure is expressed (markdown headings vs. odoc `{1 ...}` headings).

### Dune Registration Automation

When writing a new `.mld` file, the author must also update `doc/dune`:

```scheme
;; doc/dune
(documentation
 (package my_library)
 (mld_files index getting_started new_page))  ; <-- add new_page
```

The author should:
1. Read `doc/dune`
2. Parse the `(mld_files ...)` list
3. Append the new page name (without `.mld` extension)
4. Write the updated `doc/dune`

This is critical -- unregistered `.mld` files silently do not appear in generated docs. The odoc guidance file already calls this out as "the single most common reason pages go missing."

### Editor and Persona Changes for .mld

**doc-editor.md:**
- Step 2 (Discover Documentation Files): Glob pattern must include `*.mld` when `doc_system == "odoc"`. Currently hardcoded to `*.md`.
- Pass 1 (Terminology): Works on any text format -- no change needed.
- Pass 2 (Diataxis Type Integrity): Works on content structure -- needs to understand odoc heading syntax (`{1 ...}`) instead of markdown headings.
- Pass 3 (Humanizer): Works on prose -- no change needed.
- Pass 4 (Cross-Reference): Needs to understand odoc cross-reference syntax (`{!Module.value}`) instead of markdown links.
- Strip internal notes: Must handle odoc comment syntax -- see Internal Notes Problem below.

**doc-user-tester.md:**
- Step 3 (Discover Documentation Files): Glob pattern must include `*.mld` when `doc_system == "odoc"`.
- Reading .mld content: The persona agent reads docs as a user would. For odoc, the "rendered" form is HTML generated by `dune build @doc`. The agent should read the .mld source directly (it can interpret odoc markup) since it cannot run the build.

### Internal Notes Problem for .mld

The current internal notes mechanism uses HTML comments (`<!-- INTERNAL NOTES FOR EDITOR -->`). This works in markdown because HTML comments are invisible in rendered output.

In `.mld` files, HTML comments are not valid odoc syntax. Options:

1. **Skip internal notes for odoc output.** The editor already has source file access via `paths.source_root` -- it does not strictly need author notes embedded in the doc files.
2. **Use odoc's own comment syntax** with a marker. But content in .mld is all rendered -- there is no invisible comment mechanism.
3. **Write a separate notes file per .mld page** (e.g., `.doc-writer/author-notes.md`). The editor reads this companion file.

**Recommendation:** Option 3. The author writes all internal notes for odoc pages to a single `.doc-writer/author-notes.md` file, organized by page name. The editor reads this file during pre-processing (Step 3). This avoids odoc syntax issues entirely and keeps the mechanism consistent -- just the storage location changes.

### Build Implications

- **Depends on:** Nothing technically, but benefits from Feature 1 (use cases in context.md) for richer odoc content
- **Blocks:** Nothing
- **Risk:** **Medium-High.** This is the most complex feature. The author needs to handle two fundamentally different output formats. The main risks:
  1. Dune registration being forgotten (mitigated by making it explicit in the workflow)
  2. Editor not recognizing odoc syntax (mitigated by conditional logic on doc_system)
  3. Internal notes mechanism needs rethinking for .mld files (mitigated by external notes file)

---

## Feature 6: Default Concepts Page Proposal Under Explanation

### What It Is

When the author proposes the page inventory in plan mode, automatically suggest a "Concepts" or "Key Concepts" page under the Explanation category. This is not a code change to the architecture -- it is a behavioral guidance addition.

### Integration Points

| File | Change | Scope |
|------|--------|-------|
| `agents/doc-author.md` | Add guidance in Phase 1 (Step 3: Propose Page Inventory) to always include a Concepts explanation page when the library has 3+ distinct concepts/abstractions. | Small |
| `skills/diataxis/references/explanation.md` | Add "Pattern 5: Key Concepts Overview" template showing a concepts page structure. | Small |

This is the simplest feature. No config changes, no new data flows, no new files. Just behavioral guidance for the author agent.

---

## Cross-Feature Dependencies

```
Feature 1: Use Cases Q&A
    |
    v (provides data for)
Feature 2: Use Cases Docs Section
    |
    (independent of all others)

Feature 3: Nav Structure         Feature 4: Mermaid
    (independent)                    (independent)

Feature 5: OCaml .mld/.mli      Feature 6: Concepts Page
    (independent)                    (independent)
```

Only Feature 2 depends on Feature 1. All other features are independent and can be built in any order.

---

## Suggested Build Order

Based on dependency analysis, complexity, and blast radius:

| Order | Feature | Rationale |
|-------|---------|-----------|
| 1 | Feature 6: Concepts Page | Smallest change, warms up the codebase. Pure guidance addition. |
| 2 | Feature 4: Mermaid | Small, well-contained. Guidance file additions + doc-author awareness. |
| 3 | Feature 3: Nav Structure | Medium. Modifies existing Q&A and guidance files. No new patterns. |
| 4 | Feature 1: Use Cases Q&A | Medium. New setup step + config field + researcher expansion. Follows established patterns. |
| 5 | Feature 2: Use Cases Docs Section | Medium. Depends on Feature 1. New page type in author + editor exemption. |
| 6 | Feature 5: OCaml .mld/.mli | Large. Format switching, scan-exports, editor/persona .mld awareness, internal notes rethink. Highest risk. Do last to avoid blocking other work. |

---

## Component Change Matrix

Files grouped by how many features touch them:

| File | F1 | F2 | F3 | F4 | F5 | F6 | Total |
|------|----|----|----|----|----|----|-------|
| `agents/doc-author.md` | read | template | read | section | **large** | guidance | 6 |
| `skills/setup/SKILL.md` | **new step** | question | - | - | - | - | 2 |
| `skills/setup/defaults/config-template.yaml` | field | field | - | - | - | - | 2 |
| `agents/doc-researcher.md` | section | - | - | - | - | - | 1 |
| `agents/doc-editor.md` | - | exempt | - | - | .mld | - | 2 |
| `agents/doc-user-tester.md` | read | - | - | - | .mld | - | 2 |
| `skills/setup/defaults/mkdocs-material.qa.md` | - | - | **expand** | - | - | - | 1 |
| `skills/setup/defaults/sphinx-shibuya.qa.md` | - | - | **expand** | - | - | - | 1 |
| `skills/setup/defaults/mkdocs-material.md` | - | nav note | **expand** | **section** | - | - | 3 |
| `skills/setup/defaults/sphinx-shibuya.md` | - | nav note | **expand** | **section** | - | - | 3 |
| `skills/setup/defaults/odoc.md` | - | note | - | note | - | - | 2 |
| `skills/setup/defaults/plain-markdown.md` | - | - | - | **section** | - | - | 1 |
| `skills/write/scripts/scan-exports.sh` | - | - | - | - | **case** | - | 1 |
| `skills/diataxis/references/explanation.md` | - | - | - | note | - | pattern | 2 |

**Hotspot:** `agents/doc-author.md` is touched by all six features. Plan changes carefully to avoid merge conflicts. Consider building features that touch the author in sequence, not parallel.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Putting Nav Strategy in config.yaml

**What people do:** Store navigation strategy choice in config.yaml alongside doc_system.
**Why it is wrong:** Framework Q&A answers intentionally do not go into config.yaml. Config stores identity (who, what system, what paths). Framework preferences flow through the researcher into context.md. Putting nav strategy in config breaks this separation and couples config schema to framework-specific concepts.
**Do this instead:** Follow the existing pattern. Nav strategy answer goes to researcher via Agent tool message, researcher writes it to context.md, downstream agents read context.md.

### Anti-Pattern 2: Creating a Diataxis Reference File for Use Cases

**What people do:** Create `skills/diataxis/references/use-cases.md` parallel to tutorials.md, how-to-guides.md, etc.
**Why it is wrong:** Use Cases is explicitly not a diataxis type. Adding it to the diataxis references directory implies it is one, which confuses the classification system and the agents that rely on it.
**Do this instead:** Put the Use Case template in doc-author.md as a dedicated section (like README and MAINTAINER templates). It lives with the agent, not with the framework.

### Anti-Pattern 3: Hardcoding .mld Syntax in doc-author.md

**What people do:** Put odoc syntax rules (heading levels, code blocks, cross-references) directly in the doc-author agent.
**Why it is wrong:** The existing architecture deliberately separates syntax knowledge (guidance files) from writing workflow (agent). The author reads `.doc-writer/{doc_system}.md` at runtime. Hardcoding odoc syntax in the agent duplicates information and drifts out of sync.
**Do this instead:** The author should read the odoc guidance file for syntax details. The agent file should contain only the workflow branch (when to write .mld vs .md, how to register in dune) -- not the odoc syntax itself.

### Anti-Pattern 4: Rebuilding Scaffold Templates Per Nav Strategy

**What people do:** Create `scaffolds/mkdocs-material-tabs.yml`, `scaffolds/mkdocs-material-flat.yml`, etc.
**Why it is wrong:** File multiplication. The setup SKILL.md already has template processing logic that can handle conditional sections.
**Do this instead:** Keep one scaffold template per framework. Extend the setup SKILL.md's variable substitution step to handle nav strategy as a processing parameter, generating the appropriate nav section.

---

## Sources

- All findings derived from reading the existing codebase files listed in the Component Change Matrix
- odoc guidance: `skills/setup/defaults/odoc.md` (v1.0 content)
- Setup flow: `skills/setup/SKILL.md` (v1.0 content)
- Author agent: `agents/doc-author.md` (v1.0 content)
- Researcher agent: `agents/doc-researcher.md` (v1.0 content)
- Editor agent: `agents/doc-editor.md` (v1.0 content)
- Config schema: `skills/setup/defaults/config-template.yaml` (v1.0 content)

---
*Architecture research for: doc-writer v1.4.0 feature integration*
*Researched: 2026-03-21*
