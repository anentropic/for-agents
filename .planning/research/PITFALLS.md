# Domain Pitfalls: v1.5.0 Plugin Upgrade Helpers

**Domain:** Adding upgrade/migration capabilities to an existing LLM-driven plugin that copies markdown guidance files and YAML configs to user projects
**Researched:** 2026-03-26
**Confidence:** MEDIUM-HIGH (grounded in codebase analysis + web-verified merge/migration patterns)

---

## Critical Pitfalls

Mistakes that cause data loss, silent corruption, or require rewrites.

### Pitfall 1: 3-Way Merge of Markdown Guidance Files Produces Silently Wrong Output

**What goes wrong:**
3-way text merge works by diffing two versions against a common base. When the plugin updates a guidance file (e.g., `plain-markdown.md`) and the user has also edited their local copy, a 3-way merge attempts to combine both changes. This fails silently in several specific ways:

1. **Adjacent additions:** Both sides add a new section after the same anchor heading (e.g., plugin adds a "Tables" section after "Lists," user adds a "Checklists" section after "Lists"). The merge algorithm sees two non-overlapping insertions at the same location. It may interleave them or place one before the other -- but the result is a document with two sections jammed together with no structural coherence between them. There is no conflict marker because the lines are technically different.

2. **Semantic conflicts invisible to text diff:** The user changes a rule from "Use `-` for unordered lists" to "Use `*` for unordered lists." The plugin update rewrites the paragraph containing that rule to add more detail but keeps `-`. The merge sees the user changed line 34, the plugin changed lines 33-36. If the user's edit is on a different line from the plugin's, the merge silently produces a paragraph that says "Use `-` for unordered lists" in the new expanded text -- erasing the user's preference without any conflict marker.

3. **Structural rearrangement:** The plugin reorganizes sections (moves "Code Blocks" before "Links"). The user has added custom content under "Code Blocks." The merge algorithm tracks lines, not sections. It may duplicate the user's content, lose it, or place it under the wrong heading.

4. **Whitespace-sensitive context:** Markdown is whitespace-sensitive (indentation for nested lists, blank lines for paragraph breaks). Merge algorithms that normalize whitespace can break list nesting or create fused paragraphs.

**Why it happens:**
Text-based 3-way merge treats files as sequences of lines with no understanding of Markdown structure. It cannot distinguish a heading from a paragraph, a section boundary from a blank line. Guidance files are long-form prose with section structure -- exactly the format where text merge is weakest.

**Consequences:**
User sees "Upgrade complete" but their guidance file now contains garbled sections, lost customizations, or contradictory rules. The damage is invisible until an agent writes docs using the corrupted guidance and produces output that violates the user's preferences.

