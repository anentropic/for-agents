# Phase 5: Integration and Commands - Research

**Researched:** 2026-03-04
**Domain:** Claude Code plugin skills (command orchestration), subagent spawning, multi-agent pipeline coordination, gap detection, exported symbol scanning
**Confidence:** HIGH -- CC plugin skill format verified against current official docs (code.claude.com/docs/en/skills, /sub-agents, /plugins-reference); all agent artifacts verified by direct file read; pipeline architecture follows locked user decisions

## Summary

Phase 5 is the integration layer that turns the proven three-agent pipeline (Author > Editor > Persona) into user-facing commands. The primary deliverables are three skills -- `/doc:write`, `/doc:review`, `/doc:edit` -- plus a gap detection scanner that identifies undocumented public API surface. These skills orchestrate the existing agents via CC's Agent tool, manage the revision loop (FAILs trigger re-passes, PARTIALs go to project author), and produce summary reports.

A critical architecture finding: CC's skills system has fully subsumed commands. The official docs state "Custom commands have been merged into skills." A `.claude/commands/review.md` and a `.claude/skills/review/SKILL.md` both create `/review` and work identically. Skills are recommended because they support directories with supporting files, invocation control via frontmatter, and automatic model invocation. For this plugin, all three commands should be implemented as skills in the `skills/` directory, not as files in a `commands/` directory. This aligns with how `/doc-writer:setup` is already implemented.

The orchestration approach is skill-based: each `/doc:write`, `/doc:review`, and `/doc:edit` skill contains the full orchestration logic as prompt instructions. The skill uses `disable-model-invocation: true` (user must explicitly invoke), `allowed-tools` to grant Agent, Read, Write, Glob, Grep, Bash access, and the skill body describes the step-by-step pipeline. Claude reads the skill content as its orchestration playbook and uses the Agent tool to spawn doc-author, doc-editor, and doc-persona subagents as needed. The skill runs in the main conversation context (NOT `context: fork`), so the project author can interact with PARTIAL approval prompts and see progress reports.

**Primary recommendation:** Implement `/doc:write`, `/doc:review`, and `/doc:edit` as skills in `skills/write/SKILL.md`, `skills/review/SKILL.md`, and `skills/edit/SKILL.md`. Each skill contains orchestration instructions that Claude follows using the Agent tool to spawn existing agents. Gap detection is a shell script (`skills/write/scripts/scan-exports.sh`) invoked via dynamic context injection in the write and review skills.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Claude decides the orchestration approach (command file vs dedicated orchestrator agent) based on CC plugin architecture
- Pipeline sequence: gap detection scan > Author > Editor > Persona(s) > revision loop (if FAILs) > summary
- Revision loop uses locked decisions from Phase 4: only FAILs trigger revision, max 2-3 passes, Author revises targeted pages, Editor re-runs changed pages + full terminology, escalation on non-convergence
- Multi-audience: separate Persona per audience in parallel (from Phase 4)
- Generated docs are left uncommitted -- project author reviews diff and commits when satisfied
- Full summary report at completion showing: pages written/revised, Editor changes applied, Persona verdicts per scenario, revision passes taken, remaining PARTIALs
- Claude decides the UX for PARTIAL approval (inline during pipeline vs batch at end)
- Core requirement: project author sees PARTIAL fix suggestions and approves/rejects them
- Approved fixes applied directly without re-running the full pipeline
- /doc:review runs Editor + Persona only (no Author) on existing docs
- /doc:review produces editor-report.md and persona-report.md showing issues
- Gap detection also runs during /doc:review (same exported-symbols scan)
- No content generation during /doc:review -- purely an audit of existing documentation
- /doc:edit presents issues from existing reports (editor-report.md, persona-report.md) as multi-select options
- /doc:edit includes a freeform "describe something else" option for custom instructions
- Project author selects which issues to fix
- Author agent rewrites targeted content, then Editor runs humanizer + terminology + cross-refs on changed pages
- No Persona re-run after edit -- project author can run /doc:review afterwards if they want full validation
- Public API surface = exported symbols only (exported functions, classes, types, constants)
- Language-adaptive: Python's __all__, Rust's pub, TypeScript's export, etc.
- Gap detection runs during /doc:write before Author starts -- gap list handed to Author as input so it can prioritize undocumented symbols
- Also runs during /doc:review to flag undocumented symbols in existing docs
- Report appears both in the completion summary AND persisted to .doc-writer/gap-report.md
- Author reads gap-report.md from previous runs as optional input for prioritizing coverage
- Commands are the GSD integration -- /doc:write, /doc:review, /doc:edit work in any CC session including GSD sessions
- No special GSD hooks or automatic triggers
- GSD planners can naturally reference /doc:write in roadmap tasks
- INTG-04 satisfied by commands being available and invokable
- Optional: if .planning/PROJECT.md exists, Author can use it for richer project understanding (light touch, not a dependency)

