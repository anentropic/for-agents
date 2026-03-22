# Odoc Guidance

Opinionated preferences for writing documentation with odoc for OCaml libraries. These are style preferences -- agents already understand odoc syntax. This file guides how features should be used, not what they are.

## Code Blocks

- Use `{[ ... ]}` for OCaml code examples. These are compiled by odoc -- every code block must be syntactically valid OCaml. If it does not parse, the build fails.
- Use `{v ... v}` for verbatim text: shell commands, config files, directory trees, or any content that is not OCaml code. No syntax highlighting, no compilation.
- Use `{@ocaml[ ... ]}` (odoc 2.2+) when you need syntax highlighting but want to avoid compilation. Useful for showing OCaml-like pseudocode or incomplete snippets. For non-OCaml languages, use `{@bash[ ... ]}`, `{@json[ ... ]}`, etc.
- Show result types and values as comments in every example. Do not leave the reader guessing what an expression evaluates to:

  ```ocaml
  let size = Chunk.byte_length chunk
  (* val size : int = 4096 *)

  let header = Chunk.to_header chunk
  (* val header : Header.t -- fields: version, flags, length *)
  ```

- `{[ ... ]}` and `{v ... v}` blocks must start at column 0 inside .mli doc comments. Leading indentation causes parse errors. Heading levels in .mli comments start at `{1 ...}` (not `{0 ...}`, which is reserved for .mld page titles).
- Use `let () = expr` after `let` bindings in `{[ ... ]}` blocks, not bare expressions. odoc requires syntactically complete OCaml:

  ```ocaml
  (* Good *)
  {[
  let result = My_lib.compute 42
  let () = assert (result > 0)
  ]}

  (* Bad -- bare expression after let binding *)
  {[
  let result = My_lib.compute 42
  result > 0
  ]}
  ```

- Show different aspects across multiple `{[ ... ]}` blocks: basic usage, realistic scenario, error handling, composition. Do not cram everything into one block.

## .mld File Structure

- Heading levels: `{0 Page Title}` for the page title (only in .mld files), `{1 Section}`, `{2 Subsection}`, `{3 Subsubsection}`.
- Page title format: `{0 Package_name - Brief description}`. The title appears in navigation and as the HTML page heading.
- Custom anchors: `{1:anchor_name Section Title}` creates a link target accessible via `{!section-anchor_name}`.
- Filename rules: underscores ONLY. Never use hyphens in .mld filenames. `getting_started.mld` works; `getting-started.mld` breaks `{!page-...}` references. See the File Naming section for why.
- Every new .mld file MUST be registered in the `(mld_files ...)` list in the corresponding `doc/dune`. Unregistered files silently do not appear in generated docs. This is the single most common reason pages go missing.
- Standard project file structure:

  ```
  project/
  +-- dune                       # Root: must include doc in (dirs ...)
  +-- doc/
  |   +-- dune                   # Documentation stanza with (mld_files ...)
  |   +-- index.mld              # Package landing page
  |   +-- guide_name.mld         # Supplementary guide pages
  +-- lib/
  |   +-- library_name/
  |       +-- dune               # Library stanza (no documentation stanza here)
  |       +-- module.mli         # Interface with odoc comments
  |       +-- module.ml
  +-- dune-project               # Add (odoc :with-doc) to packages
  ```

- Landing page (`index.mld`) is the documentation hub. Link to all doc types and list all modules:

  ```
  {0 My_library - One-line description}

  {1 Overview}

  What the library does. How to install it.

  {v
  opam install my_library
  v}

  {1 Documentation}

  {2 Tutorial}

  {!page-getting_started} -- Step-by-step introduction.

  {2 How-to Guides}

  - {!page-custom_feature} -- How to do X

  {2 Explanation}

  - {!page-how_it_works} -- Why X works the way it does

  {1 API Reference}

  {!modules:
  My_library
  }

  {1 Project}

  - {{:https://github.com/user/my-library} GitHub repository}
  ```

## .mli Doc Comments

- Every public module should have a module-level doc comment `(** ... *)` before the first declaration. If the project has a README, adapt its content for this comment. If no README exists, write a clear summary of what the module does.
- Function docs follow this pattern: summary line, extended description, one or more `{[ ... ]}` example blocks, then `@param`, `@return`, `@raise` tags:

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

- Module-level doc comment with frontmatter pattern:

  ```ocaml
  (** My_library does X for Y.

      Description paragraph explaining why this module exists.

      {1 Basic Usage}

  {[
  open My_library
  let result = do_something input
  ]}

      {1 Project}

      - {{:https://github.com/user/my-library} GitHub repository}
  *)
  ```

