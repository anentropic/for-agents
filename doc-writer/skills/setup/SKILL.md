---
name: doc-writer:setup
description: Configure doc-writer for this project. Creates .doc-writer/ directory with config, rules, and guidance files.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
argument-hint: "[--reset] [--refresh-context]"
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

2. **If `$ARGUMENTS` contains `--refresh-context`:**
   - Verify `.doc-writer/config.yaml` exists. If it does not, tell the user: "No configuration found. Run `/doc-writer:setup` first to configure audiences, doc system, and paths." Stop.
   - Skip all Q&A. Jump directly to Step 5 (Context Enrichment) to re-run the researcher.
   - Stop after Step 5 completes.

3. **If `$ARGUMENTS` contains `--reset`:**
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

4. **If `.doc-writer/config.yaml` exists (and no flags):**
   - Read the existing config file.
   - Display it formatted nicely:
     ```
     ## Current Configuration

     **Audiences:**
     1. [name] (skill_level)
        - Assumed knowledge: [list]
        - Never assume: [list]
        - User tasks: [list or "none"]

     **Tone:** {tone or "not set"}
     **Doc system:** [doc_system]
     **Docs root:** [paths.docs_root]
     **Source root:** [paths.source_root]
     ```
   - Use AskUserQuestion:
     - header: "Update"
     - question: "What would you like to update in your doc-writer configuration?"
     - options:
       - { label: "Audiences", description: "Edit, add, or remove target audiences" }
       - { label: "Tone", description: "Change documentation writing tone (currently: {tone})" }
       - { label: "Doc system", description: "Change documentation system (currently: {doc_system})" }
       - { label: "Paths", description: "Change docs root or source root directories" }
       - { label: "Re-run researcher", description: "Regenerate context.md from current config" }
       - { label: "Done", description: "Finish updating configuration" }
       - { label: "Type something else", description: "Describe a different change" }
       - { label: "Chat about this", description: "Discuss configuration options" }
   - **"Audiences":** Jump to Step 4 audiences handling.
   - **"Tone":** Jump to Step 2a.5 (Tone Selection). After tone is updated, write updated config and return to re-run menu.
   - **"Doc system":** Jump to Step 4 doc system handling.
   - **"Paths":** Jump to Step 4 paths handling.
   - **"Re-run researcher":** Jump to Step 5 (Context Enrichment). After researcher completes, return to re-run menu.
   - **"Done":** Stop. Display current config summary.
   - **"Type something else":** Ask in plain text what the user wants to change. This covers `rules` and `guidance file` which are file-edit instructions, plus any other custom request.
   - **"Chat about this":** Explain what each section controls. After discussion, re-present the question.

5. **If `.doc-writer/config.yaml` does NOT exist:**
   - Proceed to Step 2 (Full Q&A Flow).

### Step 2: Full Q&A Flow (First-Time Setup)

Run through these questions interactively. Wait for user response after each question before proceeding to the next.

#### 2a: Audience Definition

Ask the user to define their primary audience. Each field is collected individually using infer+suggest AskUserQuestion interactions, except where noted as freeform.

**Audience name** -- freeform (too specific to infer):

Ask the user in plain text:
"Who is the primary audience for this library's documentation? Describe them in a short phrase (e.g., 'Python developers building REST APIs', 'DevOps engineers managing Kubernetes clusters')."

**Skill level** -- infer+suggest AskUserQuestion:

Using the Project Detection Results and README content, infer 2-3 likely skill levels. Mark the most likely as Recommended.

Use AskUserQuestion:
- header: "Skill level"
- question: "What skill level should docs target for {audience_name}?"
- options:
  - { label: "{inferred level} (Recommended)", description: "{why this fits based on project signals}" }
  - { label: "{alternative level}", description: "{brief description}" }
  - { label: "{alternative level}", description: "{brief description}" }
  - { label: "Type something else", description: "Describe a different skill level" }
  - { label: "Chat about this", description: "Discuss what skill levels mean for docs" }

Example inference logic:
- README mentions "getting started" prominently, uses simple examples -> suggest Intermediate (Recommended)
- Heavy type hints, abstract patterns, no tutorial content -> suggest Advanced (Recommended)
- Explicit "for beginners" in README or package description -> suggest Beginner (Recommended)

**Assumed knowledge** -- infer+suggest multiSelect AskUserQuestion:

Using dependencies, README, and code patterns, infer 3-5 knowledge areas the audience likely has. All pre-selected by default.

