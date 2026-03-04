#!/usr/bin/env bash
# Phase 2 — Doc Author Agent
# Static analysis tests for AUTH-01 through AUTH-09
# Tests verify that agents/doc-author.md contains the required behavioral
# instructions for each AUTH requirement.
#
# Usage: bash tests/phase-02/test_auth_requirements.sh
# Exit:  0 if all tests pass, 1 if any fail

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGENT_FILE="${PROJECT_ROOT}/agents/doc-author.md"

PASS=0
FAIL=0
FAILURES=()

# ---------------------------------------------------------------------------
# Test runner helpers
# ---------------------------------------------------------------------------

pass() {
  local test_id="$1"
  local description="$2"
  echo "  PASS  ${test_id}: ${description}"
  PASS=$((PASS + 1))
}

fail() {
  local test_id="$1"
  local description="$2"
  echo "  FAIL  ${test_id}: ${description}"
  FAIL=$((FAIL + 1))
  FAILURES+=("${test_id}: ${description}")
}

assert_contains() {
  local test_id="$1"
  local description="$2"
  local pattern="$3"
  if grep -qE "${pattern}" "${AGENT_FILE}"; then
    pass "${test_id}" "${description}"
  else
    fail "${test_id}" "${description}"
  fi
}

assert_not_contains() {
  local test_id="$1"
  local description="$2"
  local pattern="$3"
  if grep -qE "${pattern}" "${AGENT_FILE}"; then
    fail "${test_id}" "${description}"
  else
    pass "${test_id}" "${description}"
  fi
}

# ---------------------------------------------------------------------------
# Guard: agent file must exist
# ---------------------------------------------------------------------------

if [ ! -f "${AGENT_FILE}" ]; then
  echo "FATAL: agent file not found: ${AGENT_FILE}"
  exit 1
fi

echo ""
echo "Testing: ${AGENT_FILE}"
echo "================================================================"

# ---------------------------------------------------------------------------
# AUTH-01: Doc Author classifies content type before writing and applies
#          the correct structural template for each type
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-01: Content classification before writing"

assert_contains "AUTH-01.1" \
  "agent classifies pages using diataxis types (tutorial mentioned)" \
  "tutorial"

assert_contains "AUTH-01.2" \
  "agent classifies how-to pages" \
  "how-to"

assert_contains "AUTH-01.3" \
  "agent classifies explanation pages" \
  "explanation"

assert_contains "AUTH-01.4" \
  "agent uses classification to determine page type before writing" \
  "classify|classif|Classify|classification|classified"

assert_contains "AUTH-01.5" \
  "agent references diataxis skill for classification decision guide" \
  "diataxis"

# ---------------------------------------------------------------------------
# AUTH-02: All pages of the same doc type follow the same template structure
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-02: Consistent template structure per doc type"

assert_contains "AUTH-02.1" \
  "agent applies structural template for each page type" \
  "structural template|template.*doc type|template.*type"

assert_contains "AUTH-02.2" \
  "agent enforces Rule 3 (Consistent Structure)" \
  "Rule 3|Consistent Structure"

assert_contains "AUTH-02.3" \
  "agent uses preloaded diataxis skill templates" \
  "preloaded diataxis|diataxis skill|from the.*diataxis"

# ---------------------------------------------------------------------------
# AUTH-03: Internal details filtered out — no test utils, CI config,
#          dev scripts in end-user docs
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-03: Internal detail filtering"

assert_contains "AUTH-03.1" \
  "agent filters test directories from user-facing docs" \
  "tests/|__tests__|spec/|test_\*"

assert_contains "AUTH-03.2" \
  "agent filters CI/CD configuration from user-facing docs" \
  "CI/CD|\.github/workflows|gitlab-ci|Jenkinsfile"

assert_contains "AUTH-03.3" \
  "agent filters dev scripts and task runners from user-facing docs" \
  "justfile|Makefile|dev scripts|task runners"

assert_contains "AUTH-03.4" \
  "agent filters pre-commit hooks and linter config from user-facing docs" \
  "pre-commit|\.eslintrc|ruff\.toml"

assert_contains "AUTH-03.5" \
  "agent uses INTERNAL NOTES HTML comment format for captured internal details" \
  "INTERNAL NOTES FOR EDITOR"

assert_contains "AUTH-03.6" \
  "agent filters build tool configuration from user-facing docs" \
  "webpack\.config|vite\.config|tsconfig\.json|pyproject\.toml"

# ---------------------------------------------------------------------------
# AUTH-04: Author reads selected doc-system guidance file and produces
#          output using that system's syntax
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-04: Doc-system guidance file read and applied"

assert_contains "AUTH-04.1" \
  "agent reads .doc-writer/{doc_system}.md guidance file" \
  "doc-writer.*\{doc_system\}\.md|\.doc-writer/\{doc_system\}"

assert_contains "AUTH-04.2" \
  "agent applies doc-system formatting from guidance file when writing" \
  "Apply doc-system formatting|apply.*doc-system|formatting.*guidance"

assert_contains "AUTH-04.3" \
  "agent reads config.yaml to determine doc_system value" \
  "config\.yaml"

assert_contains "AUTH-04.4" \
  "agent prompt includes anti-pattern: do not hardcode doc-system syntax" \
  "[Dd]o not hardcode|[Nn]ot hardcode|[Nn]ever hardcode|Do NOT hardcode"

# ---------------------------------------------------------------------------
# AUTH-05: README.md has its own template with quick start, installation,
#          key features
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-05: README template with required sections"

