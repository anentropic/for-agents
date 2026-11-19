---
title: Commands
description: Every doc-writer command with its arguments, prerequisites, files read and written, and side effects
---

# Commands

doc-writer adds five slash commands to Claude Code. None of them commits anything: every change
is left in your working tree.

| Command | Purpose |
|---------|---------|
| [`/doc-writer:setup`](#setup) | Configure doc-writer for a project |
| [`/doc-writer:write`](#write) | Generate docs, or update them after code changes |
| [`/doc-writer:review`](#review) | Audit docs; read-only unless `--edit` is passed |
| [`/doc-writer:edit`](#edit) | Fix selected findings or a described problem |
| [`/doc-writer:upgrade`](#upgrade) | Migrate `.doc-writer/` after a plugin update |

Interactive commands ask multiple-choice questions. Every question also offers
**Type something else** (answer in your own words) and **Chat about this** (discuss the question,
then answer it).

## /doc-writer:setup {#setup}

Creates or updates the project configuration in `.doc-writer/`.

```text
/doc-writer:setup [--reset] [--refresh-context]
```

| Argument | Effect |
|----------|--------|
| *(none)* | With no config: the full first-time question flow. With a config: a menu to change one area |
| `--reset` | After confirmation, runs the full question flow and replaces the existing files |
| `--refresh-context` | Skips all questions and regenerates `context.md`. Needs an existing `config.yaml` |

**Prerequisites:** none.

**Question flow (first time and `--reset`):** use cases, user personas, tone, doc system,
scaffold check, framework questions, paths.

**Update menu:** User Personas, Tone, Use Cases, Doc system, Paths, Re-run researcher, Done.

**Reads:** your README, package manifest, source and doc-system config file, for detection and
for the researcher.

**Writes:**

| File | When |
|------|------|
| `.doc-writer/config.yaml` | First time, `--reset`, and after each menu change |
| `.doc-writer/{doc_system}.md` | First time, `--reset`, and when the doc system changes |
| `.doc-writer/rules.md` | First time and `--reset` |
| `.doc-writer/.originals/` | First time and `--reset` |
| `.doc-writer/context.md` | First time, `--reset`, `--refresh-context`, **Re-run researcher** |
| Doc-system config file, such as `mkdocs.yml` | Only if missing; additions to an existing one only after you confirm each |
| `{docs_root}/index.md` | A starter page, only if the docs root did not exist and a config file was scaffolded |

**Side effects:** install commands for the doc system are shown, never run. Choosing a doc system
with no built-in support starts research that writes a guidance file and question set for it.

## /doc-writer:write {#write}

Runs the full pipeline: gap detection, page plan, your approval, writing, editing and persona
evaluation, with up to three revision passes.

```text
/doc-writer:write [--skip-gap-scan]
```

| Argument | Effect |
|----------|--------|
| *(none)* | Runs gap detection first |
| `--skip-gap-scan` | Skips gap detection; the pipeline starts at the page plan |

**Prerequisites:** `.doc-writer/config.yaml`.

**Mode** is detected from the pages in `paths.docs_root`:

| Mode | When | What it produces |
|------|------|------------------|
| Create | No pages, or only a starter `index.md` | A full page set |
| Update | Two or more pages | Pages for undocumented symbols, and in-place refreshes of stale pages |

**Stages:**

| Stage | Output |
|-------|--------|
| Gap detection | `.doc-writer/gap-report.md` |
| Author plan | `.doc-writer/page-inventory.md` |
| Page inventory approval | Your selection of pages |
| Author write | New and refreshed pages in `paths.docs_root` |
| Editor | Edited pages; `.doc-writer/editor-report.md`; `.doc-writer/terminology.yaml` |
| Persona | `.doc-writer/scenarios.yaml`; `.doc-writer/persona-report.md` (one persona) or `persona-report-{persona-name}.md` (each of several) |
| Verdict check | FAIL: revision pass, up to 3 passes in total. PARTIAL: your approval. FAILs left after pass 3: escalation report |
| Summary | Printed **Documentation Pipeline Complete** report |

**Side effects:** with `doc_system: odoc`, also writes `.doc-writer/author-notes.md` and may write
`.doc-writer/mli-enrichment.md` with proposed `.mli` doc comments; `.mli` files are never
changed. In update mode, pages the run did not create or refresh are never revised; FAILs on them
are escalated.

## /doc-writer:review {#review}

Audits existing docs: gap detection, an Editor audit and persona evaluation, then a combined
summary. No revision loop.

```text
/doc-writer:review [--edit]
```

| Argument | Effect |
|----------|--------|
| *(none)* | Report-only. No documentation file is changed |
| `--edit` | After you confirm, the Editor fixes the issues it finds in the pages |

With `--edit`, the confirmation offers **Apply edits**, **Report only** (skip the Editor) and
**Type something else** (limit the files).

**Prerequisites:** `.doc-writer/config.yaml`, and at least one `.md` page in `paths.docs_root`.

**Writes:** `.doc-writer/gap-report.md`, `.doc-writer/editor-report.md`,
`.doc-writer/persona-report-{persona-name}.md` for each persona (plus `persona-report.md` when
there is one persona), `.doc-writer/scenarios.yaml`. Pages change only with `--edit`.

## /doc-writer:edit {#edit}

Revises only the pages affected by selected findings or a described change, then edits them.

```text
/doc-writer:edit [issue description or page path]
```

| Argument | Effect |
|----------|--------|
| *(none)* | Lists issues from the Editor and Persona reports for you to select. With no reports, asks you to describe the change |
| Text | Used as the instruction; the selection list is skipped |

Issues are listed in the order BLOCKING, FAIL, SUGGESTION, PARTIAL, NITPICK, with a
**Fix all issues** option.

**Prerequisites:** `.doc-writer/config.yaml`. Reports from `/doc-writer:review` or
`/doc-writer:write` to select from, if you don't pass text.

**Stages:** Doc Author (affected pages only; no new pages), then Doc Editor (four passes on the
changed pages, terminology across all pages). The Doc Persona does not run.

**Writes:** the affected pages, `.doc-writer/editor-report.md`, `.doc-writer/terminology.yaml`.

## /doc-writer:upgrade {#upgrade}

Migrates the project's `.doc-writer/` folder to the installed plugin version.

```text
/doc-writer:upgrade
```

Takes no arguments.

**Prerequisites:** `.doc-writer/config.yaml`.

**Steps:** version check (stops if already current), config field migration, section-level merge
of the guidance file and `rules.md`, questions for any new framework settings, `context.md`
refresh when the config changed, then `plugin_version` is updated.

**Writes:** `.doc-writer/config.yaml`, `.doc-writer/{doc_system}.md`, `.doc-writer/rules.md`,
`.doc-writer/.originals/`, and `.doc-writer/context.md` when a refresh is needed.

**Side effects:** prints an **Upgrade Summary**. Merge conflicts are resolved one section at a
time with your input.

## See also

- [config.yaml](configuration.md): the fields these commands read and write.
- [The .doc-writer folder](files.md): every file listed above.
- [How the pipeline works](../explanation/pipeline.md): why the stages run in this order.
