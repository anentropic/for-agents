# Phase 10: Framework Scaffolding and Unknown Framework Research+Guidance Generation - Research

**Researched:** 2026-03-17
**Domain:** Framework scaffolding, unknown framework handling, dynamic guidance generation
**Confidence:** HIGH

## Summary

Phase 10 addresses two distinct but related capabilities in the doc-writer setup flow: (1) smart framework scaffolding when a user selects a known doc framework, and (2) a researcher-driven workflow for unknown frameworks that dynamically generates guidance files and Q&A question sets that persist globally into the plugin's defaults directory, permanently expanding built-in framework support.

The scaffolding sub-problem has two modes: if no framework config exists (e.g., no `mkdocs.yml`), the setup skill generates the full config file, scaffolds the docs directory, and surfaces install commands. If the framework is already configured, the skill diffs the existing config against the plugin's opinionated defaults and surfaces missing features as AskUserQuestion suggestions (e.g., "You don't have content tabs enabled -- we recommend it. Add it?").

The unknown framework sub-problem is the more novel piece. When the user types a framework name that has no built-in support (no guidance file in `defaults/`, no pre-authored Q&A question set), the setup skill spawns a researcher agent to investigate the framework, runs a Q&A session with the user to capture preferences, and then writes both a guidance `.md` file AND a Q&A question set back into the plugin's `defaults/` directory. This is a global write -- next time any user on any project selects this framework, it works like a built-in framework, complete with guidance and questions.

**Primary recommendation:** Decompose into three logical plans: (1) scaffolding logic for known frameworks (mkdocs-material, plain-markdown) with diff-against-defaults and full-scaffold modes, (2) unknown framework researcher workflow that generates guidance + Q&A question sets into plugin defaults, (3) setup skill integration connecting both capabilities into the existing flow.

## Standard Stack

### Core

This phase involves no external libraries. All work is prompt engineering and file generation within the existing Claude Code plugin framework.

| Asset | Type | Purpose | Why Standard |
|-------|------|---------|--------------|
| AskUserQuestion | CC tool | Presenting scaffold suggestions and framework Q&A | Phase 8/9 established pattern |
| Agent tool | CC tool | Spawning researcher for unknown framework investigation | Used by setup skill already |
| Read/Write/Glob/Grep/Bash | CC tools | Framework config parsing, file scaffolding | Standard tool set |
| `${CLAUDE_PLUGIN_ROOT}` | CC variable | Resolving paths to plugin defaults directory | Plugin portability mechanism |
| YAML/Markdown | Data formats | Config scaffolding, guidance files, Q&A question sets | Established project formats |

### Supporting

| Asset | Location | Purpose | When to Use |
|-------|----------|---------|-------------|
| setup SKILL.md | `doc-writer/skills/setup/SKILL.md` | Integration point for both sub-problems | Modified to add scaffolding + unknown framework handling |
| detect-project.sh | `doc-writer/skills/setup/scripts/` | Detects existing framework config files | Feeds scaffolding mode decision |
| mkdocs-material.md | `doc-writer/skills/setup/defaults/` | Existing known guidance file | Template for what unknown framework guidance looks like |
| plain-markdown.md | `doc-writer/skills/setup/defaults/` | Existing known guidance file | Template for guidance structure |
| config-template.yaml | `doc-writer/skills/setup/defaults/` | Config schema template | No changes needed |
| doc-researcher.md | `doc-writer/agents/doc-researcher.md` | Researcher agent definition | Extended or second agent for unknown framework research |
| cookiecutter mkdocs.yml | External reference | Opinionated mkdocs-material defaults | Baseline for diff-against-defaults scaffolding |

## Architecture Patterns

### Recommended File Structure (New and Modified Files)

