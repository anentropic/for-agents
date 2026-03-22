# Phase 17: OCaml .mld/.mli Output - Research

**Researched:** 2026-03-22
**Domain:** Agent prompt engineering (doc-author odoc output mode, doc-editor .mld discovery, .mli enrichment proposals, dune registration)
**Confidence:** HIGH

## Summary

Phase 17 switches the doc-author from writing Markdown files to writing odoc-native .mld files when `doc_system` is `odoc`. This is the third syntax track alongside Markdown and RST -- the existing architecture already handles multi-format output through guidance files, so the pattern is established. Four files need modification: doc-author.md (largest change -- conditional write workflow, dune registration, .mli enrichment), doc-editor.md (file discovery, syntax-aware quality passes), doc-user-tester.md (file discovery), and the write SKILL.md (mode detection for .mld files).

The key insight from reading the codebase is that the odoc guidance file (`doc-writer/skills/setup/defaults/odoc.md`) is already comprehensive -- it covers .mld structure, dune wiring, cross-references, code blocks, quality checklist, multi-package docs, and file naming rules. The doc-author does NOT need a copy of this guidance in its prompt. Instead, the author reads `.doc-writer/odoc.md` at runtime (already does this via "Read the doc-system guidance file" in Step 1). What Phase 17 adds is: (a) conditional logic to write .mld files to `doc/` instead of .md files to `docs_root`, (b) a dune registration step after each .mld write, (c) .mli enrichment proposals as a new capability the author has never done before, and (d) a mechanism for internal notes that works without HTML comments.

The three novel aspects that require careful design are: (1) the internal notes problem -- .mld files do not support HTML comments, so author-to-editor notes must go to an external `.doc-writer/author-notes.md` file; (2) dune registration -- every .mld file must be added to `(mld_files ...)` in `doc/dune` or it silently disappears from generated docs; (3) .mli enrichment proposals -- the doc-author has never proposed source file modifications before, and the output format for these proposals is unresolved (STATE.md flags this as a blocker to resolve during planning).

**Primary recommendation:** Implement as two plans. Plan 17-01 covers doc-author .mld output mode (conditional write workflow, dune registration, external author-notes file) and doc-editor .mld discovery + odoc syntax handling. Plan 17-02 covers .mli enrichment proposals in doc-author and any remaining editor/tester adjustments.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| OCML-02 | Doc-author writes .mld files with odoc syntax when doc_system is odoc | Conditional branch in Phase 2 write workflow: when `doc_system == "odoc"`, write .mld to `doc/` using odoc markup; guidance file already documents all syntax; internal notes go to external `.doc-writer/author-notes.md` |
| OCML-03 | Doc-author registers .mld pages in doc/dune during write pass | After writing each .mld file, read `doc/dune`, parse `(mld_files ...)`, append new page name (without .mld extension), write updated dune file |
| OCML-04 | Doc-author proposes doc comment enrichment for undocumented public values in .mli files | New workflow step after .mld writing: scan .mli files for `val`/`type`/`module`/`exception` without preceding `(** ... *)`, propose complete doc comment blocks written to `.doc-writer/mli-enrichment.md` |
| OCML-05 | Editor discovers .mld files and applies quality passes using odoc syntax rules | Conditional glob in Step 2 (discover files): `*.mld` in `doc/` when `doc_system == "odoc"`; Pass 2 uses `{1 ...}` heading syntax; Pass 4 uses `{!Module.value}` cross-reference syntax; post-processing reads external author-notes file instead of stripping HTML comments |
</phase_requirements>

## Standard Stack

### Core

No new runtime dependencies. Phase 17 modifies existing markdown agent prompts. There are no npm/pip/opam packages to install for the plugin itself.

### Files Modified by This Phase

```
doc-writer/
  agents/
    doc-author.md              # Conditional .mld write workflow, dune registration, .mli enrichment, external author-notes
    doc-editor.md              # .mld file discovery, odoc syntax in Pass 2/4, external author-notes reading
    doc-user-tester.md         # .mld file discovery in Step 3
  skills/
    write/
      SKILL.md                 # Mode detection: glob *.mld when doc_system is odoc
```

