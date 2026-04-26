# Copilot Review Prompt Templates

Each prompt template below is sent to GitHub Copilot CLI as a self-contained review task.
Substitute template variables before sending:

- `{{CODEBASE_SUMMARY}}` — Brief codebase summary from the discovery step
- `{{TARGET_PATH}}` — Path being reviewed

---

## 1. Architecture

```
You are performing an architecture review of a codebase.

Codebase context:
{{CODEBASE_SUMMARY}}

Review the code under "{{TARGET_PATH}}" for architectural issues. Focus on:

- Module boundaries: Are responsibilities clearly separated? Are there god modules/classes that do too much?
- Dependency graph: Do modules have clean dependency directions? Are there circular dependencies?
- Separation of concerns: Is business logic mixed with I/O, presentation, or infrastructure?
- Coupling and cohesion: Are modules tightly coupled? Do classes/modules have high internal cohesion?
- Design patterns: Are patterns used appropriately, or are they forced/missing where they'd help?
- Scalability: Are there architectural bottlenecks that would cause problems as the codebase grows?

**NEVER flag:**
- Style, formatting, or naming conventions
- Grammar or spelling in comments or strings
- "Consider doing X" suggestions that aren't genuine problems
- Missing documentation or comments
- Code organization preferences
- Anything you are not confident is a real issue
- Reasonable abstractions that could theoretically be simpler
- File/folder organization style

Ignore the .planning/ directory and any GSD project management files.
Ignore the .reviews/ directory.

Report only genuine architectural issues, not style preferences or minor nitpicks.

If you are unsure whether something is a genuine problem, do not report it.

For each issue found, use this exact format:

## Issue: <concise title>
- **File**: <path:line>
- **Severity**: Critical | High | Medium
- **Description**: <what's wrong and why it matters>
- **Evidence**: <how you confirmed this is a real problem — file:line references, pattern matches>
- **Suggestion**: <concrete fix or refactoring approach>

Do not pad your response. Do not summarize what you examined. Do not give compliments about the code. Just report issues, or state that none were found.
```

---

## 2. Test Coverage & Correctness

```
You are performing a test coverage and correctness review of a codebase.

Codebase context:
{{CODEBASE_SUMMARY}}

Review the code under "{{TARGET_PATH}}" for testing issues. Focus on:

- Missing test coverage: What important code paths have no tests? Look at source files and check for corresponding test files.
- Test quality: Are existing tests actually testing meaningful behavior, or are they shallow/trivial?
- Edge cases: Are boundary conditions, empty inputs, error paths, and concurrent scenarios tested?
- Assertion quality: Are assertions specific enough? Do they test the right things?
- Test isolation: Do tests depend on each other, external state, or execution order?
- Mocking appropriateness: Is mocking overused (testing implementation not behavior) or underused (tests hit real services)?
- Flaky test risks: Are there race conditions, timing dependencies, or non-deterministic elements?

Before reporting an issue, check whether it is already handled elsewhere in the codebase.

**NEVER flag:**
- Style, formatting, or naming conventions
- Grammar or spelling in comments or strings
- "Consider doing X" suggestions that aren't genuine problems
- Missing documentation or comments
- Code organization preferences
- Anything you are not confident is a real issue
- Missing tests for trivial getters, setters, or pure data structures
- Test naming or file organization style

Ignore the .planning/ directory and any GSD project management files.
Ignore the .reviews/ directory.

Report only genuine testing gaps and issues, not style preferences.

If you are unsure whether something is a genuine problem, do not report it.

For each issue found, use this exact format:

## Issue: <concise title>
- **File**: <path:line>
- **Severity**: Critical | High | Medium
- **Description**: <what's wrong and why it matters>
- **Evidence**: <how you confirmed this is a real problem — file:line references, pattern matches>
- **Suggestion**: <concrete fix — what test to add or how to improve the existing test>

Do not pad your response. Do not summarize what you examined. Do not give compliments about the code. Just report issues, or state that none were found.
```

---

## 3. Code Quality

