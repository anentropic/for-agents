# Phase 13: Scaffold Variable Substitution Fix and Doc-Researcher Improvements - Research

**Researched:** 2026-03-19
**Domain:** Template variable substitution in scaffold files + agent frontmatter/logic fixes
**Confidence:** HIGH

## Summary

Phase 13 closes the only remaining blocker (P11-03) in the v1.0 milestone audit plus two tech debt items (MISSING-01, MISSING-02). All three issues are well-understood, localized to specific files and line ranges, and require no new libraries, patterns, or architectural decisions.

The P11-03 blocker is a template variable mismatch: `sphinx-shibuya.py` uses four variables (`{project_name}`, `{author_name}`, `{copyright_year}`, `{github_url}`) but SKILL.md Step 2b.3 only substitutes `{site_name}` and `{site_description}`. The fix extends Step 2b.3 to handle ALL scaffold template variables across ALL frameworks, not just the two mkdocs-material ones. This is a generic fix rather than a sphinx-shibuya-specific patch because the odoc scaffold also uses framework-specific variables (`{package_name}`, `{library_name}`, `{synopsis}`) that are only handled by the vague "Process template variable substitution" instruction.

The two tech debt items are single-line and single-block changes: adding WebFetch to the doc-researcher tools frontmatter (MISSING-01) and expanding the Framework Preferences conditional to include sphinx-shibuya and odoc (MISSING-02).

**Primary recommendation:** Fix the variable substitution generically in SKILL.md Step 2b.3 with a clear variable-to-inference mapping table, then make the two doc-researcher changes as separate atomic tasks.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| P11-03 | conf.py scaffold template exists in defaults/scaffolds/ with Shibuya theme, nav_links, autoapi, napoleon, intersphinx, sphinx-design | Scaffold file exists and is correct. The defect is in SKILL.md Step 2b.3 which fails to substitute the 4 template variables the scaffold uses. Fix requires extending Step 2b.3 substitution logic. |
</phase_requirements>

## Standard Stack

No new libraries or tools are needed. This phase modifies existing prompt/markdown files only.

### Core Files to Modify

| File | Location | Change Type |
|------|----------|-------------|
| `SKILL.md` | `doc-writer/skills/setup/SKILL.md` | Extend Step 2b.3 substitution logic |
| `doc-researcher.md` | `doc-writer/agents/doc-researcher.md` | Add tool + expand conditional |

### Files for Reference Only (no changes)

| File | Location | Purpose |
|------|----------|---------|
| `sphinx-shibuya.py` | `doc-writer/skills/setup/defaults/scaffolds/sphinx-shibuya.py` | Has the 4 template variables that need substitution |
| `mkdocs-material.yml` | `doc-writer/skills/setup/defaults/scaffolds/mkdocs-material.yml` | Only uses `{site_name}` and `{site_description}` (already handled) |
| `odoc/` directory | `doc-writer/skills/setup/defaults/scaffolds/odoc/` | Uses `{package_name}`, `{library_name}`, `{synopsis}` (handled by vague instruction) |

## Architecture Patterns

### Current Scaffold Variable Substitution (BROKEN for sphinx-shibuya)

SKILL.md Step 2b.3 currently has this substitution logic (lines 296-298):

```
b. Infer `site_name` from the project's package manifest...
c. Infer `site_description` from the package manifest `description` field...
d. Replace `{site_name}` and `{site_description}` template variables in the scaffold content.
```

This only covers mkdocs-material. The sphinx-shibuya scaffold uses 4 different variables:
- `{project_name}` (lines 8, 10 of sphinx-shibuya.py)
- `{author_name}` (lines 9, 10 of sphinx-shibuya.py)
- `{copyright_year}` (line 10 of sphinx-shibuya.py)
- `{github_url}` (line 50 of sphinx-shibuya.py)

The odoc scaffolds use 3 further variables:
- `{package_name}` (in doc_dune.sexp, index.mld, secondary_dune.sexp, secondary_index.mld)
- `{library_name}` (in index.mld, secondary_index.mld)
- `{synopsis}` (in index.mld, secondary_index.mld)

### Recommended Fix Pattern: Generic Variable-to-Inference Mapping

Instead of hardcoding `{site_name}` and `{site_description}`, Step 2b.3 should define a comprehensive mapping of template variables to inference strategies. This makes the system robust for any future scaffold additions.

**Variable Inference Table (to be embedded in SKILL.md):**

