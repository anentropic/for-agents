# Gap Report

**Generated:** 2026-03-25
**Source root:** . (plugin skill files)
**Language:** Markdown (skill definitions)
**Total undocumented symbols:** 6

## Undocumented Symbols

### doc-writer/skills/setup/SKILL.md

- `--refresh-context` argument (command argument) — re-runs the researcher agent without full Q&A flow; not in docs
- `tone` configuration field (config key) — writing tone setting (just-the-facts / warm-businesslike / personality); entirely absent from docs
- `use_cases` configuration field (config key) — library use case capture during setup; entirely absent from docs
- `use_cases_section` configuration field (config key) — promotes use cases to a docs section; entirely absent from docs
- `user_tasks` persona field (config key) — common tasks collected per persona; not shown in config schema or tutorial

### doc-writer/skills/review/SKILL.md

- `--edit` argument (command argument) — enables Editor to apply fixes (default is report-only); docs say "Argument: none" and incorrectly describe default as applying fixes

## Notes

All gaps are in `docs/doc-writer.md`. `docs/copilot-review.md` is accurate.

The `doc-writer:review` entry in the existing docs contains a factual inaccuracy: it states the Editor "applies fixes directly to doc files" by default and includes a note "The Editor applies fixes directly to docs during the review (this is by design)." The current implementation has the opposite default — report-only — with `--edit` required to apply changes.