- Add comments for public values that have none. Preserve existing comments. Do not rewrite what the maintainer already wrote unless clearly incorrect.
- Nearly every public function should have at least one usage example. If a page is just type signatures, it needs examples.
- Documentation tags reference: `@param name`, `@return`, `@raise Exception condition`, `@see <url>`, `@since 1.0.0`, `@deprecated Use {!other_function} instead`.

## Cross-References

Within-package references use odoc's native syntax. Cross-package references require HTML URLs.

**Within-package module references:**

```
{!Module.value}                          (* value in a module *)
{!Module.Type}                           (* type in a module *)
{!Module.Type.field}                     (* record field *)
{!module:Module}                         (* explicit module link *)
{!module-type:S}                         (* module type *)
{!type:t}                                (* type *)
{!exception:Exn}                         (* exception *)
```

**Within-package page references:**

```
{!page-guide_name}                       (* .mld page, same package *)
{!section-anchor_name}                   (* section anchor *)
```

**Cross-package references (HTML URLs required):**

```
{{:../other_package/page.html} text}          (* cross-package .mld page *)
{{:../other_package/Module/index.html} text}  (* cross-package module *)
```

**External URLs:**

```
{{:https://example.com} link text}
```

**Critical rules:**
- `{!page-name}` only resolves within the same package. Cross-package page links MUST use relative HTML URLs.
- HTML output is `getting_started.html`, NOT `page-getting_started.html`. There is no `page-` prefix in the generated filename. When writing cross-package HTML links, omit it.
- Cross-reference rather than re-explain concepts. If a concept is covered on another page, link to it instead of duplicating the explanation.

## File Naming

- Use underscores only. Never hyphens. This applies to all .mld filenames.
- HTML output filename = .mld filename with `.html` extension, no prefix: `getting_started.mld` produces `getting_started.html`.
- Module docs go in subdirectories: `My_library/index.html`, `My_library/Submodule/index.html`.

**Why hyphens break:** odoc parses `{!page-getting-started}` as qualifier `page-getting` + target `-started`. The hyphen is a separator in odoc's reference syntax, not part of the filename.

Examples:

| Filename | Status | Why |
|---|---|---|
| `getting_started.mld` | Works | Underscores are safe in identifiers |
| `getting-started.mld` | Breaks | Hyphen parsed as qualifier separator |
| `how_to_configure.mld` | Works | Multiple underscores are fine |
| `how-to-configure.mld` | Breaks | Each hyphen creates a new parse boundary |

## Dune Wiring

- The `(documentation ...)` stanza goes in `doc/dune`, NOT in `lib/dune`. This stanza only picks up .mld files from its own directory.
- Register every .mld file in `(mld_files ...)`. Unregistered files silently do not appear in generated docs.

  ```scheme
  ;; doc/dune
  (documentation
   (package my_library)
   (mld_files index getting_started how_it_works))
  ```

- Add `(odoc :with-doc)` to package deps in `dune-project`:

  ```scheme
  ;; dune-project
  (lang dune 3.0)

  (package
   (name my_library)
   (synopsis "What it does")
   (depends
    (ocaml (>= 4.14))
    (odoc :with-doc)))
  ```

- Root `dune` must include `doc` in `(dirs ...)` if it uses the dirs stanza. If the root dune file has `(dirs lib test benchmark)`, add `doc` to the list:

  ```scheme
  ;; dune (root)
  (dirs lib test benchmark doc)
  ```

- When creating a new .mld file, ALWAYS add it to `(mld_files ...)` in the corresponding `doc/dune`. This is the most common source of "missing pages" issues.
- Install command: `opam install . --deps-only --with-doc -y`.

## Multi-Package Documentation

For projects with multiple opam packages, only the primary package gets full documentation treatment. Secondary packages get a brief overview, API reference, and cross-links back to the primary.

**Directory layout:**

```
doc/
+-- dune                           # Primary package .mld files
+-- index.mld                      # Primary landing page
+-- getting_started.mld            # Tutorial (primary only)
+-- how_it_works.mld               # Explanation (primary only)
+-- secondary_a/
|   +-- dune                       # Secondary A .mld files
|   +-- index.mld                  # Brief overview + API links
+-- secondary_b/
    +-- dune
    +-- index.mld
```

**Primary package dune configuration:**

```scheme
;; doc/dune
(documentation
 (package my_primary)
 (mld_files index getting_started how_it_works custom_feature))
```

**Secondary package dune configuration:**

```scheme
;; doc/secondary_a/dune
(documentation
 (package secondary_a)
 (mld_files index))
```

**Cross-package link syntax:**

```
(* Within same package -- use odoc reference *)
{!page-getting_started}

(* From secondary to primary -- use HTML URL *)
{{:../my_primary/getting_started.html} Getting Started}

(* From primary to secondary -- use HTML URL *)
{{:../secondary_a/index.html} Secondary A}

(* From secondary to secondary -- use HTML URL *)
{{:../secondary_b/index.html} Secondary B}
```

