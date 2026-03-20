#!/usr/bin/env bats

# Phase 13: Scaffold Variable Substitution Fix and Doc-Researcher Improvements
# Validation tests for P11-03, MISSING-01, MISSING-02

PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"

# ---------------------------------------------------------------------------
# P11-03: SKILL.md handles all sphinx-shibuya template variables
# ---------------------------------------------------------------------------

@test "P11-03: SKILL.md Step 2b.3 references {project_name} variable" {
  grep -q '{project_name}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 references {author_name} variable" {
  grep -q '{author_name}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 references {copyright_year} variable" {
  grep -q '{copyright_year}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 references {github_url} variable" {
  grep -q '{github_url}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 has git config inference for author" {
  grep -q 'git config user.name' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 has current year inference for copyright" {
  grep -qi 'current year' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 has git remote inference for github_url" {
  grep -q 'git remote' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

# ---------------------------------------------------------------------------
# MISSING-01: doc-researcher WebFetch in tools
# ---------------------------------------------------------------------------

@test "MISSING-01: doc-researcher tools frontmatter includes WebFetch" {
  grep -q 'WebFetch' "$PROJECT_ROOT/doc-writer/agents/doc-researcher.md"
}

# ---------------------------------------------------------------------------
# MISSING-02: doc-researcher Framework Preferences expanded
# ---------------------------------------------------------------------------

@test "MISSING-02: Framework Preferences not gated on mkdocs-material/plain-markdown" {
  ! grep -q "mkdocs-material.*or.*plain-markdown" "$PROJECT_ROOT/doc-writer/agents/doc-researcher.md"
}

@test "MISSING-02: Framework Preferences references framework config file generically" {
  grep -q 'framework config file' "$PROJECT_ROOT/doc-writer/agents/doc-researcher.md"
}
