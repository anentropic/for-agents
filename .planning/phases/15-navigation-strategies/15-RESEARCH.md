# Phase 15: Navigation Strategies - Research

**Researched:** 2026-03-21
**Domain:** Doc-writer plugin Q&A flow, Sphinx-Shibuya nav_links, MkDocs-Material navigation features, scaffold template variable substitution
**Confidence:** HIGH

## Summary

Phase 15 adds three-strategy navigation selection to the setup Q&A flow and makes both Sphinx-Shibuya and MkDocs-Material scaffolds, guidance files, and the doc-researcher agent render the chosen strategy correctly. The three strategies are: (1) no top tabs (flat sidebar only), (2) a single "Docs" top tab, and (3) sections promoted to top tabs. The phase also adds section index pages with short abstracts beneath each sub-page link.

The primary architectural challenge is that nav strategy answers flow through the researcher into context.md -- NOT into config.yaml. This matches the existing Q&A data flow pattern where framework-specific answers are passed to the researcher agent in the Agent tool invocation message. The researcher then writes the nav strategy into the Framework Preferences section of context.md, where the doc-author reads it at write time. The secondary challenge is scaffold template variable substitution: the existing scaffold files use `{variable_name}` patterns replaced at setup time, and a new `{nav_links_config}` variable (for Sphinx-Shibuya) or conditional feature flags (for MkDocs-Material) must be handled.

The Shibuya nav_links and Sphinx toctree are parallel, disconnected navigation layers. `nav_links` are static URL lists in conf.py -- they do not derive from the toctree and have no build-time validation. The sidebar shows toctree contents scoped to the current section's index.rst toctree. When a user clicks a nav_link tab, Sphinx resolves the URL to the relevant section's index page, and the sidebar renders that section's toctree. This two-layer model means nav_links URLs must be hardcoded and updated atomically when pages are restructured. MkDocs-Material is simpler: tabs are derived from the top-level entries in the `nav:` section of mkdocs.yml, and the sidebar automatically shows only the active tab's children.

**Primary recommendation:** Implement as two plans: Plan 15-01 covers the setup Q&A nav strategy question for both frameworks + researcher context.md integration + scaffold template updates. Plan 15-02 covers section index page guidance in both frameworks' guidance files + abstract rendering patterns in doc-author.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| NAV-01 | Setup Q&A offers three nav strategies: no top tabs, single "Docs" top tab, sections promoted to top tabs | New Question in sphinx-shibuya.qa.md and mkdocs-material.qa.md replacing existing Q1; three options with recommendation logic |
| NAV-02 | Sections-as-tabs recommended when 12+ pages, but all three choices always available | Recommendation logic in Q&A option `recommend_if` field; recommendation text in question preamble |
| NAV-03 | Sphinx-shibuya sections-as-tabs uses dropdown menus with children and summary text via nav_links | Scaffold conf.py gets `{nav_links_config}` variable; researcher writes nav_links Python dict based on page inventory |
| NAV-04 | Sphinx-shibuya "Docs" top tab renders as dropdown with docs sections as items | `{nav_links_config}` variable resolves to a single "Docs" nav_link with children listing section indexes |
| NAV-05 | When sections promoted to top tabs, left nav starts from selected section (not full docs index) | Sphinx: each section index.rst has its own toctree; sidebar shows that toctree. MkDocs: navigation.tabs auto-scopes sidebar. Documented in guidance files. |
| NAV-06 | MkDocs-material three nav strategies use navigation.tabs, navigation.tabs.sticky, navigation.indexes features | Scaffold mkdocs.yml gets conditional feature flags; researcher writes active features to context.md |
| NAV-07 | Section index pages include a short abstract beneath each sub-page link | Doc-author guidance: section index pages list children with 1-sentence abstract per link |
| NAV-08 | Abstracts use framework-native metadata where supported (sphinx :description:), inline on index page elsewhere | Sphinx: `.. meta:: :description:` directive on each page provides machine-readable metadata, but abstracts are written inline on the index page. MkDocs: `description` frontmatter field + inline abstracts on index.md. |
</phase_requirements>

