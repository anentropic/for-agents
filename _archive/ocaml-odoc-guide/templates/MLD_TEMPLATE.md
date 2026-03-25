# .mld File Templates

Templates for different documentation page types. Use underscores in filenames (never hyphens).

## Primary Package Landing Page (index.mld)

The hub that links to all documentation types.

```
{0 Project Name - One Line Description}

{1 Overview}

What the library does. How to install it.

{v
opam install my_library
v}

Minimal example:

{[
My_library.do_thing "hello"
]}

{1 Documentation}

{2 Tutorial}

{!page-getting_started} — Description.

{2 How-to Guides}

- {!page-some_guide} — Description (note if advanced/niche)

{2 Explanation}

- {!page-how_it_works} — Description

{1 API Reference}

Brief summary of the main API.

{[
val main_function : input -> output
]}

{1 Libraries}

- {!My_library} — Main library
- {!Secondary_a} — Description

{1 See Also}

- {{:https://example.com} Related project}

{1 Project}

- {{:https://github.com/user/my-library} GitHub repository}
```

## Tutorial Page (getting_started.mld)

Step-by-step, learning-oriented. The reader does things and learns by doing.

```
{0 Getting Started with My Library}

What the reader will have by the end. One sentence.

{b Prerequisites:} What they need installed.

{1 First Step}

Instruction. Show exactly what to do.

{[
(* code they type *)
]}

What they should see. What just happened.

{1 Second Step}

Build on the previous step.

{[
(* more code *)
(* val result : t = expected_value *)
]}

{1 What You've Learned}

- Bullet list of skills acquired

{1 Next Steps}

- {!page-some_guide} — Description
- {!My_library} — Full API reference
```

## Explanation Page (how_it_works.mld)

Understanding-oriented. Explains why, not how-to.

```
{0 How X Works}

Opening that states the problem concretely. No vague puffery.

{1 The Problem}

What problem does the reader need to understand? Be specific.

{1 Why Approach A}

Why this approach was chosen. What alternatives exist.

{1 How the Pipeline Works}

Walk through the process. Use concrete values.

{1 Design Decision: Y}

Explain a non-obvious choice. What trade-offs were made.

{1 Further Reading}

- {!page-getting_started} — Tutorial
- {{:https://example.com} External reference}
```

## How-to Guide (some_guide.mld)

Goal-oriented. The reader has a specific task to accomplish.

```
{0 How to Do X}

State when and why someone would need this. If it is a niche
use case, say so upfront.

{b Prerequisites:} What they need to know already.

{1 Step One}

What to do. Show the code or config.

{v
(* config file contents *)
v}

{1 Step Two}

Next action.

{[
(* code to write *)
(* val result : t *)
]}

{1 Troubleshooting}

{b Common error}

What causes it. How to fix it.

{1 See Also}

- {{:../other_package/index.html} Related package}
- {!page-how_it_works} — Background on why this works
```

## Secondary Package Overview (index.mld)

Brief. Explain what it does, why it is a separate package, show one example, link to API and back to primary docs.

```
{0 Secondary A - Brief Description}

{1 Overview}

What this package does. Why it exists separately from the
primary package. 1-2 paragraphs.

{1 Usage}

{[
let result = Secondary_a.do_thing input
(* val result : Secondary_a.t *)
]}

{1 API Reference}

{!modules:
Secondary_a.Main_module
}

{1 See Also}

- {{:../my_primary/index.html} My Primary} — Main library
- {{:../my_primary/getting_started.html} Getting Started} — Tutorial
```

## Tips

1. Start with user needs: what questions does the reader have?
2. Show result types in examples: `(* val x : type = value *)`
3. Cross-reference rather than re-explain concepts from other pages
4. Frame niche content honestly: "if you're unsure whether you need this, you don't"
5. Use underscores in filenames: hyphens break `{!page-...}` references
