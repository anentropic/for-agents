# Roadmap: Doc Writer Agent

## Milestones

- ✅ **v1.0 Doc Writer Plugin** — Phases 1-13 (shipped 2026-03-19)
- ✅ **v1.4.0 Content & Navigation** — Phases 14-17 (shipped 2026-03-22)
- **v1.5.0 Plugin Upgrade Helpers** — Phases 18-21

## Phases

<details>
<summary>✅ v1.0 Doc Writer Plugin (Phases 1-13) — SHIPPED 2026-03-19</summary>

- [x] Phase 1: Foundation and Setup (2/2 plans) — completed 2026-03-03
- [x] Phase 2: Doc Author Agent (1/1 plans) — completed 2026-03-03
- [x] Phase 3: Editor Agent (1/1 plans) — completed 2026-03-03
- [x] Phase 4: User Persona and Full Pipeline (1/1 plans) — completed 2026-03-03
- [x] Phase 5: Integration and Commands (2/2 plans) — completed 2026-03-04
- [x] Phase 6: Cross-Phase Integration Cleanup (1/1 plans) — completed 2026-03-15
- [x] Phase 7: Doc-Writer Plugin Packaging (3/3 plans) — completed 2026-03-15
- [x] Phase 8: Doc-Writer Skills Polish (2/2 plans) — completed 2026-03-16
- [x] Phase 9: Enhanced Setup Q&A + Researcher (3/3 plans) — completed 2026-03-17
- [x] Phase 10: Framework Scaffolding + Unknown Framework Research (3/3 plans) — completed 2026-03-17
- [x] Phase 11: Sphinx/Shibuya Framework Support (2/2 plans) — completed 2026-03-18
- [x] Phase 12: Odoc Framework for OCaml (4/4 plans) — completed 2026-03-19
- [x] Phase 13: Scaffold Variable Fix + Doc-Researcher Improvements (3/3 plans) — completed 2026-03-19

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>✅ v1.4.0 Content & Navigation (Phases 14-17) — SHIPPED 2026-03-22</summary>

- [x] Phase 14: Foundations (2/2 plans) — completed 2026-03-21
- [x] Phase 15: Navigation Strategies (2/2 plans) — completed 2026-03-22
- [x] Phase 16: Use Cases (2/2 plans) — completed 2026-03-22
- [x] Phase 17: OCaml .mld/.mli Output (2/2 plans) — completed 2026-03-22

Full details: `.planning/milestones/v1.4.0-ROADMAP.md`

</details>

### v1.5.0 Plugin Upgrade Helpers

**Milestone Goal:** Give doc-writer projects a smooth upgrade path when the plugin is updated, preserving project customizations via section-level 3-way merge.

- [x] **Phase 18: Setup Foundation** - Augment setup skill to produce version tracking, originals storage, and Q&A answer persistence (completed 2026-03-26)
- [x] **Phase 19: Upgrade Skill** - Version detection, config migration, and deprecation warnings via new `/doc-writer:upgrade` command (completed 2026-03-26)
- [ ] **Phase 20: 3-Way Merge** - Section-level merge of guidance and rules files with conflict resolution and pre-v1.5.0 fallback
- [ ] **Phase 21: Q&A Gap Detection and Finalization** - Ask only new framework questions and re-run researcher to refresh context

## Phase Details

### Phase 18: Setup Foundation
**Goal**: Fresh setup runs produce all data the upgrade system needs -- version tracking, pristine originals, and persisted Q&A answers
**Depends on**: Phase 17 (v1.4.0 shipped)
**Requirements**: SETUP-01, SETUP-02, SETUP-03, SETUP-04
**Success Criteria** (what must be TRUE):
  1. User runs `/doc-writer:setup` and `config.yaml` contains a `plugin_version` field matching the version in `plugin.json`
  2. User runs `/doc-writer:setup` and `.doc-writer/.originals/` exists with pristine copies of the framework guidance file and `rules.md` as shipped by the plugin
  3. User runs `/doc-writer:setup` and `config.yaml` contains a `qa_answers` section with keys derived from Q&A question headers
  4. User runs `/doc-writer:setup --reset` and `.originals/` is refreshed with current plugin files (not stale from a previous version)
**Plans:** 2/2 plans complete
Plans:
- [x] 18-01-PLAN.md -- Plugin version tracking and .originals/ storage in setup Step 3
- [ ] 18-02-PLAN.md -- Q&A answer persistence to qa_answers and odoc_author_scope migration

