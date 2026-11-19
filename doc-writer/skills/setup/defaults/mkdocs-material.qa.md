# MkDocs Material Q&A

Framework-specific questions for mkdocs-material setup.
Presented during /doc-writer:setup after doc system selection.
Auto-detect: check for mkdocs.yml in project root.

## Detection

Config file: mkdocs.yml, mkdocs.yaml
Features to detect:
- navigation.sections, navigation.tabs (theme.features)
- pymdownx.tabbed (markdown_extensions)
- pymdownx.superfences with mermaid fence (markdown_extensions)
- admonition (markdown_extensions)
- pymdownx.details (markdown_extensions)
- content.code.annotate (theme.features)
- navigation.indexes (theme.features)
- mkdocstrings (plugins)
- literate-nav (plugins)

## Question 1: Navigation strategy

- header: "Navigation"
- question: "How should top-level documentation navigation work?"
- detect_context: "Detected: {detected features from mkdocs.yml}"
- preamble: "For projects with 12+ pages, sections-as-tabs gives readers quick access to each documentation area. Smaller projects work well with sidebar-only navigation."
- options:
  - { label: "Sections as top tabs", description: "Each diataxis section becomes a top tab; left sidebar shows only the active section's pages (navigation.tabs + navigation.tabs.sticky)", recommend_if: "12+ pages detected OR navigation.tabs detected" }
  - { label: "Single 'Docs' tab", description: "One 'Docs' tab containing all documentation sections; other tabs reserved for non-docs content", recommend_if: "6-11 pages detected" }
  - { label: "Sidebar only", description: "All navigation in the left sidebar, no top tabs (navigation.sections only)", recommend_if: "fewer than 6 pages detected OR no navigation.tabs detected" }
  - { label: "Type something else", description: "Describe a different nav structure" }
  - { label: "Chat about this", description: "Discuss navigation strategy options" }

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
