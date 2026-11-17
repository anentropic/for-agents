"""Tests for doc-writer/deslop/docs_scan.py, the docs pre-filter around the vendored deslop scanner.

Run from the repository root:

    python3 -m unittest discover -s tests/deslop -v
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import pathlib
import re
import shutil
import sys
import tempfile
import textwrap
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
DESLOP = REPO / "doc-writer" / "deslop"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(DESLOP))

import docs_scan  # noqa: E402

# Markup that must never reach the scanner as prose.
RESIDUE = re.compile(r"(\.\. [a-z]|\w::|\{[0-9a-z!:@%][^}]*\}?|:\w+:`|`|<https?:|\x00|^\||\]\}|"
                     r"\{v\b|^!!!|^\?\?\?|^===|^---)")


def write(dirpath: pathlib.Path, name: str, text: str) -> pathlib.Path:
    p = dirpath / name
    p.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")
    return p


def sentences(path: pathlib.Path, terms: list[str] | None = None) -> list[str]:
    fact, scan = docs_scan.views(path, terms or [])
    return docs_scan.make_doc(scan, fact).sentences


class TempDir(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class MarkdownView(TempDir):
    def test_frontmatter_admonitions_tabs_and_code_stay_out_of_prose(self) -> None:
        p = write(self.tmp, "page.md", '''
            ---
            title: Frontmatter Title
            description: A description that is metadata, not prose.
            ---

            # Page

            The pool opens connections lazily.

            !!! warning "Watch the timeout"
                The timeout is in seconds.

            === "uv"

                Install with uv.

                ```bash
                uv add thing
                ```

            ~~~python
            print("fenced with tildes")
            ~~~

            ::: package.module

            <!-- INTERNAL NOTES FOR EDITOR: not prose -->
            ''')
        s = sentences(p)
        joined = " ".join(s)
        self.assertNotIn("description", joined)
        self.assertNotIn("Frontmatter", joined)
        self.assertNotIn("uv add", joined)
        self.assertNotIn("tildes", joined)
        self.assertNotIn("INTERNAL", joined)
        self.assertNotIn("package.module", joined)
        self.assertIn("The timeout is in seconds.", s)
        self.assertIn("Install with uv.", s)
        self.assertFalse([x for x in s if RESIDUE.search(x)], s)
        fact, _ = docs_scan.views(p, [])
        self.assertIn("uv add thing", fact)            # the fact check still sees the code
        self.assertIn('print("fenced with tildes")', fact)

    def test_navigation_lists_become_table_rows_and_keep_their_links(self) -> None:
        p = write(self.tmp, "page.md", '''
            Body sentence here.

            ## Further reading

            - [The Kumiho Architecture](kumiho.md): multi-scope as one of two departures.
            - [`Scope`][doxastica.models.Scope] reference.
            - A normal bullet that is prose.
            ''')
        s = sentences(p)
        self.assertNotIn("multi-scope as one of two departures.", " ".join(s))
        self.assertTrue(any("normal bullet" in x for x in s))
        fact, _ = docs_scan.views(p, [])
        self.assertIn("](kumiho.md)", fact)
        self.assertIn("](doxastica.models.Scope)", fact)

    def test_footnotes_stay_prose_not_link_definitions(self) -> None:
        p = write(self.tmp, "page.md", '''
            The pool recycles connections.[^1]

            [^1]: The pool is recycled after 30 minutes.
            ''')
        fact, _ = docs_scan.views(p, [])
        self.assertIn("[^1]: The pool is recycled after 30 minutes.", fact)
        self.assertNotIn("](The)", fact)

    def test_indented_code_blocks_are_code_but_list_and_admonition_bodies_are_not(self) -> None:
        p = write(self.tmp, "page.md", '''
            Run the server:

                $ server --port 8080

            - A list item
                that continues on an indented line.

            !!! note
                Admonition bodies are prose.
            ''')
        s = sentences(p)
        self.assertNotIn("server --port", " ".join(s))
        self.assertIn("Admonition bodies are prose.", s)
        self.assertTrue(any("continues on an indented line" in x for x in s), s)
        fact, _ = docs_scan.views(p, [])
        self.assertIn("```\n$ server --port 8080\n```", fact)

    def test_inline_code_may_wrap_lines(self) -> None:
        p = write(self.tmp, "page.md", '''
            The `async with await
            pool.connect()` form is the same.
            ''')
        self.assertEqual(sentences(p), ["The CODE form is the same."])


class RstView(TempDir):
    def test_directives_titles_roles_and_literals(self) -> None:
        p = write(self.tmp, "page.rst", '''
            .. _howto-thing:

            How to do a thing
            =================

            Use :py:class:`~pkg.mod.Widget` with :func:`build` and see :ref:`tutorial-start`.
            Read `the guide <https://example.com/guide>`_ and :ref:`the intro <intro>`.

            .. code-block:: python
               :caption: example

               widget = Widget()

            .. note::

               Notes are prose and are kept.

            .. toctree::
               :maxdepth: 2

               page-one
               page-two

            .. tab-set::

               .. tab-item:: Snowflake
                  :sync: snowflake

                  Snowflake needs a warehouse.

                  .. code-block:: bash

                     pip install thing

            .. list-table::
               :header-rows: 1

               * - Field
                 - Meaning
               * - ``pool_size``
                 - Connections kept open

            =========  =======
            Field      Default
            =========  =======
            timeout    30
            recycle    3600
            =========  =======

            Run this::

               $ thing --flag

            A literal ``ALTER USER ... SET X =
            FALSE`` that wraps.

            .. mermaid::

               flowchart TD
            ''')
        s = sentences(p)
        joined = " ".join(s)
        self.assertFalse([x for x in s if RESIDUE.search(x)], s)
        for gone in ("widget = Widget", "page-one", "pip install", "--flag", "flowchart",
                     "Connections kept open", "caption", "howto-thing", "recycle", "====="):
            self.assertNotIn(gone, joined)
        self.assertIn("Notes are prose and are kept.", s)
        self.assertIn("Snowflake needs a warehouse.", s)
        self.assertIn("A literal CODE that wraps.", s)
        self.assertIn("Run this:", " ".join(s))
        fact, _ = docs_scan.views(p, [])
        self.assertIn("## How to do a thing", fact)
        self.assertIn("`Widget`", fact)
        self.assertIn("[the guide](https://example.com/guide)", fact)
        self.assertIn("[the intro](intro)", fact)
        self.assertIn("widget = Widget()", fact)
        self.assertIn("$ thing --flag", fact)
        self.assertIn("`pool_size`", fact)
        self.assertIn("| recycle    3600 |", fact)


class MldView(TempDir):
    def test_odoc_markup(self) -> None:
        p = write(self.tmp, "page.mld", r'''
            {0:intro Getting Started}

            Call [Spectrum.printf] with a {b bold} tag, see {!page-quantization} and
            {{:https://ocaml.org/api/Format.html} semantic tags}. Braces \{ are escaped \}.

            {[
            let () = Spectrum.Simple.printf "@{<green>Hi@}@."
            ]}

            {v
            opam install spectrum
            v}

            {ul
            {- First item}
            {- Second {i item}}}

            {1 Next Steps}

            - {!page-custom_palettes} — make a palette

            @since 1.0
            ''')
        s = sentences(p)
        joined = " ".join(s)
        self.assertFalse([x for x in s if RESIDUE.search(x)], s)
        for gone in ("opam install", "Simple.printf", "@since", "make a palette"):
            self.assertNotIn(gone, joined)
        self.assertIn("First item", joined)
        self.assertIn("Second item", joined)
        self.assertIn("Braces { are escaped }.", joined)
        fact, _ = docs_scan.views(p, [])
        self.assertIn("# Getting Started", fact)
        self.assertIn("## Next Steps", fact)
        self.assertIn("[semantic tags](https://ocaml.org/api/Format.html)", fact)
        self.assertIn("`Spectrum.printf`", fact)
        self.assertIn("opam install spectrum", fact)


class ProtectedTerms(TempDir):
    def setUp(self) -> None:
        super().setUp()
        (self.tmp / ".doc-writer").mkdir()
        write(self.tmp / ".doc-writer", "terminology.yaml", '''
            version: 1
            source_terms:
              - canonical: "BeliefStore"
                variants: []
            project_terms:
              - canonical: "single-agent"
                variants: ["single agent", 'belief-holder']
              - canonical: world scope
                variants: []
            overrides: {}
            ''')

    def test_terms_are_read_and_multi_part_ones_kept(self) -> None:
        terms = docs_scan.protected_terms(self.tmp)
        self.assertEqual(sorted(terms), ["belief-holder", "single agent", "single-agent", "world scope"])

    def test_scan_view_masks_terms_outside_code_only(self) -> None:
        p = write(self.tmp, "page.md", '''
            A single-agent design has one belief-holder in the World Scope.

            Code keeps it: `single-agent`.
            ''')
        fact, scan = docs_scan.views(p, docs_scan.protected_terms(self.tmp))
        self.assertIn("A TERM design has one TERM in the TERM.", scan)
        self.assertIn("`single-agent`", scan)
        self.assertIn("single-agent design", fact)

    def test_terms_are_masked_across_line_breaks_and_in_link_labels(self) -> None:
        p = write(self.tmp, "page.md", '''
            Facts in the world
            scope hold for everyone. See [the world scope](scopes.md).
            ''')
        terms = docs_scan.protected_terms(self.tmp)
        _, scan = docs_scan.views(p, terms)
        self.assertNotIn("world", scan.lower())
        self.assertEqual(docs_scan.dropped_terms("the world\nscope", "the world scope", terms), [])

    def test_terms_are_not_matched_across_a_paragraph_break(self) -> None:
        p = write(self.tmp, "page.md", '''
            Every fact lives in the world

            Scope rules come next.
            ''')
        _, scan = docs_scan.views(p, docs_scan.protected_terms(self.tmp))
        self.assertIn("lives in the world", scan)
        self.assertIn("Scope rules", scan)

    def test_compare_reports_dropped_terms_code_and_returns_error(self) -> None:
        page = write(self.tmp, "page.md", '''
            doxastica is single-agent by default. Call `contract()` to retract a belief.
            ''')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(docs_scan.main(["scan", str(page), "--root", str(self.tmp)]), 0)
        page.write_text("doxastica has one agent by default. Retract a belief to drop it.\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = docs_scan.main(["compare", str(page), "--root", str(self.tmp)])
        self.assertEqual(rc, 1, out.getvalue())                    # dropped code span is an error
        self.assertIn("DROPPED code: contract()", out.getvalue())
        self.assertIn("PROTECTED terms used less often: single-agent (1->0)", out.getvalue())
        self.assertRegex(out.getvalue(), r"LIKENESS [\d.-]+ -> [\d.-]+")
        docs_scan.main(["clean", "--root", str(self.tmp)])
        self.assertFalse((self.tmp / ".doc-writer" / ".deslop").exists())

    def test_snapshot_is_taken_once(self) -> None:
        page = write(self.tmp, "page.md", "First version of the page.\n")
        with contextlib.redirect_stdout(io.StringIO()):
            docs_scan.main(["scan", str(page), "--root", str(self.tmp)])
            page.write_text("Second version of the page.\n")
            docs_scan.main(["scan", str(page), "--root", str(self.tmp)])
        snap = docs_scan.snapshot_path(self.tmp, page)
        self.assertEqual(snap.read_text(), "First version of the page.\n")

    def test_compare_without_snapshot_fails(self) -> None:
        page = write(self.tmp, "page.md", "Text.\n")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(docs_scan.main(["compare", str(page), "--root", str(self.tmp)]), 2)


class RealPages(unittest.TestCase):
    """Whole pages from projects documented with doc-writer, one per doc system."""

    def test_no_markup_reaches_the_scanner(self) -> None:
        pages = sorted(FIXTURES.iterdir())
        self.assertEqual({p.suffix for p in pages}, {".md", ".rst", ".mld"})
        for page in pages:
            with self.subTest(page=page.name):
                s = sentences(page)
                self.assertGreater(len(s), 20)
                self.assertFalse([x for x in s if RESIDUE.search(x)], s)

    def test_an_unedited_page_compares_clean(self) -> None:
        for page in sorted(FIXTURES.iterdir()):
            with self.subTest(page=page.name):
                fact, _ = docs_scan.views(page, [])
                res = docs_scan.ci.compare(fact, fact)
                self.assertEqual((res["errors"], res["warnings"]), (0, 0))

    def test_every_code_block_reaches_the_fact_check(self) -> None:
        counts = {
            "semolina-filtering.rst": len(re.findall(r"^\s*\.\. code-block::", (FIXTURES / "semolina-filtering.rst").read_text(), re.M)),
            "spectrum-getting-started.mld": len(re.findall(r"\{\[|\{v\b", (FIXTURES / "spectrum-getting-started.mld").read_text())),
            "poolhouse-configuration.md": len(re.findall(r"^\s*```\w", (FIXTURES / "poolhouse-configuration.md").read_text(), re.M)),
        }
        for name, n in counts.items():
            with self.subTest(page=name):
                fact, _ = docs_scan.views(FIXTURES / name, [])
                self.assertEqual(fact.count("```") // 2, n)


class Vendored(unittest.TestCase):
    def test_vendored_files_match_the_pinned_checksums(self) -> None:
        listed = re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$",
                            (DESLOP / "README.md").read_text(encoding="utf-8"), re.M)
        self.assertGreater(len(listed), 5)
        for rel, digest in listed:
            with self.subTest(file=rel):
                data = (DESLOP / "vendor" / rel).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_sync_script_can_read_the_pin_and_file_list(self) -> None:
        import sync  # noqa: PLC0415

        readme = (DESLOP / "README.md").read_text(encoding="utf-8")
        self.assertRegex(sync.pinned(readme), r"^[0-9a-f]{40}$")
        files = sync.files(readme)
        self.assertIn("scripts/slop_scan.py", files)
        self.assertEqual(sorted(files), sorted(
            str(p.relative_to(DESLOP / "vendor")) for p in (DESLOP / "vendor").rglob("*")
            if p.is_file() and "__pycache__" not in p.parts))

    def test_sync_resolves_only_the_exact_branch_or_tag(self) -> None:
        import sync  # noqa: PLC0415

        a, b, c, d = "a" * 40, "b" * 40, "c" * 40, "d" * 40
        branches = f"{a}\trefs/heads/main\n{b}\trefs/heads/renovate/main\n"
        self.assertEqual(sync.pick_sha("main", branches), a)
        self.assertEqual(sync.pick_sha("main", f"{b}\trefs/heads/renovate/main\n{a}\trefs/heads/main\n"), a)
        tags = f"{c}\trefs/tags/v1.0\n{d}\trefs/tags/v1.0^{{}}\n"
        self.assertEqual(sync.pick_sha("v1.0", tags), d)  # annotated tag: the commit, not the tag object
        self.assertEqual(sync.pick_sha("v1.0", f"{c}\trefs/tags/v1.0\n"), c)  # lightweight tag
        with self.assertRaises(SystemExit):
            sync.pick_sha("main", f"{b}\trefs/heads/renovate/main\n")

    def test_docs_genre_switches_off_vocabulary_checks(self) -> None:
        docs = docs_scan.ss.GENRE_OVERRIDES["docs"]
        self.assertIsNone(docs["hyphen_compounds"]["warn_above"])
        self.assertIsNone(docs["repeated_ngrams"]["warn_above"])


if __name__ == "__main__":
    unittest.main()
