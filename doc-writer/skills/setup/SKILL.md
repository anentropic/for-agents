---
name: setup
description: Configure doc-writer for this project. Creates .doc-writer/ directory with config, rules, and guidance files.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: "[--reset]"
---

# Doc Writer Setup

Configure the doc-writer plugin for this project. Creates a `.doc-writer/` directory containing project configuration, documentation rules, and doc-system guidance.

## Project Detection Results

!`bash ${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/detect-project.sh`

## Instructions

Follow these steps in order. Read each section carefully before acting.

### Step 1: Re-Run Detection

First, check whether this project already has a doc-writer configuration:

1. Use Glob to check if `.doc-writer/config.yaml` exists.

2. **If `$ARGUMENTS` contains `--reset`:**
   - Warn the user: "This will overwrite your existing doc-writer configuration. Guidance files and rules in `.doc-writer/` will be replaced with defaults. Continue? (yes/no)"
   - If user confirms, proceed to Step 2 (Full Q&A Flow) below.
   - If user declines, stop.

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
   - Ask: "What would you like to update?"
   - Options: `audiences`, `doc system`, `paths`, `rules`, `guidance file`, or `done`
   - Jump to Step 4 (Re-Run Update Flow) below.

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

After the user provides primary audience details, ask:

```
Do you have a secondary audience? (e.g., contributors vs. end users)
If yes, I'll ask the same questions for the next audience.
If no, we'll move on to doc system selection.
```

If yes, repeat the audience questions. Continue offering additional audiences until the user says no or indicates they are done.

Store all audiences in an array — even if only one audience is configured, it must be stored as a single-element array.

#### 2b: Doc System Selection

Present the detected doc system from the Project Detection Results above as the default:

```
## Doc System

Detected: [detected doc system from auto-detection, or "plain-markdown" if none detected]

Which documentation system does this project use?
1. mkdocs-material (MkDocs with Material theme)
2. plain-markdown (standard Markdown, no doc framework)
3. custom — enter a name (you will need to create .doc-writer/{name}.md guidance file)

Press Enter to accept the detected default, or select an option.
```

Record the user's selection.

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

- **`audiences`**: Show current audiences. Ask: "Do you want to edit an existing audience, add a new one, or remove one?" Handle accordingly. Write updated config preserving all other fields.

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
