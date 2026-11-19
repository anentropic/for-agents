---
title: config.yaml
description: Every field in .doc-writer/config.yaml, its allowed values, and which command sets it
---

# config.yaml

`.doc-writer/config.yaml` holds a project's doc-writer settings. `/doc-writer:setup` creates
it, and every command reads it at startup. You can edit it by hand; run
`/doc-writer:setup --refresh-context` afterwards so `context.md` reflects the change.

## Example

```yaml title=".doc-writer/config.yaml"
version: 1
plugin_version: "1.9.0" # (1)!

user_personas: # (2)!
  - name: "Python developers who clean text data"
    skill_level: "intermediate"
    assumed_knowledge:
      - "Python, pip and virtual environments"
      - "pandas DataFrames"
    never_assume:
      - "the library's normalization rules"
      - "the rule file format"
    domain_context: "cleans and normalizes text before loading it into a database"
    discovery_story: "searched PyPI for a text-cleaning library"
    user_tasks:
      - "Clean a batch of strings"
      - "Write and load custom rules"
      - "Use the cleaner in a pandas pipeline"

tone: "warm-businesslike"

use_cases: [] # (3)!
use_cases_section: false

doc_system: "mkdocs-material"
api_reference: "" # (4)!

paths:
  docs_root: "docs/"
  source_root: "src/"

detected: # (5)!
  language: "python"
  doc_system: "mkdocs-material"
  existing_docs: false

qa_answers: # (6)!
  navigation: "Sidebar only"
  api_docs: "None"
  features: ["Content tabs", "Admonitions", "Collapsible details"]
```

1. Set by setup and updated by `/doc-writer:upgrade`. Don't edit it.
2. Always a list, even with a single persona. Each persona gets its own Doc Persona evaluation.
3. Empty when use cases were skipped during setup. See [use_cases](#use_cases).
4. Empty means the Editor looks for a generated API reference itself.
5. Written by setup's project detection.
6. Answers to the framework questions for the chosen doc system.

## Fields

### version

Config schema version. Currently `1`. Don't edit it.

### plugin_version

The doc-writer version the project's files were last set up or upgraded with, for example
`"1.9.0"`. `/doc-writer:upgrade` compares it with the installed plugin and writes the new value
when it finishes. Missing in projects set up before version 1.5.0; the upgrade adds it.

### user_personas

A list of reader profiles. Each entry has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Short label for the reader, used in reports and report file names |
| `skill_level` | string | `beginner`, `intermediate`, `advanced` or `expert`. Sets explanation depth and the kind of scenarios the Persona tries |
| `assumed_knowledge` | list of strings | What the reader already knows; the docs don't explain it |
| `never_assume` | list of strings | What the docs must always explain; a page that uses one of these unexplained breaks a quality rule |
| `domain_context` | string | The problem space the reader works in |
| `discovery_story` | string | How the reader found the library; shapes the Persona's goals |
| `user_tasks` | list of strings | What the reader does with the library; the Persona builds its scenarios from these |

`domain_context` and `discovery_story` are optional. Without them, the Persona infers a domain
from the name and assumed knowledge, and assumes the reader found the library through a web
search.

**Set by:** setup, menu option **User Personas**.

### tone

The writing tone for every page:

| Value | Style |
|-------|-------|
| `just-the-facts` | Minimal, no preamble, direct definitions, one example at most |
| `warm-businesslike` | Clear explanations, several examples, structured and approachable |
| `personality` | Same depth as `warm-businesslike`, with personality and occasional humour |

Any other string is used as a custom tone description. The expanded writing rules for the tone
are generated into `context.md`.

**Set by:** setup, menu option **Tone**.

### use_cases

A list of things readers achieve with the library. Each entry has four strings:

| Field | Description |
|-------|-------------|
| `title` | Short label, for example "Rate-limit API endpoints" |
| `problem` | The problem the reader has without the library |
| `capability` | What the library makes possible |
| `outcome` | The result once the use case is done |

Use cases give the agents real-world context. When `use_cases_section` is `true`, each one also
becomes a page in a Use Cases section.

**Set by:** setup, menu option **Use Cases**.

### use_cases_section

`true` adds a Use Cases section next to the tutorials, how-to guides, explanation and reference,
with one discovery page per use case and an index. `false` (the default) keeps use cases as
context only. Can be `true` only when `use_cases` has at least one entry.

**Set by:** setup, menu option **Use Cases**, then **Toggle section**.

### doc_system

The documentation system pages are written for. Built-in values: `mkdocs-material`,
`sphinx-shibuya`, `odoc`, `plain-markdown`. Another name is allowed if a matching guidance file
exists at `.doc-writer/{doc_system}.md`; setup generates one when you name an unsupported
system.

**Set by:** setup, menu option **Doc system**.

### api_reference

Where your generated API reference lives, for example `docs/reference/`. The Author and Editor
link inline code mentions to it. When empty, they look for one themselves (such as an
mkdocstrings plugin in `mkdocs.yml` or a `docs/api/` folder); if none is found, code mentions
stay as plain code and cross-reference linking is skipped.

**Set by:** edit by hand.

### paths

| Field | Default | Description |
|-------|---------|-------------|
| `docs_root` | `docs/` | Where pages are written and read. Must match the folder your doc system builds from |
| `source_root` | `src/` | Where your library's source code lives; scanned for exported symbols |

With `doc_system: odoc`, pages are written to `doc/` regardless of `docs_root`.

**Set by:** setup, menu option **Paths**.

### detected

Results of setup's project detection: `language` (for example `python`, `typescript`, `rust`,
`go`, `ocaml`), `doc_system`, and `existing_docs` (`true` or `false`). `language` selects how
gap detection finds exported symbols.

**Set by:** setup. Edit `language` by hand if detection guessed wrong.

### qa_answers

Your answers to the doc system's framework questions. Each key is the question's header,
lowercased with spaces replaced by underscores. Single-choice answers are strings;
multiple-choice answers are lists.

| Doc system | Keys |
|------------|------|
| `mkdocs-material` | `navigation`, `api_docs`, `features` |
| `sphinx-shibuya` | `navigation`, `api_docs`, `features` |
| `odoc` | `structure`, `scope`, `guides`, plus one key per guide topic question |
| `plain-markdown` | `callouts`, `headings`, `toc` |

For `odoc`, the `scope` answer sets whether the Author also proposes `.mli` doc comments. The
answer `".mld pages only"` turns them off.

**Set by:** setup and `/doc-writer:upgrade`, which asks only questions that have no key yet.

## See also

- [Configure or reconfigure a project](../how-to/configure.md): change these fields through setup.
- [The .doc-writer folder](files.md): the other files next to `config.yaml`.
- [Commands](commands.md): which command reads and writes each file.