Use AskUserQuestion:
- header: "Assumed"
- question: "What can {audience_name} be assumed to already know? Deselect items they might NOT know."
- multiSelect: true
- options:
  - { label: "{knowledge area 1} (Recommended)", description: "{specific description}" }
  - { label: "{knowledge area 2}", description: "{specific description}" }
  - { label: "{knowledge area 3}", description: "{specific description}" }
  - { label: "{knowledge area 4}", description: "{specific description}" }
  - { label: "Type something else", description: "Add a different knowledge area" }
  - { label: "Chat about this", description: "Discuss assumed knowledge" }

Example inference logic:
- Python project with requests dependency -> "HTTP/REST APIs" as assumed knowledge
- TypeScript project -> "TypeScript basics" and "npm/Node.js" as assumed knowledge
- Has CLI entrypoint -> "Command-line usage" as assumed knowledge
- Uses async/await patterns -> "Async programming" as assumed knowledge

**Never assume** -- infer+suggest multiSelect AskUserQuestion:

Infer 3-5 topics that should always be explained, based on project complexity and common confusion points.

Use AskUserQuestion:
- header: "Explain"
- question: "What must ALWAYS be explained for {audience_name}? These topics will never be assumed as prior knowledge."
- multiSelect: true
- options:
  - { label: "{topic 1} (Recommended)", description: "{why this needs explanation}" }
  - { label: "{topic 2}", description: "{why this needs explanation}" }
  - { label: "{topic 3}", description: "{why this needs explanation}" }
  - { label: "Type something else", description: "Add a different topic" }
  - { label: "Chat about this", description: "Discuss what needs explanation" }

Example inference logic:
- Library has custom config format -> "Configuration syntax" as never-assume
- Library uses non-standard patterns -> those patterns as never-assume
- Library has specific terminology -> that terminology as never-assume

**Domain context** -- infer+suggest AskUserQuestion:

Using README and package description, infer 2-4 domain context options.

Use AskUserQuestion:
- header: "Domain"
- question: "What problem domain does {audience_name} work in?"
- options:
  - { label: "{inferred domain 1} (Recommended)", description: "{expanded description}" }
  - { label: "{inferred domain 2}", description: "{expanded description}" }
  - { label: "Type something else", description: "Describe a different domain" }
  - { label: "Chat about this", description: "Discuss domain context" }

**User persona tasks** -- infer+suggest multiSelect AskUserQuestion:

Using the codebase scan (public API surface, README examples, test patterns), infer 3-5 common tasks users perform with this library.

Use AskUserQuestion:
- header: "Tasks"
- question: "What tasks does {audience_name} typically perform with this library? These inform User Persona scenario generation."
- multiSelect: true
- options:
  - { label: "{task 1}", description: "{brief context}" }
  - { label: "{task 2}", description: "{brief context}" }
  - { label: "{task 3}", description: "{brief context}" }
  - { label: "{task 4}", description: "{brief context}" }
  - { label: "Type something else", description: "Add a different task" }
  - { label: "Chat about this", description: "Discuss common user tasks" }

Example inference logic:
- Rate-limiting library -> "Set up rate limiting", "Configure per-route limits", "Handle 429 responses", "Monitor rate limit usage"
- HTTP client library -> "Make API requests", "Handle authentication", "Configure retries", "Process response data"

**Discovery story** -- freeform (too specific to infer):

Ask the user in plain text:
"How would a typical {audience_name} discover this library? (e.g., 'searching for a Python HTTP client that handles retries', 'recommended by a colleague for rate limiting'). This helps the User Persona generate realistic scenarios. Press Enter to skip."

**Adding more audiences:**

After completing all fields for the primary audience, use AskUserQuestion:
- header: "Audiences"
- question: "Do you have a secondary audience? (e.g., contributors vs. end users)"
- options:
  - { label: "Add audience", description: "Define another target audience" }
  - { label: "No, continue", description: "Move on to tone selection" }
  - { label: "Type something else", description: "Describe your audience setup differently" }
  - { label: "Chat about this", description: "Discuss audience configuration" }

- **"Add audience":** Repeat the audience definition questions (name, skill level, assumed knowledge, never assume, domain context, user tasks, discovery story) using the same infer+suggest pattern. After collecting answers, ask again if there are more audiences.
- **"No, continue":** Proceed to Step 2a.5 (Tone Selection).
- **"Type something else":** Ask in plain text. User may want to modify the primary audience just defined or describe a non-standard setup.
- **"Chat about this":** Explain how multiple audiences affect the pipeline (separate Persona agents per audience, independent verdicts). After discussion, re-present the question.