| Variable | Inference Strategy | Fallback |
|----------|--------------------|----------|
| `{site_name}` | Package manifest `name` field, README first heading | Ask user |
| `{site_description}` | Package manifest `description` field | Ask user |
| `{project_name}` | Same as `{site_name}` | Ask user |
| `{author_name}` | `git config user.name`, package manifest author field | Ask user |
| `{copyright_year}` | Current year (auto-detect, never ask) | Current year |
| `{github_url}` | `git remote get-url origin` (convert SSH to HTTPS), package manifest repository URL | Ask user |
| `{package_name}` | Inferred from Q1 answer or dune-project `(name ...)` | Ask user |
| `{library_name}` | Inferred from Q1 answer or dune-project `(public_name ...)` | Same as `{package_name}` |
| `{synopsis}` | Package manifest description or opam synopsis | Ask user |

**Key insight:** `{project_name}` and `{site_name}` have the same inference source. The variable names differ only because Sphinx conf.py uses `project = "..."` while mkdocs.yml uses `site_name: "..."`. The fix should map both to the same inference logic.

### Current Framework Preferences Pattern (doc-researcher.md)

Lines 117-124 of doc-researcher.md:

```markdown
### Framework Preferences

If `doc_system` is `mkdocs-material` or `plain-markdown`:

1. Read the framework config file...
2. Note which features are enabled...
3. Generate usage guidance...
4. Note features NOT detected...
```

This conditional excludes sphinx-shibuya and odoc. The fix expands the conditional to cover all doc systems with framework config files.

### Current Tools Frontmatter (doc-researcher.md)

Line 4: `tools: Read, Write, Glob, Grep, Bash`

Missing: `WebFetch`. The Unknown Framework Research mode (line 212) instructs "Use WebFetch to find the framework's official documentation" but the agent cannot call WebFetch because it is not listed in tools.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Git remote URL detection | Custom regex parsing of .git/config | `git remote get-url origin` command | Handles SSH, HTTPS, multiple remote formats |
| SSH-to-HTTPS URL conversion | Complex regex | Simple sed: `s#git@github.com:#https://github.com/#` | Covers the dominant case; edge cases are user-correctable |
| Current year detection | Date parsing | `date +%Y` or equivalent | Always correct, no timezone issues for year |
| Author name inference | Package-manifest-only parsing | `git config user.name` as primary, manifest as fallback | Git config is almost always set; manifest author fields vary by ecosystem |

## Common Pitfalls

### Pitfall 1: Patching only sphinx-shibuya instead of fixing generically

**What goes wrong:** Adding `{project_name}` etc. substitution as a sphinx-shibuya-specific block, leaving odoc variables still only vaguely handled and making every future scaffold need its own special case.
**Why it happens:** The temptation to make the smallest possible change to close P11-03.
**How to avoid:** Rewrite Step 2b.3d as a generic substitution table that any scaffold can use. Test against all three scaffold types (mkdocs-material, sphinx-shibuya, odoc).
**Warning signs:** If the fix mentions "sphinx-shibuya" by name in the substitution logic, it is too specific.

### Pitfall 2: Asking the user for values that can be auto-detected

**What goes wrong:** The fix prompts the user for `{copyright_year}` (always current year) or `{project_name}` (same inference as `{site_name}` which is already inferred).
**Why it happens:** Treating all variables as potentially unknown.
**How to avoid:** `{copyright_year}` should NEVER prompt -- it is always the current year. `{project_name}` should share the same inference chain as `{site_name}`.
**Warning signs:** Setup flow adds multiple new user-facing questions for values that are deterministic.

### Pitfall 3: Breaking the existing mkdocs-material flow

**What goes wrong:** The generic substitution table changes the behavior for mkdocs-material scaffolds (which currently work correctly).
**Why it happens:** Over-generalizing without verifying backward compatibility.
**How to avoid:** mkdocs-material.yml only uses `{site_name}` and `{site_description}`. The new table adds variables but must not change the inference for existing ones. The fix must be additive.
**Warning signs:** mkdocs-material scaffold tests fail after the change.

### Pitfall 4: Expanding Framework Preferences conditional too broadly

**What goes wrong:** The doc-researcher tries to read framework config files for plain-markdown (which has none) or for unknown frameworks (where the config format is unpredictable).
**Why it happens:** Removing the conditional entirely instead of expanding it carefully.
**How to avoid:** The conditional should become: "If `doc_system` has a framework config file (detected during scan):" which naturally handles plain-markdown (no config file = skip) and unknown frameworks (researcher would have already noted the config file during its own research).
**Warning signs:** doc-researcher errors when enriching a plain-markdown project.

## Code Examples

### Fix 1: SKILL.md Step 2b.3 -- Generic Variable Substitution

The current Step 2b.3 items b-d should be replaced with a comprehensive substitution block. The key change is replacing the hardcoded two-variable approach with a general approach.

