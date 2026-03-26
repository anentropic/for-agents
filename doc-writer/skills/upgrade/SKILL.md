---
name: doc-writer:upgrade
description: Upgrade doc-writer configuration after a plugin update. Detects version changes, migrates config fields, updates unchanged files, and reports all changes.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: ""
---

# Doc Writer Upgrade

Upgrade the doc-writer configuration after the plugin has been updated. Detects version changes, migrates config fields, updates unchanged files, and reports all changes in a summary.

## User Interaction Pattern

This skill uses AskUserQuestion for structured choices. When the user selects:
- **"Type something else"** or **"Other"**: Ask your follow-up as plain text. Wait for their response. Then resume the workflow.
- **"Chat about this"**: Explain the current decision in depth. Open a plain-text dialogue. After it resolves, re-present the original question or proceed based on what was discussed.

Never respond to these selections with another AskUserQuestion.

## Instructions

Follow these steps in order. Read each section carefully before acting.

### Step 1: Version Detection

Determine whether an upgrade is needed by comparing the project's stored plugin version against the installed plugin version.

1. Read `.doc-writer/config.yaml`.
   - **If the file does not exist:** Inform the user: "No doc-writer configuration found. Run `/doc-writer:setup` first." **Stop.**

2. Extract the `plugin_version` field from config.yaml.
   - **If the `plugin_version` field is absent or empty:** Treat the version as `"unknown"`. Display: "Config has no plugin_version field -- treating as pre-1.5.0 project." Continue to step 3.
   - **If `plugin_version` is present:** Record its value as the OLD version.

3. Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Extract the `version` field (this is the NEW version -- the currently installed plugin version).

   **IMPORTANT:** This is the `version` field in plugin.json, NOT `plugin_version`. Do not confuse these two fields.

4. **If the OLD version equals the NEW version:** Display: "doc-writer is already up to date (version {version})." **Stop.** No changes needed.

5. Display: "Upgrading doc-writer from {old_version} to {new_version}..."

6. Store both the OLD and NEW versions for use in the Step 4 summary.

**CRITICAL:** Do NOT write the new plugin_version to config.yaml in this step. The plugin_version update must happen LAST, in Step 4, after all migration is complete. Writing it early would cause subsequent upgrade attempts to see "already up to date" even if migration was incomplete.

### Step 2: Config Format Migration

