---
name: doc-writer:upgrade
description: Upgrade doc-writer configuration after a plugin update. Detects version changes, migrates config fields, updates unchanged files, and reports all changes.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
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

6. Store both the OLD and NEW versions for use in the Step 5 summary.

**CRITICAL:** Do NOT write the new plugin_version to config.yaml in this step. The plugin_version update must happen LAST, in Step 5, after all migration is complete. Writing it early would cause subsequent upgrade attempts to see "already up to date" even if migration was incomplete.

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

### Step 3: File Merge

Merge upstream plugin changes into the user's guidance and rules files using section-level comparison. Files are parsed into sections at `##` heading boundaries, and each section is classified independently to auto-apply non-conflicting changes and present conflicts to the user one at a time.

#### Section Parsing Rules

These rules apply to both the 2-way diff bootstrap path (Step 3.1) and the 3-way merge path (Step 3.3g). Parse each file into an ordered list of sections:

1. **Preamble**: Everything from the start of the file up to (but not including) the first line that starts with `## `. If no `## ` line exists, the entire file is the preamble. Identify this section as `__preamble__`.

2. **Named sections**: Each line starting with `## ` (at the document top level, NOT inside a fenced code block) begins a new section. The section includes the heading line and all content up to the next `## ` heading or end of file.

3. **Sub-headings are NOT section boundaries**: Lines starting with `### ` or `#### ` are part of their parent `## ` section. Do not split on them.

