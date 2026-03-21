# Project Research Summary

**Project:** doc-writer v1.4.0 — Content & Navigation
**Domain:** Claude Code plugin — AI-assisted documentation generation
**Researched:** 2026-03-21
**Confidence:** HIGH

## Executive Summary

Doc-writer v1.4.0 is a focused feature milestone on an existing, working plugin. The research covers six discrete features: Use Cases capture and optional docs section, three-strategy navigation for both Sphinx-Shibuya and MkDocs-Material, mermaid diagram awareness in the doc-author agent, and full OCaml/odoc gap closure (scan-exports, .mld/.mli output format switching). The stack impact is minimal — only one new dependency across all features (`sphinxcontrib-mermaid >= 2.0.1` for Sphinx). All other features are guidance, configuration, and agent-behavior changes to existing files. The existing pipeline architecture has clean extension points that accommodate five of the six features without new patterns; only the OCaml format-switching feature requires a genuinely new code path.

The recommended build order is from lowest to highest complexity and blast radius: Concepts page guidance (smallest, pure addition), then Mermaid awareness (guidance only), then Nav strategy refinement (modifies existing Q&A files), then Use Cases Q&A capture, then Use Cases docs section (depends on Q&A), and finally OCaml .mld/.mli output format switching last because it is the highest-risk change — requiring a parallel output pipeline in doc-author, changes to the editor's file discovery and syntax handling, and a new internal notes mechanism for .mld files. The OCaml feature should not block any other work and should be sequenced last.

The top risks are (1) the editor's Diataxis Type Integrity pass rejecting Use Cases pages as type blur, (2) the doc-author silently writing `.md` instead of `.mld` for odoc projects, and (3) mermaid syntax portability across three different wrapper formats. All three risks are preventable by modifying the right files before content generation is attempted — none require architectural redesign. The critical "looks done but isn't" failure mode to watch for is the doc-author writing correct odoc syntax but forgetting to register pages in `doc/dune`, which produces silent missing-page failures with no build error.

---

## Key Findings

### Recommended Stack

The v1.4.0 milestone adds exactly one new dependency: `sphinxcontrib-mermaid >= 2.0.1` (released 2026-03-05), which provides mermaid diagram rendering in Sphinx with native Shibuya dark/light mode integration. All other features — MkDocs-Material nav tabs, GitHub mermaid, OCaml .mld generation — require zero new libraries. MkDocs-Material already has mermaid support via the existing `pymdownx.superfences` custom fence config already in the scaffold. GitHub renders mermaid natively. Odoc has no mermaid support and requires a guidance-only workaround.

**Core technologies:**
- `sphinxcontrib-mermaid >= 2.0.1`: Mermaid rendering in Sphinx — only new pip dependency; Shibuya has built-in dark/light theme support
- Shibuya `nav_links.children`: Dropdown nav menus — existing Shibuya feature not yet used; zero new libraries
- MkDocs-Material `navigation.tabs` + `navigation.tabs.sticky`: Tab-based nav — existing feature flags; zero new libraries
- MkDocs-Material `navigation.indexes`: Section landing pages — existing feature flag; zero new libraries

**What NOT to add:**
- `mkdocs-mermaid2-plugin` — redundant; `pymdownx.superfences` already handles mermaid in mkdocs-material
- `odoc-mermaid-extension` — experimental, not on opam stable, not production-ready
- `myst-parser` for Sphinx — locked decision: RST-native only, no Markdown in Sphinx
- Multiple scaffold variants per nav strategy — keep one scaffold per framework; handle nav strategy via variable substitution in setup SKILL.md

### Expected Features

**Must have (table stakes):**
- OCaml/odoc scan-exports.sh language case — gap detection is silently broken for all OCaml projects without it; low complexity fix
- OCaml/odoc doc-author .mld output — writing `.md` to an odoc project produces output unparseable by `dune build @doc`; medium complexity but blocking for odoc users
- Mermaid diagram awareness in doc-author — mermaid is standard in docs-as-code in 2026; guidance-only change per framework
- Section index / landing pages with abstracts — tab-based nav requires index pages; users navigating tabbed docs expect them

