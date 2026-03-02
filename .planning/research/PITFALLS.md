# Domain Pitfalls

**Domain:** AI doc-writing agent / multi-agent documentation pipeline / Claude Code plugin
**Researched:** 2026-03-02
**Confidence Note:** Web search and fetch tools unavailable for this session. All findings are from training knowledge (cutoff August 2025), which is substantive for this domain. Confidence levels reflect verifiability, not quality of knowledge.

---

## Critical Pitfalls

Mistakes that cause rewrites, broken user trust, or fundamental product failure.

---

### Pitfall 1: The Insider Perspective Never Gets Fixed

**What goes wrong:** The Author agent writes from "what the code does" rather than "what the user needs to accomplish." Even when prompted to write for users, the agent defaults to implementation-first framing: describing parameters before use cases, explaining internals before outcomes, and structuring pages around code architecture rather than user goals.

**Why it happens:** The agent's context is the source code, not the user's mental model. LLMs anchor to what's most prominent in context — the code itself. Without an explicit forcing function, the default output is "maintainer docs with friendly tone" not "user docs."

**Consequences:** Docs pass automated checks, look complete, but users consistently fail to onboard. The Editor and User Persona agents can catch this but only if they have explicit criteria for flagging perspective failures — not just prose quality.

**Prevention:**
- User Persona agent must have a mandate to **reject** (not just annotate) docs that require implicit knowledge of the implementation
- Define "perspective test" rules explicitly: "Can a user who has never read the source code follow this without confusion?"
- Author agent's initial prompt must include known user mental models / audience background, not just project description
- Editor agent should check that use-case framing precedes API detail, not the reverse

**Detection (warning signs):**
- Docs mention internal module names, file paths, or function names that are implementation details
- Getting-started guide requires understanding the project's internal architecture
- Every example shows the full API surface rather than the simplest path to a goal
- Parameter tables appear before "when would I use this" context

**Phase:** Core architecture (agent prompt design). Must be solved in the first working pipeline — retrofitting perspective rules into a working pipeline is painful.

---

### Pitfall 2: Infinite Revision Loop Between Agents

**What goes wrong:** Editor and User Persona agents flag issues; Author agent revises; Editor and User Persona re-flag the same or new issues; the loop never terminates. In a multi-agent system without a convergence mechanism, each revision pass can introduce new issues even while fixing old ones.

**Why it happens:** No exit condition defined. Each review agent applies its full ruleset every pass. Author agent interprets feedback literally and may over-correct (e.g., adding too many examples in response to "needs examples" feedback, which then gets flagged as "too verbose"). Without a convergence threshold, the system has no signal for "good enough."

**Consequences:** Token costs explode. User waits indefinitely. Output may actually degrade as agents negotiate competing priorities across many passes.

**Prevention:**
- Define maximum revision passes (2-3 is usually sufficient; 4+ indicates a systemic problem)
- Require review agents to distinguish between **blocking** issues (must fix before publish) and **suggestions** (could improve)
- Only blocking issues trigger another Author revision pass
- Implement a "convergence check": if the same blocking issue appears in two consecutive passes, escalate to the user rather than looping again
- Track which issues were already addressed so agents don't re-raise resolved items

**Detection (warning signs):**
- First implementation has no pass limit — it's unbounded by design
- Review agents use identical checklists every pass (no memory of prior passes)
- Author agent prompt doesn't instruct it to preserve what was working, only to fix what was flagged

**Phase:** Pipeline design (before first end-to-end run). This must be designed in, not patched in.

---

### Pitfall 3: Quality Rules Become the Product Instead of Docs

**What goes wrong:** The system over-indexes on rule compliance and produces docs that technically satisfy every rule but read as mechanical and joyless. Every section has exactly the required structure. Every example is minimal and correct but demonstrates nothing interesting. The docs are rule-compliant but not genuinely useful.

**Why it happens:** Rules are easier to measure than quality. Agents optimize for what they can verify. When the Editor agent's job is "check rules," it will check rules — and if rules are the only signal, rule compliance becomes the goal.

**Consequences:** Users read the docs and feel vaguely unsatisfied without being able to articulate why. The docs aren't wrong, they're just uninspiring and miss the "aha moment" that good docs deliver.