```
doc-writer/
  agents/
    doc-researcher.md          # MODIFY: add unknown-framework research mode
  skills/
    setup/
      SKILL.md                 # MODIFY: add scaffolding logic + unknown framework flow
      defaults/
        mkdocs-material.md     # NO CHANGE (existing guidance)
        mkdocs-material.qa.md  # NEW: extracted Q&A question set for mkdocs-material
        plain-markdown.md      # NO CHANGE (existing guidance)
        plain-markdown.qa.md   # NEW: extracted Q&A question set for plain-markdown
        scaffolds/
          mkdocs-material.yml  # NEW: opinionated default mkdocs.yml template
        config-template.yaml   # NO CHANGE
        rules.md               # NO CHANGE
      scripts/
        detect-project.sh      # NO CHANGE (already detects all major frameworks)
```

### Pattern 1: Diff-Against-Defaults Scaffolding (Existing Config)

**What:** When a framework config file already exists (e.g., `mkdocs.yml`), read it, compare against the plugin's opinionated defaults, and surface missing features as AskUserQuestion suggestions. Do NOT overwrite anything without explicit user confirmation.

**When to use:** User selects a known framework AND the corresponding config file is detected.

**Flow:**
```
1. Detect: mkdocs.yml exists
2. Read: parse existing mkdocs.yml features/extensions/plugins
3. Compare: diff against plugin's opinionated defaults (scaffolds/mkdocs-material.yml)
4. Surface gaps: present missing features as multiSelect AskUserQuestion
   - "Your mkdocs.yml doesn't have these features we recommend. Enable?"
   - Pre-select recommended ones, let user deselect
5. Apply: for each confirmed feature, append to mkdocs.yml
   - Use Read then Write (append/merge, not overwrite)
   - Show the user exactly what will be added before writing
```

**Example AskUserQuestion:**
```
AskUserQuestion:
  header: "Extras"
  question: "Your mkdocs.yml is missing these recommended features. Enable any?"
  multiSelect: true
  options:
    - { label: "Content tabs", description: "pymdownx.tabbed -- for multi-language examples" }
    - { label: "Mermaid diagrams", description: "pymdownx.superfences custom fence -- for flow diagrams" }
    - { label: "Code annotations", description: "content.code.annotate -- numbered code explanations" }
    - { label: "None", description: "Keep current config as-is" }
    - { label: "Type something else", description: "Describe other changes" }
    - { label: "Chat about this", description: "Learn what each feature does" }
```

### Pattern 2: Full Scaffolding (No Existing Config)

**What:** When no framework config file exists, generate the full opinionated default config, scaffold the docs directory with starter files, and surface install commands.

**When to use:** User selects a known framework AND no corresponding config file is detected.

**Flow:**
```
1. Detect: no mkdocs.yml exists
2. Run framework Q&A (existing Step 2b.5) to capture preferences
3. Generate: write mkdocs.yml from scaffold template + Q&A answers
4. Scaffold docs/:
   - docs/index.md (starter page with project name)
   - docs/getting-started.md (placeholder)
5. Surface install commands:
   - "Run: pip install mkdocs-material" (or equivalent)
   - Present as informational, not automatically executed
```

**Key design choice:** Install commands are surfaced to the user as information, not executed automatically. The setup skill should NEVER run package installation commands. It presents them and the user runs them.

### Pattern 3: Unknown Framework Researcher Workflow

**What:** When the user types a framework name not in the plugin's built-in list, spawn a researcher agent to investigate the framework, generate a guidance file, and generate a Q&A question set. Both are written to the plugin's `defaults/` directory (global, not project-local).

**When to use:** User selects "Type something else" in doc system selection and enters a framework name that has no matching file in `defaults/`.

**Flow:**
```
1. User enters custom framework name (e.g., "docusaurus")
2. Check: does defaults/{name}.md exist?
   - YES: treat as known framework, skip to framework Q&A
   - NO: spawn unknown framework researcher
3. Researcher investigates:
   - WebSearch for official docs, config structure, features, conventions
   - Identify: config file name, docs directory convention, key features,
     admonition/callout syntax, code block conventions, nav structure options
4. Researcher generates TWO files:
   a. defaults/{name}.md -- guidance file (same structure as mkdocs-material.md)
   b. defaults/{name}.qa.md -- Q&A question set (framework-specific questions)
5. Run Q&A from the newly generated question set
6. Continue normal setup flow with the new framework as a known framework
```

