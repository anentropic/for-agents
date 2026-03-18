# Sphinx Shibuya Q&A

Framework-specific questions for sphinx-shibuya setup.
Presented during /doc-writer:setup after doc system selection.
Auto-detect: check for conf.py in project root or docs/conf.py.

## Detection

Config file: conf.py
Features to detect:
- html_theme = "shibuya" (conf.py)
- sphinx_design in extensions (conf.py)
- autoapi.extension in extensions (conf.py)
- sphinx.ext.intersphinx in extensions (conf.py)
- nav_links in html_theme_options (conf.py)

## Question 1: Navigation style

- header: "Navigation"
- question: "How should documentation be organized?"
- detect_context: "Detected: {detected features from conf.py}"
- options:
  - { label: "Top tabs + sidebar", description: "Diataxis tabs in top navbar with section sidebar (nav_links)", recommend_if: "nav_links detected" }
  - { label: "Sidebar only", description: "All navigation in left sidebar, no top tabs", recommend_if: "no nav_links detected" }
  - { label: "Flat", description: "All pages at one level, no grouping" }
  - { label: "Type something else", description: "Describe a different nav structure" }
  - { label: "Chat about this", description: "Discuss navigation options" }

## Question 2: API reference approach

- header: "API docs"
- question: "How is API reference generated?"
- detect_context: "Detected: autoapi with {docstring_style}"
- options:
  - { label: "sphinx-autoapi (Recommended)", description: "Auto-generated from docstrings via static analysis", recommend_if: "autoapi.extension detected" }
  - { label: "Manual pages", description: "Hand-written API reference in docs/" }
  - { label: "None", description: "No API reference -- narrative docs only" }
  - { label: "Type something else", description: "Describe a different approach" }
  - { label: "Chat about this", description: "Discuss API reference options" }

## Question 3: sphinx-design features

- header: "Features"
- question: "Which sphinx-design features should docs use?"
- multiSelect: true
- detect_context: "Detected: {detected list}"
- options:
  - { label: "Grids + cards", description: "Responsive grid layouts for landing pages and feature overviews (.. grid::, .. card::)", recommend_if: "sphinx_design detected" }
  - { label: "Tab sets", description: "Multi-language or multi-method code examples (.. tab-set::)", recommend_if: "sphinx_design detected" }
  - { label: "Dropdowns", description: "Collapsible optional/advanced content (.. dropdown::)", recommend_if: "sphinx_design detected" }
  - { label: "Badges + buttons", description: "Inline status/version markers and CTAs (:bdg-success:, .. button-ref::)", recommend_if: "sphinx_design detected" }
  - { label: "Type something else", description: "Add or remove features" }
  - { label: "Chat about this", description: "See examples of each feature" }
