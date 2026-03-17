# MkDocs Material Q&A

Framework-specific questions for mkdocs-material setup.
Presented during /doc-writer:setup after doc system selection.
Auto-detect: check for mkdocs.yml in project root.

## Detection

Config file: mkdocs.yml
Features to detect:
- navigation.sections, navigation.tabs (theme.features)
- pymdownx.tabbed (markdown_extensions)
- pymdownx.superfences with mermaid fence (markdown_extensions)
- admonition (markdown_extensions)
- pymdownx.details (markdown_extensions)
- content.code.annotate (theme.features)
- mkdocstrings (plugins)
- literate-nav (plugins)

## Question 1: Navigation style

- header: "Navigation"
- question: "How should documentation be organized?"
- detect_context: "Detected: {detected features from mkdocs.yml}"
- options:
  - { label: "Sections", description: "2-level nav: sections group related pages (navigation.sections)", recommend_if: "navigation.sections detected" }
  - { label: "Tabs + sections", description: "Top-level tabs with sections underneath (navigation.tabs)", recommend_if: "navigation.tabs detected" }
  - { label: "Flat", description: "All pages at one level, no grouping" }
  - { label: "Type something else", description: "Describe a different nav structure" }
  - { label: "Chat about this", description: "Discuss navigation options" }

## Question 2: API reference approach

- header: "API docs"
- question: "How is API reference generated?"
- detect_context: "Detected: mkdocstrings with {docstring_style}"
- options:
  - { label: "mkdocstrings", description: "Auto-generated from docstrings", recommend_if: "mkdocstrings detected" }
  - { label: "Manual pages", description: "Hand-written API reference in docs/" }
  - { label: "None", description: "No API reference -- narrative docs only" }
  - { label: "Type something else", description: "Describe a different approach" }
  - { label: "Chat about this", description: "Discuss API reference options" }

## Question 3: Rich features usage

- header: "Features"
- question: "Which MkDocs Material features should docs use?"
- multiSelect: true
- detect_context: "Detected: {detected list}"
- options:
  - { label: "Content tabs", description: "For multi-language or multi-method examples (pymdownx.tabbed)", recommend_if: "pymdownx.tabbed detected" }
  - { label: "Mermaid diagrams", description: "For architecture and flow diagrams (pymdownx.superfences)", recommend_if: "mermaid fence detected" }
  - { label: "Code annotations", description: "Numbered annotations explaining code lines (content.code.annotate)", recommend_if: "content.code.annotate detected" }
  - { label: "Admonitions", description: "Tip/warning/info callout boxes (admonition)", recommend_if: "admonition detected" }
  - { label: "Collapsible details", description: "Expandable sections for optional content (pymdownx.details)", recommend_if: "pymdownx.details detected" }
  - { label: "Type something else", description: "Add or remove features" }
  - { label: "Chat about this", description: "See examples of each feature" }
