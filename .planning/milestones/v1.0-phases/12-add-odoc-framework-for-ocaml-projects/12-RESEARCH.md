# Phase 12: Add Odoc Framework for OCaml Projects - Research

**Researched:** 2026-03-19
**Domain:** OCaml documentation (odoc) integrated as a built-in doc-writer framework
**Confidence:** HIGH

## Summary

Phase 12 adds odoc as a first-class built-in documentation framework in the doc-writer plugin, on equal footing with mkdocs-material and sphinx-shibuya. The deliverables are: `odoc.qa.md` (Q&A question set with follow-on sub-topic questions), `odoc.md` (comprehensive guidance file absorbing all content from the standalone `ocaml-odoc-guide` skill), `scaffolds/odoc/` (directory-based scaffold with dune stanzas and .mld stubs), and a SKILL.md update to list `odoc` as a selectable doc system.

The existing patterns from Phase 10 and Phase 11 are well-established and directly replicable. The main novel element is the Q3 follow-on sub-topic questions, which require the setup skill to dynamically scan project source (module names, .mli signatures, existing .mld files) at question-presentation time -- a new behavior not present in other framework Q&As. The scaffold is also structurally different: odoc projects need multiple files (doc/dune + doc/index.mld + optional per-package stubs) rather than a single config file, requiring either a directory scaffold or a multi-section template.

**Primary recommendation:** Follow the sphinx-shibuya pattern exactly for file format and structure, but use a directory-based scaffold (`scaffolds/odoc/`) containing separate template files for doc/dune and doc/index.mld, since odoc scaffolding produces multiple output files in different locations.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Scaffold configures existing dune files (adds `(documentation ...)` stanzas) -- projects already have dune files, they just need the doc stanza added
- Scaffold also creates `doc/index.mld` and guide page stubs (not just dune plumbing)
- For multi-library projects (detected via package count in dune-project): generate per-package doc stanzas + a minimal `index.mld` stub for each additional package; primary package gets full scaffold treatment
- Template variables: `{package_name}`, `{library_name}`, `{synopsis}` -- inferred from `dune-project` (package name, synopsis) and `lib/*/dune` (library name)
- `odoc.md` is comprehensive -- absorbs all content from the `ocaml-odoc-guide` skill: pitfalls, cross-reference syntax, .mli comment style, .mld file structure, file naming rules, dune wiring, quality checklist
- The standalone `ocaml-odoc-guide` skill becomes redundant after this phase (do not maintain both)
- Do NOT duplicate diataxis/humanizer invocation requirements in `odoc.md` -- the doc-writer agent prompts already mandate these; odoc.md focuses on OCaml/odoc-specific preferences
- Q1 (Structure): Single-library vs multi-library confirmation. Auto-detected from dune-project package count. Presented as confirmation, not discovery.
- Q2 (Scope): Author scope. `.mld pages + .mli doc comment improvements` is the Recommended option. Option: `.mld pages only` for users who want to keep .mli untouched.
- Q3 (Guides): Which guide page types to create -- multiSelect: Getting started / Tutorial, How-to guides, Explanation pages. Each selected type triggers a follow-on sub-topic question.
- Q3 follow-on sub-topic questions: Research-guided suggestions -- setup skill scans the project's module names, exported .mli signatures, and existing .mld files to propose relevant sub-topics for each selected guide type. The `.qa.md` defines the question structure; options are generated dynamically at setup time (not pre-defined static lists).
- .mli doc comments: Add comments for public values that have none. Preserve existing comments. Do not rewrite what the maintainer already wrote unless clearly incorrect.
- dune registration: When creating a new `.mld` file, the author must also add it to the `(mld_files ...)` list in the corresponding `doc/dune`. New files that aren't registered will silently not appear in the generated docs.
- Build validation: Author runs `dune build @doc` as a final check after writing.

### Claude's Discretion
- Exact prose wording and examples in `odoc.md` sections
- Whether to scaffold a `doc/dune` file or only a `lib/*/dune` snippet for the documentation stanza, depending on project layout
- Specific `(mld_files ...)` entries in stub scaffolds (generic placeholder names like `getting_started`, `how_to`, `concepts` until Q3 sub-topics are confirmed)
- Format of the research-guided sub-topic suggestions (freeform list, multiSelect, or plain-text prompt)