### Claude's Discretion
- Orchestration architecture (command file vs orchestrator agent)
- PARTIAL approval UX approach (inline vs batch)
- How gap detection scans for exported symbols per language
- How Author prioritizes gap-report.md items vs its own scan findings
- Pipeline progress reporting during execution (verbose vs summary)
- How /doc:edit presents report issues (formatting, grouping)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INTG-01 | Project author can generate new docs on-demand via `/doc:write` command | Skill at `skills/write/SKILL.md` with `disable-model-invocation: true`; orchestration logic in skill body spawns Author > Editor > Persona via Agent tool; gap detection runs first via `!`command`` dynamic context injection; summary report presented at completion |
| INTG-02 | Project author can review existing docs via `/doc:review` -- runs Editor + Persona pipeline on current docs, reports issues | Skill at `skills/review/SKILL.md`; spawns Editor then Persona(s) only (no Author); gap detection scan also included; produces editor-report.md and persona-report.md; no content generation |
| INTG-03 | Project author can make targeted fixes via `/doc:edit` -- addresses specific pages or issues | Skill at `skills/edit/SKILL.md`; reads existing reports, presents issues as numbered list for multi-select, includes freeform option; spawns Author for targeted rewrites then Editor for changed pages only; no Persona re-run |
| INTG-04 | Plugin integrates with GSD workflow -- invokable at milestone boundaries | Satisfied by skills being available in any CC session; no special GSD hooks needed; GSD planners reference `/doc-writer:write` naturally in roadmap tasks |
| INTG-05 | Gap detection compares public API surface against documented surface and reports undocumented features | Shell script at `skills/write/scripts/scan-exports.sh` scans for exported symbols per language; compared against doc page content; gap report persisted to `.doc-writer/gap-report.md`; runs in both /doc:write and /doc:review |
</phase_requirements>

## Standard Stack

### Core

| Component | Format | Purpose | Why Standard |
|-----------|--------|---------|--------------|
| Write skill (`skills/write/SKILL.md`) | YAML frontmatter + markdown body | `/doc-writer:write` orchestration | CC skill format with `disable-model-invocation: true`; orchestrates full Author > Editor > Persona pipeline; uses Agent tool to spawn subagents |
| Review skill (`skills/review/SKILL.md`) | YAML frontmatter + markdown body | `/doc-writer:review` orchestration | CC skill format; runs Editor + Persona only on existing docs; audit-only, no content generation |
| Edit skill (`skills/edit/SKILL.md`) | YAML frontmatter + markdown body | `/doc-writer:edit` targeted fixes | CC skill format; reads existing reports, presents issue selection, spawns Author + Editor for targeted fixes |
| Gap detection script (`skills/write/scripts/scan-exports.sh`) | Bash script | Public API surface scanning | Dynamic context injection via `!`command``; language-adaptive export scanning; output parsed by Claude for comparison against doc content |
| Agent tool | CC built-in tool | Spawning doc-author, doc-editor, doc-persona subagents | CC's native Agent tool (formerly Task) handles subagent lifecycle; subagents already defined in `agents/` directory |

### Supporting

| Component | Format | Purpose | When to Use |
|-----------|--------|---------|-------------|
| Gap report (`.doc-writer/gap-report.md`) | Markdown | Persisted list of undocumented exported symbols | Written after gap scan; read by Author on subsequent runs for coverage prioritization |
| Editor report (`.doc-writer/editor-report.md`) | Markdown | Structured feedback from Editor pass | Read by /doc:edit to present issues for selection; produced by /doc:review |
| Persona reports (`.doc-writer/persona-report*.md`) | Markdown | Per-audience verdict reports | Read by /doc:edit to present issues; consumed by revision loop for FAIL/PARTIAL routing |
| Summary report (console output) | Text | Completion summary for project author | Displayed at end of /doc:write showing pages written, changes applied, verdicts, passes taken |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Skills for commands | `commands/` directory files | Skills are officially recommended over commands; skills support directories with supporting files (scripts, templates); both create `/` commands identically |
| Skill-body orchestration | Dedicated orchestrator agent (`agents/doc-orchestrator.md`) | A dedicated orchestrator agent would run in isolated context, losing the ability to prompt the project author for PARTIAL approvals inline; skill-body runs in main conversation where interactive prompts work naturally |
| Shell script for gap detection | Claude-native scanning (Read + Grep in skill body) | Shell script runs as preprocessing via `!`command`` -- faster and does not consume Claude's context budget with raw source file contents; Claude only sees the gap list |
| `context: fork` for skills | Main conversation context (no fork) | Fork isolates the skill from conversation history; we NEED conversation context for interactive PARTIAL approval and progress reporting to the user |

## Architecture Patterns

### Recommended Plugin Structure (Phase 5 additions)

```
doc-writer-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── setup/                        # Existing (Phase 1)
│   │   ├── SKILL.md
│   │   ├── defaults/
│   │   └── scripts/
│   ├── quality-rules/                # Existing (Phase 1)
│   │   └── SKILL.md
│   ├── diataxis/                     # Existing (Phase 1)
│   │   └── SKILL.md
│   ├── write/                        # NEW: /doc-writer:write
│   │   ├── SKILL.md                  # Full pipeline orchestrator
│   │   └── scripts/
│   │       └── scan-exports.sh       # Gap detection script
│   ├── review/                       # NEW: /doc-writer:review
│   │   └── SKILL.md                  # Audit-only orchestrator
│   └── edit/                         # NEW: /doc-writer:edit
│       └── SKILL.md                  # Targeted fix orchestrator
├── agents/
│   ├── doc-author.md                 # Existing (Phase 2)
│   ├── doc-editor.md                 # Existing (Phase 3)
│   └── doc-persona.md                # Existing (Phase 4)
└── README.md
```

### Pattern 1: Skill-Based Orchestration (Primary Pattern)

**What:** Each command is a skill with `disable-model-invocation: true`. The skill body is a step-by-step playbook that Claude follows using the Agent tool to spawn existing subagents. The skill runs in the main conversation (not forked), allowing interactive prompts to the user.

**When to use:** For all three commands (`/doc:write`, `/doc:review`, `/doc:edit`).

