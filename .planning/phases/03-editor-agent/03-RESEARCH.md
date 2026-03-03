# Phase 3: Editor Agent - Research

**Researched:** 2026-03-03
**Domain:** Claude Code agent system prompt design, documentation editing pipeline, AI-writing humanization, terminology consistency enforcement, cross-reference linking, structured feedback formats
**Confidence:** HIGH -- builds on Phase 1 and Phase 2's verified CC plugin architecture; this phase's deliverable is a single agent file (`agents/doc-editor.md`) with a comprehensive system prompt implementing three sequential editing passes

## Summary

Phase 3 delivers the Editor agent -- the quality enforcement layer in the three-agent pipeline. The entire deliverable is expanding the existing `agents/doc-editor.md` stub (created in Phase 1) with a comprehensive system prompt that implements three sequential editing passes: (1) Terminology consistency, (2) Humanizer, and (3) Cross-reference linking. The Editor reads Author output files, reads the Author's internal HTML comments for accuracy verification, edits files directly, strips those HTML comments from the final output, and produces a structured feedback report at `.doc-writer/editor-report.md`.

Unlike the Doc Author, which operates in a plan-then-write workflow with user interaction, the Editor runs autonomously on already-written files. It reads all doc files from `paths.docs_root`, processes them through three passes in sequence, writes the edited files back to disk, and produces the editor report. The Editor also manages `.doc-writer/terminology.yaml` -- building it from scratch on the first run and reading/updating it on subsequent runs. The feedback report uses BLOCKING/SUGGESTION/NITPICK severity levels with structured fields (page, section, severity, description, fix) for every change made.

