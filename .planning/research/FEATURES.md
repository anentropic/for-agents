# Feature Landscape

**Domain:** Multi-agent documentation writing and quality plugin for library/package documentation
**Researched:** 2026-03-02
**Confidence:** MEDIUM — based on training data (cutoff Aug 2025) + project context. External web access was unavailable during research. Core diataxis, Write the Docs, and documentation tooling knowledge is well-established and unlikely to have shifted materially.

---

## Table Stakes

Features users expect. Missing = product feels incomplete or untrustworthy.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Diataxis-aware content structuring | Industry standard for technical docs since ~2021; users expect tutorials, how-tos, reference, and explanation to be clearly separated | Low-Med | Must correctly classify doc type before writing, not just apply the label. Misclassification (tutorial written as explanation) is a common AI failure mode. |
| Working code examples in every API/feature page | The single most complained-about gap in library docs; users will not trust docs without runnable examples | Med | "Working" means syntactically correct and idiomatic — not pseudocode. Author agent must have access to source to generate faithful examples. |
| Consistent page structure per doc type | Users navigate by pattern; inconsistent headings/structure forces re-learning on every page | Low | Must be enforced by template, not style suggestion. Editor must flag structural divergence. |
| Correct audience scope (exclude internal details) | AI-generated docs routinely leak implementation notes, test utilities, CI config, dev scripts — users find this noise harmful | Med | Requires active filtering, not just writing well. Author must know what "internal" means for this project. |
| Inline code cross-referencing | Every `ClassName`, `method()`, `option` mentioned in prose should resolve to its API Reference entry | Med | Requires awareness of the project's reference index. Non-trivial for multi-file projects. |
| Project-specific audience configuration | Different libraries have different user profiles; "beginner Python user" vs "experienced systems engineer" require radically different vocabulary and assumed knowledge | Med | Must be set once and persist across sessions — per-project config, not per-run prompts. |
| On-demand invocation | Writers need control over when docs are generated; auto-triggering on every commit creates noise and trust issues | Low | Should be a command the user runs explicitly, not a hook that runs automatically. |
| Content-first, doc-system-agnostic output | Docs must be writable to mkdocs-material, Docusaurus, Sphinx, plain markdown — system-specific markup should be additive, not baked in | Med | Separation of content from presentation is a core constraint from PROJECT.md. |
| Access to full project context | Author needs source code, existing docs, README, changelogs, and config to write accurately. Docs written without source access contain invention and hallucination. | Low | CC plugin has access to workspace by default — this is about explicitly scoping what agents read, not adding new capability. |
| Minimal-tweak publishability | Output must reach "ready to publish with minor edits" quality — not "good first draft that needs heavy rework" | High | This is the core quality bar. Defines all review loops. Everything else serves this. |

---

## Differentiators

Features that set the product apart from manual doc writing or single-agent approaches.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Perspective-shifted User Persona review | The fundamental problem: builder-perspective docs fail users. A dedicated agent that reads docs as a first-time user and generates its own test scenarios (without manual authoring) surfaces gaps that the author and editor cannot see. | High | This is the core differentiator. No existing CC doc plugin does this. User Persona self-generating test scenarios (rather than having maintainer write them) is a key design choice from PROJECT.md. |
| Three-agent separation of concerns | Author writes, Editor enforces quality rules, User Persona validates audience fit — mirrors how real technical writing teams work. No context contamination between roles. | High | Pipeline order (serial vs parallel) is an open design question. The separation itself is the value, not the order. |
| Layered quality rules (universal + project-specific) | Universal rules enforce non-negotiable baseline quality across all projects. Project config adds audience, tone, doc-system, and custom rules without overriding fundamentals. | Med | The layering is critical — universal rules must be baked in and not bypassable via config. Project config should only extend, not override. |
| Humanized prose (not AI-sounding output) | AI-generated docs are recognizable and off-putting. A humanizer pass produces writing that reads like a senior developer wrote it, not a language model. | Med | Builds on existing humanizer skill. The differentiator is applying it as a structural review step, not an afterthought. |
| Gap detection (missing docs for shipped features) | Compares what the source code exposes vs. what is documented and surfaces undocumented APIs, options, and workflows. | High | Requires source analysis capability. Medium-confidence this is achievable; needs phase-specific research on CC's file analysis capabilities. |
| Cross-file consistency enforcement | When a concept is described differently on two pages (e.g., "plugin" on one page, "extension" on another), Editor detects and resolves. | Med-High | Requires Editor to maintain a concept glossary across the document set — stateful across files. |
| GSD milestone integration | Invokable at milestone boundaries within GSD workflow, not just standalone — docs stay current with each shipped feature set. | Low | Integration point, not a doc-writing feature. Low complexity once plugin interface is defined. |
| Per-audience vocabulary control | Two-audience projects (users vs contributors) get different vocabulary, assumed knowledge, and tone on the same codebase. Same API reference reads differently for each audience. | High | Requires audience awareness to propagate through Author and be validated by User Persona. Significant prompt engineering. |
| Extensible custom quality rules | Project maintainers can add domain-specific rules ("always use async/await, never .then()", "always mention the license for commercial use") that are enforced by Editor. | Med | Rule definition format must be simple enough for non-researchers to write. |
| Doc type classification before writing | Before drafting, Author determines whether each piece of content is a tutorial, how-to, reference, or explanation, and adjusts structure accordingly — not labeling after the fact. | Med | Prevents the common failure of blending doc types (tutorial that explains theory, reference that reads like a tutorial). |

