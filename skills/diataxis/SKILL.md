---
name: diataxis
description: Diataxis content classification and structural templates for documentation pages.
user-invocable: false
---

# Diataxis Framework Reference

The Diataxis framework classifies documentation into four types based on what the reader needs. Each type serves a different purpose and has a different structural template. Before writing any documentation page, classify it into one of these four types and apply the corresponding template.

Understanding the distinctions is critical: a tutorial is not a how-to guide, and a reference is not an explanation. Misclassifying a page leads to content that tries to do two things at once and does neither well.

---

## Tutorial

**Orientation:** Learning-oriented
**Purpose:** Teach the reader by walking them through a complete, working example. The reader follows along and builds something concrete.
**When to use:** First contact with a feature or concept. The reader has never used this before and needs guided, hands-on experience. Tutorials answer: "Can you teach me how to do this?"

**What makes it different from a how-to guide:** A tutorial is for learning, not for accomplishing a specific task. It includes explanations of why each step matters. A how-to guide assumes the reader already understands the concepts and just needs the steps.

### Structural Template

```markdown
# [Tutorial Title: Build/Create a ...]

[1-2 sentence description of what you will build and what you will learn]

## Prerequisites

- [Specific prerequisite with version, e.g., "Python 3.9 or later"]
- [Required knowledge, e.g., "Basic familiarity with HTTP requests"]
- [Required setup, e.g., "A running PostgreSQL instance"]

## Step 1: [Action verb — Set up / Create / Configure ...]

[Brief explanation of what this step does and why it matters]

[Code block with the complete code for this step]

[Explanation of what the code does]

## Step 2: [Action verb ...]

[Continue pattern: explanation, code, explanation]

## Step N: [Final step]

[...]

## What You Learned

- [Key concept 1 demonstrated in this tutorial]
- [Key concept 2]
- [Key concept 3]

## Next Steps

- [Link to related how-to guide for specific tasks]
- [Link to reference for API details]
- [Link to more advanced tutorial]
```

---

## How-To Guide

**Orientation:** Task-oriented
**Purpose:** Provide direct steps to accomplish a specific, real-world goal. The reader knows what they want to do and needs to know how.
**When to use:** The reader has a concrete goal — "I need to configure authentication" or "I need to deploy to production." How-to guides answer: "How do I do this?"

**What makes it different from a tutorial:** A how-to guide is for doing, not for learning. It assumes the reader understands the underlying concepts and focuses on the steps. Explanations are minimal — just enough to avoid confusion.

### Structural Template

```markdown
# How to [accomplish specific goal]

[1 sentence stating what this guide helps you do]

## Prerequisites

- [What must already be in place]
- [Required access, credentials, or configuration]

## Steps

### 1. [Action verb — Configure / Install / Create ...]

[Direct instruction with code or command]

### 2. [Action verb ...]

[Direct instruction]

### N. [Verify / Confirm ...]

[How to verify the goal was accomplished]

## Troubleshooting

### [Common problem 1]

[Symptom and solution]

### [Common problem 2]

[Symptom and solution]
```

---

## Reference

**Orientation:** Information-oriented
**Purpose:** Provide precise, complete technical descriptions of the API, configuration options, or system components. The reader needs to look up specific details.
**When to use:** The reader is already using the software and needs exact specifications — function signatures, parameter types, return values, configuration keys. Reference answers: "What are the details of this?"

**What makes it different from an explanation:** Reference describes the machinery — what it is, what it accepts, what it returns. It does not discuss why the machinery exists or the thinking behind its design. Reference is austere and factual.

### Structural Template

```markdown
# [API/Component Name]

[1-2 sentence description of what this is and its primary purpose]

## Synopsis

[Function signature, CLI usage pattern, or configuration block]

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `param1` | `string` | Yes | — | [What it does] |
| `param2` | `number` | No | `10` | [What it does] |

## Return Value

[Type and description of what is returned]

[Table or description of possible return states/errors]

## Examples

### [Use case 1 — e.g., "Basic usage"]

[Code block with working example]

### [Use case 2 — e.g., "With optional parameters"]

[Code block with working example]

## Related

- [`relatedFunction()`](./related-function.md) — [brief description]
- [How-to: Accomplish X](../how-to/accomplish-x.md) — uses this API
```

---

## Explanation

**Orientation:** Understanding-oriented
**Purpose:** Help the reader understand why something works the way it does, the design decisions behind it, and how it fits into the bigger picture. Explanation provides context and insight.
**When to use:** The reader wants to understand the reasoning — "Why does the library use connection pooling?" or "What are the tradeoffs of this approach?" Explanation answers: "Why is it like this?"

**What makes it different from reference:** Explanation discusses concepts, context, and design rationale. Reference describes technical specifications. Explanation is discursive and connects ideas; reference is terse and factual.

### Structural Template

```markdown
# [Concept / Topic — e.g., "Understanding Connection Pooling"]

## Context

[Why this topic matters. What problem or situation led to this design.
Frame the discussion so the reader understands why they should care.]

## [The Concept]

[Core explanation of the idea. Use analogies where helpful.
Build understanding progressively — start with the simple version,
then add nuance.]

## How It Works

[Technical details of the mechanism, at the level appropriate for
the audience. Diagrams or step-by-step descriptions of the internal
process. This is not a how-to — the reader is learning how the
system works, not how to use it.]

## Tradeoffs and Alternatives

[What other approaches exist and why this one was chosen.
Be honest about limitations. Help the reader understand when
this approach is and is not appropriate.]

## Further Reading

- [Link to tutorial for hands-on experience]
- [Link to reference for technical details]
- [External resource for deeper understanding]
```

---

## Classification Decision Guide

When unsure which type a page should be, ask:

| Question | If yes... |
|----------|-----------|
| Is the reader learning something new through a guided experience? | **Tutorial** |
| Is the reader trying to accomplish a specific, practical goal? | **How-To Guide** |
| Is the reader looking up technical specifications or API details? | **Reference** |
| Is the reader trying to understand why something works a certain way? | **Explanation** |

A single page should be one type. If you find yourself mixing types (explaining concepts in a how-to guide, or adding steps to a reference page), split the content into separate pages of the appropriate types and cross-link them.
