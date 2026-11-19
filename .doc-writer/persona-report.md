# Persona Report

**Generated:** 2026-11-19
**Audience:** Library maintainer using Claude Code (advanced)
**Scenarios tested:** 5
**Results:** 3 PASS, 2 PARTIAL, 0 FAIL

## Summary

For a maintainer who already knows Claude Code and git, the docs work well: every command has a
how-to and a reference entry, side effects on files are stated plainly, and the "nothing is
committed" guarantee comes up wherever it matters. The two weak spots are first-time setup on a
project that already has a docs site, which only the beginner tutorial covers, and the advice
for a non-converging FAIL that needs a new page, which sends the reader to commands that the
other pages say cannot create one.

---

## Scenario S1: Install for the team and run first-time setup on a library with an existing MkDocs site

**Verdict:** PARTIAL

### Navigation Path

1. Started at: `README.md`
   - Found: install commands for a session and the terminal, "Restart Claude Code", and a link
     to the docs site.
   - Followed: Documentation link to the site front page.
2. Navigated to: `docs/src/index.md` > Installation
   - Found: both install forms in tabs; `--scope project` records the plugin in
     `.claude/settings.json`. This answers the "whole team" part.
   - Followed: "doc-writer documentation".
3. Navigated to: `docs/src/doc-writer/index.md`
   - Found: requirements, supported doc systems, "Run `/doc-writer:setup` first in any project".
     The how-to list has no entry for a first setup; "Configure or reconfigure a project" is the
     closest match.
4. Navigated to: `how-to/configure.md`
   - Found: "Before you start" says that for everything except a first setup, `config.yaml`
     already exists. The page covers the update menu, `--reset` and `--refresh-context`, but not
     the first run. Dead end for the first-run part of the goal.
   - Followed: Related > Commands reference.