Continue offering additional audiences until the user selects "No, continue" or indicates they are done.

Store all audiences in an array -- even if only one audience is configured, it must be stored as a single-element array.

#### 2a.5: Tone Selection

After audience definition is complete (all audiences collected), present tone selection.

Use AskUserQuestion:
- header: "Tone"
- question: "What writing tone should the documentation use?"
- options:
  - { label: "Just the facts", description: "Minimal, no preamble, direct definitions, one example max" }
  - { label: "Helpful and comprehensive, warm but businesslike", description: "Clear explanations, multiple examples, structured and approachable" }
  - { label: "Helpful and comprehensive, with personality and occasional humour", description: "Same depth, but with personality and occasional humour" }
  - { label: "Type something else", description: "Describe a different tone" }
  - { label: "Chat about this", description: "See examples of each tone style" }

- **"Just the facts":** Record tone as "just-the-facts"
- **"Helpful and comprehensive, warm but businesslike":** Record tone as "warm-businesslike"
- **"Helpful and comprehensive, with personality and occasional humour":** Record tone as "personality"
- **"Type something else":** Ask in plain text what tone they want. Record their description as a custom tone label.
- **"Chat about this":** Show example paragraphs in each tone for the same concept. After discussion, re-present the question.

#### 2b: Doc System Selection

Present the detected doc system from the Project Detection Results above as the default. Use AskUserQuestion:
- header: "Doc system"
- question: "Which documentation system does this project use? Detected: {detected_system}"
- options:
  - { label: "mkdocs-material", description: "MkDocs with Material theme" }
  - { label: "plain-markdown", description: "Standard Markdown, no doc framework" }
  - { label: "sphinx-shibuya", description: "Sphinx with Shibuya theme" }
  - { label: "odoc", description: "OCaml documentation via odoc" }
  - { label: "Type something else", description: "Enter a custom doc system name" }
  - { label: "Chat about this", description: "Discuss doc system options" }