**Should have (competitive differentiators):**
- Three nav strategies with smart Q&A recommendation (no tabs / single Docs tab / sections-as-tabs) — most tools offer one approach; right-sized nav for any project scale
- Use Cases Q&A capture feeding persona scenarios and page inventory — Stripe/Twilio-style use-case-driven docs at setup time
- Concepts page sub-template under Explanation — structured "What is X?" pages, contextual rather than glossary-style
- Diagram type recommendation engine — recommends WHICH diagram type fits the content (sequence for API flows, state for lifecycle, class for type hierarchies)

**Defer (v2+):**
- Glossary page generation — low value for library docs; Concepts pages serve the need better with context and examples
- Per-page diagram style configuration — premature; let doc-author decide based on content type first; add configurability if users request it
- Auto-generated mermaid diagrams from source code — noisy, drift-prone, serves the builder's mental model rather than the reader's

### Architecture Approach

The existing architecture has three clean extension points: the setup Q&A flow (new questions, new config fields), guidance files (new sections per framework), and agent prompt files (new behavioral sections). Five of the six features slot entirely into these extension points with no new files or patterns. The exception is OCaml .mld/.mli output, which requires a format-detection branch in the doc-author, changes to the editor's file discovery and syntax handling, and a new external notes file (`.doc-writer/author-notes.md`) to replace HTML comment-based internal notes that are invalid in `.mld` syntax.

**Major components touched:**
1. `agents/doc-author.md` — touched by all six features; the primary hotspot; build features that modify it sequentially not in parallel
2. `skills/setup/SKILL.md` + `config-template.yaml` — new Use Cases setup step and config field
3. `{framework}.md` + `{framework}.qa.md` guidance files — nav strategy expansion and mermaid sections across all four frameworks
4. `agents/doc-editor.md` — must recognize `(use-case)` page type in Pass 2 and `.mld` file format in file discovery
5. `skills/write/scripts/scan-exports.sh` — new OCaml language case scanning `.mli` public symbols

**Key patterns to follow:**
- Nav strategy answers flow through researcher into `context.md`, NOT into `config.yaml` — follows the existing Q&A data flow pattern used by all framework preferences
- Use Case template belongs in `doc-author.md` as a new section (parallel to README/MAINTAINER templates), NOT in `skills/diataxis/references/` — use cases are explicitly not a diataxis type
- Odoc syntax knowledge stays in `odoc.md` guidance file; doc-author reads it at runtime rather than hard-coding syntax in the agent prompt
- One scaffold template per framework — extend setup SKILL.md variable substitution for nav strategy rather than multiplying scaffold files

### Critical Pitfalls

1. **Editor Type Integrity pass rejects Use Cases pages** — doc-editor's Pass 2 (Diataxis blur detection) has no slot for `(use-case)` type; it will misclassify pages or attempt to load a nonexistent reference file. Prevention: add `(use-case)` to the recognized type set and extend the existing `(readme)` / `(maintainer)` bypass before any Use Cases pages go through the pipeline.

2. **Doc-author writes `.md` instead of `.mld` for odoc projects** — Markdown syntax is unparseable by `dune build @doc`; every heading, code block, link, and cross-reference uses completely different syntax. Recovery cost is HIGH (full rewrite; no mechanical conversion via md2mld without losing cross-references). Prevention: add output format detection to doc-author in Phase 1 (read `doc_system`, set `output_format`), and create `.mld` structural templates before content generation begins.

