# Phase 8: doc-writer skills polish - Context

**Gathered:** 2026-03-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Polish the doc-writer plugin's skill UX in two concrete ways: (1) add `argument-hint` frontmatter to all user-invocable skills so the Claude UI can suggest flags, and (2) replace plain-text list questions in skills and the Doc Author agent with native AskUserQuestion multi-choice UI using the GSD pattern. No new pipeline features or agent logic changes — purely UX polish on existing interaction points.

</domain>

<decisions>
## Implementation Decisions

### argument-hint frontmatter
- All four user-invocable skills get `argument-hint` added: write, setup, review, edit
- Flags to document per skill:
  - `doc-writer:write` → `[--skip-gap-scan]`
  - `doc-writer:setup` → `[--reset]`
  - `doc-writer:review` → `[--edit]`
  - `doc-writer:edit` → `[issue-numbers-or-description]` (freeform, not a flag)
- Format follows `frontmatter-reference.md`: square brackets per argument, descriptive names

### Multi-choice UI: which places
- **Skills (orchestrators):** write, review, edit, setup skills — all places where the user currently sees a list and types a response
- **Doc Author agent:** the page inventory approval step (Author proposes pages, user confirms/modifies)
- Doc Editor and Doc Persona agents do NOT ask the user questions mid-run — excluded

### Multi-choice UI: option set pattern
Every AskUserQuestion in skills/agents must include, at the bottom of every options list:
- One "Type something else" option in the main options group (before the chat option)
- One "Chat about this" option as the final option

These two slots are part of the standard pattern on every question — not optional per-question.

### "Type something else" handling
- Agent uses judgment based on context
- In practice: if the user's freeform text is a clear instruction (e.g. "remove page 3"), act on it directly; if it's ambiguous, drop to plain-text follow-up before acting
- No fixed rule — Claude decides

### "Chat about this" handling
- Agent acknowledges the selection, explains the current decision point in more depth (what's being decided, why, what the options mean)
- Then opens a plain-text dialogue to understand what the user wants to discuss
- After the conversation resolves, resumes structured flow (re-presents options or proceeds)

### Claude's Discretion
- Exact wording of "Type something else" and "Chat about this" option descriptions
- Which questions within a skill get multi-choice vs remain plain-text (use judgment: structured choices benefit from AskUserQuestion, open-ended inputs like "describe the issue you want fixed" do not)
- AskUserQuestion header text (max 12 chars)
- Whether to use multiSelect: true for the page inventory approval (likely yes — user confirms/deselects pages)

</decisions>

<specifics>
## Specific Ideas

- GSD's pattern from `.claude/get-shit-done/references/questioning.md` is the reference: "Other" auto-provided by AskUserQuestion, freeform answers trigger plain-text follow-up (not another AskUserQuestion)
- `argument-hint` format reference: `/Users/paul/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/command-development/references/frontmatter-reference.md`
- The "Chat about this" option is additive to the GSD pattern — GSD uses "Other" for freeform but doesn't have a dedicated "explain this decision" option

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### argument-hint frontmatter
- `/Users/paul/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/command-development/references/frontmatter-reference.md` — Complete argument-hint syntax, examples, and best practices

### AskUserQuestion pattern
- `/Users/paul/.claude/get-shit-done/references/questioning.md` — GSD's AskUserQuestion usage guide: option design, freeform_rule (when to drop to plain text), anti-patterns

### Skills to modify
- `doc-writer/skills/write/SKILL.md` — add argument-hint; add multi-choice to PARTIAL approval list and any other user-facing choice points
- `doc-writer/skills/setup/SKILL.md` — add argument-hint; add multi-choice to doc system selection and paths confirmation
- `doc-writer/skills/review/SKILL.md` — add argument-hint; add multi-choice to --edit confirmation gate
- `doc-writer/skills/edit/SKILL.md` — add argument-hint; add multi-choice to issue selection list
- `doc-writer/agents/doc-author.md` — add multi-choice to page inventory approval step

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AskUserQuestion` tool: available in all skill/agent contexts; auto-adds "Other" to every question; supports `multiSelect: true`; header max 12 chars; 2-4 options per question

### Established Patterns
- `disable-model-invocation: true` already set on write, setup, review, edit skills — no change needed there
- Frontmatter lives at top of each SKILL.md file before the `# Title` heading
- Current skills present choices as plain markdown lists (e.g. "Enter numbers to approve (e.g., '1,3'), 'all', or 'none'") — these are the primary conversion targets

### Integration Points
- PARTIAL approval in write skill: currently "Enter numbers to approve" plain text → convert to AskUserQuestion multiSelect
- Issue selection in edit skill: currently numbered list → convert to AskUserQuestion multiSelect
- Doc system selection in setup skill: currently numbered list → convert to AskUserQuestion
- Page inventory in doc-author agent: currently "Please confirm this plan" → convert to AskUserQuestion multiSelect

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-doc-writer-skills-polish*
*Context gathered: 2026-03-16*