## Standard Stack

### Core

No new runtime dependencies. Phase 15 modifies existing markdown agent prompts, YAML templates, Python scaffold templates, and Q&A data files. There are no npm/pip packages to install for the plugin itself.

### Frameworks Referenced (end-user dependencies, already in scaffolds)

| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| Shibuya theme | >= 2023.6.7 | nav_links with children dropdowns | children feature added 2023.6.7; keyboard accessibility 2025.7.24 |
| MkDocs-Material | >= 9.0 | navigation.tabs, navigation.tabs.sticky, navigation.indexes | All three feature flags available in Material 9.x+ |

### What NOT to Add

| Do Not Add | Why |
|------------|-----|
| Nav strategy Q&A for plain-markdown or odoc | User decision: nav strategy Q&A only for sphinx-shibuya and mkdocs-material |
| Multiple scaffold variants per nav strategy | Out of scope per REQUIREMENTS.md; handle via variable substitution in single scaffold |
| Nav strategy stored in config.yaml | User decision: answers flow through researcher into context.md |
| Dropdown menus on MkDocs-Material tabs | User decision: MkDocs-Material does NOT support dropdown menus on tabs (flat tabs only) |

## Architecture Patterns

### Files Modified by This Phase

```
doc-writer/
  agents/
    doc-author.md              # Add section index page guidance + abstract writing rules
    doc-researcher.md          # Add nav strategy expansion in context.md output
  skills/
    setup/
      SKILL.md                 # No changes needed -- Q&A flow already reads .qa.md files dynamically
      defaults/
        sphinx-shibuya.qa.md   # Replace Q1 with three-strategy nav question
        mkdocs-material.qa.md  # Replace Q1 with three-strategy nav question
        sphinx-shibuya.md      # Expand Navigation section with three strategy patterns + section index guidance
        mkdocs-material.md     # Expand Navigation section with three strategy patterns + section index guidance
        scaffolds/
          sphinx-shibuya.py    # Replace static nav_links with {nav_links_config} variable
          mkdocs-material.yml  # Add {nav_feature_flags} variable for conditional navigation features
```

### Pattern 1: Q&A Data File Update (Replacing Question 1)

**What:** Both `sphinx-shibuya.qa.md` and `mkdocs-material.qa.md` already have a Question 1 about navigation style. Replace each with a standardized three-option nav strategy question that matches across both frameworks.

**Why replace rather than add:** The existing Q1 in both files already asks about navigation. The new question is a refined version with explicit three-strategy choices and a 12+ pages recommendation. Adding a separate question would create duplication and confusion.

**Sphinx-shibuya.qa.md new Question 1:**
```markdown
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
```

**MkDocs-material.qa.md new Question 1:**
```markdown
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
```

### Pattern 2: Scaffold Variable Substitution for Nav Strategy

**What:** The scaffold templates need conditional content based on the chosen nav strategy. Use the existing `{variable_name}` substitution pattern already used for `{project_name}`, `{github_url}`, etc.

**Sphinx-shibuya scaffold (conf.py):**

Replace the hardcoded `nav_links` block with a `{nav_links_config}` variable:

```python
html_theme_options = {
    "accent_color": "violet",
    "color_mode": "auto",
    "github_url": "{github_url}",
    "globaltoc_expand_depth": 1,
    "toctree_maxdepth": 3,
    "toctree_titles_only": True,
{nav_links_config}
}
```

The setup SKILL.md substitution logic resolves `{nav_links_config}` based on the Q&A answer:

- **Sections as top tabs:** Full nav_links list with children and summaries per section
- **Single "Docs" tab:** One nav_link "Docs" entry with children listing each section index
- **Sidebar only:** Empty string (no nav_links key at all)

**MkDocs-Material scaffold (mkdocs.yml):**

Replace the static features list with a base set plus `{nav_feature_flags}`:

```yaml
  features:
    - navigation.instant
    - navigation.sections
    - navigation.top
    - navigation.tracking
    - toc.follow
    - content.code.copy
    - content.code.annotate
    - search.suggest
    - search.highlight
{nav_feature_flags}
```

