# Project Research Summary

**Project:** doc-writer v1.5.0 Plugin Upgrade Helpers
**Domain:** LLM-driven plugin upgrade system (markdown 3-way merge, YAML config migration, Q&A gap detection)
**Researched:** 2026-03-26
**Confidence:** HIGH

## Executive Summary

This milestone adds upgrade capability to the doc-writer Claude Code plugin, allowing projects that ran `/doc-writer:setup` to migrate to new plugin versions without losing their customizations. The domain is well-understood: 3-way merge (diff3) for prose files, field-additive migration for YAML configs, and gap detection for structured Q&A answers. The entire implementation must stay within the existing skill system constraints -- bash scripts, markdown instruction files, and Claude itself as the compute engine -- which actually simplifies the stack considerably. All required tools are either standard Unix utilities or Claude's own capabilities; no npm, Python libraries, or external services are needed.

The recommended approach is dependency-driven and falls naturally into five phases. The most important architectural decision is that `.doc-writer/.originals/` (the immutable reference copy directory) must be created by the setup skill before the upgrade skill can do anything useful. Originals storage is the foundation on which 3-way merge, version detection, and Q&A gap detection all depend. Equally important: the setup skill must begin persisting Q&A answers into `config.yaml` (a new `qa_answers` section), since answers are currently ephemeral and upgrade cannot know which questions were already answered without them.

The primary risk is not technical complexity but correctness: 3-way text merge applied naively to prose guidance files will silently produce garbled or contradictory output, because diff3 treats files as line sequences with no understanding of Markdown section structure. The mitigation is to perform comparison at section (heading) level rather than line level, or fall back to diff-and-ask. A secondary risk is that all pre-v1.5.0 projects have no stored originals, so the first upgrade must bootstrap the base using heuristics. Both risks have well-defined prevention strategies confirmed by the research.

## Key Findings

### Recommended Stack

The entire feature set is buildable with zero new dependencies. See `.planning/research/STACK.md` for full details including verified system checks and alternatives considered.

**Core technologies:**
- `diff3` (system built-in, `/usr/bin/diff3`): 3-way merge of guidance and rules markdown files -- pre-installed on macOS and Linux, tested with markdown content (non-overlapping edits exit 0; conflicts exit 1 with parseable markers)
- Claude-as-reader (the agent itself): YAML config schema comparison and field-by-field migration -- more reliable than bash regex for structured data; already the established pattern throughout doc-writer
- Question header IDs (`## Question N: {topic}`): Q&A gap tracking -- existing naming convention in `.qa.md` files; stable identifiers requiring no new tooling
- `plugin.json` + new `config.yaml plugin_version` field: version tracking -- `plugin.json` already exists; `plugin_version` is a new top-level field added to config-template.yaml
- File copy (`cp`) to `.doc-writer/.originals/`: merge base storage -- simplest possible approach; no moving parts; user-inspectable

### Expected Features

See `.planning/research/FEATURES.md` for full details and the feature dependency graph.

**Must have (table stakes):**
- Originals storage at setup time -- prerequisite for everything else; 3-way merge has no base without it
- Version detection -- reads `plugin.json` version vs `config.yaml plugin_version`; triggers the upgrade flow
- Guidance/rules 3-way merge -- primary user value; preserves customizations while applying upstream plugin changes
- Config field additions -- Claude reads old and new templates, adds missing fields with inferred or default values
- No-op on clean files -- silently overwrite when user made no customizations (zero diff from original)
- Conflict presentation -- when merge produces conflicts, surface them clearly for user resolution via AskUserQuestion
- Q&A gap detection -- only ask new framework questions; never re-ask questions the user already answered

**Should have (differentiators):**
- Smart conflict resolution suggestions -- Claude interprets conflict markers with knowledge of guidance file purpose
- Researcher re-run after config changes -- automatically triggers `--refresh-context` after migration adds behavior-affecting fields
- Deprecation warnings -- warn when config fields or guidance sections are removed in new plugin version
- First-time upgrade fallback -- handle pre-v1.5.0 projects gracefully using heuristic bootstrap

**Defer (v2+):**
- Dry-run mode -- user can review changes as they are presented; not essential for v1.5.0
- Interactive merge editor -- not available in Claude Code's tool set

**Explicit anti-features (do not build):** Automatic conflict resolution, per-version migration scripts, YAML 3-way merge via diff3 (use Claude-as-reader for structured data), undo/rollback mechanism (user has git).

### Architecture Approach

The upgrade system introduces a third data lifecycle to `.doc-writer/`. Currently, files are either mutable-by-user (config.yaml, guidance files, rules.md) or regenerated-from-scratch (context.md). The upgrade system needs immutable reference copies in `.doc-writer/.originals/` that track what the plugin shipped at setup time. See `.planning/research/ARCHITECTURE.md` for full data flow diagrams, component tables, and the dependency-driven build order.