5. Navigated to: `reference/commands.md` > `/doc-writer:setup`
   - Found: question flow order, the Writes table (mkdocs.yml "only if missing; additions to an
     existing one only after you confirm each"), starter `index.md` only if the docs root did not
     exist. This answers the "won't clobber mkdocs.yml" concern.
6. Navigated to: `tutorial.md` > Step 2
   - Found: what each question looks like, the existing-mkdocs.yml behavior, and Paths ("Accept
     the defaults if they match your project, for example `docs/` and `src/`"). It does not say how
     to enter `docs/src/` when the proposed default is wrong. Friction: the tutorial's
     beginner-level, no-docs framing (Skip use cases, choose the tutorial answers) is for a
     different situation from mine.
7. Navigated to: `how-to/update-docs.md` > Troubleshooting (found later, during S2)
   - Found: the explicit `docs/src/` rather than `docs/` warning, but only as a symptom
     ("runs in create mode on a documented project"), after the fact.

### Gap Analysis

**Where:** `how-to/configure.md` (no first-setup section); `tutorial.md` > Step 2 > Paths
**What:** No how-to covers first-time setup on a project that already has docs. The facts are
spread across the reference (what setup writes), the beginner tutorial (what the questions look
like) and an update-mode troubleshooting entry (`docs/src/` and `docs/`). The page type does not
match the need: the user is in work mode but has to piece it together from a tutorial and a
reference.
**Impact:** A determined user gets there, but may accept a `docs/` default and only find out when
`write` runs in create mode over an existing site.
**Suggested Fix:** In `how-to/configure.md`, add a section "Set up a project that already has
docs": run `/doc-writer:setup`, expect the existing `mkdocs.yml` to be offered feature
additions one at a time, and at **Paths** set the docs root to `mkdocs.yml`'s `docs_dir` (choose
**Type something else** if the default is wrong). Link it from the how-to list in
`doc-writer/index.md`. In `tutorial.md` > Paths, add one sentence on what to do when the default
does not match.

---

## Scenario S2: Update docs after a release, changing only new and stale pages

**Verdict:** PASS

### Navigation Path

1. Started at: `README.md` > Documentation link > `docs/src/index.md` > doc-writer documentation.
2. Navigated to: `doc-writer/index.md` > How-to guides > "Update docs after code changes".
3. Navigated to: `how-to/update-docs.md`
   - Found: preconditions (two or more pages, committed code, git dates), the update-mode banner
     to expect, gap report sections, the stale-check false-positive caveat, ↻ refresh entries
     and "✓ current" deselection, the all-pages terminology pass, `--skip-gap-scan`, and how to
     review with `git status`/`git diff`.
   - Found: Troubleshooting "A page you did not approve was changed" explains the one source of
     unexpected diffs and where it is logged.
4. Followed: Related > How the pipeline works > Create mode and update mode table, which confirms
   "Update mode never rewrites a page you did not approve".
   - Success: the goal is fully achievable, with realistic output excerpts.

---

## Scenario S3: Audit before a release, then fix only BLOCKING findings and FAILs

**Verdict:** PASS

### Navigation Path

1. Started at: `README.md` > docs site > `doc-writer/index.md` > "Audit docs without changing
   them".
2. Navigated to: `how-to/audit.md`
   - Found: the three stages, "does not loop", a realistic summary excerpt, where to start
     (BLOCKING and FAIL), a table of which report holds what, the `--edit` confirmation options
     and a warning to commit first.
   - Minor friction: the table names `persona-report.md`, while `reference/commands.md` and
     `reference/files.md` say `review` also writes `persona-report-{persona-name}.md` with one
     persona. How a name such as "Library maintainer using Claude Code" becomes a file name is
     not stated.
   - Followed: Related > Make targeted fixes.
3. Navigated to: `how-to/targeted-fixes.md`
   - Found: the issue list ordered BLOCKING, FAIL, SUGGESTION, PARTIAL, NITPICK, selection, the
     scope of the Author and Editor, "Pages outside the selection changed", and re-running
     `review` to confirm.
   - Minor friction: "Any argument other than a number selection becomes the instruction"
     suggests issues can be picked by number, but the sample list shows severity labels and no
     numbers.
   - Success: the goal is achievable without real obstacles. The two points above are worth a
     small clarification but do not block the task.

---

## Scenario S4: Add house rules and force a term's spelling

**Verdict:** PASS

### Navigation Path

1. Started at: `README.md` > docs site > `doc-writer/index.md` > "Add project rules and
   terminology".
2. Navigated to: `how-to/project-rules.md`
   - Found: where to put rules (Project Rules heading, plain instructions, realistic examples
     including British spelling and a Requirements section), the note that rules cannot override
     the baseline, an annotated `terminology.yaml`, `overrides` to force a spelling, precedence
     order in Troubleshooting, when each agent reads the files, and `/doc-writer:review` as the
     check.
   - Found: `--reset` replaces `rules.md`; upgrade merges it.
3. Followed: Related > The .doc-writer folder.
4. Navigated to: `reference/files.md` > Settings you own
   - Found: confirmation of which files survive which commands, and a recommendation to commit
     the settings files.
   - Success: complete, with no friction.

---

## Scenario S5: Handle a non-converging FAIL in update mode that needs a new page

**Verdict:** PARTIAL

### Navigation Path

1. Started at: `README.md` > docs site > `doc-writer/index.md` > "Resolve PARTIAL and FAIL
   verdicts".
2. Navigated to: `how-to/resolve-verdicts.md` > Handle FAILs that did not converge
   - Found: the escalation report format, that in update mode a FAIL on an untouched page is
     escalated with no attempts, and a triage list. For **Missing content**: "Add it with a
     targeted edit, or re-run `/doc-writer:write` and approve a new page for it."
   - Followed: Related > Make targeted fixes.
3. Navigated to: `how-to/targeted-fixes.md` > Stages of an edit run
   - Found: the Author "does not create pages". So a targeted edit can only add a section to an
     existing page, not the new page the goal needs.
4. Navigated to: `how-to/update-docs.md` > Approve new and refreshed pages
   - Found: in update mode, new pages are proposed "for undocumented symbols. Existing features
     are not proposed again." A workflow page that is not tied to a new symbol will not be
     offered, so "re-run write and approve a new page" may show nothing to approve.
5. Navigated to: `tutorial.md` > Step 4
   - Found: at the inventory, "To add or reshape a page, choose **Type something else** and
     describe the change." That is the probable route, but it appears only in the tutorial, in
     create mode.
6. Back to `resolve-verdicts.md` > Check the result and Troubleshooting
   - Found: re-test with `/doc-writer:review`, scenarios are reused while pages stay similar;
     delete `scenarios.yaml` to regenerate. Adding one page to 17 is within the ~30% threshold,
     and `personas.md` says "If pages are added or removed... the Persona writes new scenarios",
     which contradicts this for a single added page.

### Gap Analysis

**Where:** `how-to/resolve-verdicts.md` > Handle FAILs that did not converge > step 2, "Missing
content"
**What:** The two suggested routes conflict with other pages. `edit` cannot create pages, and
update-mode `write` proposes new pages only for undocumented symbols. The route that works,
**Type something else** at the inventory approval, is documented only in the tutorial.
Separately, `explanation/personas.md` says that adding or removing any page regenerates
scenarios, while the ~30% rule elsewhere implies a single new page does not.
**Impact:** A user may run `edit` and get only a section, or re-run `write` and find no new page
proposed. They could work it out, but only by cross-reading three pages.
**Suggested Fix:** In `how-to/resolve-verdicts.md`, section "Handle FAILs that did not converge",
step 2: say that `/doc-writer:edit` can add a section to an existing page but not create one,
and that for a new page you re-run `/doc-writer:write` and, at the inventory approval, choose
**Type something else** to request it, since update mode proposes new pages only for
undocumented symbols. Mention the same option in `how-to/update-docs.md` > Approve new and
refreshed pages. In `explanation/personas.md` > From persona to scenarios, state the reuse rule
once, precisely, so that it matches `resolve-verdicts.md` and `reference/files.md`.

---

## Revision Recommendations

### FAIL Issues (trigger revision)

None.

### PARTIAL Issues (for project author approval)

| Scenario | Page | Gap | Suggested Fix |
|----------|------|-----|---------------|
| S1 | `how-to/configure.md`; `tutorial.md` > Paths | No how-to for first setup on a project with existing docs; docs_root mismatch is only found after the fact | In `how-to/configure.md`, add "Set up a project that already has docs" (mkdocs.yml additions are confirmed one by one; set Paths to `docs_dir`, using **Type something else** if needed) and link it from `doc-writer/index.md`. In `tutorial.md` > Paths, add what to do when the default does not match |
| S5 | `how-to/resolve-verdicts.md` > Handle FAILs that did not converge | "Missing content" routes conflict: `edit` cannot create pages, and update-mode `write` proposes new pages only for undocumented symbols | In `how-to/resolve-verdicts.md`, step 2: say to re-run `write` and request the page with **Type something else** at the inventory; repeat that in `how-to/update-docs.md` > Approve new and refreshed pages. Align the scenario-reuse rule in `explanation/personas.md` with the ~30% rule |

Minor notes (no verdict impact): `how-to/audit.md` > Read the summary does not mention the
`persona-report-{persona-name}.md` file that the reference pages say `review` writes with one
persona, or how a persona name becomes a file name. `how-to/targeted-fixes.md` mentions "number
selection", but its sample list shows no numbers.
