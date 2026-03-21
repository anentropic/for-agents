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
   - Verify `.doc-writer/config.yaml` exists. If it does not, tell the user: "No configuration found. Run `/doc-writer:setup` first to configure user personas, doc system, and paths." Stop.
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

     **User Personas:**
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
       - { label: "User Personas", description: "Edit, add, or remove user personas" }
       - { label: "Tone", description: "Change documentation writing tone (currently: {tone})" }
       - { label: "Doc system", description: "Change documentation system (currently: {doc_system})" }
       - { label: "Paths", description: "Change docs root or source root directories" }
       - { label: "Re-run researcher", description: "Regenerate context.md from current config" }
       - { label: "Done", description: "Finish updating configuration" }
       - { label: "Type something else", description: "Describe a different change" }
       - { label: "Chat about this", description: "Discuss configuration options" }
   - **"User Personas":** Jump to Step 4 persona handling.
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

#### 2a: User Persona Definition

Before asking any questions, display this introduction:

```
## User Personas

Before writing docs, we define who will read them. A **User Persona** captures
your reader's background, skill level, and goals. The pipeline uses it to
calibrate language, generate test scenarios, and validate that docs actually
work for real people.

You can define multiple personas if you have distinct audiences (e.g., end
users vs. contributors). Most projects need just one.
```

**Step 1: Freeform description**

Ask the user in plain text:

"Describe your first user persona -- who are they, what do they already know, and what are they trying to do with this library? Write as much or as little as you want.

Things you might cover (but just write naturally):
- Their role and skill level
- What they can be assumed to already know
- What should always be explained
- What problem domain they work in
- Common tasks they perform with this library
- How they discovered it"

Wait for the user's freeform response.

**Step 2: Extract structured fields**

From the user's freeform response, extract these fields:

- `name`: a short descriptive label for this persona (e.g., "Python developers building REST APIs")
- `skill_level`: beginner, intermediate, advanced, or expert
- `assumed_knowledge`: list of things this persona already knows
- `never_assume`: list of things that must always be explained
- `domain_context`: the problem space they work in
- `user_tasks`: common tasks they perform with this library
- `discovery_story`: how they found the library

For any field the user did not mention, infer a value using the Project Detection Results and README content. Use the same inference logic as the examples below:

Skill level inference:
- README mentions "getting started" prominently, uses simple examples -> Intermediate
- Heavy type hints, abstract patterns, no tutorial content -> Advanced
- Explicit "for beginners" in README or package description -> Beginner

Assumed knowledge inference:
- Python project with requests dependency -> "HTTP/REST APIs"
- TypeScript project -> "TypeScript basics" and "npm/Node.js"
- Has CLI entrypoint -> "Command-line usage"
- Uses async/await patterns -> "Async programming"

Never-assume inference:
- Library has custom config format -> "Configuration syntax"
- Library uses non-standard patterns -> those patterns
- Library has specific terminology -> that terminology

User tasks inference:
- Rate-limiting library -> "Set up rate limiting", "Configure per-route limits", "Handle 429 responses"
- HTTP client library -> "Make API requests", "Handle authentication", "Configure retries"

**Step 3: Confirm the persona**

Present the extracted persona as a formatted summary:

```
### {name}

**Skill level:** {skill_level}
**Assumed knowledge:** {comma-separated list}
**Always explain:** {comma-separated list}
**Domain:** {domain_context}
**Tasks:** {comma-separated list}
**Discovery:** {discovery_story}
```

Use AskUserQuestion:
- header: "Persona"
- question: "Does this capture your user persona?"
- options:
  - { label: "Looks good", description: "Save this persona and continue" }
  - { label: "Edit", description: "Change specific fields" }
  - { label: "Chat about this", description: "Discuss what these fields mean and how they're used" }

- **"Looks good":** Save the persona and continue.
- **"Edit":** Ask in plain text which fields to change. Update accordingly, then re-present the summary.
- **"Chat about this":** Explain how personas flow through the pipeline -- the User Tester agent generates scenarios from `user_tasks` and `discovery_story`, validates docs against `assumed_knowledge` and `never_assume`, and calibrates expectations to `skill_level`. After discussion, re-present the question.

**Step 4: Additional personas**

After confirming the persona, use AskUserQuestion:
- header: "Personas"
- question: "Add another user persona? (e.g., contributors, ops engineers)"
- options:
  - { label: "Add persona", description: "Define another target persona" }
  - { label: "No, continue", description: "Move on to tone selection" }
  - { label: "Chat about this", description: "Discuss when multiple personas are useful" }

- **"Add persona":** Repeat Steps 1-3 for the new persona. After confirming, ask again if there are more.
- **"No, continue":** Proceed to Step 2a.5 (Tone Selection).
- **"Chat about this":** Explain how multiple personas affect the pipeline (separate User Tester agents per persona, independent verdicts). After discussion, re-present the question.

Continue offering additional personas until the user selects "No, continue" or indicates they are done.

Store all user personas in an array -- even if only one persona is configured, it must be stored as a single-element array.

#### 2a.5: Tone Selection