**Guidance file structure (generated):**
```markdown
# {Framework Name} Guidance

Opinionated preferences for writing documentation with {Framework Name}.
These are style preferences -- agents already understand {Framework Name} syntax.
This file guides how features should be used, not what they are.

## {Feature Category 1}
- {preference 1}
- {preference 2}

## {Feature Category 2}
- {preference 1}
...
```

**Q&A question set structure (generated):**
```markdown
# {Framework Name} Q&A

Framework-specific questions for {Framework Name} setup.
Presented during /doc-writer:setup after doc system selection.

## Question 1: {Topic}
- header: "{short header}"
- question: "{question text}"
- options:
  - { label: "{option}", description: "{description}" }
  ...
  - { label: "Type something else", description: "{fallback}" }
  - { label: "Chat about this", description: "{discuss}" }

## Question 2: {Topic}
...
```

### Pattern 4: Q&A Question Sets as Data Files

**What:** Extract framework Q&A questions from the setup SKILL.md into separate `.qa.md` data files in `defaults/`. The setup skill reads the appropriate `.qa.md` file and presents the questions dynamically rather than having them hardcoded in the skill body.

**Why:** This is the key architectural enabler for unknown framework support. If Q&A questions are hardcoded in the setup skill, adding a new framework requires modifying the skill. If they are data files in `defaults/`, the unknown framework researcher can generate new question sets that the setup skill automatically picks up.

**When to use:** Always -- even for mkdocs-material and plain-markdown, extract their Q&A into `.qa.md` files.

**Setup skill reads Q&A dynamically:**
```
1. After doc system selection, check for:
   ${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{doc_system}.qa.md
2. If found: Read the file, parse questions, present them via AskUserQuestion
3. If not found AND defaults/{doc_system}.md exists: skip Q&A (known framework, no questions)
4. If not found AND defaults/{doc_system}.md does NOT exist: trigger unknown framework researcher
```

### Pattern 5: Scaffold Templates as Data Files

**What:** Store opinionated default config files as templates in `defaults/scaffolds/`. The scaffolding logic reads these templates when generating config for projects that don't have one.

**Why:** Keeps the setup skill lean -- it reads templates rather than embedding config generation logic.

**Template naming:** `defaults/scaffolds/{doc_system}.yml` (or `.js`, `.py` as appropriate for the framework).

### Anti-Patterns to Avoid

- **Executing install commands automatically:** The setup skill must NEVER run `pip install`, `npm install`, or similar. Surface commands as information only.
- **Overwriting existing config without confirmation:** Every change to an existing framework config must be explicitly confirmed by the user via AskUserQuestion.
- **Hardcoding framework Q&A in setup SKILL.md:** This prevents dynamic expansion. Use `.qa.md` data files.
- **Writing unknown framework outputs to project-local `.doc-writer/`:** Generated guidance and Q&A go to the plugin's `defaults/` directory (global), not to the project's `.doc-writer/`. The project gets a copy of the guidance file in `.doc-writer/` during Step 3, same as known frameworks.
- **Researcher trying to scaffold config for unknown frameworks:** The researcher generates guidance and Q&A question sets. Config scaffolding for unknown frameworks is manual -- the user creates their own config. Only known frameworks (with scaffold templates) get auto-generated config.
- **Making the researcher's WebSearch mandatory:** If the researcher cannot reach the internet (e.g., sandboxed environment), it should fall back to generating guidance from its training knowledge, flagging it as LOW confidence and suggesting the user review.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parsing for mkdocs.yml | Custom bash scripts | Agent's Read + Grep tools | Agents can natively parse YAML |
| Framework feature detection | Regex-based shell scripts | Agent analysis of config file content | More robust, handles edge cases |
| Install command lookup | Hardcoded command table | Researcher inference from framework docs | Scales to unknown frameworks |
| Config merging (existing + new features) | Custom merge logic | Agent reads existing, appends additions via Write | Simpler, handles complex YAML structure |

