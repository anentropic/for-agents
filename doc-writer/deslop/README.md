# deslop (vendored)

The Doc Editor's deslop pass (Pass 3 in `agents/doc-editor.md`) measures prose with
[deslop](https://github.com/etodanik/deslop) by Danny Povolotski. This folder holds the parts
of deslop that the pass runs, plus a wrapper that makes them work on documentation pages.

## What is here

| Path | What it is |
|---|---|
| `docs_scan.py` | Ours. Builds a Markdown view of a `.md`, `.rst` or `.mld` page, masks protected terms, and runs deslop's scanner and fact check on that view. Never writes to the page. |
| `vendor/` | Unmodified files from deslop, pinned below. |

`docs_scan.py` commands, run from the project root:

```bash
python3 docs_scan.py scan PAGE       # flagged metrics for one page; snapshots the page on first scan
python3 docs_scan.py compare PAGE    # new flags, dropped facts and dropped protected terms since the snapshot
python3 docs_scan.py view PAGE       # the Markdown view the scanner reads (add --masked for the scan view)
python3 docs_scan.py clean           # delete the snapshots in .doc-writer/.deslop/
```

`compare` exits 1 when the revision dropped a number, code span or link.

### How a page becomes the scanner's view

The scanner reads Markdown, so `docs_scan.py` rewrites each page into a Markdown view first.
The view is thrown away after the scan; the editor edits the real page.

- **Code** is kept as fenced blocks and inline code, which the scanner skips and the fact check
  compares: MkDocs and Markdown fences (including `~~~`) and 4-space indented code blocks, RST
  `code-block` and `::` literal blocks, odoc `{[ ]}`, `{@lang[ ]}` and `{v v}`, and inline code in every format.
- **Links** are kept as Markdown links, so the fact check sees them: RST `:ref:` and `:doc:`,
  `` `text <url>`_ ``, odoc `{!ref}`, `{{:url} text}` and `{{!ref} text}`, MkDocs autorefs.
  A list item that starts with a link ("Further reading", "Next steps") becomes a table row,
  which the scanner skips and the fact check still reads.
- **Prose containers** keep their text: MkDocs admonitions and content tabs, and RST
  admonitions, `tab-set`/`tab-item`, `grid`, `card`, `dropdown` and similar directives. Their
  titles become headings.
- **Dropped:** YAML frontmatter, HTML comments, mkdocstrings `:::` lines, snippets, raw HTML,
  RST comments, targets, `toctree`, autodoc and any other unknown directive, odoc `@tags`,
  `{!modules: }` and raw `{% %}` markup. Tables (`list-table`, `csv-table`, simple `===  ===`
  tables) become table rows. Markdown footnotes (`[^1]: ...`) stay prose.

### Protected terms

Every multi-word or hyphenated `canonical` and `variants` entry in
`.doc-writer/terminology.yaml` is replaced by `TERM` in the scanned text, so the scanner can't
flag a project's own vocabulary ("single-agent", "belief state"). Terms wrapped across a line
break and terms inside link labels are masked too. Single words are not masked.
`compare` lists any protected term the revision uses less often than before.

### Docs thresholds

`docs_scan.py` always scans with deslop's `docs` genre and switches off two metrics for it:
`hyphen_compounds` and `repeated_ngrams`. Both fire on technical vocabulary, which docs repeat
word for word on purpose.

## Provenance

- Upstream: https://github.com/etodanik/deslop
- Commit: `a3260a6e7d2e9836673257b761c4824b5c80bb34` (2026-11-17)
- Changes: none. `docs_scan.py` adjusts thresholds at import time instead of editing
  `slop_scan.py`.

Only the files the pass needs are copied. deslop's evals, research notes, model-based tools and
`sources/` (third-party text that is not for redistribution) are left out. `vendor/references/data/README.md`
describes data files that are not copied here; only `graphite_tells_lexicon.json` is.

### Checksums

`tests/deslop/test_docs_scan.py` checks these, so an edit to a vendored file fails the tests.

| File | SHA-256 |
|---|---|
| `LICENSE.md` | `99d7f49f48f677ee2b9d692f008fc5f61e31fc1afb87190f71851abc8dc48718` |
| `references/data/README.md` | `07af5b70e44e8ceed4350ea45525e3c9025e51d157080cea96b2d7ad57298419` |
| `references/data/graphite_tells_lexicon.json` | `b9da589239842c770862dc821b79dcf6ebb0117ab5acce532156c8531b7e585e` |
| `references/patterns.md` | `25db412586f4a0515d0614a4f0f5d1dce0a282eb85055c6cc09dfdc0f21d435c` |
| `references/register.md` | `df7b4d872f05f0b862842b9ab8eae2eea05783b9f6f80bdaec668fc6c09cbfbb` |
| `scripts/check_invariants.py` | `66a9b82eff2862376c0164aa421c35622736a140fe040b28cf7dd236c723c610` |
| `scripts/slop_scan.py` | `e86b49c657d37f27d3d2aff4c3cecd9a3d6c31da9accb97248342578acc1daba` |

### Updating

`.github/workflows/deslop-sync.yml` checks upstream every Monday. When upstream `main` has moved,
it runs `sync.py`, runs the tests, and opens a PR with the upstream diff link and the test
result. Read the upstream diff before merging: these files run on users' machines.

To sync by hand, from the repository root:

```bash
python3 doc-writer/deslop/sync.py --check        # has upstream moved?
python3 doc-writer/deslop/sync.py                # sync to upstream main
python3 doc-writer/deslop/sync.py --ref <sha>    # sync to a branch, tag or commit
python3 -m unittest discover -s tests/deslop
```

`sync.py` downloads every file in the checksum table above at the resolved commit, and rewrites
the pinned commit (with the date of the sync) and the checksums. To vendor another file, add a
row for it to the table and run `sync.py`. Then scan a few real pages with
`docs_scan.py scan` to check the flags still make sense for docs.

## Licensing

- deslop's code and docs: MIT, Copyright (c) 2026 Danny Povolotski (`vendor/LICENSE.md`).
- `vendor/references/data/graphite_tells_lexicon.json` is derived from Graphite,
  "AI Tells" (2026), https://graphite.io/five-percent/research/ai-tells, licensed under
  CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Derived by deslop's
  `build_tell_lexicon.py`.