**Why NOT `context: fork`:** The official docs state: "`context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines without a task, the subagent receives the guidelines but no actionable prompt." More importantly, a forked context loses access to the conversation -- the project author cannot approve PARTIALs, see progress, or interact during pipeline execution. These commands MUST run in the main conversation context.

**Why NOT a dedicated orchestrator agent:** Subagents cannot spawn other subagents. The CC docs explicitly state: "Subagents cannot spawn other subagents." If we made a `doc-orchestrator` agent, it could not use the Agent tool to spawn `doc-author`, `doc-editor`, or `doc-persona`. The orchestration MUST happen at the main conversation level (via a skill).

**Example frontmatter for /doc:write:**

```yaml
---
name: write
description: Generate new documentation using the full Author > Editor > Persona pipeline. Runs gap detection, writes docs, edits for quality, validates from user perspective, and handles revision loop.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--skip-gap-scan]"
---
```

**Confidence:** HIGH -- verified from official CC docs: skills with `disable-model-invocation: true` are the recommended pattern for user-triggered workflows with side effects; Agent tool is the standard mechanism for spawning subagents; subagents cannot spawn other subagents, confirming skill-level orchestration is required.

### Pattern 2: Agent Tool Invocation for Pipeline Stages

**What:** The orchestrating skill uses the Agent tool to spawn each pipeline stage. Each Agent invocation creates a fresh subagent context with the agent's system prompt preloaded. The skill passes specific instructions via the delegation message.

**When to use:** Every time a pipeline stage runs (Author writes, Editor edits, Persona evaluates).

**Example delegation messages:**

```
# Spawning Author for initial write
Agent(doc-author): "Generate documentation for this project. Read .doc-writer/config.yaml for audience and paths configuration. Read .doc-writer/gap-report.md for previously identified undocumented symbols to prioritize."

# Spawning Editor for quality pass
Agent(doc-editor): "Edit the documentation in {docs_root}. Run all three passes: terminology, humanizer, cross-references."

# Spawning Persona for evaluation (per audience)
Agent(doc-persona): "Evaluate documentation as the '{audience_name}' audience."

# Spawning Author for revision pass
Agent(doc-author): "Revise targeted pages based on Persona FAIL verdicts. Read .doc-writer/persona-report.md for specific gaps. Revise ONLY the pages identified in FAIL scenarios: {page_list}."

# Spawning Editor for revision pass
Agent(doc-editor): "Edit the revised documentation pages: {changed_pages}. Run all three passes on changed pages. Run terminology pass on ALL pages (term changes can ripple)."
```

**Confidence:** HIGH -- Agent tool is the standard CC mechanism for spawning subagents; delegation messages are plain text that the subagent receives as its task.

### Pattern 3: Gap Detection via Dynamic Context Injection

**What:** A shell script scans the project for exported symbols and compares against documented symbols. The script runs as preprocessing (before Claude sees the skill content) via the `!`command`` syntax, or as an explicit Bash tool call during pipeline execution.

**When to use:** At the start of `/doc:write` (before Author) and during `/doc:review`.

**Two approaches for gap detection timing:**

1. **Dynamic context injection (`!`command``):** Script runs before the skill content reaches Claude. Pros: fast, no context consumption. Cons: only runs at skill load time, not mid-pipeline.
2. **Explicit Bash tool call:** The skill instructs Claude to run the script as a step. Pros: can run at any point in the pipeline. Cons: output enters Claude's context.

**Recommendation:** Use explicit Bash tool call, not dynamic context injection. The gap scan needs to read `paths.source_root` and `paths.docs_root` from `.doc-writer/config.yaml`, which requires Claude to read config first and then invoke the script with the correct paths. Dynamic context injection runs before Claude processes anything, so it cannot use config values.

**Script approach:**

```bash
#!/bin/bash
# scan-exports.sh -- scan for exported symbols in source code
# Usage: scan-exports.sh <source_root> <language>

SOURCE_ROOT="$1"
LANG="$2"

case "$LANG" in
  python)
    # Find __all__ definitions and public symbols (no leading underscore)
    grep -rn '__all__\s*=' "$SOURCE_ROOT" --include="*.py" 2>/dev/null
    grep -rn '^def [^_]' "$SOURCE_ROOT" --include="*.py" 2>/dev/null
    grep -rn '^class [^_]' "$SOURCE_ROOT" --include="*.py" 2>/dev/null
    ;;
  typescript|javascript)
    grep -rn '^export ' "$SOURCE_ROOT" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null
    ;;
  rust)
    grep -rn '^pub ' "$SOURCE_ROOT" --include="*.rs" 2>/dev/null
    ;;
  go)
    # Go exports via capitalized first letter
    grep -rn '^func [A-Z]' "$SOURCE_ROOT" --include="*.go" 2>/dev/null
    grep -rn '^type [A-Z]' "$SOURCE_ROOT" --include="*.go" 2>/dev/null
    ;;
  *)
    echo "Language '$LANG' not supported for gap detection"
    exit 1
    ;;
esac
```

**Claude then compares the symbol list against documented content** by reading doc pages and checking which exported symbols have corresponding documentation. The comparison is done by Claude's reasoning, not by the script.

**Confidence:** HIGH for the approach; MEDIUM for the script's completeness across all languages (edge cases in Python `__all__` parsing, TypeScript re-exports, etc. will need refinement per-project).

### Pattern 4: Revision Loop State Machine

**What:** The `/doc:write` skill implements a state machine for the revision loop. After each Persona evaluation pass, the skill checks verdicts and routes accordingly.

**When to use:** Within `/doc:write` orchestration after the initial Author > Editor > Persona pass.

**State machine logic (encoded in skill body):**

