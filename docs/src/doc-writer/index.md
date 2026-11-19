---
title: doc-writer
description: A Claude Code plugin that drafts, edits and tests library documentation with a pipeline of agents
---

# doc-writer

doc-writer is a Claude Code plugin that writes, audits and fixes the documentation for your
library. You describe who reads your docs, approve a list of pages, and a pipeline of agents
drafts the pages, edits them, and then checks whether a reader can get real tasks done with
them.

## Differences from prompting Claude directly

Prompting Claude to "write the docs" tends to produce pages written from the builder's point of
view, full of internal detail and familiar AI phrasing. doc-writer splits the work across
separate agents so that each one has a narrower job:

- **The Doc Persona never reads your source code.** It takes the reader profile you configured,
  sets itself 3 to 5 concrete goals, and tries to reach each one by following only the docs.
  Missing steps and dead-end links show up as FAIL or PARTIAL verdicts instead of slipping
  past someone who already knows the code.
- **The Doc Editor enforces your terminology and removes AI-writing patterns.** Its deslop
  pass measures every page before and after it rewrites, and checks that no code span, number
  or link was lost.
- **Nothing is committed for you.** Every command leaves its changes in your working tree, so
  you review them as an ordinary `git diff`.

!!! info "Requirements"

    - Claude Code, with permission to add a plugin marketplace.
    - A git repository for the library you want to document.
    - `python3` on your `PATH` for the Editor's prose measurements. Without it the Editor still
      runs and notes in its report that measurements were skipped.

## Supported documentation systems

doc-writer writes pages in the format of the system your project already uses:

| Doc system | Output |
|------------|--------|
| `mkdocs-material` | Markdown pages for MkDocs with the Material theme |
| `sphinx-shibuya` | Sphinx pages for the Shibuya theme |
| `odoc` | `.mld` pages for OCaml's odoc, plus proposed doc comments for `.mli` files |
| `plain-markdown` | Plain Markdown with no doc framework |

You can also name another system during setup. doc-writer then researches it and generates a
guidance file for it.

## Install

Add the marketplace, then install the plugin from it. In a Claude Code session:

```text
/plugin marketplace add anentropic/for-agents
/plugin install doc-writer@anentropic-for-agents
```

From the terminal, run the same two commands as `claude plugin marketplace add ...` and
`claude plugin install ...`. See [Installation](../index.md#installation) for scopes and
other details.

The plugin adds five commands: `/doc-writer:setup`, `/doc-writer:write`, `/doc-writer:review`,
`/doc-writer:edit` and `/doc-writer:upgrade`. Run `/doc-writer:setup` first in any project.

## Tutorial

- **[Document your first project](tutorial.md)**: install doc-writer, configure it for a
  library with no docs, and review a full set of generated pages.

## How-to guides

- **[Set up a project that already has docs](how-to/configure.md#set-up-a-project-that-already-has-docs)**:
  run the first setup on a library with an existing site, keeping its config and pointing the
  docs root at its pages.
- **[Configure or reconfigure a project](how-to/configure.md)**: change personas, tone, doc
  system or paths, reset the configuration, or refresh the generated context.
- **[Update docs after code changes](how-to/update-docs.md)**: re-run the pipeline to cover new
  symbols and refresh pages that describe old behavior.
- **[Resolve PARTIAL and FAIL verdicts](how-to/resolve-verdicts.md)**: decide which persona
  suggestions to apply and what to do when failures do not converge.
- **[Audit docs without changing them](how-to/audit.md)**: get coverage, quality and persona
  findings for your existing docs, with optional Editor fixes.
- **[Make targeted fixes](how-to/targeted-fixes.md)**: fix selected findings or a described
  problem on only the pages involved.
- **[Add project rules and terminology](how-to/project-rules.md)**: give every agent your own
  writing rules and canonical terms.
- **[Upgrade after a plugin update](how-to/upgrade.md)**: migrate your `.doc-writer/` files to a
  new plugin version without losing your edits.

## Reference

- **[Commands](reference/commands.md)**: every command, its arguments, what it reads and writes,
  and its side effects.
- **[config.yaml](reference/configuration.md)**: every field in `.doc-writer/config.yaml`, with
  an annotated example.
- **[The .doc-writer folder](reference/files.md)**: each file doc-writer keeps, who writes it,
  and whether your edits survive.

## Explanation

- **[How the pipeline works](explanation/pipeline.md)**: the four agents, the order they run in,
  and why the work is split this way.
- **[Personas and verdicts](explanation/personas.md)**: how the Doc Persona builds scenarios,
  walks the docs and decides between PASS, PARTIAL and FAIL.
- **[Quality rules and the deslop pass](explanation/quality.md)**: the rules every page must
  meet, Diataxis page types, and how prose gets measured.
