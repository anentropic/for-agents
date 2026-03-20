# Phase 11: sphinx-shibuya doc framework support - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Sphinx + Shibuya theme as a built-in supported framework in the doc-writer plugin — on equal footing with mkdocs-material. Deliverables: `sphinx.qa.md` question set, `sphinx.md` guidance file, `conf.py` scaffold template, and setup skill updated to list Sphinx/Shibuya as a selectable doc system. RST-native throughout. No changes to the core writing/review pipeline.

</domain>

<decisions>
## Implementation Decisions

### Content format
- RST native — no MyST/Markdown dependency, no extra parser required
- Full Sphinx-specific directive palette: `.. note::`, `.. warning::`, `.. code-block::` with `:emphasize-lines:`, `.. versionadded::`, etc. Do not constrain to portable RST
- Cross-references: `:ref:\`label\`` for internal links + intersphinx for external Sphinx project links (e.g. Python stdlib). Guidance discourages `:doc:\`path\`` direct links as they break on page moves

### Navigation structure
- Top tabs: **Home, Tutorials, How-To Guides, Explanation, Reference** — same Diataxis order as mkdocs-material guidance (Reference last)
- Scaffold pattern: `index.rst` at root with a hidden `toctree` listing `tutorials/index`, `how-to/index`, `explanation/index`, `reference/index`. Each section has its own `index.rst`. Shibuya picks up these top-level toctree entries as tabs
- Tab threshold: same rule as mkdocs-material — disable tabs when all sections have ≤ 2 pages each; use single sidebar instead
- Left nav depth: same 3-level max as mkdocs-material (section heading → page → sub-page). Level descriptions apply directly to Sphinx sidebar hierarchy

### sphinx-design components
- Guidance covers all four component groups with curated use-case guidance:
  - **Grid + cards** — landing pages, feature overviews, section index pages
  - **Tabs (sd-tab-set)** — multi-language or multi-method code examples (same role as content tabs in mkdocs-material)
  - **Dropdowns** — collapsible optional/advanced content (equivalent to collapsible admonitions)
  - **Badges + buttons** — inline status/version markers, prominent CTAs on landing pages
- Approach: guidance file covers the top use cases with concrete rules, then references the sphinx-design documentation for the full component inventory. Agents should be pro-active about suggesting sphinx-design features where they improve clarity or navigation — not just apply them reactively
- Link to include: https://sphinx-design.readthedocs.io/en/latest/

### API reference (sphinx-autoapi)
- sphinx-autoapi is the **recommended default** in the Q&A — presented as the top option, detected if already configured in `conf.py`. User can choose manual pages or none
- Google docstring style (consistent with mkdocstrings in mkdocs-material guidance)
- autoapi output **replaces** the Reference tab entirely — the Author agent does not write reference pages (consistent with Phase 2 locked decision: Author defers to auto-generated API reference)
- Q&A should detect autoapi in `conf.py` extensions list and mark it as "(Recommended)" pre-selected

### Scaffold scope (conf.py)
- Template variables: `{project_name}`, `{author_name}`, `{copyright_year}`, `{github_url}` (for Shibuya social links)
- Extensions included by default: `sphinx.ext.intersphinx`, `sphinx_design`, `autoapi.extension`
- Shibuya theme configured with sensible defaults: `html_theme = "shibuya"`, `html_theme_options` for nav tabs enabled, dark/light mode
- Scaffold structure: root `index.rst` + `tutorials/`, `how-to/`, `explanation/`, `reference/` directories with stub `index.rst` files

### Setup skill integration
- Doc system selection label: `"sphinx-shibuya"` — distinguishes from any generic "sphinx" entry the unknown framework researcher might have generated
- Detection: check for `conf.py` in project root or `docs/conf.py`
- Features to detect in `conf.py` for Q&A pre-selection: `sphinx_design` in extensions, `autoapi.extension` in extensions, intersphinx configured, `html_theme = "shibuya"` confirmed