```
You are performing a code quality review of a codebase.

Codebase context:
{{CODEBASE_SUMMARY}}

Review the code under "{{TARGET_PATH}}" for code quality issues. Focus on:

- Dead code: Unreachable code, unused imports, unused variables, commented-out code blocks, unused functions/classes
- Code smells: Long methods, deep nesting, feature envy, data clumps, primitive obsession
- Duplication: Copy-pasted logic that should be extracted (3+ similar occurrences)
- Naming: Misleading names, unclear abbreviations, inconsistent naming conventions
- Idiomatic usage: Code that fights the language/framework instead of using its idioms
- Complexity: Functions/methods with high cyclomatic complexity, hard-to-follow control flow
- Readability: Magic numbers, unclear boolean expressions, overly clever code

**NEVER flag:**
- Style, formatting, or naming conventions
- Grammar or spelling in comments or strings
- "Consider doing X" suggestions that aren't genuine problems
- Missing documentation or comments
- Code organization preferences
- Anything you are not confident is a real issue
- Code that is verbose but unambiguous
- Personal style differences that don't affect correctness or readability

Ignore the .planning/ directory and any GSD project management files.
Ignore the .reviews/ directory.

Report only genuine quality issues that impact maintainability, not personal style preferences.
Do not flag missing comments or documentation — only flag misleading comments.

If you are unsure whether something is a genuine problem, do not report it.

For each issue found, use this exact format:

## Issue: <concise title>
- **File**: <path:line>
- **Severity**: Critical | High | Medium
- **Description**: <what's wrong and why it matters>
- **Evidence**: <how you confirmed this is a real problem — file:line references, pattern matches>
- **Suggestion**: <concrete fix>

Do not pad your response. Do not summarize what you examined. Do not give compliments about the code. Just report issues, or state that none were found.
```

---

## 4. Error Handling & Robustness

```
You are performing an error handling and robustness review of a codebase.

Codebase context:
{{CODEBASE_SUMMARY}}

Review the code under "{{TARGET_PATH}}" for error handling issues. Focus on:

- Error propagation: Are errors silently swallowed? Are catch blocks empty or just logging without re-throwing?
- Missing error cases: What operations can fail but have no error handling? (file I/O, network calls, parsing, type conversions)
- Input validation: Is user input or external data validated at system boundaries?
- Defensive coding: Are null/undefined checks missing where they should exist? Are array bounds checked?
- Logging: Are errors logged with enough context to debug? Are sensitive details leaked in logs?
- Graceful degradation: Does the system handle partial failures? What happens when a dependency is unavailable?
- Resource cleanup: Are file handles, database connections, and other resources properly closed in error paths?

Before reporting an issue, check whether it is already handled elsewhere in the codebase.

**NEVER flag:**
- Style, formatting, or naming conventions
- Grammar or spelling in comments or strings
- "Consider doing X" suggestions that aren't genuine problems
- Missing documentation or comments
- Code organization preferences
- Anything you are not confident is a real issue
- Theoretical edge cases that cannot realistically occur given the codebase's usage context

Ignore the .planning/ directory and any GSD project management files.
Ignore the .reviews/ directory.

Report only genuine robustness issues, not theoretical edge cases that cannot realistically occur.

If you are unsure whether something is a genuine problem, do not report it.

For each issue found, use this exact format:

## Issue: <concise title>
- **File**: <path:line>
- **Severity**: Critical | High | Medium
- **Description**: <what's wrong and why it matters>
- **Evidence**: <how you confirmed this is a real problem — file:line references, pattern matches>
- **Suggestion**: <concrete fix>

Do not pad your response. Do not summarize what you examined. Do not give compliments about the code. Just report issues, or state that none were found.
```

---

## 5. Dependency Audit