```
INITIAL PASS:
  1. Run gap detection scan
  2. Spawn Author (with gap report)
  3. Spawn Editor (on Author output)
  4. For each audience: Spawn Persona
  5. Collect all Persona reports
  6. Check verdicts:
     - All PASS across all audiences -> DONE
     - Any FAIL -> REVISION PASS (pass_count = 1)
     - Only PARTIAL (no FAIL) -> PARTIAL APPROVAL FLOW

REVISION PASS (max 3 total passes including initial):
  1. Extract FAIL gaps from Persona reports (pages + what's missing)
  2. Spawn Author with revision instructions (targeted pages only)
  3. Spawn Editor on changed pages (+ full terminology scan)
  4. For each audience: Spawn Persona (reuse existing scenarios)
  5. Compare verdicts with previous pass
  6. Check verdicts:
     - All PASS -> DONE
     - Any FAIL and pass_count < 3 -> REVISION PASS (pass_count++)
     - Any FAIL and pass_count >= 3 -> ESCALATION
     - Only PARTIAL (no FAIL) -> PARTIAL APPROVAL FLOW

PARTIAL APPROVAL FLOW:
  1. Collect all PARTIAL fix suggestions from Persona reports
  2. Present to project author: numbered list of suggestions
  3. Project author selects which to approve
  4. Apply approved fixes directly (Claude writes to doc files)
  5. Continue to DONE (no re-pipeline for PARTIAL fixes)

ESCALATION:
  1. Present remaining FAILs to project author with full context
  2. Show what was tried across passes and why it didn't converge
  3. Recommend manual intervention

DONE:
  1. Present summary report
  2. Docs left uncommitted for project author review
```

**Confidence:** HIGH -- state machine directly implements the locked decisions from CONTEXT.md and Phase 4's revision loop protocol.

### Pattern 5: PARTIAL Approval UX (Batch at End)

**What:** PARTIAL fix suggestions are batched and presented to the project author after the pipeline completes (or after all FAILs are resolved). The project author sees a numbered list of suggestions and selects which to approve.

**Recommendation: Batch at end, not inline during pipeline.** Inline interruption during multi-audience Persona evaluation would fragment the workflow. Batching gives the project author a complete picture of all PARTIAL issues before deciding which to fix.

**UX flow:**

```
## PARTIAL Issues Requiring Your Decision

The following issues were identified but do not prevent users from
accomplishing their goals. Review each and decide which to fix:

1. [Beginner audience, S3] docs/getting-started.md > "Installation"
   Issue: Steps assume familiarity with virtual environments
   Suggested fix: Add a "Prerequisites" subsection explaining venv creation
   -> approve / reject

2. [Advanced audience, S2] docs/how-to/caching.md > "Cache Invalidation"
   Issue: Missing example for programmatic invalidation
   Suggested fix: Add code example showing cache.invalidate(key) pattern
   -> approve / reject

3. Freeform: [describe any additional changes]

Enter numbers to approve (e.g., "1,2") or "all" / "none":
```

**Confidence:** MEDIUM -- UX is Claude's discretion per CONTEXT.md. Batch-at-end is recommended based on the reasoning that inline interruption during parallel Persona evaluation would be confusing, but the project may prefer a different approach.

### Pattern 6: /doc:edit Report-Driven Issue Selection

**What:** The `/doc:edit` skill reads existing reports (editor-report.md, persona-report*.md) and presents issues as a numbered multi-select list. The project author selects which issues to address, plus an optional freeform description.

**When to use:** When `/doc:edit` is invoked.

**UX flow:**

```
## Available Issues from Previous Reports

### From Editor Report
1. [BLOCKING] docs/getting-started.md > "Installation"
   Accuracy mismatch: doc says `pip install lib`, source shows `pip install lib[all]`

2. [SUGGESTION] docs/how-to/configure.md > "Advanced Options"
   AI pattern detected: "It's important to note that..." -> rewrite more directly

### From Persona Report (Beginner audience)
3. [FAIL] docs/getting-started.md
   Goal "Install and run hello world" failed: missing pip command

4. [PARTIAL] docs/how-to/auth.md
   Goal "Set up authentication" achievable but confusing step ordering

### Custom
5. Describe something else: ___

Select issues to fix (e.g., "1,3,5"):
```

After selection, the skill spawns Author to rewrite targeted content, then Editor to run quality passes on changed pages only. No Persona re-run.

**Confidence:** HIGH -- directly implements CONTEXT.md locked decision about report-driven multi-select with freeform option.

### Anti-Patterns to Avoid

- **Using `context: fork` for orchestration skills:** Forked skills lose access to the conversation. The project author cannot approve PARTIALs, see progress, or interact. Orchestration MUST run in the main conversation.

- **Creating an orchestrator agent:** Subagents cannot spawn other subagents. An `agents/doc-orchestrator.md` file would be a dead end -- it could not invoke the Agent tool to spawn Author, Editor, or Persona. This is explicitly documented in CC's subagent docs.

- **Gap detection via dynamic context injection:** `!`command`` runs before Claude processes anything. The gap scan needs config values (source_root, language) that Claude reads from `.doc-writer/config.yaml`. Use explicit Bash tool call instead.

- **Committing generated docs automatically:** CONTEXT.md locked decision: "Generated docs are left uncommitted -- project author reviews diff and commits when satisfied." The skills must NOT run `git add` or `git commit`.

- **Running Persona after /doc:edit:** CONTEXT.md locked decision: "No Persona re-run after edit." The project author can run `/doc:review` afterwards if they want full validation.

