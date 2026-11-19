# for-agents

Claude Code plugins for AI-assisted development.

**Documentation:** https://anentropic.github.io/for-agents/

## Plugins

### doc-writer

Writes and reviews library documentation with a pipeline of agents: an Author drafts pages,
an Editor checks terminology, structure and prose, and a Persona tries to complete real tasks
using only the docs. Because the Persona never reads the source code, it catches the gaps that
builders don't see in their own docs.

## Installation

Add this repository as a Claude Code plugin marketplace, then install the plugin from it.
In a Claude Code session:

```
/plugin marketplace add anentropic/for-agents
/plugin install doc-writer@anentropic-for-agents
```

Or from the terminal:

```bash
claude plugin marketplace add anentropic/for-agents
claude plugin install doc-writer@anentropic-for-agents
```

Restart Claude Code afterwards so the plugin loads.

## Building the docs

```bash
uv sync --group docs
uv run mkdocs serve
```

## License

MIT