### Deferred Ideas (OUT OF SCOPE)
- Apply follow-on sub-topic Q&A pattern to mkdocs-material and sphinx-shibuya -- currently those frameworks have flat Q3 feature lists. Worth adding in a future polish phase.
- Delete/deprecate the `ocaml-odoc-guide` skill after this phase ships -- that's a separate operation outside the doc-writer plugin scope.
</user_constraints>

## Standard Stack

### Core
| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| odoc | 2.x (dune-compatible) | Documentation generator for OCaml | Only maintained doc tool for OCaml; 3.x exists but dune integration not yet rewritten |
| dune | 3.x | Build system | Standard OCaml build system; `dune build @doc` is the canonical doc build command |

### Supporting
| Component | Purpose | When to Use |
|-----------|---------|-------------|
| `(documentation ...)` stanza | Registers .mld files with dune | Every package that has documentation pages |
| `(odoc :with-doc)` dep | Ensures odoc available during doc builds | Listed in dune-project package deps |
| `dune-project` | Package metadata source | Scaffold reads package_name, synopsis, package count from here |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| odoc 2.x | odoc 3.x | odoc 3 has new features (media, cross-package config, tables) but dune rules not yet rewritten for it; projects using `dune build @doc` need odoc 2.x |
| Directory scaffold | Single template file | odoc needs multiple output files (doc/dune + doc/index.mld + per-package stubs); a single file cannot represent this |

**Note on odoc versions:** odoc 3.0.0 and 3.1.0 exist on opam but dune has not yet updated its rules to support odoc 3's new CLI and incremental build capabilities. The guidance file should document both odoc 2.x syntax (which works with `dune build @doc` today) and note odoc 3.x additions (tables, media, language-specific code blocks) as forward-looking features. The scaffold and Q&A should target odoc 2.x since that is what `dune build @doc` actually invokes.

## Architecture Patterns

### Deliverable File Structure
```
doc-writer/skills/setup/defaults/
  odoc.qa.md              # Q&A question set (3 questions + follow-on sub-topics)
  odoc.md                 # Comprehensive guidance (absorbs ocaml-odoc-guide)
  scaffolds/
    odoc/                 # Directory scaffold (new pattern)
      doc_dune.sexp       # Template for doc/dune
      index.mld           # Template for doc/index.mld
      secondary_dune.sexp # Template for secondary package doc/*/dune
      secondary_index.mld # Template for secondary package doc/*/index.mld
```

### Pattern 1: Q&A File Structure (replicate sphinx-shibuya.qa.md)
**What:** A .qa.md file with Detection section, 3 questions, and follow-on sub-topic mechanism
**When to use:** Always -- this is the standard format for framework Q&A files

The Detection section for odoc:
```markdown
## Detection

Config file: dune-project
Features to detect:
- (documentation ...) stanza in doc/dune or any dune file
- Number of (package ...) blocks in dune-project (single vs multi-library)
- Existing .mld files in doc/ directory
- (odoc :with-doc) in package deps
```

Q1, Q2 follow standard AskUserQuestion format. Q3 introduces a new pattern:

```markdown
## Question 3: Guide pages

- header: "Guides"
- question: "Which guide page types should the documentation include?"
- multiSelect: true
- detect_context: "Detected: {existing .mld files}"
- options:
  - { label: "Getting started / Tutorial", description: "..." }
  - { label: "How-to guides", description: "..." }
  - { label: "Explanation pages", description: "..." }
  - { label: "Type something else", description: "..." }
  - { label: "Chat about this", description: "..." }

### Follow-on: Sub-topic questions

For each selected guide type, present a follow-on sub-topic question.
Options are generated dynamically at setup time by scanning:
- Module names from lib/*/dune (public_name field)
- Exported .mli signatures (function/module names)
- Existing .mld files in doc/

The .qa.md defines the question STRUCTURE (header, question template,
scan instructions). Actual option values are computed by the setup skill
at runtime.
```

