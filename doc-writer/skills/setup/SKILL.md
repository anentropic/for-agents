---
name: doc-writer:setup
description: Configure doc-writer for this project. Creates .doc-writer/ directory with config, rules, and guidance files.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: "[--reset]"
---

# Doc Writer Setup

Configure the doc-writer plugin for this project. Creates a `.doc-writer/` directory containing project configuration, documentation rules, and doc-system guidance.

## User Interaction Pattern

This skill uses AskUserQuestion for structured choices. When the user selects:
- **"Type something else"** or **"Other"**: Ask your follow-up as plain text. Wait for their response. Then resume the workflow.
- **"Chat about this"**: Explain the current decision in depth. Open a plain-text dialogue. After it resolves, re-present the original question or proceed based on what was discussed.

Never respond to these selections with another AskUserQuestion.

## Project Detection Results

!`bash ${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/detect-project.sh`

## Instructions

Follow these steps in order. Read each section carefully before acting.

### Step 1: Re-Run Detection

First, check whether this project already has a doc-writer configuration:

1. Use Glob to check if `.doc-writer/config.yaml` exists.

2. **If `$ARGUMENTS` contains `--reset`:**
   - Use AskUserQuestion to confirm:
     - header: "Reset"
     - question: "This will overwrite your existing doc-writer configuration. Guidance files and rules will be replaced with defaults."
     - options:
       - { label: "Reset config", description: "Overwrite existing configuration with fresh defaults" }
       - { label: "Keep current", description: "Cancel and keep existing configuration" }
       - { label: "Type something else", description: "Specify what to reset" }
       - { label: "Chat about this", description: "Discuss what will be overwritten" }
   - **"Reset config":** Proceed to Step 2 (Full Q&A Flow).
   - **"Keep current":** Stop.
   - **"Type something else":** Ask in plain text what the user wants to reset selectively. Handle accordingly.
   - **"Chat about this":** Explain which files exist and what will be overwritten. After discussion, re-present the question.

3. **If `.doc-writer/config.yaml` exists (and no `--reset` flag):**
   - Read the existing config file.
   - Display it formatted nicely:
     ```
     ## Current Configuration

     **Audiences:**
     1. [name] (skill_level)
        - Assumed knowledge: [list]
        - Never assume: [list]

     **Doc system:** [doc_system]
     **Docs root:** [paths.docs_root]
     **Source root:** [paths.source_root]
     ```
   - Use AskUserQuestion:
     - header: "Update"
     - question: "What would you like to update in your doc-writer configuration?"
     - options:
       - { label: "Audiences", description: "Edit, add, or remove target audiences" }
       - { label: "Doc system", description: "Change documentation system (currently: {doc_system})" }
       - { label: "Paths", description: "Change docs root or source root directories" }
       - { label: "Done", description: "Finish updating configuration" }
       - { label: "Type something else", description: "Describe a different change" }
       - { label: "Chat about this", description: "Discuss configuration options" }
   - **"Audiences":** Jump to Step 4 audiences handling.
   - **"Doc system":** Jump to Step 4 doc system handling.
   - **"Paths":** Jump to Step 4 paths handling.
   - **"Done":** Stop. Display current config summary.
   - **"Type something else":** Ask in plain text what the user wants to change. This covers `rules` and `guidance file` which are file-edit instructions, plus any other custom request.
   - **"Chat about this":** Explain what each section controls. After discussion, re-present the question.

4. **If `.doc-writer/config.yaml` does NOT exist:**
   - Proceed to Step 2 (Full Q&A Flow).

### Step 2: Full Q&A Flow (First-Time Setup)

Run through these questions interactively. Wait for user response after each question before proceeding to the next.

#### 2a: Audience Definition

Ask the user to define their primary audience:

```
## Audience Definition

Who is the primary audience for this library's documentation?

Please provide:
1. **Name**: A description of who they are (e.g., "Python developers building REST APIs")
2. **Skill level**: beginner, intermediate, or advanced
3. **Assumed knowledge**: What can you assume they already know? (comma-separated list)
4. **Never assume**: What must always be explained, never skipped? (comma-separated list)
5. **Domain context** (optional): What problem domain does this audience work in? (e.g., "building REST APIs for fintech applications")
6. **Discovery story** (optional): How did they discover your library? (e.g., "searching for a Python HTTP client that handles retries")

These optional fields help the User Persona agent generate more realistic testing scenarios. If left blank, the Persona will infer defaults.
```

After the user provides primary audience details, use AskUserQuestion:
- header: "Audiences"
- question: "Do you have a secondary audience? (e.g., contributors vs. end users)"
- options:
  - { label: "Add audience", description: "Define another target audience" }
  - { label: "No, continue", description: "Move on to doc system selection" }
  - { label: "Type something else", description: "Describe your audience setup differently" }
  - { label: "Chat about this", description: "Discuss audience configuration" }

