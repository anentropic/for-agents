---
name: quality-rules
description: Universal documentation quality rules applied by all doc-writer agents. Non-overridable baseline standards.
user-invocable: false
---

# Universal Quality Rules

These rules apply to ALL documentation produced by doc-writer agents. They cannot be overridden by project configuration. Project-specific rules (in `.doc-writer/rules.md`) are additive — they extend these universal rules but can never weaken or bypass them.

## Rule 1: No Internal Details

Documentation must never reference test utilities, CI/CD configuration, development scripts, justfile recipes, internal module names that are not part of the public API, or any other maintainer-only concerns. The reader is an end user of the library, not a contributor to it. If something would only matter to someone working on the library's internals, it does not belong in user-facing documentation.

**What violation looks like:** A how-to guide mentions "run `just test-integration` to verify" or references an internal `_utils.py` module that users cannot import. A tutorial includes steps for setting up the CI pipeline or configuring pre-commit hooks. Any mention of files, scripts, or processes that exist solely for the library's own development workflow.

## Rule 2: Working Code Examples Required

Every documented API feature or function must include at least one realistic, working code example. Examples must demonstrate a real use case — not placeholder values like `doThing("example", 42)` — and include enough surrounding context for the reader to understand what the code does and why they would use it. All fenced code blocks must specify the programming language.

**What violation looks like:** A reference page lists function signatures with parameter descriptions but no usage examples. An example uses meaningless variable names (`foo`, `bar`, `x`) or placeholder strings that do not represent a real scenario. A code block is missing its language identifier, making syntax highlighting impossible and copy-paste error-prone.

## Rule 3: Consistent Structure

All pages of the same documentation type (tutorial, how-to, reference, explanation) must follow the same structural template. A reader opening two how-to guides should see the same section layout, the same ordering of prerequisites and steps, and the same patterns for troubleshooting. Structural consistency reduces cognitive load and builds reader trust in the documentation.

**What violation looks like:** One tutorial has "Prerequisites" before "Introduction" while another reverses the order. A how-to guide includes a "Background" section that no other how-to guide has. Reference pages use different table column layouts for parameters across different API entries.

## Rule 4: Cross-Reference Code Mentions

All inline `code` mentions in prose must be linked to the relevant API Reference entry where one exists. When a reader encounters a function name, class name, or configuration key in running text, they should be able to click through to its full documentation. This reduces friction and ensures readers can quickly find detailed information about any symbol mentioned in passing.

**What violation looks like:** A tutorial mentions `client.connect()` in a paragraph but the text is plain inline code with no link to the `connect()` reference page. An explanation discusses the `RetryPolicy` class without linking to its reference entry. Code mentions are formatted as inline code but serve as dead ends rather than navigation points.

## Rule 5: Audience-Calibrated Language

Vocabulary, assumed knowledge, and explanation depth must match the configured audience. Never assume knowledge listed in the audience's `never_assume` list. If the audience is "beginner Python developers," do not skip over virtual environment setup or assume familiarity with async patterns. If the audience is "advanced systems programmers," do not over-explain basic memory management concepts. The calibration comes from the project's `.doc-writer/config.yaml` audience definition.

**What violation looks like:** Documentation for beginners uses jargon without definition — "memoize the callback" assumes the reader knows what memoization means. Documentation for advanced users spends three paragraphs explaining what a function is. A never-assume item like "database ORMs" is referenced without explanation in a getting-started guide.