The setup SKILL.md substitution logic resolves `{nav_feature_flags}` based on the Q&A answer:

- **Sections as top tabs:** `    - navigation.tabs\n    - navigation.tabs.sticky\n    - navigation.indexes`
- **Single "Docs" tab:** `    - navigation.tabs\n    - navigation.tabs.sticky\n    - navigation.indexes`
- **Sidebar only:** Empty string (no additional features)

**Variable inference table addition:** Add both `{nav_links_config}` and `{nav_feature_flags}` to the variable inference table in setup SKILL.md. Source: Q&A answer for "Navigation strategy" question. The value depends on the Q&A answer and the doc_system.

### Pattern 3: Researcher Nav Strategy Expansion in context.md

**What:** The doc-researcher agent writes nav strategy guidance into the Framework Preferences section of context.md. This is where the doc-author reads nav strategy at write time.

**How it works in the existing architecture:**
1. Setup Q&A asks the nav strategy question (from .qa.md file)
2. Answer is passed to the researcher via the Agent tool invocation message (same as all framework Q&A answers)
3. Researcher expands the answer into concrete navigation guidance in context.md
4. Doc-author reads context.md and applies nav strategy when writing page inventory and pages

**Addition to doc-researcher.md Framework Preferences section:**

```markdown
### Navigation Strategy Expansion

If the framework Q&A answers include a navigation strategy selection:

**Sections as top tabs:**
- Document which sections become tabs (Tutorials, How-To Guides, Explanation, Reference)
- Note that each tab maps to a section index page
- Specify that the sidebar shows only the active section's pages
- Remind that section index pages must list children with abstracts

**Single "Docs" tab:**
- Document that one "Docs" tab contains all documentation sections
- Note that the sidebar shows the full docs tree under the Docs tab
- Specify that the Docs tab acts as a landing page with section links

**Sidebar only:**
- Document that all pages appear in the left sidebar
- Note that sections are rendered as expandable groups
- No tabs present; navigation is sidebar-driven
```

### Pattern 4: Section Index Pages with Abstracts

**What:** Section index pages (e.g., `tutorials/index.md` or `tutorials/index.rst`) list their children with a 1-sentence abstract beneath each link. The abstract tells the reader what the child page covers before they click.

**Framework-specific abstract sources:**

- **Sphinx-shibuya:** Each child page uses `.. meta:: :description: One-sentence abstract` at the top. The section index page writes the abstract inline beneath each toctree entry link. The `.. meta::` directive stores the description for HTML meta tags and social sharing, but the inline abstract on the index page is what readers actually see. The index page uses sphinx-design grids or a simple link list with descriptions.

- **MkDocs-Material:** Each child page uses `description` frontmatter field. The section index page (enabled via `navigation.indexes` feature flag) writes the abstract inline beneath each link. MkDocs-Material does NOT auto-render descriptions from child pages on the index -- the abstracts must be written explicitly on the index page.

- **Plain-markdown / odoc:** Not applicable -- nav strategy Q&A not presented for these frameworks.

**Doc-author guidance addition:**

When writing section index pages, the doc-author should:
1. List each child page as a link
2. Write a 1-sentence abstract beneath each link describing what the page covers
3. Group links by sub-section if the section has 6+ children
4. Use sphinx-design grids (Sphinx) or a styled list (MkDocs) for visual presentation

### Anti-Patterns to Avoid