### What NOT to Add

| Do Not Add | Why |
|------------|-----|
| odoc syntax reference in doc-author.md | The odoc guidance file already covers this comprehensively; author reads it at runtime via Step 1 |
| .mld template files per diataxis type | The diataxis references provide structure; format translation is handled by the guidance file |
| HTML comments in .mld files | Not valid odoc syntax; use external author-notes file instead |
| Direct .mli file writing by doc-author | Author proposes enrichments as a separate document; user applies them manually |
| Modifications to odoc.md guidance file | Already comprehensive; no changes needed |
| Modifications to scan-exports.sh | OCaml case already added in Phase 14 (OCML-01) |

## Architecture Patterns

### Pattern 1: Conditional Write Workflow in Doc-Author Phase 2

**What:** When `doc_system == "odoc"`, the doc-author's Phase 2 writing workflow branches to produce .mld output instead of Markdown. This is a format translation layer -- the diataxis structure (tutorials have Prerequisites/Steps/Verification, how-to guides have Goal/Steps/Result, etc.) stays the same, but the markup syntax changes.

**Where in doc-author.md:** In Phase 2 (Write), after "### General Writing Workflow", add a new conditional section. This parallels how the author already reads the guidance file for doc-system-specific formatting (Step 4 of the General Writing Workflow). The change makes the branch explicit for odoc output because the differences go beyond formatting -- file location, file extension, and registration all change.

**Branching logic:**

```
IF doc_system == "odoc":
  output_dir = "doc/" (not paths.docs_root)
  file_ext = ".mld" (not ".md" or ".rst")
  markup = odoc syntax from guidance file
  internal_notes = write to .doc-writer/author-notes.md (not HTML comments in page)
  post_write = register page in doc/dune (mld_files stanza)
  file_naming = underscores only, no hyphens
ELSE:
  existing behavior unchanged
```

**What changes per page:**
1. File path: `doc/getting_started.mld` instead of `docs/getting-started.md`
2. Heading syntax: `{0 Title}` / `{1 Section}` instead of `# Title` / `## Section`
3. Code blocks: `{[ ocaml_code ]}` and `{v shell_command v}` instead of fenced markdown blocks
4. Cross-references: `{!Module.value}` and `{!page-name}` instead of markdown links
5. Internal notes: appended to `.doc-writer/author-notes.md` under a page heading instead of HTML comment in the page
6. Post-write: update `doc/dune` mld_files list

**What does NOT change:**
- Phase 1 (Plan) remains identical -- the inventory proposes pages regardless of output format
- Diataxis reference files are still loaded and followed
- Quality rules still apply
- Persona calibration still applies
- The guidance file is still read at runtime for syntax details

### Pattern 2: External Author-Notes File

**What:** Since .mld files do not support HTML comments, the doc-author writes internal notes to a separate `.doc-writer/author-notes.md` file instead of embedding them in the page. This file is organized by page name with the same structured sections as the current HTML comment format.

**Format:**

```markdown
# Author Notes for Editor

## doc/index.mld

### Page Classification
- Type: tutorial
- Reference used: skills/diataxis/references/tutorials.md

### Source References
- lib/my_library/core.mli (lines 10-45)

### Accuracy Notes
- Claims `parse` handles all RFC 3339 formats -- verify against source

### Known Limitations
- No async API mentioned; library is sync-only

### API Reference Links Used
- {!My_library.parse}
- {!My_library.Config.t}

---

## doc/getting_started.mld

### Page Classification
- Type: how-to
...
```

**Why this approach:**
- Option 1 (skip notes): Not viable -- the editor needs source references and accuracy claims for quality passes
- Option 2 (odoc comment syntax): Not viable -- there is no invisible comment mechanism in .mld. All content renders.
- Option 3 (external file): Best option -- avoids odoc syntax issues entirely; keeps the mechanism consistent; only the storage location changes

