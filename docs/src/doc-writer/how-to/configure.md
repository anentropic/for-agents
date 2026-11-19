---
title: Configure or reconfigure a project
description: Run the first setup on a project with existing docs, change personas, tone, use cases, doc system or paths, reset the configuration, or refresh the generated context
---

# How to configure or reconfigure a project

If your project already has a docs site, the first setup works around its config. After that
first run you can change doc-writer's configuration in three ways: edit one area through the
setup menu, start over with `--reset`, or regenerate `context.md` after you edit `config.yaml`
by hand.

## Before you start

- doc-writer is installed, and you are in your project's root directory.
- For everything except a first setup, `.doc-writer/config.yaml` already exists.

## Set up a project that already has docs

On a library with an existing site, the first setup leaves your pages and doc-system config
in place. Run:

```text
/doc-writer:setup
```

Answer the early questions as usual. Two of the later ones need care on an existing site.

### Doc system

The doc system question names the system that setup detected. Confirm it, and setup looks
for that system's config file in the project root: `mkdocs.yml` for `mkdocs-material`, `conf.py`
for `sphinx-shibuya`, `doc/dune` for `odoc`. When it finds the file, it never rewrites it:

- Under **Extras** it lists the recommended features your file lacks. Choose **None** to keep
  your config unchanged.
- For each feature you select, it shows the exact lines to add and asks you to choose
  **Add it** or **Skip**. Confirmed lines are appended and the rest of the file is left as it is.
- The framework questions that follow preselect the options that match the features your file
  already enables.

!!! warning "A config file outside the project root is not found"

    Setup checks the project root only. If your `conf.py` lives in `docs/`, for example, setup
    treats the project as having no config and writes a new `conf.py` to the project root.
    Delete that file before you commit.

### Paths

Setup proposes a docs root and a source root. It picks the docs root by folder name, not from
your doc-system config, so the default is wrong when your pages live in a subfolder. This
question takes plain text: press Enter to accept the defaults, or type the folder that holds
your pages, for example `docs/src/` when `mkdocs.yml` sets `docs_dir: docs/src`.

Check `paths.docs_root` in `.doc-writer/config.yaml` before your first `/doc-writer:write`.
With a wrong docs root, `write` finds fewer than two pages there and runs in create mode,
planning a whole new docs set instead of updating yours. To fix it, choose **Paths** from the
setup menu described next.

## Change one area of the configuration

Run setup again with no arguments:

```text
/doc-writer:setup
```

Setup prints the current configuration (personas, tone, use cases, doc system and paths) and
asks what to update:

| Option | What it changes |
|--------|-----------------|
| **User Personas** | Edit, add or remove a persona |
| **Tone** | The writing tone for all pages |
| **Use Cases** | Add, edit or remove use cases, or turn the Use Cases docs section on or off |
| **Doc system** | The documentation system, and its guidance file |
| **Paths** | The docs root and the source root |
| **Re-run researcher** | Regenerates `context.md` from the current config |
| **Done** | Ends setup and prints the current configuration |

Pick an option and answer its follow-up questions. Setup writes the change to `config.yaml`,
leaves every other field as it was, and then asks if you want to change anything else.

!!! warning "Re-run the researcher after changing the config"

    Changing a persona, the tone or the doc system from this menu updates `config.yaml` only.
    The agents also read the expanded guidance in `context.md`, which was generated from the
    old values. Choose **Re-run researcher** before you finish so the two match.

### Change the doc system

Choosing **Doc system** copies the new system's guidance file into `.doc-writer/` and runs the
same scaffold check as a first setup: it writes a config file such as `mkdocs.yml` if your
project has none, or offers missing recommended features if it has one. The previous guidance
file stays in `.doc-writer/`; delete it yourself if you no longer need it.

To use a system doc-writer does not ship guidance for, choose **Type something else** and
enter its name, for example `docusaurus`. doc-writer researches the framework and generates a
guidance file and setup questions for it before continuing.

### Turn on the Use Cases section

A Use Cases section adds discovery pages ("did you know you could do this?") next to the
tutorials, how-to guides, explanation and reference. It needs at least one explicit use case.
Choose **Use Cases**, add a use case, then choose **Toggle section**.

### Change rules or guidance

Rules and doc-system guidance are not menu options because you edit those files directly:
`.doc-writer/rules.md` and `.doc-writer/{doc_system}.md`. See
[Add project rules and terminology](project-rules.md).

## Start over with --reset

```text
/doc-writer:setup --reset
```

Setup asks you to confirm before it overwrites anything. Choose **Reset config** to run the full
first-time question flow. Your `config.yaml`, guidance file, `rules.md` and `.originals/` are
replaced with fresh files built from your new answers and the current plugin defaults, and
`context.md` is regenerated.

!!! danger "Your rules and guidance edits are replaced"

    `--reset` replaces `rules.md` and the guidance file with the plugin defaults. Copy any rules
    you want to keep before you confirm, and paste them back afterwards.

## Regenerate context.md after editing config.yaml

If you edit `config.yaml` directly, for example to add an item to a persona's `never_assume`
list, regenerate the expanded context without answering any questions:

```text
/doc-writer:setup --refresh-context
```

This runs only the Doc Researcher. It reads `config.yaml` and your codebase and overwrites
`.doc-writer/context.md`. It does not print the "Next Steps" block that a first setup shows.

## Check the result

Open `.doc-writer/config.yaml` and confirm the field you changed. If you re-ran the researcher,
check that the **Generated** date at the top of `.doc-writer/context.md` is today's.

## Troubleshooting

### Setup says "No configuration found"

`--refresh-context` needs an existing `config.yaml`. Run `/doc-writer:setup` without flags.

### Hand edits to context.md disappeared

The researcher overwrites `context.md` on every setup, `--reset`, `--refresh-context`,
**Re-run researcher**, and on upgrades that change the config. Put lasting changes in
`config.yaml` or `rules.md` instead.

### Pages are written to the wrong folder

Choose **Paths** and set the docs root to the folder your doc system builds from, for example
the `docs_dir` in `mkdocs.yml`.

## Related

- [config.yaml reference](../reference/configuration.md): every field and its allowed values.
- [The .doc-writer folder](../reference/files.md): which files are safe to edit.
- [Commands reference](../reference/commands.md#setup): all `setup` arguments.
