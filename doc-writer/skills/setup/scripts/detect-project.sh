#!/bin/bash
# detect-project.sh — scan project for doc system, language, existing docs, and source root
# Output: markdown format injected into setup skill via !`bash` dynamic context

echo "## Detected Configuration"
echo ""

# Doc system detection
if [ -f "mkdocs.yml" ] || [ -f "mkdocs.yaml" ]; then
  echo "- **Doc system:** mkdocs-material (found mkdocs.yml)"
elif [ -f "docusaurus.config.js" ] || [ -f "docusaurus.config.ts" ]; then
  echo "- **Doc system:** docusaurus (found docusaurus.config)"
elif [ -f ".vitepress/config.js" ] || [ -f ".vitepress/config.ts" ] || [ -f ".vitepress/config.mts" ]; then
  echo "- **Doc system:** vitepress (found .vitepress/config)"
elif SPHINX_CONF=$(for f in docs/conf.py docs/source/conf.py doc/conf.py doc/source/conf.py conf.py; do [ -f "$f" ] && echo "$f" && break; done) && [ -n "$SPHINX_CONF" ]; then
  echo "- **Doc system:** sphinx (found $SPHINX_CONF)"
else
  echo "- **Doc system:** plain-markdown (no doc system detected)"
fi

# Language detection
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "setup.cfg" ]; then
  echo "- **Language:** Python"
elif [ -f "package.json" ]; then
  if [ -f "tsconfig.json" ]; then
    echo "- **Language:** TypeScript"
  else
    echo "- **Language:** JavaScript"
  fi
elif [ -f "Cargo.toml" ]; then
  echo "- **Language:** Rust"
elif [ -f "go.mod" ]; then
  echo "- **Language:** Go"
else
  echo "- **Language:** Unknown"
fi

# Existing docs detection
DOC_DIR=""
if [ -d "docs" ]; then
  DOC_DIR="docs"
elif [ -d "doc" ]; then
  DOC_DIR="doc"
elif [ -d "documentation" ]; then
  DOC_DIR="documentation"
fi

if [ -n "$DOC_DIR" ]; then
  DOC_COUNT=$(find "$DOC_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "- **Existing docs:** Yes — ${DOC_COUNT} markdown file(s) in ${DOC_DIR}/"
else
  echo "- **Existing docs:** No docs directory found"
fi

# Source root detection
if [ -d "src" ]; then
  echo "- **Source root:** src/"
elif [ -d "lib" ]; then
  echo "- **Source root:** lib/"
elif [ -d "pkg" ]; then
  echo "- **Source root:** pkg/"
else
  echo "- **Source root:** . (no standard source directory detected)"
fi