- **Using RST cross-references in Shibuya nav_links URLs:** nav_links URLs are plain strings, not RST cross-references. Do NOT use `:ref:` or `:doc:` syntax in nav_links. Use plain relative paths like `"tutorials/index"`.
- **MkDocs-Material dropdown menus on tabs:** MkDocs-Material tabs are flat -- no dropdown children. Do NOT attempt to add children/summary to MkDocs tabs.
- **Single-page tab sections in MkDocs-Material:** A top-level tab section with fewer than 2 child pages renders a nearly-empty sidebar. Every tab section must have at least 2 children.
- **Storing nav strategy in config.yaml:** Framework Q&A answers (including nav strategy) do NOT go into config.yaml. They flow through the researcher into context.md.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dropdown nav menus in Sphinx | Custom JavaScript dropdown | Shibuya nav_links children | Native feature since 2023.6.7; accessible; keyboard-navigable since 2025.7.24 |
| Tab-scoped sidebar in MkDocs | Custom JavaScript sidebar filtering | navigation.tabs feature flag | Built-in behavior: sidebar auto-scopes to active tab's children |
| Section index pages | Custom template rendering | navigation.indexes (MkDocs) / index.rst toctree (Sphinx) | Framework-native patterns; well-documented |
| Page abstracts/descriptions | Custom metadata extraction | description frontmatter (MkDocs) / .. meta:: :description: (Sphinx) | Framework-native metadata; SEO benefits; social card integration |

## Common Pitfalls

### Pitfall 1: Sphinx nav_links and toctree Disconnect

**What goes wrong:** After adding nav_links tabs, the sidebar still shows the full docs tree instead of just the selected section's pages. Or worse, nav_links URLs break silently when pages are restructured.

**Why it happens:** Shibuya's nav_links are static URL lists in conf.py. They do not derive from the toctree. The sidebar shows toctree contents scoped to whichever section's index.rst the current page belongs to -- this scoping happens naturally through the toctree hierarchy, not through nav_links.

**How to avoid:**
1. Each section (Tutorials, How-To, Explanation, Reference) MUST have its own `index.rst` with a `:hidden:` toctree listing its child pages
2. The root `index.rst` MUST have a hidden toctree listing all section index files
3. nav_links URLs must match the section index file paths exactly
4. Document in guidance that nav_links URLs are plain strings, not RST cross-references

**Warning signs:** Clicking a tab shows an empty sidebar or shows the wrong section's pages.

### Pitfall 2: MkDocs-Material Tabs Require Multiple Sections

**What goes wrong:** Enabling `navigation.tabs` with only one top-level section in `nav:` renders a single tab that looks like a header, not a tab bar.

**Why it happens:** Tabs are generated from top-level entries in the `nav:` section. With one entry, there is nothing to tab between.

**How to avoid:** The recommendation logic suggests tabs only when 12+ pages exist. A post-plan validation in the doc-author should verify that every tab section has at least 2 child pages before writing the nav structure.

**Warning signs:** Only one tab visible, or a tab with no children rendering an empty sidebar.

### Pitfall 3: Scaffold Variable Not Substituted

**What goes wrong:** The `{nav_links_config}` or `{nav_feature_flags}` variable appears literally in the generated conf.py or mkdocs.yml instead of being replaced with the actual configuration.

**Why it happens:** The setup SKILL.md substitution logic uses a variable inference table. If the new variables are not added to the table, they are treated as literal text.

**How to avoid:** Add both variables to the inference table with their Source (Q&A answer for "Navigation strategy" question) and resolution logic. Test substitution for all three strategies.

**Warning signs:** Literal `{nav_links_config}` or `{nav_feature_flags}` in generated config files.

### Pitfall 4: Abstracts Written Only as Metadata, Not Visible on Index

**What goes wrong:** Abstracts are set via `.. meta:: :description:` or `description` frontmatter, but no human-readable abstract appears on the section index page.

**Why it happens:** Neither MkDocs-Material nor Sphinx auto-renders child page descriptions on the parent index page. The metadata is only used for HTML meta tags, SEO, and social cards.

**How to avoid:** Abstracts must be written BOTH as metadata (for SEO) AND as inline text on the section index page (for readers). The doc-author guidance must explicitly instruct writing the abstract in both places.

**Warning signs:** Section index pages that list links without any description text.

### Pitfall 5: "Docs" Tab Strategy Confusion with Sections-as-Tabs

**What goes wrong:** The "Docs" tab strategy is implemented identically to sections-as-tabs, creating multiple tabs instead of a single "Docs" tab.

**Why it happens:** The two strategies share similar configuration. The difference is:
- Sections-as-tabs: Tutorials, How-To, Explanation, Reference as separate top tabs
- Single "Docs" tab: One "Docs" tab that contains all four sections as children (Sphinx) or one top-level nav entry wrapping all sections (MkDocs)

