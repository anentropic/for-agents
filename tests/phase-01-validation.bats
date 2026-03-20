#!/usr/bin/env bats
# Phase 1 — Foundation and Setup
# Automated validation for SETUP-01 through SETUP-05 (automatable assertions only)

setup() {
  PROJECT_ROOT="/Users/paul/Documents/Dev/Personal/doc-writer-agent"
}

# ---------------------------------------------------------------------------
# SETUP-01: Setup command asks about audiences, persists config
# ---------------------------------------------------------------------------

@test "SETUP-01: setup SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md" ]
}

@test "SETUP-01: config-template.yaml exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/config-template.yaml" ]
}

@test "SETUP-01: config-template has audiences as array (not singular)" {
  run grep -n "^audiences:" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/config-template.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" == *"audiences:"* ]]
}

@test "SETUP-01: config-template audiences entry has skill_level field" {
  run grep "skill_level" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/config-template.yaml"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: config-template audiences entry has assumed_knowledge field" {
  run grep "assumed_knowledge" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/config-template.yaml"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: config-template audiences entry has never_assume field" {
  run grep "never_assume" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/config-template.yaml"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: setup SKILL.md asks for audience name field" {
  run grep -i "name" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: setup SKILL.md includes skill_level question" {
  run grep "skill_level\|skill level\|Skill level" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: setup SKILL.md includes assumed_knowledge question" {
  run grep "assumed_knowledge\|assumed knowledge\|Assumed knowledge" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: setup SKILL.md includes never_assume question" {
  run grep "never_assume\|never assume\|Never assume" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: setup SKILL.md has re-run detection logic (checks for existing config)" {
  run grep -i "config.yaml\|Re-Run\|re-run\|already" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-01: setup SKILL.md instructs to store audiences as array even for single audience" {
  run grep -i "array\|single-element\|even if only one" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

# ---------------------------------------------------------------------------
# SETUP-02: Layered quality rules — universal + project-specific
# ---------------------------------------------------------------------------

@test "SETUP-02: quality-rules SKILL.md exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md" ]
}

@test "SETUP-02: quality-rules skill has user-invocable: false" {
  run grep "user-invocable: false" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: quality-rules skill contains exactly 5 rules" {
  run grep -c "^## Rule " "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -eq 0 ]
  [ "$output" -eq 5 ]
}

@test "SETUP-02: quality-rules has Rule 1 (No Internal Details)" {
  run grep "No Internal Details\|Internal Details" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: quality-rules has Rule 2 (Working Code Examples)" {
  run grep "Working Code Examples\|Code Examples Required" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: quality-rules has Rule 3 (Consistent Structure)" {
  run grep "Consistent Structure" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: quality-rules has Rule 4 (Cross-Reference Code Mentions)" {
  run grep "Cross-Reference" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: quality-rules has Rule 5 (Audience-Calibrated Language)" {
  run grep "Audience-Calibrated" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: rules.md exists as default project-specific rules template" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/rules.md" ]
}

@test "SETUP-02: rules.md describes the additive relationship to universal rules" {
  run grep -i "additive\|extend\|add.*on top" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/rules.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: doc-author agent references quality-rules skill" {
  run grep "quality-rules" "${PROJECT_ROOT}/doc-writer/agents/doc-author.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-02: doc-editor agent references quality-rules skill" {
  run grep "quality-rules" "${PROJECT_ROOT}/doc-writer/agents/doc-editor.md"
  [ "$status" -eq 0 ]
}

# ---------------------------------------------------------------------------
# SETUP-03: Doc-system-agnostic rules + separate guidance files
# ---------------------------------------------------------------------------

@test "SETUP-03: mkdocs-material guidance file exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/mkdocs-material.md" ]
}

@test "SETUP-03: plain-markdown guidance file exists" {
  [ -f "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/plain-markdown.md" ]
}

@test "SETUP-03: mkdocs-material guidance file mentions admonition preferences" {
  run grep -i "admonition" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/mkdocs-material.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-03: plain-markdown guidance file mentions markdown conventions" {
  run grep -i "markdown\|heading\|fenced\|ATX" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/plain-markdown.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-03: guidance files are separate from quality-rules skill" {
  # Quality-rules SKILL.md must not contain mkdocs-material or plain-markdown content
  run grep -i "admonition\|mkdocs-material\|plain-markdown" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -ne 0 ]
}

@test "SETUP-03: quality-rules skill contains no doc-system-specific syntax" {
  # The quality-rules skill must not reference MkDocs-specific directives
  run grep -i "mkdocs\|docusaurus\|vitepress\|sphinx" "${PROJECT_ROOT}/doc-writer/skills/quality-rules/SKILL.md"
  [ "$status" -ne 0 ]
}

@test "SETUP-03: setup SKILL.md instructs copying guidance file to .doc-writer/" {
  run grep -i "guidance\|{doc_system}.md\|defaults/" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-03: setup SKILL.md references CLAUDE_PLUGIN_ROOT for guidance file path" {
  run grep "CLAUDE_PLUGIN_ROOT" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

# ---------------------------------------------------------------------------
# SETUP-04: Custom quality rules in config
# ---------------------------------------------------------------------------

@test "SETUP-04: rules.md is freeform markdown (not structured YAML)" {
  # Verify it does NOT start with YAML frontmatter (---) or have rigid schema keys
  run head -1 "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/rules.md"
  [ "$status" -eq 0 ]
  [[ "$output" != "---" ]]
}

@test "SETUP-04: rules.md contains commented-out examples for guidance" {
  run grep "<!--" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/rules.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-04: rules.md explains rules are written as natural language instructions" {
  run grep -i "natural language\|interpret" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/rules.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-04: setup SKILL.md instructs copying rules.md to .doc-writer/" {
  run grep -i "rules.md\|rules" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
  # Verify the copy instruction for defaults/rules.md exists
  run grep "defaults/rules.md\|Copy.*rules\|rules.md" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-04: setup SKILL.md copy uses CLAUDE_PLUGIN_ROOT for rules.md path" {
  run grep "CLAUDE_PLUGIN_ROOT.*rules\|rules.*CLAUDE_PLUGIN_ROOT\|defaults/rules" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

# ---------------------------------------------------------------------------
# SETUP-05: Audience Q&A determines persona count
# ---------------------------------------------------------------------------

@test "SETUP-05: config-template stores audiences as YAML array (dash entry)" {
  # Must have an array entry (- name: ...) not a scalar
  run grep "^  - name:" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/config-template.yaml"
  [ "$status" -eq 0 ]
}

@test "SETUP-05: setup SKILL.md asks about secondary audience" {
  run grep -i "secondary audience\|secondary\|additional audience" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-05: setup SKILL.md has loop logic for multiple audiences" {
  run grep -i "continue\|loop\|until.*no\|repeat\|additional" "${PROJECT_ROOT}/doc-writer/skills/setup/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-05: doc-persona agent reads audiences from config" {
  run grep -i "audiences\|audience\|config.yaml" "${PROJECT_ROOT}/doc-writer/agents/doc-persona.md"
  [ "$status" -eq 0 ]
}

@test "SETUP-05: config-template uses plural audiences key (never singular audience)" {
  # Must have 'audiences:' key, must NOT have a top-level 'audience:' key
  run grep "^audience:" "${PROJECT_ROOT}/doc-writer/skills/setup/defaults/config-template.yaml"
  [ "$status" -ne 0 ]
}
