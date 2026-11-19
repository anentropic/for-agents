---
title: Resolve PARTIAL and FAIL verdicts
description: Decide which persona fixes to apply at the end of a pipeline run and deal with failures that did not converge
---

# How to resolve PARTIAL and FAIL verdicts

At the end of `/doc-writer:write`, the Doc Persona's verdicts decide what happens next. FAIL
verdicts are revised automatically; PARTIAL verdicts wait for you. This guide covers both
decision points: choosing PARTIAL fixes, and handling FAILs that remain after three passes.

## Before you start

- You are running `/doc-writer:write`, and the pipeline has reached the end of a Persona
  evaluation.
- You know what the verdicts mean: PASS is "the reader reached the goal", PARTIAL is "reached it
  with friction", FAIL is "could not reach it". See
  [Personas and verdicts](../explanation/personas.md) for the full criteria.

## Choose which PARTIAL fixes to apply

If any scenario ended PARTIAL, the pipeline lists the Persona's suggested fixes, each labelled
with its page and section:

```text
Select PARTIAL fixes to apply, or choose an action below.

[1] docs/how-to/custom-rules.md > Load rules from a file
    Show the expected file format before the loading example
[2] docs/tutorial.md > Install
    Mention that the package needs Python 3.10 or later
```

For each one, ask whether a real reader would hit that friction. Then:

- Select the individual fixes you agree with and confirm.
- Choose **Apply all fixes** to accept every suggestion.
- Choose **Skip all fixes** to leave the pages as they are.
- Choose **Type something else** to describe additional changes, which are applied directly to
  the pages.
- Choose **Chat about this** to discuss what each fix would change before deciding.

Approved fixes are written straight to the pages. They do not trigger another Author, Editor or
Persona pass, so check them in the diff.

!!! tip "Skipped fixes are not lost"

    The suggestions stay in `.doc-writer/persona-report.md` until the next run overwrites it.
    You can apply any of them later with `/doc-writer:edit`.

## Handle FAILs that did not converge

A FAIL sends the pages responsible back to the Author, then through the Editor and Persona
again, for up to three passes. If FAILs remain after the third pass, the pipeline stops revising
and prints an escalation report:

```text
## Escalation: Non-Converging Issues

After 3 passes, the following issues could not be resolved automatically:

### Remaining FAILs

- **Audience:** Python developers who clean text data
- **Scenario:** S3 -- I want to plug the cleaner into a pandas pipeline
- **Page:** docs/how-to/pandas.md
- **Issue:** ...
- **Attempts:** ...
```

In update mode, a FAIL on a page the run did not create or refresh goes straight into this
report without any revision attempts, because the update pipeline never rewrites pages it did
not touch.

Work through each remaining FAIL:

1. Read the **Issue** and **Attempts** lines, and the scenario's navigation path in
   `.doc-writer/persona-report.md`.
2. Decide what kind of problem it is:
    - **Missing content**: the docs have no page or section for the goal. If a section on an
      existing page would cover it, add one with `/doc-writer:edit`; that command does not
      create pages. For a new page, re-run `/doc-writer:write` and ask
      for it: choose **Type something else** at the page inventory approval, or **Add pages**
      if gap detection found nothing, and describe the page. Update mode proposes new pages
      only for undocumented symbols, so a page for a workflow is not offered unless you ask
      for it.
    - **Wrong or contradictory content**: fix the page with `/doc-writer:edit`, quoting the
      issue.
    - **A miscalibrated persona**: the scenario expects knowledge your readers would not need,
      or the persona's skill level is wrong. Adjust the persona with `/doc-writer:setup`.
3. Run the fix:

    ```text
    /doc-writer:edit docs/how-to/pandas.md: add a complete example that applies the cleaner to a DataFrame column
    ```

## Check the result

Run an audit to re-evaluate every scenario against the fixed pages:

```text
/doc-writer:review
```

If your fix only changed existing pages, the Persona reuses the scenarios in
`.doc-writer/scenarios.yaml`, so the verdicts are directly comparable with the previous run. A
fix that added a page changes the page list, so the Persona writes new scenarios. See
[Personas and verdicts](../explanation/personas.md#from-persona-to-scenarios).

## Troubleshooting

### The same scenario fails on every pass

The fix usually needs content the Author cannot produce from the code alone, such as a
recommended workflow or an integration with another tool. Write that section yourself, or give
`/doc-writer:edit` the specifics.

### A scenario asks for something your library does not do

The Persona built the scenario from the persona's tasks. Remove or reword the task with
`/doc-writer:setup`, choosing **User Personas**. Delete `.doc-writer/scenarios.yaml` so the next
run generates new scenarios.

## Related

- [Personas and verdicts](../explanation/personas.md): how scenarios and verdicts are produced.
- [Make targeted fixes](targeted-fixes.md): the `edit` workflow in detail.
- [How the pipeline works](../explanation/pipeline.md#the-revision-loop): the revision loop.