**Current (lines 296-298):**
```markdown
     b. Infer `site_name` from the project's package manifest...
     c. Infer `site_description` from the package manifest `description` field...
     d. Replace `{site_name}` and `{site_description}` template variables in the scaffold content.
```

**Proposed replacement (items b-d become a single expanded block):**
```markdown
     b. Identify all template variables in the scaffold content (patterns matching `{variable_name}`).
        Infer values for each using this table:

        | Variable | Primary Source | Fallback Source | Last Resort |
        |----------|---------------|-----------------|-------------|
        | `{site_name}` | Package manifest `name` | README first heading | Ask user: "Project name for the documentation site:" |
        | `{site_description}` | Package manifest `description` | README subtitle or first paragraph | Ask user: "One-sentence description:" |
        | `{project_name}` | Same as `{site_name}` | Same as `{site_name}` | Same as `{site_name}` |
        | `{author_name}` | git config user.name | Package manifest author | Ask user: "Author name:" |
        | `{copyright_year}` | Current year (automatic) | — | — |
        | `{github_url}` | git remote get-url origin (SSH converted to HTTPS) | Package manifest repository URL | Ask user: "GitHub URL:" |
        | `{package_name}` | dune-project `(name ...)` or inferred from project structure | Same as `{site_name}` | Ask user |
        | `{library_name}` | dune-project `(public_name ...)` or library name from Q1 | Same as `{package_name}` | Ask user |
        | `{synopsis}` | Same as `{site_description}` | opam file synopsis | Ask user |

        Variables not in this table: ask the user in plain text for a value.
        Variables with an automatic source (e.g., `{copyright_year}`): never ask -- always use the computed value.

     c. Replace all identified template variables in the scaffold content with their inferred values.
```

### Fix 2: doc-researcher.md -- Add WebFetch to Tools

**Current (line 4):**
```
tools: Read, Write, Glob, Grep, Bash
```

**Fixed:**
```
tools: Read, Write, Glob, Grep, Bash, WebFetch
```

### Fix 3: doc-researcher.md -- Expand Framework Preferences Conditional

**Current (lines 117-118):**
```markdown
### Framework Preferences

If `doc_system` is `mkdocs-material` or `plain-markdown`:
```

**Fixed:**
```markdown
### Framework Preferences

If the project has a framework config file (e.g., `mkdocs.yml`, `conf.py`, `doc/dune`):
```

This naturally covers all doc systems with config files (mkdocs-material, sphinx-shibuya, odoc) and skips those without (plain-markdown). It also handles future unknown frameworks that the researcher discovers -- if the researcher identified a config file during Step 2, it will be available during enrichment.

Additionally, the four sub-steps under Framework Preferences should be generalized. The current text says "from `mkdocs.yml` extensions/plugins or equivalent" which is mkdocs-specific. The updated text should say "from the framework config file" generically.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded `{site_name}` + `{site_description}` only | Generic variable inference table | Phase 13 (this fix) | All scaffolds work correctly including sphinx-shibuya and odoc |
| doc-researcher gates on mkdocs-material/plain-markdown | doc-researcher gates on "has framework config file" | Phase 13 (this fix) | sphinx-shibuya and odoc get framework preferences in context.md |
| doc-researcher has no WebFetch | doc-researcher has WebFetch | Phase 13 (this fix) | Unknown framework research can reach HIGH confidence |

## Open Questions

1. **Should odoc variable inference be explicit in the table?**
   - What we know: odoc uses `{package_name}`, `{library_name}`, `{synopsis}` which are OCaml-ecosystem-specific. The directory scaffold processing instruction at line 295 says "Process template variable substitution on each file" without specifying how.
   - What's unclear: Whether the current vague instruction actually works at runtime (the LLM executing the skill may or may not figure out what to substitute).
   - Recommendation: Include odoc variables in the generic table. This makes substitution deterministic rather than relying on LLM inference. Risk: zero (additive change).

2. **Should the sphinx-shibuya.py scaffold be changed to use `{site_name}` instead of `{project_name}`?**
   - What we know: The audit recommends either (a) extend SKILL.md or (b) rename variables in the scaffold.
   - What's unclear: Whether using framework-native variable names (`project` for Sphinx conf.py) is more readable than generic names (`site_name`).
   - Recommendation: Keep `{project_name}` in sphinx-shibuya.py (matches Sphinx convention: `project = "..."`). Fix the mapping in SKILL.md so `{project_name}` maps to the same source as `{site_name}`. This preserves scaffold readability.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | bats (bash automated testing) |
