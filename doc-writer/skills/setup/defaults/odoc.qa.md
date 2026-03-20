# Odoc Q&A

Framework-specific questions for odoc setup.
Presented during /doc-writer:setup after doc system selection.
Auto-detect: check for dune-project in project root and (documentation ...) stanza in doc/dune.

## Detection

Config file: doc/dune
Features to detect:
- (documentation ...) stanza in doc/dune or any dune file
- Number of (package ...) blocks in dune-project (single vs multi-library)
- Existing .mld files in doc/ directory
- (odoc :with-doc) in dune-project package deps

## Question 1: Library structure

- header: "Structure"
- question: "How is this project organized?"
- detect_context: "Detected: {number of packages in dune-project}"
- options:
  - { label: "Single library", description: "One package with one library", recommend_if: "1 package detected" }
  - { label: "Multi-library", description: "Multiple packages (e.g. core + plugins + utilities)", recommend_if: "2+ packages detected" }
  - { label: "Type something else", description: "Describe a different project layout" }
  - { label: "Chat about this", description: "Discuss library organization" }

## Question 2: Author scope

- header: "Scope"
- question: "What should the documentation author work on?"
- options:
  - { label: ".mld pages + .mli doc comment improvements (Recommended)", description: "Write guide pages and add/improve doc comments on public .mli values that lack them", recommend_if: "always" }
  - { label: ".mld pages only", description: "Write guide pages only -- leave .mli files untouched", recommend_if: "never" }
  - { label: "Type something else", description: "Describe a different scope" }
  - { label: "Chat about this", description: "Discuss what each scope means" }

## Question 3: Guide pages

- header: "Guides"
- question: "Which guide page types should the documentation include?"
- multiSelect: true
- detect_context: "Detected: {existing .mld files in doc/}"
- options:
  - { label: "Getting started / Tutorial", description: "Step-by-step introduction for new users (getting_started.mld)", recommend_if: "always" }
  - { label: "How-to guides", description: "Goal-oriented guides for specific tasks", recommend_if: "3+ public modules" }
  - { label: "Explanation pages", description: "Background and design rationale (how_it_works.mld)", recommend_if: "complex domain logic" }
  - { label: "Type something else", description: "Describe different guide types" }
  - { label: "Chat about this", description: "See examples of each guide type" }

### Follow-on: Sub-topic questions

For each selected guide type above, present a follow-on sub-topic question.
Options are generated dynamically at setup time by scanning the project:

Scan targets:
- Module names from lib/*/dune (public_name field)
- Exported .mli signatures (type names, function names, module names)
- Existing .mld files in doc/ (to avoid duplicates)
- README.md feature sections and examples

Question template per selected guide type:
- header: "{guide_type} topics"
- question: "What sub-topics should the {guide_type} pages cover?"
- multiSelect: true
- options: (dynamically generated from scan results -- NOT static)
  - Each option: { label: "{suggested_topic}", description: "{why this topic, based on scan}" }
  - Plus: { label: "Type something else", description: "Add a custom sub-topic" }
  - Plus: { label: "Chat about this", description: "Discuss sub-topic selection" }

Example scan output for a color library:
- Tutorial sub-topics: "Basic color creation", "Color mixing", "Palette generation"
- How-to sub-topics: "Custom color spaces", "Terminal integration", "PPX usage"
- Explanation sub-topics: "Color quantization algorithm", "Capability detection"