- **"mkdocs-material":** Record selection.
- **"plain-markdown":** Record selection.
- **"sphinx-shibuya":** Record selection.
- **"odoc":** Record selection.
- **"Type something else":** Ask in plain text for the doc system name. Then:
  1. Normalize the name to lowercase-hyphenated form (e.g., "Docusaurus" -> "docusaurus", "VitePress" -> "vitepress").
  2. Check if `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{name}.md` exists using Glob:
     - **If YES:** Record as doc_system. Set `framework_root` = `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults`. Proceed to Step 2b.3 (Scaffold Check).
     - **If NO:** Inform the user: "No built-in support for '{name}' yet. I'll research this framework and generate guidance. This will take a moment."
       Use the Agent tool to spawn `doc-researcher` with this message:
       > Research the documentation framework '{name}'. Generate guidance, Q&A question set, and scaffold template files into the plugin defaults directory. Read the existing mkdocs-material.md and mkdocs-material.qa.md files in ${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/ as reference for the file structure and format.
       After researcher completes, check the response for a `FALLBACK:` prefix:
       - **If FALLBACK detected:** Set `framework_root` = `.doc-writer` (project-local). The researcher wrote files to `.doc-writer/{name}.md`, `.doc-writer/{name}.qa.md`, and optionally `.doc-writer/scaffolds/{name}.{ext}` instead of the plugin defaults directory. All subsequent file lookups in Step 2b.3 and Step 2b.5 MUST use `framework_root` instead of `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults`.
       - **If no FALLBACK:** Set `framework_root` = `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults`.
       Record as doc_system. Proceed to Step 2b.3 (Scaffold Check).
- **"Chat about this":** Explain what each doc system means for formatting output. After discussion, re-present the question.

For built-in frameworks (mkdocs-material, plain-markdown, sphinx-shibuya, odoc) selected from the standard options (not "Type something else"), set `framework_root` = `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults`.

#### 2b.3: Scaffold Check

After doc system selection, check whether the project already has a framework config file.

1. **Determine what to look for:**
   - Read `{framework_root}/{doc_system}.qa.md` if it exists.
   - If the .qa.md file has a `## Detection` section with `Config file: {filename}`, use that filename.
   - If no .qa.md file exists or Config file is "none", skip scaffold check entirely and proceed to Step 2b.5.

2. **Check for existing framework config:**
   - Use Glob to check if `{config_filename}` exists in the project root (e.g., `mkdocs.yml` for mkdocs-material).

3. **If config file NOT found (full scaffold mode):**
   - Check if `{framework_root}/scaffolds/{doc_system}.yml` (or `.js`, `.yaml`, `.toml`, `.py` variants) exists. Also check if `{framework_root}/scaffolds/{doc_system}/` directory exists (for multi-file scaffolds like odoc).
   - **If scaffold template exists:**
     a. Read the scaffold template.
     For directory scaffolds (`scaffolds/{doc_system}/` exists): read each template file in the directory. Process template variable substitution on each file. The scaffold directory contains files that map to project locations (e.g., `doc_dune.sexp` -> `doc/dune`, `index.mld` -> `doc/index.mld`). For multi-library projects (detected from Q1), also instantiate secondary templates (`secondary_dune.sexp`, `secondary_index.mld`) for each non-primary package.
     b. Infer `site_name` from the project's package manifest (pyproject.toml `name` field, package.json `name` field, Cargo.toml `[package] name`, or README.md first heading). If not found, ask the user in plain text: "What is the project name for the documentation site?"
     c. Infer `site_description` from the package manifest `description` field. If not found, ask the user in plain text: "One-sentence description for the documentation site:"
     d. Replace `{site_name}` and `{site_description}` template variables in the scaffold content.
     e. Write the generated config file to the project root (e.g., `mkdocs.yml`).
     f. Check if `{paths.docs_root}` directory exists. If not, create it with a starter `index.md`:
        ```markdown
        # {site_name}

        Welcome to the {site_name} documentation.
        ```
     g. Surface install commands as informational text. Do NOT execute them:
        ```
        ## Install

        To serve your documentation locally, install the framework:

        mkdocs-material: `pip install mkdocs-material`

        This command is shown for your reference -- run it manually when ready.
        ```
        For other frameworks, infer the appropriate install command from the researcher's knowledge or the framework's conventions.
   - **If no scaffold template exists:** Inform the user: "No scaffold template for '{doc_system}'. You'll need to create the config file manually." Proceed to Step 2b.5.

4. **If config file FOUND (diff-against-defaults mode):**
   - Read the existing config file from the project root.
   - Check if `{framework_root}/scaffolds/{doc_system}.yml` (or `.js`, `.yaml`, `.toml`, `.py` variants) exists. Also check if `{framework_root}/scaffolds/{doc_system}/` directory exists (for multi-file scaffolds like odoc).
   - **If scaffold template exists:**
     a. Read the scaffold template (opinionated defaults).
     For directory scaffolds (`scaffolds/{doc_system}/` exists): read each template file in the directory. Compare each template against the corresponding project file to identify missing features or stanzas. Present gaps as a combined list across all template files.
     b. Compare: identify features, extensions, and plugins in the scaffold template that are ABSENT from the existing config. Use Grep on the existing config to check for each feature listed in the scaffold.
     c. If gaps found, present as AskUserQuestion:
        - header: "Extras"
        - question: "Your {config_filename} is missing these recommended features. Enable any?"
        - multiSelect: true
        - options: (one per missing feature, using feature name and brief description)
          - Plus: { label: "None", description: "Keep current config as-is" }
          - Plus: { label: "Type something else", description: "Describe other changes" }
          - Plus: { label: "Chat about this", description: "Learn what each feature does" }
     d. For each selected feature: show the exact config YAML that will be added. Use AskUserQuestion to confirm:
        - header: "Confirm"
        - question: "Add this to {config_filename}?"
        - Display the proposed addition as a code block.
        - options:
          - { label: "Add it", description: "Append to existing config" }
          - { label: "Skip", description: "Don't add this feature" }
          - { label: "Chat about this", description: "Discuss this change" }
     e. For confirmed additions: Read the existing config file, append the new config blocks, and Write the complete updated file. Never overwrite existing config -- only append.
     f. If "None" selected: proceed without changes.
   - **If no scaffold template exists:** No diff possible. Proceed to Step 2b.5.

#### 2b.5: Framework Configuration

After scaffold check, present framework-specific questions. These are read dynamically from Q&A data files.

1. **Check for Q&A data file:**
   - Use Glob to check if `{framework_root}/{doc_system}.qa.md` exists.
   - **If found:** Read the file. Parse the `## Question N:` sections.
   - **If NOT found:** Skip framework Q&A. Proceed to Step 2c (Paths).

2. **If config file exists (detected in Step 2b.3):** Use Grep on the config file to detect which features are currently enabled. Match detected features against the `recommend_if` fields in the Q&A options. Mark matching options as "(Recommended)" and pre-select them for multiSelect questions. Show detected features in the `detect_context` field.

3. **Present each question from the .qa.md file as an AskUserQuestion:**
   - Use the `header`, `question`, and `options` fields from each `## Question` section.
   - If the question has `multiSelect: true`, set multiSelect on the AskUserQuestion.
   - If the question has `detect_context` and features were detected, include the detected values in the question text.
   - Every question MUST have "Type something else" and "Chat about this" as trailing options (the .qa.md files already include them).

4. **Record all answers.** Framework Q&A answers do NOT go into config.yaml. Store them in-memory and pass them to the researcher via the Agent tool invocation message in Step 5.

**Passing framework answers to the researcher:**

This is unchanged from the current behavior. Framework Q&A answers are passed to the researcher in the Agent tool invocation message in Step 5.

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

2. **Write `.doc-writer/config.yaml`** -- Read the config template from `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/config-template.yaml` and populate it with the Q&A answers. The config MUST use `audiences:` as an array, even for a single audience. Include the `detected:` section with auto-detection results from the Project Detection Results above. The config MUST include `tone: "{selected_tone}"` as a top-level field. Each audience entry MUST include `user_tasks: [{selected_tasks}]`.

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
   - config.yaml -- [N] audience(s), tone: {tone}, doc system: [system], paths configured
   - [doc_system].md -- Documentation system guidance (editable)
   - rules.md -- Project-specific rules template (editable)

   Running researcher to generate context.md...
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

- **`tone`** (from "Tone" selection above): Present the tone selection AskUserQuestion (same as Step 2a.5). Write updated config preserving all other fields.

- **`doc system`**: Show current doc system. Present selection options (same as Step 2b). If changed, copy new guidance file to `.doc-writer/`. Note: the old guidance file remains in `.doc-writer/` -- user can delete it manually if desired. If the new doc system triggers the unknown framework researcher flow, wait for it to complete and check for FALLBACK prefix to set framework_root. Then run Step 2b.3 (Scaffold Check) for the new framework.

- **`paths`**: Show current paths. Ask for new values. Write updated config preserving all other fields.

- **`researcher`** (from "Re-run researcher" selection above): Jump to Step 5 (Context Enrichment). Return to the re-run menu after completion.

- **`rules`**: Inform the user: "Rules are in `.doc-writer/rules.md`. Edit that file directly -- it's freeform markdown that agents interpret." Open or display the file path.

- **`guidance file`**: Inform the user: "Guidance is in `.doc-writer/{doc_system}.md`. Edit that file directly -- it contains documentation system preferences." Open or display the file path.

- **`done`**: Stop. Display current config summary.

After any update, ask if the user wants to update anything else, or if they are done.

### Step 5: Context Enrichment

After file creation (Step 3) completes, or when triggered by --refresh-context or "Re-run researcher":

Use the Agent tool to spawn `doc-researcher` with this message:

> Enrich the project configuration. Read `.doc-writer/config.yaml` for audiences, tone, and doc system. Scan the codebase (README, source files, framework config) and produce `.doc-writer/context.md` with expanded audience guidance, project domain summary, tone-specific writing rules, and framework usage preferences.
>
> Framework Q&A answers: {framework_answers or "none -- use defaults from framework config detection"}

After the researcher completes, display the updated confirmation:
```
   - context.md -- Expanded context for downstream agents (editable)
```

Both first-time setup and --reset flows end at Step 5. The --refresh-context flow jumps directly to Step 5 and stops after.

## Notes

- All plugin-internal file references use `${CLAUDE_PLUGIN_ROOT}` for portability across different installation locations.
- The detection script runs automatically via `!`bash`` dynamic context injection when this skill is loaded.
- Config schema uses `audiences:` (plural, array) -- never `audience:` (singular).
- Guidance files are opinionated preferences, not syntax references. Agents already understand doc system syntax.
- Rules in `.doc-writer/rules.md` are additive to universal quality rules -- they extend but cannot override the baseline.
- `tone` field in config.yaml stores a label; expanded writing rules live in `.doc-writer/context.md`.
- `user_tasks` on each audience entry stores the user's selections; expanded task descriptions live in `context.md`.
- The researcher agent is spawned at the end of every setup flow (first-time, --reset, --refresh-context) to ensure context.md is always current.
