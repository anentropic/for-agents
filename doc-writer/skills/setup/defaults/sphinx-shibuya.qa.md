# Sphinx Shibuya Q&A

Framework-specific questions for sphinx-shibuya setup.
Presented during /doc-writer:setup after doc system selection.
Auto-detect: check for conf.py in project root or docs/conf.py.

## Detection

Config file: conf.py, docs/conf.py, docs/source/conf.py, doc/conf.py, doc/source/conf.py
Features to detect:
- html_theme = "shibuya" (conf.py)
- sphinx_design in extensions (conf.py)
- autoapi.extension in extensions (conf.py)
- sphinx.ext.intersphinx in extensions (conf.py)
- nav_links in html_theme_options (conf.py)

## Question 1: Navigation strategy

- header: "Navigation"
- question: "How should top-level documentation navigation work?"
- detect_context: "Detected: {detected features from conf.py}"
- preamble: "For projects with 12+ pages, sections-as-tabs gives readers quick access to each documentation area. Smaller projects work well with sidebar-only navigation."
- options:
  - { label: "Sections as top tabs", description: "Each diataxis section (Tutorials, How-To, Explanation, Reference) becomes a dropdown tab in the top navbar with children links and summaries (nav_links with children)", recommend_if: "12+ pages detected OR nav_links detected" }
  - { label: "Single 'Docs' tab", description: "One 'Docs' dropdown in the top navbar with section links as children items", recommend_if: "6-11 pages detected" }
  - { label: "Sidebar only", description: "All navigation in the left sidebar, no top tabs", recommend_if: "fewer than 6 pages detected OR no nav_links detected" }
  - { label: "Type something else", description: "Describe a different nav structure" }
  - { label: "Chat about this", description: "Discuss navigation strategy options" }

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
