# Phase 12: Odoc Framework for OCaml Projects - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Odoc as a built-in supported framework in the doc-writer plugin — on equal footing with mkdocs-material and sphinx-shibuya. Deliverables: `odoc.qa.md` question set (with follow-on sub-topic questions), `odoc.md` comprehensive guidance file (replacing the standalone `ocaml-odoc-guide` skill), `scaffolds/odoc/` template files (dune stanzas + .mld stubs), and setup skill updated to list `odoc` as a selectable doc system. The `odoc.md` guidance absorbs all content from the existing `ocaml-odoc-guide` skill — that skill becomes redundant after this phase.

</domain>

<decisions>
## Implementation Decisions

### Scaffold scope
- Scaffold configures existing dune files (adds `(documentation ...)` stanzas) — projects already have dune files, they just need the doc stanza added
- Scaffold also creates `doc/index.mld` and guide page stubs (not just dune plumbing)
- For multi-library projects (detected via package count in dune-project): generate per-package doc stanzas + a minimal `index.mld` stub for each additional package; primary package gets full scaffold treatment
- Template variables: `{package_name}`, `{library_name}`, `{synopsis}` — inferred from `dune-project` (package name, synopsis) and `lib/*/dune` (library name)

### ocaml-odoc-guide skill replacement
- `odoc.md` is comprehensive — absorbs all content from the `ocaml-odoc-guide` skill: pitfalls, cross-reference syntax, .mli comment style, .mld file structure, file naming rules, dune wiring, quality checklist
- The standalone `ocaml-odoc-guide` skill becomes redundant after this phase (do not maintain both)
- Do NOT duplicate diataxis/humanizer invocation requirements in `odoc.md` — the doc-writer agent prompts already mandate these; odoc.md focuses on OCaml/odoc-specific preferences

### Q&A content
- **Q1 (Structure):** Single-library vs multi-library confirmation. Auto-detected from dune-project package count. Presented as confirmation, not discovery.
- **Q2 (Scope):** Author scope. `.mld pages + .mli doc comment improvements` is the **Recommended** option. Option: `.mld pages only` for users who want to keep .mli untouched.
- **Q3 (Guides):** Which guide page types to create — multiSelect: `Getting started / Tutorial`, `How-to guides`, `Explanation pages`. Each selected type triggers a follow-on sub-topic question.
- **Q3 follow-on sub-topic questions:** Research-guided suggestions — setup skill scans the project's module names, exported .mli signatures, and existing .mld files to propose relevant sub-topics for each selected guide type. The `.qa.md` defines the question structure; options are generated dynamically at setup time (not pre-defined static lists).

### Author agent behaviour
- **.mli doc comments:** Add comments for public values that have none. Preserve existing comments. Do not rewrite what the maintainer already wrote unless clearly incorrect.
- **dune registration:** When creating a new `.mld` file, the author must also add it to the `(mld_files ...)` list in the corresponding `doc/dune`. New files that aren't registered will silently not appear in the generated docs.
- **Build validation:** Author runs `dune build @doc` as a final check after writing. Catches broken cross-references, invalid .mld syntax, missing dune registrations, and bad OCaml code blocks before handoff to Editor.

### Claude's Discretion
- Exact prose wording and examples in `odoc.md` sections
- Whether to scaffold a `doc/dune` file or only a `lib/*/dune` snippet for the documentation stanza, depending on project layout
- Specific `(mld_files ...)` entries in stub scaffolds (generic placeholder names like `getting_started`, `how_to`, `concepts` until Q3 sub-topics are confirmed)
- Format of the research-guided sub-topic suggestions (freeform list, multiSelect, or plain-text prompt)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing framework infrastructure (pattern source)
- `doc-writer/skills/setup/defaults/mkdocs-material.qa.md` — Pattern for .qa.md structure: Detection section, question format, detect_context, recommend_if fields
- `doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md` — Pattern for .qa.md with follow-on-style questions; same format to replicate for odoc
- `doc-writer/skills/setup/defaults/mkdocs-material.md` — Pattern for guidance file: section structure, opinionated preference style
- `doc-writer/skills/setup/defaults/sphinx-shibuya.md` — Pattern for comprehensive guidance file to replicate for odoc
- `doc-writer/skills/setup/defaults/scaffolds/sphinx-shibuya.py` — Pattern for scaffold template with `{template_variable}` substitution
- `doc-writer/skills/setup/SKILL.md` — Integration point: Step 2b option list, framework_root logic, Step 2b.3 scaffold check (now includes `.py` variant), Step 2b.5 Q&A reading

