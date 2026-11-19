---
title: Audit docs without changing them
description: Get coverage, quality and persona findings for existing docs, and optionally let the Editor apply its fixes
---

# How to audit docs without changing them

Before a release, you may want to know whether your docs are good enough without letting a tool
rewrite them. `/doc-writer:review` checks coverage, prose quality and whether a reader can
complete real tasks, and by default changes no documentation file.

## Before you start

- `.doc-writer/config.yaml` exists. Run `/doc-writer:setup` if it does not.
- `paths.docs_root` contains your documentation pages. The pages do not need to have been
  written by doc-writer.

## Run the audit

```text
/doc-writer:review
```

The audit runs three stages in order:

1. **Gap detection** lists exported symbols that no page mentions and writes
   `.doc-writer/gap-report.md`.
2. **Editor audit** runs the Doc Editor's four passes (terminology, page-type integrity,
   humanizer and cross-references) in report-only mode, and writes its findings to
   `.doc-writer/editor-report.md`.
3. **Persona evaluation** runs one Doc Persona per configured persona. Each tries its scenarios
   against your docs and writes a report.

The audit does not loop: no pages are revised, whatever the verdicts.

## Read the summary

When the audit finishes it prints a combined summary:

```text
## Documentation Audit Summary

### Gap Detection
- **Total exported symbols:** 42
- **Documented:** 37 (88%)
- **Undocumented:** 5
- Key undocumented symbols: normalize_unicode, merge_rules, ...

### Editor Findings
- **BLOCKING issues:** 1
- **SUGGESTION issues:** 9
- **NITPICK issues:** 4
- Top issues: ...

Note: Editor ran in report-only mode. Run `/doc-writer:review --edit` to apply fixes.

### Persona Verdicts

**Python developers who clean text data** (intermediate):
| Scenario | Verdict | Notes |
|----------|---------|-------|
| I want to clean a batch of strings | PASS | ... |
| I want to load custom rules from a file | PARTIAL | ... |
...
```

Start with BLOCKING findings and FAIL verdicts: these are the issues that stop a reader or put
wrong information in front of them. The details are in the report files:

| File | What to look for |
|------|------------------|
| `.doc-writer/gap-report.md` | The table of undocumented exports, with source file and symbol type |
| `.doc-writer/editor-report.md` | Findings per page, grouped by severity, with the exact fix for each |
| `.doc-writer/persona-report-{persona-name}.md` | Each scenario's navigation path, verdict and suggested fix |

`review` writes one persona report per configured persona. The file name is the persona's name
in lower case with spaces replaced by hyphens, so the persona "Python developers who clean text
data" writes `persona-report-python-developers-who-clean-text-data.md`. With one persona,
the same report is also written to `.doc-writer/persona-report.md`.

## Apply the Editor's fixes

To let the Editor fix what it finds, run the audit with `--edit`:

```text
/doc-writer:review --edit
```

Before the Editor runs, you are shown the files in your docs root and asked to confirm:

- **Apply edits** lets the Editor rewrite the pages.
- **Report only** skips the Editor for this run.
- **Type something else** lets you name the files the Editor may change.

!!! warning "Manual edits can be overwritten"

    With **Apply edits**, the Editor rewrites wording on any page it finds an issue in. Commit or
    stash your own work first, so you can tell its changes apart in the diff.

`--edit` applies only the Editor's fixes. It does not act on gap findings or persona verdicts.

## Check the result

In report-only mode, `git status` should show changes only inside `.doc-writer/`. After
`--edit`, review the page changes:

```bash
git diff docs/
```

## Troubleshooting

### "No documentation files found"

The audit reads Markdown pages from `paths.docs_root`. Check that the docs root in
`.doc-writer/config.yaml` points at your pages, or run `/doc-writer:write` to create some.

### Gap detection reports symbols you don't consider public

Gap detection uses each language's export conventions, such as names without a leading
underscore in Python. Document the symbols, or ignore those lines: the audit takes no action on
them.

## Related

- [Make targeted fixes](targeted-fixes.md): act on selected findings from these reports.
- [Commands reference](../reference/commands.md#review): `review` arguments and outputs.
- [Quality rules and the humanizer pass](../explanation/quality.md): what the Editor checks.