assert_contains "AUTH-05.1" \
  "agent has dedicated README template section" \
  "README Template|Section 4.*README|README.*Template"

assert_contains "AUTH-05.2" \
  "README template includes Quick Start section" \
  "Quick Start"

assert_contains "AUTH-05.3" \
  "README template includes installation instruction" \
  "[Ii]nstallation|[Ii]nstall command"

assert_contains "AUTH-05.4" \
  "README template includes Key Features section" \
  "Key Features"

assert_contains "AUTH-05.5" \
  "README template includes project description" \
  "[Dd]escription"

assert_contains "AUTH-05.6" \
  "README template includes license section" \
  "[Ll]icense"

assert_contains "AUTH-05.7" \
  "README template includes docs URL link" \
  "[Dd]ocs.*[Uu]rl|Full Documentation|docs_url"

# ---------------------------------------------------------------------------
# AUTH-06: MAINTAINER.md has its own template with setup, architecture,
#          contribution guidelines
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-06: MAINTAINER template with required sections"

assert_contains "AUTH-06.1" \
  "agent has dedicated MAINTAINER template section" \
  "MAINTAINER Template|Section 5.*MAINTAINER|MAINTAINER.*Template"

assert_contains "AUTH-06.2" \
  "MAINTAINER template includes dev setup section" \
  "Dev Setup|[Dd]ev setup|development setup"

assert_contains "AUTH-06.3" \
  "MAINTAINER template includes architecture overview" \
  "[Aa]rchitecture"

assert_contains "AUTH-06.4" \
  "MAINTAINER template includes CI/CD process section" \
  "CI/CD"

assert_contains "AUTH-06.5" \
  "MAINTAINER template includes release process section" \
  "[Rr]elease [Pp]rocess|Release Process"

assert_contains "AUTH-06.6" \
  "MAINTAINER template includes decision log section" \
  "[Dd]ecision [Ll]og|Decision Log"

assert_contains "AUTH-06.7" \
  "MAINTAINER template includes common development tasks" \
  "Common Development Tasks|Common.*Tasks|[Cc]ommon tasks"

# ---------------------------------------------------------------------------
# AUTH-07: Every feature page includes working, realistic code examples
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-07: Working realistic code examples"

assert_contains "AUTH-07.1" \
  "agent sources examples from both source code and test files" \
  "[Ss]ource.*test files|test files.*[Ss]ource|from BOTH source"

assert_contains "AUTH-07.2" \
  "agent requires first example to be self-contained with imports" \
  "self-contained|[Ff]irst example"

assert_contains "AUTH-07.3" \
  "agent requires all imports in first example" \
  "[Ii]mports|[Ii]nclude all.*imports"

assert_contains "AUTH-07.4" \
  "agent requires happy path as primary example, error handling separate" \
  "[Hh]appy path"

assert_contains "AUTH-07.5" \
  "agent requires all fenced code blocks to specify a language" \
  "[Ff]enced code blocks.*language|specify.*language|bare triple backticks"

assert_contains "AUTH-07.6" \
  "agent prohibits generating API calls not observed in source" \
  "[Nn]ever generate|not observed"

# ---------------------------------------------------------------------------
# AUTH-08: Python/mkdocs projects support blacken-docs formatting and
#          doctest validation
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-08: Python/MkDocs formatting support"

assert_contains "AUTH-08.1" \
  "agent has conditional Python/MkDocs section" \
  "[Pp]ython.*[Mm][Kk][Dd]ocs|[Mm][Kk][Dd]ocs.*[Pp]ython"

assert_contains "AUTH-08.2" \
  "agent specifies Black-compatible code formatting for Python" \
  "[Bb]lack.compatible|[Bb]lack formatting|Black-compatible"

assert_contains "AUTH-08.3" \
  "agent mentions blacken-docs tool compatibility" \
  "blacken-docs"

assert_contains "AUTH-08.4" \
  "agent specifies doctest-compatible pattern usage" \
  "doctest|Doctest"

assert_contains "AUTH-08.5" \
  "agent specifies Black line length of 88 characters" \
  "88"

assert_contains "AUTH-08.6" \
  "agent specifies Black double-quote string convention" \
  "double quotes|double quote"

# ---------------------------------------------------------------------------
# AUTH-09: Vocabulary and assumed knowledge level are calibrated to the
#          configured audience
# ---------------------------------------------------------------------------

echo ""
echo "AUTH-09: Audience calibration"

assert_contains "AUTH-09.1" \
  "agent reads never_assume list from config for audience calibration" \
  "never_assume"

assert_contains "AUTH-09.2" \
  "agent includes per-page audience reminder to prevent calibration drift" \
  "[Pp]er.page.*reminder|reminder.*calibrat|prevent.*drift|calibration drift"

assert_contains "AUTH-09.3" \
  "agent requires no term from never_assume used without explanation" \
  "never_assume.*without explanation|without explanation.*never_assume|never_assume.*list.*used without"

assert_contains "AUTH-09.4" \
  "agent references Rule 5 (Audience-Calibrated Language)" \
  "Rule 5|Audience-Calibrated"

assert_contains "AUTH-09.5" \
  "agent calibrates vocabulary to configured skill_level" \
  "skill_level|skill level"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
echo "================================================================"
echo "Results: ${PASS} passed, ${FAIL} failed"
echo ""

if [ "${FAIL}" -gt 0 ]; then
  echo "FAILED tests:"
  for f in "${FAILURES[@]}"; do
    echo "  - ${f}"
  done
  echo ""
  exit 1
fi

echo "All AUTH requirements verified in agents/doc-author.md."
exit 0