---

## Anti-Features

Features to explicitly NOT build, with rationale.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Auto-generation of API reference from source code | Tools like TypeDoc, pdoc, rustdoc, javadoc already do this well and are maintained by the language ecosystem. Rebuilding this is wasted effort and will be worse. | Assume API reference exists or is generated by existing tooling; focus on narrative docs that link into it. |
| Doc site hosting or deployment | Infrastructure concerns (CDN, versioning, search indexing) are a different product. Adding them increases scope massively with low documentation value. | Output clean content; let maintainer deploy with their existing workflow. |
| Automated publishing (commit/push on completion) | Removes human review step. Documentation mistakes in production damage trust more than slow publication. Maintainer must have a review gate. | Output to a staging location or branch; make it easy for the maintainer to review and publish. |
| Non-library documentation (blog posts, marketing, wikis) | Different audiences, different quality bars, different frameworks. Dilutes the specialized prompt engineering that makes library docs good. | Scope hard to library/package documentation. Accept this limitation explicitly. |
| Real-time doc updating on every code change | Creates constant noise, conflicts with WIP branches, and generates docs for unfinished features. Users lose trust in output quality. | On-demand invocation only. Let maintainer decide the cadence. |
| Automated test coverage validation | Running actual code is outside the scope of a doc-writing agent and introduces execution environment complexity. | Verify code examples are syntactically correct and idiomatic; do not attempt to execute them. |
| Enforcing a specific doc system | Locking to mkdocs-material or Docusaurus excludes users on other systems. The content quality is what matters, not the rendering system. | Content-first output with optional doc-system-specific formatting rules in project config. |
| Interactive feedback loops during generation | Asking the user questions mid-generation ("What should I write for this section?") breaks the autonomous workflow and defeats the purpose. | Front-load configuration. Ask questions during setup Q&A, not mid-task. |
| Doc versioning management | Managing multiple versions of docs across releases is a deployment concern, not a writing concern. | Out of scope. Let the maintainer handle versioning with their existing tooling. |

---

## Feature Dependencies

```
Project context access (source + existing docs)
  └── Doc type classification
        └── Doc Author writing
              └── Diataxis-aware content structuring
              └── Working code examples
              └── Audience-appropriate vocabulary
                    └── Audience configuration (must exist first)

Audience configuration (setup Q&A)
  └── User Persona instantiation
        └── Self-generated test scenarios
              └── Audience perspective review

Universal quality rules (baked in)
  └── Editor review
        └── Consistency enforcement (cross-file)
        └── Internal detail filtering
        └── Inline code cross-referencing
        └── Gap detection (requires source analysis)

Project config (per-project)
  └── Doc system-specific formatting rules
  └── Custom quality rules
  └── Two-audience mode

Doc Author output + Editor output
  └── User Persona review
        └── Final output (minimal-tweak publishable)

GSD integration
  └── Standalone plugin (must exist first)
```

---

## MVP Recommendation

The smallest set that delivers the core value proposition (perspective-shifted, publication-quality library docs):

**Prioritize:**
1. Doc Author with diataxis framework, working code examples, internal detail filtering, and audience-appropriate vocabulary
2. Universal quality rules baked into Editor (structure consistency, cross-referencing, audience scope)
3. User Persona with self-generated test scenarios and audience perspective review
4. Per-project audience configuration via setup Q&A (persisted in project config)
5. Content-first markdown output (no doc-system-specific markup)

**Defer to later phases:**
- Gap detection (source-to-docs coverage analysis): High complexity, requires careful source analysis design
- Two-audience mode (users vs contributors): Additive complexity on top of single-audience; validate single-audience first
- GSD milestone integration: Integration point, not core writing capability; add after standalone works well
- Extensible custom quality rules: Nice to have; universal rules cover most cases at launch
- Doc system-specific formatting rules: Add once content quality is validated

**Reasoning:**
The core value is "docs written from the user's perspective." That requires Author + User Persona + basic quality enforcement. Everything else is optimization or integration. Ship the three-agent pipeline with universal rules and single-audience config; validate that the perspective shift is working before adding complexity.

---

## Sources

- PROJECT.md: Project requirements, constraints, out-of-scope decisions (HIGH confidence — primary source)
- Training data knowledge of: diataxis framework (Daniele Procida, 2021), Write the Docs community standards, common AI documentation failure modes, Claude Code plugin architecture (MEDIUM confidence — well-established, pre-cutoff)
- Training data knowledge of: TypeDoc, pdoc, rustdoc, Sphinx, mkdocs-material, Docusaurus feature sets (MEDIUM confidence — stable tools, unlikely to have changed materially)
- Note: Web search and WebFetch were unavailable during this research session. Competitive landscape (e.g., new AI doc tools released after Aug 2025) is not covered. Recommend a follow-up search for "AI documentation generation tools 2026" before finalizing the roadmap.
