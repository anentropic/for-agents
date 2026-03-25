# Multi-Package odoc Documentation

Patterns for documenting OCaml projects split across multiple opam packages.

## Architecture

Only the primary package gets full documentation treatment. Secondary packages get a brief overview + API reference + cross-links back to the primary.

Example layout for a project with 5 packages:

```
doc/
├── dune                           # Primary package .mld files
├── index.mld                      # Primary landing page
├── getting_started.mld            # Tutorial (primary only)
├── how_it_works.mld               # Explanation (primary only)
├── secondary_a/
│   ├── dune                       # Secondary A .mld files
│   └── index.mld                  # Brief overview + API links
├── secondary_b/
│   ├── dune
│   └── index.mld
```

## Dune Configuration

Each package needs its own `(documentation ...)` stanza declaring its .mld files.

Primary package (in `doc/dune`):
```scheme
(documentation
 (package my_primary)
 (mld_files index getting_started how_it_works custom_feature))
```

Secondary package (in `doc/secondary_a/dune`):
```scheme
(documentation
 (package secondary_a)
 (mld_files index))
```

## Cross-Package Link Syntax

The `{!page-name}` reference syntax only resolves within the same package. For links between packages, use relative HTML URLs:

```
(* Within same package *)
See {!page-getting_started} for a tutorial.

(* From secondary_a to primary *)
See {{:../my_primary/getting_started.html} Getting Started} for a tutorial.

(* From primary to secondary_a *)
See {{:../secondary_a/index.html} Secondary A} for details.

(* From secondary_a to secondary_b *)
See {{:../secondary_b/index.html} Secondary B}.
```

The URL structure mirrors the generated HTML directory layout:
```
_build/default/_doc/_html/
├── my_primary/
│   ├── index.html
│   ├── getting_started.html
│   └── My_primary/index.html     # Module docs
├── secondary_a/
│   ├── index.html
│   └── Secondary_a/index.html
```

## HTML Filename Rules

- `.mld` filename maps directly to `.html`: `getting_started.mld` -> `getting_started.html`
- There is NO `page-` prefix in the output: NOT `page-getting_started.html`
- Module docs go in subdirectories: `My_primary/index.html`, `My_primary/Submodule/index.html`

## Primary Package Landing Page

The primary `index.mld` is the documentation hub. It should link to all doc types and list all packages in the suite:

```
{0 My Project - One Line Description}

{1 Overview}

Brief description. Install command. Quick example.

{1 Documentation}

{2 Tutorial}

{!page-getting_started} — Step-by-step introduction.

{2 How-to Guides}

- {!page-custom_feature} — How to do X (advanced, rarely needed)

{2 Explanation}

- {!page-how_it_works} — Why X works the way it does

{1 API Reference}

Brief summary of the main API surface with code example.

{1 Libraries}

- {!My_primary} — Main library
- {!Secondary_a} — Description
- {!Secondary_b} — Description
```

## Secondary Package Pages

Keep these short. Explain what the package does, why it exists as a separate package, then link to API reference and back to primary docs.

```
{0 Secondary A - Brief Description}

{1 Overview}

What this package does and why it's separate.
[1-2 paragraphs max]

{1 Usage}

[One code example with result type annotations]

{[
let result = Secondary_a.do_thing input
(* val result : Secondary_a.t *)
]}

{1 API Reference}

{!modules:
Secondary_a.Main_module
}

{1 See Also}

- {{:../my_primary/index.html} My Primary} — Main library
- {{:../my_primary/how_it_works.html} How It Works} — Background
```

## Diataxis Mapping

For projects using the Diataxis framework:

| Type | Where | Which packages |
|---|---|---|
| Tutorial | `.mld` in primary | Primary only |
| How-to Guide | `.mld` in primary | Primary only |
| Explanation | `.mld` in primary | Primary only |
| Reference | `.mli` in each lib | All packages |
| Package overview | `index.mld` per package | All packages |

Secondary packages get reference docs (from .mli) + a brief overview page, with cross-links to the primary package's tutorials and explanations.
