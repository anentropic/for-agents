# Page Inventory: doc-writer docs site

Plan for moving `docs/src/doc-writer.md` (one long page mixing all four Diataxis types) into a
multi-page mkdocs-material site. `docs_dir` is `docs/src`; every page below must be added to `nav:`
in `mkdocs.yml`. Target persona for every page: **Library maintainer using Claude Code** (the only
configured persona). Tone: warm-businesslike.

## Proposed Documentation

| # | Type | Title | Key Sections | File Path |
|---|------|-------|--------------|-----------|
| 1 | (refresh) | Overview (site front page) | Marketplace intro, plugin list with abstract and link to `doc-writer/index.md` (link currently points at `doc-writer.md`), install via `/plugin marketplace add anentropic/for-agents` + `/plugin install doc-writer@anentropic-for-agents` (already correct here) | docs/src/index.md |
| 2 | explanation (section index) | doc-writer | What it does in two sentences, the differentiators (Persona tests docs without source, Editor de-slops and enforces terminology, nothing committed), requirements (Claude Code, optional `python3`), supported doc systems (mkdocs-material, sphinx-shibuya, odoc, plain Markdown), child pages with 1-sentence abstracts | docs/src/doc-writer/index.md |
| 3 | tutorial | Document your first project | Prerequisites, install (marketplace form), `/doc-writer:setup` walkthrough (use cases, personas, tone, doc system, framework/navigation questions, paths), `/doc-writer:write` create mode, approving the page inventory, reading verdicts, reviewing the uncommitted diff, building the site, what you learned | docs/src/doc-writer/tutorial.md |
| 4 | how-to | Configure or reconfigure a project | Re-run menu (change one area: personas, tone, use cases, doc system, paths), `--reset`, `--refresh-context` after hand-editing `config.yaml`, custom doc systems, scaffold check, troubleshooting | docs/src/doc-writer/how-to/configure.md |
| 5 | how-to | Update docs after code changes | Re-run `/doc-writer:write` (update mode auto-detected), read `gap-report.md`, approve new and `(refresh)` pages, `--skip-gap-scan` | docs/src/doc-writer/how-to/update-docs.md |
| 6 | how-to | Resolve PARTIAL and FAIL verdicts | What the decision step asks, accepting vs fixing PARTIALs, non-converging FAILs after the third pass, follow-up with `/doc-writer:edit` | docs/src/doc-writer/how-to/resolve-verdicts.md |
| 7 | how-to | Audit docs without changing them | `/doc-writer:review`, reading the combined summary and reports, `--edit` with confirmation | docs/src/doc-writer/how-to/audit.md |
| 8 | how-to | Make targeted fixes | `/doc-writer:edit` from report findings or a freeform description/page path, reviewing the diff | docs/src/doc-writer/how-to/targeted-fixes.md |
| 9 | how-to | Add project rules and terminology | `rules.md` (additive to universal rules), `terminology.yaml` (`project_terms`, `proper_nouns`, `overrides`), when agents pick changes up | docs/src/doc-writer/how-to/project-rules.md |
| 10 | how-to | Upgrade after a plugin update | Update the plugin, run `/doc-writer:upgrade`, what it migrates (config fields, unchanged default files, merges of edited ones, new setup questions, context refresh), reading the Upgrade Summary | docs/src/doc-writer/how-to/upgrade.md |
| 11 | reference (hand-written) | Commands | `setup` (`--reset`, `--refresh-context`), `write` (`--skip-gap-scan`, create/update mode), `review` (`--edit`), `edit` (`[issue or page path]`), `upgrade`; for each: prerequisites, files read/written, side effects | docs/src/doc-writer/reference/commands.md |
| 12 | reference (hand-written) | config.yaml | All fields: `user_personas`, `tone`, `doc_system`, `api_reference`, `paths`, `use_cases`, `use_cases_section`, `qa_answers`, `detected`, `version`/`plugin_version`; annotated example (neutral persona) | docs/src/doc-writer/reference/configuration.md |
| 13 | reference (hand-written) | The .doc-writer folder | Every file: who writes it, when regenerated, safe to edit or not (`context.md` regenerated on refresh; reports overwritten; `.originals/`, `.deslop/` internal) | docs/src/doc-writer/reference/files.md |
| 14 | explanation | How the pipeline works | Four agents (Doc Researcher, Doc Author, Doc Editor, Doc Persona), stage order and outputs, revision loop (max three passes), Mermaid flow, why separate agents | docs/src/doc-writer/explanation/pipeline.md |
| 15 | explanation | Understanding personas and verdicts | What a persona is, scenarios (`scenarios.yaml` reused across passes), docs-only navigation, PASS/PARTIAL/FAIL meaning, multiple personas | docs/src/doc-writer/explanation/personas.md |
| 16 | explanation | Quality rules and the deslop pass | Universal vs project rules, Diataxis types and "type blur", the Editor's four passes, deslop measurement (credited, what it measures for you), `python3` requirement and fallback | docs/src/doc-writer/explanation/quality.md |
| 17 | (readme) | README.md | Optional: align install form and agent count with the site | README.md |
| 18 | (maintainer) | MAINTAINER.md | Optional; recommend excluding for now (internals stay out of the public site) | MAINTAINER.md |

