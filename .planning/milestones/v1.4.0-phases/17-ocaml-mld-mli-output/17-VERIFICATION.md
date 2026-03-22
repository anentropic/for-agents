---
phase: 17-ocaml-mld-mli-output
verified: 2026-03-22T00:00:00Z
status: passed
score: 13/13 must-haves verified
re_verification: false
---

# Phase 17: OCaml .mld/.mli Output Verification Report

**Phase Goal:** Doc-author produces odoc-native .mld files (not Markdown) for odoc projects, and the full pipeline handles .mld discovery and syntax
**Verified:** 2026-03-22
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                         | Status     | Evidence                                                                              |
|----|-----------------------------------------------------------------------------------------------|------------|---------------------------------------------------------------------------------------|
| 1  | When doc_system is odoc, doc-author writes .mld files to doc/ with odoc syntax               | VERIFIED   | `doc-author.md` line 295-302: "Odoc Output Mode" section with explicit file output rules |
| 2  | Doc-author registers each .mld page in doc/dune mld_files list after writing it              | VERIFIED   | `doc-author.md` lines 308-328: "Dune registration (mandatory after each .mld write)" with before/after example |
| 3  | Doc-author writes internal notes to .doc-writer/author-notes.md instead of HTML comments     | VERIFIED   | `doc-author.md` lines 330-366: "Internal notes (replaces Step 7 for odoc)" section |
| 4  | Editor discovers .mld files in doc/ when doc_system is odoc                                  | VERIFIED   | `doc-editor.md` lines 55-58: conditional `doc/**/*.mld` glob in Step 2               |
| 5  | Editor uses odoc heading syntax {1 ...} and cross-reference syntax {!...} in Pass 2 and Pass 4 | VERIFIED | `doc-editor.md` lines 396-413: "Odoc Syntax Adjustments for Pass 2 and Pass 4" section with `{1 Section}` and `{!Module.value}` |
| 6  | Editor reads .doc-writer/author-notes.md instead of HTML comments for odoc                   | VERIFIED   | `doc-editor.md` lines 65-68: Step 3 conditional reads `author-notes.md`              |
| 7  | Editor skips HTML comment stripping in post-processing for odoc                               | VERIFIED   | `doc-editor.md` lines 422-423: "Skip this step entirely" for odoc doc_system         |
| 8  | User tester discovers .mld files in doc/ when doc_system is odoc                             | VERIFIED   | `doc-user-tester.md` lines 62-65: conditional `doc/**/*.mld` glob in Step 3          |
| 9  | Write SKILL.md scans doc/**/*.mld instead of docs_root/**/*.md when doc_system is odoc       | VERIFIED   | `write/SKILL.md` lines 51-57: Step 0 conditional glob with scaffold filtering        |
| 10 | Doc-author proposes doc comment enrichments for undocumented public values in .mli files     | VERIFIED   | `doc-author.md` lines 368-443: ".mli Doc Comment Enrichment Proposals" section       |
| 11 | Enrichment proposals written to .doc-writer/mli-enrichment.md, never to .mli files          | VERIFIED   | `doc-author.md` line 441: "Do NOT use the Write tool on .mli files"                  |
| 12 | Enrichment workflow only runs when odoc Q&A scope includes .mli improvements                 | VERIFIED   | `doc-author.md` line 370-372: scope control gate before running enrichment            |
| 13 | Write SKILL.md pipeline summary mentions enrichment file when proposals are generated        | VERIFIED   | `write/SKILL.md` lines 354-359: ".mli Enrichment (odoc only)" summary section        |

**Score:** 13/13 truths verified

---

### Required Artifacts

| Artifact                              | Expected                                          | Status     | Details                                                                                             |
|---------------------------------------|---------------------------------------------------|------------|-----------------------------------------------------------------------------------------------------|
| `doc-writer/agents/doc-author.md`     | Odoc output mode conditional branch in Phase 2    | VERIFIED   | "Odoc Output Mode" heading present; `doc_system.*odoc` conditional; file output, dune registration, author-notes, enrichment workflow all present |
| `doc-writer/agents/doc-editor.md`     | .mld file discovery and odoc syntax handling      | VERIFIED   | `.mld` glob in Step 2; author-notes in Step 3; odoc syntax adjustments section; HTML comment bypass |
| `doc-writer/agents/doc-user-tester.md`| .mld file discovery for persona evaluation        | VERIFIED   | `doc/**/*.mld` glob in Step 3; `doc/index.mld` in homepage fallback chain Step 4                   |
| `doc-writer/skills/write/SKILL.md`    | Mode detection for .mld files                     | VERIFIED   | Conditional `doc/**/*.mld` glob in Step 0; `index.mld` scaffold filtering; `.mli Enrichment` in Step 7 |

