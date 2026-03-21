# Pitfalls Research: v1.4.0 Content & Navigation

**Domain:** Adding content types, nav structures, mermaid diagrams, and OCaml gap closure to existing doc-writer plugin
**Researched:** 2026-03-21
**Confidence:** MEDIUM-HIGH (mix of codebase-verified and web-verified findings)

## Critical Pitfalls

### Pitfall 1: Editor Type Integrity Pass Rejects Non-Diataxis "Use Cases" Pages

**What goes wrong:**
The doc-editor agent's Pass 2 (Diataxis Type Integrity) classifies every page by its declared type -- tutorial, how-to, explanation. It then runs blur detection against that type's reference file. A "Use Cases" page has no Diataxis type, no reference file, and no blur detection criteria. The editor will either (a) fail to classify it and skip it entirely, (b) misclassify it as how-to or explanation and flag false-positive blur, or (c) attempt to load `skills/diataxis/references/use-cases.md` which does not exist.

The doc-author agent has the same problem: Phase 2 loads a Diataxis reference file per page type. The page inventory in Phase 1 only accepts types `tutorial`, `how-to`, `explanation`, `(readme)`, `(maintainer)`. There is no slot for "use-cases" in the inventory classification.

**Why it happens:**
The entire pipeline -- author, editor, persona -- is built around Diataxis as the single type system. Adding a content type that lives outside the four Diataxis quadrants requires explicit exemption paths in every agent that touches page classification.

**How to avoid:**
1. Define "use-cases" as a recognized page type in the inventory, alongside the existing Diataxis types and the special `(readme)` / `(maintainer)` types.
2. Create a `use-cases.md` reference file under `skills/diataxis/references/` (or a separate `skills/content-types/references/` directory) that gives the author structural guidance for Use Cases pages -- template, writing style, quality checklist.
3. In the editor's Pass 2, add an explicit bypass for non-Diataxis types: skip blur detection for `use-cases`, `(readme)`, and `(maintainer)` pages. The editor already skips README/MAINTAINER -- extend that pattern.
4. In the editor's Pass 2 Step 2, when checking for declared type, add `use-cases` to the recognized set so it does not fall through to the "infer from structure" path.
5. The doc-author's Page Classification internal note must declare `Type: use-cases` and `Reference used: skills/content-types/references/use-cases.md` so the editor knows to skip blur detection.

**Warning signs:**
- Editor report shows BLOCKING "Type blur" on every Use Cases page
- Author agent tries to load a nonexistent reference file and produces malformed output
- Page inventory shows "use-cases" pages classified as "how-to" with incorrect structural templates applied

**Phase to address:**
The phase that adds Use Cases as a content type. Must be implemented before any Use Cases pages are written through the pipeline.

---

### Pitfall 2: Sphinx-Shibuya nav_links and Toctree Operating as Parallel, Disconnected Navigation Layers

**What goes wrong:**
Shibuya's `nav_links` in `html_theme_options` are a manually configured top navbar -- they do not derive from or synchronize with the Sphinx toctree. Developers assume that adding a section to the toctree automatically creates a top tab, or that adding a nav_link automatically populates the sidebar. Neither is true. The result: top tabs link to pages that have empty sidebars (no toctree children), or the sidebar shows sections that have no corresponding top tab.

With dropdown menus (`children` on nav_links), the disconnect compounds. Dropdown children are static URL lists in conf.py. If you restructure the toctree (move pages, rename files), the dropdown URLs break silently -- there is no build-time validation of nav_links URLs.

The Shibuya changelog confirms these are independent systems: `children` navbar links were added in 2023.6.7, `toctree_maxdepth` was added separately in 2025.1.29. No integration layer exists between them.

**Why it happens:**
Shibuya's `nav_links` was designed as a simpler alternative to toctree-derived navigation, not as a toctree overlay. They are configured in Python (conf.py `html_theme_options`) while toctree is configured in RST files. Two configuration surfaces, no synchronization.