**Major components:**

1. Modified `skills/setup/SKILL.md` -- writes `plugin_version` to config, creates `.originals/` directory at Step 3 (File Creation), persists `qa_answers` to config after Step 2b.5 (Framework Q&A); approximately 25 new lines total
2. New `skills/upgrade/SKILL.md` -- separate skill invoked via `/doc-writer:upgrade`; six-step workflow: version detection, config migration, 3-way merge, Q&A gap detection, researcher re-run, finalization
3. Modified `skills/setup/defaults/config-template.yaml` -- adds `plugin_version: ""` and `qa_answers:` section; approximately 10 new lines
4. `.doc-writer/.originals/` directory -- pristine copies of `rules.md` and `{framework}.md` as shipped; created by setup, read and updated after each upgrade

All other components (doc-researcher, doc-author, doc-editor, doc-user-tester, write/review/edit/diataxis/quality-rules skills, all `.qa.md` files, all guidance `.md` files) are unchanged.

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full details, detection strategies, phase-specific warnings, and recovery steps.

1. **Silent 3-way merge corruption on prose guidance files** -- Line-level diff3 cannot detect adjacent insertions at the same anchor point, semantic conflicts (same concept, different wording), or section rearrangements. Prevention: use section-level merge (parse by `##` headings; compare section-by-section); fall back to diff-and-ask when ambiguous. Never auto-merge prose silently.

2. **No originals base for pre-v1.5.0 projects** -- All existing projects lack `.originals/`. Without a base, 3-way merge is impossible. Prevention: on first upgrade, compare user file against known plugin defaults; zero-diff files can be safely replaced; modified files get side-by-side diff for manual resolution; always bootstrap `.originals/` after the first upgrade.

3. **Config migration silently drops user data on field rename or restructure** -- Additive "add missing fields with defaults" fails when a new field semantically replaces an old one (e.g., `user_tasks` should be inferred from `domain_context`, not defaulted to empty). Prevention: per-field migration rules that infer values from existing data; never silently default a behavior-affecting field.

4. **Q&A gap detection re-asks all questions when no stored answers exist** -- Current design keeps Q&A answers ephemeral; upgrade cannot distinguish new from answered questions. Prevention: add `qa_answers` section to config.yaml in v1.5.0 setup; for existing projects, infer from guidance file and context.md what was likely configured.

5. **Upgrade breaks on partially configured or manually edited real-world projects** -- Real installed-base projects deviate: missing context.md, custom fields in config.yaml, YAML comments, extra files in `.doc-writer/`. Prevention: validate before migrating; parse config permissively; tolerate missing files; never touch files outside upgrade scope (anything other than config.yaml, `{doc_system}.md`, rules.md, context.md).

## Implications for Roadmap

The dependency graph from ARCHITECTURE.md and FEATURES.md drives a clear, unambiguous five-phase structure. Phase 1 is mandatory before all others.

### Phase 1: Foundation -- Setup Skill Changes

**Rationale:** Every upgrade feature depends on data the setup skill must produce. Without `plugin_version` in config, version detection is impossible. Without `.originals/`, 3-way merge has no base. Without `qa_answers`, gap detection re-asks everything. These additions are backward-compatible (existing installs get them on next `--reset` or via upgrade bootstrap).

**Delivers:** Fresh setup runs produce config.yaml with `plugin_version` + `qa_answers`; `.originals/` directory with pristine copies of `rules.md` and `{framework}.md`. Existing `--reset` and `--refresh-context` flags continue working correctly.

**Addresses:** Originals storage (table-stakes), Q&A answer persistence (prerequisite for gap detection)

**Avoids:** Pitfall 2 (no base for existing projects), Pitfall 4 (Q&A re-asks everything)

**Files changed:** `skills/setup/SKILL.md` (~25 lines added), `skills/setup/defaults/config-template.yaml` (~10 lines added)

### Phase 2: Upgrade Skill -- Version Detection and Config Migration

**Rationale:** Version detection is the entry point for the entire upgrade flow. Config migration must ship alongside version tracking because they are semantically coupled: detecting a version mismatch implies knowing how to migrate between those versions. A detection-only feature without migration is a broken half-feature.

**Delivers:** `/doc-writer:upgrade` command skeleton with working version detection (reads `plugin.json` vs `config.yaml plugin_version`; treats missing `plugin_version` as pre-1.5.0). Config field additions with semantic inference (not empty defaults for behavior-affecting fields). Deprecation warnings. Permissive config parsing that preserves unknown fields and YAML comments.