- **"Add audience":** Repeat the audience definition questions (name, skill level, assumed knowledge, never assume, domain context, discovery story) in plain text. After collecting answers, ask again if there are more audiences.
- **"No, continue":** Proceed to Step 2b (Doc System Selection).
- **"Type something else":** Ask in plain text. User may want to modify the primary audience just defined or describe a non-standard setup.
- **"Chat about this":** Explain how multiple audiences affect the pipeline (separate Persona agents per audience, independent verdicts). After discussion, re-present the question.

Continue offering additional audiences until the user selects "No, continue" or indicates they are done.

Store all audiences in an array — even if only one audience is configured, it must be stored as a single-element array.

#### 2b: Doc System Selection

Present the detected doc system from the Project Detection Results above as the default. Use AskUserQuestion:
- header: "Doc system"
- question: "Which documentation system does this project use? Detected: {detected_system}"
- options:
  - { label: "mkdocs-material", description: "MkDocs with Material theme" }
  - { label: "plain-markdown", description: "Standard Markdown, no doc framework" }
  - { label: "Type something else", description: "Enter a custom doc system name" }
  - { label: "Chat about this", description: "Discuss doc system options" }

- **"mkdocs-material":** Record selection.
- **"plain-markdown":** Record selection.
- **"Type something else":** Ask in plain text for the custom doc system name. Inform the user they will need to create `.doc-writer/{name}.md` with their doc system preferences.
- **"Chat about this":** Explain what each doc system means for formatting output. After discussion, re-present the question.

#### 2c: Paths

Ask for documentation paths:

```
## Paths

Where should documentation be written?
- **Docs root** (default: docs/): [detected docs directory or "docs/"]
- **Source root** (default: src/): [detected source directory or "src/"]

Press Enter to accept defaults, or provide custom paths.
```

### Step 3: File Creation

After Q&A completes, create the project configuration:

1. **Create `.doc-writer/` directory** if it does not exist.

2. **Write `.doc-writer/config.yaml`** — Read the config template from `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/config-template.yaml` and populate it with the Q&A answers. The config MUST use `audiences:` as an array, even for a single audience. Include the `detected:` section with auto-detection results from the Project Detection Results above.

3. **Copy the selected guidance file:**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.md`
   - Write its contents to `.doc-writer/{doc_system}.md`
   - If the file does not exist (custom doc system name), inform the user:
     "No built-in guidance file for '{doc_system}'. Create `.doc-writer/{doc_system}.md` with your documentation system preferences."

4. **Copy the default rules file:**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/rules.md`
   - Write its contents to `.doc-writer/rules.md`

5. **Display confirmation:**
   ```
   ## Setup Complete

   Created `.doc-writer/` with:
   - config.yaml — [N] audience(s), doc system: [system], paths configured
   - [doc_system].md — Documentation system guidance (editable)
   - rules.md — Project-specific rules template (editable)

   Next steps:
   - Edit `.doc-writer/rules.md` to add project-specific documentation rules
   - Edit `.doc-writer/[doc_system].md` to customize documentation system preferences
   - Run `/doc-writer:setup` again to update configuration
   ```

### Step 4: Re-Run Update Flow

This section handles field-by-field editing when an existing config is detected.

Based on user selection from Step 1:

- **`audiences`** (from "Audiences" selection above): Show current audiences. Use AskUserQuestion:
  - header: "Audiences"
  - question: "What would you like to do with your audience configuration?"
  - options:
    - { label: "Edit audience", description: "Modify an existing audience's settings" }
    - { label: "Add audience", description: "Define a new target audience" }
    - { label: "Remove audience", description: "Delete an existing audience" }
    - { label: "Type something else", description: "Describe a different audience change" }
    - { label: "Chat about this", description: "Discuss audience configuration" }
  - Handle each selection with plain-text follow-ups as needed (which audience to edit/remove, new audience details).
  - Write updated config preserving all other fields.

- **`doc system`**: Show current doc system. Present selection options (same as Step 2b). If changed, copy new guidance file to `.doc-writer/`. Note: the old guidance file remains in `.doc-writer/` — user can delete it manually if desired.

- **`paths`**: Show current paths. Ask for new values. Write updated config preserving all other fields.

- **`rules`**: Inform the user: "Rules are in `.doc-writer/rules.md`. Edit that file directly — it's freeform markdown that agents interpret." Open or display the file path.

- **`guidance file`**: Inform the user: "Guidance is in `.doc-writer/{doc_system}.md`. Edit that file directly — it contains documentation system preferences." Open or display the file path.

- **`done`**: Stop. Display current config summary.

After any update, ask if the user wants to update anything else, or if they are done.

## Notes

- All plugin-internal file references use `${CLAUDE_PLUGIN_ROOT}` for portability across different installation locations.
- The detection script runs automatically via `!`bash`` dynamic context injection when this skill is loaded.
- Config schema uses `audiences:` (plural, array) — never `audience:` (singular).
- Guidance files are opinionated preferences, not syntax references. Agents already understand doc system syntax.
- Rules in `.doc-writer/rules.md` are additive to universal quality rules — they extend but cannot override the baseline.