**Editor change:** In Pre-Processing Step 3 (Extract Author's Internal Notes), when `doc_system == "odoc"`, read `.doc-writer/author-notes.md` instead of parsing HTML comments from doc files. In Post-Processing (Strip Internal HTML Comments), skip the stripping step for odoc -- there are no HTML comments to strip.

### Pattern 3: Dune Registration After Each .mld Write

**What:** After writing each .mld file, the doc-author reads `doc/dune`, parses the `(mld_files ...)` list, appends the new page name (without the .mld extension), and writes the updated dune file. This is critical because unregistered .mld files silently do not appear in generated docs.

**Implementation:**

1. Read `doc/dune` using the Read tool
2. Find the `(mld_files ...)` sexp within the `(documentation ...)` stanza
3. Check if the new page name is already in the list (avoid duplicates)
4. If not present, append the page name to the list
5. Write the updated `doc/dune` using the Write tool

**Example -- before:**
```scheme
(documentation
 (package my_library)
 (mld_files index))
```

**Example -- after writing getting_started.mld:**
```scheme
(documentation
 (package my_library)
 (mld_files index getting_started))
```

**Multi-package projects:** Each package has its own `doc/{package}/dune` file. The author must update the correct dune file based on which package the page belongs to. The guidance file already documents this directory layout.

**Self-verification:** Add a checklist item to the Phase 2 odoc checklist: "Every .mld file written in this pass is registered in the corresponding doc/dune (mld_files) stanza."

### Pattern 4: .mli Enrichment Proposals

**What:** The doc-author scans .mli files for undocumented public values (val, type, module, exception declarations without preceding `(** ... *)` doc comments) and proposes doc comment enrichments. This is a NEW capability -- the author has never proposed source file modifications before.

**Scope control:** The odoc Q&A (Question 2: Author scope) already asks: ".mld pages + .mli doc comment improvements (Recommended)" vs ".mld pages only." The config stores this choice. Phase 17 implements the first option.

**Detection algorithm:**
1. Use scan-exports.sh output (already available from gap detection in write SKILL.md Step 1)
2. For each exported symbol in .mli files, check if the line above it contains `*)` (end of a doc comment)
3. Symbols without a preceding doc comment are candidates for enrichment

**Output format decision (resolves STATE.md blocker):**

Recommendation: Write proposals to `.doc-writer/mli-enrichment.md` as complete doc comment blocks with file path and line context. The user reviews and applies manually. This matches the project's principle of never auto-committing generated content.

```markdown
# .mli Doc Comment Enrichment Proposals

**Generated:** {date}
**Source files scanned:** {count}
**Undocumented symbols found:** {count}

## lib/my_library/core.mli

### `val parse : string -> t` (line 15)

**Current:** No doc comment

**Proposed:**
```ocaml
(** Parse a duration string into a {!type:t} value.

    Accepts formats like ["3h30m"], ["45s"], or ["1d12h"].

    {[
      let d = Core.parse "2h30m"
      (* val d : t *)
    ]}

    @param s Duration string
    @return Parsed duration value
    @raise Invalid_argument if format is unrecognized *)
```

### `type t` (line 5)

**Current:** No doc comment

**Proposed:**
```ocaml
(** Opaque duration type.

    Create values with {!val:parse} or {!val:of_seconds}. *)
```

---

## lib/my_library/config.mli

...
```

**Why NOT direct .mli writes:**
- The project convention is to never auto-commit generated content (user reviews and commits)
- .mli files are source code, not documentation output -- modifying them is higher risk than writing .mld files
- The user may want to adjust doc comments to match their style or add details the author cannot infer
- A proposals file lets the user cherry-pick which enrichments to apply

**Author codebase scan for enrichment:** During Phase 1 (Scan), the author already reads .mli files. The enrichment scan extends this: for each undocumented symbol, the author uses its type signature, module context, and any .ml implementation details to write a meaningful doc comment (not just a stub). The comment follows odoc.md guidance: summary line, example block, @param/@return/@raise tags.

### Pattern 5: Editor .mld File Discovery and Odoc Syntax Handling

**What:** The doc-editor needs three conditional changes when `doc_system == "odoc"`:

1. **File discovery (Step 2):** Glob `doc/**/*.mld` instead of `{paths.docs_root}/**/*.md`. Also scan .mli files in `paths.source_root` for doc comment quality if the scope includes .mli enrichment.

2. **Pass 2 (Diataxis Type Integrity):** Recognize odoc heading syntax `{1 Section}` instead of markdown `## Section`. The structural analysis is the same (detect type blur based on content, not syntax), but the editor needs to parse odoc structure correctly.

3. **Pass 4 (Cross-Reference Linking):** Verify odoc cross-references `{!Module.value}` instead of markdown links `[symbol](path)`. Check that referenced modules and values exist in the scanned .mli files.

4. **Pre-Processing Step 3 (Extract Author Notes):** Read from `.doc-writer/author-notes.md` instead of parsing HTML comments.

5. **Post-Processing (Strip Internal Notes):** Skip the HTML comment stripping step -- there are no HTML comments in .mld files. The author-notes.md file is a separate file that persists (not embedded in doc pages).

**Pass 1 (Terminology):** No change needed -- terminology checking works on prose text regardless of markup format.

**Pass 3 (Humanizer):** No change needed -- humanizer checks work on prose text regardless of markup format. The existing rule "NEVER modify content inside fenced code blocks or inline code spans" translates to: never modify content inside `{[ ... ]}`, `{v ... v}`, or `[inline_code]` blocks for odoc.

### Pattern 6: User Tester .mld Discovery

**What:** The doc-user-tester's Step 3 (Discover Documentation Files) currently globs for `.md` files. When `doc_system == "odoc"`, it must also glob for `.mld` files in `doc/` and include `README.md` from the project root.

**Change in doc-user-tester.md Step 3:**

```
When doc_system is "odoc":
  Glob doc/**/*.mld for documentation pages
  Also include README.md from project root if it exists
  The "docs homepage" fallback chain becomes:
    1. README.md in project root
    2. doc/index.mld
    3. First .mld file alphabetically in doc/
```

The tester reads .mld source directly (it can interpret odoc markup) since it cannot run `dune build @doc`.

### Pattern 7: Write SKILL.md Mode Detection for .mld

**What:** The write SKILL.md Step 0 (Mode Detection) checks for existing docs by globbing `.md` files in `paths.docs_root`. For odoc projects, it must check for `.mld` files in `doc/` instead.

**Change:**

```
When doc_system is "odoc":
  Scan doc/**/*.mld for existing documentation pages
  Filter out bare scaffold pages (an index.mld with only {0 ...} and TODO placeholders)
  Count remaining substantive .mld pages
```

### Anti-Patterns to Avoid

- **Do NOT duplicate odoc syntax from the guidance file into doc-author.md:** The guidance file is comprehensive and already loaded at runtime. The author prompt should say "follow the odoc syntax from the guidance file" not repeat the syntax.
- **Do NOT write .md files for odoc projects:** The whole point of this phase is to produce native .mld files. No markdown fallback.
- **Do NOT embed HTML comments in .mld files:** They are not valid odoc syntax. Use the external author-notes file.
- **Do NOT auto-write .mli files:** Propose enrichments in a separate document. The user reviews and applies.
- **Do NOT skip dune registration:** Unregistered .mld files silently vanish from generated docs. This is the #1 odoc pitfall per the guidance file.
- **Do NOT use hyphens in .mld filenames:** odoc parses hyphens as reference qualifier separators. Underscores only. The guidance file documents this in detail.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| odoc syntax documentation | Inline syntax reference in doc-author prompt | Existing `odoc.md` guidance file loaded at runtime | Already comprehensive; 400 lines covering all syntax, patterns, and pitfalls |
| .mld file structure templates | Per-type .mld template files | Diataxis references + format translation via guidance file | The diataxis references provide structure; the guidance file provides syntax translation |
| Dune sexp parser | Custom parser for (mld_files ...) | Simple Read + string manipulation + Write | The sexp is regular and small; a parser is overkill |
| Undocumented symbol detection | Custom OCaml AST parser | grep for `val`/`type`/`module`/`exception` + check for preceding `(** ... *)` | Line-oriented detection is sufficient; matches scan-exports pattern |

## Common Pitfalls

### Pitfall 1: Author Writes .md Instead of .mld for Odoc Projects

**What goes wrong:** The doc-author follows its default workflow and writes `docs/getting-started.md` instead of `doc/getting_started.mld`.
**Why it happens:** The existing Phase 2 workflow assumes markdown output. Without an explicit conditional branch, the author defaults to .md.
**How to avoid:** Add an explicit conditional at the start of Phase 2 write workflow that sets `output_format`, `output_dir`, `file_ext`, and `file_naming_rules` based on `doc_system`. The conditional must be early and prominent -- not buried in a footnote.
**Warning signs:** .md files appearing in docs_root for an odoc project; no .mld files in doc/.

### Pitfall 2: Unregistered .mld Files

**What goes wrong:** The author writes getting_started.mld but does not add `getting_started` to `(mld_files ...)` in doc/dune. The page silently does not appear in generated docs.
**Why it happens:** The dune registration is a separate step that is easy to forget -- there is no analog in the Markdown/RST workflows.
**How to avoid:** Make dune registration an explicit step in the write workflow that runs AFTER each .mld write. Add it to the Phase 2 self-verification checklist.
**Warning signs:** .mld files in doc/ that are not in the mld_files list; pages missing from `dune build @doc` output.

### Pitfall 3: Hyphens in .mld Filenames

**What goes wrong:** The author creates `getting-started.mld` following standard doc naming conventions. odoc's `{!page-getting-started}` reference parses this as qualifier `page-getting` + target `-started`, breaking the cross-reference.
**Why it happens:** Markdown and RST use hyphens in filenames (standard URL convention). odoc uses underscores because hyphens are semantic in its reference syntax.
**How to avoid:** The file naming rule must be part of the conditional branch at the start of the odoc write workflow. The guidance file already documents this extensively. The self-verification checklist should include "No .mld filenames contain hyphens."
**Warning signs:** Broken `{!page-...}` references; odoc build warnings about unknown references.

### Pitfall 4: HTML Comments in .mld Files

**What goes wrong:** The author writes internal notes as HTML comments (`<!-- INTERNAL NOTES -->`) in .mld files. odoc does not parse HTML comments -- the literal text appears in generated docs.
**Why it happens:** The existing internal notes mechanism uses HTML comments. Without explicit guidance, the author applies the same pattern.
**How to avoid:** The odoc write workflow explicitly directs notes to `.doc-writer/author-notes.md`. The self-verification checklist includes "No HTML comments in .mld files."
**Warning signs:** `<!--` appearing in .mld file content.

### Pitfall 5: .mli Enrichment Proposals Applied Without Review

**What goes wrong:** The doc-author directly modifies .mli source files instead of writing proposals to a review document.
**Why it happens:** The natural action after identifying undocumented symbols is to fix them immediately.
**How to avoid:** The .mli enrichment workflow must be framed as "propose" not "write." The author writes proposals to `.doc-writer/mli-enrichment.md`. The write SKILL.md summary tells the user to review and apply proposals manually.
**Warning signs:** doc-author using Write tool on .mli files in paths.source_root.

### Pitfall 6: Editor Fails on .mld Syntax

**What goes wrong:** The editor's Pass 2 looks for `## Heading` markdown syntax to parse page structure in .mld files. It finds none and reports all pages as structureless.
**Why it happens:** The editor's syntax parsing assumes markdown heading format.
**How to avoid:** Add a conditional in the editor that switches syntax recognition based on `doc_system`. For odoc, headings are `{1 ...}`, code blocks are `{[ ... ]}`, cross-references are `{!...}`, and inline code is `[...]`.
**Warning signs:** Editor reporting no headings found in .mld files; Pass 2 failing to detect type blur.

## Code Examples

### Doc-Author Conditional Write (for doc-author.md Phase 2)

```markdown
### Odoc Output Mode

When `doc_system` is `odoc`, the writing workflow changes:

**File output:**
- Write .mld files to `doc/` directory (not `paths.docs_root`)
- File extension: `.mld` (not `.md` or `.rst`)
- File naming: underscores ONLY, never hyphens (e.g., `getting_started.mld`, not `getting-started.mld`)
- Page title: `{0 Package_name - Brief description}` (only in .mld files)

**Markup format:**
- Read `.doc-writer/odoc.md` for the complete odoc syntax reference
- Use `{1 Section}`, `{2 Subsection}`, `{3 Subsubsection}` for headings
- Use `{[ ocaml_code ]}` for OCaml code blocks
- Use `{v shell_or_text v}` for verbatim/non-OCaml blocks
- Use `{!Module.value}` for API cross-references
- Use `{!page-page_name}` for page cross-references

**Dune registration (mandatory after each .mld write):**
1. Read `doc/dune`
2. Find the `(mld_files ...)` list
3. If the new page name is not already listed, append it
4. Write the updated `doc/dune`

**Internal notes:**
- Do NOT write HTML comments in .mld files (not valid odoc syntax)
- Write all internal notes to `.doc-writer/author-notes.md` instead
- Organize by page name with the same sections as markdown internal notes

**README.md and MAINTAINER.md:**
- These are still written as markdown to the project root (unchanged)
- They are NOT converted to .mld format
```

### Dune Registration Example

```scheme
;; Before: doc/dune
(documentation
 (package my_library)
 (mld_files index))

;; After writing getting_started.mld and how_it_works.mld:
(documentation
 (package my_library)
 (mld_files index getting_started how_it_works))
```

### .mli Enrichment Proposal Format

```markdown
# .mli Doc Comment Enrichment Proposals

**Generated:** 2026-03-22
**Source files scanned:** 4
**Undocumented public symbols:** 7

## lib/my_library/core.mli

### `val parse : string -> t` (line 15)

**Current:** No doc comment

**Proposed:**
\```ocaml
(** Parse a duration string into a {!type:t} value.

    Accepts formats like ["3h30m"], ["45s"], or ["1d12h"].
    Components can appear in any order.

    {[
      let d = Core.parse "2h30m"
      (* val d : t *)
    ]}

    @param s Duration string (e.g., "3h", "45m10s")
    @return Parsed duration value
    @raise Invalid_argument if the format is unrecognized *)
\```

---
```

### Editor .mld Discovery (for doc-editor.md Step 2)

```markdown
### Step 2: Discover Documentation Files

When `doc_system` is `odoc`:
- Use Glob to find all `.mld` files in `doc/` (pattern: `doc/**/*.mld`)
- Also check for `README.md` and `MAINTAINER.md` in the project root
- Do NOT glob for `.md` files in `paths.docs_root` -- odoc docs live in `doc/`

When `doc_system` is NOT `odoc`:
- Use Glob to find all `.md` files in `paths.docs_root` (existing behavior)
```

### Editor Odoc Syntax Awareness (for doc-editor.md Pass 2 and Pass 4)

```markdown
**When doc_system is odoc, adjust syntax recognition:**

Pass 2 (Diataxis Type Integrity):
- Headings: `{1 Section}`, `{2 Subsection}` (not `## Section`, `### Subsection`)
- Code blocks: `{[ ... ]}` and `{v ... v}` (not fenced backtick blocks)
- Bold: `{b text}` (not `**text**`)
- Lists: `{ul {- item}}` or abbreviated `- item` (same as markdown)

Pass 4 (Cross-Reference Linking):
- Cross-refs: `{!Module.value}` (not `[text](url)`)
- Page refs: `{!page-name}` (not markdown links)
- External URLs: `{{:https://example.com} text}` (not `[text](url)`)
- Do NOT modify content inside `{[ ... ]}`, `{v ... v}`, or `[inline_code]` blocks

Pre-Processing Step 3 (Extract Author Notes):
- Read `.doc-writer/author-notes.md` instead of parsing HTML comments
- Parse sections organized by page name

Post-Processing (Strip Internal Notes):
- Skip entirely for odoc -- no HTML comments to strip
- The author-notes.md file persists as a separate file
```

### User Tester .mld Discovery (for doc-user-tester.md Step 3)

```markdown
### Step 3: Discover Documentation Files

When `doc_system` is `odoc`:
- Use Glob to find all `.mld` files in `doc/` (pattern: `doc/**/*.mld`)
- Also check for `README.md` in the project root

When `doc_system` is NOT `odoc`:
- Existing behavior: Glob for `.md` files in `paths.docs_root`

Docs homepage fallback chain for odoc:
1. `README.md` in the project root
2. `doc/index.mld`
3. First `.mld` file alphabetically in `doc/`
```

## State of the Art

| Old Approach (current) | New Approach (Phase 17) | Impact |
|------------------------|-------------------------|--------|
| Doc-author writes .md for ALL doc systems | Doc-author writes .mld when doc_system is odoc | Native odoc output; no Markdown-to-odoc conversion needed by user |
| Internal notes as HTML comments in page files | External author-notes.md for odoc (HTML comments for MD/RST unchanged) | Works with .mld syntax; keeps editor mechanism functional |
| No dune registration awareness | Doc-author updates doc/dune mld_files after each .mld write | Pages actually appear in generated docs |
| No .mli enrichment | Doc-author proposes doc comments for undocumented symbols | Better API reference quality without requiring user to write all comments |
| Editor globs only .md files | Editor globs .mld files when doc_system is odoc | Quality passes work on native odoc files |
| Editor parses markdown syntax | Editor conditionally parses odoc syntax ({1...}, {!...}) | Accurate type integrity and cross-reference checking |

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | grep-based content verification + manual review |
| Config file | none |
| Quick run command | `grep -c "odoc\|\.mld\|mld_files\|author-notes\|mli-enrichment" doc-writer/agents/doc-author.md doc-writer/agents/doc-editor.md doc-writer/agents/doc-user-tester.md doc-writer/skills/write/SKILL.md` |
| Full suite command | Manual: verify each success criterion against modified files |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| OCML-02 | Doc-author writes .mld when doc_system is odoc | smoke | `grep -c "doc_system.*odoc\|\.mld\|odoc.*output" doc-writer/agents/doc-author.md` | Wave 0 |
| OCML-02 | Doc-author uses odoc syntax (headings, code blocks, cross-refs) | smoke | `grep -c "{0.*Title}\|{1.*Section}\|{\\[.*\\]}\|{!Module" doc-writer/agents/doc-author.md` | Wave 0 |
| OCML-02 | Internal notes go to external file for odoc | smoke | `grep "author-notes" doc-writer/agents/doc-author.md` | Wave 0 |
| OCML-03 | Doc-author registers .mld in doc/dune | smoke | `grep -c "mld_files\|doc/dune\|dune registration" doc-writer/agents/doc-author.md` | Wave 0 |
| OCML-04 | Doc-author proposes .mli enrichment | smoke | `grep -c "mli.*enrichment\|undocumented.*public\|doc comment" doc-writer/agents/doc-author.md` | Wave 0 |
| OCML-05 | Editor discovers .mld files | smoke | `grep -c "\.mld\|doc/\*\*" doc-writer/agents/doc-editor.md` | Wave 0 |
| OCML-05 | Editor uses odoc syntax rules | smoke | `grep -c "{1.*heading\|odoc.*syntax\|{!.*cross-ref" doc-writer/agents/doc-editor.md` | Wave 0 |
| OCML-05 | Editor reads external author-notes | smoke | `grep "author-notes" doc-writer/agents/doc-editor.md` | Wave 0 |

### Sampling Rate

- **Per task commit:** grep smoke tests on modified files
- **Per wave merge:** Full grep suite across all modified files
- **Phase gate:** All grep checks pass + manual review of conditional logic and odoc syntax examples

### Wave 0 Gaps

None -- all validation is grep-based content verification on modified files. No test framework, config files, or fixtures needed.

## Open Questions

1. **Should the .mli enrichment scan run during Phase 1 (plan) or Phase 2 (write)?**
   - What we know: Phase 1 already scans the codebase including .mli files. Phase 2 writes content. The enrichment proposals are a write-time output.
   - What's unclear: Should undocumented symbols appear in the page inventory, or is the enrichment file a separate output alongside the written pages?
   - Recommendation: Run the enrichment scan during Phase 2, AFTER all .mld pages are written. The enrichment proposals are a separate deliverable, not part of the page inventory. The page inventory is about documentation pages; .mli enrichment is about source code quality. Present the enrichment file path in the pipeline summary report.

2. **How does the author determine which .mli files to scan for enrichment?**
   - What we know: scan-exports.sh already scans all .mli files in source_root. The author reads .mli files during Phase 1 codebase scan.
   - What's unclear: Should it scan ALL .mli files or only the ones referenced in the page inventory?
   - Recommendation: Scan all .mli files in `paths.source_root`. The goal is to improve API reference quality across the entire library, not just the pages the author wrote. This aligns with the odoc Q&A scope option: ".mld pages + .mli doc comment improvements."

3. **What about multi-package projects?**
   - What we know: The odoc guidance file documents multi-package directory layout with separate doc/{package}/dune files. The scaffold already has secondary_dune.sexp and secondary_index.mld templates.
   - What's unclear: Does the author need to determine which package each page belongs to for dune registration?
   - Recommendation: For Phase 17, focus on single-package projects. The dune registration step reads the primary `doc/dune`. Multi-package awareness can be added in a future phase if needed. The odoc Q&A (Question 1) already captures whether the project is single-library or multi-library, so the data is available.

4. **Should the editor verify dune registration?**
   - What we know: The editor does quality passes on documentation. Dune registration is a build system concern, not a content quality concern.
   - What's unclear: Is missing dune registration an editor responsibility?
   - Recommendation: No -- the author's self-verification checklist should catch this. The editor focuses on content quality (terminology, type integrity, humanizer, cross-references). Add a note to the editor that unregistered .mld files will not appear in generated docs, but do not add a registration verification pass.

## Sources

### Primary (HIGH confidence)
- Existing codebase: `doc-writer/agents/doc-author.md` -- current Phase 2 write workflow, internal notes format, self-verification checklists
- Existing codebase: `doc-writer/agents/doc-editor.md` -- current file discovery (Step 2), Pass 2/4 syntax, pre/post-processing
- Existing codebase: `doc-writer/agents/doc-user-tester.md` -- current file discovery (Step 3), homepage fallback chain
- Existing codebase: `doc-writer/skills/write/SKILL.md` -- current mode detection (Step 0), gap detection (Step 1)
- Existing codebase: `doc-writer/skills/setup/defaults/odoc.md` -- comprehensive odoc syntax reference, dune wiring, file naming rules, cross-references, quality checklist
- Existing codebase: `doc-writer/skills/setup/defaults/odoc.qa.md` -- Q2 "Author scope" captures .mli enrichment preference
- Existing codebase: `doc-writer/skills/setup/defaults/scaffolds/odoc/` -- scaffold templates for doc/dune and index.mld
- [odoc for authors](https://ocaml.github.io/odoc/odoc/odoc_for_authors.html) -- confirmed .mld syntax, heading levels, code blocks, cross-references, NO HTML comment support
- [OCaml modules docs](https://ocaml.org/docs/modules) -- .mli file structure, doc comment format `(** ... *)`
- `.planning/research/ARCHITECTURE.md` -- Internal Notes Problem analysis with three options evaluated; recommendation for external notes file
- `.planning/STATE.md` -- ".mli enrichment output format unresolved -- resolve during Phase 17 planning"

### Secondary (MEDIUM confidence)
- `.planning/research/SUMMARY.md` -- Phase ordering rationale, risk assessment for odoc feature
- `.planning/phases/14-foundations/14-RESEARCH.md` -- OCaml scan-exports pattern verification

### Tertiary (LOW confidence)
- None -- all findings derived from reading the actual codebase, official odoc docs, and project architecture research

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies; all modifications target existing files with clear extension points
- Architecture: HIGH -- every pattern is either established (conditional branches exist for doc_system in guidance loading) or directly recommended by the project's own architecture research (external author-notes file)
- Pitfalls: HIGH -- all pitfalls derived from official odoc documentation (hyphen filenames, unregistered .mld files, no HTML comments) and codebase analysis (editor syntax assumptions)
- .mli enrichment: MEDIUM-HIGH -- the proposal format is a design decision (not externally constrained), but the recommendation follows the project's established pattern of never auto-committing generated content

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable domain; odoc syntax is mature and stable; no fast-moving external dependencies)