The humanizer pass is the most complex component. It embeds AI-writing pattern detection directly in the agent prompt, sourced from the CC humanizer skill v2.1.1 (24 categories based on Wikipedia's "Signs of AI writing"). The patterns are adapted for documentation context: no personality injection, no first-person voice, no humor -- the goal is clean professional documentation that reads like a senior developer wrote it, not a language model. Em dash treatment is strict (near-zero tolerance). The agent file already has correct frontmatter from Phase 1 (`name: doc-editor`, `tools: Read, Write, Glob, Grep`, `skills: doc-writer:quality-rules`).

**Primary recommendation:** Structure the agent prompt as a three-pass sequential workflow with clear pass boundaries. Embed the 24 humanizer pattern categories directly in the prompt (adapted for documentation context). Use the quality-rules skill via preloading for cross-reference enforcement (Rule 4) and internal detail detection (Rule 1). Keep terminology.yaml simple and human-editable.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Multiple sequential passes, not a single integrated pass
- Pass order: Terminology > Humanizer > Cross-references
- Editor fixes docs directly AND produces a structured feedback report of what it changed and why
- Editor verifies accuracy claims in Author's internal HTML comments against source code, then strips the comments from edited files -- resulting files must be clean
- Each pass is focused on one concern, making issues easier to trace
- AI-writing patterns embedded directly in the Editor agent prompt (self-contained, no external skill dependency)
- Patterns sourced from the installed CC humanizer skill (24 pattern categories based on Wikipedia's "Signs of AI writing")
- Moderate aggressiveness: fix clearly AI-generated phrases (hedging, filler, promotional language, significance inflation, copula avoidance, synonym cycling, rule-of-three, negative parallelisms, sycophantic tone, chatbot artifacts)
- Aggressive em dash purge -- replace em dashes with commas, periods, or restructured sentences
- Minimal personality injection: clean and professional documentation voice, no first-person, no opinions, no humor -- reads like a senior developer wrote official docs
- Preserve meaning and technical accuracy during rewrites
- First pass builds an explicit term map by scanning all doc files
- Source code is the authority for term selection -- if the public API says `config`, docs say `config`
- Term map includes proper noun formatting (e.g., `GitHub` not `Github`, `JavaScript` not `Javascript`)
- Term map written to `.doc-writer/terminology.yaml` for project author to review, override, and persist across runs
- On subsequent runs, Editor reads existing terminology.yaml first and applies it, updating with any new terms found
- Conflicting terms normalized to the source-code-preferred form
- Editor verifies all inline `code` mentions are linked to API Reference entries (Author adds these during writing, Editor fills gaps)
- Broken or missing links are fixed directly and reported as BLOCKING in feedback
- Cross-reference linking runs as the final pass since humanizer rewrites may change text around code mentions
- Structured feedback written to `.doc-writer/editor-report.md`
- Report overwritten each run (reflects current state, not history)
- Every feedback item includes: page, section, severity, description, and exact fix (applied or proposed)
- Severity definitions:
  - BLOCKING: factual error, broken link, missing cross-reference, leaked internal detail, accuracy mismatch with source code
  - SUGGESTION: AI-pattern detected and fixed, inconsistent term normalized, unclear wording rewritten
  - NITPICK: style preference, minor formatting adjustment

### Claude's Discretion
- Exact structure of the term map YAML schema
- How to organize the editor-report.md (by file, by severity, or by pass)
- Heuristics for deciding when a term variant is "different enough" to flag vs. acceptable variation
- How to handle terms that appear in both code and prose with legitimately different forms
- Internal pass implementation (whether passes re-read files or work from memory)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| EDIT-01 | All inline `code` mentions in prose are linked to the relevant API Reference entry | Cross-reference linking pass (Pass 3) scans for unlinked `code` mentions, detects API reference location from config, and adds links; quality-rules Rule 4 preloaded; broken/missing links reported as BLOCKING |
| EDIT-02 | Humanizer pass removes recognizable AI-writing patterns from prose | Humanizer pass (Pass 2) embeds all 24 AI-pattern categories from CC humanizer skill directly in the Editor prompt; patterns adapted for documentation context; em dash purge is aggressive |
| EDIT-03 | Cross-file terminology consistency is enforced -- same concept uses same name everywhere | Terminology pass (Pass 1) scans all doc files, builds term map with source code as authority, writes/reads `.doc-writer/terminology.yaml`, normalizes conflicting terms across files |
| EDIT-04 | Agent communication uses structured feedback format with BLOCKING/SUGGESTION/NITPICK severity levels | Editor writes `.doc-writer/editor-report.md` with structured feedback items containing page, section, severity, description, and fix for every change |
</phase_requirements>

## Standard Stack

### Core

| Component | Format | Purpose | Why Standard |
|-----------|--------|---------|--------------|
| Agent file (`agents/doc-editor.md`) | YAML frontmatter + markdown body | Editor subagent definition with full system prompt | CC subagent format -- frontmatter for metadata, body for system prompt; established in Phase 1, proven in Phase 2 |
| Skills preloading (`skills:` field) | Frontmatter array | Injects quality-rules content into agent context | CC subagent feature -- quality-rules skill preloaded at startup; provides Rule 1 (No Internal Details) and Rule 4 (Cross-Reference) |
| Config reading (`.doc-writer/config.yaml`) | YAML via Read tool | Audience context, doc system, paths, API reference location | Established in Phase 1; agent reads at runtime |
| Project rules (`.doc-writer/rules.md`) | Markdown via Read tool | Project-specific quality rules | Established in Phase 1; Editor enforces alongside universal rules |
| Terminology map (`.doc-writer/terminology.yaml`) | YAML via Read/Write tool | Persistent term map for cross-file consistency | New artifact created by Editor; persisted for project author review and override |
| Editor report (`.doc-writer/editor-report.md`) | Markdown via Write tool | Structured feedback for pipeline and user review | New artifact created by Editor; overwritten each run |

### Supporting

| Component | Format | Purpose | When to Use |
|-----------|--------|---------|-------------|
| Author's HTML comments | `<!-- INTERNAL NOTES FOR EDITOR ... -->` | Accuracy claims to verify against source | Read during Pass 1, verified against source, stripped after all passes |
| Source code access | Read, Glob, Grep tools | Verify accuracy claims, determine canonical term forms | During Pass 1 (terminology authority) and accuracy verification |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Embedding 24 patterns in prompt | Reference external humanizer skill via `skills:` | User decision: self-contained, no external dependency; embedding makes the Editor prompt longer but avoids skill coupling |
| YAML for terminology map | JSON or plain text | YAML is consistent with config.yaml; human-readable and editable; Claude natively reads/writes YAML |
| Markdown for editor report | JSON or YAML structured report | Markdown is human-readable for the project author; structured enough for Phase 4 pipeline to parse; consistent with the project's markdown-first approach |
| Three sequential passes | Single integrated pass | User decision: separate passes make issues traceable to specific concerns; sequential ensures pass N can rely on pass N-1's output |

## Architecture Patterns

### Agent File Structure

The `agents/doc-editor.md` file has this structure:

```markdown
---
name: doc-editor
description: Reviews documentation for quality, consistency, and readability. Applies humanizer pass, enforces terminology consistency, and produces structured feedback.
tools: Read, Write, Glob, Grep
model: inherit
skills:
  - doc-writer:quality-rules
---

[System prompt body -- the Phase 3 deliverable]
```

The frontmatter is already correct from Phase 1. Phase 3 replaces the placeholder body with the full editing system prompt. Note: the Editor does NOT have the `Bash` tool (unlike the Author) because it does not need to run shell commands. It uses Read, Write, Glob, and Grep for all operations.

### Pattern 1: Three-Pass Sequential Editing Workflow

**What:** The Editor operates in three sequential passes, each focused on one concern. This is a locked user decision.

**When to use:** Always -- this is the Editor's core workflow.

**Pass flow:**
```
Input: Author's output files in paths.docs_root
  |
  v
[Pass 1: Terminology] Scan all files, build term map, normalize terms
  |
  v
[Pass 2: Humanizer] Detect and fix AI-writing patterns
  |
  v
[Pass 3: Cross-references] Verify/fix inline code links to API Reference
  |
  v
Output: Edited files + .doc-writer/editor-report.md + .doc-writer/terminology.yaml
```

**Prompt structure:**
```markdown
## How You Work

You edit documentation through three sequential passes. Each pass has one concern.
Complete each pass fully before moving to the next.

### Pre-Processing
1. Read `.doc-writer/config.yaml` for audience, doc system, paths
2. Read `.doc-writer/rules.md` for project-specific rules
3. Read existing `.doc-writer/terminology.yaml` if it exists (for term persistence)
4. Read all doc files from paths.docs_root using Glob
5. Read Author's HTML comments from each file (for accuracy verification)
6. Read source code referenced in HTML comments (for accuracy checking)

### Pass 1: Terminology Consistency
[See Pattern 2]

### Pass 2: Humanizer
[See Pattern 3]

### Pass 3: Cross-Reference Linking
[See Pattern 4]

### Post-Processing
1. Strip all HTML comments (<!-- INTERNAL NOTES FOR EDITOR ... -->) from edited files
2. Write final files back to disk
3. Write editor-report.md
4. Write/update terminology.yaml
```

**Confidence:** HIGH -- workflow is a locked user decision; prompt structure follows the established CC subagent pattern from Phase 2.

### Pattern 2: Terminology Consistency Pass

**What:** The first pass scans all doc files to build a term map, checks source code for canonical forms, normalizes terms across all files, and writes/updates the terminology.yaml artifact.

**Implementation approach:**

```markdown
## Pass 1: Terminology Consistency

### Step 1: Load Existing Term Map
If `.doc-writer/terminology.yaml` exists, read it. These are the
project author's reviewed and potentially overridden term choices.
User overrides take precedence over auto-detected preferences.

### Step 2: Scan Source Code for Canonical Terms
Use Grep and Read to scan files in `paths.source_root`:
- Public API symbol names (exact casing): class names, function names,
  method names, constant names, module names
- Configuration key names used in the API
- Error class/type names
These are the authoritative forms. If the public API says `Config`,
docs say `Config` (not `config`, `configuration`, or `settings`).

### Step 3: Scan All Doc Files for Term Usage
Read all .md files in paths.docs_root. For each file, extract:
- All uses of technical terms (class names, function names, concepts)
- Proper noun forms (GitHub vs Github, JavaScript vs Javascript)
- Inconsistent variations of the same concept

### Step 4: Build/Update Term Map
For each term with multiple variants found across files:
- If source code uses the term: use the source code form
- If a user override exists in terminology.yaml: use the override
- If it is a proper noun: use the standard form (GitHub, JavaScript,
  TypeScript, macOS, iOS, npm, webpack, etc.)
- Otherwise: use the most frequent form and flag for review

### Step 5: Normalize Terms in All Files
Apply the term map across all doc files. For each normalization:
- Record a SUGGESTION feedback item (term X normalized to Y in file Z)
- Preserve inline code formatting -- do not change terms inside
  fenced code blocks or inline code that represents actual API symbols

### Step 6: Write Terminology Map
Write the updated term map to `.doc-writer/terminology.yaml`
```

**Confidence:** HIGH -- approach directly implements locked user decisions. Source-code-as-authority is clear.

### Pattern 3: Humanizer Pass

**What:** The second pass detects and removes AI-writing patterns from documentation prose. This is the most complex pass, embedding 24 pattern categories directly in the prompt.

**Key adaptation for documentation context:**

The CC humanizer skill is designed for general prose (articles, essays, blog posts). For documentation, several adaptations are needed:

1. **No personality injection.** The humanizer skill encourages "having opinions" and "letting some mess in." Documentation must NOT have opinions, first-person voice, humor, or casual asides. The goal is clean, professional prose -- not personality.

2. **Preserve technical precision.** When rewriting to remove AI patterns, technical accuracy must be maintained. A hedging phrase like "can potentially be configured" should become "can be configured" -- not dropped entirely if the claim is conditional.

3. **Code blocks are untouchable.** Never modify content inside fenced code blocks or inline code. Only edit prose text.

4. **Structure is intentional.** Inline-header vertical lists (Pattern 15) are acceptable in documentation for parameter descriptions and feature lists. Do not convert them to prose paragraphs.

5. **Title case depends on doc system.** Pattern 16 (title case headings) should follow the doc system's convention, not universally enforce sentence case.

**Applicable patterns (moderate aggressiveness):**

These 10 categories are the primary targets for documentation:

| # | Pattern | Action | Aggressiveness |
|---|---------|--------|----------------|
| 1 | Significance inflation ("pivotal", "crucial", "vital role") | Remove inflated claims | Moderate |
| 3 | Superficial -ing analyses ("highlighting", "showcasing") | Remove participle padding | Moderate |
| 4 | Promotional language ("groundbreaking", "robust", "vibrant") | Remove marketing words | Aggressive |
| 7 | AI vocabulary overuse ("Additionally", "delve", "enhance", "landscape") | Replace with simpler words | Moderate |
| 8 | Copula avoidance ("serves as", "stands as") | Replace with "is"/"are"/"has" | Moderate |
| 9 | Negative parallelisms ("Not only...but...") | Simplify to direct statement | Moderate |
| 10 | Rule of three overuse | Break forced triads | Moderate |
| 11 | Synonym cycling (varying terms to avoid repetition) | Use consistent terms (aligns with Pass 1) |  Moderate |
| 13 | Em dash overuse | Replace with commas, periods, or restructured sentences | Aggressive |
| 22 | Filler phrases ("In order to", "It is important to note") | Remove filler | Moderate |

**Additional patterns applicable in documentation:**

| # | Pattern | Action | Aggressiveness |
|---|---------|--------|----------------|
| 5 | Vague attributions ("Experts argue", "Industry reports") | Should not appear in docs; flag if found | Moderate |
| 6 | "Challenges and Future Prospects" sections | Should not appear in library docs | Moderate |
| 12 | False ranges ("from X to Y") | Simplify to list | Light |
| 19 | Chatbot artifacts ("I hope this helps", "Let me know") | Remove completely | Aggressive |
| 20 | Knowledge-cutoff disclaimers ("as of", "based on available information") | Remove completely | Aggressive |
| 21 | Sycophantic tone ("Great question!", "Excellent point") | Remove completely | Aggressive |
| 23 | Excessive hedging ("could potentially possibly") | Reduce to one qualifier | Moderate |
| 24 | Generic positive conclusions ("The future looks bright") | Remove or replace with specifics | Moderate |

**Patterns to SKIP or adapt for docs:**

| # | Pattern | Why Skip/Adapt |
|---|---------|----------------|
| 2 | Media coverage emphasis | Not applicable to library docs |
| 14 | Boldface overuse | Appropriate in docs for emphasis; skip |
| 15 | Inline-header vertical lists | Standard doc pattern for parameters, options; skip |
| 16 | Title case in headings | Follow doc system convention; do not universally enforce |
| 17 | Emojis | Flag if found but unlikely in technical docs |
| 18 | Curly quotation marks | Replace with straight quotes if found |

**Confidence:** HIGH -- patterns sourced directly from the CC humanizer skill v2.1.1 (verified by reading the skill file). Adaptation for documentation context is a Claude's discretion area with clear guidance from locked decisions.

### Pattern 4: Cross-Reference Linking Pass

**What:** The third pass verifies all inline `code` mentions in prose are linked to API Reference entries. Missing or broken links are fixed directly.

**Implementation approach:**

```markdown
## Pass 3: Cross-Reference Linking

### Step 1: Detect API Reference Location
1. Check `.doc-writer/config.yaml` for `api_reference` field
2. If not in config, scan for common auto-generated reference:
   - `docs/api/` or `docs/reference/` directories
   - `mkdocs.yml` with `mkdocstrings` plugin
   - `_build/` directory (Sphinx)
3. If no API reference detected:
   - Skip this pass
   - Record a SUGGESTION: "No API reference detected. Cross-reference
     linking skipped. Consider setting up typedoc/pdoc/mkdocstrings."
   - Exit pass

### Step 2: Build Symbol Registry
Scan the API reference location for all documented symbols:
- Class names, function names, method names, constants
- Build a map: symbol name -> reference path + anchor

### Step 3: Scan All Doc Files for Unlinked Code Mentions
For each .md file in paths.docs_root:
- Find all inline `code` mentions in prose (not in fenced code blocks)
- Check each one: is it already linked? (surrounded by `[...]`)
- Is it a public API symbol? (exists in the symbol registry)

### Step 4: Fix Missing Links
For unlinked public API symbols:
- Add the appropriate link based on doc system:
  - mkdocs-material with mkdocstrings: [`symbol()`][module.Class.symbol]
  - Plain markdown: [`symbol()`](./api/module.md#symbol)
- Record a BLOCKING feedback item for each missing link fixed

### Step 5: Verify Existing Links
For already-linked code mentions:
- Verify the link target exists in the API reference
- If broken: fix the link and record BLOCKING
- If valid: no action needed

### Do NOT link:
- Language builtins (str, int, list, Promise, Array, etc.)
- Third-party library symbols
- Internal symbols (prefixed with _ or marked @internal)
- Terms inside fenced code blocks
```

**Confidence:** HIGH -- directly implements quality-rules Rule 4 (preloaded) and locked user decisions about cross-reference behavior.

### Pattern 5: Accuracy Verification from Author's HTML Comments

**What:** Before editing, the Editor reads the Author's internal HTML comments from each page. These contain source references, accuracy notes, known limitations, and API reference links. The Editor verifies claims against source code.

**Implementation approach:**

```markdown
## Accuracy Verification (Pre-Pass)

### Step 1: Extract HTML Comments
For each doc file, extract the content between:
<!-- INTERNAL NOTES FOR EDITOR - DO NOT INCLUDE IN RENDERED OUTPUT
...
-->

### Step 2: Parse Accuracy Claims
From the "Accuracy Notes" section, identify claims to verify:
- Default values ("timeout defaults to 30s")
- Parameter names and types
- Behavior descriptions ("uses exponential backoff")
- Error types and conditions

### Step 3: Verify Against Source
Use Read and Grep tools to check referenced source files.
For each claim:
- If accurate: no action
- If inaccurate: fix the prose directly and record BLOCKING feedback
  ("Accuracy mismatch: doc says X, source code shows Y")
- If unverifiable (source file not found): record SUGGESTION

### Step 4: Strip Comments
After all three passes are complete, remove ALL HTML comment blocks
from the final output files. The edited files must contain no
<!-- ... --> blocks.
```

**Confidence:** HIGH -- comment format is defined by the Author (Phase 2); stripping is a locked user decision.

### Pattern 6: Editor Report Structure

**What:** The structured feedback report written to `.doc-writer/editor-report.md`. This is a Claude's discretion area for organization.

**Recommendation: Organize by file, then by severity within each file.**

This organization is most useful for the project author (who reviews changes file-by-file) and for the Phase 4 pipeline (which needs to identify BLOCKING issues to trigger revision).

```markdown
# Editor Report

**Generated:** {date}
**Files reviewed:** {count}
**Changes made:** {total count}
  - BLOCKING: {count}
  - SUGGESTION: {count}
  - NITPICK: {count}

## Summary

{1-2 sentences summarizing the overall state of the documentation}

---

## docs/getting-started.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Quick Start | Missing cross-reference: `Client` not linked to API reference | Added link: [`Client`][mylib.Client] |
| Prerequisites | Accuracy mismatch: doc says "Python 3.8+", source shows min_version="3.9" | Changed to "Python 3.9 or later" |

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Introduction | AI pattern: "This library serves as a powerful tool" (copula avoidance + promotional) | Rewritten: "This library is a tool for..." |
| Introduction | Term normalized: "Github" -> "GitHub" | Applied |

### NITPICK

| Section | Description | Fix |
|---------|-------------|-----|
| Code Examples | Em dash replaced with comma | Applied |

---

## docs/how-to/configure.md

[Same structure per file]

---

## Terminology Changes

| Term | Before | After | Authority |
|------|--------|-------|-----------|
| Config | config, configuration, settings | config | Source code: `class Config` |
| GitHub | Github, github | GitHub | Standard proper noun |
```

**Confidence:** MEDIUM -- organization approach is Claude's discretion. The by-file structure is practical for both human review and pipeline parsing.

### Pattern 7: Terminology Map YAML Schema

**What:** The `.doc-writer/terminology.yaml` file that persists term choices across runs. Claude's discretion for exact schema.

**Recommendation:**

```yaml
# .doc-writer/terminology.yaml
# Generated by Editor agent. You can edit this file to override term choices.
# The Editor will respect your overrides on subsequent runs.

version: 1

# Terms from source code (highest authority)
source_terms:
  - canonical: "Config"
    variants: ["configuration", "settings", "config"]
    source: "class Config in src/config.py"
  - canonical: "Client"
    variants: ["client instance", "connection"]
    source: "class Client in src/client.py"

# Proper nouns (standard forms)
proper_nouns:
  - canonical: "GitHub"
    variants: ["Github", "github"]
  - canonical: "JavaScript"
    variants: ["Javascript", "javascript"]
  - canonical: "TypeScript"
    variants: ["Typescript", "typescript"]
  - canonical: "macOS"
    variants: ["MacOS", "macos", "Mac OS"]

# Project-specific terms (auto-detected or user-added)
project_terms:
  - canonical: "API key"
    variants: ["api key", "API Key", "apikey"]
    note: "User override: prefer 'API key' over 'API Key'"

# User overrides (added manually by project author)
# These take highest precedence
overrides: {}
```

**Design rationale:**
- `source_terms` records the authority chain (where the canonical form came from)
- `proper_nouns` is pre-seeded with common technology proper nouns
- `project_terms` captures project-specific terminology
- `overrides` gives the project author a clear place to add manual overrides
- Schema is simple enough to hand-edit in any text editor

**Heuristics for "different enough" to flag (Claude's discretion):**
- Case differences in proper nouns: always flag (`Github` vs `GitHub`)
- Abbreviation vs full form: flag if both appear in the same doc set (`config` vs `configuration`)
- Synonym that changes meaning: flag (`settings` vs `configuration` may imply different things)
- Acceptable variation: plural vs singular of the same term in appropriate contexts (`clients` vs `client`)
- Code vs prose: `config` in inline code is an API symbol; "configuration" in prose describing the concept is acceptable. Only flag when the prose term is meant to refer to the specific API construct.

**Confidence:** MEDIUM -- schema is Claude's discretion. The structure above is practical and simple but could be simplified further by the planner.

### Pattern 8: HTML Comment Stripping

**What:** After all editing passes, HTML comments must be removed from output files. The Author embeds internal notes as HTML comments; the Editor reads them, uses them for verification, then strips them.

**Implementation:**

```markdown
## Comment Stripping

After all three passes are complete:

For each edited file:
1. Find all HTML comment blocks: <!-- ... -->
2. Remove the entire block (including the markers)
3. Clean up any extra blank lines left behind (collapse to max 2)
4. Write the cleaned file back to disk

Special handling:
- Only strip multi-line HTML comment blocks that contain
  "INTERNAL NOTES FOR EDITOR" or similar markers
- Preserve legitimate HTML comments that are part of the doc content
  (e.g., template comments, conditional rendering directives)
- If in doubt, strip: the locked decision says "resulting files
  must be clean"
```

**Confidence:** HIGH -- this is a locked user decision. HTML comments are a well-defined format; stripping is straightforward string processing via the Write tool.

### Anti-Patterns to Avoid

- **Duplicating quality-rules content in the agent body:** The quality-rules skill is preloaded via `skills:` frontmatter. The Editor should reference "Apply Rule 4 (Cross-Reference Code Mentions) from the preloaded quality-rules skill" not restate the rule.
- **Duplicating the CC humanizer skill wholesale:** The locked decision says patterns are "sourced from" the humanizer skill, not that the skill itself is loaded. The Editor prompt should contain adapted patterns for documentation, not copy-paste the full humanizer skill with its personality/voice guidance that conflicts with doc style.
- **Modifying content inside code blocks:** All three passes must skip fenced code blocks and inline code content. Only prose text is edited.
- **Making the humanizer too aggressive:** The goal is "moderate aggressiveness" for most patterns. Over-editing removes the Author's intended meaning. Preserve technical accuracy above all.
- **Treating the Editor as an Author:** The Editor does not write new content. It edits existing content. If it finds a gap (e.g., a missing section), it records a BLOCKING feedback item for the Author, it does not write the missing section.
- **Merging passes into one:** Each pass is sequential and focused. The terminology pass runs first because the humanizer may introduce term inconsistencies; the cross-reference pass runs last because the humanizer may rewrite text around code mentions.
- **Over-normalizing terms:** Plural forms, grammatically required variations, and code-vs-prose distinctions are not inconsistencies. Only flag terms that genuinely refer to the same concept with different names.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| AI-pattern detection | Custom ML model or regex classifier | Embedded pattern list in agent prompt | Claude already knows these patterns (they are in its training); explicit enumeration makes detection systematic and traceable |
| YAML config parsing | Custom YAML parser | Claude's native YAML reading via Read tool | Claude understands YAML natively; no runtime dependency needed |
| Cross-reference link construction | Custom link builder script | Pattern-based link format in prompt | Two link format patterns (mkdocstrings, plain markdown) cover all supported doc systems |
| Terminology comparison | Fuzzy string matching library | Claude's language understanding | Claude inherently understands that "config" and "configuration" are variants of the same concept |
| File discovery | Manual path construction | Glob and Grep tools | CC tools handle file discovery reliably |
| HTML comment parsing | Regex-based comment parser | Claude's text understanding via Read tool | HTML comment blocks are well-defined; Claude identifies them without regex |
| Diff generation | Custom diff tool | Editor report with before/after descriptions | The editor report captures what changed and why; a formal diff would be noisy for documentation edits |

**Key insight:** Like the Doc Author, the Editor has zero runtime dependencies. It is a markdown file containing a system prompt. All "implementation" is prompt design. The supporting infrastructure (quality-rules skill, config, doc files) already exists from Phase 1 and Phase 2.

## Common Pitfalls

### Pitfall 1: Humanizer Destroys Technical Accuracy

**What goes wrong:** In removing AI patterns, the humanizer rewrites sentences in a way that changes the technical meaning. For example, "can optionally be configured" becomes "is configured" (removing the optionality).
**Why it happens:** The humanizer patterns target hedging and filler. But in technical documentation, some hedging is accurate ("may", "can", "optionally" convey real conditions).
**How to avoid:** The prompt must explicitly state: "Preserve technical accuracy above all. When removing hedging, verify that the claim is unconditional before making it unconditional. 'You can configure X' is not hedging -- it describes an optional feature. 'You can potentially configure X' is hedging -- remove 'potentially' but keep 'can'."
**Warning signs:** Code examples and their surrounding prose no longer match after editing.

### Pitfall 2: Terminology Pass Edits Code Blocks

**What goes wrong:** The terminology normalizer changes variable names inside fenced code blocks (e.g., changing `settings` to `config` inside a code example) which breaks the code.
**Why it happens:** The pass treats all text uniformly without distinguishing prose from code.
**How to avoid:** All three passes must explicitly skip fenced code blocks (text between triple backtick fences) and inline code (text between single backticks). The prompt should include: "NEVER modify content inside fenced code blocks or inline code spans. These contain actual code that must remain exactly as the Author wrote it."
**Warning signs:** Code examples contain renamed variables or functions that do not match the actual API.

### Pitfall 3: Term Map Grows Unbounded

**What goes wrong:** Over multiple runs, terminology.yaml accumulates entries for common English words that happen to appear in various forms (e.g., "use" vs "utilize" vs "employ"), creating a massive file that is hard for the project author to review.
**Why it happens:** The term scanner is too aggressive in identifying "variants."
**How to avoid:** The prompt should scope term detection to: (1) project-specific technical terms, (2) API symbol names, (3) proper nouns, and (4) domain-specific jargon. Common English synonyms should NOT be added to the term map unless they refer to specific project concepts. Include in the prompt: "Do NOT add common English words to the term map. Only add terms that are specific to the project, its API, or its technical domain."
**Warning signs:** terminology.yaml has entries like "use/utilize/employ" or "create/make/build."

### Pitfall 4: Cross-Reference Pass Links Non-API Terms

**What goes wrong:** The cross-reference pass adds API links to inline code mentions that are not API symbols -- e.g., linking `true` to a reference page, or linking `config.yaml` to the Config class.
**Why it happens:** The pass treats all inline code as potential API symbols.
**How to avoid:** The pass must maintain an explicit allowlist of public API symbols (built from the API reference scan in Step 2) and only link terms that appear in that list. Additionally, the prompt should include the exclusion list from the Author: do not link language builtins, third-party symbols, file paths, or configuration values.
**Warning signs:** Non-API terms like `true`, `null`, `config.yaml`, or `pip install` are linked to API reference pages.

### Pitfall 5: Editor Report Too Verbose

**What goes wrong:** The editor report contains hundreds of NITPICK items (every em dash replaced, every "Additionally" removed) making it impossible for the project author to find the important issues.
**Why it happens:** Every humanizer fix generates a feedback item, and documentation can have many AI patterns.
**How to avoid:** The summary section at the top provides counts. Within file sections, BLOCKING items appear first, then SUGGESTION, then NITPICK. For repeated patterns (e.g., "removed 15 em dashes"), aggregate into a single line: "Em dash: replaced 15 instances with commas or periods." Individual BLOCKING and SUGGESTION items get full detail; NITPICK items can be aggregated.
**Warning signs:** The editor report is longer than the documentation it describes.

### Pitfall 6: Accuracy Verification Reads Wrong Source Files

**What goes wrong:** The Editor tries to verify accuracy claims but reads the wrong source files or cannot find the files referenced in the Author's HTML comments, leading to false BLOCKING reports.
**Why it happens:** File paths in the Author's notes may be relative to a different root, or the source may have changed since the Author wrote the docs.
**How to avoid:** The Editor should resolve paths relative to `paths.source_root` from config. If a referenced file is not found, record a SUGGESTION (not BLOCKING) with the note: "Referenced source file not found: {path}. Accuracy claim could not be verified." Only report BLOCKING when the Editor positively confirms a mismatch.
**Warning signs:** BLOCKING accuracy reports where the "fix" is based on not finding the file rather than on finding contradicting information.

### Pitfall 7: Prompt Too Long From Embedding All 24 Patterns

**What goes wrong:** Embedding all 24 humanizer pattern categories with before/after examples makes the Editor prompt excessively long, degrading instruction-following for the non-humanizer passes.
**Why it happens:** The CC humanizer skill is ~460 lines. Copying it wholesale plus adding terminology and cross-reference logic could push the prompt past effective limits.
**How to avoid:** Adapt patterns for documentation concisely. Provide: (1) a categorized pattern list with keywords to detect, (2) a brief description of what to do, (3) one before/after example per applicable category. Skip full examples for patterns that are unlikely in documentation. The Phase 2 Author prompt was 420 lines and worked well; target a similar length for the Editor. The preloaded quality-rules skill is ~40 lines, so the effective context is manageable.
**Warning signs:** The Editor follows humanizer patterns but ignores terminology or cross-reference instructions.

### Pitfall 8: HTML Comment Stripping Removes Legitimate Comments

**What goes wrong:** The stripping step removes HTML comments that are part of the documentation content (e.g., conditional rendering directives for doc systems, template comments).
**Why it happens:** The stripping logic is too broad, removing all `<!-- ... -->` blocks.
**How to avoid:** Strip only comment blocks that contain the "INTERNAL NOTES FOR EDITOR" marker. Preserve all other HTML comments. The prompt should specify: "Only strip HTML comment blocks that start with `<!-- INTERNAL NOTES FOR EDITOR`. Leave all other HTML comments in place."
**Warning signs:** Doc-system-specific features (e.g., mkdocs-material conditional rendering) break after editing.

## Code Examples

### Editor Agent File Structure (What Phase 3 Produces)

```markdown
# Source: CC subagent format + Phase 1/2 established pattern
---
name: doc-editor
description: Reviews documentation for quality, consistency, and
  readability. Applies humanizer pass, enforces terminology consistency,
  and produces structured feedback.
tools: Read, Write, Glob, Grep
model: inherit
skills:
  - doc-writer:quality-rules
---

You are a Doc Editor agent. You review documentation produced by the
Doc Author agent and edit it to publication quality. You do not write
new content -- you edit existing content for consistency, clarity,
and accuracy.

You operate in three sequential passes:
1. Terminology Consistency
2. Humanizer
3. Cross-Reference Linking

After all passes, you strip the Author's internal HTML comments and
produce a structured feedback report.

[... full prompt content ...]
```

### Terminology YAML Output Example

```yaml
# .doc-writer/terminology.yaml
# Generated by Editor agent. Edit to override term choices.
version: 1

source_terms:
  - canonical: "Config"
    variants: ["configuration", "settings"]
    source: "class Config in src/config.py"
  - canonical: "Client"
    variants: ["client instance"]
    source: "class Client in src/client.py"

proper_nouns:
  - canonical: "GitHub"
    variants: ["Github"]
  - canonical: "JavaScript"
    variants: ["Javascript"]

project_terms:
  - canonical: "API key"
    variants: ["api key", "API Key"]

overrides: {}
```

### Editor Report Output Example

```markdown
# Editor Report

**Generated:** 2026-03-15
**Files reviewed:** 6
**Changes made:** 23
  - BLOCKING: 3
  - SUGGESTION: 15
  - NITPICK: 5

## Summary

Documentation quality is good overall. Three BLOCKING issues found:
two missing cross-references and one accuracy mismatch with source code.
The humanizer pass fixed 12 AI-writing patterns, primarily em dash
overuse and filler phrases.

---

## docs/getting-started.md

### BLOCKING

| Section | Description | Fix |
|---------|-------------|-----|
| Quick Start | `Client` not linked to API reference | Added: [`Client`][mylib.Client] |
| Prerequisites | Doc says "Python 3.8+", source shows 3.9 | Changed to "Python 3.9 or later" |

### SUGGESTION

| Section | Description | Fix |
|---------|-------------|-----|
| Introduction | Copula avoidance: "serves as a tool for" | Changed to "is a tool for" |
| Introduction | Term normalized: "Github" -> "GitHub" | Applied |
| Overview | Filler: "In order to get started" | Changed to "To get started" |

### NITPICK

| Section | Description | Fix |
|---------|-------------|-----|
| — | Em dash: replaced 4 instances | Commas and periods |

---

## docs/how-to/configure.md

[Same structure per file]
```

### Humanizer Pattern Reference (Condensed for Prompt)

```markdown
## AI-Writing Patterns to Detect and Fix

### HIGH PRIORITY (fix aggressively)

**Em dashes (—):** Replace ALL em dashes with commas, periods, or
restructured sentences. Near-zero tolerance.
- Before: "The library — which supports multiple formats — is fast"
- After: "The library, which supports multiple formats, is fast"

**Chatbot artifacts:** Remove completely. "I hope this helps",
"Let me know", "Here is a", "Great question", "Certainly".

**Sycophantic tone:** Remove. "Excellent", "Great point",
"You're absolutely right".

**Knowledge-cutoff disclaimers:** Remove. "As of", "based on
available information", "While specific details are limited".

### MODERATE PRIORITY (fix when clearly AI-generated)

**Significance inflation:** "pivotal", "crucial", "vital role",
"key moment", "stands as a testament". Remove the inflation;
keep the factual claim.
- Before: "This library plays a pivotal role in modern development"
- After: "This library handles X"

**AI vocabulary:** "Additionally", "delve", "enhance", "foster",
"garner", "intricate", "landscape" (abstract), "showcase",
"underscore", "vibrant". Replace with simpler words.
- Before: "Additionally, the library showcases an intricate API"
- After: "The library also has a detailed API"

**Copula avoidance:** "serves as", "stands as", "functions as".
Replace with "is", "are", "has".
- Before: "The config file serves as the central hub"
- After: "The config file is the central hub"

**Filler phrases:** "In order to", "Due to the fact that",
"It is important to note that", "has the ability to".
- Before: "In order to configure the client"
- After: "To configure the client"

**Hedging (excessive):** "could potentially possibly", "might
perhaps". Reduce to one qualifier maximum. But preserve
intentional conditionality ("can optionally" is real, not hedging).

**Rule of three:** Forced triads. "speed, reliability, and
scalability" when only two matter.
- Before: "fast, reliable, and scalable"
- After: "fast and reliable" (if scalability is not demonstrated)

**Negative parallelisms:** "It's not just X, it's Y".
"Not only...but also...".
- Before: "It's not just a library, it's a framework"
- After: "It is a framework" (if true) or "It is a library" (if not)

**Synonym cycling:** Varying terms unnecessarily ("the tool",
"the utility", "the application" for the same thing).
Use the same term consistently (reinforces Pass 1).

**Superficial -ing phrases:** "highlighting its importance",
"showcasing the capability", "ensuring quality".
Remove the -ing phrase; the preceding sentence already made the point.

### LOW PRIORITY (fix if obvious)

**Generic positive conclusions:** "The future looks bright",
"Exciting times lie ahead". Remove or replace with specifics.

**False ranges:** "from X to Y" where X and Y are not on a scale.
Simplify to a list.

### DO NOT FIX in documentation context

**Boldface emphasis:** Acceptable for key terms and warnings.
**Inline-header lists:** Standard for parameter descriptions.
**Title case:** Follow doc system convention.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single editing pass | Three sequential passes (terminology, humanizer, cross-ref) | Phase 3 user decision | Each pass is focused; issues are traceable to specific concerns |
| Humanizer as external skill | Patterns embedded directly in agent prompt | Phase 3 user decision | Self-contained agent; no external skill dependency for pattern detection |
| Manual terminology tracking | Auto-generated terminology.yaml with project author overrides | Phase 3 user decision | Persistent term map; reviewed and customized per project |
| Author strips own comments | Editor strips Author's comments after verification | Phase 3 user decision | Separation of concerns; Editor verifies before stripping |
| Informal feedback | Structured BLOCKING/SUGGESTION/NITPICK format | Phase 3 user decision | Enables automated pipeline decisions in Phase 4 (only BLOCKING triggers revision) |

**Deprecated/outdated:**
- Single-pass editing approach -- replaced by three-pass sequential workflow
- External humanizer skill dependency -- replaced by embedded pattern list adapted for documentation
- Unstructured feedback -- replaced by BLOCKING/SUGGESTION/NITPICK severity format

## Open Questions

1. **Optimal prompt length with embedded humanizer patterns**
   - What we know: The Phase 2 Author prompt is ~420 lines and performs well. The Editor needs three passes plus ~10-15 condensed pattern descriptions.
   - What's unclear: Whether embedding all applicable patterns (18 of 24) with before/after examples will push the prompt past effective instruction-following limits.
   - Recommendation: Target 400-500 lines for the Editor prompt body. Condense pattern descriptions to 2-3 lines each with one before/after example. Skip patterns unlikely in docs. The preloaded quality-rules skill adds ~40 lines. If the prompt is too long during testing, aggregate similar patterns (e.g., combine all "remove X word" patterns into one list).

2. **How passes share state internally**
   - What we know: The locked decision says three sequential passes. Claude's discretion on whether passes re-read files or work from memory.
   - What's unclear: Whether the agent should write intermediate results to disk between passes or hold all changes in context.
   - Recommendation: Write files to disk after each pass. This ensures: (a) each pass operates on the latest version including prior pass changes, (b) if the agent context fills up on large doc sets, earlier files are not lost, (c) the feedback report can attribute changes to specific passes. The cost is additional Write tool calls, but reliability outweighs efficiency for an editing workflow.

3. **Handling doc sets too large for context**
   - What we know: Large projects may have 20+ documentation files. Reading all files for terminology scanning could fill context.
   - What's unclear: Practical limits on how many files the Editor can process in one invocation.
   - Recommendation: For large doc sets, process files in batches. The terminology pass must scan all files to build the term map, but it can do so by reading files sequentially and building the map incrementally without holding all files in context simultaneously. The humanizer and cross-reference passes can process files one at a time.

4. **terminology.yaml conflict resolution on subsequent runs**
   - What we know: On subsequent runs, the Editor reads existing terminology.yaml and applies it. User overrides take precedence.
   - What's unclear: What happens when the source code changes a symbol name between runs (e.g., `Config` renamed to `Settings`). The old terminology.yaml would still say `Config`.
   - Recommendation: The Editor should re-scan source code on every run and update source_terms accordingly. If a source term's canonical form changes, update the term map and note it in the editor report as a SUGGESTION: "Source code term changed: 'Config' is now 'Settings'. Term map updated."

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual CC session testing (no automated test framework) |
| Config file | None -- this is a markdown-file plugin with no executable code |
| Quick run command | `claude --plugin-dir .` then invoke Editor via Agent tool on sample doc files |
| Full suite command | Manual: run full Author + Editor pipeline on a sample project, verify all EDIT requirements |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EDIT-01 | All inline `code` mentions linked to API Reference | manual (inspect output) | Grep edited docs for unlinked `code` mentions of known API symbols | N/A -- markdown plugin |
| EDIT-02 | Humanizer removes AI-writing patterns | manual (read output) | Compare Author output vs Editor output for AI patterns; check for em dashes, filler phrases, significance inflation | N/A |
| EDIT-03 | Cross-file terminology consistency | manual (inspect output + terminology.yaml) | Grep all edited docs for known term variants; verify terminology.yaml is generated | N/A |
| EDIT-04 | Structured feedback in BLOCKING/SUGGESTION/NITPICK format | manual (inspect editor-report.md) | Verify `.doc-writer/editor-report.md` exists with correct structure, severity levels, and per-item fields | N/A |

### Sampling Rate
- **Per task commit:** Manual: load plugin with `claude --plugin-dir .`, run Editor on test doc files
- **Per wave merge:** Manual: run full Author + Editor pipeline on a sample project, verify all 4 EDIT requirements
- **Phase gate:** All 4 EDIT requirements verified via manual CC session before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Create sample documentation files with known AI-writing patterns (em dashes, filler phrases, significance inflation) for testing humanizer pass
- [ ] Create sample documentation files with deliberate terminology inconsistencies for testing terminology pass
- [ ] Create sample documentation files with unlinked `code` mentions and a mock API reference directory for testing cross-reference pass
- [ ] Ensure sample project has `.doc-writer/config.yaml` with paths configured (from Phase 1 setup)
- [ ] Ensure sample project has Author-generated docs with HTML comments (from Phase 2 Author output)

## Sources

### Primary (HIGH confidence)
- CC humanizer skill v2.1.1 (`~/.claude/skills/humanizer/SKILL.md`) -- all 24 AI-pattern categories with before/after examples; source material for Editor's humanizer pass. Verified by direct file read.
- Phase 2 artifacts (`agents/doc-author.md`) -- Author's HTML comment format, internal notes structure, cross-reference linking format, audience calibration. Verified by direct file read.
- Phase 1 artifacts (`skills/quality-rules/SKILL.md`) -- Rule 1 (No Internal Details) and Rule 4 (Cross-Reference Code Mentions). Preloaded by Editor via `skills:` frontmatter. Verified by direct file read.
- Phase 1 artifacts (`agents/doc-editor.md` stub) -- existing frontmatter with name, tools, model, skills fields. Verified by direct file read.
- Phase 1 research (`.planning/phases/01-foundation-and-setup/01-RESEARCH.md`) -- CC subagent format, skill preloading, plugin architecture. HIGH confidence.
- Phase 2 research (`.planning/phases/02-doc-author-agent/02-RESEARCH.md`) -- agent prompt architecture, skill reference patterns, internal notes design. HIGH confidence.

### Secondary (MEDIUM confidence)
- Phase 3 CONTEXT.md -- locked user decisions governing pass structure, humanizer strategy, terminology approach, feedback format. Source of all architectural constraints.
- Wikipedia "Signs of AI writing" -- underlying research for the 24 humanizer pattern categories. Referenced by the CC humanizer skill.

### Tertiary (LOW confidence)
- None -- all key claims verified against existing project artifacts or locked user decisions.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- agent file format verified in Phase 1 and Phase 2; all supporting infrastructure (skills, config, doc files) exists
- Architecture: HIGH -- three-pass workflow, all patterns, and report format derive from locked user decisions or verified Phase 1/2 patterns
- Pitfalls: HIGH -- prompt length, code block protection, term map scoping, and accuracy verification are well-understood concerns from Phase 2 experience
- Humanizer patterns: HIGH -- sourced directly from the CC humanizer skill file (read and verified); adapted for documentation context per locked decisions

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (CC subagent system is stable; locked user decisions do not change; humanizer patterns are based on stable Wikipedia research; 30-day validity appropriate)