**Key insight:** The setup skill should remain an orchestrator. All intelligence about framework analysis, guidance generation, and Q&A generation belongs in the researcher agent or in data files. The setup skill reads data files and spawns agents.

## Common Pitfalls

### Pitfall 1: Global Write Permissions

**What goes wrong:** Writing to `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/` fails because the plugin directory may be read-only (e.g., installed via marketplace, managed by CC).
**Why it happens:** The plugin's installation directory might not be writable in all deployment scenarios.
**How to avoid:** Before writing to `defaults/`, verify write access. If the write fails, fall back to writing the guidance file to the project's `.doc-writer/` directory and inform the user that the generated guidance is project-local. Log a message: "Could not write to plugin defaults. Generated guidance saved locally. To make it globally available, copy `.doc-writer/{name}.md` and `.doc-writer/{name}.qa.md` to your plugin's defaults/ directory."
**Warning signs:** Permission denied errors when writing to `${CLAUDE_PLUGIN_ROOT}`.

### Pitfall 2: Scaffolding Overwrites User Customizations

**What goes wrong:** Full scaffolding mode writes a `docs/index.md` that overwrites existing content.
**Why it happens:** The scaffolding checks for config file existence but not docs directory content.
**How to avoid:** Before writing any scaffold file, check if it already exists. If it does, skip it or ask the user. The diff-against-defaults mode should only ADD missing features, never remove or modify existing ones.
**Warning signs:** Any Write call without a preceding existence check.

### Pitfall 3: Unknown Framework Researcher Produces Low-Quality Guidance

**What goes wrong:** The researcher generates a guidance file that's too generic or contains incorrect framework conventions.
**Why it happens:** WebSearch results may be outdated, incomplete, or for the wrong version. Training data may be stale.
**How to avoid:** The researcher should explicitly flag confidence level in the generated guidance file header. Include a "Review Status" field: "Auto-generated -- review recommended." The user should be prompted to review the generated guidance before it's used by downstream agents.
**Warning signs:** Generic guidance that doesn't mention framework-specific features. Guidance that contradicts official docs.

### Pitfall 4: Q&A Question Set Format Drift

**What goes wrong:** Generated `.qa.md` files don't follow the exact format the setup skill expects, causing parse errors or missed questions.
**Why it happens:** The researcher generates free-form markdown that doesn't match the structured format.
**How to avoid:** Define a strict schema for `.qa.md` files in the researcher prompt. Include a concrete example of a well-formed `.qa.md` file. The setup skill should validate the format and handle malformed files gracefully (skip Q&A if parse fails, inform user).
**Warning signs:** Generated .qa.md files with inconsistent structure compared to the mkdocs-material.qa.md reference.

### Pitfall 5: Circular Detection -- Framework Already Known

**What goes wrong:** User types "mkdocs-material" in the "Type something else" path, triggering the unknown framework flow for a known framework.
**Why it happens:** The "Type something else" handler doesn't check against known frameworks before spawning the researcher.
**How to avoid:** After the user enters a framework name, FIRST check if `defaults/{name}.md` or `defaults/{name}.qa.md` exists. If so, use the existing files -- don't re-research. Only spawn the researcher if no defaults exist.
**Warning signs:** Researcher running for frameworks that already have guidance files.

### Pitfall 6: Scaffold Template Staleness

**What goes wrong:** The opinionated mkdocs.yml template becomes outdated as MkDocs Material releases new features.
**Why it happens:** Static templates don't auto-update.
**How to avoid:** Keep scaffold templates minimal -- include core structure and recommended features, not every possible option. Document the template version/date in a comment. The diff-against-defaults approach naturally handles this: even if the template is slightly outdated, it still surfaces genuinely useful missing features.
**Warning signs:** Scaffold templates referencing deprecated features or missing important new ones.

### Pitfall 7: Step Ordering with Unknown Framework