**Addresses:** Version detection (table-stakes), config field additions (table-stakes), deprecation warnings (differentiator)

**Avoids:** Pitfall 3 (silent data drop -- inference over empty defaults), Pitfall 5 (breaks on real configs -- permissive parsing), Pitfall 6 (version skipping/downgrade -- idempotent migration steps)

**Files changed:** New `skills/upgrade/SKILL.md`, `plugin.json` version bump to 1.5.0

### Phase 3: 3-Way Merge for Guidance and Rules Files

**Rationale:** Primary user value of the milestone. Depends on Phase 1 (`.originals/` must exist) and Phase 2 (upgrade skill scaffold). Highest-risk feature: must use section-level merge, not raw line-level diff3, to avoid silent corruption.

**Delivers:** Upgrade merges `{framework}.md` and `rules.md` using section-level comparison (parse by `##` headings; apply section-by-section rules). Auto-applies non-conflicting upstream changes. Surfaces conflicts for user resolution. Updates `.originals/` after successful merge. Handles pre-v1.5.0 bootstrap: compare against known defaults; prompt user for modified files; silently replace unmodified files.

**Addresses:** Guidance file merge (table-stakes), rules file merge (table-stakes), conflict presentation (table-stakes), no-op on clean files (table-stakes), first-time upgrade fallback (differentiator)

**Avoids:** Pitfall 1 (silent merge corruption -- section-level, not line-level), Pitfall 2 (pre-1.5.0 bootstrap), Pitfall 12 (semantically contradictory merged output -- LLM consistency check after merge)

### Phase 4: Q&A Gap Detection

**Rationale:** Depends on Phase 1 (qa_answers must exist in config) and Phase 2 (upgrade skill scaffold). Can be built independently from Phase 3. Delivers the "only ask new questions" experience that prevents re-setup fatigue.

**Delivers:** Upgrade compares current `.qa.md` question headers against stored `qa_answers`. Presents only new questions (ID not in manifest) or changed questions (ID found but question hash differs). Re-presents changed questions pre-filled with previous answer where still valid. Merges answers into `qa_answers` after user responds.

**Addresses:** Q&A gap detection (differentiator)

**Avoids:** Pitfall 4 (re-asks everything), Pitfall 11 (YAML round-trip destroys comments -- Claude does surgical field edits, not parse-transform-serialize)

### Phase 5: Researcher Re-Run and Finalization

**Rationale:** Terminal phase; depends on Phases 2-4 to have complete, finalized state before re-running the researcher. Researcher re-run is only triggered when config changes affect its inputs.

**Delivers:** Researcher spawned with all answers (old + new merged). Backs up context.md before regeneration; preserves user-added sections not generated by researcher. Writes final `plugin_version` to config.yaml. Displays summary of all changes made during upgrade.

**Addresses:** Researcher re-run on config changes (differentiator)

**Avoids:** Pitfall 9 (researcher overwrites user-edited context.md -- backup + section preservation), Pitfall 8 (upgrade/setup command conflicts -- clear command separation, sentinel values instead of empty defaults on migrated fields)

### Phase Ordering Rationale

- Phase 1 is a strict prerequisite for all others: no originals = no merge; no `plugin_version` = no version detection; no `qa_answers` = no gap detection.
- Phase 2 before Phase 3: config migration is simpler and validates the upgrade skill structure before adding 3-way merge complexity.
- Phase 3 before Phase 4: guidance merge is the primary user value and the highest-risk feature; it should be built and validated independently before adding Q&A logic.
- Phase 5 last: integration testing needs all components in place; researcher re-run synthesizes all prior migration outputs.
- Every phase must test against the live `.doc-writer/` directory (a v1.0-era project), not only fresh setups -- this is the PITFALLS research's most emphatic recommendation.

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 3 (3-way merge):** The section-level merge algorithm for Markdown needs careful specification before implementation. Key open decisions: how to handle content between headings (inter-heading prose), how to detect section rearrangement vs addition, when to fall back to diff-and-ask. A prototype against actual guidance files before writing the full skill is recommended.

Phases with standard patterns (skip research-phase):

