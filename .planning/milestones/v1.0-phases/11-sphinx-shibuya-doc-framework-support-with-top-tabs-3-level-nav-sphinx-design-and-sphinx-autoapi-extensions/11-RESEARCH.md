# Phase 11: Sphinx/Shibuya Doc Framework Support - Research

**Researched:** 2026-03-18
**Domain:** Sphinx documentation framework (Shibuya theme, sphinx-design, sphinx-autoapi) + doc-writer plugin integration
**Confidence:** HIGH

## Summary

This phase adds Sphinx + Shibuya theme as a built-in doc system in the doc-writer plugin, on equal footing with mkdocs-material. The deliverables are four files (sphinx-shibuya.qa.md, sphinx-shibuya.md, conf.py scaffold, SKILL.md update) that mirror the existing mkdocs-material pattern exactly.

The most important technical finding is that **Shibuya does NOT have automatic toctree-to-tabs navigation** like mkdocs-material's `navigation.tabs`. Instead, Shibuya uses explicit `nav_links` in `html_theme_options` for the top navbar, while the toctree drives only the left sidebar. The CONTEXT.md statement "Shibuya picks up these top-level toctree entries as tabs" is technically inaccurate -- the scaffold conf.py must wire `nav_links` explicitly to point at each Diataxis section's index page. This is a scaffold concern, not a conceptual change: the user still sees top tabs for Home/Tutorials/How-To/Explanation/Reference, but the implementation mechanism differs from mkdocs-material.

