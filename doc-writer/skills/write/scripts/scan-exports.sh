#!/bin/bash
# scan-exports.sh -- scan source code for exported symbols
# Usage: scan-exports.sh <source_root> <language>
# Output: exported symbols grouped by category, one per line in file:line:symbol format

SOURCE_ROOT="${1:-.}"
LANG="${2:-unknown}"

# Skip common non-source directories
EXCLUDE="--exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=.git --exclude-dir=dist --exclude-dir=build --exclude-dir=test --exclude-dir=tests --exclude-dir=spec --exclude-dir=target"

case "$LANG" in
  python)
    echo "## Python Exports (from __all__)"
    grep -rn '__all__\s*=' "$SOURCE_ROOT" --include="*.py" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## Python Public Functions"
    grep -rn '^def [^_]' "$SOURCE_ROOT" --include="*.py" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## Python Public Classes"
    grep -rn '^class [^_]' "$SOURCE_ROOT" --include="*.py" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## Python Public Constants"
    grep -rn '^[A-Z][A-Z_]*\s*=' "$SOURCE_ROOT" --include="*.py" $EXCLUDE 2>/dev/null || true
    ;;
  typescript|javascript)
    echo "## TypeScript/JavaScript Exports"
    grep -rn '^export ' "$SOURCE_ROOT" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" --include="*.mts" --include="*.mjs" $EXCLUDE 2>/dev/null || true
    ;;
  rust)
    echo "## Rust Public Items"
    grep -rn '^pub ' "$SOURCE_ROOT" --include="*.rs" $EXCLUDE 2>/dev/null || true
    ;;
  go)
    echo "## Go Exported Functions"
    grep -rn '^func [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## Go Exported Types"
    grep -rn '^type [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## Go Exported Variables"
    grep -rn '^var [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## Go Exported Constants"
    grep -rn '^const [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE 2>/dev/null || true
    ;;
  ocaml)
    echo "## OCaml Public Values"
    grep -rn '^val ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## OCaml Type Declarations"
    grep -rn '^type ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## OCaml Module Declarations"
    grep -rn '^module ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
    echo ""
    echo "## OCaml Exception Declarations"
    grep -rn '^exception ' "$SOURCE_ROOT" --include="*.mli" $EXCLUDE 2>/dev/null || true
    ;;
  *)
    echo "Language '$LANG' not directly supported for export scanning."
    echo "Claude will scan source files manually to identify exported symbols."
    ;;
esac