**How to avoid:** Clear differentiation in Q&A option descriptions, researcher expansion, and guidance file examples. The scaffold variable resolution must produce distinctly different configs for each strategy.

## Code Examples

### Sphinx-Shibuya: Sections-as-Tabs nav_links Config

```python
# Source: Shibuya official navbar docs (shibuya.lepture.com/customisation/navbar/)
# Strategy: Sections as top tabs with dropdown children
"nav_links": [
    {
        "title": "Tutorials",
        "url": "tutorials/index",
        "children": [
            {
                "title": "Getting Started",
                "url": "tutorials/getting-started",
                "summary": "Install and run your first example"
            },
            {
                "title": "Build Your First App",
                "url": "tutorials/first-app",
                "summary": "Step-by-step guide to building a complete application"
            },
        ],
    },
    {
        "title": "How-To Guides",
        "url": "how-to/index",
        "children": [
            {
                "title": "Authentication",
                "url": "how-to/authentication",
                "summary": "Configure OAuth, API keys, and token refresh"
            },
        ],
    },
    {
        "title": "Explanation",
        "url": "explanation/index",
        "children": [
            {
                "title": "Architecture Overview",
                "url": "explanation/architecture",
                "summary": "How the library is structured and why"
            },
        ],
    },
    {
        "title": "Reference",
        "url": "reference/index",
    },
],
```

### Sphinx-Shibuya: Single "Docs" Tab nav_links Config

```python
# Source: Shibuya official navbar docs
# Strategy: Single "Docs" dropdown with sections as children
"nav_links": [
    {
        "title": "Docs",
        "url": "index",
        "children": [
            {
                "title": "Tutorials",
                "url": "tutorials/index",
                "summary": "Step-by-step learning guides"
            },
            {
                "title": "How-To Guides",
                "url": "how-to/index",
                "summary": "Goal-oriented task instructions"
            },
            {
                "title": "Explanation",
                "url": "explanation/index",
                "summary": "Background concepts and design rationale"
            },
            {
                "title": "Reference",
                "url": "reference/index",
                "summary": "API documentation and specifications"
            },
        ],
    },
],
```

### MkDocs-Material: Sections-as-Tabs mkdocs.yml

```yaml
# Source: MkDocs-Material navigation docs (squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
# Strategy: Sections as top tabs
theme:
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.indexes
    - navigation.sections

nav:
  - Home: index.md
  - Tutorials:
    - tutorials/index.md
    - Getting Started: tutorials/getting-started.md
    - Build Your First App: tutorials/first-app.md
  - How-To Guides:
    - how-to/index.md
    - Authentication: how-to/authentication.md
  - Explanation:
    - explanation/index.md
    - Architecture Overview: explanation/architecture.md
  - Reference:
    - reference/index.md
```

### MkDocs-Material: Single "Docs" Tab mkdocs.yml

```yaml
# Source: MkDocs-Material navigation docs
# Strategy: Single "Docs" tab wrapping all sections
theme:
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.indexes

nav:
  - Home: index.md
  - Docs:
    - docs/index.md
    - Tutorials:
      - tutorials/index.md
      - Getting Started: tutorials/getting-started.md
    - How-To Guides:
      - how-to/index.md
      - Authentication: how-to/authentication.md
    - Explanation:
      - explanation/index.md
      - Architecture Overview: explanation/architecture.md
    - Reference:
      - reference/index.md
```

### Section Index Page with Abstracts (MkDocs-Material)

```markdown
---
title: Tutorials
description: Step-by-step learning guides for new users
---

# Tutorials

Learn to use the library from scratch with these step-by-step guides.

- **[Getting Started](getting-started.md)** -- Install the library and run your first example in under 5 minutes.
- **[Build Your First App](first-app.md)** -- Walk through building a complete application from an empty directory to a working deployment.
```

### Section Index Page with Abstracts (Sphinx RST)