### Pattern 2: Guidance File Structure (replicate sphinx-shibuya.md)
**What:** A comprehensive .md file with opinionated preferences for odoc documentation
**When to use:** Absorbs ALL content from the `ocaml-odoc-guide` SKILL.md plus reference materials

Sections to include (mapped from the existing skill content):
1. **Intro paragraph** -- "Opinionated preferences for writing documentation with odoc..."
2. **Code Blocks** -- `{[ ... ]}` for OCaml, `{v ... v}` for verbatim, `{@lang[ ... ]}` for other languages
3. **.mld File Structure** -- heading levels, page titles ({0}), section structure
4. **.mli Doc Comments** -- function docs, module docs, @param/@return/@raise tags, examples
5. **Cross-References** -- within-package (`{!page-name}`, `{!Module.value}`), cross-package (HTML URLs), section refs
6. **File Naming** -- underscores only (never hyphens), HTML output filename rules
7. **Dune Wiring** -- `(documentation ...)` stanza, `(mld_files ...)` registration, `(odoc :with-doc)` dep
8. **Multi-Package Documentation** -- primary vs secondary packages, per-package doc/ trees, cross-package HTML URLs
9. **Build Validation** -- `dune build @doc` as final check, common error patterns
10. **Quality Checklist** -- the checklist from the existing skill, adapted to doc-writer context (without diataxis/humanizer mandates)

### Pattern 3: Directory-Based Scaffold
**What:** A scaffold that produces multiple files rather than a single config file
**When to use:** odoc projects need doc/dune + doc/index.mld at minimum

This is a new pattern not present in mkdocs-material (single .yml) or sphinx-shibuya (single .py). The scaffold check in SKILL.md currently looks for `scaffolds/{doc_system}.{ext}` as a single file. For odoc, the check needs to also support `scaffolds/{doc_system}/` as a directory.

**SKILL.md integration impact:** The Step 2b.3 scaffold check currently tries file extensions (.yml, .js, .yaml, .toml, .py). For odoc, it needs an additional check: if none of those file variants match, check if `scaffolds/{doc_system}/` directory exists. If yes, read all template files from the directory and process each one. This is a minor SKILL.md change (one additional check in the scaffold lookup logic).

Template variables for odoc scaffold:
- `{package_name}` -- from dune-project first `(package (name ...))`
- `{library_name}` -- from `lib/*/dune` `(public_name ...)` field
- `{synopsis}` -- from dune-project `(synopsis "...")`

### Pattern 4: SKILL.md Touch Points (3 changes, same as Phase 11)
**What:** Three specific locations in SKILL.md need modification
**When to use:** Adding any new built-in framework

1. **Step 2b option list** (line 253-255): Add `{ label: "odoc", description: "OCaml documentation via odoc" }`
2. **Built-in frameworks list** (line 275): Add `odoc` to `(mkdocs-material, plain-markdown, sphinx-shibuya, odoc)`
3. **Step 2b.3 scaffold check**: Add directory scaffold support (check for `scaffolds/{doc_system}/` directory in addition to single file variants)

### Anti-Patterns to Avoid
- **Duplicating diataxis/humanizer mandates in odoc.md:** The doc-writer agent prompts already enforce these. The guidance file focuses on OCaml/odoc-specific preferences only.
- **Putting `(documentation ...)` stanza in lib/dune:** It only picks up .mld files from its own directory. Always put it in doc/dune.
- **Using hyphens in .mld filenames:** Hyphens break `{!page-...}` references because odoc parses `{!page-getting-started}` as qualifier `page-getting` + target `-started`.
- **Using `{!page-name}` for cross-package links:** This syntax only resolves within the same package. Cross-package links must use relative HTML URLs: `{{:../other_package/page.html} text}`.
- **Hardcoding sub-topic options in .qa.md:** The Q3 follow-on questions must be dynamically generated from project scanning, not static lists. The .qa.md defines the question structure and scan instructions only.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Q&A file format | Custom format | Replicate sphinx-shibuya.qa.md structure exactly | Existing Q&A parser in setup skill already handles this format |
| Guidance file format | Custom sections | Replicate sphinx-shibuya.md section style | Consistent agent consumption pattern across all frameworks |
| Scaffold template variables | Custom substitution | Use `{variable_name}` pattern from existing scaffolds | Setup skill already has template variable substitution logic |
| Cross-reference syntax rules | Simplified subset | Absorb full content from ocaml-odoc-guide skill | The existing skill has battle-tested, accurate pitfall documentation |

