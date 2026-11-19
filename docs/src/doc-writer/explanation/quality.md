---
title: Quality rules and the humanizer pass
description: The rules every page must meet, how Diataxis page types and type blur work, and how the Editor measures prose
---

# Quality rules and the humanizer pass

Every page doc-writer produces is held to the same standards, whatever your project. This page
explains those standards: the universal quality rules, the Diataxis page types and the "type
blur" the Editor looks for, and how the humanizer pass measures and rewrites prose.

## Universal rules and project rules

Five universal rules apply to every page and cannot be turned off:

1. **No internal details.** Test utilities, CI configuration, development scripts and internal
   modules never appear in user-facing pages. The reader uses the library; they don't work on
   it.
2. **Working code examples.** Every documented feature has at least one realistic example, and
   every code block names its language.
3. **Consistent structure.** Pages of the same type follow the same template, so two how-to
   guides have their prerequisites, steps and troubleshooting in the same places.
4. **Cross-referenced code mentions.** When there is an API reference, inline code mentions in
   prose link to it.
5. **Persona-calibrated language.** Vocabulary and depth match the configured persona, and
   nothing from its `never_assume` list is used without explanation.

Your own rules in `.doc-writer/rules.md` sit on top of these. They can add requirements, such
as a spelling convention or a mandatory section, but not remove any of the five. The baseline is
the same in every project that uses doc-writer, and each project adds its house style on top. See [Add project rules and terminology](../how-to/project-rules.md).

## Diataxis page types

doc-writer organizes pages with the [Diataxis](https://diataxis.fr/) framework, which sorts
documentation by what the reader needs at that moment:

| Type | The reader is | The page |
|------|---------------|----------|
| Tutorial | Learning, by doing | Leads them through a guaranteed-to-work exercise |
| How-to guide | Working on a specific goal | Gives the steps, assuming competence |
| Reference | Looking something up | States facts: options, fields, signatures |
| Explanation | Trying to understand | Discusses background, design and trade-offs |

The Author classifies every page in the inventory as one of these and writes it to that type's
template. API reference is normally left to a generator such as mkdocstrings or Sphinx autodoc,
so the Author proposes tutorials, how-to guides and explanation pages.

### Type blur

**Type blur** is a page that drifts into another type's job: a how-to guide that stops to
explain the theory behind a step, or a tutorial that offers the reader five alternative
approaches. Each drift serves one reader at the expense of another.

The Editor's second pass looks for blur. A paragraph or two that drifted is moved, trimmed or
replaced with a link to the right kind of page. A page that fundamentally mixes two types is not
patched: the Editor reports it as a BLOCKING finding, so the Author can split or restructure it.

## The humanizer pass

Machine-written prose has recognizable habits: significance inflation ("plays a crucial role"),
filler and hedging, sentences that end in a trailing "-ing" clause, em dashes everywhere, and
words a model uses far more often than people do. Readers notice them, and they make
documentation harder to trust. The humanizer, the Editor's third pass, rewrites them out.

The pass measures as well as rewrites. It uses the prose scanner from
[deslop](https://github.com/etodanik/deslop) by Danny Povolotski, which ships with doc-writer.
For each page, the Editor:

1. **Scans the page before editing.** The scanner flags individual sentences against a catalog
   of patterns and computes a likeness score: 0 is a typical human rate, 1 a typical model rate.
2. **Reads the page itself** for what a scanner can't see, such as a recap paragraph that adds
   nothing or a benefit claimed with no cost.
3. **Rewrites**, keeping the formal, second-person register of documentation. It adds no first
   person, humor or invented examples.
4. **Compares the rewrite with the original.** The comparison lists flags fixed and any new ones
   introduced, and checks that no number, code span or link was lost. A dropped fact must be
   restored.

The Editor stops after at most two rounds of fixes, because rewriting again tends to make text
worse. The before and after scores for each page appear in the **Humanizer Measurements** table
of `.doc-writer/editor-report.md`.

The pass leaves some things alone: code blocks and inline code, bold key terms,
lists of options or parameters, the section headings your doc system and page type expect, and
your project's own terms.

### Protected terms

Technical docs repeat their own vocabulary on purpose. A scanner looking for repetition would
flag a phrase like "connection pool" every time it appears. To prevent that, every multi-word or
hyphenated term listed in `.doc-writer/terminology.yaml` is masked before scanning, and the
comparison reports any protected term a rewrite used less often. Single words are not masked.
The Editor adds the project's concept names to the file during its terminology pass, and you can
add more.

### Without python3

The scanner is a Python script that needs only the standard library. If `python3` is not on your
`PATH`, the Editor still rewrites the prose by the same rules, but without measurements, and adds
a NITPICK to its report: "Humanizer ran without deslop measurements (scanner unavailable)." The
measurements table is left out.

## Related

- [How the pipeline works](pipeline.md): where the Editor's passes fit in a run.
- [Add project rules and terminology](../how-to/project-rules.md): add rules and protected terms.
- [The .doc-writer folder](../reference/files.md): `editor-report.md` and `terminology.yaml`.