- **Regenerating scenarios during revision passes:** The Persona prompt already handles this (from Phase 4), but the orchestration skill must also ensure it does NOT tell the Persona to generate fresh scenarios when it is a revision pass.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Subagent spawning | Custom orchestration code or process management | CC Agent tool | CC handles subagent lifecycle, context isolation, result return; subagents already defined in `agents/` |
| Export symbol scanning | Claude reading all source files | Shell script (`scan-exports.sh`) via Bash tool | Avoids filling Claude's context with raw source code; shell grep is faster and more reliable for pattern matching |
| Multi-audience parallel execution | Custom parallel framework | Sequential Agent tool calls (CC handles concurrency) | CC may parallelize Agent calls when independent; if not, sequential is fine -- each Persona runs in its own context |
| YAML config parsing | Custom parser | Claude reads `.doc-writer/config.yaml` via Read tool | Claude natively understands YAML; no parsing library needed |
| Report parsing for /doc:edit | Regex-based report parser | Claude reads editor-report.md and persona-report.md via Read tool | Claude natively understands the report format it defined; structured sections with headers make parsing trivial |
| Pipeline state tracking | State management library or database | Claude's conversational memory within the skill execution | The skill runs in the main conversation; Claude remembers which pass it is on, what verdicts were received, etc. |

**Key insight:** The orchestration skills have the same zero-dependency property as the agents. They are markdown files containing instructions. Claude is both the runtime and the state manager. The only runtime dependency is the gap detection shell script, which uses standard Unix tools (grep, awk).

## Common Pitfalls

### Pitfall 1: Subagent Cannot Spawn Subagents

**What goes wrong:** An orchestrator agent is created in `agents/doc-orchestrator.md` to manage the pipeline. When it tries to spawn Author via the Agent tool, the call fails silently or is not available.
**Why it happens:** CC explicitly prohibits subagent nesting: "Subagents cannot spawn other subagents."
**How to avoid:** All orchestration must happen at the skill level (main conversation context). Skills can use the Agent tool freely. Never create an orchestrator as an agent file.
**Warning signs:** Agent tool calls fail or are not listed in the subagent's available tools.

### Pitfall 2: Using context: fork and Losing User Interaction

**What goes wrong:** The `/doc:write` skill uses `context: fork` and runs the entire pipeline in isolation. When PARTIALs need approval, the skill cannot prompt the user because forked contexts do not have access to the conversation.
**Why it happens:** `context: fork` seems appropriate for long-running operations, but it isolates the skill completely.
**How to avoid:** Do NOT use `context: fork` for any of the three commands. They must run in the main conversation context where Claude can interact with the project author.
**Warning signs:** PARTIAL approval UX never triggers; user sees only a final summary with no opportunity to approve fixes.

### Pitfall 3: Gap Detection Script Path Resolution

**What goes wrong:** The gap detection script fails because the path uses `${CLAUDE_PLUGIN_ROOT}` but resolves incorrectly, or the script is not executable.
**Why it happens:** Path resolution differs between `--plugin-dir` development mode and marketplace installation; scripts need `chmod +x`.
**How to avoid:** Always use `${CLAUDE_PLUGIN_ROOT}` for script paths. Ensure the script has executable permissions. Test with both `--plugin-dir` and after copying to plugin cache.
**Warning signs:** "Permission denied" or "No such file or directory" errors when running the scan script.

### Pitfall 4: Gap Detection False Positives

**What goes wrong:** The export scanner identifies internal helpers, private utilities, or test fixtures as "undocumented public API." The Author wastes effort documenting internal implementation details.
**Why it happens:** Simple grep-based scanning cannot perfectly distinguish public API from internal helpers in all languages. Python files without `__all__` export everything; TypeScript barrel files re-export internal modules.
**How to avoid:** The script should prioritize `__all__` when present in Python, focus on top-level module exports in TypeScript, and skip test directories. Claude should also filter the raw scan results against the CONTEXT.md principle: "Public API surface = exported symbols only." The Author already filters internal details (Phase 2 AUTH-03).
**Warning signs:** Gap report contains dozens of internal function names that clearly should not be in user docs.

### Pitfall 5: Revision Loop Infinite Context Growth

**What goes wrong:** After 3 revision passes (initial + 2 revisions), each spawning Author + Editor + Persona, the main conversation's context is consumed by Agent tool result summaries, making it impossible to present the final summary or handle PARTIAL approval.
**Why it happens:** Each Agent tool call returns a summary of the subagent's work. With 3 passes x 3+ agents per pass, that is 9+ agent summaries in context.
**How to avoid:** The skill should instruct Claude to keep delegation messages concise and focused. Agent results naturally summarize. If context pressure becomes an issue, the skill can instruct Claude to compact intermediate results into brief status notes.
**Warning signs:** Claude produces truncated or confused summaries at the end of multi-pass pipelines.

### Pitfall 6: /doc:edit Without Prior Reports

**What goes wrong:** User runs `/doc:edit` before running `/doc:write` or `/doc:review`. No reports exist, so the issue selection list is empty.
**Why it happens:** The edit skill assumes reports exist from a prior pipeline run.
**How to avoid:** The skill must check for report files and present a clear message if none exist: "No editor or persona reports found. Run `/doc-writer:review` first to generate an issues report, or use the freeform option below to describe specific changes." The freeform option should always be available.
**Warning signs:** Empty issue list with no explanation.

### Pitfall 7: Plugin Namespace Mismatch

