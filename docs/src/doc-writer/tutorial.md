---
title: Document your first project
description: Install doc-writer, configure it for a library with no docs, and review a full set of generated pages
difficulty: beginner
---

# Document your first project

In this tutorial you install doc-writer, configure it for a small library that has a README and
docstrings but no documentation site, and run the full pipeline. At the end you have a set of
uncommitted pages in `docs/`, organized by page type, that you review as a diff and preview in
your browser.

The examples use a small Python package with an MkDocs Material site. The same commands work
for TypeScript, Rust, Go and OCaml projects, and for the other supported doc systems.

## Prerequisites

- A library project open in a Claude Code session, at the root of its git repository.
- A clean working tree, so the diff at the end shows only what doc-writer wrote.
- `python3` on your `PATH`. The Editor uses it to measure prose; without it the pipeline still
  runs, unmeasured.
- MkDocs Material installed, or ready to install, so you can preview the result.

## Step 1: Install the plugin

Add the marketplace and install doc-writer from it:

```text
/plugin marketplace add anentropic/for-agents
/plugin install doc-writer@anentropic-for-agents
```

Type `/doc-writer` and check that the five commands appear in the command list: `setup`,
`write`, `review`, `edit` and `upgrade`.

## Step 2: Run setup

Setup asks who reads your docs and how your doc system is configured, then writes its answers
to a `.doc-writer/` folder in your project. Start it:

```text
/doc-writer:setup
```

Every question offers fixed choices plus two escape options: **Type something else**, to answer
in your own words, and **Chat about this**, to discuss the question before you answer it.

### Use cases

The first question asks for a typical use case: what problem someone solves with your library.
Choose **Skip** for this tutorial. doc-writer infers use cases from your persona description
instead.

### User persona

Next, setup asks you to describe your reader in plain text. A **persona** is a profile of one
kind of reader: what they already know, what must always be explained to them, and what they
try to do with your library. Write a few sentences, for example:

```text
Python developers who clean and normalize text before loading it into a
database. They know Python, pip and virtual environments. They don't know
our normalization rules or our config file format. They mostly want to
clean a batch of strings, configure custom rules, and plug the library
into a pandas pipeline. They found us searching PyPI for a text-cleaning
library.
```

Setup turns this into structured fields (skill level, assumed knowledge, what to never assume,
tasks) and shows them back to you. Choose **Looks good**, then **No, continue** when asked
whether to add another persona.

### Tone

Choose **Helpful and comprehensive, warm but businesslike**. The tone applies to every page the
pipeline writes.

### Doc system and framework questions

Setup shows the doc system it detected. Choose **mkdocs-material**.

If your project has no `mkdocs.yml` yet, setup writes one from its defaults, creates a starter
`docs/index.md`, and shows the install command for MkDocs Material without running it. If you
already have an `mkdocs.yml`, setup lists any recommended features it lacks and asks before
adding each one.

Three MkDocs questions follow. For this tutorial, choose:

- **Navigation**: **Sidebar only**.
- **API docs**: **None**.
- **Features**: keep the preselected options.

### Paths

Setup proposes a docs root (where pages are written) and a source root (where your code lives).
Accept the defaults if they match your project, for example `docs/` and `src/`. If a default is
wrong, type the correct path instead of pressing Enter, for example `docs/src/` when your pages
live there.

### Check the result

Setup writes its files and then runs the Doc Researcher, which reads your config and code and
writes an expanded `context.md`. You should see a summary like this:

```text
## Setup Complete

Created `.doc-writer/` with:
- config.yaml -- 1 user persona(s), tone: warm-businesslike, doc system: mkdocs-material, plugin version: 1.8.0, paths configured
- mkdocs-material.md -- Documentation system guidance (editable)
- rules.md -- Project-specific rules template (editable)
- .originals/ -- Pristine copies of guidance and rules for future upgrades

Running researcher to generate context.md...
```

When the researcher finishes, setup suggests running `/clear` before your next command. Do
that now: the pipeline in the next step uses a lot of context.

## Step 3: Run the pipeline

```text
/doc-writer:write
```

Because `docs/` holds no pages yet (a starter `index.md` does not count), the pipeline runs in
create mode:

```text
No existing documentation found in docs/. Running full pipeline.
```

It first scans your source root for exported symbols and writes the ones with no documentation
to `.doc-writer/gap-report.md`. Then the Doc Author scans the codebase and proposes a page
inventory.

## Step 4: Approve the page inventory

The pipeline shows the proposed pages as a list with every page selected. Each entry gives the
page title, its type (tutorial, how-to or explanation) and the sections it will contain. The
full proposal, with file paths, is in `.doc-writer/page-inventory.md`.

Deselect any page you don't want and confirm. To add or reshape a page, choose
**Type something else** and describe the change.

After you confirm, the pipeline runs without further questions until the end:

1. The **Doc Author** writes the approved pages.
2. The **Doc Editor** normalizes terminology, fixes pages that mix page types, rewrites
   AI-sounding prose, and checks cross-references. It writes `.doc-writer/editor-report.md`.
3. The **Doc Persona** tries to complete 3 to 5 tasks as your reader, using only the docs, and
   gives each one a verdict: PASS, PARTIAL or FAIL.

If any task FAILs, the Author revises the pages responsible and the Editor and Persona run
again, for up to three passes in total.

## Step 5: Decide on PARTIAL fixes

A PARTIAL verdict means the reader could finish the task, but with friction. If any remain, the
pipeline lists the Persona's suggested fixes, one per line, labelled with the page and section:

```text
[1] docs/how-to/custom-rules.md > Load rules from a file
    Show the expected file format before the loading example
```

Select the fixes you want, or choose **Apply all fixes** or **Skip all fixes**. Selected fixes
are applied straight to the pages, without another pipeline pass.

## Step 6: Read the summary

The pipeline ends with a summary:

```text
## Documentation Pipeline Complete

### Pipeline Mode
Full documentation generated from scratch.

### Pages Written/Revised
...

### Persona Verdicts
**Python developers who clean text data:**
- S1: PASS -- installed the library and cleaned a first batch of strings
...
```

Check the **Persona Verdicts** section. Every scenario should show PASS, or a PARTIAL you chose
to accept.

## Step 7: Review and build

Nothing has been committed. List what changed:

```bash
git status
git diff
```

You should see new pages under `docs/`, the `.doc-writer/` folder, and `mkdocs.yml` if setup
created it. Preview the site:

```bash
mkdocs serve
```

Open the local URL that MkDocs prints and read the pages as your reader would. Commit the pages
you are happy with. Edit or discard the rest as you would any other change.

## What you learned

- How to install doc-writer and describe your readers as a persona during setup.
- How `/doc-writer:write` proposes a page inventory and waits for your approval.
- What the Author, Editor and Persona each do, and how FAIL verdicts trigger revision passes.
- How to accept or skip PARTIAL fixes and review the uncommitted result.

## Next steps

- [Update docs after code changes](how-to/update-docs.md): re-run the pipeline after a release.
- [Audit docs without changing them](how-to/audit.md): check your docs before you publish.
- [How the pipeline works](explanation/pipeline.md): what each stage does and why.