**Prevention:**
- Include qualitative success criteria alongside rules: "Would an experienced developer actually recommend this page to a newcomer?"
- User Persona agent's role is specifically to catch rule-compliant-but-unhelpful content — give it explicit permission to flag this
- At least one rule should encode "narrative quality": the docs should tell a coherent story about how to solve a problem, not just enumerate capabilities
- Rules should be versioned and periodically reviewed — a rule that seemed good at design time may prove too rigid in practice

**Detection (warning signs):**
- Examples are syntactically correct but contrived (`doThing("example", 42)` with no context)
- Every page has identical structure even when the content type would benefit from variation
- Getting-started guide covers all features rather than the fastest path to success
- No page has a "you might be wondering" or "why does this work this way" moment

**Phase:** Quality rules design. Rules need a "spirit" description alongside their mechanical definition.

---

### Pitfall 4: Context Overload Degrades Output Quality

**What goes wrong:** Passing all source code, all existing docs, and all project context into every agent call causes the agent to produce generic or unfocused output. The agent "knows" too much and produces docs that try to address every edge case and internal nuance rather than focusing on what a typical user needs.

**Why it happens:** LLMs attend to all context when generating. More context is not always better — it can cause the agent to include information that's technically true but irrelevant to the user's goal. Maintainer details (dev scripts, CI config, test utilities) in context will leak into output unless explicitly filtered.

**Consequences:** Docs are comprehensive but unfocused. Users can't find what they need. The specific problem from PROJECT.md — internal details leaking into user docs — is actively caused by feeding the agent internal context without filtering.

