---
title: Update docs after code changes
description: Re-run the pipeline to document new symbols and refresh pages whose source has changed
---

# How to update docs after code changes

After a release adds functions or changes behavior, some symbols have no docs and some pages
describe old behavior. Re-running `/doc-writer:write` on a project that already has docs finds
both and fixes only those pages.

## Before you start

- `.doc-writer/config.yaml` exists. Run `/doc-writer:setup` if it does not.
- Your docs root already contains at least two documentation pages. With none, or only a
  starter `index.md`, the pipeline treats the project as undocumented and runs in create mode.
- Your project is a git repository with the code changes committed. Stale-page detection
  compares git commit dates.

## Run the pipeline

```text
/doc-writer:write
```

The pipeline detects your existing pages and switches to update mode:

```text
Existing documentation detected (14 pages in docs/). Running incremental update — checking for new features and stale content.
```

## Read the gap report

Gap detection writes `.doc-writer/gap-report.md` and prints a one-line summary:

```text
6 undocumented exported symbols found across 3 modules. 4 existing pages may have stale content.
```

The report has two sections:

- **Undocumented Symbols**: exported functions, classes, constants and types that no page
  mentions, grouped by source file.
- **Potentially Stale Pages**: pages whose last commit is older than the last commit to your
  source root, with both dates.

The stale-page check is deliberately coarse. Any commit to the source root flags every page
older than it, so expect false positives. The Doc Author checks each flagged page against the
current code before proposing a change.

If both lists are empty, the pipeline asks whether you want any new pages. Choose
**Quality pass only** to skip the Doc Author and have the Doc Editor go over all your existing
pages before the Doc Persona evaluates them. Choose **Add pages** to describe pages you want,
such as a guide to a workflow that is not tied to one symbol. The Author then plans them for
your approval as described below.

## Approve new and refreshed pages

The Author proposes two kinds of entries:

- **New pages** for undocumented symbols. Existing features are not proposed again.
- **Refresh entries**, marked with ↻, for flagged pages that really are out of date. Each one
  names the discrepancies, such as a renamed parameter or an outdated example.

A flagged page that turned out to be accurate appears as **↻ {title} ✓ current** and is
deselected, so it is left alone unless you select it.

Deselect anything you don't want and confirm. The Author writes the new pages and updates the
refreshed ones in place, changing only the stale parts and keeping their structure and tone.

To add a page the Author did not propose, such as a guide to a workflow that is not tied to a new
symbol, choose **Type something else** and describe it. The updated list is shown again for you
to confirm.

## Let the pipeline finish

The Editor runs all its passes on the new and refreshed pages, plus a terminology pass across
every page, since a renamed term can affect any of them. The Doc Persona then evaluates the
whole docs set.

FAIL verdicts on new or refreshed pages go back to the Author for revision, as in create mode.
A FAIL on a page this run did not touch is not revised: it is listed in the escalation report
for you to handle. See [Resolve PARTIAL and FAIL verdicts](resolve-verdicts.md).

## Skip gap detection

When you have only edited docs by hand and the code has not changed, skip the scan:

```text
/doc-writer:write --skip-gap-scan
```

The pipeline goes straight to the Author's plan. The existing `gap-report.md` is not rewritten.

## Check the result

The summary's **Pipeline Mode** line reports how many pages were added and refreshed. Review
the changes before committing:

```bash
git diff docs/
git status docs/
```

`git status` lists the new pages; `git diff` shows the edits to refreshed ones.

## Troubleshooting

### The pipeline runs in create mode on a documented project

Update mode needs at least two pages in `paths.docs_root`. Check that the docs root in
`.doc-writer/config.yaml` points to the folder holding your pages, for example `docs/src/`
rather than `docs/`.

### Every page is flagged as stale

Any commit under the source root makes older pages look stale. The Author's check filters
these out; approve only the refresh entries that list real discrepancies.

### A page you did not approve was changed

The Editor's terminology pass runs across all pages. Its changes are listed in the
**Terminology Changes** table of `.doc-writer/editor-report.md`.

## Related

- [Commands reference](../reference/commands.md#write): all `write` arguments and outputs.
- [How the pipeline works](../explanation/pipeline.md): create mode and update mode side by side.
- [Make targeted fixes](targeted-fixes.md): change one page without re-running the pipeline.
