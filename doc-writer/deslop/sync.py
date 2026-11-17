#!/usr/bin/env python3
"""sync: update the vendored deslop files from upstream.

    python3 doc-writer/deslop/sync.py               # latest commit on upstream main
    python3 doc-writer/deslop/sync.py --ref v1.2.0  # a branch, tag or commit SHA
    python3 doc-writer/deslop/sync.py --check       # only report whether upstream has moved

The files to sync are the ones listed in README.md's checksum table, so adding a file there (and
running this) is how to vendor one more. The script downloads each file at the resolved commit,
writes it to vendor/, and rewrites the pinned commit and the checksum table in README.md. It
prints which files changed, so you can read upstream's changes before committing.

Afterwards, run the tests and scan a few real pages (see README.md, "Updating").
Needs git (to resolve the ref) and network access to github.com. Standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import pathlib
import re
import subprocess
import sys
import urllib.request

UPSTREAM = "https://github.com/etodanik/deslop"
RAW = "https://raw.githubusercontent.com/etodanik/deslop/{sha}/{path}"
HERE = pathlib.Path(__file__).resolve().parent
README = HERE / "README.md"
VENDOR = HERE / "vendor"

PIN_RE = re.compile(r"^- Commit: `([0-9a-f]{40})` \((\d{4}-\d{2}-\d{2})\)$", re.M)
ROW_RE = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", re.M)


def pinned(readme: str) -> str:
    m = PIN_RE.search(readme)
    if not m:
        raise SystemExit("README.md has no '- Commit: `<sha>` (<date>)' line")
    return m.group(1)


def files(readme: str) -> list[str]:
    rows = [path for path, _ in ROW_RE.findall(readme)]
    if not rows:
        raise SystemExit("README.md has no checksum table")
    return rows


def resolve(ref: str) -> str:
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return ref
    out = subprocess.run(["git", "ls-remote", UPSTREAM, ref, f"refs/tags/{ref}^{{}}"],
                         capture_output=True, text=True, check=True).stdout
    shas = [line.split()[0] for line in out.splitlines() if line.strip()]
    if not shas:
        raise SystemExit(f"{ref!r} is not a branch, tag or full commit SHA in {UPSTREAM}")
    return shas[-1]  # a peeled annotated tag (^{}) sorts last and names the commit


def fetch(sha: str, path: str) -> bytes:
    with urllib.request.urlopen(RAW.format(sha=sha, path=path), timeout=60) as r:
        return r.read()


def github_output(**values: str) -> None:
    """In GitHub Actions, also hand the result to later steps."""
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.writelines(f"{k}={v}\n" for k, v in values.items())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", default="main", help="upstream branch, tag or commit SHA (default: main)")
    ap.add_argument("--check", action="store_true", help="report whether upstream moved; change nothing")
    a = ap.parse_args(argv)

    readme = README.read_text(encoding="utf-8")
    old = pinned(readme)
    sha = resolve(a.ref)
    if sha == old:
        print(f"Up to date: vendored deslop is {old[:7]}, which is {a.ref}.")
        return 0
    print(f"Upstream {a.ref} is {sha[:7]}; vendored is {old[:7]}.")
    print(f"Upstream changes: {UPSTREAM}/compare/{old}...{sha}")
    if a.check:
        return 1

    digests: dict[str, str] = {}
    changed: list[str] = []
    for rel in files(readme):
        data = fetch(sha, rel)  # vendor/ mirrors upstream's layout
        dest = VENDOR / rel
        if not dest.exists() or dest.read_bytes() != data:
            changed.append(rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        digests[rel] = hashlib.sha256(data).hexdigest()

    readme = ROW_RE.sub(lambda m: f"| `{m.group(1)}` | `{digests[m.group(1)]}` |", readme)
    today = datetime.date.today().isoformat()
    readme = PIN_RE.sub(f"- Commit: `{sha}` ({today})", readme)
    README.write_text(readme, encoding="utf-8")

    print(f"Pinned {sha[:7]}. Files changed: {', '.join(changed) or 'none'}.")
    github_output(old=old, new=sha, changed=" ".join(changed), compare=f"{UPSTREAM}/compare/{old}...{sha}")
    if changed:
        print("Next: read the upstream diff above, run `python3 -m unittest discover -s tests/deslop`,"
              " and scan a few real pages with docs_scan.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