## Content Refresh

| # | Type | Title | Key Sections | File Path |
|---|------|-------|--------------|-----------|
| 19 | (refresh) | doc-writer (old single page) | Retire: content moves into pages 2-16. Stale: wrong install (`/plugin install github:anentropic/for-agents`); "three-agent" pipeline (four agents; Doc Researcher missing); `/doc-writer:upgrade` undocumented; setup omits use cases, tone, framework/navigation questions and `context.md`; config reference missing `use_cases`, `use_cases_section`, `qa_answers`, `plugin_version`; example output uses a real person's name — replace with the configured persona or a neutral name. odoc is already listed. | docs/src/doc-writer.md |

## Proposed nav (mkdocs.yml)

```yaml
nav:
  - Overview: index.md
  - doc-writer:
      - doc-writer/index.md
      - Tutorial: doc-writer/tutorial.md
      - How-to guides:
          - Configure a project: doc-writer/how-to/configure.md
          - Update docs after code changes: doc-writer/how-to/update-docs.md
          - Resolve verdicts: doc-writer/how-to/resolve-verdicts.md
          - Audit docs: doc-writer/how-to/audit.md
          - Make targeted fixes: doc-writer/how-to/targeted-fixes.md
          - Add rules and terminology: doc-writer/how-to/project-rules.md
          - Upgrade the plugin: doc-writer/how-to/upgrade.md
      - Reference:
          - Commands: doc-writer/reference/commands.md
          - config.yaml: doc-writer/reference/configuration.md
          - The .doc-writer folder: doc-writer/reference/files.md
      - Explanation:
          - How the pipeline works: doc-writer/explanation/pipeline.md
          - Personas and verdicts: doc-writer/explanation/personas.md
          - Quality rules and the deslop pass: doc-writer/explanation/quality.md
```

"Home" becomes "Overview" per the guidance file. Sidebar-only nav (`navigation.sections`, no tabs).
`navigation.indexes` is off, so `doc-writer/index.md` shows as a first child entry rather than a
clickable section header; enable `navigation.indexes` if a clickable header is wanted. No per-quadrant
index pages are proposed because of this.

## Notes

- **API Reference status:** not detected, and not applicable: the plugin has no code API. Reference
  pages 11-13 are hand-written (commands, config schema, files), an intended exception to the
  "no reference pages" rule, as `context.md` notes.
- **Audience targeting:** all pages target "Library maintainer using Claude Code". Examples use a
  neutral sample library (small Python/TypeScript package), never doc-writer itself.
- **Use Cases section:** `use_cases_section` is not set in config, so none proposed.
- **Coverage gaps / exclusions:** `docs_scan.py` internals, deslop vendoring, `detect-project.sh`,
  `scan-exports.sh`, agent prompts and this repo's tests/CI stay out. Removing `doc-writer.md` breaks
  its old URL (no redirect plugin installed); the front-page link must be updated.