**Prevention:**
1. Do NOT attempt line-level 3-way merge on guidance files. These are opinionated prose documents, not code files.
2. Instead, use **section-level merge**: parse both files by heading (## sections), compare section-by-section, and apply these rules:
   - Section exists in both and is unchanged from base: take plugin's updated version (user never touched it).
   - Section exists in both and user modified it: keep user's version, append a comment noting the plugin's version changed. Surface this as a conflict for user review.
   - Section exists only in plugin's new version: append it to the user's file.
   - Section exists only in user's file (user added it): keep it.
   - Section was removed in plugin's new version but user kept it: keep user's version, warn that plugin removed the section.
3. Store the plugin's original version of each guidance file at setup time (the "base" for future 3-way comparisons). Without this base, you have only 2-way merge, which cannot distinguish "user changed it" from "plugin changed it."
4. If section-level merge is too complex for MVP, use a simpler strategy: **show diff, ask user.** Present what changed in the plugin's version and let the user accept/reject per-section. This is slower but never silently wrong.

**Detection:**
- After merge, diff the result against the user's pre-upgrade file. If any user content disappeared, the merge was wrong.
- Count headings in the merged file vs. the union of headings from both inputs. Missing headings = lost sections.

**Phase to address:** The 3-way merge implementation phase. This is the single highest-risk feature in the milestone.

---

### Pitfall 2: Existing v1.0-v1.4 Projects Have No Base Snapshot, Making 3-Way Merge Impossible

**What goes wrong:**
3-way merge requires three inputs: base (original plugin version at setup time), theirs (current plugin version), ours (user's current file). Existing projects set up before v1.5.0 have no stored base. The `.doc-writer/` directory contains the user's current files, but there is no record of what the plugin's original looked like when setup ran.

Without a base, you can only do 2-way merge (user's file vs. new plugin version), which cannot distinguish:
- "User added this paragraph" (should keep) vs. "Plugin had this paragraph but removed it in the update" (should remove)
- "User changed this rule" (should preserve) vs. "This rule was always there and plugin now wants to change it" (both changed -- conflict)

Every difference between the user's file and the plugin's new version looks like a conflict because there is no base to determine who changed what.

**Why it happens:**
Version tracking was not part of the v1.0-v1.4 design. The setup flow copies files but does not store originals. The `version: 1` field in config.yaml is a schema version, not a plugin version.

**Consequences:**
The upgrade command either (a) treats every existing project as "fully customized" and shows hundreds of false conflicts, or (b) assumes nothing was customized and overwrites user edits, or (c) refuses to upgrade existing projects ("please re-run setup with --reset").

**Prevention:**
1. **Bootstrap the base on first upgrade:** When upgrade runs on a project with no stored originals, use a heuristic: diff the user's file against every historical version of the plugin's default file. The version with the smallest diff is the likely base. If the diff is zero (user never edited), confidently use the current plugin version as a clean replacement.
2. **Simpler bootstrap:** Compare the user's file against the v1.0 plugin default (the only historical version for most files). If identical, record v1.0 as base and proceed with 3-way merge. If different, flag the file as "customized, base unknown" and use the diff-and-ask approach from Pitfall 1 prevention.
3. **Store originals going forward:** At upgrade time (not just setup time), store the plugin's version of every copied file in a `.doc-writer/.originals/` directory. This becomes the base for the next upgrade.
4. **Do NOT require --reset for existing projects.** This throws away user customizations and defeats the purpose of upgrade. The whole point is smooth migration, not "nuke and rebuild."

**Detection:**
- Check for `.doc-writer/.originals/` directory. If missing, this is a pre-v1.5 project.
- Compare each user file against the plugin's defaults. Zero-diff files are safe to replace. Non-zero-diff files need the heuristic approach.

**Phase to address:** Must be the first thing implemented -- the originals storage mechanism -- because every other upgrade feature depends on having a base for comparison.

---

### Pitfall 3: Config Schema Migration Silently Drops User Data on Field Rename or Restructure

**What goes wrong:**
The v1.0 config template has different fields than the v1.4 template. The live config in this repo is missing `tone`, `use_cases`, `use_cases_section`, and `user_tasks` (all added in v1.4). A naive migration that "adds missing fields with defaults" works for additive changes. But if a future version renames a field (e.g., `skill_level` to `experience_level`) or restructures a section (e.g., flattening nested `paths.docs_root` to top-level `docs_root`), the migration adds the new field with a default and ignores the old field -- silently losing the user's actual value.

Concretely for the current upgrade: the v1.0 config has no `user_tasks` on persona entries. The migration adds `user_tasks: []`. But the user may have been relying on the persona's `domain_context` to convey task information. The empty `user_tasks` now signals "no tasks" to downstream agents, degrading persona quality.

**Why it happens:**
Additive migration ("add field if missing, set default") does not account for semantic relationships between old and new fields. The migration code does not know that `user_tasks` conceptually replaces or supplements part of what `domain_context` was carrying.

**Consequences:**
User upgrades, config looks fine, but downstream agent behavior degrades because new fields have empty/default values where meaningful values should exist. The user does not realize the persona is now less effective because `user_tasks: []` overrides the previous implicit inference from `domain_context`.

**Prevention:**
1. **Migration functions, not field diffing.** Each version-to-version transition gets an explicit migration function that knows the semantic relationships. `v1_to_v1.4` knows to populate `user_tasks` from the persona's `domain_context` if possible, or flag it for user input.
2. **Never silently default a field that affects agent behavior.** If a new field materially changes how agents work (like `tone` or `user_tasks`), the migration must either (a) infer a value from existing data, or (b) ask the user. Silent empty defaults are only acceptable for truly optional fields.
3. **Version-stamped migration chain:** Each config records `plugin_version: "1.5.0"` (distinct from the existing `version: 1` schema version). Migrations run sequentially: v1.0 -> v1.4 -> v1.5. Skipping versions applies all intermediate migrations in order. Never write a "jump" migration that goes directly from v1.0 to v1.5 -- this creates a combinatorial explosion of source/target pairs.
4. **Preserve unknown fields.** If the user has added custom fields to config.yaml (which YAML allows), the migration must not strip them. Parse, transform, and re-serialize without dropping unrecognized keys.

**Detection:**
- After migration, validate that no field with a user-meaningful value in the old config was lost or defaulted.
- Log what the migration did: "Added `tone: ""` (new field, no value inferred), Added `use_cases: []` (new field), Preserved `user_personas` (unchanged)."

**Phase to address:** Config migration must ship in the same phase as version tracking. These are inseparable -- you cannot track versions without knowing how to migrate between them.

---

### Pitfall 4: Q&A Gap Detection Re-Asks Questions Users Already Answered

**What goes wrong:**
The upgrade flow needs to detect "new questions since last setup" so it can ask only those. But framework Q&A answers are NOT stored in config.yaml -- they are passed in-memory to the researcher and discarded. When upgrade runs, there is no record of which Q&A questions the user already answered or what they chose.

The gap detection logic then falls back to "ask all framework questions" (treating every question as new), which forces the user through the full Q&A flow again. This is especially frustrating because the user already made these choices, the choices are reflected in their running system (guidance file, context.md), and re-answering produces identical results.

Worse: if the user does not remember their original answers, they might choose differently, causing the researcher to regenerate context.md with conflicting assumptions.

**Why it happens:**
The v1.0 design intentionally kept Q&A answers ephemeral ("Framework Q&A answers do NOT go into config.yaml. Store them in-memory"). This was fine for setup (run once) but breaks for upgrade (needs to know what was already answered).

**Consequences:**
- Users are annoyed by redundant questions ("I already told you this").
- Users who answer differently trigger a context.md regeneration that may conflict with their customized guidance file.
- The upgrade flow feels like a full re-setup, not an incremental update.

**Prevention:**
1. **Store Q&A answers in config.yaml starting with v1.5.** Add a `framework_qa:` section that records question IDs and selected options. This is a one-time schema change that enables all future gap detection.
2. **For existing projects without stored answers:** Infer from artifacts. Read the guidance file and context.md to detect which features were configured. For example, if the guidance file mentions mermaid, infer that Q3 "Rich features" included "Mermaid diagrams." This is imperfect but avoids re-asking obvious questions.
3. **Question identity must be stable.** Each question in `.qa.md` files needs a stable identifier (not just "Question 1" -- what if questions are reordered?). Use semantic IDs: `nav-strategy`, `api-reference`, `rich-features`. Gap detection compares stored answer IDs against current question IDs to find new ones.
4. **Distinguish "new question" from "question with new options."** If Q3 adds a new option ("Code annotations") but the user already answered Q3, do NOT re-ask the full question. Instead, present only the new option: "A new feature is available: Code annotations. Enable it?"
5. **Never auto-answer on behalf of the user.** If gap detection finds a new question, ask it. If it finds a question with new options, present just the delta. But never silently apply a default for a question the user was supposed to answer.

**Detection:**
- Count questions asked during upgrade. If it equals the total Q&A count, gap detection is broken (re-asking everything).
- After upgrade, compare stored `framework_qa` answers against the actual Q&A file. Missing IDs = unanswered new questions. Extra IDs = questions that were removed (warn, do not error).

**Phase to address:** Q&A storage must be added to the config schema in the same phase as version tracking (it is a schema change). Gap detection logic ships in the upgrade flow phase.

---

### Pitfall 5: Upgrade Assumes Clean Setup State -- Breaks on Partially Configured or Manually Edited Projects

**What goes wrong:**
The upgrade flow assumes `.doc-writer/` was created by the setup flow and follows the expected structure: config.yaml with known fields, guidance file matching `doc_system`, rules.md present, context.md generated by researcher. Real-world projects deviate:

1. **Partially configured:** User ran setup, answered personas, but cancelled before the researcher ran. `.doc-writer/context.md` does not exist. Upgrade tries to merge context.md and crashes or skips context enrichment.
2. **Manually created config:** User hand-wrote config.yaml with custom fields, different indentation, comments. YAML parsing works, but the migration function expects specific field names and types. A typo like `user_persona:` (singular) instead of `user_personas:` (plural) causes the migration to add a new `user_personas:` field while the old `user_persona:` remains -- config now has both, and agents read the wrong one.
3. **Renamed or missing guidance file:** User renamed `plain-markdown.md` to `my-style.md` or deleted it. Upgrade looks for `{doc_system}.md`, does not find it, and either crashes or creates a new default file alongside the user's renamed file.
4. **Extra files in .doc-writer/:** User added custom files (the live project has `terminology.yaml`, `gap-report.md`, `page-inventory.md`, `editor-report.md`, `scenarios.yaml`, `persona-report.md`). Upgrade must not touch, move, or delete these.
5. **Config with `version: 1` but no `plugin_version`:** Every existing project. The upgrade must handle this as "unknown plugin version" and run all migrations from the earliest known version.

**Why it happens:**
Upgrade code is typically developed against freshly-setup test projects (greenfield). Edge cases from the installed base -- partial configs, manual edits, extra files -- are not represented in test fixtures.

**Consequences:**
Upgrade fails on real projects while passing all tests. Users report "upgrade crashed" or "upgrade broke my config" -- exactly the opposite of the smooth experience intended.

**Prevention:**
1. **Validate before migrating.** Before any upgrade operation, verify the `.doc-writer/` directory state:
   - config.yaml exists and parses as valid YAML
   - config.yaml has `doc_system` field (required for guidance file lookup)
   - config.yaml has `user_personas` (plural, array)
   - Guidance file `{doc_system}.md` exists (or warn if missing)
   - Record what is missing or unexpected; proceed with what exists
2. **Tolerate missing files.** If context.md is missing, skip context merge and offer to re-run the researcher. If rules.md is missing, copy the default. Never crash on a missing optional file.
3. **Tolerate unknown config fields.** Parse config.yaml permissively. Migrate known fields, preserve unknown fields. Warn about fields that look like typos of known fields (Levenshtein distance check: `user_persona` vs `user_personas`).
4. **Never touch files outside the upgrade scope.** Any file in `.doc-writer/` that is not config.yaml, `{doc_system}.md`, rules.md, or context.md should be left completely untouched. Do not list them, do not warn about them, do not migrate them.
5. **Build test fixtures from real projects, not fresh setups.** The live `.doc-writer/` directory in this repo is a v1.0-era project -- use it (or a sanitized copy) as the primary test case for upgrade. Also test: config with no `tone`, config with no `use_cases`, config with comments, config with custom fields.

**Detection:**
- Run upgrade on a copy of the live `.doc-writer/` directory. If it fails or produces warnings about unexpected files, the validation layer is missing.
- Check that `terminology.yaml`, `gap-report.md`, `scenarios.yaml`, etc. are untouched after upgrade.

**Phase to address:** Validation layer must ship in the first upgrade phase, before any merge or migration logic runs.

---

## Moderate Pitfalls

### Pitfall 6: Version Tracking Breaks on Version Skipping, Downgrade, and Cross-Machine Sync

**What goes wrong:**
User at plugin v1.4 skips v1.5 and upgrades to v1.6. The migration chain expects v1.4 -> v1.5 -> v1.6, but if v1.5 migration had side effects (added a field, restructured a section), the v1.5 -> v1.6 migration assumes those side effects already happened. Skipping breaks the chain.

Downgrade: user at v1.6 installs an older plugin (v1.5). The config now has a `plugin_version` higher than the installed plugin. The upgrade command either (a) refuses to run, (b) tries to "downgrade" the config, or (c) ignores the version mismatch and runs v1.5 logic on v1.6 data.

Cross-machine: user syncs `.doc-writer/` via git. Machine A has plugin v1.5, machine B has plugin v1.6. Machine B upgrades config to v1.6 schema. User pulls on machine A (still v1.5). Machine A does not understand v1.6 config fields.

**Prevention:**
1. **Migrations must be idempotent.** Running v1.4 -> v1.5 migration on a config that already has v1.5 fields should be a no-op, not an error or duplicate. Check "is this field already present and populated?" before adding.
2. **Forward compatibility: ignore unknown fields.** Older plugin versions must not crash on config fields they do not recognize. Parse permissively, use what you understand, ignore the rest.
3. **Downgrade detection:** If `plugin_version` in config is newer than the installed plugin, warn the user: "This config was created by a newer version of doc-writer. Some features may not work." Do NOT attempt to downgrade the config -- that path is a minefield.
4. **Sequential migration chain with idempotent steps.** Always run all migrations from the recorded version to the current version, in order. Each step checks preconditions before acting.

---

### Pitfall 7: Originals Storage Doubles Disk Footprint and Creates Sync Confusion

**What goes wrong:**
Storing original plugin files in `.doc-writer/.originals/` means every guidance file, rules file, and Q&A file exists twice -- the user's copy and the original. This doubles the `.doc-writer/` footprint (currently ~10KB, so the absolute size is fine, but the conceptual overhead matters).

The real problem: users see `.originals/plain-markdown.md` alongside `plain-markdown.md` and:
- Edit the wrong file (editing the original instead of their copy)
- Commit `.originals/` to git and create merge conflicts when collaborators upgrade at different times
- Delete `.originals/` to "clean up" and break future upgrades

**Prevention:**
1. **Name the directory unambiguously:** `.doc-writer/.plugin-base/` rather than `.originals/`. The name signals "this is the plugin's reference copy, do not edit."
2. **Add a README in the directory:** A one-line file: "These files are plugin reference copies used for upgrade diffing. Do not edit. They are regenerated on each upgrade."
3. **Add `.doc-writer/.plugin-base/` to `.gitignore` recommendation.** During upgrade, suggest adding it if not already ignored. This prevents cross-machine sync conflicts.
4. **Validate integrity on upgrade:** Before using a base file for 3-way merge, verify it matches the expected plugin version. If the base was tampered with, fall back to the diff-and-ask approach.

---

### Pitfall 8: Upgrade Command Conflicts with Existing Setup Re-Run Flow

**What goes wrong:**
The existing setup flow already handles "config exists" with an update menu (edit personas, change tone, re-run researcher). The new `/doc-writer:upgrade` command handles plugin-level changes (new guidance content, config schema migration, new Q&A questions). If the boundaries are unclear, users do not know which command to use, and the commands may interfere:

1. User runs `upgrade`, which migrates config and adds `tone: ""`. Then runs `setup` to set the tone. Setup reads the config, sees `tone: ""`, and treats it as "already configured" (field exists) rather than "needs input" (field is empty).
2. User runs `setup --reset` after upgrading, which overwrites the migrated config with a fresh template, losing migration metadata (`plugin_version`, `framework_qa` answers).
3. User runs `upgrade` while setup is mid-flight (unlikely in CLI, but possible if upgrade is triggered by a hook). Config is in a half-written state.

**Prevention:**
1. **Clear command separation:** `upgrade` handles plugin-version changes only (merge guidance files, migrate config schema, detect new Q&A). `setup` handles user-preference changes only (edit personas, change tone, switch doc system). Document this distinction in both command help texts.
2. **Upgrade sets fields to sentinel values, not empty strings.** When adding `tone`, set it to a value like `"(pending -- run /doc-writer:setup to configure)"` rather than `""`. This makes it obvious the field needs user input and setup can detect it as "needs configuration."
3. **Setup --reset must preserve upgrade metadata.** When resetting, keep `plugin_version` and `.plugin-base/` directory. Reset user preferences (personas, tone, doc system) but not the migration tracking infrastructure.
4. **Lock file during operations.** Write a `.doc-writer/.lock` file at the start of upgrade/setup; check for it at the start of both commands. Remove on completion. This prevents concurrent modification.

---

### Pitfall 9: Researcher Re-Run After Upgrade Overwrites User-Edited context.md

**What goes wrong:**
After upgrade adds new config fields or updates guidance files, it re-runs the researcher to regenerate `context.md`. But `context.md` may contain user edits (the setup flow's confirmation message says it is "editable"). The researcher writes `context.md` from scratch based on config + source code scan -- it does not merge with the existing file.

User's hand-added context ("This project uses a proprietary authentication system -- always document auth flows using the `AuthManager` class") vanishes after upgrade.

**Prevention:**
1. **Backup context.md before researcher re-run.** Save to `.doc-writer/context.md.pre-upgrade`. If the user notices lost content, they can recover.
2. **Better: preserve user additions.** If context.md has a `## User Notes` or `## Custom Context` section (or any section not generated by the researcher), preserve those sections and append them to the regenerated file.
3. **Best: make researcher re-run optional during upgrade.** After config migration and guidance merge, ask: "Re-run researcher to update context.md? (Your edits to context.md will be preserved in a backup.)" Let the user decide.

---

## Minor Pitfalls

### Pitfall 10: Plugin Version Detection Fails When Plugin Is Installed via Different Methods

**What goes wrong:**
The upgrade command needs to know the current plugin version. If the plugin is installed via git clone, the version can be read from a version file or git tags. If installed via marketplace, the version comes from `marketplace.json`. If copied manually, there may be no version indicator at all.

**Prevention:**
1. Store the plugin version in a canonical location: `doc-writer/.claude-plugin/VERSION` (simple text file). Read this first, regardless of installation method.
2. Fall back to `marketplace.json` version field if VERSION file is missing.
3. If neither exists, warn the user and ask them to confirm which version they have.

---

### Pitfall 11: YAML Round-Trip Destroys Comments and Formatting

**What goes wrong:**
config.yaml may contain user comments (YAML allows `# comment`). Standard YAML parsers (PyYAML, js-yaml, most libraries) discard comments on parse. After migration re-serializes the config, all comments are gone. Users who documented their choices ("# Changed to expert because team is all senior devs") lose that context.

Additionally, YAML serialization may reorder keys, change quote styles, or alter indentation. The file is semantically identical but textually different, creating noisy git diffs.

**Prevention:**
1. Since this is an LLM-driven plugin (the agent reads and writes files), the migration should **read the YAML, determine what changes are needed, then surgically edit the file** rather than parse-transform-serialize. The LLM can preserve comments, formatting, and ordering naturally.
2. If programmatic migration is needed (bash scripts), use tools that preserve comments (`yq` with `--inplace` mostly preserves comments, though not perfectly).
3. Add comments sparingly to config.yaml template to minimize what can be lost.

---

### Pitfall 12: Guidance File Merge Produces Valid Markdown That Is Semantically Contradictory

**What goes wrong:**
After merging, the guidance file contains two contradictory rules: the user's rule ("Use `*` for unordered lists") and the plugin's updated rule ("Use `-` for unordered lists. Do not use `*` or `+`"). Both are valid Markdown paragraphs. The file parses fine. But the agent now has contradictory instructions and will follow whichever one it encounters last (or arbitrarily).

**Prevention:**
1. After any merge, run a semantic consistency check: scan for contradictory instructions within the same section. This is where the LLM-driven nature of the system is an advantage -- the agent performing the upgrade can read the merged file and flag contradictions.
2. When surfacing conflicts to the user, show both versions side-by-side with the prompt: "These instructions conflict. Which should the agents follow?"
3. Never silently include both sides of a semantic conflict. If the merge cannot determine which version to keep, it must ask.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Version tracking + config schema | Existing projects have no `plugin_version`; migration must handle "unknown version" as v1.0 | Default to earliest version; run full migration chain |
| Version tracking + config schema | `version: 1` in existing configs is schema version, not plugin version -- do not confuse them | Use distinct field names: keep `version` for schema, add `plugin_version` for plugin |
| Originals storage | First upgrade on existing project has no base files | Bootstrap: compare user's file against plugin defaults to detect customization; store current plugin defaults as base for next upgrade |
| Guidance file merge | Section-level merge requires consistent heading structure across versions | Standardize heading format in all guidance files; use `## Section Name` as the merge unit |
| Guidance file merge | User adds content between sections (e.g., a paragraph between two `##` headings) | Treat inter-heading content as belonging to the preceding section |
| Config migration | v1.0 configs missing `tone`, `use_cases`, `use_cases_section`, `user_tasks`, `odoc_author_scope` | Each field gets a migration rule: infer from existing data or flag for user input |
| Config migration | `user_tasks` added as empty array when persona's `domain_context` already implies tasks | Migration should infer basic tasks from `domain_context` rather than defaulting to empty |
| Q&A gap detection | No stored Q&A answers in pre-v1.5 projects | Infer from guidance file and context.md what was likely configured |
| Q&A gap detection | Question IDs change between versions (reordered, renamed) | Use semantic IDs, not positional numbering |
| Q&A gap detection | Distinguishing "new question" from "existing question with new options" | Store both question ID and option selections; detect new options within answered questions |
| Upgrade + setup interaction | Upgrade adds fields with empty defaults; setup treats them as "already configured" | Use sentinel values or a "needs_configuration" flag on migration-added fields |
| Upgrade + setup interaction | `--reset` wipes upgrade metadata | Preserve `plugin_version` and `.plugin-base/` on reset |
| Researcher re-run | context.md user edits lost on regeneration | Backup before regeneration; preserve user-added sections |
| Testing | Tests use fresh setups, not real installed-base configs | Build test fixtures from actual v1.0-era `.doc-writer/` directories |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Upgrade + existing config.yaml | Parsing config.yaml with strict schema validation that rejects unknown fields | Parse permissively; migrate known fields; preserve unknown fields; warn on likely typos |
| Upgrade + existing guidance files | Attempting line-level 3-way merge on prose documents | Use section-level comparison or diff-and-ask; never silently merge prose |
| Upgrade + researcher | Re-running researcher unconditionally after every upgrade | Only re-run if config changes affect researcher input (new doc_system, new personas, new Q&A answers); otherwise skip |
| Version tracking + config `version` field | Using existing `version: 1` field for plugin version tracking | Add separate `plugin_version` field; `version` remains the config schema version |
| Q&A storage + config migration | Adding `framework_qa` section only for new setups, forgetting existing projects | Migration adds `framework_qa: {}` to existing configs; first upgrade populates it from inference |
| Originals storage + git | Committing `.plugin-base/` directory to the project's git repo | Recommend adding `.doc-writer/.plugin-base/` to `.gitignore`; it is machine-local upgrade state |
| Setup --reset + upgrade metadata | `--reset` deletes everything in `.doc-writer/` including `.plugin-base/` and `plugin_version` | Reset preserves upgrade infrastructure; only resets user preferences |
| Upgrade + custom doc systems | Upgrade assumes `{doc_system}.md` comes from plugin defaults; custom/researched frameworks wrote to `.doc-writer/` directly | Check `framework_root` from config or infer from file location; do not assume plugin defaults directory |
| Upgrade + odoc_author_scope | Migration adds `odoc_author_scope: ""` to all configs, even non-odoc projects | Only add `odoc_author_scope` when `doc_system` is `odoc`; omit entirely for other frameworks |

## "Works for Greenfield but Breaks Existing" Checklist

These are the specific ways upgrade code typically works perfectly on test projects but fails on real installed-base projects:

- [ ] **Config missing fields added in v1.4:** Live config has no `tone`, `use_cases`, `use_cases_section`, `user_tasks`. Migration must add each with appropriate defaults or inferred values, not crash on their absence.
- [ ] **Config has extra fields:** Live config may have fields the migration does not expect (e.g., `api_reference: ""`). Migration must preserve them.
- [ ] **Guidance file identical to plugin default:** Common case -- user never edited it. Upgrade should detect this (zero diff from known default) and silently replace with the new version. No merge needed, no user prompt.
- [ ] **Guidance file with minor edits:** User changed one rule. Upgrade must preserve that change while applying plugin updates to other sections.
- [ ] **Guidance file completely rewritten:** User replaced the entire file. Upgrade should detect this (high diff from any known default) and skip merge entirely, offering to show what changed in the plugin's version.
- [ ] **No context.md:** Partially configured project. Upgrade should not crash; offer to run researcher.
- [ ] **Extra files in .doc-writer/:** `terminology.yaml`, `gap-report.md`, `scenarios.yaml`, etc. Upgrade must not touch them.
- [ ] **Different directory structure per doc system:** odoc projects have `doc/dune`, `doc/index.mld` files that mkdocs projects do not. Upgrade logic that scans `.doc-writer/` must not be confused by framework-specific artifacts.
- [ ] **Custom doc system from researcher fallback:** A project using a custom framework (e.g., "docusaurus") has guidance files in `.doc-writer/` (not the plugin defaults directory) and may have been generated by the researcher, not copied from defaults. Upgrade cannot assume these files have a known base version.
- [ ] **config.yaml with YAML comments:** User may have added `# comments` explaining their choices. Migration must not strip them.
- [ ] **config.yaml created by different plugin versions:** Two team members set up doc-writer at different times, producing configs with different field sets. Both are valid; both must be upgradeable.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| 3-way merge corrupts guidance file | LOW | Restore from `.doc-writer/.plugin-base/` (the pre-upgrade backup) and re-run upgrade with manual review |
| Config migration loses user data | MEDIUM | No automatic recovery if no backup. Prevention: always write `config.yaml.pre-upgrade` before migrating. Recovery: diff `.pre-upgrade` against current config, manually restore lost fields |
| Q&A re-asks all questions | LOW (annoying, not destructive) | User re-answers; results are identical to original. Fix: store answers in config going forward |
| Upgrade crashes on unexpected config format | LOW | Fix the parser, re-run upgrade. User's files are unmodified (crash happened before writes) |
| Researcher overwrites custom context.md | MEDIUM | Recovery depends on whether backup was made. If `context.md.pre-upgrade` exists: restore user sections. If not: user must re-add custom content from memory or git history |
| .plugin-base/ deleted by user | LOW | Upgrade falls back to 2-way diff-and-ask approach. Less automated, but functional. .plugin-base/ is recreated on next upgrade |
| Upgrade + setup conflict | MEDIUM | Determine which command ran last from config state. If upgrade metadata is missing, re-run upgrade. If user preferences are wrong, re-run setup for the affected field |

## Sources

- [Three-Way Merge algorithms](https://tonyg.github.io/revctrl.org/ThreeWayMerge.html) -- base selection importance, conflict detection rules (MEDIUM confidence, community reference)
- [Merging with diff3](https://blog.jcoglan.com/2017/05/08/merging-with-diff3/) -- diff algorithm sensitivity, reverted change edge case (MEDIUM confidence, well-known technical blog)
- [Git merge strategies (official docs)](https://git-scm.com/docs/merge-strategies) -- semantic conflicts invisible to text merge, rename detection heuristics (HIGH confidence, official docs)
- [Backward compatibility in schema evolution](https://www.dataexpert.io/blog/backward-compatibility-schema-evolution-guide) -- additive changes, default values, migration patterns (MEDIUM confidence, technical blog)
- [YAML schema versioning (SUEWS docs)](https://suews.readthedocs.io/latest/contributing/schema/schema_versioning.html) -- version field, migration chain pattern (LOW confidence, niche project docs)
- [Flyway out-of-order migrations](https://www.baeldung.com/flyway-migrations) -- skip-version handling, sequential migration chain (MEDIUM confidence, well-known technical reference)
- [Plugin architecture versioning](https://oninebx.github.io/blog/architecture/plugin-architecture-in-practice-part-4-versioning-distribution-and-ecosystem/) -- parallel version support, migration strategies (LOW confidence, blog post)
- [Helm provider upgrade guide](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/guides/v2-upgrade-guide) -- upgrade_install overwrites original values, state mismatch on adoption (HIGH confidence, official docs)
- [Craft CMS version mismatch](https://github.com/craftcms/cms/issues/4914) -- config file created for different versions error pattern (MEDIUM confidence, official issue tracker)
- Codebase: `.doc-writer/config.yaml` -- verified v1.0-era config missing `tone`, `use_cases`, `use_cases_section`, `user_tasks` fields (HIGH confidence, direct file reading)
- Codebase: `doc-writer/skills/setup/defaults/config-template.yaml` -- verified v1.4 template has all current fields (HIGH confidence, direct file reading)
- Codebase: `doc-writer/skills/setup/SKILL.md` -- verified Q&A answers are ephemeral ("do NOT go into config.yaml"), existing re-run flow handles config updates, `--reset` behavior (HIGH confidence, direct file reading)
- Codebase: `.doc-writer/` directory listing -- verified extra files exist (terminology.yaml, gap-report.md, scenarios.yaml, etc.) that upgrade must not touch (HIGH confidence, direct directory listing)

---
*Pitfalls research for: doc-writer v1.5.0 Plugin Upgrade Helpers milestone*
*Researched: 2026-03-26*