3. **Mermaid syntax portability** — three different wrappers required: `` ```mermaid `` fenced block (MkDocs/GitHub), `.. mermaid::` RST directive (Sphinx), `{v ... v}` verbatim with external SVG (odoc). Writing the wrong wrapper silently produces raw text or code blocks. Prevention: add a "Mermaid Diagrams" section to each framework's guidance file before wiring doc-author mermaid awareness.

4. **Sphinx nav_links and toctree are parallel, disconnected layers** — Shibuya's `nav_links` do not derive from the toctree; they are static URL lists in `conf.py` with no build-time validation. Restructuring pages silently breaks dropdown child URLs. Prevention: document the two-layer model explicitly in the Sphinx-Shibuya guidance file; treat nav_links children URLs as hard-coded references that must be updated atomically with any page restructuring.

5. **MkDocs-Material tabs require second-level nav items** — a top-level tab section with no child pages renders an empty sidebar (confirmed issue #197). Single-page sections must be folded into a parent section or given additional pages before tabs are enabled. Prevention: add a post-plan validation check after page inventory approval; verify every proposed tab section has at least 2 child pages.

---

## Implications for Roadmap

Based on combined research, the recommended phase structure builds from zero-risk additions through medium-risk modifications to the highest-risk new patterns. All phases modify `doc-author.md` — sequence phases to avoid parallel conflicts on that file.

### Phase 1: Foundations
**Rationale:** These features are fully independent, have no dependencies, and are pure additions with zero risk of breaking existing behavior. Building them first establishes the guidance-file-first pattern before touching shared agent files.
**Delivers:** Concepts page sub-template under Explanation, scan-exports OCaml language case, mermaid diagram awareness in doc-author and all four framework guidance files
**Addresses:** Concepts page template (P1), OCaml scan-exports.sh (P1), mermaid awareness in doc-author (P2)
**Avoids:** Establishes the guidance-file-first approach that Phase 4 relies on for odoc mermaid guidance; no blast radius on shared files

### Phase 2: Navigation
**Rationale:** Nav strategy refinement modifies existing Q&A files and scaffolds — no new patterns, established Q&A data flow, medium complexity. Must complete before section indexes (also in this phase) because section index page generation requires knowing the nav strategy. Both mkdocs-material and sphinx-shibuya nav strategies should ship together to prevent half-complete guidance state.
**Delivers:** Three nav strategies for both MkDocs-Material and Sphinx-Shibuya, updated Q&A questions, scaffold template updates with nav strategy processing, section index pages with abstracts
**Addresses:** Nav strategy selection (P1), section index pages + abstracts (P2)
**Avoids:** Pitfall 4 (Sphinx nav_links/toctree disconnect) and Pitfall 5 (MkDocs single-page tabs) — prevention guidance and post-plan validation ship in this phase

### Phase 3: Use Cases
**Rationale:** Feature 1 (Use Cases Q&A capture) must come before Feature 2 (Use Cases docs section). Combined in one phase because Feature 2 has no value without Feature 1's data. Use Cases setup Q&A follows the exact same persona → config → researcher → context.md pipeline already established by User Personas — no novel architecture.
**Delivers:** Use Cases Q&A step in setup flow (after persona definition, optional and skippable), `use_cases` config field, researcher expansion in context.md, `(use-case)` page type in doc-author with template section, `(use-case)` type bypass in editor Pass 2
**Addresses:** Use Cases Q&A capture (P1), Use Cases optional docs section (P2)
**Avoids:** Pitfall 1 (editor type integrity rejection) — `(use-case)` type bypass ships as part of this phase, not separately after; avoids the failure mode where Use Cases pages are written before the editor recognizes the type

### Phase 4: OCaml / Odoc Gap Closure
**Rationale:** The highest-risk and most complex feature. Requires a parallel output format in doc-author (branching on `doc_system == "odoc"`), changes to the editor's file discovery and syntax handling for `.mld`, persona tester changes for `.mld` discovery, and a new external notes file mechanism for author-to-editor communication. Sequenced last to avoid blocking all other phases and to allow testing the simpler phases before touching the riskiest component (doc-author has six changes across this milestone).
**Delivers:** doc-author `.mld` output mode with dune registration automation, `.mld` structural templates per diataxis type, `.mli` doc comment enrichment, editor `.mld` file discovery and odoc syntax handling, persona tester `.mld` discovery, external `.doc-writer/author-notes.md` for odoc projects
**Addresses:** OCaml doc-author .mld/.mli handling (P2) — scan-exports is already delivered in Phase 1
**Avoids:** Pitfall 2 (doc-author writes .md for odoc) and Pitfall 6 (heading hierarchy violations) — `.mld` structural templates with heading validation checklist and dune registration step ship with this phase

### Phase Ordering Rationale

- Phase 1 before everything because guidance-file additions have zero blast radius; establishing the mermaid guidance pattern first means Phase 4 can reference it for odoc mermaid guidance without duplication
- Phase 2 before Phase 3 because nav strategy determines whether section indexes are needed, and Use Cases section placement in the nav requires knowing which nav strategies are available
- Phase 3 after Phase 2 because the Use Cases optional docs section needs to know how to integrate with the three nav strategies (e.g., where to place a Use Cases section in tabs vs flat sidebar)
- Phase 4 last because it touches the most files across the system and requires the most new patterns; doing it last prevents it from blocking other phases and ensures the surrounding system is stable before the highest-risk change
- `doc-author.md` is touched by all four phases — build within each phase sequentially; assign each phase a distinct numbered section in the agent prompt to minimize conflicts

### Research Flags

Phases likely needing `/gsd:research-phase` during planning:
- **Phase 4 (OCaml):** The `.mli` doc comment enrichment output format is unresolved — ARCHITECTURE.md recommends "propose doc comment additions as patches or complete comment blocks" but does not specify the exact format. Needs design-phase decision before implementation.
- **Phase 2 (Nav):** Scaffold template variable substitution for nav strategy needs confirmation that the existing setup SKILL.md processing logic can handle conditional sections without restructuring the scaffold generation step. Low risk but worth confirming before writing the implementation plan.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundations):** All findings are HIGH confidence from official docs. Mermaid syntax, Concepts diataxis placement, and scan-exports shell scripting are all well-documented.
- **Phase 3 (Use Cases):** Follows the exact same Q&A → config → researcher → context.md pipeline as User Personas. No novel patterns.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All findings verified via WebFetch on official docs. One new dependency (sphinxcontrib-mermaid 2.0.1) verified on PyPI. No speculative additions. |
| Features | MEDIUM-HIGH | Core features verified against official docs and diataxis framework. Use Cases Q&A design is a pattern recommendation grounded in Stripe/Twilio doc structures and diataxis creator's explicit statements, not a single authoritative source. |
| Architecture | HIGH | All findings derived from reading the actual codebase. Extension points are confirmed by existing agent prompt structure. No speculative architecture. |
| Pitfalls | MEDIUM-HIGH | Critical pitfalls (editor type rejection, .md vs .mld, mermaid portability) verified by reading agent prompt source. MkDocs-Material single-page tab issue verified via official GitHub issue tracker. Sphinx nav_links disconnect verified via official Shibuya docs and changelog. |

**Overall confidence:** HIGH

### Gaps to Address

- **`.mli` enrichment output format:** ARCHITECTURE.md recommends "propose doc comment additions as patches or complete comment blocks" but does not specify the exact format (inline patch file vs. annotated code comments vs. separate file). Resolve in Phase 4 planning — recommended direction is complete comment blocks inserted above undocumented declarations, matching the pattern of existing `.mli` doc comments in the project.
- **Scaffold nav strategy processing:** The setup SKILL.md variable substitution step needs to handle nav strategy as a conditional parameter. The existing mechanism has not been tested with conditional sections. Low risk — the skill already processes template variables — but worth confirming the approach before writing the Phase 2 implementation plan.
- **Use Cases Q&A position:** PITFALLS.md and ARCHITECTURE.md have a minor conflict on ordering. ARCHITECTURE.md originally suggested Use Cases Q&A before persona definition (use cases inform persona quality). PITFALLS.md says after persona definition (persona `user_tasks` already captures task-oriented use cases; Use Cases Q&A can extend rather than duplicate them). PITFALLS.md's rationale is stronger. **Recommendation: Use Cases Q&A goes AFTER persona definition**, presented as optional with a clear skip path. Total new questions for the milestone should not exceed 2 to avoid turning setup into an interrogation.

---

## Sources

### Primary (HIGH confidence)
- [Shibuya navbar docs](https://shibuya.lepture.com/customisation/navbar/) — nav_links children/summary/external/resource fields
- [Shibuya mermaid docs](https://shibuya.lepture.com/extensions/mermaid/) — sphinxcontrib-mermaid integration with Shibuya theme
- [Shibuya changelog](https://shibuya.lepture.com/changelog/) — children links added 2023.6.7; keyboard accessibility 2025.7.24
- [MkDocs-Material navigation docs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/) — navigation.tabs, navigation.tabs.sticky, navigation.sections, navigation.indexes
- [MkDocs-Material diagrams docs](https://squidfunk.github.io/mkdocs-material/reference/diagrams/) — mermaid config via pymdownx.superfences
- [MkDocs-Material Issue #197](https://github.com/squidfunk/mkdocs-material/issues/197) — tabs require second-level nav items
- [MkDocs-Material Issue #2125](https://github.com/squidfunk/mkdocs-material/issues/2125) — top-level pages behavior change at 6.2.0
- [GitHub diagrams docs](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams) — native mermaid in GitHub markdown
- [sphinxcontrib-mermaid PyPI](https://pypi.org/project/sphinxcontrib-mermaid/) — version 2.0.1 released 2026-03-05
- [sphinxcontrib-mermaid 2.0 docs](https://sphinxcontrib-mermaid-demo.readthedocs.io/en/latest/) — full config reference
- [odoc for authors](https://ocaml.github.io/odoc/odoc/odoc_for_authors.html) — .mld/.mli syntax, heading levels, code blocks, cross-refs
- [Dune documentation stanza](https://dune.readthedocs.io/en/stable/documentation.html) — mld_files registration
- [Diataxis framework](https://diataxis.fr/) — quadrant definitions; explicit rejection of 5th type
- [Diataxis complex hierarchies](https://diataxis.fr/complex-hierarchies/) — landing page patterns
- [Diataxis GitHub Discussion #36](https://github.com/evildmp/diataxis-documentation-framework/discussions/36) — creator's rejection of 5th type
- Existing codebase: `agents/doc-author.md`, `agents/doc-editor.md`, `skills/setup/SKILL.md`, `skills/write/scripts/scan-exports.sh`, all `{framework}.md` guidance files, all `{framework}.qa.md` files, scaffold templates, `skills/setup/defaults/config-template.yaml`

### Secondary (MEDIUM confidence)
- [odoc 3.1.0 package docs](https://ocaml.org/p/odoc/latest/doc/odoc_for_authors.html) — latest odoc authoring guide
- [sphinxcontrib-mermaid GitHub README](https://github.com/mgaitan/sphinxcontrib-mermaid) — output formats (raw/svg/png), mermaid-cli requirements
- [md2mld](https://github.com/mseri/md2mld) — markdown to .mld conversion limitations; heading level constraints
- [OCaml discuss: 2025 documentation best practices](https://discuss.ocaml.org/t/2025-documentation-best-practices/17008) — community consensus on .mli documentation

### Tertiary (MEDIUM-LOW confidence)
- [Stripe/Twilio documentation patterns](https://devdocs.work/post/stripe-twilio-achieving-growth-through-cutting-edge-documentation) — use-case-driven doc structure; supports Use Cases Q&A design decision but is a secondary source

---
*Research completed: 2026-03-21*
*Ready for roadmap: yes*
