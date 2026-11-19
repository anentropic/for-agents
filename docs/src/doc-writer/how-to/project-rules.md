---
title: Add project rules and terminology
description: Give the Author and Editor your own writing rules and the exact spelling of your project's terms
---

# How to add project rules and terminology

doc-writer applies five universal quality rules to every page. On top of them you can add rules
of your own, such as a required section or a spelling convention, and fix how your project's
terms are written. This guide covers `.doc-writer/rules.md` and `.doc-writer/terminology.yaml`.

## Before you start

- `/doc-writer:setup` has run, so `.doc-writer/rules.md` exists.
- `.doc-writer/terminology.yaml` appears after the first Doc Editor run. You can also create it
  yourself.

## Add a writing rule

Open `.doc-writer/rules.md` and add rules under the **Project Rules** heading. Write each rule
as a plain instruction; there is no special syntax.

```markdown title=".doc-writer/rules.md"
## Project Rules

- Include a "Requirements" section in every how-to guide listing the minimum Python version.
- Use British English spelling throughout.
- Show the import line in every code example, even when an earlier example already has it.
- Refer to the command-line tool as `tidy`, never as "the CLI".
```

Make each rule specific enough to check. "Use clear language" gives an agent nothing to act on;
"Use British English spelling throughout" does.

!!! info "Rules add to the baseline"

    Project rules extend the universal rules but cannot switch any of them off. A rule such as
    "examples may skip imports" does not override the requirement that the first example in a
    section is self-contained.

## Fix how a term is written

The Doc Editor keeps a term map in `.doc-writer/terminology.yaml`. On each run it loads the
file, normalizes the docs to the canonical forms, adds any new terms it finds, and writes the
file back. The file has four sections:

```yaml title=".doc-writer/terminology.yaml"
version: 1

source_terms: # (1)!
  - canonical: "RuleSet"
    variants: ["ruleset", "Ruleset"]
    source: "class RuleSet in src/tidyclip/rules.py"

proper_nouns: # (2)!
  - canonical: "PyPI"
    variants: ["Pypi", "pypi"]

project_terms: # (3)!
  - canonical: "rule file"
    variants: ["rules file"]
  - canonical: "dry-run mode"
    variants: []

overrides: # (4)!
  "rules file": "rule file"
```

1. Symbol names found in your source code. The Editor fills this in; the exact casing in the
   code is the canonical form.
2. Product and brand names, with the misspellings to correct.
3. Your project's own vocabulary. Add multi-word and hyphenated concept names here, even with no
   variants, to protect them from the deslop pass.
4. Your decisions. An entry here wins over everything the Editor detects.

To fix a term:

- **To force a spelling**, add an entry under `overrides`. Overrides take precedence over source
  code, standard proper-noun forms and frequency.
- **To protect a phrase**, add it under `project_terms`. The deslop scanner would otherwise
  flag a repeated multi-word name such as "dry-run mode" as jargon or repetition, and the Editor
  might reword it. Listed terms are kept as written, and the Editor reports any that a rewrite
  removed.

Only list your project's fixed names. Ordinary English synonyms, such as "use" and "utilize", are
not terms and the Editor ignores them.

## When the agents pick up your changes

There is no reload step. Each agent reads these files when it starts:

| File | Read by |
|------|---------|
| `rules.md` | Doc Author and Doc Editor, on every `write`, `review` and `edit` run |
| `terminology.yaml` | Doc Editor, on every run |

The Doc Persona reads neither. It judges the docs as a reader would, not against your rules.

## Check the result

Run an audit to see your rules applied as findings without changing any page:

```text
/doc-writer:review
```

Rule violations and term normalizations appear in `.doc-writer/editor-report.md`; term changes
are listed in its **Terminology Changes** table.

## Troubleshooting

### A term you added keeps being changed back

The Editor ranks term sources: overrides first, then the spelling in your source code, then
standard proper-noun forms, then the most frequent form. If your preferred form loses to the
source code, add it under `overrides`.

### Your rules were replaced

`/doc-writer:setup --reset` replaces `rules.md` with the default template. During
`/doc-writer:upgrade`, your rules are merged section by section and you are asked about any
conflict, so they are kept unless you choose otherwise.

## Related

- [Quality rules and the deslop pass](../explanation/quality.md): the universal rules and how
  the deslop pass uses protected terms.
- [The .doc-writer folder](../reference/files.md): which files are safe to edit.
