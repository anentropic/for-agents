---
title: Overview
description: Claude Code plugins for AI-assisted development
---

# for-agents

Claude Code plugins for AI-assisted development.

## Plugins

### doc-writer

Writes and reviews library documentation with a pipeline of agents: the Doc Author drafts
pages, the Doc Editor checks terminology, structure and prose, and the Doc Persona tries to
complete real tasks using only the docs. Because the Doc Persona never reads the source code, it
catches the gaps that builders don't see in their own docs.

[doc-writer documentation](doc-writer/index.md)

## Installation

Install the plugins with Claude Code's plugin manager. First add this repository as a plugin
marketplace, then install a plugin from it. You can do this inside a Claude Code session or from
your terminal.

=== "In a Claude Code session"

    ```text
    /plugin marketplace add anentropic/for-agents
    /plugin install doc-writer@anentropic-for-agents
    ```

=== "From the terminal"

    ```bash
    claude plugin marketplace add anentropic/for-agents
    claude plugin install doc-writer@anentropic-for-agents
    ```

Both install the plugin for your user, so it is available in every project. To share it with
everyone who works on one repository, add `--scope project` to the terminal command. This records
the plugin in that repository's `.claude/settings.json`.

Restart Claude Code after installing so the plugin loads.