### Claude's Discretion
- Exact wording of guidance prose and example RST snippets
- Whether the scaffold conf.py uses `conf.py` dict syntax or `pyproject.toml` `[tool.sphinx]` style (recommend `conf.py` for broadest compatibility)
- Specific intersphinx_mapping defaults to include in scaffold (recommend: Python stdlib + any common library the project likely uses based on context)
- Exact Shibuya `html_theme_options` keys to include in scaffold template

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing framework infrastructure (pattern source)
- `doc-writer/skills/setup/defaults/mkdocs-material.qa.md` — Pattern for .qa.md structure: Detection section, question format, detect_context, recommend_if fields. Replicate this structure for sphinx.qa.md
- `doc-writer/skills/setup/defaults/mkdocs-material.md` — Pattern for guidance file: section structure, opinionated preference style, what to cover. Replicate tone and approach for sphinx.md
- `doc-writer/skills/setup/defaults/scaffolds/mkdocs-material.yml` — Pattern for scaffold templates. sphinx equivalent will be conf.py (Python, not YAML)
- `doc-writer/skills/setup/SKILL.md` — Integration point: Step 2b doc system selection, framework_root logic, Step 2b.3 scaffold check, Step 2b.5 Q&A reading. New sphinx-shibuya entry slots into existing built-in framework detection

### Navigation and guidance decisions
- `doc-writer/skills/setup/defaults/mkdocs-material.md` §Navigation — Top tabs + 3-level nav model, threshold rule, level definitions. Sphinx guidance should mirror these decisions exactly (same model, different implementation)

### Shibuya theme
- https://shibuya.lepture.com/customisation/ — Shibuya theme customisation reference (use WebFetch for research)

### sphinx-design
- https://sphinx-design.readthedocs.io/en/latest/ — Full component inventory for the guidance file reference link

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `doc-writer/skills/setup/defaults/mkdocs-material.qa.md` — Direct template for sphinx.qa.md structure. Three questions (nav style, API ref, rich features) maps cleanly to Sphinx equivalents
- `doc-writer/skills/setup/defaults/mkdocs-material.md` — Direct template for sphinx.md section headings and prose style
- `doc-writer/skills/setup/SKILL.md` Step 2b — The built-in framework detection block (`if doc_system is mkdocs-material`) needs a parallel `if doc_system is sphinx-shibuya` block. Same pattern, different config file name (`conf.py` vs `mkdocs.yml`)

### Established Patterns
- `.qa.md` format: Detection section (config file + features to detect) + numbered questions with header/question/detect_context/options/recommend_if — exact format must be replicated for sphinx
- Scaffold template: written as a file with `{template_variable}` placeholders, read and interpolated by setup skill during Step 2b.3 full scaffold mode
- Guidance file style: opinionated preferences, not syntax references. Sections named by feature category, each bullet is a "do this, not that" rule with rationale

### Integration Points
- Setup skill Step 2b option list — add `{ label: "sphinx-shibuya", description: "Sphinx with Shibuya theme" }` to the doc system choices
- `framework_root` logic — sphinx-shibuya is a built-in, so `framework_root` = `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults` (same as mkdocs-material)
- Step 2b.3 detection: check for `conf.py` (project root) or `docs/conf.py`

</code_context>

<specifics>
## Specific Ideas

- Shibuya reference config: https://shibuya.lepture.com/customisation/ — use for scaffold `html_theme_options` defaults
- Google docstring style is already the standard in mkdocs-material guidance (mkdocstrings) — sphinx-autoapi should match to keep the ecosystem consistent
- The sphinx-design docs link (https://sphinx-design.readthedocs.io/en/latest/) belongs in the guidance file so agents can self-serve the full component inventory when writing pages that might benefit from richer layout
- The `autoapi.extension` replaces the Reference tab entirely — the Author agent should explicitly be told not to create manual reference pages when autoapi is enabled

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-sphinx-shibuya-doc-framework-support-with-top-tabs-3-level-nav-sphinx-design-and-sphinx-autoapi-extensions*
*Context gathered: 2026-03-18*