**What goes wrong:** The setup flow tries to run framework Q&A before the researcher has generated the question set.
**Why it happens:** The current flow assumes Q&A question sets exist before they're needed.
**How to avoid:** The flow for unknown frameworks MUST be: (1) detect unknown, (2) spawn researcher to generate guidance + Q&A, (3) THEN run the generated Q&A, (4) continue to paths + file creation. The Q&A step must wait for the researcher to complete.
**Warning signs:** AskUserQuestion referencing a .qa.md file that doesn't exist yet.

## Code Examples

### Scaffold Template: mkdocs-material.yml

```yaml
# Source: opinionated defaults based on cookiecutter-python-uv-library/mkdocs.yml
# Stored at: doc-writer/skills/setup/defaults/scaffolds/mkdocs-material.yml
# Template variables: {site_name}, {site_description}

site_name: "{site_name}"
site_description: "{site_description}"
docs_dir: docs/

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.instant
    - navigation.sections
    - navigation.top
    - navigation.tracking
    - toc.follow
    - content.code.copy
    - content.code.annotate
    - search.suggest
    - search.highlight

plugins:
  - search

markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
```

### Q&A Question Set: mkdocs-material.qa.md

```markdown
# MkDocs Material Q&A

Framework-specific questions for mkdocs-material setup.
Presented during /doc-writer:setup after doc system selection.
Auto-detect: check for mkdocs.yml in project root.

## Detection

Config file: mkdocs.yml
Features to detect:
- navigation.sections, navigation.tabs (theme.features)
- pymdownx.tabbed (markdown_extensions)
- pymdownx.superfences with mermaid fence (markdown_extensions)
- admonition (markdown_extensions)
- pymdownx.details (markdown_extensions)
- content.code.annotate (theme.features)
- mkdocstrings (plugins)
- literate-nav (plugins)

## Question 1: Navigation style

- header: "Navigation"
- question: "How should documentation be organized?"
- detect_context: "Detected: {detected features from mkdocs.yml}"
- options:
  - { label: "Sections", description: "2-level nav: sections group related pages (navigation.sections)", recommend_if: "navigation.sections detected" }
  - { label: "Tabs + sections", description: "Top-level tabs with sections underneath (navigation.tabs)", recommend_if: "navigation.tabs detected" }
  - { label: "Flat", description: "All pages at one level, no grouping" }
  - { label: "Type something else", description: "Describe a different nav structure" }
  - { label: "Chat about this", description: "Discuss navigation options" }

## Question 2: API reference approach

- header: "API docs"
- question: "How is API reference generated?"
- detect_context: "Detected: mkdocstrings with {docstring_style}"
- options:
  - { label: "mkdocstrings", description: "Auto-generated from docstrings", recommend_if: "mkdocstrings detected" }
  - { label: "Manual pages", description: "Hand-written API reference in docs/" }
  - { label: "None", description: "No API reference -- narrative docs only" }
  - { label: "Type something else", description: "Describe a different approach" }
  - { label: "Chat about this", description: "Discuss API reference options" }

## Question 3: Rich features usage

- header: "Features"
- question: "Which MkDocs Material features should docs use?"
- multiSelect: true
- detect_context: "Detected: {detected list}"
- options:
  - { label: "Content tabs", description: "For multi-language or multi-method examples (pymdownx.tabbed)", recommend_if: "pymdownx.tabbed detected" }
  - { label: "Mermaid diagrams", description: "For architecture and flow diagrams (pymdownx.superfences)", recommend_if: "mermaid fence detected" }
  - { label: "Code annotations", description: "Numbered annotations explaining code lines (content.code.annotate)", recommend_if: "content.code.annotate detected" }
  - { label: "Admonitions", description: "Tip/warning/info callout boxes (admonition)", recommend_if: "admonition detected" }
  - { label: "Collapsible details", description: "Expandable sections for optional content (pymdownx.details)", recommend_if: "pymdownx.details detected" }
  - { label: "Type something else", description: "Add or remove features" }
  - { label: "Chat about this", description: "See examples of each feature" }
```

### Setup Skill: Unknown Framework Detection Branch