**Key insight:** The existing `ocaml-odoc-guide` skill at `/Users/paul/.claude/skills/ocaml-odoc-guide/` contains comprehensive, verified content covering all the odoc-specific patterns, pitfalls, and syntax. The task is primarily content absorption and reformatting, not original research.

## Common Pitfalls

### Pitfall 1: Scaffold assumes single file output
**What goes wrong:** The scaffold check in SKILL.md only looks for single file extensions (.yml, .js, .yaml, .toml, .py). A directory scaffold won't be found.
**Why it happens:** Previous frameworks (mkdocs-material, sphinx-shibuya) each produce a single config file.
**How to avoid:** Add directory scaffold support to SKILL.md's Step 2b.3 -- check for `scaffolds/{doc_system}/` directory after checking single-file variants.
**Warning signs:** "No scaffold template for 'odoc'" message during setup despite scaffold directory existing.

### Pitfall 2: Detection config file confusion
**What goes wrong:** The Detection section says `Config file: dune-project` but the scaffold check looks for this file to decide full-scaffold vs diff mode. Every OCaml project already has `dune-project`, so scaffold would always enter diff-against-defaults mode instead of full scaffold mode.
**Why it happens:** `dune-project` is the project identity file, not a documentation config file. The documentation config is the `(documentation ...)` stanza in `doc/dune`.
**How to avoid:** The Detection section should use `Config file: doc/dune` (or wherever the documentation stanza lives). The scaffold check then correctly enters full scaffold mode when `doc/dune` doesn't exist, and diff mode when it does.
**Warning signs:** Setup never offers to create scaffold files because it always finds `dune-project`.

### Pitfall 3: Multi-library scaffold complexity
**What goes wrong:** Scaffold tries to generate per-package doc directories but doesn't know how many packages exist or what they're named.
**Why it happens:** Package count and names come from dune-project, which must be parsed at scaffold time.
**How to avoid:** Q1 confirms single vs multi-library (auto-detected from dune-project package count). Scaffold templates use `{package_name}` variable. For multi-library, the setup skill loops over detected packages and instantiates the secondary template for each non-primary package.
**Warning signs:** Scaffold generates files for wrong package names or wrong number of packages.

### Pitfall 4: odoc 2.x vs 3.x syntax confusion
**What goes wrong:** Guidance file includes odoc 3.x features (tables with `{t ...}`, media with `{image:...}`, `odoc-config.sexp`) that don't work when built via `dune build @doc` which uses odoc 2.x rules.
**Why it happens:** odoc 3.0+ exists on opam but dune hasn't updated its build rules to support it.
**How to avoid:** Guidance file should document odoc 2.x syntax as the primary path (what `dune build @doc` actually uses). odoc 3.x features can be mentioned in a "Future / odoc 3.x" section as forward-looking notes.
**Warning signs:** `dune build @doc` fails or ignores odoc 3.x-only syntax.

### Pitfall 5: Follow-on sub-topic question is entirely new behavior
**What goes wrong:** The .qa.md file tries to define static sub-topic options, but they need to be generated dynamically from project scanning.
**Why it happens:** mkdocs-material and sphinx-shibuya Q&A files have static option lists. The odoc Q3 follow-on is different.
**How to avoid:** The .qa.md defines the question structure (header, question template, what to scan) but explicitly states that options are runtime-generated. The SKILL.md's Step 2b.5 needs a handler for this "dynamic options" pattern.
**Warning signs:** Generic placeholder sub-topics that don't match the actual project's modules.

## Code Examples

Verified patterns from the reference OCaml projects.

### Single-Library doc/dune (from ocaml-oktree)
```scheme
;; Source: /Users/paul/Documents/Dev/Personal/ocaml-oktree/doc/dune
(documentation
 (package oktree)
 (mld_files index oktree))
```

