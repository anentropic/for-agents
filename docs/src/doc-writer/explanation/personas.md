---
title: Personas and verdicts
description: What a persona is, how the Doc Persona turns it into test scenarios, and what PASS, PARTIAL and FAIL mean
---

# Personas and verdicts

doc-writer judges your docs by whether a particular reader can use them, not by a checklist.
This page explains what a persona is, how the Doc Persona turns one into concrete tests, and how
it decides between PASS, PARTIAL and FAIL.

## Personas

A **persona** is a profile of one kind of reader, stored in `config.yaml` under
`user_personas`. It records how experienced the reader is (`skill_level`), what they already
know (`assumed_knowledge`), what must always be explained to them (`never_assume`), and what
they want to do with your library (`user_tasks`). Optional fields describe their domain and how
they found the library.

Two agents use the persona differently:

- The **Doc Author** and **Doc Editor** use it to set vocabulary and depth: what to explain, what
  to take as known.
- The **Doc Persona** becomes that reader and tries to use the docs.

Most projects need one persona. Add a second only for an audience with different needs, such as
application developers and plugin authors. Each persona gets its own scenarios and its own
verdicts, and a PASS for one never cancels a FAIL for another.

## From persona to scenarios

On its first run the Persona writes 3 to 5 **scenarios**, each a concrete goal phrased in the
reader's words, with a definition of done:

```yaml title=".doc-writer/scenarios.yaml (excerpt)"
user_personas:
  - name: "Python developers who clean text data"
    skill_level: "intermediate"
    scenarios:
      - id: S2
        goal: "I want to load my own cleaning rules from a file"
        starting_point: "docs/index.md"
        persona_relevance: "Teams keep house rules in version control"
        done_when: "I have a rule file in the right format and the cleaner applies it"
```

The goals come mostly from `user_tasks` and `discovery_story`, filtered by skill level. A
beginner persona gets installation and first-use goals. An intermediate persona gets everyday
tasks and configuration. An advanced persona gets edge cases, extension points and tuning.

Scenarios are saved in `.doc-writer/scenarios.yaml` and reused:

- **On revision passes, always.** The point of a revision pass is to fix the gaps the scenarios
  found, so the scenarios must not change underneath it.
- **On later runs, while the page list is unchanged.** `scenarios.yaml` stores the file names
  of the doc pages that existed when the scenarios were written. On a fresh run the Persona
  compares the current file names with that list. If the names match and the page count has moved
  by no more than about 30 percent, it reuses the scenarios. Adding or removing even one page,
  or a major restructuring, makes it write new scenarios.

Because the scenarios stay fixed, verdicts from one run can be compared with the next.

## Navigating the docs as a reader

For each scenario, the Persona starts at the docs home page (your project README if there is one,
otherwise the index page in your docs root) and moves the way a reader would: it follows links,
reads headings and checks the code examples. It may read only the documentation pages, the
README, `config.yaml`, `context.md` and its own scenarios. Your source code, tests and the
Editor's reports are off limits, and it cannot search all pages at once.

A maintainer reviewing their own docs fills every gap from memory.
The Persona has nothing to fill gaps with, so a missing step or a dead-end link stops it the way
it would stop a reader. Its report records the path it took, page by page, so you can see where
it went wrong.

## Verdicts

| Verdict | Meaning | What happens next |
|---------|---------|-------------------|
| **PASS** | The reader reaches the goal from start to finish, without significant friction | Nothing |
| **PARTIAL** | The reader gets there, but with friction: hard-to-find content, unclear steps, an incomplete example, or the right information in the wrong kind of page | The suggested fix is offered to you |
| **FAIL** | The reader cannot reach the goal: content is missing, wrong, contradictory or leads nowhere | The Author revises the page, if passes remain |

The Persona's test for the boundary: a determined reader who could work it out from what is
there is PARTIAL; if the information is missing or critically wrong, it is FAIL.

A PARTIAL can come from the page type, not just the content. A beginner who lands on a how-to
guide that assumes the basics, or a working developer who has to read through a tutorial to find
one command, has the right information in the wrong form. The fix is usually a cross-link to the
right kind of page.

## PARTIAL verdicts wait for you

Only FAIL starts an automatic revision. Revising for every PARTIAL would rewrite pages over small
problems and can make them worse. You know your readers better than the pipeline does, so PARTIAL
fixes are presented as suggestions, each tied to a page and section, for you to accept or skip.

## Related

- [Resolve PARTIAL and FAIL verdicts](../how-to/resolve-verdicts.md): what to do with each
  verdict.
- [How the pipeline works](pipeline.md#the-revision-loop): how verdicts drive the revision loop.
- [config.yaml](../reference/configuration.md#user_personas): the persona fields.