```markdown
# Inserted into Step 2b (Doc System Selection) "Type something else" handler:

- **"Type something else":** Ask in plain text for the doc system name. Then:
  1. Normalize the name to lowercase-hyphenated form (e.g., "Docusaurus" -> "docusaurus")
  2. Check if `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{name}.md` exists:
     - **If YES:** Record as doc_system. Proceed to Step 2b.5 (framework Q&A).
     - **If NO:** Inform the user: "No built-in support for '{name}' yet. I'll research
       this framework and generate guidance. This will take a moment."
       Spawn the doc-researcher agent with framework research mode:
       > Research the documentation framework '{name}'. Generate two files:
       > 1. A guidance file at `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{name}.md`
       >    following the structure of the existing mkdocs-material.md guidance file.
       >    Cover: admonitions/callouts, code blocks, content organization, navigation,
       >    frontmatter, cross-references, and any framework-specific features.
       > 2. A Q&A question set at `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{name}.qa.md`
       >    following the structure of mkdocs-material.qa.md. Include 2-4 questions about
       >    key framework configuration choices (navigation, features, content organization).
       >
       > Use WebSearch to find official documentation for '{name}'. If WebSearch is unavailable,
       > generate from training knowledge and flag as LOW confidence in the file header.
       >
       > After generating, also write a scaffold template to
       > `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/scaffolds/{name}.{ext}` if the
       > framework uses a config file.

       After researcher completes, record as doc_system. Proceed to Step 2b.5.
```

### Researcher Agent: Framework Research Mode

```markdown
# Addition to doc-researcher.md -- a new mode triggered by setup skill

## Mode: Unknown Framework Research

When spawned with a framework research message (containing "Research the documentation framework"):

### Step 1: Investigate Framework

1. Use WebSearch to find the framework's:
   - Official documentation site
   - Getting started / installation guide
   - Configuration file format and default structure
   - Key features and extensions
   - Markdown/content conventions (admonitions, code blocks, frontmatter)
   - Navigation structure options

2. If WebSearch is unavailable, use training knowledge and flag output as:
   ```
   **Confidence:** LOW -- generated from training knowledge without live verification.
   Review against current official docs before relying on this guidance.
   ```

### Step 2: Generate Guidance File

Write `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{name}.md` following this structure:

```markdown
# {Framework Name} Guidance

<!-- Auto-generated by doc-researcher. Review recommended. -->
<!-- Generated: {date} -->
<!-- Confidence: {HIGH if WebSearch verified, LOW if training only} -->

Opinionated preferences for writing documentation with {Framework Name}.
These are style preferences -- agents already understand {Framework Name} syntax.
This file guides how features should be used, not what they are.

## {Category 1: e.g., Admonitions / Callouts}
- {preference}
- {preference}

