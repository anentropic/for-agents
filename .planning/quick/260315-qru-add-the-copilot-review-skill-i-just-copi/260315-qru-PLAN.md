---
phase: quick
plan: 260315-qru
type: execute
wave: 1
depends_on: []
files_modified:
  - .claude-plugin/marketplace.json
autonomous: true
requirements: []

must_haves:
  truths:
    - "marketplace.json lists both doc-writer and copilot-review as plugins"
    - "copilot-review entry points to ./copilot-review source directory"
  artifacts:
    - path: ".claude-plugin/marketplace.json"
      provides: "Plugin registry with both plugins"
      contains: "copilot-review"
  key_links:
    - from: ".claude-plugin/marketplace.json"
      to: "./copilot-review"
      via: "source field in plugin entry"
      pattern: "\"source\".*copilot-review"
---

<objective>
Register the copilot-review skill (already copied to ./copilot-review/) as a second plugin entry in the marketplace config.

Purpose: The repo hosts multiple plugins; marketplace.json is the registry. The copilot-review skill is present on disk but not yet declared in the registry.
Output: Updated marketplace.json with a copilot-review plugin entry alongside the existing doc-writer entry.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md

<!-- Current marketplace.json (read before editing):
{
  "name": "doc-writer-plugins",
  "owner": { "name": "Your Name" },
  "plugins": [
    {
      "name": "doc-writer",
      "source": "./doc-writer",
      "description": "AI-powered library documentation generator"
    }
  ]
}

copilot-review/SKILL.md frontmatter:
  name: copilot-review
  description: >-
    Use this skill when the user invokes /copilot-review or asks for a code review
    using GitHub Copilot as a second opinion. Performs multi-dimensional code review
    by running parallel Copilot CLI sub-reviews across 6 focus areas (architecture,
    test coverage, code quality, error handling, dependency audit, reinvented wheels),
    then consolidates and prioritizes all findings into actionable items.
-->
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add copilot-review entry to marketplace.json</name>
  <files>.claude-plugin/marketplace.json</files>
  <action>
Read .claude-plugin/marketplace.json then add a second plugin entry to the "plugins" array:

```json
{
  "name": "copilot-review",
  "source": "./copilot-review",
  "description": "Multi-dimensional code review using GitHub Copilot as a second opinion — runs 6 parallel sub-reviews (architecture, tests, quality, errors, deps, reinvented wheels) then consolidates and prioritizes findings"
}
```

The description is derived from copilot-review/SKILL.md. Do not alter the existing doc-writer entry or any other fields.
  </action>
  <verify>
    <automated>node -e "const m = require('./.claude-plugin/marketplace.json'); const names = m.plugins.map(p => p.name); if (!names.includes('copilot-review')) throw new Error('copilot-review missing'); if (!names.includes('doc-writer')) throw new Error('doc-writer missing'); console.log('OK:', names.join(', '));"</automated>
  </verify>
  <done>marketplace.json has two plugin entries: doc-writer (unchanged) and copilot-review pointing to ./copilot-review</done>
</task>

</tasks>

<verification>
node -e "const m = require('./.claude-plugin/marketplace.json'); console.log(JSON.stringify(m, null, 2));"

Confirm both plugins listed, source paths correct, JSON is valid.
</verification>

<success_criteria>
- marketplace.json is valid JSON
- plugins array has exactly 2 entries: doc-writer and copilot-review
- copilot-review source is "./copilot-review"
- doc-writer entry is unchanged
</success_criteria>

<output>
After completion, create `.planning/quick/260315-qru-add-the-copilot-review-skill-i-just-copi/260315-qru-SUMMARY.md`
</output>