4. **Code block awareness**: When scanning for `## ` headings, track whether you are inside a fenced code block (between ``` delimiters). Skip any `## ` that appears within a fenced code block.

5. **Comparison**: When comparing two sections for equality, compare after trimming trailing whitespace from each line and normalizing trailing newlines. Semantic comparison, not byte-exact.

#### Step 3.1: Check for .originals/ Directory

Check if `.doc-writer/.originals/` directory exists. Use Glob for `.doc-writer/.originals/*`.

**If the directory exists and contains files:** Continue to Step 3.2 (3-way merge path).

**If the directory does not exist or is empty (2-way diff bootstrap):**

This project was set up before upgrade support was available. Since there are no original baseline files, a full 3-way merge is not possible. Instead, compare the user's current files against the current plugin defaults section by section.

1. Display: "This project was set up before upgrade support was available. Comparing your files against current plugin defaults section by section."

2. Read `doc_system` from the user's config.yaml.

3. For each file to compare (the `{doc_system}.md` guidance file and `rules.md`):

   a. Read the USER file from `.doc-writer/{file}`.

   b. Determine the NEW file path: `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{file}`. Check if it exists. **If it does not exist** (FALLBACK framework -- the guidance file was researcher-generated, not shipped by the plugin): Skip this file.

   c. Read the NEW file from plugin defaults.

   d. Parse both USER and NEW into sections using the section parsing rules above.

   e. For each section that is identical between USER and NEW: no action needed.

   f. For each section in NEW but not in USER (new section added by the plugin): present via AskUserQuestion:
      - header: "New Section"
      - question: "The plugin update adds a new section '{heading}' to {filename}:\n\n{first 10 lines of section, or full section if <= 10 lines}\n{if truncated: '... ({N} more lines)'}\n\nAdd this section?"
      - options:
        - { label: "Add", description: "Include this new section" }
        - { label: "Skip", description: "Do not add this section" }
        - { label: "Chat about this", description: "Discuss what this section covers" }

   g. For each section that exists in both USER and NEW but differs: present via AskUserQuestion:
      - header: "Section Difference"
      - question: "Section '{heading}' in {filename} differs from the current plugin version.\n\nYour version:\n---\n{first 10 lines of USER section, or full section if <= 10 lines}\n{if truncated: '... ({N} more lines)'}\n---\n\nPlugin version:\n---\n{first 10 lines of NEW section, or full section if <= 10 lines}\n{if truncated: '... ({N} more lines)'}\n---"
      - options:
        - { label: "Keep mine", description: "Preserve your current version of this section" }
        - { label: "Accept update", description: "Take the plugin version of this section" }
        - { label: "Type something else", description: "Provide a custom version of this section" }
        - { label: "Chat about this", description: "See full content and discuss the differences" }

   h. Sections in USER but not in NEW (user additions): keep silently.

   i. After all decisions for this file: write the merged result to `.doc-writer/{file}`. **Ordering:** NEW sections in their order, then user-only sections appended at the end.

   j. Create `.doc-writer/.originals/{file}` with the NEW (current plugin default) content -- NOT the merged content. The `.originals/` directory always tracks what the plugin shipped.

4. Record merge stats for each file in the summary. **Skip to Step 3.5.**

#### Step 3.2: Read doc_system

Read the `doc_system` value from the user's config.yaml (needed to identify the guidance file name).

#### Step 3.3: Merge Each File

For each file found in `.doc-writer/.originals/` (typically `rules.md` and `{doc_system}.md`):

a. Read `.doc-writer/.originals/{file}` -- this is **BASE** (the previous plugin default, stored at setup time).

b. Read `.doc-writer/{file}` -- this is **USER** (the user's current working copy).

c. Determine the corresponding new plugin default path: `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{file}`.

   Check if this file exists. **If it does not exist** (this happens for FALLBACK frameworks where the guidance file was researcher-generated, not shipped by the plugin): Skip this file. Record for the summary: "Skipped {file} -- not a plugin-shipped file."

d. Read the new plugin default file -- this is **NEW** (the current plugin version's default).

e. **If BASE content is identical to NEW content:** No upstream changes to this file in this plugin version. Skip. Nothing to report.

f. **If USER content is identical to BASE content:** The user has NOT customized this file -- it still matches what was installed at setup time. Silently overwrite `.doc-writer/{file}` with the NEW content. **Also update `.doc-writer/.originals/{file}` with the same NEW content** (this is critical -- if you only update the user copy but leave .originals/ stale, future upgrades would see a diff between .originals/ and the user file and incorrectly treat the file as "customized"). Record for the summary: "Updated {file} to new plugin version."

g. **If USER content differs from BASE content AND BASE content differs from NEW content:** The user has customized this file AND the plugin has updated it. Run the section-level 3-way merge:

   **Parse** BASE, USER, and NEW into sections using the section parsing rules above.

   **Classify** each section by building a unified section list from the union of all section keys across BASE, USER, and NEW. For each section key, apply the 3-way classification table:

   | In BASE? | In USER? | In NEW? | BASE==USER? | BASE==NEW? | USER==NEW? | Classification | Action |
   |----------|----------|---------|-------------|------------|------------|----------------|--------|
   | Y | Y | Y | Y | Y | - | Unchanged | Keep as-is |
   | Y | Y | Y | Y | N | - | Upstream only | Auto-apply NEW |
   | Y | Y | Y | N | Y | - | User only | Keep USER |
   | Y | Y | Y | N | N | Y | Convergent | Keep USER |
   | Y | Y | Y | N | N | N | **Conflict** | Ask user |
   | N | N | Y | - | - | - | Added upstream | Auto-add from NEW |
   | Y | Y | N | Y | - | - | Removed upstream | Auto-remove (user did not customize) |
   | Y | Y | N | N | - | - | **Conflict** | Ask user (see removal conflict below) |
   | Y | N | Y | - | - | - | User removed | Keep removed (user intentionally deleted) |
   | Y | N | N | - | - | - | Both removed | Already gone |
   | N | Y | N | - | - | - | User added | Keep USER |
   | N | Y | Y | - | - | Y | Both added same | Keep USER |
   | N | Y | Y | - | - | N | **Conflict** | Ask user (both added differently) |

   **Resolve conflicts** -- for each conflict, present one at a time via AskUserQuestion:

   *Standard conflict* (both sides changed the same section differently):
   - header: "Merge Conflict"
   - question: "Section '{heading}' in {filename} was changed both by you and in the plugin update.\n\nYour version:\n---\n{first 10 lines of USER section, or full section if <= 10 lines}\n{if truncated: '... ({N} more lines)'}\n---\n\nPlugin version:\n---\n{first 10 lines of NEW section, or full section if <= 10 lines}\n{if truncated: '... ({N} more lines)'}\n---"
   - options:
     - { label: "Keep mine", description: "Preserve your customized version of this section" }
     - { label: "Take plugin update", description: "Replace with the new plugin version of this section" }
     - { label: "Type something else", description: "Provide a custom resolution for this section" }
     - { label: "Chat about this", description: "See full content and discuss the differences" }

   *Removal conflict* (user customized a section that upstream removed):
   - header: "Merge Conflict"
   - question: "Section '{heading}' in {filename} was removed in the plugin update, but you have customized it.\n\nYour version:\n---\n{first 10 lines of USER section, or full section if <= 10 lines}\n{if truncated: '... ({N} more lines)'}\n---"
   - options:
     - { label: "Remove it", description: "Remove this section (matches the plugin update)" }
     - { label: "Keep mine", description: "Preserve your customized version of this section" }
     - { label: "Chat about this", description: "Discuss why this section was removed" }

   **Assemble the merged output** using this ordering:
   1. Preamble always first
   2. Sections present in NEW define the canonical order
   3. User-added sections (in USER but not in NEW or BASE) appended after the last NEW section, preserving their relative order from USER
   4. Removed sections omitted

   **After merge for this file:**
   1. Write the merged result to `.doc-writer/{file}`
   2. Write the NEW content (not the merged content) to `.doc-writer/.originals/{file}` -- the `.originals/` directory always tracks what the plugin shipped, not the user's merged version
   3. Record merge stats: "{N} sections auto-merged, {M} conflicts resolved by user"

### Step 3.5: Q&A Gap Detection

Detect whether the plugin has added new framework Q&A questions since the user last ran setup. Only ask questions whose answers are not already stored.

1. Read the `doc_system` value from config.yaml (already read in Step 1).

2. Check if `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.qa.md` exists.

   **If the file does not exist:** This is a FALLBACK framework (researcher-generated, not built-in). Q&A gap detection only applies to built-in frameworks with plugin-shipped Q&A files. Record for summary: "Q&A gap detection skipped -- {doc_system} is not a built-in framework." Skip to Step 4.

3. Read the `.qa.md` file. Parse each `## Question N:` section (ignore `### Follow-on:` sub-sections -- follow-on questions are tied to their parent question's answer and were handled during the original setup session). Extract the `header` field from each question.

4. For each question header, derive the expected `qa_answers` key: lowercase the header and replace spaces with underscores (e.g., "API docs" becomes `api_docs`, "Navigation" becomes `navigation`). This MUST match the setup skill's derivation rule exactly (setup SKILL.md Step 2b.5 item 4).

5. Read the `qa_answers` section from the user's config.yaml.

6. For each derived key: check if the key exists in `qa_answers`.
   - If the key exists: this question was already answered. Skip it.
   - If the key is absent: this is a new question. Add to the list of questions to ask.

7. **If no new questions found:** Record "No new Q&A questions" for summary. Skip to Step 4.

8. **If new questions found:**

   a. Display: "The plugin update includes {N} new framework question(s) for {doc_system}."

   b. If a framework config file exists (e.g., `mkdocs.yml`, `conf.py` -- detected in Step 1 or detected now via Glob), use Grep on it to detect which features are currently enabled. Match detected features against the `recommend_if` fields in the Q&A options and mark matching options as "(Recommended)". This mirrors setup Step 2b.5 behavior.

   c. For each new question, present it via AskUserQuestion:
      - Use the `header`, `question`, and `options` fields from the `.qa.md` question section.
      - If the question has `multiSelect: true`, set multiSelect on the AskUserQuestion.
      - If the question has `detect_context` and features were detected, include the detected values in the question text.
      - Every question MUST have "Type something else" and "Chat about this" as trailing options (the .qa.md files already include them).

   d. After all new questions are answered, persist the new answers to config.yaml under `qa_answers` using the derived key for each answer. Store the selected label as the value (string for single-select, array of strings for multi-select). For "Type something else" responses, store the user's freeform text. **Write config.yaml NOW** -- the researcher re-run in Step 4 reads config.yaml and must see the new answers.

   e. Record for summary: "Asked {N} new Q&A question(s): {list of question headers}"

### Step 4: Context Refresh

Regenerate `context.md` if the upgrade produced changes that downstream agents should reflect.

1. Determine if a context refresh is needed:
   - Did Step 2 add any new config fields? (If yes, refresh needed.)
   - Did Step 3.5 collect any new Q&A answers? (If yes, refresh needed.)

2. **If no refresh needed:** Record "Context refresh skipped -- no config or Q&A changes" for summary. Skip to Step 5.

3. **If refresh needed:**

   a. Display: "Refreshing context.md to reflect updated configuration..."

   b. Use the Agent tool to spawn `doc-researcher` with this message:

   > Enrich the project configuration. Read `.doc-writer/config.yaml` for user personas, tone, and doc system. Scan the codebase (README, source files, framework config) and produce `.doc-writer/context.md` with expanded persona guidance, project domain summary, tone-specific writing rules, and framework usage preferences.
   >
   > Framework Q&A answers: {all qa_answers from config.yaml, including both existing and newly added answers}

   c. After the researcher completes, record for summary: "context.md regenerated via researcher re-run"

### Step 5: Finalize

Update the stored plugin version and present the upgrade summary.

1. Write the new `plugin_version` value to config.yaml, replacing the old value (or adding it if it was absent). The new value is the `version` from plugin.json (read in Step 1). This is the **LAST** write to config.yaml -- all migration changes from Step 2 and Q&A answer persistence from Step 3.5 must already be written.

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
- {list each customized file that was merged (see File Merges below)}
- {list each file skipped (FALLBACK framework, not a plugin-shipped file)}
- {or "No file updates"}

### File Merges
- {list each file merged: "{file}: {N} sections auto-merged, {M} conflicts resolved by user"}
- {or "No merges needed" / "2-way diff bootstrap completed -- .originals/ created"}

### Q&A Updates
- {list each new question asked with the answer given}
- {or "No new Q&A questions"}
- {or "Q&A gap detection skipped -- {doc_system} is not a built-in framework"}

### Context Refresh
- {context.md regenerated via researcher re-run}
- {or "Skipped -- no config or Q&A changes to reflect"}

### Warnings
- {any warnings from above steps, e.g., missing plugin_version}
- {or "None"}
```

## Notes

- All plugin-internal file references use `${CLAUDE_PLUGIN_ROOT}` for portability across different installation locations.
- Config schema uses `user_personas:` as an array -- even for a single persona.
- The upgrade command delivers the complete upgrade flow: version detection, config migration, file merge, Q&A gap detection, context refresh, and summary.
- When inferring config field values, read the user's existing configuration holistically. The goal is to produce values that feel like the user configured them during setup, not mechanical defaults.