**How to avoid:**
1. In the sphinx-shibuya guidance file, explicitly document the two-layer model: nav_links control the top bar, toctree controls the sidebar. They must be kept in sync manually.
2. When the doc-author proposes a nav structure with "sections-as-tabs with dropdowns," the guidance must instruct: each nav_link URL must point to an actual section index.rst that has its own toctree. The dropdown children URLs must match actual file paths.
3. Add a validation step to the doc-researcher or setup flow: after scaffold generation, verify that every nav_links URL resolves to an existing .rst file and that every section toctree has a corresponding nav_link.
4. Document that nav_links `url` values are relative to the doc root and do NOT include `.html` extension (Shibuya appends it unless `resource: True` is set).
5. nav_links only support one level of nesting (`children`). There is no deeper dropdown. Do not design nav structures expecting multi-level dropdowns.
6. Dropdown `children` have an optional `summary` field (brief description). Keep summaries under 80 characters -- they render in a compact dropdown card.

**Warning signs:**
- Top tabs work but clicking them shows an empty sidebar
- Sidebar shows correct hierarchy but top tabs are missing or link to 404s
- Dropdown menus contain stale URLs after page restructuring
- Build succeeds with zero warnings (Sphinx does not validate nav_links URLs)

**Phase to address:**
The phase implementing sphinx-shibuya nav strategies. The guidance file update and validation step should ship together.

---

### Pitfall 3: MkDocs-Material Tabs Requiring Second-Level Nav Items

**What goes wrong:**
When `navigation.tabs` is enabled in mkdocs-material, every top-level nav entry becomes a tab. But if a top-level entry has no second-level items (no child pages), the tab renders but produces an empty sidebar with no content. mkdocs-material Issue #197 documents this: tabs cannot handle top-level entries without second-level markdown files.

For the doc-writer plugin, this means a "Use Cases" section with a single page (no subsections) would create a broken tab. A "Concepts" section with just one explanation page would have the same problem.

