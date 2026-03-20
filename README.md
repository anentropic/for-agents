# anentropic/for-agents

A collection of Claude Code plugins for working with AI-assisted development.

[Full Documentation](./docs/)

## Plugins

### `doc-writer`

Writes and reviews library documentation to publication quality using a three-agent pipeline (Author, Editor, User Persona). Solves the perspective problem: agents that build features tend to document from the builder's viewpoint. This plugin produces docs written from the end user's perspective.

[doc-writer documentation](./docs/doc-writer.md)

### `copilot-review`

Runs a multi-dimensional code review by decomposing into six focused sub-reviews (architecture, test coverage, code quality, error handling, dependency audit, reinvented wheels), getting a second opinion from GitHub Copilot CLI on each dimension, then consolidating findings into prioritised action items.

[copilot-review documentation](./docs/copilot-review.md)

## Installation

Install both plugins via the Claude Code marketplace:

```
/plugin install github:anentropic/for-agents
```

Install individual plugins by name once they appear in the marketplace search results.

## License

MIT
