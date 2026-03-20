#!/usr/bin/env bats
# Phase 7 — Doc-Writer Plugin Packaging
# Structural validation for PKG-01 through PKG-08

setup() {
  PROJECT_ROOT="/Users/paul/Documents/Dev/Personal/doc-writer-agent"
}

# ---------------------------------------------------------------------------
# PKG-01: doc-writer/ directory exists with correct top-level structure
# ---------------------------------------------------------------------------

@test "PKG-01: doc-writer/ directory exists" {
  [ -d "${PROJECT_ROOT}/doc-writer" ]
}

@test "PKG-01: doc-writer/skills/ directory exists" {
  [ -d "${PROJECT_ROOT}/doc-writer/skills" ]
}

@test "PKG-01: doc-writer/agents/ directory exists" {
  [ -d "${PROJECT_ROOT}/doc-writer/agents" ]
}

@test "PKG-01: doc-writer/.claude-plugin/ directory exists" {
  [ -d "${PROJECT_ROOT}/doc-writer/.claude-plugin" ]
}

# ---------------------------------------------------------------------------
# PKG-02: plugin.json exists and declares name: "doc-writer"
# ---------------------------------------------------------------------------

@test "PKG-02: doc-writer/.claude-plugin/plugin.json exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/.claude-plugin/plugin.json" ]
}

@test "PKG-02: plugin.json has name field set to doc-writer" {
  run grep '"name": "doc-writer"' "${PROJECT_ROOT}/doc-writer/.claude-plugin/plugin.json"
  [ "$status" -eq 0 ]
}

@test "PKG-02: plugin.json has version field" {
  run grep '"version"' "${PROJECT_ROOT}/doc-writer/.claude-plugin/plugin.json"
  [ "$status" -eq 0 ]
}

@test "PKG-02: plugin.json has description field" {
  run grep '"description"' "${PROJECT_ROOT}/doc-writer/.claude-plugin/plugin.json"
  [ "$status" -eq 0 ]
}

# ---------------------------------------------------------------------------
# PKG-03: marketplace.json exists at repo root with doc-writer plugin entry
# ---------------------------------------------------------------------------

@test "PKG-03: .claude-plugin/ directory exists at repo root" {
  [ -d "${PROJECT_ROOT}/.claude-plugin" ]
}

@test "PKG-03: .claude-plugin/marketplace.json exists at repo root" {
  [ -f "${PROJECT_ROOT}/.claude-plugin/marketplace.json" ]
}

@test "PKG-03: marketplace.json has doc-writer plugin entry" {
  run grep '"name": "doc-writer"' "${PROJECT_ROOT}/.claude-plugin/marketplace.json"
  [ "$status" -eq 0 ]
}

@test "PKG-03: marketplace.json has source pointing to ./doc-writer" {
  run grep '"source": "./doc-writer"' "${PROJECT_ROOT}/.claude-plugin/marketplace.json"
  [ "$status" -eq 0 ]
}

# ---------------------------------------------------------------------------
# PKG-04: All 6 skills exist at new path doc-writer/skills/<name>/SKILL.md
# ---------------------------------------------------------------------------

@test "PKG-04: doc-writer/skills/diataxis/SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/diataxis/SKILL.md" ]
}

@test "PKG-04: doc-writer/skills/edit/SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/edit/SKILL.md" ]
}

@test "PKG-04: doc-writer/skills/quality-rules/SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md" ]
}

@test "PKG-04: doc-writer/skills/review/SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/review/SKILL.md" ]
}

@test "PKG-04: doc-writer/skills/setup/SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md" ]
}

@test "PKG-04: doc-writer/skills/write/SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/write/SKILL.md" ]
}

# ---------------------------------------------------------------------------
# PKG-05: All 3 agents exist at new path doc-writer/agents/*.md
# ---------------------------------------------------------------------------

@test "PKG-05: doc-writer/agents/doc-author.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/agents/doc-author.md" ]
}

@test "PKG-05: doc-writer/agents/doc-editor.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/agents/doc-editor.md" ]
}

@test "PKG-05: doc-writer/agents/doc-persona.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/agents/doc-persona.md" ]
}

# ---------------------------------------------------------------------------
# PKG-06: CLAUDE_PLUGIN_ROOT references in skill files resolve correctly
#         (paths must be within skills/ or agents/ under doc-writer/)
# ---------------------------------------------------------------------------

@test "PKG-06: setup SKILL.md uses CLAUDE_PLUGIN_ROOT (not PROJECT_ROOT or hardcoded paths)" {
  run grep "CLAUDE_PLUGIN_ROOT" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "PKG-06: write SKILL.md uses CLAUDE_PLUGIN_ROOT for script references" {
  run grep "CLAUDE_PLUGIN_ROOT" "${PROJECT_ROOT}/doc-writer/skills/write/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "PKG-06: skill files do not reference absolute /Users paths" {
  run grep -r "/Users/" "${PROJECT_ROOT}/doc-writer/skills/"
  [ "$status" -ne 0 ]
}

@test "PKG-06: skill files do not use relative ../ paths" {
  run grep -r '\.\./\.\.' "${PROJECT_ROOT}/doc-writer/skills/"
  [ "$status" -ne 0 ]
}

# ---------------------------------------------------------------------------
# PKG-07: Old skills/ and agents/ directories at repo root are gone
# ---------------------------------------------------------------------------

@test "PKG-07: old skills/ directory at repo root is gone" {
  [ ! -d "${PROJECT_ROOT}/skills" ]
}

@test "PKG-07: old agents/ directory at repo root is gone" {
  [ ! -d "${PROJECT_ROOT}/agents" ]
}

# ---------------------------------------------------------------------------
# PKG-08: Supporting files moved with their parent skill directories
# ---------------------------------------------------------------------------

@test "PKG-08: diataxis references directory moved" {
  [ -d "${PROJECT_ROOT}/doc-writer/skills/diataxis/references" ]
}

@test "PKG-08: setup defaults directory moved" {
  [ -d "${PROJECT_ROOT}/doc-writer/skills/setup/defaults" ]
}

@test "PKG-08: setup scripts directory moved" {
  [ -d "${PROJECT_ROOT}/doc-writer/skills/setup/scripts" ]
}

@test "PKG-08: write scripts directory moved" {
  [ -d "${PROJECT_ROOT}/doc-writer/skills/write/scripts" ]
}
