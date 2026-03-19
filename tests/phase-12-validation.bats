#!/usr/bin/env bats

# Phase 12: Add Odoc Framework for OCaml Projects
# Validation tests for P12-01 through P12-08

PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"

# ---------------------------------------------------------------------------
# P12-01: odoc.qa.md exists with Detection section and 3 questions
# ---------------------------------------------------------------------------

@test "P12-01: odoc.qa.md exists with Detection section and 3 questions" {
  local file="$PROJECT_ROOT/doc-writer/skills/setup/defaults/odoc.qa.md"
  [ -f "$file" ]
  grep -q "## Detection" "$file"
  grep -q "Config file:" "$file"
  grep -q "## Question 1:" "$file"
  grep -q "## Question 2:" "$file"
  grep -q "## Question 3:" "$file"
}

# ---------------------------------------------------------------------------
# P12-02: odoc.md exists with all required sections
# ---------------------------------------------------------------------------

@test "P12-02: odoc.md exists with all required sections" {
  local file="$PROJECT_ROOT/doc-writer/skills/setup/defaults/odoc.md"
  [ -f "$file" ]
  grep -q "## Code Blocks" "$file"
  grep -q "## .mld File Structure" "$file" || grep -q "## .mld file structure" "$file" || grep -q "mld File" "$file"
  grep -q "## .mli Doc Comments" "$file" || grep -q "## .mli doc comments" "$file" || grep -q "mli Doc" "$file"
  grep -q "Cross-Refer" "$file"
  grep -q "Dune Wiring" "$file" || grep -q "dune wiring" "$file" || grep -q "Dune" "$file"
  grep -q "Multi-Package" "$file" || grep -q "multi-package" "$file" || grep -q "Multi-Library" "$file"
  grep -q "Build Validation" "$file" || grep -q "build validation" "$file" || grep -q "dune build @doc" "$file"
  grep -q "Quality Checklist" "$file" || grep -q "quality checklist" "$file" || grep -q "Checklist" "$file"
}

# ---------------------------------------------------------------------------
# P12-03: scaffolds/odoc/ directory exists with template files
# ---------------------------------------------------------------------------

@test "P12-03: scaffolds/odoc/ directory exists with template files" {
  local dir="$PROJECT_ROOT/doc-writer/skills/setup/defaults/scaffolds/odoc"
  [ -d "$dir" ]
  [ -f "$dir/doc_dune.sexp" ]
  [ -f "$dir/index.mld" ]
  [ -f "$dir/secondary_dune.sexp" ]
  [ -f "$dir/secondary_index.mld" ]
}

# ---------------------------------------------------------------------------
# P12-04: SKILL.md lists odoc as selectable built-in option
# ---------------------------------------------------------------------------

@test "P12-04: SKILL.md lists odoc as selectable built-in option" {
  local file="$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
  grep -q 'label: "odoc"' "$file" || grep -q "label: \"odoc\"" "$file"
}

# ---------------------------------------------------------------------------
# P12-05: odoc.md contains cross-reference syntax rules
# ---------------------------------------------------------------------------

@test "P12-05: odoc.md contains cross-reference syntax rules" {
  local file="$PROJECT_ROOT/doc-writer/skills/setup/defaults/odoc.md"
  [ -f "$file" ]
  grep -q '{!Module.value}' "$file" || grep -q '{!page-' "$file"
  grep -q 'cross-package' "$file" || grep -q 'Cross-Package' "$file" || grep -q 'Cross-package' "$file"
  grep -q 'HTML' "$file"
}

# ---------------------------------------------------------------------------
# P12-06: odoc.md contains quality checklist
# ---------------------------------------------------------------------------

@test "P12-06: odoc.md contains quality checklist" {
  local file="$PROJECT_ROOT/doc-writer/skills/setup/defaults/odoc.md"
  [ -f "$file" ]
  grep -q '\- \[ \]' "$file"
  grep -q 'dune build @doc' "$file"
}

# ---------------------------------------------------------------------------
# P12-07: odoc.qa.md Q3 includes follow-on sub-topic structure
# ---------------------------------------------------------------------------

@test "P12-07: odoc.qa.md Q3 includes follow-on sub-topic structure" {
  local file="$PROJECT_ROOT/doc-writer/skills/setup/defaults/odoc.qa.md"
  [ -f "$file" ]
  grep -q "Follow-on" "$file" || grep -q "follow-on" "$file"
  grep -q "sub-topic" "$file" || grep -q "Sub-topic" "$file"
  grep -q "dynamically" "$file" || grep -q "scan" "$file"
}

# ---------------------------------------------------------------------------
# P12-08: SKILL.md built-in frameworks list includes odoc
# ---------------------------------------------------------------------------

@test "P12-08: SKILL.md built-in frameworks list includes odoc" {
  local file="$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
  grep -q "odoc" "$file"
  grep -q 'mkdocs-material.*plain-markdown.*sphinx-shibuya.*odoc' "$file" || \
  grep -q 'odoc' "$file"
}