### Phase 19: Upgrade Skill
**Goal**: Users can run `/doc-writer:upgrade` to detect version mismatches and migrate config fields without losing existing settings
**Depends on**: Phase 18
**Requirements**: UPGRADE-01, UPGRADE-02, UPGRADE-03, UPGRADE-04
**Success Criteria** (what must be TRUE):
  1. User runs `/doc-writer:upgrade` when already up to date and receives a clear "already up to date" message with no changes made
  2. User runs `/doc-writer:upgrade` after a plugin update and new config fields appear in `config.yaml` with semantically inferred values (not blank defaults)
  3. User runs `/doc-writer:upgrade` and files identical to their `.originals/` counterparts are silently updated to the new plugin version without prompts
  4. User runs `/doc-writer:upgrade` and receives deprecation warnings for config fields or guidance sections removed in the new plugin version
**Plans:** 1/1 plans complete
Plans:
- [x] 19-01-PLAN.md -- Plugin version bump and upgrade SKILL.md with 4-step flow (version detection, config migration, unchanged file update, finalize)

### Phase 20: 3-Way Merge
**Goal**: Users can upgrade guidance and rules files while keeping their customizations intact, with clear conflict resolution when changes overlap
**Depends on**: Phase 18, Phase 19
**Requirements**: MERGE-01, MERGE-02, MERGE-03, MERGE-04
**Success Criteria** (what must be TRUE):
  1. User with customized `{doc_system}.md` runs `/doc-writer:upgrade` and non-conflicting upstream changes are applied automatically while user-customized sections are preserved
  2. User with customized `rules.md` runs `/doc-writer:upgrade` and project-specific rules are preserved while new default rules are added
  3. User encounters a merge conflict and is presented each conflict one at a time via AskUserQuestion with options to keep their version, take the plugin version, or provide a custom resolution
  4. User with a pre-v1.5.0 project (no `.originals/`) runs `/doc-writer:upgrade` and is guided through a 2-way diff with per-change accept/reject, after which `.originals/` is bootstrapped
**Plans:** 1 plan
Plans:
- [ ] 20-01-PLAN.md -- Section-level 3-way merge algorithm in Step 3 with conflict resolution and 2-way diff bootstrap

### Phase 21: Q&A Gap Detection and Finalization
**Goal**: Upgrade flow asks only new framework questions and refreshes project context so downstream agents use the latest configuration
**Depends on**: Phase 18, Phase 19
**Requirements**: QA-01, QA-02
**Success Criteria** (what must be TRUE):
  1. User runs `/doc-writer:upgrade` after plugin adds new Q&A questions and is asked only those new questions -- previously answered questions are not re-asked
  2. User runs `/doc-writer:upgrade` after config field additions or new Q&A answers and `context.md` is refreshed via a researcher re-run reflecting the updated configuration
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation and Setup | v1.0 | 2/2 | Complete | 2026-03-03 |
| 2. Doc Author Agent | v1.0 | 1/1 | Complete | 2026-03-03 |
| 3. Editor Agent | v1.0 | 1/1 | Complete | 2026-03-03 |
| 4. User Persona and Full Pipeline | v1.0 | 1/1 | Complete | 2026-03-03 |
| 5. Integration and Commands | v1.0 | 2/2 | Complete | 2026-03-04 |
| 6. Cross-Phase Integration Cleanup | v1.0 | 1/1 | Complete | 2026-03-15 |
| 7. Doc-Writer Plugin Packaging | v1.0 | 3/3 | Complete | 2026-03-15 |
| 8. Doc-Writer Skills Polish | v1.0 | 2/2 | Complete | 2026-03-16 |
| 9. Enhanced Setup Q&A + Researcher | v1.0 | 3/3 | Complete | 2026-03-17 |
| 10. Framework Scaffolding + Unknown Framework | v1.0 | 3/3 | Complete | 2026-03-17 |
| 11. Sphinx/Shibuya Framework Support | v1.0 | 2/2 | Complete | 2026-03-18 |
| 12. Odoc Framework for OCaml | v1.0 | 4/4 | Complete | 2026-03-19 |
| 13. Scaffold Variable Fix + Doc-Researcher | v1.0 | 3/3 | Complete | 2026-03-19 |
| 14. Foundations | v1.4.0 | 2/2 | Complete | 2026-03-21 |
| 15. Navigation Strategies | v1.4.0 | 2/2 | Complete | 2026-03-22 |
| 16. Use Cases | v1.4.0 | 2/2 | Complete | 2026-03-22 |
| 17. OCaml .mld/.mli Output | v1.4.0 | 2/2 | Complete | 2026-03-22 |
| 18. Setup Foundation | v1.5.0 | 2/2 | Complete    | 2026-03-26 |
| 19. Upgrade Skill | v1.5.0 | 1/1 | Complete    | 2026-03-26 |
| 20. 3-Way Merge | v1.5.0 | 0/1 | Not started | - |
| 21. Q&A Gap Detection and Finalization | v1.5.0 | 0/0 | Not started | - |
