# Plain Markdown Guidance

Preferences for writing documentation in standard Markdown without a specific documentation framework. These are style choices for consistency — agents already understand Markdown syntax.

## Structure

- Use ATX-style headings (`# Heading`) exclusively. Do not use setext-style (underline) headings.
- Maximum heading depth: 4 levels (`####`). If you need deeper nesting, restructure the content into separate pages or use bold text within a section.
- Leave one blank line before and after headings. This improves readability in the raw Markdown source.

## Code Blocks

- Always use fenced code blocks (triple backticks). Never use indented code blocks — they are ambiguous and harder to read in source.
- Always specify the language identifier after the opening backticks: `` ```python ``, `` ```bash ``, `` ```json ``. This enables syntax highlighting in all renderers.
- For shell commands, use `bash` or `sh` as the language. Prefix user-typed commands with `$` only when showing mixed output (command + result). For command-only blocks, omit the `$`.

## Links

- Use reference-style links `[text][ref]` for URLs that appear more than once on a page. Define references at the bottom of the page in alphabetical order.
- Use inline links `[text](url)` for one-off links that appear only once.
- For internal links between documentation pages, use relative paths: `[Setup Guide](./setup.md)`. Relative paths survive repo moves and work across different hosting platforms.

## Emphasis

- **Bold** for UI element names, important terms on first use, and key concepts being defined.
- *Italic* for book titles, document titles, and introducing new terms before their definition.
- `Inline code` for function names, parameter names, file paths, CLI commands, config keys, and any text that represents literal code or input.
- Do not combine bold and italic. Do not nest emphasis markers.

## Lists

- Use `-` (hyphen) for unordered lists. Do not use `*` or `+` — pick one marker for consistency.
- Use `1.` for all ordered list items (Markdown auto-numbers). Do not manually number items — manual numbers create merge conflicts and maintenance burden.
- Indent nested lists with 2 spaces. Keep nesting to 2 levels maximum.

## Tables

- Use tables for structured data: parameters with types and defaults, option comparisons, feature matrices.
- Align columns using spaces for readability in the raw source. Most Markdown formatters handle this automatically.
- Keep tables under 5 columns. Wider tables break on mobile and are hard to scan. If you need more columns, consider a definition list or separate subsections.

## Callouts

- Since plain Markdown has no admonition syntax, use blockquotes with bold labels for callouts:
  - `> **Note:** supplementary information`
  - `> **Warning:** things that might surprise or cause problems`
  - `> **Tip:** best practices and recommendations`
- Keep callouts to one paragraph. For longer callout content, consider making it a regular section with a descriptive heading.
- Do not stack multiple callouts back-to-back. Consolidate related warnings or notes into a single callout with a list.

## Mermaid Diagrams

GitHub renders mermaid diagrams natively in Markdown files, Issues, PRs, and wikis. Other Markdown renderers may not support mermaid.

- Use standard fenced code blocks with the `mermaid` language identifier:

  ````markdown
  ```mermaid
  flowchart LR
      A[Input] --> B{Validate}
      B -->|Valid| C[Process]
      B -->|Invalid| D[Error]
      C --> E[Output]
  ```
  ````

- Mermaid blocks render as diagrams on GitHub. On renderers without mermaid support, they appear as syntax-highlighted code blocks -- still readable, just not visual.
- Keep diagrams simple. Complex diagrams with many nodes may not render well in narrow views (mobile, GitHub PR diffs).