| Config file | none (bats is standalone) |
| Quick run command | `bats tests/phase-13-validation.bats` |
| Full suite command | `bats tests/phase-13-validation.bats` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P11-03 | SKILL.md Step 2b.3 substitutes all sphinx-shibuya variables | unit (static grep) | `bats tests/phase-13-validation.bats` | No -- Wave 0 |
| MISSING-01 | doc-researcher tools frontmatter includes WebFetch | unit (static grep) | `bats tests/phase-13-validation.bats` | No -- Wave 0 |
| MISSING-02 | doc-researcher Framework Preferences not gated on mkdocs-material/plain-markdown | unit (static grep) | `bats tests/phase-13-validation.bats` | No -- Wave 0 |

### Test Strategy

**What CAN be automated (static verification):**
- SKILL.md contains references to `{project_name}`, `{author_name}`, `{copyright_year}`, `{github_url}` in the substitution logic (Step 2b.3)
- SKILL.md substitution block mentions inference strategies (e.g., "git config user.name", "current year", "git remote")
- doc-researcher.md tools frontmatter includes WebFetch
- doc-researcher.md Framework Preferences block does NOT gate on "mkdocs-material or plain-markdown" (negative grep)
- doc-researcher.md Framework Preferences block references "framework config file" generically

**What CANNOT be automated (runtime only):**
- Actual substitution happens correctly when a user runs `/doc-writer:setup` selecting sphinx-shibuya in a real project
- Git remote URL is correctly parsed and converted from SSH to HTTPS
- doc-researcher actually uses WebFetch during unknown framework research
- Framework Preferences section in context.md is populated for sphinx-shibuya projects

### Proposed Test Cases

```bash
# P11-03: SKILL.md handles all sphinx-shibuya template variables
@test "P11-03: SKILL.md Step 2b.3 references {project_name} variable" {
  grep -q '{project_name}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 references {author_name} variable" {
  grep -q '{author_name}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 references {copyright_year} variable" {
  grep -q '{copyright_year}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 references {github_url} variable" {
  grep -q '{github_url}' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 has git config inference for author" {
  grep -q 'git config user.name' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 has current year inference for copyright" {
  grep -qi 'current year' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

@test "P11-03: SKILL.md Step 2b.3 has git remote inference for github_url" {
  grep -q 'git remote' "$PROJECT_ROOT/doc-writer/skills/setup/SKILL.md"
}

# MISSING-01: doc-researcher WebFetch in tools
@test "MISSING-01: doc-researcher tools frontmatter includes WebFetch" {
  grep -q 'WebFetch' "$PROJECT_ROOT/doc-writer/agents/doc-researcher.md"
}

# MISSING-02: doc-researcher Framework Preferences expanded
@test "MISSING-02: Framework Preferences not gated on mkdocs-material/plain-markdown" {
  ! grep -q "mkdocs-material.*or.*plain-markdown" "$PROJECT_ROOT/doc-writer/agents/doc-researcher.md"
}

@test "MISSING-02: Framework Preferences references framework config file generically" {
  grep -q 'framework config file' "$PROJECT_ROOT/doc-writer/agents/doc-researcher.md"
}
```

### Sampling Rate

- **Per task commit:** `bats tests/phase-13-validation.bats`
- **Per wave merge:** `bats tests/phase-13-validation.bats` (same -- small test file)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/phase-13-validation.bats` -- covers P11-03 + MISSING-01 + MISSING-02 (11 tests)
- No framework install needed (bats already available from prior phases)
- No shared fixtures needed

## Sources

### Primary (HIGH confidence)
- Direct file inspection of `doc-writer/skills/setup/SKILL.md` lines 279-317 (Step 2b.3)
- Direct file inspection of `doc-writer/skills/setup/defaults/scaffolds/sphinx-shibuya.py` (template variables on lines 8-10, 50)
- Direct file inspection of `doc-writer/agents/doc-researcher.md` lines 1-6 (tools frontmatter) and lines 116-124 (Framework Preferences)
- Direct file inspection of `doc-writer/skills/setup/defaults/scaffolds/odoc/` (4 template files with variables)
- v1.0-MILESTONE-AUDIT.md audit findings (P11-03, MISSING-01, MISSING-02, MISSING-03)

### Secondary (MEDIUM confidence)
- None needed -- all findings are from direct file inspection

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries, direct file inspection
- Architecture: HIGH -- fix pattern is clear, all affected files identified, change is additive
- Pitfalls: HIGH -- pitfalls derived from direct analysis of current code and prior phase patterns

**Research date:** 2026-03-19
**Valid until:** Indefinite -- this is a fix for a known defect in a stable codebase
