---
title: Upgrade after a plugin update
description: Bring your .doc-writer files up to date with a new plugin version without losing your edits
---

# How to upgrade after a plugin update

A new doc-writer version can add config fields, improve its default guidance and rules, or ask
new setup questions. Your project's `.doc-writer/` folder doesn't change by itself when the
plugin updates. `/doc-writer:upgrade` migrates it and keeps your own edits.

## Before you start

- `.doc-writer/config.yaml` exists in the project.
- Your `.doc-writer/` folder is committed, so you can review the upgrade as a diff.

## Update the plugin

Refresh the marketplace, then update the plugin. From the terminal:

```bash
claude plugin marketplace update anentropic-for-agents
claude plugin update doc-writer@anentropic-for-agents
```

Inside a Claude Code session, run `/plugin` and update doc-writer from the installed plugins list.
Restart Claude Code so the new version loads.

## Run the upgrade

```text
/doc-writer:upgrade
```

The command compares the `plugin_version` stored in your config with the installed plugin. If
they match, it prints `doc-writer is already up to date (version 1.8.0).` and stops. Otherwise it
prints the two versions and works through four steps.

### 1. Config migration

New fields in the config schema are added to your `config.yaml`. Each gets a value inferred
from your existing settings, not an empty default. When more than one value is plausible,
you are asked to choose. Fields the plugin no longer uses are removed.

### 2. Guidance and rules merge

Your guidance file (for example `mkdocs-material.md`) and `rules.md` are compared with the new
plugin defaults:

- A file you never edited is replaced with the new default.
- A file you edited is merged one `##` section at a time. Sections only the plugin changed are
  updated, sections only you changed are kept, and sections you added are kept.
- When you and the plugin changed the same section differently, you see both versions and
  choose **Keep mine**, **Take plugin update**, or **Type something else** to write your own.

The comparison uses the copies of the old defaults in `.doc-writer/.originals/`. Projects set
up before those copies existed get a simpler comparison: every section that differs from the new
default is shown to you to keep or replace, and `.originals/` is created for next time.

### 3. New setup questions

If the new version asks framework questions your config has no answer for, such as a new
navigation option, you are asked only those. Questions you already answered are not repeated.

### 4. Context refresh

If steps 1 or 3 changed anything, the Doc Researcher regenerates `.doc-writer/context.md`.

The new `plugin_version` is written last, so an interrupted upgrade can simply be run again.

## Read the Upgrade Summary

The command ends with a summary of everything it did:

```text
## Upgrade Summary

**Version:** 1.7.0 -> 1.8.0

### Config Changes
- No config schema changes

### File Updates
- Updated rules.md to new plugin version.

### File Merges
- mkdocs-material.md: 3 sections auto-merged, 1 conflicts resolved by user

### Q&A Updates
- No new Q&A questions

### Context Refresh
- Skipped -- no config or Q&A changes to reflect

### Warnings
- None
```

## Check the result

Review the changes:

```bash
git diff .doc-writer/
```

Check any merged sections in your guidance file and `rules.md`, and the values given to new
config fields. Commit when you are satisfied.

## Troubleshooting

### "doc-writer is already up to date" right after updating

Claude Code is still running the previous plugin version. Restart Claude Code and run the
command again.

### "Config has no plugin_version field"

The project was set up before version tracking existed. The upgrade treats it as an old project
and continues; the field is added at the end.

### Your guidance file was skipped

Guidance generated for a doc system without built-in support is not a plugin default, so there
is nothing to merge it with. It is left as it is.

## Related

- [The .doc-writer folder](../reference/files.md): what `.originals/` holds.
- [Configure or reconfigure a project](configure.md): change settings after upgrading.
- [Commands reference](../reference/commands.md#upgrade): what `upgrade` reads and writes.