Additionally, prior to version 6.2.0, all top-level pages were grouped under the first tab. From 6.2.0 on, all top-level pages and sections become distinct tabs (Issue #2125). This means adding too many top-level sections can create excessive tabs that overflow on narrow viewports (tabs only display above 1220px viewport width; below that, they collapse to standard mobile nav).

**Why it happens:**
mkdocs-material tabs are structurally a grouping mechanism. A tab without children is like a folder with no files -- it renders but has no navigation content. The tab-to-sidebar relationship requires at least one level of nesting beneath each tab.

**How to avoid:**
1. When the doc-author proposes a tab-based nav structure, verify every tab section has at least 2 pages. Single-page sections should be folded into a parent section, not given their own tab.
2. In the nav strategy Q&A, add a guardrail: "Tabs + sections" should recommend a minimum of 3 top-level sections with 2+ pages each. Below that threshold, recommend "Sections" only.
3. Add a post-plan validation: after the page inventory is approved, check whether the proposed nav structure creates any single-page tabs. If so, warn the user.
4. The Use Cases section specifically should be placed under a broader grouping (e.g., nested under "Guides" or alongside How-To Guides) unless it has enough pages to stand alone.
5. When both `navigation.tabs` and `navigation.sections` are enabled, tabs consume level 1 and sections apply to level 2. Design the hierarchy knowing this: tabs are the outermost grouping.

**Warning signs:**
- Tab bar renders but clicking a tab shows blank sidebar
- Tab count exceeds 5-6 items, causing horizontal overflow
- `navigation.tabs` behavior changes if the mkdocs-material version is pre-6.2.0
- Mobile view does not show tabs (below 1220px) -- navigation still needs to work without them

**Phase to address:**
The phase implementing mkdocs-material nav strategies. Must validate proposed nav against tab structure requirements.

---

### Pitfall 4: Doc-Author Writing .md When It Should Write .mld for Odoc Projects

**What goes wrong:**
The doc-author agent currently writes all output as `.md` files to `paths.docs_root`. For odoc projects, the output should be `.mld` files in `doc/` with odoc markup syntax (`{0 Title}`, `{[ code ]}`, `{!cross-ref}`), not Markdown syntax (`# Title`, fenced code blocks, `[link](url)`). PROJECT.md explicitly calls this out as a known issue: "doc-author has no .mld/.mli file handling for odoc projects (writes .md to docs_root instead of .mld to doc/)."

The syntax difference is fundamental -- every construct differs:

| Concept | Markdown | odoc .mld |
|---------|----------|-----------|
| Page title | `# Title` | `{0 Package - Title}` |
| Section | `## Section` | `{1 Section}` |
| Code block | `` ```ocaml `` | `{[ code ]}` |
| Verbatim | `` ```bash `` | `{v command v}` |
| Bold | `**text**` | `{b text}` |
| Italic | `*text*` | `{i text}` |
| Link | `[text](url)` | `{{:url} text}` |
| Cross-ref | `[text](path)` | `{!Module.value}` |
| List item | `- item` | `{- item}` |

Writing Markdown to an odoc project means the entire file is unparseable by `dune build @doc`.

**Why it happens:**
The doc-author was built for Markdown-based doc systems. Odoc uses a completely different markup language. The author's code example rules, structural templates, and output format all assume Markdown.

**How to avoid:**
1. Add output format detection to the doc-author: when `doc_system` is `odoc`, switch to .mld output format.
2. Create structural templates for .mld page types (tutorial.mld, how-to.mld, explanation.mld) that mirror the Diataxis templates but use odoc syntax.
3. The file path logic must change: odoc pages go to `doc/` (the dune documentation stanza directory), not `paths.docs_root` which might be `docs/`.
4. Every code block must use `{[ ... ]}` for OCaml and `{v ... v}` for non-OCaml. The "always specify language on fenced code blocks" rule needs an odoc equivalent: "always use the correct block type."
5. After writing each .mld file, add it to the `(mld_files ...)` list in `doc/dune`. This is the single most common reason for missing pages in odoc projects.
6. .mld filenames must use underscores only -- never hyphens. The doc-author's file path inference (which might generate `getting-started.mld`) must be overridden to produce `getting_started.mld`.

**Warning signs:**
- `dune build @doc` fails with syntax errors on every generated page
- Pages appear as raw text in the HTML output instead of rendered content
- Cross-references show `{!Module.value}` as literal text
- Generated pages missing from navigation (not registered in dune)

**Phase to address:**
The phase implementing OCaml/odoc gap closure. This is the highest-risk change in the milestone because it requires a parallel output pipeline, not a patch to the existing one.

---

### Pitfall 5: Mermaid Syntax Portability -- Three Systems, Three Wrappers

**What goes wrong:**
The doc-author writes mermaid diagrams using one syntax, but each doc system needs a different wrapper:

- **GitHub/plain-markdown:** `` ```mermaid `` fenced code block (rendered natively by GitHub)
- **MkDocs-material:** `` ```mermaid `` fenced code block (rendered by pymdownx.superfences custom fence, requires specific mkdocs.yml config)
- **Sphinx:** `.. mermaid::` RST directive (rendered by sphinxcontrib-mermaid extension)
- **Odoc:** No native mermaid support. Must use `{v ... v}` verbatim block (no rendering) or generate SVG externally.

If the doc-author writes mermaid using the GitHub/MkDocs fence syntax in a Sphinx project, the diagram renders as a raw code block. If it writes the Sphinx directive in a MkDocs project, the directive renders as literal text.

Additionally, the rendering engine matters:
- MkDocs-material uses client-side JS rendering with automatic theme integration (fonts, colors sync with mkdocs.yml). Fully supported diagram types: flowcharts, sequence, state, class, ER. Partially supported: pie, gantt, user journey, git graphs (they work but do not adapt to mobile or theme changes well).
- sphinxcontrib-mermaid has three output modes: `raw` (client-side JS, like MkDocs), `svg` (build-time via mermaid-cli), `png` (build-time via mermaid-cli). Non-raw modes require `npm install -g @mermaid-js/mermaid-cli`. PDF generation requires svg/png mode -- raw does not work for LaTeX/PDF builders.
- GitHub renders natively -- no configuration needed, but no theme control.

The mermaid diagram content itself (the flowchart/sequence/state syntax) is portable. Only the wrapper differs.

**Why it happens:**
Mermaid rendering is handled by different extension/plugin mechanisms per doc system. There is no universal wrapper syntax. The doc-author needs to consult the doc-system guidance file to determine the correct wrapper.

**How to avoid:**
1. Add mermaid wrapper syntax to each doc-system guidance file. The author loads the guidance file already -- add a "Mermaid Diagrams" section showing the correct syntax.
2. For MkDocs-material: document the required `pymdownx.superfences` custom fence config in the guidance file. The setup scaffold should include this if mermaid is selected during Q&A.
3. For Sphinx-shibuya: add `sphinxcontrib-mermaid` to the guidance file with the `.. mermaid::` directive syntax. Recommend `mermaid_output_format = "raw"` for browser-based rendering unless PDF output is needed.
4. For odoc: explicitly state that mermaid is not natively supported. Recommend ASCII art with `{v ... v}` blocks or generating SVG externally. Do not attempt to embed mermaid syntax in .mld files -- it will not render.
5. For plain-markdown/GitHub: the standard `` ```mermaid `` fence works natively.
6. The doc-author's code example rules need a "diagram block" category distinct from "code block" -- diagrams are not code and should not be subjected to code formatting rules (like Black formatting for Python projects).

**Warning signs:**
- Mermaid blocks render as raw text or code blocks instead of diagrams
- Sphinx build fails with "unknown directive" (sphinxcontrib-mermaid not installed)
- MkDocs site shows mermaid syntax but no diagram (superfences custom fence not configured)
- Dark/light mode mismatch: mermaid themes not synced with doc site theme
- PDF build shows empty spaces where diagrams should be (raw mode used for LaTeX)

**Phase to address:**
The phase adding mermaid diagram awareness. Must update guidance files for all four doc systems before the doc-author can produce correct output.

---

### Pitfall 6: OCaml .mld Heading Level Rules Causing Silent Build Failures

**What goes wrong:**
In .mld files, `{0 Title}` is reserved for the page title and can appear only once, only in .mld files (never in .mli comments). All subsequent headings must be `{1 ...}`, `{2 ...}`, `{3 ...}`. If the doc-author generates a page with two `{0}` headings, or uses `{0}` in an .mli doc comment, `dune build @doc` fails with "heading level should be lower than top heading level '0'."

Additionally, heading levels must be strictly hierarchical. You cannot jump from `{1}` to `{3}` -- odoc requires `{1}` then `{2}` then `{3}`. Markdown allows `# -> ###` skipping; odoc does not.

In .mli doc comments, headings start at `{1}` (not `{0}`, which is reserved for .mld page titles). Code blocks in .mli comments must start at column 0 -- leading indentation causes parse errors.

**Why it happens:**
The doc-author generates content using Diataxis structural templates, which use Markdown heading levels (`#`, `##`, `###`). Converting to .mld headings requires both syntax changes and structural validation. An LLM generating .mld content may produce headings that look right but violate the strict hierarchy rules, especially when adapting Markdown templates that skip levels.

**How to avoid:**
1. The .mld structural templates must enforce: exactly one `{0}` heading per page (the title), followed by `{1}` sections, `{2}` subsections, `{3}` sub-subsections. No gaps in levels.
2. Add a self-verification checklist item for odoc pages: "Heading levels are contiguous (no jumps from {1} to {3})."
3. In .mli doc comments, headings start at `{1}` -- never `{0}`. The doc-author must know the file type context (.mld vs .mli) when generating headings.
4. Code blocks in .mli comments (`{[ ... ]}` and `{v ... v}`) must start at column 0 inside the doc comment -- not indented to match the surrounding OCaml code.
5. Recommend running `dune build @doc` as a validation step after writing. The existing odoc guidance already recommends this, but it should be treated as a hard gate, not a suggestion.

**Warning signs:**
- `dune build @doc` fails with heading level errors
- Generated .mld files have `{0}` appearing mid-page
- .mli doc comments use `{0}` headings (invalid)
- Code blocks in .mli comments fail to parse due to indentation

**Phase to address:**
Same phase as OCaml/odoc gap closure. The .mld templates must be validated before any content is generated.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-coding "use-cases" bypass in editor Pass 2 instead of generalizing non-Diataxis type support | Fast to implement, unblocks Use Cases | Each future non-Diataxis type needs another bypass; editor becomes a maze of special cases | MVP only -- generalize to a "custom types" registry before adding a third non-Diataxis type |
| Generating mermaid diagrams without checking if the doc system supports them | Author can add diagrams to any page | Sphinx projects without sphinxcontrib-mermaid get raw text; odoc projects get no rendering at all | Never -- always check guidance file for mermaid support before adding diagrams |
| Writing .mld files without updating doc/dune mld_files list | Faster generation, skip dune file parsing | Pages silently missing from generated docs -- no error, no warning, just invisible | Never -- the dune registration must happen atomically with file creation |
| Using md2mld to convert existing .md output to .mld instead of native .mld generation | Reuses existing Markdown pipeline | md2mld has heading level limitations (minimum header level 3 without -min-header flag), loses cross-reference semantics, produces inferior .mld lacking odoc idioms | Never for production; acceptable only as a debugging comparison tool |
| Putting Use Cases Q&A before User Personas in setup flow | Captures use cases early for persona inference | Breaks the existing flow where personas inform all downstream decisions; use cases without persona context produce less useful results | Never -- use cases should come after personas, feeding into the researcher |
| Adding mermaid config to scaffolds without checking if user selected mermaid | Simpler scaffold generation | Projects get mermaid extension installed that they do not use; adds dependencies and config complexity | Never -- only add mermaid config when user selects mermaid during setup Q&A |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| sphinx-shibuya nav_links + toctree | Assuming nav_links auto-derive from toctree, or that toctree pages appear as tabs | Configure nav_links manually in conf.py pointing to section index pages; verify each URL matches an actual .rst file with its own toctree |
| sphinx-shibuya dropdown children + page restructuring | Renaming/moving .rst files without updating dropdown children URLs in conf.py | Treat nav_links children URLs as hard-coded; update conf.py atomically with any page restructuring |
| mkdocs-material tabs + navigation.sections | Enabling both without understanding interaction: tabs become top-level, sections apply to level 2 | Design nav hierarchy knowing that tabs consume the first level and sections group the second level; ensure every tab has 2+ child pages |
| mkdocs-material tabs + single pages | Creating top-level nav entries with no children | Every tab must have at least 2 child pages; fold single-page topics into a broader section |
| sphinxcontrib-mermaid output format + PDF | Using "raw" (browser-rendered) then expecting PDF builds to work | Use "raw" for HTML only; switch to "svg" or "png" with mermaid-cli for LaTeX/PDF output |
| sphinxcontrib-mermaid + mermaid-cli | Using svg/png output mode without mermaid-cli installed | Install via `npm install -g @mermaid-js/mermaid-cli`; set `mermaid_cmd` in conf.py if mmdc is not in PATH |
| mkdocs-material mermaid + dark mode | Assuming all diagram types auto-adapt to dark mode | Only flowcharts, sequence, state, class, and ER diagrams get theme-adaptive styling. Pie charts, gantt, git graphs do not. Test dark mode on all diagram types |
| odoc .mld + dune mld_files | Creating .mld file but not registering it in `(mld_files ...)` | Always update doc/dune when creating or renaming .mld files; treat registration as atomic with file creation |
| odoc cross-package .mld references | Using `{!page-name}` for pages in a different package | `{!page-name}` only resolves within the same package; use `{{:../other_package/page.html} text}` for cross-package links |
| odoc .mld filenames | Using hyphens in .mld filenames | Always use underscores: `getting_started.mld` not `getting-started.mld`. Hyphens break `{!page-...}` references because the hyphen is a separator in odoc reference syntax |
| Editor type-integrity pass + non-Diataxis types | Passing "use-cases" pages through blur detection | Add explicit type recognition and blur-skip for non-Diataxis types; extend the existing README/MAINTAINER bypass pattern |
| Setup Q&A + Use Cases capture | Adding Use Cases questions at the start of the Q&A flow | Place Use Cases after User Personas (which provide context) and before Tone selection; present as optional with clear skip path |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Adding 3+ new Q&A questions to setup for Use Cases + nav strategy | Setup flow becomes 15+ questions; feels like an interrogation instead of configuration | Group Use Cases as a single optional question with multi-select. Nav strategy is already covered by existing Q&A questions -- extend the options list rather than adding new questions. Target max 2 new questions total for the milestone. |
| Requiring Use Cases before personas are defined | User is asked "what are common use cases?" before they have articulated who uses the library | Place Use Cases after persona definition. The persona's `user_tasks` field already captures task-oriented use cases. Use Cases Q&A can reference and extend what was captured in the persona. |
| Presenting "sections-as-tabs with dropdowns" as a nav option without explaining the complexity | User selects the fancy option, then gets confused when sidebar and tabs do not interact as expected | Show concrete preview or example of what each nav strategy looks like in the final docs. Recommend "Top tabs + sidebar" as default; "sections-as-tabs with dropdowns" only for projects with 5+ major sections and 3+ pages each. |
| Offering mermaid diagrams as a feature without checking doc system support | User enables mermaid in Q&A, author generates diagrams, diagrams render as raw text because extension is not installed | During setup, verify mermaid support: check pymdownx.superfences config (MkDocs), sphinxcontrib-mermaid in extensions (Sphinx). If not configured, offer to add it rather than silently generating unusable diagrams. |
| Concepts page proposal being unconditionally prescriptive | Every project gets a "Concepts" page under Explanation even when the library has no complex concepts worth explaining | Make Concepts proposal conditional: only suggest if the library has complex domain concepts, architectural patterns, or design decisions. Check source code for design doc comments, abstract types, or complex type hierarchies before proposing. |

## "Looks Done But Isn't" Checklist

- [ ] **Use Cases type:** Author generates Use Cases pages AND editor recognizes the type without false blur flags. Test: run full pipeline on a project with Use Cases pages and verify editor report does not show type-blur BLOCKING on those pages.
- [ ] **Sphinx nav_links:** conf.py has nav_links configured AND each URL resolves to an existing .rst AND each section has a toctree AND sidebar populates correctly. Test: click every tab, verify sidebar shows correct section content.
- [ ] **Sphinx dropdown menus:** nav_links with children render as dropdowns AND child URLs resolve AND keyboard navigation works (fixed in Shibuya 2025.7.24). Test: hover over dropdown parent, verify children appear; tab through with keyboard.
- [ ] **MkDocs tabs:** mkdocs.yml has `navigation.tabs` AND every top-level section has 2+ child pages AND tabs render on desktop. Test: resize browser below 1220px, verify mobile nav still works.
- [ ] **MkDocs tabs + sections:** When both features enabled, verify level-2 items render as sections (not collapsible nav). Test: enable both features, check that the visual hierarchy is tab > section > page.
- [ ] **Mermaid in MkDocs:** pymdownx.superfences custom fence configured AND diagrams render (not raw text) AND dark mode works for supported diagram types. Test: switch between light/dark mode on a page with mermaid diagrams.
- [ ] **Mermaid in Sphinx:** sphinxcontrib-mermaid in extensions AND `.. mermaid::` directive renders AND output format matches deployment target (raw for HTML, svg/png for PDF). Test: build HTML and verify diagram renders.
- [ ] **Mermaid in odoc:** Guidance file explicitly states mermaid is unsupported AND doc-author does not attempt to embed mermaid syntax in .mld files. Test: request mermaid diagram for an odoc project; verify author uses alternative (ASCII art or external SVG).
- [ ] **Odoc .mld output:** Doc-author writes .mld (not .md) AND files use odoc syntax AND files are registered in doc/dune AND `dune build @doc` passes AND pages appear in generated HTML. Test: run `dune build @doc` and open `_build/default/_doc/_html/index.html`.
- [ ] **Odoc .mli improvements:** Doc-author adds/improves doc comments on .mli files AND headings use `{1}` not `{0}` AND code blocks use `{[ ... ]}` at column 0 AND cross-references resolve. Test: `dune build @doc` with zero warnings.
- [ ] **Odoc filenames:** All generated .mld files use underscores only. Test: `ls doc/*.mld` and verify no hyphens in any filename.
- [ ] **Setup Q&A flow:** Use Cases question appears after personas AND is skippable AND total new questions do not exceed 2 AND total setup time does not increase significantly. Test: run full setup flow from scratch, count total questions.
- [ ] **Scan-exports OCaml:** scan-exports.sh has an OCaml language case AND detects public values from .mli files AND gap report identifies undocumented symbols. Test: run on an OCaml project with known undocumented symbols.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Editor rejects all Use Cases pages as type blur | LOW | Add the type bypass in the editor. Re-run editor pass only -- author output is fine, just the editor classification needs updating. |
| nav_links URLs do not match toctree structure | LOW | Update conf.py nav_links to match actual file paths. This is a config fix, not a content fix. |
| MkDocs tabs with single-page sections | LOW | Either add more pages to the section or restructure nav to fold single-page sections into parent tabs. Config-only fix in mkdocs.yml. |
| Doc-author wrote .md instead of .mld for odoc project | HIGH | All generated content must be rewritten in odoc syntax. Cannot mechanically convert -- md2mld loses cross-references, has heading level limitations, and produces inferior output. Re-run author in .mld mode from scratch. |
| Mermaid diagrams render as raw text | LOW | Add the mermaid extension to the doc system config (one-line fix). Diagram content itself is fine -- only the wrapper/extension was missing. |
| .mld files not registered in doc/dune | LOW | Add filenames to `(mld_files ...)` in doc/dune. Quick fix, but must be caught -- the failure mode is silent omission with no error or warning. |
| .mld heading hierarchy violations | MEDIUM | Re-generate affected pages with correct heading levels. Cannot sed-fix because level adjustments cascade (promoting one heading may require demoting others). |
| Setup Q&A interrogation effect | MEDIUM | Restructure Q&A to merge Use Cases into existing persona flow. Requires SKILL.md rewrite of question ordering, but no agent prompt changes needed. |
| .mld filenames with hyphens | LOW | Rename files from `getting-started.mld` to `getting_started.mld`. Update all `{!page-...}` references and doc/dune `(mld_files ...)` list. Mechanical but tedious. |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Editor rejects Use Cases type | Use Cases content type implementation | Full pipeline run with Use Cases page: editor report shows no false-positive blur |
| nav_links / toctree disconnect | Sphinx-shibuya nav strategy implementation | Generate docs with all 3 nav strategies; verify tabs + sidebar work in each |
| Sphinx dropdown children stale | Sphinx-shibuya nav strategy implementation | Restructure a page after generation; verify dropdown URLs still resolve |
| MkDocs single-page tabs | MkDocs-material nav strategy implementation | Generate docs with tabs enabled; verify every tab has populated sidebar |
| Doc-author writes .md for odoc | OCaml/odoc .mld handling implementation | `dune build @doc` passes on generated output with zero syntax errors |
| Mermaid syntax portability | Mermaid diagram awareness implementation | Generate mermaid pages for each of the 4 doc systems; verify rendering or graceful fallback in each |
| .mld heading hierarchy | OCaml/odoc .mld handling implementation | `dune build @doc` passes; no heading level warnings |
| .mld filename hyphens | OCaml/odoc .mld handling implementation | All generated .mld filenames contain only underscores |
| Setup Q&A interrogation | Use Cases setup Q&A implementation | Setup flow adds max 2 new questions; Use Cases is after personas and is skippable |
| scan-exports.sh OCaml case | OCaml/odoc scan-exports implementation | Run on OCaml project; verify .mli public values detected |
| Concepts page over-prescription | Default Concepts page proposal implementation | Concepts only proposed when library has sufficient complexity; simple libraries skip it |

## Sources

- [Shibuya theme navbar configuration](https://shibuya.lepture.com/customisation/navbar/) -- nav_links syntax, children/dropdown, summary field, resource flag (MEDIUM confidence, verified via official docs)
- [Shibuya changelog](https://shibuya.lepture.com/changelog/) -- children links added 2023.6.7, toctree_maxdepth 2025.1.29, keyboard accessibility 2025.7.24 (HIGH confidence, official changelog)
- [MkDocs-Material navigation setup](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/) -- tabs behavior, viewport threshold 1220px, tabs+sections interaction (HIGH confidence, official docs)
- [MkDocs-Material Issue #197](https://github.com/squidfunk/mkdocs-material/issues/197) -- tabs require second-level nav items (HIGH confidence, official issue tracker)
- [MkDocs-Material Issue #2125](https://github.com/squidfunk/mkdocs-material/issues/2125) -- top-level pages behavior change at 6.2.0 (HIGH confidence, official issue tracker)
- [MkDocs-Material diagrams reference](https://squidfunk.github.io/mkdocs-material/reference/diagrams/) -- mermaid setup, theming, supported diagram types (HIGH confidence, official docs)
- [sphinxcontrib-mermaid GitHub](https://github.com/mgaitan/sphinxcontrib-mermaid) -- output formats (raw/svg/png), mermaid-cli requirements, directive syntax (MEDIUM confidence, verified via README)
- [Dune documentation stanza](https://dune.readthedocs.io/en/stable/documentation.html) -- mld_files registration, documentation stanza placement, index.mld special handling (HIGH confidence, official docs)
- [OCaml generating documentation guide](https://ocaml.org/docs/generating-documentation) -- odoc + dune workflow (HIGH confidence, official docs)
- [md2mld](https://github.com/mseri/md2mld) -- markdown to .mld conversion limitations, heading level constraints, -min-header flag (MEDIUM confidence, verified via README)
- [odoc for authors](https://ocaml.org/p/odoc/latest/doc/odoc_for_authors.html) -- .mld syntax rules (HIGH confidence, official docs)
- [Diataxis framework](https://diataxis.fr/) -- guidance on non-standard content types: "not every piece of information will fit exactly into one of the diataxis categories" (HIGH confidence, official source)
- Codebase: `doc-writer/agents/doc-editor.md` Pass 2 (Diataxis Type Integrity) -- verified page classification logic and blur detection (HIGH confidence, direct code reading)
- Codebase: `doc-writer/agents/doc-author.md` Phase 1 Step 3 -- verified inventory type constraints: tutorial, how-to, explanation, (readme), (maintainer) (HIGH confidence, direct code reading)
- Codebase: `doc-writer/skills/write/scripts/scan-exports.sh` -- verified no OCaml case exists in the language switch (HIGH confidence, direct code reading)
- Codebase: `doc-writer/skills/setup/defaults/odoc.md` -- verified .mld syntax rules, dune wiring requirements, filename rules (HIGH confidence, direct code reading)
- Codebase: `doc-writer/skills/setup/SKILL.md` -- verified Q&A flow ordering: personas > tone > doc system > paths > researcher (HIGH confidence, direct code reading)

---
*Pitfalls research for: doc-writer v1.4.0 Content & Navigation milestone*
*Researched: 2026-03-21*