- **Phase 1 (setup changes):** Straightforward file copy additions; the pattern already exists in setup SKILL.md; no ambiguity.
- **Phase 2 (version detection + config migration):** Well-understood; Claude-as-reader is the established doc-writer pattern; bash semver comparison with `sort -V` is verified.
- **Phase 4 (Q&A gap detection):** Algorithm is fully specified in ARCHITECTURE.md; no ambiguity in the comparison logic.
- **Phase 5 (researcher re-run):** Already have `--refresh-context` flow; terminal step is primarily orchestration.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All technologies verified on this system; diff3 tested with markdown content; no external dependencies introduced; python3/PyYAML unavailability confirmed |
| Features | HIGH | Derived from existing codebase analysis and direct testing; MVP vs defer rationale is clear; dependency graph is explicit |
| Architecture | HIGH | All findings from reading the actual codebase (setup SKILL.md 583 lines, all .qa.md files, all guidance files, config-template.yaml, plugin.json); no external research needed |
| Pitfalls | MEDIUM-HIGH | Critical pitfalls verified via codebase analysis and official git merge documentation; moderate pitfalls based on migration pattern literature (community blogs) |

**Overall confidence:** HIGH

### Gaps to Address

- **Section-level merge algorithm specification:** PITFALLS.md establishes what NOT to do (raw line-level diff3 on prose) but the specific section-level algorithm needs precise specification during Phase 3 planning. Decisions needed: treatment of inter-heading content, structural rearrangement detection, fallback threshold.

- **Originals directory naming:** STACK.md uses `.doc-writer/.originals/`; PITFALLS.md recommends renaming to `.doc-writer/.plugin-base/` to signal "do not edit" and recommend `.gitignore` addition. This naming decision should be made before Phase 1 implementation begins.

- **Canonical plugin version source:** STACK.md reads from `plugin.json` via grep or python3. PITFALLS.md suggests a simpler `doc-writer/.claude-plugin/VERSION` text file that is installation-method-agnostic. The authoritative version source should be confirmed before Phase 2.

- **Sentinel values for migrated fields:** PITFALLS.md recommends sentinel values like `"(pending -- run /doc-writer:setup to configure)"` rather than empty strings for fields added during migration. This needs validation against how doc-author, doc-editor, and other consuming skills handle empty or missing config fields to avoid breaking them.

- **Researcher-generated custom framework files:** For non-standard doc systems generated via the researcher FALLBACK path, the guidance file in `.doc-writer/` has no corresponding plugin default. The 3-way merge base may be unreliable if the researcher produces different output on subsequent runs. This edge case may not need solving in v1.5.0 but should be acknowledged in Phase 3.

## Sources

### Primary (HIGH confidence)

- `doc-writer/skills/setup/SKILL.md` (583 lines, direct reading) -- setup flow, Q&A answer handling, file copy patterns, --reset/--refresh-context behavior
- `doc-writer/skills/setup/defaults/config-template.yaml` (direct reading) -- config schema, current v1.4 field set
- `.doc-writer/config.yaml` (direct reading) -- confirmed v1.0-era config missing tone, use_cases, use_cases_section, user_tasks
- `doc-writer/.claude-plugin/plugin.json` (direct reading) -- version source, current version 1.4.0
- `doc-writer/skills/setup/defaults/*.qa.md` (4 files, direct reading) -- Q&A file format, question header naming convention
- `doc-writer/skills/setup/defaults/*.md` (4 guidance files, direct reading) -- guidance file format and line counts
- `/usr/bin/diff3` (verified present, FreeBSD diff3 20220517) -- tested with markdown content; non-overlapping merges exit 0; conflicting merges exit 1 with parseable markers
- [GNU Diffutils Manual](https://www.gnu.org/software/diffutils/manual/html_mono/diff.html) -- diff3 options and conflict markers
- [Git merge strategies](https://git-scm.com/docs/merge-strategies) -- semantic conflicts invisible to text merge

### Secondary (MEDIUM confidence)

- [Merging with diff3](https://blog.jcoglan.com/2017/05/08/merging-with-diff3/) -- algorithm walkthrough, diff sensitivity, reverted change edge case
- [Three-Way Merge algorithms](https://tonyg.github.io/revctrl.org/ThreeWayMerge.html) -- base selection importance, conflict detection rules
- [Backward compatibility in schema evolution](https://www.dataexpert.io/blog/backward-compatibility-schema-evolution-guide) -- additive changes, migration patterns
- [Flyway out-of-order migrations](https://www.baeldung.com/flyway-migrations) -- sequential migration chain, skip-version handling

### Tertiary (LOW confidence)

- [YAML schema versioning](https://suews.readthedocs.io/latest/contributing/schema/schema_versioning.html) -- version field patterns (niche project docs)
- [Plugin architecture versioning](https://oninebx.github.io/blog/architecture/plugin-architecture-in-practice-part-4-versioning-distribution-and-ecosystem/) -- parallel version support (blog post)
- [zdiff3 and conflict styles](https://www.ductile.systems/zdiff3/) -- conflict marker format reference
- [diff3 Linux examples](https://www.tecmint.com/diff3-command-in-linux/) -- practical usage patterns

---
*Research completed: 2026-03-26*
*Ready for roadmap: yes*
