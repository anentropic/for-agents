# Requirements: Doc Writer Agent v1.5.0

**Milestone:** v1.5.0 Plugin Upgrade Helpers
**Goal:** Give doc-writer projects a smooth upgrade path when the plugin is updated, preserving project customizations via section-level 3-way merge.

---

## v1.5.0 Requirements

### Setup Foundation

- [x] **SETUP-01**: User can run `/doc-writer:setup` and have `plugin_version` (matching version from `plugin.json`) written to `config.yaml` as a top-level field
- [x] **SETUP-02**: User can run `/doc-writer:setup` and have `.doc-writer/.originals/` created with pristine copies of `{doc_system}.md` and `rules.md` as shipped by the plugin
- [x] **SETUP-03**: User can run `/doc-writer:setup` and have framework Q&A answers persisted to `config.yaml` under a `qa_answers` section, keyed by question ID derived from question headers in `.qa.md` files
- [x] **SETUP-04**: User can run `/doc-writer:setup --reset` and have `.originals/` refreshed with current plugin files alongside the config reset

### Upgrade Command

- [x] **UPGRADE-01**: User can run `/doc-writer:upgrade` and receive an "already up to date" message when `config.yaml plugin_version` matches the installed `plugin.json` version
- [x] **UPGRADE-02**: User can run `/doc-writer:upgrade` and have new fields from `config-template.yaml` added to their `config.yaml` with semantically inferred defaults — not blank — (e.g., `user_tasks` inferred from `domain_context`, not defaulted to `[]`)
- [x] **UPGRADE-03**: User can run `/doc-writer:upgrade` and have files where the user copy is identical to `.originals/` silently updated to the new plugin version without any prompts
- [x] **UPGRADE-04**: User can run `/doc-writer:upgrade` and receive deprecation warnings when config fields or guidance sections present in `.originals/` are absent from the new plugin version

### File Merge

- [x] **MERGE-01**: User can run `/doc-writer:upgrade` and have `{doc_system}.md` updated via section-level 3-way merge (parsed by `##` headings) — non-conflicting upstream changes applied automatically, user-customized sections preserved
- [x] **MERGE-02**: User can run `/doc-writer:upgrade` and have `rules.md` updated via the same section-level 3-way merge — project-specific rules preserved while new default rules are added
- [x] **MERGE-03**: User can resolve each merge conflict individually, presented one at a time via AskUserQuestion with options: keep user version, take plugin version, or provide custom resolution
- [x] **MERGE-04**: User with a pre-v1.5.0 project (no `.originals/` directory) can run `/doc-writer:upgrade` and be guided through a 2-way diff of plugin changes — shown what would change, confirming which changes to accept; `.originals/` bootstrapped after completion

### Q&A Updates

- [x] **QA-01**: User can run `/doc-writer:upgrade` and only be asked framework Q&A questions whose IDs are absent from the stored `qa_answers` in `config.yaml` (new questions added to `.qa.md` since last setup)
- [x] **QA-02**: User can run `/doc-writer:upgrade` after any config field additions or new Q&A answers and have `context.md` refreshed via a researcher re-run

---

## Future Requirements

*(Deferred from v1.5.0 — not in scope this milestone)*

- Dry-run mode (`/doc-writer:upgrade --dry-run`) — show what would change without applying
- Smart conflict resolution suggestions — Claude interprets conflict markers with guidance-file knowledge and suggests the likely correct resolution
- Custom/researcher-generated framework upgrade path — projects using unknown frameworks generated via the FALLBACK researcher path; `.originals/` may be unreliable for these

---

## Out of Scope

- **Automatic conflict resolution** — conflicts must always surface to the user; trust violation if silently resolved
- **Per-version migration scripts** — template comparison (current originals vs current plugin defaults) is sufficient; version-chain scripts create combinatorial explosion
- **YAML 3-way merge via diff3** — config.yaml is structured data; Claude-as-reader is more reliable for field-by-field migration than line-based merge
- **Undo/rollback** — user has git; document "undo" as `git checkout .doc-writer/`
- **Plugin auto-update** — out of scope; Claude Code handles plugin distribution; this milestone only handles project-side migration after plugin files have been updated
- **Backup before upgrade** — user has git; inform user to commit before upgrading if rollback is desired

---

## Traceability

| REQ-ID | Phase | Plans | Status |
|--------|-------|-------|--------|
| SETUP-01 | Phase 18 | 18-01 | Complete |
| SETUP-02 | Phase 18 | 18-01 | Complete |
| SETUP-03 | Phase 18 | 18-02 | Complete |
| SETUP-04 | Phase 18 | 18-01 | Complete |
| UPGRADE-01 | Phase 19 | 19-01 | Complete |
| UPGRADE-02 | Phase 19 | 19-01 | Complete |
| UPGRADE-03 | Phase 19 | 19-01 | Complete |
| UPGRADE-04 | Phase 19 | 19-01 | Complete |
| MERGE-01 | Phase 20 | 20-01 | Complete |
| MERGE-02 | Phase 20 | 20-01 | Complete |
| MERGE-03 | Phase 20 | 20-01 | Complete |
| MERGE-04 | Phase 20 | 20-01 | Complete |
| QA-01 | Phase 21 | 21-01 | Complete |
| QA-02 | Phase 21 | 21-01 | Complete |