**Prevention:**
- Filter context before passing to agents: strip test files, CI configs, justfile/Makefile, dev-only scripts, internal utilities
- Pass source code of public API surface only (what's exported/published), not internal implementation files
- Separate "project background" context (for agent understanding) from "citable content" context (what the agent should document)
- Author agent receives public API context; Editor and User Persona receive output docs — not raw source
- Document what NOT to include in context as explicitly as what to include

**Detection (warning signs):**
- Generated docs mention test utilities, fixture data, or dev-only configuration
- Docs describe how to run the dev environment or CI pipeline
- Pages include implementation details that aren't part of the public interface
- Author agent output includes comments like "this internal helper function..."

**Phase:** Input pipeline design. Solved at the point where context is assembled before agent invocation.

---

### Pitfall 5: User Persona Agent Is Just a Checklist Runner

**What goes wrong:** User Persona agent is implemented as "apply these checks from a user perspective" rather than genuinely simulating a user who has a goal and is trying to accomplish it using only the docs. The result is a review that catches surface-level issues (missing examples, passive voice) but misses deep usability failures (user can't figure out how to do X even though X is documented).

**Why it happens:** It's much easier to implement "check these criteria" than "simulate a user journey." The scenario generation (mentioned in PROJECT.md) is the right approach but needs to be implemented as genuine goal-oriented testing, not criterion testing.

**Consequences:** Docs that pass User Persona review still fail users in practice. The agent provides false confidence.

**Prevention:**
- User Persona must generate concrete user journeys: "I want to do X. I start at the Getting Started page. Following only what's written here, can I accomplish X?" — not "Does this page have a code example?"
- Generated scenarios must be diverse: include a skeptical user, a confused user, a power user trying to do something advanced
- Scenarios must be generated from project context (what users actually want to do) not from the docs themselves
- Agent must be willing to declare "FAIL: user cannot accomplish this goal from docs alone" — not just "here are suggestions"
- Test scenarios should be saved and reused across runs so improvements can be validated

**Detection (warning signs):**
- User Persona feedback is always a list of additions ("add this, clarify that") never a hard stop ("this page doesn't work for its purpose")
- Feedback doesn't reference specific user goals, only abstract quality criteria
- Every page gets the same type of feedback regardless of its purpose

**Phase:** User Persona agent design. Scenario generation is the core differentiator of this project — it must be implemented with depth.

---

### Pitfall 6: Agent Coordination via Loose Natural Language Breaks Down at Scale

**What goes wrong:** Agents communicate review findings as free-form prose. Author agent interprets feedback differently than intended. Important blocking issues get buried in paragraphs of suggestions. Minor suggestions get treated as requirements. Signal-to-noise degrades across revisions.

**Why it happens:** Free-form prose is the natural output of LLMs, but it's ambiguous for downstream consumption. "Consider adding more examples to the installation section" could mean "this is required" or "this would be nice." An Author agent reading this has no reliable way to triage.

**Consequences:** Author agent makes wrong changes. Blocking issues are missed. Suggestions get implemented when they shouldn't. Revision passes compound the confusion.

**Prevention:**
- Define a structured feedback format for review agents: each issue must include severity (BLOCKING / SUGGESTION / NITPICK), location (page + section), description, and what fix looks like
- Author agent only responds to BLOCKING items in revision passes
- SUGGESTION items are surfaced to the user as "recommended improvements" but don't trigger revision
- Format must be enforced in the review agent's prompt with examples — not just described

**Detection (warning signs):**
- Review agents output prose paragraphs, not structured lists
- Author agent revision changes things that weren't flagged as issues
- Two revision passes produce contradictory changes
- No clear way to tell which issues were resolved vs still open after a revision

**Phase:** Agent interface design. This is infrastructure that must be in place before testing the full pipeline.

---

## Moderate Pitfalls

---

### Pitfall 7: Diataxis Framework Applied Mechanically Without Understanding

**What goes wrong:** Author agent classifies content into Tutorial / How-To / Reference / Explanation, then generates each type with the right structure — but doesn't understand that the *most important* Diataxis insight is keeping these types separate and resisting the urge to mix them. The agent writes a "tutorial" that's actually a reference with narrative coating, or a "how-to" that explains why things work (which belongs in Explanation).

**Why it happens:** Diataxis structure is easy to teach mechanically (four boxes, four structures). The deeper principle — that mixing types serves neither purpose well — requires understanding, not just pattern-matching.

**Consequences:** Pages feel off without users being able to explain why. A tutorial that mixes in reference material loses the learning arc. An Explanation page that includes step-by-step instructions isn't actually explaining anything.

**Prevention:**
- Author agent prompt must include Diataxis mixing prohibition, not just four-type definitions
- Include concrete examples of bad mixing: "Don't do this: [tutorial that includes a reference table mid-flow]"
- Editor agent should specifically check for type mixing as a named rule
- Existing diataxis-documentation skill's guidance should be audited for whether it covers the mixing prohibition

**Detection (warning signs):**
- Tutorial pages have API parameter tables in them
- Reference pages include "you might want to do this when..." guidance
- How-To pages explain background theory before the steps
- A single page tries to serve both "I want to learn" and "I want to look up" use cases

**Phase:** Author agent prompt design.

---

### Pitfall 8: CC Plugin Architecture Mismatches Agent Communication Needs

**What goes wrong:** Claude Code's plugin/skill system may not natively support the stateful multi-agent pipeline needed (Author writes, Editor reviews, Author revises with Editor's feedback, User Persona reviews, final output). Attempting to implement this as a sequence of independent slash commands loses state between steps.

**Why it happens:** CC plugins are designed for relatively self-contained tasks. A multi-pass review pipeline needs shared state (current draft, feedback history, issue list, pass count) that may require explicit file-based handoffs or orchestrator patterns not native to CC's skill system.

**Consequences:** Either the pipeline is a single monolithic prompt (loses agent specialization benefits) or state management becomes a hand-rolled solution that's fragile.

**Prevention:**
- Research CC's actual orchestration primitives before designing agent communication (subagents? file handoffs? orchestrator pattern?)
- Treat the filesystem as the communication medium: each agent reads the current draft from a temp file, writes its output to a known location
- Design for the simplest possible state model first — a single working pipeline before optimization
- Keep the orchestrator thin: it routes, it doesn't reason

**Detection (warning signs):**
- First design assumes in-memory state passing between agents
- No explicit answer to "where does the draft live between agent calls?"
- Pipeline can't be resumed if interrupted mid-way

**Phase:** Foundation / architecture phase. Must be resolved before building agent logic.

---

### Pitfall 9: Per-Project Config Becomes Configuration Hell

**What goes wrong:** The layered rules system (universal defaults + project config) becomes overly complex as projects add custom rules. Users accumulate rules that conflict with universal defaults, override each other unpredictably, or become stale as the project evolves. The config becomes a maintenance burden rather than a productivity tool.

**Why it happens:** Configuration systems grow organically. Each addition seems reasonable individually but the aggregate becomes unmanageable. There's no cleanup mechanism and no way to see what's actually active.

**Consequences:** Users spend more time managing config than writing docs. Rules conflict silently and produce confusing output. A new team member can't understand what rules are in effect.

**Prevention:**
- Keep universal rules minimal (5-7 max) and well-justified — resist adding more defaults over time
- Config schema should prevent conflicting rules at write time, not just at run time
- Provide a "show active rules" command that lists all rules with their source (universal / project config) and their effect
- Config format should be human-readable and minimal (YAML or simple JSON, not a DSL)
- Rules should have a description field explaining their intent, not just their mechanical effect

**Detection (warning signs):**
- Config file has more than ~10 project-specific rules
- Rules reference other rules (chained dependencies)
- No way to audit which rules are active during a run
- Users copy-paste rules without understanding their effect

**Phase:** Configuration design. Schema and validation should be defined early even if the rule set starts minimal.

---

### Pitfall 10: Audience Confusion Breaks Everything Downstream

**What goes wrong:** The Q&A setup to configure audience is ambiguous, the user gives a vague answer ("developers"), and all three agents operate with a vague audience model. Agents can't make concrete decisions about what to include or exclude, how technical to be, or what prior knowledge to assume. Everything is hedged.

**Why it happens:** Audience definition feels like an administrative task, not a core technical problem. Setup Q&A may feel thorough while actually being underspecified ("who are your users?" elicits "developers using Python" which tells agents almost nothing useful).

**Consequences:** Docs are calibrated for nobody. Too advanced for beginners, too basic for experts, wrong framing for the actual use case.

**Prevention:**
- Audience config must collect: skill level (what do they already know?), goal context (what are they trying to build?), likely entry point (where do they start?), and what to never assume
- Provide audience templates ("Python library users," "REST API consumers," "CLI tool users") as starting points
- User Persona agent's generated scenarios should be validated against the stated audience — if scenarios don't match, flag it
- Store audience config with enough detail that any agent could generate a concrete example user from it

**Detection (warning signs):**
- Audience config is a single sentence or single field
- Author agent output uses hedging language like "depending on your use case" constantly
- User Persona scenarios are generic (a "developer" doing "something") not specific

**Phase:** Setup / onboarding design. Audience definition is too important to be an afterthought in the Q&A flow.

---

### Pitfall 11: Humanizer Creates Inconsistency Across Pages

**What goes wrong:** The humanizer skill (used by the Editor) applies tone improvements page-by-page in isolation. Across a doc set, the voice becomes inconsistent: one page uses formal academic tone, another is conversational, a third is terse technical. No single reader reads only one page, and the inconsistency degrades trust.

**Why it happens:** Humanizer is naturally a local operation — improve this text. Without a doc-set-wide style guide enforced across all pages, each page optimizes locally.

**Consequences:** The doc set feels like it was written by different people (which, in a sense, it was — different agent invocations). Users notice even if they can't articulate it.

**Prevention:**
- Define a tone profile as part of project config: formality level (1-5), use of second person (always / sometimes / never), code-first vs prose-first preference, etc.
- Humanizer always receives the tone profile and applies it consistently
- Editor agent should explicitly check tone consistency against the profile, not just "is this humanized?"
- Consider generating a style guide page in the doc set itself — it creates a reference for the agents and helps maintainers too

**Detection (warning signs):**
- Two pages in the same doc set use different pronouns for the user ("the user" vs "you")
- Some pages use imperative ("Run the command") and others are passive ("The command should be run")
- Formality level varies noticeably between sections

**Phase:** Editor agent design + project config schema.

---

## Minor Pitfalls

---

### Pitfall 12: Output Assumes a Doc System That Isn't Present

**What goes wrong:** Author agent generates markdown with doc-system-specific frontmatter, admonitions, or directives (e.g., mkdocs-material `!!! note` blocks or Docusaurus `:::tip` blocks) even when no doc system is configured. Output is valid for one system but breaks in another or reads as raw markup.

**Prevention:** Default to plain markdown. Only use system-specific syntax when the project config explicitly specifies a doc system. Validate that system-specific syntax is only applied when the corresponding config is present.

**Phase:** Output format design.

---

### Pitfall 13: Existing Docs Treated as Ground Truth Instead of Draft

**What goes wrong:** When existing docs are passed as context, the Author agent treats them as authoritative and preserves their structure, framing, and errors. The output is improved existing docs rather than docs written from the user's perspective. The whole point of the tool — correcting the perspective problem — is undermined.

**Prevention:** Explicitly instruct the Author agent that existing docs are "reference only — not authoritative." The agent should extract facts from existing docs (what the library does) but regenerate structure and framing from scratch using the user perspective.

**Phase:** Author agent prompt design.

---

### Pitfall 14: Code Examples Are Technically Correct but Pedagogically Useless

**What goes wrong:** Universal rule enforces that every API has a code example. Examples are generated as minimal valid code that exercises the API, but they don't demonstrate a real use case. `client.connect("host", 8080)` is a code example; it satisfies the rule but teaches nothing.

**Prevention:** Code example rule must specify that examples must demonstrate a realistic scenario — not just valid syntax. Add a "context requirement": the example should include enough surrounding code that the reader understands why they'd write this. Editor reviews examples against this criterion specifically.

**Phase:** Quality rules design.

---

### Pitfall 15: Plugin Invocation Is Too Coarse-Grained

**What goes wrong:** Plugin only supports "document everything" mode. Users who want to document a single new function, update docs for one changed API, or add a how-to for one use case have to run the full pipeline and then discard most of the output.

**Prevention:** Design invocation modes from the start: full (all docs), targeted (specific module or function), incremental (only what changed since last run). Even if only full mode ships in v1, the invocation interface should be designed to support the others without breaking changes.

**Phase:** Plugin interface design / v1 scope definition.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Agent prompt design (Author) | Insider perspective never corrected | Explicit "perspective test" rules, user mental model in context |
| Agent prompt design (User Persona) | Checklist-runner not real simulation | Goal-oriented scenarios, hard fail option |
| Pipeline architecture | Infinite revision loops | Max pass limit, BLOCKING vs SUGGESTION distinction |
| Pipeline architecture | State loss between CC agent calls | File-based state handoffs, explicit draft location |
| Quality rules design | Rules become the product | Include qualitative criteria alongside mechanical rules |
| Context assembly | Internal details leak into output | Explicit context filter: strip test/CI/dev files |
| Agent communication | Free-form prose causes misinterpretation | Structured feedback format (severity, location, fix) |
| Config schema | Configuration hell | Minimal defaults, "show active rules" command, descriptions |
| Onboarding Q&A | Vague audience definition | Audience templates, required specificity fields |
| Editor agent + config | Tone inconsistency across pages | Tone profile in project config, Editor enforces it |
| Output format | Doc-system-specific syntax leaks | Plain markdown default, system syntax only when configured |
| Author prompt | Existing docs become ground truth | Explicit instruction: extract facts, regenerate framing |
| Code examples | Minimal-valid but pedagogically empty | Context requirement in code example rule |
| Plugin interface | Too coarse-grained for incremental use | Design invocation modes early even if only full ships in v1 |

---

## Sources

**Confidence assessment:**

| Area | Confidence | Notes |
|------|------------|-------|
| AI doc quality failures (perspective, insider bias) | HIGH | Well-documented failure mode in AI coding tools — directly observed pattern from multiple projects |
| Multi-agent coordination (loops, state, communication) | HIGH | Well-understood from AI systems design literature and CC agent documentation patterns |
| Diataxis framework misapplication | HIGH | Documented extensively by the Diataxis framework authors and community |
| CC plugin architecture constraints | MEDIUM | Based on CC documentation known at training cutoff (August 2025) — actual current primitives may have evolved |
| LLM context overload behavior | HIGH | Well-studied phenomenon in LLM research and applications |
| Quality rules / configuration design | MEDIUM | General software engineering principles applied to this domain — may need project-specific validation |

**Note:** Web search and fetch were unavailable during this research session. No external sources could be verified at time of writing. The MEDIUM-confidence items around CC plugin architecture should be verified against current CC documentation before Phase 1 design decisions are made.