## {Category 2: e.g., Code Blocks}
- {preference}
...
```

### Step 3: Generate Q&A Question Set

Write `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/{name}.qa.md` with 2-4 questions.

### Step 4: Generate Scaffold Template (if applicable)

If the framework uses a config file, write a minimal opinionated default to
`${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/scaffolds/{name}.{ext}`.
```

### Diff-Against-Defaults: Feature Comparison Logic

```markdown
# In setup SKILL.md, new step between framework detection and framework Q&A:

### Step 2b.3: Scaffold Check (Known Frameworks)

After doc system selection and BEFORE framework Q&A:

1. **Check for existing framework config:**
   - mkdocs-material: Glob for `mkdocs.yml` or `mkdocs.yaml`
   - plain-markdown: Skip (no config file)
   - Other known frameworks: check for their config file per the .qa.md Detection section

2. **If config file NOT found (full scaffold):**
   - Check if `${CLAUDE_PLUGIN_ROOT}/skills/setup/defaults/scaffolds/{doc_system}.yml` exists.
   - If scaffold template exists:
     - Read the template.
     - Ask user for site_name (infer from package manifest or README title).
     - Generate config file from template.
     - Create starter docs:
       - `{paths.docs_root}/index.md` with project name and basic intro
     - Surface install commands as informational text:
       - mkdocs-material: "Install: pip install mkdocs-material"
       - Show but do NOT execute.
   - If no scaffold template: inform user they will need to create config manually.
   - Proceed to Step 2b.5 (framework Q&A).

3. **If config file FOUND (diff-against-defaults):**
   - Read the existing config file.
   - Read the scaffold template (opinionated defaults).
   - Compare: identify features/extensions in the template that are ABSENT from the existing config.
   - If gaps found, present as AskUserQuestion:
     - header: "Extras"
     - question: "Your {config_file} is missing these recommended features. Enable any?"
     - multiSelect: true
     - options: one per missing feature + "None" + trailing options
   - For each selected feature: append the relevant config block to the existing file.
     - Show the exact YAML/config that will be added BEFORE writing.
     - Use AskUserQuestion to confirm: "Add this to {config_file}?"
   - Proceed to Step 2b.5 (framework Q&A).
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Only 2 built-in frameworks (mkdocs-material, plain-markdown) | Dynamic expansion via researcher | Phase 10 | Any doc framework becomes supported on first use |
| Q&A questions hardcoded in setup SKILL.md | Q&A as data files (.qa.md) in defaults/ | Phase 10 | Framework support is purely additive -- no skill code changes |
| No scaffolding -- user creates config manually | Smart scaffolding with diff-against-defaults | Phase 10 | Lower friction for new projects, better configs for existing ones |
| "Type something else" for unknown frameworks = dead end | Unknown frameworks trigger research + global guidance generation | Phase 10 | Plugin gets smarter over time |

## Open Questions

1. **Q&A Data File Format**
   - What we know: Q&A question sets need a structured format the setup skill can parse.
   - What's unclear: Should the format be strictly YAML-parseable or loose markdown that the agent interprets?
   - Recommendation: Use structured markdown (as shown in the code examples above) that the agent interprets. Strict YAML parsing in an agent prompt is fragile. The agent reads the .qa.md file, understands the question structure, and presents AskUserQuestion calls accordingly. This is more robust than machine-parsed YAML and consistent with how agents already read guidance files.

2. **Scaffold Template Scope**
   - What we know: mkdocs-material needs a scaffold template. plain-markdown has no config file.
   - What's unclear: Should we scaffold config for ALL known frameworks or only frameworks with templates?
   - Recommendation: Start with mkdocs-material scaffold template only. plain-markdown has no config file to scaffold. Unknown frameworks get scaffold templates generated by the researcher (if the framework uses a config file). Future known frameworks (docusaurus, vitepress, sphinx) can add scaffold templates when their guidance is generated.

3. **Global Write Failure Fallback**
   - What we know: Writing to `${CLAUDE_PLUGIN_ROOT}` may fail in read-only installations.
   - What's unclear: How common is this? What's the graceful fallback?
   - Recommendation: Try global write first. If it fails, fall back to project-local `.doc-writer/` and inform the user. Log the path where files were saved. This handles both writable (typical dev) and read-only (marketplace) scenarios.

4. **Researcher Internet Access for Unknown Frameworks**
   - What we know: The researcher uses WebSearch to investigate unknown frameworks.
   - What's unclear: What if WebSearch is unavailable or sandboxed?
   - Recommendation: The researcher should fall back to training knowledge with a LOW confidence flag. Generated guidance from training knowledge is still useful -- it covers major frameworks well. The confidence flag tells the user to review it.

5. **Extracting Existing Q&A from Setup Skill**
   - What we know: mkdocs-material and plain-markdown Q&A is currently hardcoded in Step 2b.5 of the setup SKILL.md.
   - What's unclear: Should Phase 10 extract them into .qa.md files or keep them inline and only use .qa.md for new frameworks?
   - Recommendation: Extract them. This creates a single code path: the setup skill always reads .qa.md for framework Q&A, whether the framework is built-in or newly researched. Two code paths (inline for known, .qa.md for unknown) is error-prone and harder to maintain. The extraction is a straightforward refactor of existing content.

6. **Existing Config Modification Safety**
   - What we know: The diff-against-defaults feature modifies existing config files.
   - What's unclear: How to safely append YAML without breaking the file.
   - Recommendation: The agent reads the existing file, determines the correct insertion point, and uses the Write tool to write the complete updated file. This is safer than trying to surgically append. The agent shows the user the complete proposed change via a code block before writing.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | BATS (Bash Automated Testing System) |
| Config file | None -- BATS uses convention-based test files |
| Quick run command | `bats tests/phase-10-validation.bats` |
| Full suite command | `bats tests/` |

### Phase Requirements -> Test Map

Phase 10 has no formal requirement IDs. Testing validates structural changes:

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P10-01 | mkdocs-material.qa.md exists in defaults/ | unit | `bats tests/phase-10-validation.bats -f "mkdocs qa"` | No -- Wave 0 |
| P10-02 | plain-markdown.qa.md exists in defaults/ | unit | `bats tests/phase-10-validation.bats -f "plain qa"` | No -- Wave 0 |
| P10-03 | scaffolds/mkdocs-material.yml exists | unit | `bats tests/phase-10-validation.bats -f "mkdocs scaffold"` | No -- Wave 0 |
| P10-04 | setup SKILL.md references .qa.md files | unit | `bats tests/phase-10-validation.bats -f "qa reference"` | No -- Wave 0 |
| P10-05 | setup SKILL.md has scaffold check step | unit | `bats tests/phase-10-validation.bats -f "scaffold check"` | No -- Wave 0 |
| P10-06 | setup SKILL.md handles unknown framework | unit | `bats tests/phase-10-validation.bats -f "unknown framework"` | No -- Wave 0 |
| P10-07 | doc-researcher.md has framework research mode | unit | `bats tests/phase-10-validation.bats -f "researcher framework"` | No -- Wave 0 |
| P10-08 | No hardcoded framework Q&A in setup SKILL.md body | unit | `bats tests/phase-10-validation.bats -f "no hardcoded qa"` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `bats tests/phase-10-validation.bats`
- **Per wave merge:** `bats tests/`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/phase-10-validation.bats` -- all P10-XX tests
- [ ] BATS framework already installed (used in Phase 1 and Phase 7)

## Sources

### Primary (HIGH confidence)
- Existing codebase: setup SKILL.md (465 lines), doc-researcher.md, mkdocs-material.md, plain-markdown.md, config-template.yaml, detect-project.sh
- Phase 9 CONTEXT.md and RESEARCH.md: established patterns for researcher agent, framework Q&A, AskUserQuestion
- Phase 9 plan 03 and summary: exact implementation of current framework Q&A flow
- Cookiecutter mkdocs.yml: opinionated defaults baseline for scaffold template

### Secondary (MEDIUM confidence)
- [MkDocs Configuration](https://www.mkdocs.org/user-guide/configuration/) -- config file structure and defaults
- [Material for MkDocs Setup](https://squidfunk.github.io/mkdocs-material/setup/) -- feature configuration
- [VitePress Getting Started](https://vitepress.dev/guide/getting-started) -- VitePress scaffold structure
- [Docusaurus Configuration](https://docusaurus.io/docs/api/docusaurus-config) -- Docusaurus config structure
- [Sphinx Getting Started](https://www.sphinx-doc.org/en/master/usage/quickstart.html) -- Sphinx quickstart structure

### Tertiary (LOW confidence)
- None -- all findings sourced from existing codebase analysis or official documentation

## Metadata

**Confidence breakdown:**
- Scaffolding for known frameworks: HIGH -- straightforward extension of existing setup flow with well-understood frameworks
- Unknown framework researcher: HIGH -- extends existing doc-researcher pattern with WebSearch (already available)
- Q&A data file format: MEDIUM -- the .qa.md format is a new design; the agent-interpreted approach is sound but the exact format needs validation during implementation
- Global write strategy: MEDIUM -- depends on deployment scenario; fallback path is well-defined but untested

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stable -- no external dependencies that change rapidly)