After user persona definition is complete (all personas collected), present tone selection.

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
     b. Identify all template variables in the scaffold content (patterns matching `{variable_name}`).
        Infer values for each using this table:

        | Variable | Primary Source | Fallback Source | Last Resort |
        |----------|---------------|-----------------|-------------|
        | `{site_name}` | Package manifest `name` field (pyproject.toml, package.json, Cargo.toml) | README.md first heading | Ask user: "Project name for the documentation site:" |
        | `{site_description}` | Package manifest `description` field | README.md subtitle or first paragraph | Ask user: "One-sentence description:" |
        | `{project_name}` | Same as `{site_name}` | Same as `{site_name}` | Same as `{site_name}` |
        | `{author_name}` | `git config user.name` | Package manifest author field | Ask user: "Author name:" |
        | `{copyright_year}` | Current year (automatic) | -- | -- |
        | `{github_url}` | `git remote get-url origin` (convert SSH to HTTPS via `sed 's#git@github.com:#https://github.com/#'`) | Package manifest repository URL | Ask user: "GitHub repository URL:" |
        | `{package_name}` | dune-project `(name ...)` sexp or inferred from project structure | Same as `{site_name}` | Ask user: "Package name:" |
        | `{library_name}` | dune-project `(public_name ...)` sexp or library name from Q1 answer | Same as `{package_name}` | Ask user: "Library name:" |
        | `{synopsis}` | Same as `{site_description}` | opam file synopsis field | Ask user: "One-line synopsis:" |

        Variables not in this table: ask the user in plain text for a value.
        Variables with an automatic source (e.g., `{copyright_year}`): never ask -- always use the computed value.

     c. Replace all identified template variables in the scaffold content with their inferred values.
     d. Write the generated config file to the project root (e.g., `mkdocs.yml`).
     e. Check if `{paths.docs_root}` directory exists. If not, create it with a starter `index.md`:
        ```markdown
        # {site_name}

        Welcome to the {site_name} documentation.
        ```
     f. Surface install commands as informational text. Do NOT execute them:
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

2. **Write `.doc-writer/config.yaml`** -- Read the config template from `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/config-template.yaml` and populate it with the Q&A answers. The config MUST use `user_personas:` as an array, even for a single persona. Include the `detected:` section with auto-detection results from the Project Detection Results above. The config MUST include `tone: "{selected_tone}"` as a top-level field. Each persona entry MUST include `user_tasks: [{selected_tasks}]`.

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
   - config.yaml -- [N] user persona(s), tone: {tone}, doc system: [system], paths configured
   - [doc_system].md -- Documentation system guidance (editable)
   - rules.md -- Project-specific rules template (editable)

   Running researcher to generate context.md...
   ```

### Step 4: Re-Run Update Flow

This section handles field-by-field editing when an existing config is detected.

Based on user selection from Step 1:

- **`user_personas`** (from "User Personas" selection above): Show current personas. Use AskUserQuestion:
  - header: "Personas"
  - question: "What would you like to do with your user persona configuration?"
  - options:
    - { label: "Edit persona", description: "Modify an existing persona's settings" }
    - { label: "Add persona", description: "Define a new user persona" }
    - { label: "Remove persona", description: "Delete an existing persona" }
    - { label: "Type something else", description: "Describe a different persona change" }
    - { label: "Chat about this", description: "Discuss persona configuration" }
  - Handle each selection with plain-text follow-ups as needed (which persona to edit/remove, new persona details).
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

> Enrich the project configuration. Read `.doc-writer/config.yaml` for user personas, tone, and doc system. Scan the codebase (README, source files, framework config) and produce `.doc-writer/context.md` with expanded persona guidance, project domain summary, tone-specific writing rules, and framework usage preferences.
>
> Framework Q&A answers: {framework_answers or "none -- use defaults from framework config detection"}

After the researcher completes, display the updated confirmation:
```
   - context.md -- Expanded context for downstream agents (editable)
```

For --refresh-context flows: Stop here. Do not show next steps.

For first-time setup and --reset flows, display this guidance after the confirmation:

```
## Next Steps

Setup is complete. To generate documentation:

1. Run `/clear` to free up context
2. Run `/doc-writer:write` to start the documentation pipeline

You can also run `/doc-writer:review` to audit existing docs without generating new ones.
```

## Notes

- All plugin-internal file references use `${CLAUDE_PLUGIN_ROOT}` for portability across different installation locations.
- The detection script runs automatically via `!`bash`` dynamic context injection when this skill is loaded.
- Config schema uses `user_personas:` (array) -- even for a single persona.
- Guidance files are opinionated preferences, not syntax references. Agents already understand doc system syntax.
- Rules in `.doc-writer/rules.md` are additive to universal quality rules -- they extend but cannot override the baseline.
- `tone` field in config.yaml stores a label; expanded writing rules live in `.doc-writer/context.md`.
- `user_tasks` on each persona entry stores the user's selections; expanded task descriptions live in `context.md`.
- The researcher agent is spawned at the end of every setup flow (first-time, --reset, --refresh-context) to ensure context.md is always current.
