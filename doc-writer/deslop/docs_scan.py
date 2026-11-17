#!/usr/bin/env python3
"""docs_scan: run the vendored deslop scanner and fact check on documentation pages.

deslop's scanner reads Markdown. Documentation pages also carry markup it does not
know: YAML frontmatter, MkDocs admonitions and content tabs, reStructuredText
directives and roles, and odoc markup. This wrapper turns a page into a Markdown
*view* for the scanner and never writes that view back to the page. The editor
edits the real file; the view exists only for the length of a scan.

    python3 docs_scan.py scan PAGE [--root DIR]      # flags for one page
    python3 docs_scan.py compare PAGE [--root DIR]   # regressions + fact check vs the snapshot
    python3 docs_scan.py view PAGE [--masked]        # print the Markdown view (debugging)
    python3 docs_scan.py clean [--root DIR]          # delete all snapshots

`scan` saves a snapshot of the page the first time it sees it, in
DIR/.doc-writer/.deslop/. `compare` checks the current page against that
snapshot, so take the first scan before editing. `clean` removes the snapshots.

Protected terms. Terms listed in DIR/.doc-writer/terminology.yaml (every
`canonical` and `variants` entry) are masked as TERM in the scanned text, so the
scanner cannot flag a project's own vocabulary. `compare` reports any protected
term the revision uses less often than the snapshot did.

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor" / "scripts"))

import check_invariants as ci  # noqa: E402
import slop_scan as ss  # noqa: E402

# Docs-genre changes to deslop's thresholds. hyphen_compounds and repeated_ngrams
# fire on a project's technical vocabulary ("single-agent", "belief state"), which
# docs must repeat word for word, so they are switched off for docs.
DOCS_OVERRIDES = {
    "hyphen_compounds": {"warn_above": None},
    "repeated_ngrams": {"warn_above": None},
}
ss.GENRE_OVERRIDES.setdefault("docs", {}).update(DOCS_OVERRIDES)

GENRE = "docs"
SELF = "claude"
SNAPSHOT_DIR = pathlib.Path(".doc-writer") / ".deslop"
TERM = "TERM"


# --------------------------------------------------------------------------
# Placeholders: code and links are lifted out while markup is rewritten, so
# rewrites never touch them, and put back at the end.
# --------------------------------------------------------------------------

class Stash:
    def __init__(self) -> None:
        self.items: list[str] = []

    def put(self, s: str) -> str:
        self.items.append(s)
        return f"\x00{len(self.items) - 1}\x00"

    def restore(self, text: str, links_as_text: bool = False) -> str:
        def item(m: re.Match[str]) -> str:
            s = self.items[int(m.group(1))]
            lm = re.fullmatch(r"\[(.*)\]\((.*)\)", s, flags=re.S) if links_as_text else None
            return lm.group(1) if lm else s

        for _ in range(5):  # stashed items can contain other placeholders
            new = re.sub(r"\x00(\d+)\x00", item, text)
            if new == text:
                break
            text = new
        return text


def fence(body: str, stash: Stash) -> str:
    lines = [ln.rstrip() for ln in body.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n" + stash.put("```\n" + "\n".join(dedent(lines)) + "\n```") + "\n"


def inline_code(s: str, stash: Stash) -> str:
    s = s.replace("`", "'").strip()
    return stash.put(f"`{s}`") if s else ""


def link(label: str, target: str, stash: Stash) -> str:
    return stash.put(f"[{label.strip()}]({target.strip()})")


def dedent(lines: list[str]) -> list[str]:
    ind = [len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()]
    n = min(ind) if ind else 0
    return [ln[n:] for ln in lines]


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip())


# --------------------------------------------------------------------------
# Markdown (MkDocs Material, plain Markdown)
# --------------------------------------------------------------------------

def md_to_view(text: str, stash: Stash) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)            # YAML frontmatter
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)                    # HTML comments
    # fenced code (``` or ~~~, any indent) -> stashed ``` fence
    text = re.sub(r"(?ms)^([ \t]*)(`{3,}|~{3,})[^\n]*\n(.*?)^[ \t]*\2[ \t]*$",
                  lambda m: fence(m.group(3), stash), text)
    # inline code: any run of backticks, may wrap onto the next line (not across paragraphs)
    text = re.sub(r"(?<!`)(`+)(?!`)((?:(?!\n\s*\n).)+?)(?<!`)\1(?!`)",
                  lambda m: inline_code(" ".join(m.group(2).split()), stash), text, flags=re.S)
    # links: inline, reference-style / mkdocs autorefs, definitions
    text = re.sub(r"(?<!!)\[([^\]\n]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)",
                  lambda m: link(m.group(1), m.group(2), stash), text)
    text = re.sub(r"(?<!!)\[([^\]\n]+)\]\[([^\]\n]*)\]",
                  lambda m: link(m.group(1), m.group(2) or m.group(1), stash), text)
    text = re.sub(r"(?m)^\s*\[([^\]\n]+)\]:\s*(\S+).*$",
                  lambda m: "| " + link(m.group(1), m.group(2), stash) + " |", text)
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        m = re.match(r"^(?:!!!|\?\?\?\+?)\s*[\w-]+(?:\s+[\w-]+)*\s*(?:\"(.*)\")?\s*$", s)
        if m:                                             # admonition: keep its title as a heading
            out.append(f"#### {m.group(1)}" if m.group(1) else "")
            continue
        m = re.match(r'^===\+?\s+"(.*)"\s*$', s)
        if m:                                             # content tab label
            out.append(f"#### {m.group(1)}")
            continue
        if re.match(r"^(:::\s|--8<--|\{[:.#])", s) or re.match(r"^</?[A-Za-z][^>]*>\s*$", s):
            out.append("")                                # mkdocstrings, snippets, attr lists, raw HTML
            continue
        out.append(ln[4:] if ln.startswith("    ") and not s.startswith("\x00") else ln)
    return "\n".join(out)


# --------------------------------------------------------------------------
# reStructuredText (Sphinx)
# --------------------------------------------------------------------------

RST_CODE = {"code-block", "code", "sourcecode", "parsed-literal", "doctest", "testcode",
            "testoutput", "math", "productionlist", "prompt", "jupyter-execute", "ipython"}
RST_PROSE = {"note", "warning", "tip", "important", "caution", "attention", "danger", "error",
             "hint", "seealso", "admonition", "topic", "sidebar", "versionadded",
             "versionchanged", "deprecated", "versionremoved", "tab-set", "tab-item", "tabs",
             "tab", "group-tab", "grid", "grid-item", "grid-item-card", "card", "dropdown",
             "container", "only", "rst-class", "glossary", "epigraph", "highlights",
             "pull-quote", "compound", "centered", "hlist", "rubric", "div"}
RST_TITLED = {"admonition", "topic", "sidebar", "tab-item", "tab", "group-tab", "card",
              "grid-item-card", "dropdown", "rubric"}
RST_TABLE = {"list-table", "csv-table", "table"}
PUNCT_LINE = re.compile(r"""^([=\-~^"'`#*+:._!$%&,/;<>?@\\|])\1{2,}\s*$""")
PY_ROLE = re.compile(r"^(py:|c:|cpp:|js:)?(class|func|meth|attr|mod|exc|data|obj|const|"
                     r"function|member|type|macro|struct|var|enum|enumerator)$")


def rst_inline(text: str, stash: Stash) -> str:
    text = re.sub(r"``(.+?)``", lambda m: inline_code(m.group(1), stash), text)

    def role(m: re.Match[str]) -> str:
        name, body = m.group(1), m.group(2)
        lm = re.fullmatch(r"(.*?)\s*<([^<>]+)>", body, flags=re.S)
        label, target = (lm.group(1), lm.group(2)) if lm else (None, body)
        if name in ("ref", "doc", "any", "numref", "download"):
            return link(label or inline_code(target, stash), target, stash)
        if name == "term":
            return label or target
        if PY_ROLE.match(name):
            t = (label or target).lstrip("!")
            if t.startswith("~"):
                t = t[1:].split(".")[-1]
            return inline_code(t, stash)
        if name in ("emphasis", "strong", "dfn", "abbr", "guilabel", "menuselection"):
            return label or target
        return inline_code(label or target, stash)        # kbd, file, command, samp, envvar, math, ...

    text = re.sub(r":([\w:+-]+):`(.+?)`", role, text, flags=re.S)
    text = re.sub(r"`([^`<>]+?)\s*<([^<>`]+)>`__?", lambda m: link(m.group(1), m.group(2), stash), text)
    text = re.sub(r"`([^`]+)`__?", r"\1", text)                     # named reference
    text = re.sub(r"`([^`\n]+)`", lambda m: inline_code(m.group(1), stash), text)  # default role
    return text


def rst_open_markup(line: str) -> bool:
    """True if the line opens a ``literal`` or `reference` it does not close."""
    return line.count("``") % 2 == 1 or line.replace("``", "").count("`") % 2 == 1


def rst_block(lines: list[str], stash: Stash) -> list[str]:
    out: list[str] = []
    i, n = 0, len(lines)

    def body_end(start: int, base: int) -> int:
        j = start
        while j < n and (not lines[j].strip() or indent_of(lines[j]) > base):
            j += 1
        return j

    while i < n:
        ln = lines[i]
        s = ln.strip()
        ind = indent_of(ln)
        # explicit markup: directives, comments, targets, footnotes, substitutions
        if s.startswith(".. ") or s == "..":
            m = re.match(r"^\.\.\s+(?:\|[^|]+\|\s+)?([\w:-]+)::\s*(.*)$", s)
            j = i + 1
            opts_end = j
            while opts_end < n and lines[opts_end].strip().startswith(":") and indent_of(lines[opts_end]) > ind:
                opts_end += 1
            end = body_end(opts_end, ind)
            body = lines[opts_end:end]
            if m:
                name, arg = m.group(1).split(":")[-1], m.group(2).strip()
                if name in RST_CODE:
                    out.append(fence("\n".join(body), stash))
                elif name in RST_TABLE:
                    for b in body:
                        cell = re.sub(r"^\s*(\*\s+-|-|\*)\s+", "", b).strip()
                        if cell:
                            out.append("| " + rst_inline(cell, stash) + " |")
                    out.append("")
                elif name in RST_PROSE:
                    if arg and name in RST_TITLED:
                        out += ["", "#### " + rst_inline(arg, stash), ""]
                    elif arg and name not in ("versionadded", "versionchanged", "deprecated",
                                              "versionremoved", "only", "rst-class", "grid",
                                              "tab-set", "container", "hlist"):
                        out += ["", rst_inline(arg, stash), ""]
                    out += rst_block(dedent(body), stash)
                    out.append("")
                # anything else (toctree, autodoc, image, raw, include, mermaid, ...) is dropped
            # comments, targets and footnote/citation bodies are dropped too
            i = end
            continue
        # section title with overline
        if PUNCT_LINE.match(s) and i + 2 < n and lines[i + 1].strip() and PUNCT_LINE.match(lines[i + 2].strip()):
            out += ["## " + rst_inline(lines[i + 1].strip(), stash), ""]
            i += 3
            continue
        # section title with underline
        if s and not PUNCT_LINE.match(s) and i + 1 < n and PUNCT_LINE.match(lines[i + 1].strip()) \
                and len(lines[i + 1].strip()) >= len(s) and ind == 0:
            out += ["## " + rst_inline(s, stash), ""]
            i += 2
            continue
        if PUNCT_LINE.match(s) and len(s) >= 4:            # transition
            out.append("")
            i += 1
            continue
        # literal block introduced by "::"
        if s.endswith("::"):
            intro = re.sub(r"\s*::$", "", ln) if (s == "::" or s.endswith(" ::")) else ln[:-1]
            if intro.strip():
                out.append(rst_inline(intro, stash))
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n and indent_of(lines[j]) > ind:
                end = body_end(j, ind)
                out.append(fence("\n".join(lines[j:end]), stash))
                i = end
            else:
                i += 1
            continue
        ln = re.sub(r"^(\s*)#\.\s", r"\g<1>1. ", ln)          # auto-enumerated list
        # inline markup can wrap onto the next line: join lines until backticks pair up
        j = i + 1
        while rst_open_markup(ln) and j < n and lines[j].strip():
            ln += " " + lines[j].strip()
            j += 1
        out.append(rst_inline(ln, stash))
        i = j
    return out


def rst_to_view(text: str, stash: Stash) -> str:
    return "\n".join(rst_block(text.replace("\r\n", "\n").split("\n"), stash))


# --------------------------------------------------------------------------
# odoc (.mld)
# --------------------------------------------------------------------------

def mld_inline_code(text: str, stash: Stash) -> str:
    """odoc inline code is [ ... ] with balanced brackets."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            out.append(text[i:i + 2])
            i += 2
            continue
        if c == "[" and not (i > 0 and text[i - 1] in "{@"):
            depth, j = 1, i + 1
            while j < n and depth:
                if text[j] == "\\":
                    j += 2
                    continue
                depth += {"[": 1, "]": -1}.get(text[j], 0)
                j += 1
            if depth == 0:
                out.append(inline_code(text[i + 1:j - 1].replace("\n", " "), stash))
                i = j
                continue
        out.append(c)
        i += 1
    return "".join(out)


def mld_ref(target: str) -> str:
    t = re.sub(r"^(page|module|val|type|section|class|exception|modtype|label)-", "", target.strip())
    return t.split(".")[-1] if "." in t else t


def mld_to_view(text: str, stash: Stash) -> str:
    text = text.replace("\r\n", "\n")
    for a, b in (("\\{", "\x01"), ("\\}", "\x02"), ("\\[", "\x03"), ("\\]", "\x04"), ("\\@", "@")):
        text = text.replace(a, b)
    text = re.sub(r"\{v\b(.*?)\bv\}", lambda m: fence(m.group(1), stash), text, flags=re.S)
    text = re.sub(r"\{(?:@[\w-]+(?:\[[^\]]*\])?)?\[(.*?)\]\}", lambda m: fence(m.group(1), stash),
                  text, flags=re.S)
    text = re.sub(r"\{%.*?%\}", "", text, flags=re.S)                     # raw backend markup
    text = re.sub(r"\{!(?:modules|indexlist)\b[^}]*\}", "", text)          # generated listings
    text = mld_inline_code(text, stash)
    text = re.sub(r"(?m)^\s*@\w+.*$", "", text)                            # @author, @since, ...
    rules = [
        (r"\{\{:([^}\s]+)\}\s*([^{}]*)\}", lambda m: link(m.group(2), m.group(1), stash)),
        (r"\{\{!([^}\s]+)\}\s*([^{}]*)\}", lambda m: link(m.group(2), m.group(1), stash)),
        (r"\{:([^}\s]+)\}", lambda m: link(m.group(1), m.group(1), stash)),
        (r"\{!([^}\s]+)\}", lambda m: link(inline_code(mld_ref(m.group(1)), stash), m.group(1), stash)),
        (r"\{([0-5])(?::[\w-]+)?\s+([^{}]*)\}", lambda m: "\n" + "#" * (int(m.group(1)) + 1) + " "
         + " ".join(m.group(2).split()) + "\n"),
        (r"\{(?:b|i|e|em|\^|_)\s+([^{}]*)\}", lambda m: m.group(1)),
        (r"\{(?:-|li)\s+([^{}]*)\}", lambda m: "\n- " + " ".join(m.group(1).split()) + "\n"),
        (r"\{(?:ul|ol)\s*([^{}]*)\}", lambda m: "\n" + m.group(1) + "\n"),
        (r"\{t(?:able)?\s*([^{}]*)\}", lambda m: "\n" + m.group(1) + "\n"),
        (r"\{(?:tr|th|td)\s*([^{}]*)\}", lambda m: "| " + " ".join(m.group(1).split()) + " |\n"),
        (r"\{(?:math|m)\s+([^{}]*)\}", lambda m: inline_code(m.group(1), stash)),
    ]
    for _ in range(20):
        before = text
        for pat, rep in rules:
            text = re.sub(pat, rep, text, flags=re.S)
        if text == before:
            break
    text = text.replace("\x01", "{").replace("\x02", "}").replace("\x03", "[").replace("\x04", "]")
    return re.sub(r"\n{3,}", "\n\n", text)


# --------------------------------------------------------------------------
# Views, protected terms, snapshots
# --------------------------------------------------------------------------

def fmt_of(path: pathlib.Path) -> str:
    ext = path.suffix.lower()
    if ext in (".rst", ".rest"):
        return "rst"
    if ext == ".mld":
        return "mld"
    return "md"


def protected_terms(root: pathlib.Path) -> list[str]:
    """Every canonical form and variant in .doc-writer/terminology.yaml (no YAML library needed)."""
    p = root / ".doc-writer" / "terminology.yaml"
    if not p.is_file():
        return []
    raw = p.read_text(encoding="utf-8")
    terms: set[str] = set()
    for m in re.finditer(r"^\s*-?\s*canonical:\s*(\"[^\"]*\"|'[^']*'|[^\n#]+)", raw, flags=re.M):
        terms.add(m.group(1).strip().strip("\"'"))
    for m in re.finditer(r"^\s*variants:\s*\[(.*?)\]", raw, flags=re.M | re.S):
        for v in re.findall(r"\"([^\"]+)\"|'([^']+)'|([^,\s][^,]*)", m.group(1)):
            terms.add(next(x for x in v if x).strip())
    # a term is worth masking only if it has more than one word part (single words are
    # rarely flagged, and masking common words would hide real problems)
    return sorted((t for t in terms if t and re.search(r"[\s-]", t)), key=len, reverse=True)


def mask(view: str, terms: list[str]) -> str:
    if not terms:
        return view
    pat = re.compile(r"(?<![\w-])(?:" + "|".join(re.escape(t) for t in terms) + r")(?![\w-])", re.I)
    # only prose is masked: code and links are still stashed when this runs
    return pat.sub(TERM, view)


def views(path: pathlib.Path, terms: list[str]) -> tuple[str, str]:
    """(fact-check view, scan view) of a page. Both are Markdown; the scan view masks terms
    and shows links as their labels."""
    text = path.read_text(encoding="utf-8")
    stash = Stash()
    conv = {"md": md_to_view, "rst": rst_to_view, "mld": mld_to_view}[fmt_of(path)]
    view = conv(text, stash)

    # "- [Page](target): what it covers" is navigation, not prose. As a table row the
    # scanner skips it, while the fact check still sees the link.
    view = re.sub(r"(?m)^(\s*)(?:[-*+]|\d+[.)])\s+(\x00(\d+)\x00)(.*)$",
                  lambda m: (m.group(1) + "| " + m.group(2) + m.group(4) + " |")
                  if stash.items[int(m.group(3))].startswith("[") else m.group(0), view)
    view = re.sub(r"\n{3,}", "\n\n", view)
    # The scan view shows a link as its label, which is what the scanner reduces it to anyway.
    # Left as Markdown, a URL followed by ")" can make the scanner's link pattern swallow the
    # text up to the next link.
    return stash.restore(view), stash.restore(mask(view, terms), links_as_text=True)


def make_doc(scan_view: str, fact_view: str) -> ss.Doc:
    d = ss.Doc(scan_view)
    d.raw = fact_view          # check_invariants reads .raw: give it the unmasked view
    return d


def snapshot_path(root: pathlib.Path, page: pathlib.Path) -> pathlib.Path:
    rel = str(page.resolve())
    digest = hashlib.sha1(rel.encode()).hexdigest()[:10]
    return root / SNAPSHOT_DIR / f"{page.stem}-{digest}{page.suffix}"


def cmd_scan(page: pathlib.Path, root: pathlib.Path) -> int:
    snap = snapshot_path(root, page)
    if not snap.exists():
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(page, snap)
    fact, scan = views(page, protected_terms(root))
    d = make_doc(scan, fact)
    names = list(ss.METRICS)
    results = {n: ss.run_metric(n, d, None, {}, None) for n in names}
    flags = {n: ss.flag(n, results[n], GENRE) for n in names}
    print(f"[{page}]  (prose view: CODE = code span, {TERM} = protected term)")
    print(ss.agent_report(d, results, flags, SELF))
    return 0


def cmd_compare(page: pathlib.Path, root: pathlib.Path) -> int:
    snap = snapshot_path(root, page)
    if not snap.exists():
        print(f"no snapshot for {page}: run `scan` before editing", file=sys.stderr)
        return 2
    terms = protected_terms(root)
    # the snapshot keeps the page's extension, so it is converted the same way
    bf, bs = views(snap, terms)
    af, as_ = views(page, terms)
    before, after = make_doc(bs, bf), make_doc(as_, af)
    names = list(ss.METRICS)
    text, data = ss.regression_report(before, after, names, GENRE, {}, None)
    tb = {t["term"] for t in ss.own_family_tells(before, SELF, top=200)}
    added = [t for t in ss.own_family_tells(after, SELF, top=200) if t["term"] not in tb]
    text += f"\nSELF ({SELF}) tells ADDED by the revision: {len(added)}"
    text += "".join(f"\n  '{t['term']}' {t['ratio'] or 'inf'}x in " + ", ".join(f"s{i}" for i in t["sentences"])
                    for t in added[:12])
    lost = dropped_terms(bf, af, terms)
    if lost:
        text += "\nPROTECTED terms used less often: " + ", ".join(f"{t} ({b}->{a})" for t, b, a in lost)
    print(f"[{page}]")
    print(text)
    return 1 if data.get("invariants", {}).get("errors") else 0


def dropped_terms(before: str, after: str, terms: list[str]) -> list[tuple[str, int, int]]:
    """Protected terms that occur fewer times after the revision than before it."""
    out = []
    for t in terms:
        pat = re.compile(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", re.I)
        b, a = len(pat.findall(before)), len(pat.findall(after))
        if a < b:
            out.append((t, b, a))
    return out


def cmd_view(page: pathlib.Path, root: pathlib.Path, masked: bool) -> int:
    fact, scan = views(page, protected_terms(root))
    print(scan if masked else fact)
    return 0


def cmd_clean(root: pathlib.Path) -> int:
    shutil.rmtree(root / SNAPSHOT_DIR, ignore_errors=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["scan", "compare", "view", "clean"])
    ap.add_argument("page", nargs="?", help="documentation page (.md, .rst or .mld)")
    ap.add_argument("--root", default=".", help="project root holding .doc-writer/ (default: .)")
    ap.add_argument("--masked", action="store_true", help="view: show the scan view, with terms masked")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    if a.command == "clean":
        return cmd_clean(root)
    if not a.page:
        ap.error(f"{a.command} needs a page")
    page = pathlib.Path(a.page)
    if a.command == "scan":
        return cmd_scan(page, root)
    if a.command == "compare":
        return cmd_compare(page, root)
    return cmd_view(page, root, a.masked)


if __name__ == "__main__":
    sys.exit(main())
