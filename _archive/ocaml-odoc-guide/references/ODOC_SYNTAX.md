# odoc Markup Syntax Quick Reference

## Text Formatting

- `{b bold text}` - **bold**
- `{i italic text}` - *italic*
- `{e emphasized}` - emphasis
- `{{:url}link text}` - external link
- `{!Module.value}` - cross-reference to code

## Headings

```ocaml
{0 Top level (page title)}
{1 Section}
{2 Subsection}
{3 Subsubsection}
{4:custom_anchor Subsubsection with custom anchor}
```

## Code

### Inline Code
- `` `code` `` - inline code

### Code Blocks
```ocaml
{[
  (* OCaml code block - will be compiled! *)
  let x = 42
]}
```

### Verbatim Blocks
```ocaml
{v
Raw text, not compiled
No syntax highlighting
v}
```

## Lists

### Unordered Lists
```ocaml
- Item 1
- Item 2
  - Nested item
- Item 3
```

### Ordered Lists
```ocaml
+ First
+ Second
  + Nested
+ Third
```

## Documentation Tags

```ocaml
(** Function description.

    @param name Parameter description
    @return Return value description
    @raise Exception Condition when raised
    @see <url> External reference
    @since 1.0.0
    @deprecated Use {!other_function} instead
    @author Name *)
```

## Modules

```ocaml
(** {1 Modules}

    - {!module:Submodule} - Description
    - {!module-type:S} - Module type description *)
```

## Cross-References

```ocaml
{!Module}              (* Link to module *)
{!Module.Type}         (* Link to type *)
{!Module.value}        (* Link to value *)
{!Module.Type.field}   (* Link to record field *)
{!module:Module}       (* Explicit module link *)
{!module-type:S}       (* Link to module type *)
{!type:t}              (* Link to type *)
{!exception:Exn}       (* Link to exception *)
```

## Sections and Anchors

```ocaml
{1:anchor_name Section Title}

(** See {!section-anchor_name} *)
```

## Special Blocks

### Examples
```ocaml
{[
  (* Example code - gets compiled *)
  let example = "value"
]}
```

### Math (if supported)
```ocaml
{m x^2 + y^2 = z^2}
```

## Common Patterns

### Multiple Examples
```ocaml
(** Function description.

    {[
      (* Basic usage *)
      let x = f 1
    ]}

    {[
      (* Advanced usage *)
      let y = f 2 |> g
    ]}

    @param input Description *)
```

### Grouping Functions
```ocaml
(** {1 Conversion Functions}

    Convert between different representations.

    {2 To String}

    Functions that produce string output. *)

val to_string : t -> string
(** Convert to string representation.

    {[ let s = to_string value ]} *)

val to_int : t -> int
(** Convert to integer representation.

    {[ let n = to_int value (* 42 *) ]} *)
```

### Module Documentation
```ocaml
(** Duration parsing and formatting.

    This module parses human-readable duration strings
    and converts them to seconds.

    {1 Example}

    {[
      open Duration

      let secs = of_string "2h30m"
      let pretty = to_string secs
    ]}

    {1 API} *)

(* Function declarations follow... *)
```