### ocaml-odoc-guide skill (content to absorb)
- `/Users/paul/.claude/skills/ocaml-odoc-guide/SKILL.md` — Primary source: writing rules, pitfalls, file structure, cross-reference syntax, quality checklist. All of this content moves into `odoc.md`.
- `/Users/paul/.claude/skills/ocaml-odoc-guide/references/ODOC_SYNTAX.md` — odoc markup syntax reference
- `/Users/paul/.claude/skills/ocaml-odoc-guide/references/CROSS_PACKAGE.md` — Cross-package link syntax rules (critical pitfall area)
- `/Users/paul/.claude/skills/ocaml-odoc-guide/templates/MLD_TEMPLATE.md` — .mld file template to incorporate into guidance

### Reference OCaml projects
- `../ocaml-spectrum/` — Multi-library reference project (5 packages: spectrum, spectrum_capabilities, spectrum_palette_ppx, spectrum_palettes, spectrum_tools). Shows per-package `doc/` trees and `(documentation (package ...) (mld_files ...))` stanzas.
- `../ocaml-oktree/` — Single-library reference project. Shows minimal root `dune` + `doc/dune` setup.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `sphinx-shibuya.qa.md` — Direct template for `odoc.qa.md` structure; replicate Detection section format and question fields exactly
- `sphinx-shibuya.md` — Direct template for `odoc.md` section headings and prose style
- `scaffolds/sphinx-shibuya.py` — Pattern for scaffold: single file with `{template_variable}` placeholders; odoc scaffold may need multiple files (doc/dune, doc/index.mld) — planner should decide whether to use a directory or a combined template

### Established Patterns
- `.qa.md` Detection section: `Config file:` field + `Features to detect:` list. For odoc: `Config file: dune-project` + detect `(documentation ...)` stanza, number of `(package ...)` blocks.
- `framework_root` variable in SKILL.md: built-in frameworks point to `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults`. Scaffold lookup already supports `.py` extension (Phase 11 fix). Odoc scaffold may be a directory — SKILL.md scaffold check may need to support directory scaffolds.
- SKILL.md Step 2b option list (line 253–255): `odoc` entry slots in here as `{ label: "odoc", description: "OCaml documentation via odoc" }`

### Integration Points
- Step 2b detection: check for `dune-project` in project root (OCaml project identifier)
- Step 2b.5 dynamic Q&A reading: `{framework_root}/odoc.qa.md` — same mechanism as other built-in frameworks
- New pattern: Q3 follow-on sub-topic questions require setup skill to scan project source (module names, .mli signatures) at Q3 presentation time — this is new behaviour not present in other framework Q&As

</code_context>

<specifics>
## Specific Ideas

- `ocaml-spectrum` shows the canonical multi-library layout: each sub-package has `doc/{package_name}/dune` with `(documentation (package {name}) (mld_files index))`. The primary package `spectrum` has the richer `doc/` with narrative guide pages.
- `ocaml-oktree` shows the minimal single-library layout: root `dune` lists `(dirs lib test benchmark doc)`, `doc/dune` has `(documentation (package oktree) (mld_files index oktree))`.
- Build validation command: `dune build @doc` — this is the standard target; odoc.md should instruct the author to run this and fix all warnings/errors before finishing.
- The `ocaml-odoc-guide` skill's quality checklist is a good ending section for `odoc.md` — keep it as a checklist the author self-checks against before handing off.
- Scaffold for multi-library: the setup skill already detects library count from Q1; the scaffold generator should loop over detected packages and create stub `doc/{package}/dune` + `doc/{package}/index.mld` for each non-primary package.

</specifics>

<deferred>
## Deferred Ideas

- Apply follow-on sub-topic Q&A pattern to mkdocs-material and sphinx-shibuya — currently those frameworks have flat Q3 feature lists. Worth adding in a future polish phase.
- Delete/deprecate the `ocaml-odoc-guide` skill after this phase ships — that's a separate operation outside the doc-writer plugin scope.

</deferred>

---

*Phase: 12-add-odoc-framework-for-ocaml-projects*
*Context gathered: 2026-03-19*