**What goes wrong:** Skills are invoked as `/doc:write` but the actual command becomes `/doc-writer:write` due to plugin namespacing.
**Why it happens:** Plugin skills are namespaced as `plugin-name:skill-name`. The plugin is named "doc-writer" in plugin.json, so skills become `/doc-writer:write`, `/doc-writer:review`, `/doc-writer:edit`.
**How to avoid:** Accept the namespacing. The commands will be `/doc-writer:write`, `/doc-writer:review`, `/doc-writer:edit`, and `/doc-writer:setup`. Update all documentation and user-facing references accordingly. The CONTEXT.md uses shorthand `/doc:write` but the actual invocations will use the full plugin namespace.
**Warning signs:** User tries `/doc:write` and gets "command not found."

### Pitfall 8: Multi-Audience Persona Reports Not Collected

**What goes wrong:** With multiple audiences, the orchestration skill spawns Persona for audience A, processes its report, then spawns Persona for audience B -- but forgets to check audience A's report when routing revision.
**Why it happens:** The skill must aggregate verdicts across ALL audience reports before making revision decisions.
**How to avoid:** The skill should explicitly collect all persona reports (`.doc-writer/persona-report-{audience-name}.md`) after all Persona runs complete. Revision is triggered if ANY audience has a FAIL. The summary report should show per-audience results.
**Warning signs:** Revision only addresses one audience's FAILs while another audience still has FAILs.

## Code Examples

### /doc:write Skill Structure

```yaml
# Source: CC skills docs (code.claude.com/docs/en/skills) + project conventions
---
name: write
description: Generate new documentation using the full Author > Editor > Persona pipeline with gap detection, revision loop, and quality validation.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
argument-hint: "[--skip-gap-scan]"
---

# Doc Writer: Full Pipeline

You are orchestrating the doc-writer pipeline. Follow these steps exactly.

## Pre-Flight

1. Read `.doc-writer/config.yaml` for audiences, doc_system, paths
2. If config does not exist, tell the user to run `/doc-writer:setup` first and stop
3. Note the number of configured audiences (for Persona count)

## Step 1: Gap Detection

[Unless $ARGUMENTS contains "--skip-gap-scan"]

1. Read `detected.language` from config
2. Run: `bash ${CLAUDE_PLUGIN_ROOT}/skills/write/scripts/scan-exports.sh {paths.source_root} {detected.language}`
3. Read existing docs in `paths.docs_root` to identify which symbols are already documented
4. Write gap report to `.doc-writer/gap-report.md`:
   - List each exported symbol not found in any doc page
   - Group by module/file
   - Note total count

## Step 2: Author

Spawn the doc-author agent:

Agent(doc-author): "Generate documentation for this project.
Read .doc-writer/config.yaml for configuration.
Read .doc-writer/gap-report.md for undocumented symbols to prioritize.
{If revision pass: 'This is revision pass N. Revise ONLY these pages based on Persona FAIL verdicts: {page_list}. Read .doc-writer/persona-report.md for specific gaps.'}"

Wait for Author to complete.

## Step 3: Editor

[... similar pattern ...]

## Step 4: Persona (per audience)

[... spawns one Persona per audience ...]

## Step 5: Verdict Check and Revision Routing

[... state machine logic ...]

## Step 6: PARTIAL Approval

[... batch presentation of PARTIAL fixes ...]

## Step 7: Summary Report

[... final report ...]
```

### /doc:review Skill Structure

```yaml
---
name: review
description: Audit existing documentation without generating new content. Runs Editor quality checks and Persona validation, plus gap detection.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep, Bash
---

# Doc Writer: Review Existing Docs

## Pre-Flight
1. Read `.doc-writer/config.yaml`
2. Verify docs exist in `paths.docs_root`

## Step 1: Gap Detection
[Same as /doc:write]

## Step 2: Editor (Audit Mode)
Agent(doc-editor): "Review the documentation in {docs_root}.
Run all three passes but focus on reporting issues.
Write your report to .doc-writer/editor-report.md."

## Step 3: Persona (per audience)
[Same as /doc:write -- spawns Persona per audience]

## Step 4: Present Results
Combine editor-report.md and persona-report(s) into a summary.
No revision loop. No content generation.
Present the audit results to the project author.
```

### /doc:edit Skill Structure

```yaml
---
name: edit
description: Make targeted fixes to documentation based on specific issues or freeform instructions.
disable-model-invocation: true
allowed-tools: Agent, Read, Write, Glob, Grep
argument-hint: "[issue description]"
---

# Doc Writer: Targeted Edit

## Step 1: Collect Issues
1. Read `.doc-writer/editor-report.md` if it exists
2. Read `.doc-writer/persona-report*.md` files if they exist
3. Present issues as a numbered list grouped by source (Editor / Persona)
4. Include a freeform option at the end

If $ARGUMENTS is provided, use it as the freeform instruction
and skip the selection prompt.

## Step 2: Author Revision
Agent(doc-author): "Revise the following specific issues in the documentation:
{selected_issues_with_details}
Read .doc-writer/config.yaml for configuration.
Only modify the pages listed. Do not regenerate other pages."

## Step 3: Editor Quality Pass
Agent(doc-editor): "Edit the revised pages: {changed_pages}.
Run all three passes on changed pages.
Run full terminology scan across all files."

## Step 4: Done
Present what was changed. No Persona re-run.
Docs are left uncommitted.
```

### Gap Detection Script