```rst
.. meta::
   :description: Step-by-step learning guides for new users

Tutorials
=========

Learn to use the library from scratch with these step-by-step guides.

- :ref:`getting-started` -- Install the library and run your first example in under 5 minutes.
- :ref:`first-app` -- Walk through building a complete application from an empty directory to a working deployment.

.. toctree::
   :hidden:

   getting-started
   first-app
```

## State of the Art

| Old Approach (current scaffold) | New Approach (Phase 15) | Impact |
|--------------------------------|-------------------------|--------|
| Static nav_links with 4 tabs hardcoded in sphinx-shibuya.py | Variable `{nav_links_config}` resolved per nav strategy | Scaffold supports all three strategies from one template |
| No navigation feature flags in mkdocs-material.yml | Variable `{nav_feature_flags}` resolved per nav strategy | Scaffold supports tabs/no-tabs from one template |
| Single "Top tabs + sidebar" Q&A option in sphinx-shibuya | Three explicit strategies with recommendation logic | Clearer choices; smart defaults based on project size |
| Single "Tabs + sections" Q&A option in mkdocs-material | Three explicit strategies with recommendation logic | Matches sphinx-shibuya pattern |
| No section index page guidance | Explicit guidance for index pages with abstracts | Landing pages with navigation context for readers |

## Open Questions

1. **Scaffold variable resolution for multi-line Python dicts**
   - What we know: The existing substitution pattern uses simple `{variable_name}` replacement. `{nav_links_config}` for Sphinx needs to resolve to a multi-line Python dict with proper indentation.
   - What's unclear: Whether the existing substitution step in setup SKILL.md handles multi-line replacements with correct indentation. The current variables (`{project_name}`, `{github_url}`, etc.) are all single-line strings.
   - Recommendation: The setup SKILL.md substitution is done by an LLM agent (not a regex tool). The agent reads the template, identifies variables, infers values, and writes the completed file. Multi-line substitution works because the agent is generating text, not doing find-and-replace. The `{nav_links_config}` variable serves as a marker -- the agent replaces it with the full Python dict at the correct indentation level. This approach is confirmed by the existing scaffold handling of directory scaffolds for odoc (Step 2b.3 in SKILL.md).

2. **Page count detection for recommendation logic**
   - What we know: The Q&A question recommends sections-as-tabs when 12+ pages. The setup flow has access to the project detection results.
   - What's unclear: Whether existing page count detection is accurate enough for the recommendation. The detect-project.sh script scans for existing docs.
   - Recommendation: The recommendation is a soft suggestion (the `recommend_if` field in the Q&A), not an enforcement. If page count detection is imprecise, the user simply selects their preferred strategy. The Q&A preamble text explains the 12+ threshold. LOW risk.

3. **Nav strategy for existing projects (diff-against-defaults mode)**
   - What we know: When a config file already exists (Step 2b.3 mode), the setup flow diffs against scaffold defaults and offers missing features.
   - What's unclear: How the nav strategy selection interacts with diff mode. If a project already has nav_links configured, should the setup suggest changing them?
   - Recommendation: In diff mode, the nav strategy Q&A still runs as Question 1. The `detect_context` field shows what is currently detected. If nav_links are already configured, the current approach is pre-selected with `recommend_if`. The user can change or keep the current strategy. No special diff handling needed -- the Q&A is independent of the scaffold diff flow.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | bats (existing) |