### Multi-Library Primary doc/dune (from ocaml-spectrum)
```scheme
;; Source: /Users/paul/Documents/Dev/Personal/ocaml-spectrum/doc/dune
(documentation
 (package spectrum)
 (mld_files index getting_started color_quantization custom_palettes))
```

### Multi-Library Secondary doc/*/dune (from ocaml-spectrum)
```scheme
;; Source: /Users/paul/Documents/Dev/Personal/ocaml-spectrum/doc/spectrum_capabilities/dune
(documentation
 (package spectrum_capabilities)
 (mld_files index))
```

### Root dune with (dirs ...) including doc (from ocaml-oktree)
```scheme
;; Source: /Users/paul/Documents/Dev/Personal/ocaml-oktree/dune
(dirs lib test benchmark doc)
```

### Scaffold Template: doc_dune.sexp
```scheme
;; Template for doc/dune
;; Template variables: {package_name}
(documentation
 (package {package_name})
 (mld_files index))
```

### Scaffold Template: index.mld
```
{0 {package_name} - {synopsis}}

{1 Overview}

TODO: Describe what {library_name} does and how to install it.

{v
opam install {package_name}
v}

{1 Documentation}

{2 Tutorial}

TODO: Link to getting_started.mld when created.

{2 How-to Guides}

TODO: Add guide page links here.

{2 Explanation}

TODO: Add explanation page links here.

{1 API Reference}

{!modules:
{library_name}
}

{1 Project}

TODO: Add project links (GitHub, etc.).
```

### Scaffold Template: secondary_dune.sexp
```scheme
;; Template for doc/{package_name}/dune
;; Template variables: {package_name}
(documentation
 (package {package_name})
 (mld_files index))
```

### Scaffold Template: secondary_index.mld
```
{0 {package_name} - {synopsis}}

{1 Overview}

TODO: Describe what this package does and why it exists separately.

{1 API Reference}

{!modules:
{library_name}
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| odoc 2.x only | odoc 3.0/3.1 released | March 2025 | New features (tables, media, cross-package config) but dune rules not yet updated |
| Manual HTML cross-package links | odoc 3.x `odoc-config.sexp` + `{!/package/page-foo}` | odoc 3.0 | Cleaner cross-package refs, but only usable with odoc 3.x driver (not dune build @doc yet) |
| `{[ ... ]}` OCaml-only code blocks | `{@lang[ ... ]}` language-specific blocks | odoc 2.2 | Can now show non-OCaml code with syntax highlighting |

**Deprecated/outdated:**
- odoc 3.x cross-package reference syntax (`{!/library/Module}`) is NOT yet usable via `dune build @doc`. The guidance file should document the HTML URL approach as the working method, with a note about odoc 3.x future.

## Open Questions

1. **Directory scaffold support in SKILL.md**
   - What we know: Current scaffold check looks for single files only (`.yml`, `.js`, `.yaml`, `.toml`, `.py`)
   - What's unclear: Whether the SKILL.md change should be a generic "also check for directory" or odoc-specific
   - Recommendation: Make it generic -- check for `scaffolds/{doc_system}/` directory as a fallback after single-file check. This benefits any future framework that needs multi-file scaffolding.

2. **Dynamic sub-topic question implementation**
   - What we know: The .qa.md defines the structure; options are runtime-generated from project scanning
   - What's unclear: Exact format of the scan instructions in the .qa.md, and whether SKILL.md Step 2b.5 needs modification or if the dynamic behavior can be described entirely within the .qa.md
   - Recommendation: Define scan instructions in the .qa.md as a new `## Follow-on` section with `scan:` fields. The SKILL.md's Step 2b.5 already says "Parse the `## Question N:` sections" -- it just needs to also parse follow-on sections. Keep the SKILL.md change minimal.

3. **odoc 3.x forward-compatibility in guidance**
   - What we know: odoc 3.0/3.1 exists; dune doesn't support it yet; features like tables, media, and odoc-config.sexp are real
   - What's unclear: Timeline for dune to support odoc 3.x
   - Recommendation: Guidance focuses on odoc 2.x (the dune-compatible path). Add a brief "odoc 3.x Preview" section at the end noting upcoming features. Do not use odoc 3.x-only syntax in any templates or examples.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bats (Bash Automated Testing System) |