```bash
#!/bin/bash
# scan-exports.sh -- scan source code for exported symbols
# Usage: scan-exports.sh <source_root> <language>
# Output: one symbol per line in format "file:line:symbol_name"

SOURCE_ROOT="${1:-.}"
LANG="${2:-unknown}"

# Skip common non-source directories
EXCLUDE_DIRS="--exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=.git --exclude-dir=dist --exclude-dir=build --exclude-dir=test --exclude-dir=tests --exclude-dir=spec"

case "$LANG" in
  python)
    # Prefer __all__ when available
    echo "## Python Exports (from __all__)"
    grep -rn '__all__' "$SOURCE_ROOT" --include="*.py" $EXCLUDE_DIRS 2>/dev/null || true
    echo ""
    echo "## Python Public Functions and Classes"
    grep -rn '^def [^_]' "$SOURCE_ROOT" --include="*.py" $EXCLUDE_DIRS 2>/dev/null || true
    grep -rn '^class [^_]' "$SOURCE_ROOT" --include="*.py" $EXCLUDE_DIRS 2>/dev/null || true
    echo ""
    echo "## Python Public Constants"
    grep -rn '^[A-Z][A-Z_]*\s*=' "$SOURCE_ROOT" --include="*.py" $EXCLUDE_DIRS 2>/dev/null || true
    ;;
  typescript|javascript)
    echo "## TypeScript/JavaScript Exports"
    grep -rn '^export ' "$SOURCE_ROOT" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" --include="*.mts" --include="*.mjs" $EXCLUDE_DIRS 2>/dev/null || true
    ;;
  rust)
    echo "## Rust Public Items"
    grep -rn '^pub ' "$SOURCE_ROOT" --include="*.rs" $EXCLUDE_DIRS 2>/dev/null || true
    ;;
  go)
    echo "## Go Exported Items"
    grep -rn '^func [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE_DIRS 2>/dev/null || true
    grep -rn '^type [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE_DIRS 2>/dev/null || true
    grep -rn '^var [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE_DIRS 2>/dev/null || true
    grep -rn '^const [A-Z]' "$SOURCE_ROOT" --include="*.go" $EXCLUDE_DIRS 2>/dev/null || true
    ;;
  *)
    echo "Language '$LANG' not directly supported for export scanning."
    echo "Claude will scan source files manually."
    ;;
esac
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `commands/` directory for slash commands | `skills/` directory with SKILL.md | 2025 (CC skills merged with commands) | Skills are officially recommended; commands still work but skills support directories, supporting files, invocation control |
| Task tool for spawning subagents | Agent tool (Task still works as alias) | CC v2.1.63 | New code should use Agent; Task is deprecated alias |
| Manual pipeline execution | Skill-based orchestration with Agent tool | Phase 5 | Users invoke `/doc-writer:write` instead of manually spawning agents in sequence |
| No gap detection | Shell script + Claude comparison | Phase 5 | INTG-05: undocumented exported symbols identified before Author writes |

**Deprecated/outdated:**
- `commands/` directory: still works, but `skills/` is recommended for new components
- Task tool name: renamed to Agent in CC v2.1.63; Task works as alias
- The shorthand `/doc:write` from CONTEXT.md: actual plugin invocations will be `/doc-writer:write` due to plugin namespacing

## Open Questions

1. **Plugin namespace shorthand**
   - What we know: Plugin skills are namespaced as `plugin-name:skill-name`. The plugin is named "doc-writer" so commands become `/doc-writer:write`.
   - What's unclear: Whether the CONTEXT.md shorthand `/doc:write` was intentional (expecting a shorter namespace) or informal (accepting that it will be `/doc-writer:write`).
   - Recommendation: Accept `/doc-writer:write` as the actual invocation. Document both the full name and the shorthand in user-facing instructions. The plugin name "doc-writer" is already set in plugin.json.

2. **Multi-audience Persona parallelism**
   - What we know: Multiple audiences spawn separate Persona agents. CC can run Agent tool calls in parallel when independent.
   - What's unclear: Whether Claude will naturally parallelize multiple Agent(doc-persona) calls or run them sequentially.
   - Recommendation: Instruct the skill to explicitly request parallel execution: "For each audience, spawn a Persona agent. These can run in parallel since they produce independent reports." If CC does not support parallel Agent calls from a skill, sequential execution is acceptable -- each Persona run is fast (read-only evaluation).

3. **Gap detection script robustness across languages**
   - What we know: The shell script uses grep patterns for Python, TypeScript, Rust, and Go.
   - What's unclear: Edge cases in each language (Python packages without `__all__`, TypeScript re-exports from barrel files, Rust `pub(crate)` vs `pub`, Go internal packages).
   - Recommendation: Ship a basic working script for v1. Claude can supplement with manual source scanning for languages or patterns the script misses. The script is a starting point, not a complete solution.

4. **Skill body length for /doc:write**
   - What we know: The /doc:write skill has the most complex orchestration (gap scan, Author, Editor, multi-Persona, revision loop, PARTIAL approval, summary). CC docs recommend keeping SKILL.md under 500 lines.
   - What's unclear: Whether all orchestration steps fit within a reasonable skill length.
   - Recommendation: Target 300-400 lines for the /doc:write SKILL.md. Use clear section headers and concise instructions. If the skill exceeds 500 lines, move reference material (summary report template, escalation format) to supporting files in the `skills/write/` directory.

5. **PARTIAL approval mechanism**
   - What we know: The skill runs in the main conversation where Claude can interact with the user. PARTIAL fixes should be presented as a batch.
   - What's unclear: Exactly how Claude prompts for multi-select approval in the CC interface. There is no formal multi-select UI -- Claude presents text and the user responds.
   - Recommendation: Present PARTIAL fixes as a numbered list and ask the user to respond with numbers (e.g., "1,3,5"), "all", or "none". This is a text-based interaction within the normal CC conversation flow.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual CC session testing (no automated test framework) |
| Config file | None -- this is a markdown-file plugin with no executable code |
| Quick run command | `claude --plugin-dir .` then invoke `/doc-writer:write` on a sample project with `.doc-writer/config.yaml` |
| Full suite command | Manual: run all three commands on a sample project, verify all 5 INTG requirements |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INTG-01 | `/doc-writer:write` runs full pipeline and produces docs | manual (CC session) | Invoke `/doc-writer:write` on sample project; verify Author runs, Editor edits, Persona evaluates; docs appear in `paths.docs_root` uncommitted | N/A -- markdown plugin |
| INTG-02 | `/doc-writer:review` runs Editor + Persona audit, no content generation | manual (CC session) | Invoke `/doc-writer:review` on project with existing docs; verify editor-report.md and persona-report.md produced; verify NO doc files were modified | N/A |
| INTG-03 | `/doc-writer:edit` presents issues and applies targeted fixes | manual (CC session) | Invoke `/doc-writer:edit` after a review; verify issues from reports are presented; select issues; verify only targeted pages are modified | N/A |
| INTG-04 | Plugin works in GSD sessions | manual (GSD + CC session) | From a GSD session, invoke `/doc-writer:write`; verify the command is available and runs normally | N/A |
| INTG-05 | Gap detection reports undocumented exported symbols | manual (inspect output) | Invoke `/doc-writer:write` on a project with known undocumented exports; verify `.doc-writer/gap-report.md` lists them; verify gap report appears in summary | N/A |

### Sampling Rate
- **Per task commit:** Manual: load plugin with `claude --plugin-dir .`, run the specific command being implemented
- **Per wave merge:** Manual: run all three commands in sequence on a sample project, verify all INTG requirements
- **Phase gate:** All 5 INTG requirements verified via manual CC session before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Ensure sample project has `.doc-writer/config.yaml` (from Phase 1 setup)
- [ ] Ensure sample project has existing docs in `paths.docs_root` (for /doc:review and /doc:edit testing)
- [ ] Ensure sample project has source code with exported symbols (for gap detection testing)
- [ ] Ensure `scan-exports.sh` is executable: `chmod +x skills/write/scripts/scan-exports.sh`
- [ ] Prepare a sample project where at least one exported function has no documentation (for INTG-05 verification)
- [ ] Prepare editor-report.md and persona-report.md from a prior run (for /doc:edit testing without running full pipeline first)

## Sources

### Primary (HIGH confidence)
- [CC Skills documentation](https://code.claude.com/docs/en/skills) -- skill format, frontmatter fields, invocation control, `disable-model-invocation`, `allowed-tools`, `$ARGUMENTS`, `context: fork`, `!`command`` dynamic context injection, supporting files, 500-line recommendation
- [CC Plugins reference](https://code.claude.com/docs/en/plugins-reference) -- plugin manifest schema, directory structure (skills/, agents/, commands/ at plugin root), `${CLAUDE_PLUGIN_ROOT}`, component path fields, standard plugin layout
- [CC Subagents documentation](https://code.claude.com/docs/en/sub-agents) -- Agent tool (renamed from Task), subagent spawning, "subagents cannot spawn other subagents" constraint, delegation messages, parallel execution, `skills:` preloading, tool restrictions
- Direct file reads of `agents/doc-author.md` (428 lines), `agents/doc-editor.md` (390 lines), `agents/doc-persona.md` (403 lines) -- verified all agent frontmatter formats, system prompt conventions, artifact file paths, pipeline contracts
- Direct file read of `.claude-plugin/plugin.json` -- verified plugin name is "doc-writer" (commands will be `/doc-writer:{name}`)
- Direct file read of `skills/setup/SKILL.md` (Phase 1) -- verified existing skill pattern: frontmatter with `disable-model-invocation: true`, `allowed-tools`, supporting files in `defaults/` and `scripts/`
- Phase 1 research (`01-RESEARCH.md`) -- CC plugin architecture, skill format, agent format, all verified HIGH confidence
- Phase 4 research (`04-RESEARCH.md`) -- revision loop protocol, multi-audience execution, Persona report format, all verified HIGH confidence

### Secondary (MEDIUM confidence)
- Phase 5 CONTEXT.md -- locked user decisions governing pipeline orchestration, command behavior, gap detection scope, GSD integration approach, PARTIAL approval UX
- REQUIREMENTS.md -- INTG-01 through INTG-05 requirement definitions; out-of-scope declaration (no automated publishing)
- STATE.md -- project decisions history; blocker: "CC Marketplace distribution format is TBD" (not relevant to Phase 5 command creation)

### Tertiary (LOW confidence)
- Gap detection script robustness across all languages -- grep-based patterns cover common cases but edge cases (re-exports, `pub(crate)`, `__all__` parsing) are language-specific and may need refinement per-project

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- CC skill format, Agent tool, plugin structure all verified against official docs; existing project conventions well-established across 4 completed phases
- Architecture: HIGH -- skill-based orchestration is the only viable approach (subagents cannot spawn subagents); `context: fork` incompatible with interactive PARTIAL approval; both constraints verified from official CC docs
- Pitfalls: HIGH -- subagent nesting prohibition, fork isolation, namespace mismatch, revision loop context growth all documented with specific prevention strategies
- Gap detection: MEDIUM -- approach is sound (shell script + Claude comparison), but per-language export scanning has known edge cases that will need refinement

**Research date:** 2026-03-04
**Valid until:** 2026-04-04 (CC plugin system is stable; locked user decisions do not change; 30-day validity appropriate)
