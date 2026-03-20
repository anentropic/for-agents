# MkDocs Material Guidance

Opinionated preferences for writing documentation with MkDocs Material. These are style preferences — agents already understand MkDocs Material syntax. This file guides how features should be used, not what they are.

## Admonitions

- Prefer admonition blocks over bold text for callouts. Bold text in paragraphs gets lost; admonitions create visual hierarchy that readers scan.
- Use specific admonition types instead of generic `!!! note`:
  - `!!! tip` for best practices and recommended approaches
  - `!!! warning` for gotchas, common mistakes, and things that might surprise
  - `!!! danger` for breaking changes, security concerns, and data loss risks
  - `!!! info` for supplementary context that enriches understanding
  - `!!! example` for extended examples that would disrupt the flow if inline
- Use collapsible admonitions (`??? note "Title"`) for optional or advanced details that most readers can skip. This keeps the main content focused.
- Do not stack multiple admonitions back-to-back. If you need three warnings in a row, consolidate into one admonition with a list.

## Code Blocks

- Always specify the programming language on fenced code blocks. Never use bare triple backticks.
- Use line highlighting (`hl_lines="3 4"`) to draw attention to the important lines in longer examples. Do not highlight everything — highlight only the lines that are new or critical.
- Use code annotations for complex examples where inline comments would be too noisy. Annotations provide explanation without cluttering the code.
- Prefer tabbed multi-language examples (using content tabs) over separate consecutive code blocks when showing the same concept in multiple languages.
- Use the `title` attribute on code blocks to label file paths: `` ```python title="src/main.py" `` `.

## Content Tabs

- Use content tabs when showing the same concept in multiple languages, frameworks, or installation methods. Tabs keep alternatives side-by-side without page bloat.
- Keep tab labels short and consistent: "Python", "JavaScript", "Rust" — not "Python Example Code" or "Using Python".
- Group related alternatives: install methods (pip/conda/docker), OS-specific instructions (macOS/Linux/Windows), sync/async patterns.
- Do not use tabs for unrelated content. If the tabs show different concepts rather than different expressions of the same concept, use separate sections instead.

## Navigation

### Top-level tabs

- Enable top nav tabs (`navigation.tabs`) for projects following the Diataxis structure. The standard tab set is: Home, Tutorials, How-To Guides, Explanation, Reference. Each tab maps to one Diataxis quadrant; Home is the landing page.
- Disable tabs for simple projects where all sections have only 1–2 pages each. At that scale, tabs add overhead without aiding navigation — a single sidebar works better.
- Tabs are a separate root layer above the left nav, not a nav level. With tabs enabled, the left sidebar shows the contents of the active tab only.

### Left nav depth

- Keep left nav depth to 3 levels maximum (section heading → page → sub-page). Deeper nesting makes content hard to find and creates narrow, scrolling nav panels.
- Level 1: section heading (e.g., "Authentication"). Level 2: page link (e.g., "OAuth setup"). Level 3: child page link as a submenu entry. Avoid Level 4.
- Group related pages under a single section. Prefer fewer sections with more pages over many sections with 1–2 pages each.
- Use `index.md` pages for section landing pages. These should provide an overview of what the section contains and guide readers to the right page.

## Frontmatter

- Every page needs `title` and `description` fields. The title appears in the browser tab and search results; the description appears in search snippets and link previews.
- Tutorials should include a `difficulty` field (beginner, intermediate, advanced) to help readers self-select appropriate content.
- Use `tags` for cross-cutting concerns that span sections (e.g., `tags: [authentication, security]`).

## Cross-References

- Use reference-style links `[text][reference]` for internal links that appear in multiple places. Define references at the bottom of the page.
- Inline code mentions of functions, classes, and config keys should link to their API Reference page: `` [`connect()`](../reference/client.md#connect) ``.
- Prefer relative paths for internal links. Absolute paths break when the site root changes.