**HTML directory layout (generated):**

```
_build/default/_doc/_html/
+-- my_primary/
|   +-- index.html
|   +-- getting_started.html
|   +-- My_primary/index.html     # Module docs
+-- secondary_a/
|   +-- index.html
|   +-- Secondary_a/index.html
```

**Secondary package pages should be brief.** Explain what the package does, why it exists as a separate package, show one usage example, link to API reference, and cross-link back to the primary docs.

**Documentation distribution across packages:**

| Type | Where | Which Packages |
|---|---|---|
| Tutorial | `.mld` in primary | Primary only |
| How-to Guide | `.mld` in primary | Primary only |
| Explanation | `.mld` in primary | Primary only |
| Reference | `.mli` in each lib | All packages |
| Package overview | `index.mld` per package | All packages |

## Build Validation

- `dune build @doc` is the standard build target. Run it as a final check after writing documentation.
- Alternative: `opam exec -- dune build @doc` if the system dune version differs from the project's.
- Review output: `open _build/default/_doc/_html/index.html`.

**What `dune build @doc` catches:**
- Broken cross-references (`{!Module.nonexistent}`)
- Invalid .mld syntax (malformed headings, unclosed blocks)
- Missing dune registrations (unregistered .mld files silently omitted)
- Bad OCaml code blocks (`{[ ... ]}` that do not parse)

**Common error patterns:**

| Error | Cause | Fix |
|---|---|---|
| `Unknown reference` | Typo in `{!Module.value}` or cross-package `{!page-...}` | Check module/value name; use HTML URL for cross-package |
| `Syntax error in code block` | Invalid OCaml in `{[ ... ]}` | Fix the OCaml or switch to `{v ... v}` for pseudocode |
| `Page not found` | .mld file not in `(mld_files ...)` | Add to doc/dune |
| `Heading level 0 in .mli` | Used `{0 ...}` in an .mli comment | Use `{1 ...}` -- `{0}` is for .mld page titles only |

## odoc 3.x Preview

odoc 3.0 and 3.1 are available on opam, but dune has not yet updated its build rules to support the new CLI and incremental build capabilities. Until dune is updated, `dune build @doc` invokes odoc 2.x rules.

**New features in odoc 3.x (not yet usable via `dune build @doc`):**
- Tables: `{t ... }` for structured tabular content
- Media: `{image:...}` and `{audio:...}` for embedded media
- Language blocks: `{@lang[ ... ]}` for syntax-highlighted non-OCaml code (available since odoc 2.2)
- Cross-package configuration: `odoc-config.sexp` for managing cross-package references without HTML URLs
- Improved cross-package reference syntax: `{!/package/page-name}` (replaces HTML URL workaround)

Do NOT use odoc 3.x-only syntax in templates or examples. Stick to odoc 2.x syntax that `dune build @doc` actually processes.

## Quality Checklist

- [ ] Main .mli has module-level doc comment (from README if available)
- [ ] Each library has an .mld overview page (index.mld)
- [ ] 90%+ of public functions have usage examples
- [ ] Examples show result types/values as comments
- [ ] `dune build @doc` passes with zero warnings
- [ ] Cross-package links use HTML URLs, not `{!page-...}`
- [ ] .mld filenames use underscores, not hyphens
- [ ] Every .mld file registered in `(mld_files ...)` in its doc/dune
- [ ] Top-level pages link to GitHub repository
- [ ] Generated HTML reviewed for navigation and broken links

## Mermaid Diagrams

odoc has no native mermaid rendering support. Use a workaround: include the mermaid source as a verbatim block for reference, and link to an externally-generated SVG for the rendered diagram.

- Include mermaid source in a `{v ... v}` verbatim block so readers can see the diagram definition:

  ```ocaml
  (** Architecture overview.

      The processing pipeline follows this flow:

      {{:./diagrams/pipeline.svg} Pipeline diagram}

      Mermaid source for reference:

      {v
      flowchart LR
          A[Input] --> B{Validate}
          B -->|Valid| C[Process]
          B -->|Invalid| D[Error]
          C --> E[Output]
      v}
  *)
  ```

- To generate the SVG, use the mermaid CLI (`mmdc`) outside of odoc: `mmdc -i pipeline.mmd -o diagrams/pipeline.svg`. Store `.mmd` source files alongside the generated SVGs.
- Do NOT use or recommend `odoc-mermaid` or any experimental odoc mermaid extension -- these are not on opam stable and are not production-ready.
- The `{v ... v}` block renders as preformatted text, not as a diagram. The SVG link provides the visual rendering.