All four artifacts: exist, are substantive (not stubs), and are wired into the pipeline.

---

### Key Link Verification

| From                          | To                               | Via                                   | Status  | Details                                                                                             |
|-------------------------------|----------------------------------|---------------------------------------|---------|-----------------------------------------------------------------------------------------------------|
| `doc-author.md`               | `.doc-writer/odoc.md`            | guidance file read at runtime         | WIRED   | Line 305: "Follow the odoc syntax from `.doc-writer/odoc.md` (already loaded in Step 1)"           |
| `doc-author.md`               | `doc/dune`                       | dune registration step                | WIRED   | Lines 309-325: explicit Read/Write `doc/dune` step referencing `(mld_files ...)` stanza            |
| `doc-author.md`               | `.doc-writer/author-notes.md`    | external author notes for odoc        | WIRED   | Lines 332-333: "Write all internal notes to `.doc-writer/author-notes.md` instead"                 |
| `doc-editor.md`               | `.doc-writer/author-notes.md`    | reads external notes instead of HTML  | WIRED   | Lines 66-67: "Read `.doc-writer/author-notes.md` instead of parsing HTML comments from doc files"   |
| `doc-author.md`               | `.doc-writer/mli-enrichment.md`  | enrichment proposal output file       | WIRED   | Lines 386-387: "Write all proposals to `.doc-writer/mli-enrichment.md`"                             |
| `doc-author.md`               | `scan-exports.sh`                | scan-exports output for undocumented symbols | NOT_WIRED | No reference to scan-exports.sh in doc-author.md; enrichment workflow describes direct Read/Glob of .mli files instead |

**Note on scan-exports.sh link:** Plan 17-02 listed this as a key link (`pattern: "scan-exports"`), but the implemented enrichment workflow uses direct Glob + Read tool calls on `.mli` files rather than the scan-exports.sh script. The plan stated the author "uses scan-exports output for undocumented symbol detection," but the actual implementation bypasses the script and reads .mli files directly. This is a deviation from the plan's key link specification, but the functional goal (detecting undocumented public values) is fully achieved through an equivalent mechanism. The RESEARCH.md pattern for enrichment (Pattern 4) was the design authority and is faithfully implemented.

---

### Requirements Coverage

| Requirement | Source Plan | Description                                                                         | Status    | Evidence                                                                           |
|-------------|------------|--------------------------------------------------------------------------------------|-----------|------------------------------------------------------------------------------------|
| OCML-02     | 17-01       | Doc-author writes .mld files with odoc syntax when doc_system is odoc               | SATISFIED | `doc-author.md`: "Odoc Output Mode" section, file output rules, `.mld` extension, `doc/` directory |
| OCML-03     | 17-01       | Doc-author registers .mld pages in doc/dune during write pass                       | SATISFIED | `doc-author.md`: "Dune registration (mandatory after each .mld write)" with Read/Write `doc/dune` |
| OCML-04     | 17-02       | Doc-author proposes doc comment enrichment for undocumented public values in .mli   | SATISFIED | `doc-author.md`: ".mli Doc Comment Enrichment Proposals" section with 3-step workflow, quality rules |
| OCML-05     | 17-01       | Editor handles .mld file discovery and odoc syntax in quality passes                | SATISFIED | `doc-editor.md`: conditional .mld discovery, odoc syntax adjustments for Pass 2/4, author-notes reading |

All four requirements assigned to Phase 17 are satisfied. No orphaned requirements found — REQUIREMENTS.md maps OCML-02 through OCML-05 to Phase 17, matching the plan declarations exactly.

---

### Anti-Patterns Found

No anti-patterns detected in the modified files:

- No TODO/FIXME/placeholder comments in the modified sections
- No empty implementations or stub returns
- No odoc syntax table duplicated from `odoc.md` into `doc-author.md` (the plan explicitly required this be avoided — confirmed absent)
- No HTML comment syntax in doc-author.md's odoc section (correctly directed to external file)

---

### Human Verification Required

None. All phase 17 deliverables are agent instruction files (`.md` prose documents). Their correctness is fully verifiable by reading the text and confirming the presence of required sections, patterns, and conditional branches. No runtime behavior, visual rendering, or external service integration is involved.

---

## Gaps Summary

No gaps found. All 13 truths are verified.

The one noted deviation (scan-exports.sh key link not implemented as specified) does not constitute a gap: the functional requirement (OCML-04 — enrichment proposals for undocumented .mli values) is fully satisfied. The plan's key link was an implementation hint, not a requirement. The implemented approach (direct Glob + Read of .mli files) achieves the same observable outcome.

---

_Verified: 2026-03-22_
_Verifier: Claude (gsd-verifier)_