```
You are performing a dependency audit of a codebase.

Codebase context:
{{CODEBASE_SUMMARY}}

Review the dependencies declared in "{{TARGET_PATH}}" (check package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml, Gemfile, or equivalent). Focus on:

- Maintenance status: Are any dependencies unmaintained, deprecated, or archived? Check for signs like very old last-publish dates or deprecation notices in package metadata.
- Popularity and trust: Are dependencies well-known and battle-tested, or obscure with few downloads/stars? Obscure deps are higher risk.
- Weight justification: Does each dependency earn its weight? Are there large dependencies pulled in for a single small feature?
- Redundancy: Are there multiple dependencies that serve the same purpose? (e.g., two HTTP clients, two date libraries)
- Missing dependencies: Is there hand-rolled code that would benefit from a well-maintained library?
- Version constraints: Are version ranges too loose (risking breaking changes) or too tight (preventing security patches)?
- Security: Are there dependencies with known security advisories?

**NEVER flag:**
- Style, formatting, or naming conventions
- Grammar or spelling in comments or strings
- "Consider doing X" suggestions that aren't genuine problems
- Missing documentation or comments
- Code organization preferences
- Anything you are not confident is a real issue
- Packages that are slightly outdated but have no known issues or security advisories

Ignore the .planning/ directory and any GSD project management files.
Ignore the .reviews/ directory.

Report only actionable dependency issues.

If you are unsure whether something is a genuine problem, do not report it.

For each issue found, use this exact format:

## Issue: <concise title>
- **File**: <path:line>
- **Severity**: Critical | High | Medium
- **Description**: <what's wrong and why it matters>
- **Evidence**: <how you confirmed this is a real problem — file:line references, pattern matches>
- **Suggestion**: <concrete alternative or action>

Do not pad your response. Do not summarize what you examined. Do not give compliments about the code. Just report issues, or state that none were found.
```

---

## 6. Reinvented Wheels

```
You are performing a "reinvented wheels" audit of a codebase.

Codebase context:
{{CODEBASE_SUMMARY}}

Review the code under "{{TARGET_PATH}}" for hand-rolled implementations that duplicate well-known libraries. This is especially common in AI-generated codebases where LLMs tend to implement things from scratch instead of using established packages. Look for:

- Custom retry/backoff logic — should use: tenacity (Python), p-retry (JS), backoff (Python)
- Custom HTTP clients/wrappers — should use: httpx (Python), got/axios (JS), reqwest (Rust)
- Custom argument parsing — should use: click/typer (Python), yargs/commander (JS), clap (Rust)
- Custom logging frameworks — should use: structlog/loguru (Python), pino/winston (JS), tracing (Rust)
- Custom config file parsing — should use: pydantic-settings (Python), dotenv/convict (JS)
- Custom date/time manipulation — should use: pendulum/arrow (Python), date-fns/dayjs (JS)
- Custom schema validation — should use: pydantic/marshmallow (Python), zod/joi (JS)
- Custom task queues or schedulers — should use: celery/rq (Python), bull (JS)
- Custom path manipulation utilities — should use stdlib path modules
- Custom string utilities (slugify, truncate, etc.) — should use established micro-libraries
- Custom test utilities that replicate pytest fixtures, Jest helpers, etc.
- Custom ORM or database abstraction layers
- Any utility file over 200 lines that duplicates library functionality

The key question for each finding: "Is there a well-maintained, popular library that does this better?"

**NEVER flag:**
- Style, formatting, or naming conventions
- Grammar or spelling in comments or strings
- "Consider doing X" suggestions that aren't genuine problems
- Missing documentation or comments
- Code organization preferences
- Anything you are not confident is a real issue
- Simple utility functions under ~20 lines where a dependency would add more overhead than value

Ignore the .planning/ directory and any GSD project management files.
Ignore the .reviews/ directory.

If you are unsure whether something is a genuine problem, do not report it.

For each issue found, use this exact format:

## Issue: <concise title>
- **File**: <path:line>
- **Severity**: Critical | High | Medium
- **Description**: <what was hand-rolled and what it reimplements>
- **Evidence**: <how you confirmed this is a real problem — file:line references, pattern matches>
- **Suggestion**: <specific library to use instead, with migration guidance>

Do not pad your response. Do not summarize what you examined. Do not give compliments about the code. Just report issues, or state that none were found.
```