| Config file | `tests/` directory |
| Quick run command | `grep -c "nav_links_config\|nav_feature_flags\|nav.*strategy\|Navigation strategy" doc-writer/skills/setup/defaults/*.qa.md doc-writer/skills/setup/defaults/scaffolds/*.py doc-writer/skills/setup/defaults/scaffolds/*.yml` |
| Full suite command | `bats tests/` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NAV-01 | Q&A offers three nav strategies | grep | `grep -c "Sections as top tabs\|Single.*Docs.*tab\|Sidebar only" doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md doc-writer/skills/setup/defaults/mkdocs-material.qa.md` | Wave 0 |
| NAV-02 | Sections-as-tabs recommended when 12+ pages | grep | `grep -c "12+" doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md doc-writer/skills/setup/defaults/mkdocs-material.qa.md` | Wave 0 |
| NAV-03 | Sphinx sections-as-tabs uses nav_links with children | grep | `grep -c "nav_links_config\|children" doc-writer/skills/setup/defaults/scaffolds/sphinx-shibuya.py doc-writer/skills/setup/defaults/sphinx-shibuya.md` | Wave 0 |
| NAV-04 | Sphinx "Docs" tab renders as dropdown | grep | `grep -c "Docs.*tab\|Docs.*dropdown" doc-writer/skills/setup/defaults/sphinx-shibuya.md` | Wave 0 |
| NAV-05 | Tab selection scopes left nav | grep | `grep -c "active section\|selected section\|sidebar shows" doc-writer/skills/setup/defaults/sphinx-shibuya.md doc-writer/skills/setup/defaults/mkdocs-material.md` | Wave 0 |
| NAV-06 | MkDocs nav strategies use correct feature flags | grep | `grep -c "navigation.tabs\|navigation.tabs.sticky\|navigation.indexes" doc-writer/skills/setup/defaults/mkdocs-material.md doc-writer/skills/setup/defaults/scaffolds/mkdocs-material.yml` | Wave 0 |
| NAV-07 | Section index pages with abstracts | grep | `grep -c "abstract\|section index" doc-writer/agents/doc-author.md doc-writer/skills/setup/defaults/sphinx-shibuya.md doc-writer/skills/setup/defaults/mkdocs-material.md` | Wave 0 |
| NAV-08 | Abstracts use framework-native metadata | grep | `grep -c "description.*frontmatter\|meta.*description\|:description:" doc-writer/skills/setup/defaults/sphinx-shibuya.md doc-writer/skills/setup/defaults/mkdocs-material.md doc-writer/agents/doc-author.md` | Wave 0 |

### Sampling Rate

- **Per task commit:** Quick grep checks on modified files
- **Per wave merge:** `bats tests/`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

None -- existing test infrastructure (bats + grep checks) covers all phase requirements. No new test framework, config files, or fixtures needed. All validation is grep-based content verification on modified files.

## Sources

### Primary (HIGH confidence)
- [Shibuya navbar docs](https://shibuya.lepture.com/customisation/navbar/) -- nav_links children/summary/external/resource fields, dropdown configuration
- [Shibuya sidebar docs](https://shibuya.lepture.com/customisation/sidebar/) -- globaltoc_expand_depth, toctree_maxdepth, toctree_collapse options
- [Shibuya changelog](https://shibuya.lepture.com/changelog/) -- children links added 2023.6.7; keyboard accessibility 2025.7.24; resource parameter 2025.4.25
- [MkDocs-Material navigation docs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/) -- navigation.tabs, navigation.tabs.sticky, navigation.sections, navigation.indexes feature flags
- [MkDocs-Material reference](https://squidfunk.github.io/mkdocs-material/reference/) -- description frontmatter for page metadata
- [Sphinx field lists docs](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html) -- :description: NOT a recognized special metadata field; use .. meta:: directive instead
- Existing codebase: all files listed in "Files Modified by This Phase" section, plus setup SKILL.md scaffold processing logic

### Secondary (MEDIUM confidence)
- [MkDocs-Material Issue #197](https://github.com/squidfunk/mkdocs-material/issues/197) -- tabs require second-level nav items
- [MkDocs-Material Issue #2060](https://github.com/squidfunk/mkdocs-material/issues/2060) -- section index page clickable sections history

### Tertiary (LOW confidence)
- None. All findings verified against primary sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies; features verified in official docs
- Architecture: HIGH -- follows existing Q&A data flow, researcher expansion, and scaffold substitution patterns; all extension points confirmed by reading codebase
- Pitfalls: HIGH -- all pitfalls verified against official docs and existing codebase behavior
- Section index abstracts: MEDIUM-HIGH -- confirmed that neither framework auto-renders child descriptions on index pages; inline abstracts are the correct approach

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (30 days -- stable frameworks, no fast-moving changes expected)
