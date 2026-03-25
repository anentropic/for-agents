---
name: ocaml-odoc-guide
description: Generate comprehensive, example-rich documentation for OCaml libraries using odoc. Emphasizes examples in isolation, validated code blocks, and informative frontmatter.
---

# OCaml odoc Documentation Guide

Best practices for creating documentation for OCaml libraries using odoc.

## Core Principles

### Examples Everywhere
- Nearly every public function should have at least one usage example
- Low-level pages must be informative in isolation
- Show result types and values in examples as comments:
  ```ocaml
  let size = Chunk.byte_length chunk
  (* val size : int = 4096 *)

  let header = Chunk.to_header chunk
  (* val header : Header.t — fields: version, flags, length *)
  ```

### Validated Code
- All examples in `{[ ... ]}` blocks are compiled by odoc
- Include expected outputs as comments in examples
- Test complex examples before adding them

### Explain Why, Not Just What
- Don't just describe what a module does — explain why it exists
- Frame niche features honestly: "if you're unsure whether you need this, you almost certainly don't"
- Don't repeat explanations across pages; cross-reference instead

### Frontmatter Sourcing
- If the project has a README.md, adapt it for the main .mli module doc comment
- If no README exists, generate appropriate content and ask the user if they want a README too

### Writing Tone
- Direct and technical. Match the project's existing tone.
- MANDATORY: After writing or editing any documentation text, invoke the `humanizer` skill on the result. Do not skip this step.

## Critical odoc Gotchas

These cause real build failures or broken links. Check every time.

### Page filenames: underscores only
Hyphens in .mld filenames break `{!page-...}` references. odoc parses `{!page-getting-started}` as qualifier `page-getting` + target `-started`.

- `getting_started.mld` — works
- `getting-started.mld` — breaks

### Cross-package references
`{!page-name}` only resolves within the same package. For cross-package links, use HTML URLs:

```
(* Within same package — use odoc reference *)
{!page-getting_started}

(* Across packages — use relative HTML URL *)
{{:../my_library/getting_started.html} Getting Started}
```

### HTML output filenames
odoc generates `getting_started.html`, NOT `page-getting_started.html`. There is no `page-` prefix in the output filename. When writing cross-package HTML links, omit it.

### Code blocks in .mli comments
`{v ... v}` and `{[ ... ]}` blocks must start at column 0 (no leading indentation). Heading levels in .mli comments start at `{1 ...}` (not `{0 ...}`, which is for .mld page titles). Code in `{[ ... ]}` must be syntactically valid OCaml — use `let () = expr` after `let` bindings, not bare expressions.

## File Structure

```
project/
├── dune                       # Root: must include doc in (dirs ...)
├── doc/
│   ├── dune                   # Documentation stanza with (mld_files ...)
│   ├── index.mld              # Package landing page
│   └── guide_name.mld         # Supplementary guide pages
├── lib/
│   └── library_name/
│       ├── dune               # Library stanza (no documentation stanza here)
│       ├── module.mli         # Interface with odoc comments
│       └── module.ml
└── dune-project               # Add (odoc :with-doc) to packages
```

## Setup Checklist

1. Add `(odoc :with-doc)` to package deps in `dune-project`
2. Install: `opam install . --deps-only --with-doc -y`
3. If root `dune` has `(dirs ...)`, ensure `doc` is listed
4. Create `doc/dune` with the documentation stanza:
   ```scheme
   (documentation
    (package my_library)
    (mld_files index guide_name))
   ```
   Do NOT put `(documentation ...)` in `lib/dune` — it only picks up .mld files from its own directory.
5. Build: `dune build @doc` (or `opam exec -- dune build @doc` if system dune version differs)
6. View: `open _build/default/_doc/_html/index.html`

## Multi-Package Documentation

For projects with multiple opam packages, see [CROSS_PACKAGE.md](references/CROSS_PACKAGE.md) for detailed patterns. Key points:

- Only the primary package needs full documentation (tutorials, how-tos, explanations)
- Secondary packages get a brief overview .mld + API reference + cross-links back to the primary
- Each package's .mld files live in `doc/<package_name>/dune` (except the primary, which uses `doc/dune`)
- Use relative HTML URLs for all cross-package links

## Top-Level Frontmatter

The main .mli module doc comment is the primary entry point users see. Place a `(** ... *)` comment before the first declaration:

```ocaml
(** My_library does X for Y.

    Description paragraph.

    {1 Basic Usage}

{[
open My_library
let result = do_something input
]}

    {1 Project}

    - {{:https://github.com/user/my-library}GitHub repository}
*)
```

## Writing .mld Files

Library-level guides. See [MLD_TEMPLATE.md](templates/MLD_TEMPLATE.md) for odoc-specific structure.

MANDATORY: Invoke the `diataxis-documentation` skill to choose the right documentation type for each page and apply its writing guidelines. Every .mld page must map to a Diataxis type (tutorial, how-to, explanation, or reference). Do not skip this step.

Only the primary package needs full Diataxis treatment; secondary packages just need overview + API reference.

## Writing .mli Function Docs

```ocaml
(** Parse a duration string into seconds.

    Accepts formats like ["3h30m"], ["45s"], or ["1d12h"].
    Components can appear in any order.

    {[
      let secs = Duration.of_string "2h30m"
      (* val secs : int = 9000 *)
    ]}

    {[
      let secs = Duration.of_string "1d"
      (* val secs : int = 86400 *)
    ]}

    @param s Duration string (e.g. "3h", "45m10s")
    @return Total seconds
    @raise Invalid_argument if the format is unrecognized *)
val of_string : string -> int
```

Show different aspects across multiple `{[ ... ]}` blocks: basic usage, realistic scenario, error handling, composition.

## Cross-References

```
{!Module.value}                          (* within same package *)
{!page-guide_name}                       (* .mld page, same package *)
{{:../other_package/page.html} text}     (* cross-package .mld *)
{{:../other_package/Module/index.html} text}  (* cross-package module *)
{{:https://example.com} text}            (* external URL *)
```

See [ODOC_SYNTAX.md](references/ODOC_SYNTAX.md) for full markup reference.

## Common Pitfalls

1. **Not enough examples**: If a page is just type signatures, add examples
2. **Hyphens in .mld filenames**: Use underscores. Hyphens break `{!page-...}` references.
3. **Wrong cross-package link syntax**: `{!page-X}` is same-package only. Use HTML URLs across packages.
4. **`page-` prefix in HTML URLs**: odoc outputs `name.html`, not `page-name.html`
5. **`doc/` excluded from `(dirs ...)`**: Root dune must list `doc` if it uses `(dirs ...)`
6. **`(documentation ...)` in wrong dir**: This stanza only finds .mld files in its own directory
7. **AI writing patterns**: You MUST invoke the `humanizer` skill on all documentation text before finalizing.

## Quality Checklist

- [ ] Main .mli has frontmatter (from README if available)
- [ ] Each library has an .mld overview page
- [ ] 90%+ of public functions have usage examples
- [ ] Examples show result types/values as comments
- [ ] `dune build @doc` passes with zero warnings
- [ ] Cross-package links use HTML URLs, not `{!page-...}`
- [ ] .mld filenames use underscores, not hyphens
- [ ] Each .mld page classified via `diataxis-documentation` skill
- [ ] All text reviewed with `humanizer` skill
- [ ] Top-level pages link to GitHub repository
- [ ] Generated HTML reviewed for navigation and broken links