| Config file | none -- tests use PROJECT_ROOT variable |
| Quick run command | `bats tests/phase-12-validation.bats` |
| Full suite command | `bats tests/` |

### Phase Requirements -> Test Map

No explicit requirement IDs were assigned for Phase 12. Based on the CONTEXT.md deliverables, the implicit requirements are:

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P12-01 | odoc.qa.md exists in defaults/ with Detection section and 3 questions | unit | `bats tests/phase-12-validation.bats -f "P12-01"` | Wave 0 |
| P12-02 | odoc.md exists in defaults/ with all required sections | unit | `bats tests/phase-12-validation.bats -f "P12-02"` | Wave 0 |
| P12-03 | scaffolds/odoc/ directory exists with template files | unit | `bats tests/phase-12-validation.bats -f "P12-03"` | Wave 0 |
| P12-04 | SKILL.md lists odoc as a selectable built-in doc system option | unit | `bats tests/phase-12-validation.bats -f "P12-04"` | Wave 0 |
| P12-05 | odoc.md contains cross-reference syntax rules from ocaml-odoc-guide | unit | `bats tests/phase-12-validation.bats -f "P12-05"` | Wave 0 |
| P12-06 | odoc.md contains quality checklist from ocaml-odoc-guide | unit | `bats tests/phase-12-validation.bats -f "P12-06"` | Wave 0 |
| P12-07 | odoc.qa.md Q3 includes follow-on sub-topic question structure | unit | `bats tests/phase-12-validation.bats -f "P12-07"` | Wave 0 |
| P12-08 | SKILL.md built-in frameworks list includes odoc | unit | `bats tests/phase-12-validation.bats -f "P12-08"` | Wave 0 |

### Sampling Rate
- **Per task commit:** `bats tests/phase-12-validation.bats`
- **Per wave merge:** `bats tests/`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/phase-12-validation.bats` -- covers P12-01 through P12-08
- Framework install: `brew install bats-core` -- if not already installed (likely already present from Phase 7)

## Sources

### Primary (HIGH confidence)
- Existing `ocaml-odoc-guide` SKILL.md at `/Users/paul/.claude/skills/ocaml-odoc-guide/SKILL.md` -- comprehensive, battle-tested odoc writing rules
- Existing `ocaml-odoc-guide` references at `/Users/paul/.claude/skills/ocaml-odoc-guide/references/` -- ODOC_SYNTAX.md, CROSS_PACKAGE.md, MLD_TEMPLATE.md
- Reference projects: `ocaml-spectrum` (5 packages, multi-library) and `ocaml-oktree` (1 package, single-library) -- real working dune/odoc configurations
- Existing framework files: `sphinx-shibuya.qa.md`, `sphinx-shibuya.md`, `scaffolds/sphinx-shibuya.py` -- pattern templates for new framework additions
- Setup SKILL.md at `doc-writer/skills/setup/SKILL.md` -- integration point for all framework changes

### Secondary (MEDIUM confidence)
- [OCaml.org generating-documentation guide](https://ocaml.org/docs/generating-documentation) -- `dune build @doc` usage, documentation stanza format
- [odoc for authors (3.1.0)](https://ocaml.org/p/odoc/latest/doc/odoc_for_authors.html) -- .mld file format, cross-referencing, code blocks, odoc 3.x features
- [odoc official site](https://ocaml.github.io/odoc/) -- confirms odoc 3.0 as latest with dune rules pending update

### Tertiary (LOW confidence)
- odoc 3.x dune compatibility timeline -- no official timeline found; dune rules rewrite mentioned as needed but no ETA

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- odoc and dune are well-established; versions verified against official sources
- Architecture: HIGH -- patterns directly replicate Phase 10/11 work; reference projects provide concrete examples
- Pitfalls: HIGH -- drawn from battle-tested ocaml-odoc-guide skill with known-good pitfall documentation
- Q3 follow-on mechanism: MEDIUM -- new behavior not present in other frameworks; implementation approach is sound but untested

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stable domain; main uncertainty is odoc 3.x dune timeline)
