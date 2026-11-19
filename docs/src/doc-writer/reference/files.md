---
title: The .doc-writer folder
description: Every file doc-writer keeps in .doc-writer/, who writes it, when it is replaced, and whether your edits survive
---

# The .doc-writer folder

doc-writer keeps its per-project state in a `.doc-writer/` folder at your project root. Some
files are settings you own and edit; most other files are reports that each run overwrites. Commit the
settings files so collaborators share them.

## Settings you own

Edit these freely. doc-writer reads them on every run.

| File | Written by | Your edits |
|------|------------|------------|
| `config.yaml` | Setup; changed by the setup menu and by upgrade | Kept. Upgrade adds and removes fields but keeps your values. See [config.yaml](configuration.md) |
| `rules.md` | Setup, from the default template | Kept by upgrade, which merges section by section. Replaced by `setup --reset` |
| `{doc_system}.md` | Setup, from the default guidance for your doc system, for example `mkdocs-material.md` | Same as `rules.md` |
| `terminology.yaml` | The Doc Editor, on its first run; updated on every run | Kept. Entries under `overrides` always win |
| `context.md` | The Doc Researcher | **Lost** whenever it is regenerated: by setup, `--reset`, `--refresh-context`, **Re-run researcher**, or an upgrade that changes the config |

!!! warning "context.md is regenerated"

    `context.md` is the researcher's expansion of `config.yaml`: persona guidance, tone rules
    and doc-system preferences, in detail. Hand edits work until the next regeneration. For a
    lasting change, edit `config.yaml` and run `/doc-writer:setup --refresh-context`, or add a
    rule to `rules.md`.

## Reports and working files

doc-writer writes these during a run. Read them; editing them has no lasting effect, because the
next run overwrites them.

| File | Written by | Contents |
|------|------------|----------|
| `gap-report.md` | `write` and `review` (gap detection) | Exported symbols with no documentation, and in update mode the pages that may be stale |
| `page-inventory.md` | `write` (Author plan) | The proposed pages: type, title, key sections, file path |
| `editor-report.md` | Every Editor run | Findings per page by severity (BLOCKING, SUGGESTION, NITPICK), terminology changes, deslop measurements |
| `persona-report.md` | The Doc Persona, with one persona | Each scenario's verdict, navigation path and suggested fixes |
| `persona-report-{persona-name}.md` | The Doc Persona, one per persona | The same, for each of several personas. `review` also writes it with one persona |
| `scenarios.yaml` | The Doc Persona, on its first run | The goals each persona tests. Reused on later runs until the page set changes substantially |
| `author-notes.md` | The Doc Author, `odoc` projects only | The Author's notes for the Editor, which other doc systems keep as hidden comments in the pages |
| `mli-enrichment.md` | The Doc Author, `odoc` projects only | Proposed doc comments for undocumented `.mli` values, for you to apply by hand |

`scenarios.yaml` is the one working file whose removal changes behavior: delete it to make the
Persona generate fresh scenarios on the next run.

## Internal folders

| Folder | Purpose |
|--------|---------|
| `.originals/` | Copies of the plugin's default `rules.md` and guidance file as they were at setup or the last upgrade. `/doc-writer:upgrade` compares against them to tell your edits from plugin changes. Don't edit or delete it |
| `.deslop/` | Temporary snapshots the Editor's prose scanner compares against. Cleared at the end of each Editor run |

## Files for unsupported doc systems

When you name a doc system without built-in support, setup may also create:

| File | Contents |
|------|----------|
| `{doc_system}.qa.md` | The framework questions generated for that system |
| `scaffolds/` | A starter config file for that system |

These exist only when the generated files could not be saved inside the plugin. You can edit
them; upgrades leave them alone.

## See also

- [config.yaml](configuration.md): every configuration field.
- [Add project rules and terminology](../how-to/project-rules.md): editing `rules.md` and
  `terminology.yaml`.
- [Upgrade after a plugin update](../how-to/upgrade.md): how `.originals/` is used.
