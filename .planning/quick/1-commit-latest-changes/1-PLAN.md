---
phase: quick
plan: 1
type: execute
wave: 1
depends_on: []
files_modified:
  - agents/doc-author.md
  - agents/doc-editor.md
  - agents/doc-persona.md
  - skills/diataxis/SKILL.md
  - skills/diataxis/references/explanation.md
  - skills/diataxis/references/framework-overview.md
  - skills/diataxis/references/how-to-guides.md
  - skills/diataxis/references/reference.md
  - skills/diataxis/references/tutorials.md
autonomous: true
requirements: []

must_haves:
  truths:
    - "All Diataxis skill changes are committed in a single atomic commit"
    - ".pre-commit-config.yaml is NOT included in the commit"
  artifacts:
    - path: "skills/diataxis/references/explanation.md"
      provides: "Diataxis explanation type reference"
    - path: "skills/diataxis/references/framework-overview.md"
      provides: "Diataxis framework overview reference"
    - path: "skills/diataxis/references/how-to-guides.md"
      provides: "Diataxis how-to guide type reference"
    - path: "skills/diataxis/references/reference.md"
      provides: "Diataxis reference type reference"
    - path: "skills/diataxis/references/tutorials.md"
      provides: "Diataxis tutorial type reference"
  key_links: []
---

<objective>
Commit the Diataxis skill deep integration across all three agents (doc-author, doc-editor, doc-persona) along with new reference files and updated SKILL.md.

Purpose: Capture a cohesive set of changes that add Diataxis type-awareness to every stage of the documentation pipeline — writing, editing, and persona validation.
Output: A clean git commit on branch gsd/v1.0-milestone with all 9 files staged.
</objective>

<execution_context>
@/Users/paul/.claude/get-shit-done/workflows/execute-plan.md
@/Users/paul/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Stage and commit Diataxis integration changes</name>
  <files>
    agents/doc-author.md
    agents/doc-editor.md
    agents/doc-persona.md
    skills/diataxis/SKILL.md
    skills/diataxis/references/explanation.md
    skills/diataxis/references/framework-overview.md
    skills/diataxis/references/how-to-guides.md
    skills/diataxis/references/reference.md
    skills/diataxis/references/tutorials.md
  </files>
  <action>
Stage exactly these 9 files (4 modified + 5 new) and create a single commit:

Modified agents:
- agents/doc-author.md — reads type-specific reference files during Phase 2; internal notes include page classification
- agents/doc-editor.md — new Pass 2 (Diataxis Type Integrity) for type blur detection; 4 passes total; added diataxis skill
- agents/doc-persona.md — type-alignment validation during simulation; diataxis skill; type mismatch as friction source

Modified skill:
- skills/diataxis/SKILL.md — updated and reformatted as part of the reference system

New reference files:
- skills/diataxis/references/explanation.md
- skills/diataxis/references/framework-overview.md
- skills/diataxis/references/how-to-guides.md
- skills/diataxis/references/reference.md
- skills/diataxis/references/tutorials.md

DO NOT stage .pre-commit-config.yaml — it is unrelated to this change set.

Commit message style: follow the existing convention (e.g., `feat(diataxis): ...`). Use a descriptive body summarizing all three agent integrations and the new reference files.

Stage with explicit file paths (not `git add .` or `git add -A`).
  </action>
  <verify>
    <automated>git log --oneline -1 && git diff --name-only HEAD~1..HEAD | sort && git status --short | grep -q ".pre-commit-config.yaml"</automated>
  </verify>
  <done>
    - Commit exists with all 9 files and only those 9 files
    - .pre-commit-config.yaml remains untracked (visible in git status)
    - Commit message clearly describes the Diataxis deep integration
  </done>
</task>

</tasks>

<verification>
- `git log --oneline -1` shows the new commit
- `git diff --name-only HEAD~1..HEAD` lists exactly 9 files (4 modified + 5 new)
- `git status --short` still shows `?? .pre-commit-config.yaml` as untracked
</verification>

<success_criteria>
All Diataxis skill integration changes are committed atomically. The .pre-commit-config.yaml file is not included. The commit message follows project conventions.
</success_criteria>

<output>
After completion, create `.planning/quick/1-commit-latest-changes/1-SUMMARY.md`
</output>
