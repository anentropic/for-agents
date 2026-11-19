---
title: Make targeted fixes
description: Fix selected audit findings, or a problem you describe, on only the pages involved
---

# How to make targeted fixes

When you know what is wrong, from an audit report or from reading the docs yourself, you don't
need the whole pipeline. `/doc-writer:edit` sends the Doc Author to fix only the pages involved,
then runs the Doc Editor over them.

## Before you start

- `.doc-writer/config.yaml` exists.
- To pick from findings, run `/doc-writer:review` first so that
  `.doc-writer/editor-report.md` or a persona report exists. To describe a fix yourself, no
  report is needed.

## Fix findings from a report

Run the command with no argument:

```text
/doc-writer:edit
```

The command collects every issue from the Editor and Persona reports and lists them, most
severe first:

```text
Select issues to fix from previous reports.

[BLOCKING] docs/how-to/custom-rules.md > Load rules from a file
    Example calls load_rules() with a path argument; the function takes a file object
[FAIL] docs/how-to/pandas.md
    I want to plug the cleaner into a pandas pipeline -- no DataFrame example
[SUGGESTION] docs/explanation/rules.md > Rule order
    ...
[PARTIAL] docs/tutorial.md
    ...
[NITPICK] docs/index.md > Install
    ...
```

The order is BLOCKING, FAIL, SUGGESTION, PARTIAL, NITPICK. Select the issues you want fixed, or
choose **Fix all issues**. You can also type a number selection instead: `1,3` picks the first
and third issues in the list, counting from the top, and `all` picks every issue. To describe a
different change instead, choose **Type something else**.

## Describe the fix yourself

Pass the instruction as the argument. Name the page and say what should change:

```text
/doc-writer:edit fix the installation steps in docs/tutorial.md: the package is installed with uv, not pip
```

Any argument other than a number selection (such as `1,3`) or `all` becomes the instruction,
and the selection list is skipped. Without reports, running `/doc-writer:edit` with no argument tells you none were
found and asks you to describe the change.

## Stages of an edit run

1. The **Doc Author** revises only the pages named by the selected issues or your instruction.
   It does not create pages or regenerate other pages.
2. The **Doc Editor** runs its four passes on the changed pages. Its terminology pass covers
   every page, so a corrected term is corrected everywhere.

The Doc Persona does not run. The command ends with an **Edit Complete** summary listing each
modified page and the issues addressed.

## Check the result

Review the diff before committing:

```bash
git diff docs/
```

To confirm the fixes resolved the persona's problems, run `/doc-writer:review` again.

## Troubleshooting

### The issue list is out of date

The list is built from the last reports written. Run `/doc-writer:review` to regenerate them
against the current pages.

### Pages outside the selection changed

Those are terminology corrections from the Editor's all-pages terminology pass. Each one is in
the **Terminology Changes** table of `.doc-writer/editor-report.md`.

### The earlier Editor report was replaced

Each Editor run overwrites `.doc-writer/editor-report.md`. Copy a report elsewhere first if you
want to keep its findings while you work through them.

## Related

- [Audit docs without changing them](audit.md): produce the reports this command reads.
- [Resolve PARTIAL and FAIL verdicts](resolve-verdicts.md): when to edit and when to re-run.
- [Commands reference](../reference/commands.md#edit): `edit` arguments.