All four libraries (Sphinx, Shibuya, sphinx-design, sphinx-autoapi) are stable, well-documented, and compatible. Napoleon integration with sphinx-autoapi for Google docstrings has been resolved since 2017 (PR #117). The RST directive syntax for sphinx-design components is well-documented and maps cleanly to the mkdocs-material feature equivalents listed in CONTEXT.md.

**Primary recommendation:** Follow the existing mkdocs-material file patterns exactly. The conf.py scaffold needs explicit `nav_links` for top tabs and `autoapi_add_toctree_entry = False` with manual toctree placement for clean Reference tab integration.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- RST native -- no MyST/Markdown dependency, no extra parser required
- Full Sphinx-specific directive palette: `.. note::`, `.. warning::`, `.. code-block::` with `:emphasize-lines:`, `.. versionadded::`, etc. Do not constrain to portable RST
- Cross-references: `:ref:\`label\`` for internal links + intersphinx for external Sphinx project links (e.g. Python stdlib). Guidance discourages `:doc:\`path\`` direct links as they break on page moves
- Top tabs: **Home, Tutorials, How-To Guides, Explanation, Reference** -- same Diataxis order as mkdocs-material guidance (Reference last)
- Scaffold pattern: `index.rst` at root with a hidden `toctree` listing `tutorials/index`, `how-to/index`, `explanation/index`, `reference/index`. Each section has its own `index.rst`. Shibuya picks up these top-level toctree entries as tabs
- Tab threshold: same rule as mkdocs-material -- disable tabs when all sections have <= 2 pages each; use single sidebar instead
- Left nav depth: same 3-level max as mkdocs-material (section heading -> page -> sub-page). Level descriptions apply directly to Sphinx sidebar hierarchy
- sphinx-design components: Grid + cards, Tabs (sd-tab-set), Dropdowns, Badges + buttons -- with curated use-case guidance
- sphinx-autoapi is the recommended default in Q&A -- detected if already configured in `conf.py`
- Google docstring style (consistent with mkdocstrings in mkdocs-material guidance)
- autoapi output replaces the Reference tab entirely -- Author agent does not write reference pages
- Template variables: `{project_name}`, `{author_name}`, `{copyright_year}`, `{github_url}`
- Extensions by default: `sphinx.ext.intersphinx`, `sphinx_design`, `autoapi.extension`
- Doc system selection label: `"sphinx-shibuya"`
- Detection: check for `conf.py` in project root or `docs/conf.py`

### Claude's Discretion
- Exact wording of guidance prose and example RST snippets
- Whether the scaffold conf.py uses `conf.py` dict syntax or `pyproject.toml` `[tool.sphinx]` style (recommend `conf.py` for broadest compatibility)
- Specific intersphinx_mapping defaults to include in scaffold (recommend: Python stdlib + any common library the project likely uses based on context)
- Exact Shibuya `html_theme_options` keys to include in scaffold template

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Sphinx | >= 7.0 | Documentation generator | Industry standard for Python docs, RST-native |
| shibuya | 2026.1.9 | Sphinx theme | Modern, responsive, dark/light mode, good sphinx-design support |
| sphinx-design | 0.6.1 | UI components (grids, cards, tabs, dropdowns) | Official Sphinx extension for rich layouts |
| sphinx-autoapi | 3.7.0+ | Auto-generated API reference | Static analysis (no imports needed), Napoleon-compatible |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sphinx.ext.napoleon | (built-in) | Google/NumPy docstring parsing | Always -- enables Google docstring style |
| sphinx.ext.intersphinx | (built-in) | Cross-project linking | Always -- links to Python stdlib and external docs |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| shibuya | pydata-sphinx-theme | PyData has native toctree-to-tabs; Shibuya has better visual design but needs explicit nav_links |
| sphinx-autoapi | sphinx.ext.autodoc | autodoc requires importing code; autoapi uses static analysis (safer, no runtime dependencies) |
| RST | MyST Markdown | MyST adds a dependency; RST is Sphinx-native with richer directive support |

**Installation:**
```bash
pip install sphinx shibuya sphinx-design sphinx-autoapi
```

## Architecture Patterns

### Critical Finding: Shibuya Nav Implementation

Shibuya does NOT automatically derive top-level tabs from toctree entries. The navigation model is:

- **Top navbar:** Controlled by `nav_links` in `html_theme_options` -- must be explicitly configured in conf.py
- **Left sidebar:** Driven by toctree directives in index.rst files -- controlled by `globaltoc_expand_depth`, `toctree_maxdepth`, etc.
- **Right sidebar:** Local table of contents (page headings)

To achieve the "top tabs" user experience described in CONTEXT.md, the scaffold conf.py must wire `nav_links` pointing to the Diataxis section index pages:

```python
html_theme_options = {
    "nav_links": [
        {"title": "Tutorials", "url": "tutorials/index"},
        {"title": "How-To Guides", "url": "how-to/index"},
        {"title": "Explanation", "url": "explanation/index"},
        {"title": "Reference", "url": "reference/index"},
    ],
}
```

This is functionally equivalent to mkdocs-material's `navigation.tabs` but implemented differently. The guidance file should explain this mechanism so agents understand the relationship between nav_links and the sidebar toctree.

### Recommended Scaffold Directory Structure
```
docs/
  conf.py
  index.rst              # Root landing page with hidden toctree
  tutorials/
    index.rst            # Section landing page
  how-to/
    index.rst            # Section landing page
  explanation/
    index.rst            # Section landing page
  reference/
    index.rst            # Section landing page (may be autoapi-driven)
```

### Pattern 1: Root index.rst with Hidden Toctree
**What:** Root document declares all sections in a hidden toctree so they appear in sidebar navigation without rendering a visible list on the landing page.
**When to use:** Always -- this is the standard Sphinx pattern for section-based navigation.
**Example:**
```rst
.. Source: Sphinx toctree documentation + Shibuya conventions

Welcome to {project_name}
==========================

Project description and landing content here.

.. toctree::
   :hidden:
   :maxdepth: 2

   tutorials/index
   how-to/index
   explanation/index
   reference/index
```

### Pattern 2: sphinx-autoapi Reference Integration
**What:** autoapi generates reference pages into a subdirectory; a manual toctree in reference/index.rst includes them.
**When to use:** When autoapi is enabled (the recommended default).
**Example conf.py:**
```python
# Source: sphinx-autoapi official docs
autoapi_dirs = ["../src"]           # Path to source code
autoapi_root = "reference/api"     # Output under reference/
autoapi_add_toctree_entry = False  # We manage the toctree manually
autoapi_options = [
    "members", "undoc-members", "show-inheritance",
    "show-module-summary", "imported-members",
]
autoapi_python_class_content = "both"  # Show class + __init__ docstrings
autoapi_member_order = "bysource"
```

**Example reference/index.rst:**
```rst
Reference
=========

.. toctree::
   :maxdepth: 2

   api/index
```

### Pattern 3: Shibuya Theme Configuration
**What:** Sensible Shibuya defaults for dark/light mode, accent color, social links, sidebar depth.
**Example:**
```python
# Source: Shibuya official docs (shibuya.lepture.com)
html_theme = "shibuya"
html_theme_options = {
    "accent_color": "violet",
    "color_mode": "auto",
    "github_url": "{github_url}",
    "globaltoc_expand_depth": 1,
    "toctree_maxdepth": 3,
    "toctree_titles_only": True,
    "nav_links": [
        {"title": "Tutorials", "url": "tutorials/index"},
        {"title": "How-To Guides", "url": "how-to/index"},
        {"title": "Explanation", "url": "explanation/index"},
        {"title": "Reference", "url": "reference/index"},
    ],
}
```

### Anti-Patterns to Avoid
- **Using `:doc:` references instead of `:ref:`:** `:doc:` breaks when pages move; `:ref:` with labels is stable. The guidance must strongly recommend `:ref:` per CONTEXT.md.
- **Setting `autoapi_add_toctree_entry = True` (the default):** This injects the autoapi index at the root toctree level, breaking the clean Diataxis tab structure. Always set to `False` and place the autoapi toctree entry manually under reference/.
- **Over-nesting toctree depth:** Shibuya default `toctree_maxdepth` is 4 but the guidance limits to 3 levels. Set `toctree_maxdepth: 3` in theme options.
- **Mixing MyST and RST:** CONTEXT.md locks RST-native. Do not include `myst_parser` in extensions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API reference pages | Manual RST reference docs | sphinx-autoapi + napoleon | Docstrings are the source of truth; manual pages drift |
| Grid/card layouts | Custom RST tables or raw HTML | sphinx-design `.. grid::` + `.. card::` | Responsive, accessible, theme-compatible |
| Tabbed content | Multiple code blocks with headings | sphinx-design `.. tab-set::` | Synchronized tabs, compact UI |
| Collapsible sections | Custom JavaScript | sphinx-design `.. dropdown::` | No-JS fallback, theme-integrated |
| Cross-project links | Hardcoded URLs to other Sphinx docs | intersphinx | Auto-resolves to correct version, inventory-based |
| Dark/light toggle | Custom CSS/JS | Shibuya built-in `color_mode: "auto"` | Follows system preference, no custom code |

**Key insight:** Every feature in the mkdocs-material guidance has a direct Sphinx equivalent. The mapping is 1:1 -- the guidance file structure should mirror mkdocs-material.md section by section.

## Common Pitfalls

### Pitfall 1: Assuming Shibuya Has Automatic Toctree Tabs
**What goes wrong:** Building a scaffold that relies on toctree entries automatically becoming top nav tabs (like PyData theme or mkdocs-material).
**Why it happens:** The CONTEXT.md implies this behavior, and other Sphinx themes (PyData, Furo) do support it.
**How to avoid:** Use explicit `nav_links` in `html_theme_options` for top navbar entries. The toctree still drives the left sidebar.
**Warning signs:** Top tabs don't appear after building; only sidebar navigation is visible.

### Pitfall 2: Napoleon Not Loaded with sphinx-autoapi
**What goes wrong:** Google-style docstrings render as plain text instead of structured parameter lists.
**Why it happens:** sphinx-autoapi resolved napoleon integration in 2017, but `sphinx.ext.napoleon` must still be in the extensions list.
**How to avoid:** Always include `sphinx.ext.napoleon` in extensions alongside `autoapi.extension`.
**Warning signs:** Parameters, returns, and raises sections appear as unformatted text.

### Pitfall 3: autoapi Toctree Entry at Root Level
**What goes wrong:** An "API Reference" entry appears at the root toctree level instead of nested under the Reference tab.
**Why it happens:** `autoapi_add_toctree_entry` defaults to `True`, which injects into the root toctree.
**How to avoid:** Set `autoapi_add_toctree_entry = False` and manually add the autoapi output to `reference/index.rst` toctree.
**Warning signs:** Extra "API" tab appears in nav or autoapi index shows at root level.

### Pitfall 4: sphinx-design RST vs MyST Syntax Confusion
**What goes wrong:** Using MyST markdown colon-fence syntax (`:::`) instead of RST directives (`.. directive::`).
**Why it happens:** sphinx-design docs show both syntaxes; agents may pick the wrong one.
**How to avoid:** Guidance file must use RST syntax exclusively. All examples use `.. tab-set::`, `.. grid::`, `.. dropdown::`, `.. card::` directives.
**Warning signs:** Build warnings about unknown directives or MyST syntax in RST files.

### Pitfall 5: conf.py Template Variable Collision
**What goes wrong:** Template variables like `{project_name}` in the scaffold are valid Python format strings that could collide with actual Python expressions.
**Why it happens:** Unlike YAML scaffolds, conf.py is Python code where braces have meaning in f-strings and `.format()`.
**How to avoid:** Use the same `{variable}` placeholder pattern as mkdocs-material.yml but ensure they only appear in string literals (quoted values), never in code expressions. The setup skill's scaffold interpolation handles string replacement safely.
**Warning signs:** Python SyntaxError when building docs after scaffold generation.

### Pitfall 6: `:doc:` Links Breaking on Restructure
**What goes wrong:** Internal links break when pages are moved or renamed.
**Why it happens:** `:doc:` references use file paths; `:ref:` references use labels that survive moves.
**How to avoid:** Guidance must strongly recommend `:ref:\`label\`` over `:doc:\`path\`` per CONTEXT.md locked decision.
**Warning signs:** Broken link warnings during `sphinx-build`.

## Code Examples

Verified patterns from official sources:

### sphinx-design: Grid with Cards (RST)
```rst
.. Source: sphinx-design.readthedocs.io/en/latest/grids.html

.. grid:: 1 2 3 3
   :gutter: 2

   .. grid-item-card:: Tutorials
      :link: tutorials/index
      :link-type: doc

      Learn step by step

   .. grid-item-card:: How-To Guides
      :link: how-to/index
      :link-type: doc

      Solve specific problems

   .. grid-item-card:: Reference
      :link: reference/index
      :link-type: doc

      API and configuration details
```

### sphinx-design: Tab Set for Multi-Language Code (RST)
```rst
.. Source: sphinx-design.readthedocs.io/en/latest/tabs.html

.. tab-set::
   :sync-group: lang

   .. tab-item:: Python
      :sync: python

      .. code-block:: python

         client = MyClient(api_key="...")
         result = client.query("hello")

   .. tab-item:: JavaScript
      :sync: js

      .. code-block:: javascript

         const client = new MyClient({ apiKey: "..." });
         const result = await client.query("hello");
```

### sphinx-design: Dropdown for Advanced Content (RST)
```rst
.. Source: sphinx-design.readthedocs.io/en/latest/dropdowns.html

.. dropdown:: Advanced: Custom retry configuration
   :color: info
   :icon: gear

   Override the default retry strategy:

   .. code-block:: python

      client = MyClient(retries=5, backoff_factor=0.5)
```

### sphinx-design: Badges for Version/Status (RST)
```rst
.. Source: sphinx-design.readthedocs.io/en/latest/badges_buttons.html

:bdg-success:`stable` :bdg-info:`v2.1` :bdg-warning:`deprecated in v3.0`

.. button-ref:: tutorials/quickstart
   :color: primary

   Get Started
```

### Sphinx Admonitions (RST)
```rst
.. tip::

   Use ``client.connect(timeout=30)`` for slow networks.

.. warning::

   Calling ``close()`` on an active session discards pending writes.

.. versionadded:: 2.1

   The ``batch_size`` parameter.

.. code-block:: python
   :emphasize-lines: 3,4
   :caption: src/config.py

   config = Config()
   config.load("settings.toml")
   config.validate()  # New in v2.1
   config.apply()
```

### Cross-References with :ref: and Intersphinx
```rst
.. Source: Sphinx official docs

.. _auth-setup:

Authentication Setup
====================

See :ref:`auth-setup` from any page.

For Python's built-in :py:class:`pathlib.Path`, see the stdlib docs
(resolved via intersphinx).
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| sphinx.ext.autodoc (runtime import) | sphinx-autoapi (static analysis) | ~2020 | No need to install project dependencies to build docs |
| sphinxcontrib-napoleon (separate package) | sphinx.ext.napoleon (built-in) | Sphinx 1.3 | Napoleon is bundled, no extra install |
| RTD theme as default | Shibuya/PyData/Furo modern themes | ~2022-2024 | Better design, dark mode, responsive layouts |
| Raw HTML for cards/grids | sphinx-design directives | 2022+ | Accessible, responsive, theme-compatible UI components |
| `:doc:` path references | `:ref:` label references | Always best practice | Survives page restructuring |

**Deprecated/outdated:**
- `sphinxcontrib-napoleon`: Use built-in `sphinx.ext.napoleon` instead
- `sphinx.ext.autodoc` for greenfield projects: prefer `sphinx-autoapi` (no import side-effects)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual verification (file pattern matching) |
| Config file | none -- files are templates and guidance docs |
| Quick run command | `diff` between new sphinx files and mkdocs-material file patterns |
| Full suite command | Visual inspection of all four deliverables |

### Phase Requirements -> Test Map

No formal requirement IDs assigned. Validation is pattern-based:

| Deliverable | Behavior | Test Type | Verification |
|-------------|----------|-----------|-------------|
| sphinx-shibuya.qa.md | Matches mkdocs-material.qa.md structure | manual | Compare Detection section, Question format, option format |
| sphinx-shibuya.md | Mirrors mkdocs-material.md section structure | manual | Compare section headings, directive coverage |
| conf.py scaffold | Valid Python, correct template vars | manual | Python syntax check, template var presence |
| SKILL.md update | sphinx-shibuya appears in Step 2b | manual | Grep for sphinx-shibuya in option list |

### Sampling Rate
- **Per task:** Verify file structure matches mkdocs-material equivalent
- **Phase gate:** All four files created; SKILL.md correctly updated

### Wave 0 Gaps
None -- no automated test infrastructure needed for template/guidance files.

## File-by-File Specifications

### 1. sphinx-shibuya.qa.md

**Location:** `doc-writer/skills/setup/defaults/sphinx-shibuya.qa.md`
**Pattern source:** `mkdocs-material.qa.md`

**Detection section:**
```
Config file: conf.py
Features to detect:
- html_theme = "shibuya" (conf.py)
- sphinx_design in extensions (conf.py)
- autoapi.extension in extensions (conf.py)
- sphinx.ext.intersphinx in extensions (conf.py)
- nav_links in html_theme_options (conf.py)
```

**Question mapping from mkdocs-material:**
| mkdocs-material Question | sphinx-shibuya Equivalent |
|--------------------------|---------------------------|
| Q1: Navigation style (Sections / Tabs+sections / Flat) | Q1: Navigation style (Top tabs + sidebar / Sidebar only / Flat) |
| Q2: API reference (mkdocstrings / Manual / None) | Q2: API reference (sphinx-autoapi (Recommended) / Manual pages / None) |
| Q3: Rich features (content tabs, mermaid, annotations, admonitions, details) | Q3: sphinx-design features (Grids+cards, Tab sets, Dropdowns, Badges+buttons) |

**Detection feature mapping:**
- `nav_links` detected -> recommend "Top tabs + sidebar"
- `autoapi.extension` detected -> recommend "sphinx-autoapi"
- `sphinx_design` detected -> recommend individual sphinx-design features

### 2. sphinx-shibuya.md (Guidance File)

**Location:** `doc-writer/skills/setup/defaults/sphinx-shibuya.md`
**Pattern source:** `mkdocs-material.md`

**Section-by-section mapping:**

| mkdocs-material.md Section | sphinx-shibuya.md Equivalent |
|----------------------------|------------------------------|
| Admonitions | Admonitions (RST directives: `.. tip::`, `.. warning::`, `.. danger::`, `.. note::`, `.. versionadded::`) |
| Code Blocks | Code Blocks (RST: `.. code-block::` with `:emphasize-lines:`, `:caption:`, `:linenos:`) |
| Content Tabs | Tab Sets (sphinx-design: `.. tab-set::` / `.. tab-item::` with `:sync-group:`) |
| Navigation | Navigation (same 3-level + tabs model, but implementation via nav_links + toctree) |
| Frontmatter | Page Metadata (RST meta directives: `:orphan:`, field lists, no YAML frontmatter in RST) |
| Cross-References | Cross-References (`:ref:`, intersphinx `:py:class:`, `:py:func:`, etc.) |

**Additional sections for sphinx-shibuya.md (no mkdocs equivalent):**
- sphinx-design Components (grids, cards, dropdowns, badges -- with curated use-case rules)
- sphinx-autoapi Integration (how autoapi replaces Reference tab, Google docstring conventions)

### 3. conf.py Scaffold

**Location:** `doc-writer/skills/setup/defaults/scaffolds/sphinx-shibuya.py`
**Pattern source:** `scaffolds/mkdocs-material.yml`

**Template variables (per CONTEXT.md):**
- `{project_name}` -- project display name
- `{author_name}` -- author/maintainer
- `{copyright_year}` -- e.g. "2026"
- `{github_url}` -- for Shibuya social link

**Key configuration decisions (Claude's Discretion, researched recommendations):**
- Use `conf.py` format (not pyproject.toml) -- broadest compatibility with Sphinx versions and hosting platforms
- `intersphinx_mapping`: include Python 3 stdlib as default: `{"python": ("https://docs.python.org/3", None)}`
- Shibuya `html_theme_options`: `accent_color`, `color_mode: "auto"`, `github_url`, `globaltoc_expand_depth: 1`, `toctree_maxdepth: 3`, `nav_links` with Diataxis sections

### 4. SKILL.md Update

**Integration points (from CONTEXT.md code_context):**
- Step 2b option list: add `{ label: "sphinx-shibuya", description: "Sphinx with Shibuya theme" }`
- framework_root logic: sphinx-shibuya is built-in, so `framework_root` = `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults`
- Step 2b.3 detection: check for `conf.py` (project root) or `docs/conf.py`

## Open Questions

1. **Shibuya nav_links URL format: relative or with .html suffix?**
   - What we know: Shibuya has a `resource` flag on nav_links that prevents `.html` suffix appending. Standard links get `.html` appended automatically.
   - What's unclear: Whether `tutorials/index` works as-is or needs `tutorials/index.html` for the `dirhtml` builder.
   - Recommendation: Use `tutorials/index` without suffix (Sphinx default builder appends `.html`). If users switch to `dirhtml` builder, they may need to adjust. Note this in guidance as an edge case.

2. **autoapi_root placement under reference/ directory**
   - What we know: `autoapi_root = "reference/api"` would place generated files under the reference section.
   - What's unclear: Whether this creates a clean toctree hierarchy when reference/index.rst includes `api/index`.
   - Recommendation: Use `autoapi_root = "reference/api"` with `autoapi_add_toctree_entry = False` and manual toctree inclusion. This is the documented pattern from sphinx-autoapi how-to guide.

## Sources

### Primary (HIGH confidence)
- [Shibuya official docs](https://shibuya.lepture.com/) -- installation, theme options, nav_links, sidebar, colors, social links, layouts
- [sphinx-design official docs](https://sphinx-design.readthedocs.io/en/latest/) -- grids, cards, tabs, dropdowns, badges, installation
- [sphinx-autoapi official docs](https://sphinx-autoapi.readthedocs.io/en/latest/) -- configuration options, autoapi_root, autoapi_add_toctree_entry, how-to guide
- [Sphinx official docs](https://www.sphinx-doc.org/en/master/) -- intersphinx, napoleon, toctree
- [Existing mkdocs-material.qa.md](doc-writer/skills/setup/defaults/mkdocs-material.qa.md) -- pattern source for Q&A structure
- [Existing mkdocs-material.md](doc-writer/skills/setup/defaults/mkdocs-material.md) -- pattern source for guidance structure
- [Existing SKILL.md](doc-writer/skills/setup/SKILL.md) -- integration point for setup skill

### Secondary (MEDIUM confidence)
- [Shibuya PyPI](https://pypi.org/project/shibuya/) -- version 2026.1.9 (verified)
- [sphinx-autoapi PyPI](https://pypi.org/project/sphinx-autoapi/) -- version 3.7.0 (verified)
- [sphinx-design PyPI](https://pypi.org/project/sphinx_design/) -- version 0.6.1 (verified)
- [sphinx-autoapi GitHub Issue #98](https://github.com/readthedocs/sphinx-autoapi/issues/98) -- Napoleon integration resolved in 2017

### Tertiary (LOW confidence)
- None -- all findings verified with primary or secondary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries verified on PyPI with current versions and official docs
- Architecture: HIGH -- Shibuya nav mechanism verified through official docs, mistune example conf.py, and Shibuya's own docs source
- Pitfalls: HIGH -- nav_links vs toctree-tabs finding verified through multiple sources; napoleon issue verified as resolved
- sphinx-design RST syntax: HIGH -- verified from official docs with explicit RST examples

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (stable ecosystem, calver Shibuya releases)
