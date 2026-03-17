# Plain Markdown Q&A

Framework-specific questions for plain-markdown setup.
Presented during /doc-writer:setup after doc system selection.
Auto-detect: no config file (plain markdown is the fallback when no doc system detected).

## Detection

Config file: none
Features to detect: none (plain markdown has no configurable features)

## Question 1: Callout style

- header: "Callouts"
- question: "How should callouts (tips, warnings, notes) be formatted?"
- options:
  - { label: "Blockquotes", description: "Use > **Note:** and > **Warning:** blockquote pattern" }
  - { label: "None", description: "No special callout formatting -- just regular paragraphs" }
  - { label: "Type something else", description: "Describe a different callout style" }
  - { label: "Chat about this", description: "See examples of each style" }

## Question 2: Heading convention

- header: "Headings"
- question: "What case convention should headings use?"
- options:
  - { label: "Sentence case", description: "Only first word capitalized: 'Getting started with auth'" }
  - { label: "Title case", description: "Major words capitalized: 'Getting Started with Auth'" }
  - { label: "Type something else", description: "Describe a different convention" }
  - { label: "Chat about this", description: "Discuss heading conventions" }

## Question 3: Table of contents

- header: "TOC"
- question: "How should documentation pages be indexed?"
- options:
  - { label: "Index page", description: "Manual index.md with links to all pages" }
  - { label: "Filename-based", description: "Readers navigate by file/folder structure" }
  - { label: "Type something else", description: "Describe a different approach" }
  - { label: "Chat about this", description: "Discuss table of contents options" }