Compare the user's config fields against the current plugin's config template to detect new fields that need to be added and deprecated fields that need to be removed.

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/config-template.yaml` as the canonical config schema.

2. Read the user's `.doc-writer/config.yaml` if not already in memory from Step 1.

3. Compare the fields in the user's config.yaml against the fields in config-template.yaml.

   **Exclude these meta-fields from comparison** -- they are managed programmatically by setup/upgrade, not user-configured fields:
   - `version` (config schema version, e.g., `version: 1`)
   - `plugin_version` (plugin release version, e.g., `plugin_version: "1.5.0"`)
   - `detected` (auto-detection results section)
   - `qa_answers` (framework Q&A answer storage)

   Only compare user-configurable fields: `user_personas`, `tone`, `use_cases`, `use_cases_section`, `doc_system`, `api_reference`, `paths`, and any other fields NOT in the exclusion list above.

4. **Identify new fields** -- fields present in config-template.yaml but absent from the user's config.yaml (after excluding meta-fields).

   For each new field, examine the user's existing config values holistically to infer an appropriate value. The inference should feel natural -- as if the user had been asked the question during setup and answered based on their existing configuration.

   **Inference rules by field type:**

   - **String field:** Infer from other config fields with related semantics. For example, `domain_context` can be inferred from persona name, assumed_knowledge, and discovery_story.
   - **Array field:** Infer from related arrays or decomposition of existing string fields. For example, `user_tasks` can be inferred from domain_context if it describes what users do with the library.
   - **Boolean field:** Infer from existing config state. For example, `use_cases_section: false` if `use_cases` is empty or contains only blank placeholder entries.
   - **Nested object:** Infer from existing flat fields or reasonable project-context defaults. For example, `paths.docs_root` from any existing path configuration.

   **If inference is clear and unambiguous** (single obvious source, one plausible interpretation): Write the inferred value silently. Record for the summary: "Added {field}: {value} (inferred from {source})".

   **If inference is ambiguous** (more than one plausible interpretation, even if you could pick one): Use AskUserQuestion to ask the user:
   - header: "Config Migration"
   - question: "New field '{field_name}' needs a value. Based on your config, it could be: ..."
   - options:
     - { label: "{option_1}", description: "{what this value means}" }
     - { label: "{option_2}", description: "{what this value means}" }
     - { label: "Type something else", description: "Provide a custom value" }
     - { label: "Chat about this", description: "Discuss what this field controls" }

   **NEVER copy placeholder/empty values from config-template.yaml.** The template contains empty strings (`""`), empty arrays (`[]`), and placeholder structures. Every new field must have a real, inferred value -- not a blank default.

5. **Identify deprecated fields** -- fields present in the user's config.yaml but absent from config-template.yaml (after excluding meta-fields).

   Auto-remove deprecated fields without prompting. Record for the summary: "Removed deprecated field: {field}".

6. **If no new fields AND no deprecated fields were detected:** Record "No config schema changes" for the summary. Do NOT write config.yaml unnecessarily.

7. **If changes were made** (new fields added or deprecated fields removed): Write the updated config.yaml with new fields added in their natural position and deprecated fields removed. Preserve all existing user values for unchanged fields. Maintain YAML formatting and comments.

### Step 3: Unchanged File Update

Compare project-side guidance and rules files against their `.originals/` baselines to detect which files can be silently updated to the new plugin version.

1. Check if `.doc-writer/.originals/` directory exists. Use Glob for `.doc-writer/.originals/*`.

   - **If the directory does not exist or is empty:** Display: "This project was set up before upgrade support was available. File comparison skipped. Run `/doc-writer:setup --reset` to establish baseline files." Record this warning for the summary. **Skip to Step 4.**

2. Read the `doc_system` value from the user's config.yaml (needed to identify the guidance file name).

3. For each file found in `.doc-writer/.originals/` (typically `rules.md` and `{doc_system}.md`):

   a. Read `.doc-writer/.originals/{file}` -- this is **BASE** (the previous plugin default, stored at setup time).

   b. Read `.doc-writer/{file}` -- this is **USER** (the user's current working copy).

   c. Determine the corresponding new plugin default path: `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{file}`.

      Check if this file exists. **If it does not exist** (this happens for FALLBACK frameworks where the guidance file was researcher-generated, not shipped by the plugin): Skip this file. Record for the summary: "Skipped {file} -- not a plugin-shipped file."

   d. Read the new plugin default file -- this is **NEW** (the current plugin version's default).

   e. **If BASE content is identical to NEW content:** No upstream changes to this file in this plugin version. Skip. Nothing to report.

   f. **If USER content is identical to BASE content:** The user has NOT customized this file -- it still matches what was installed at setup time. Silently overwrite `.doc-writer/{file}` with the NEW content. **Also update `.doc-writer/.originals/{file}` with the same NEW content** (this is critical -- if you only update the user copy but leave .originals/ stale, future upgrades would see a diff between .originals/ and the user file and incorrectly treat the file as "customized"). Record for the summary: "Updated {file} to new plugin version."

   g. **If USER content differs from BASE content:** The user has customized this file. Do NOT modify it. Record for the summary: "Skipped {file} -- file has been customized. Merge support coming in a future upgrade."

### Step 4: Finalize

Update the stored plugin version and present the upgrade summary.

1. Write the new `plugin_version` value to config.yaml, replacing the old value (or adding it if it was absent). The new value is the `version` from plugin.json (read in Step 1). This is the **LAST** write to config.yaml -- all migration changes from Step 2 must already be written.

2. Display a consolidated upgrade summary:

```
## Upgrade Summary

**Version:** {old_version} -> {new_version}

### Config Changes
- {list each added field with its inferred value and inference source}
- {list each removed deprecated field}
- {or "No config schema changes"}

### File Updates
- {list each file updated (unchanged files overwritten with new plugin defaults)}
- {list each file skipped (customized by user, deferred to future merge)}
- {list each file skipped (FALLBACK framework, not a plugin-shipped file)}
- {or "No file updates" / ".originals/ not found -- file comparison skipped"}

### Warnings
- {any warnings from above steps, e.g., missing .originals/, missing plugin_version}
- {or "None"}
```

## Notes

- All plugin-internal file references use `${CLAUDE_PLUGIN_ROOT}` for portability across different installation locations.
- Config schema uses `user_personas:` as an array -- even for a single persona.
- The upgrade command delivers a complete minimal slice: version detection, config migration, unchanged-file update, and summary. Three-way merge for customized files and Q&A gap detection are handled by separate future upgrades to this command.
- When inferring config field values, read the user's existing configuration holistically. The goal is to produce values that feel like the user configured them during setup, not mechanical defaults.
