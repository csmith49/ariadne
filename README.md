# Ariadne

Ariadne is a set of tools and file formats for escaping from the labyrinth of benchmarking medium-sized scripts.

## What is Ariadne

In this repository is a collection of tools and modules intended to work together.

Critical to the story is the **Thread** message protocol, which allows for serial communication of region-based statistics across a variety of formats.

### What is a region

A region is a contiguous block of code. In the typical execution of a program, regions are opened and closed in a well-nested manner. In this way, regions mirror scopes/contexts.

### Why use regions

By design, regions are artifacts at the source-level. Annotating regions at the source level gives some confidence that the benchmarking being done is measuring the appropriate code.

Furthermore, regions mirror common syntactic forms and constructs, such as Python's context managers. Regions are easy to incorporate into existing code and natural to reason about.

## Thread

**Thread** is a message protocol that leaves just enough information to extract a variety of benchmarking statistics from post-hoc analysis tools.

In what follows, we present the structure of **Thread** messages and several examples.

### Front matter and format

All **Thread** messages begin with the *front matter*, which contains 1) an initial string `THREAD`, 2) an entity identifier, and 3) a timestamp. This front matter is derived from the following production rule:

```bnf
<FRONT-MATTER> := THREAD|<ENTITY-ID>|<TIME>
```

Entity identifiers are used in streaming mode to disambiguate between different processes. Timestamps are given as integers representing milliseconds from some fixed time.

### Commands

There are a total of five commands: `OPEN`, `CLOSE`, `INIT`, `TERMINATE`, and `VALUE`. Each command has a small set of positional parameters that follow.

The positional parameters are as follows:

```bnf
OPEN|<REGION-ID>
CLOSE|<REGION-ID>
INIT
TERMINATE
VALUE|<VALUE-ID>|<VALUE>
```

### Identifiers and values

Identifiers, as in the grammar productions `<ENTITY-ID>`, `<REGION-ID>`, and `<VALUE-ID>`, are all alphanumeric strings that can include underscores. That is, identifiers are identified by the following grammar:

```bnf
<IDENTIFIER> := [a-z A-Z 0-9 _]+
```

Values, as in the production `<VALUE>`, are given by the following grammar:

```bnf
<VALUE> := {<TYPE>:<LITERAL>}
<LITERAL> := <BOOL>
           | <INT>
           | <STRING>
<TYPE> := BOOL
        | INT
        | STRING
```

### Keywords

To support further analysis, each message can contain *keyword-value* pairs, which are encoded as follows:

```bnf
<KEYWORD> := <IDENTIFIER>:<VALUE>
```

### Total grammar

We present the entirety of the message grammar in one place for convenience:

```bnf
<MESSAGE> := THREAD|<ENTITY-ID>|<TIME>|<COMMAND> <KEYWORDS>

<COMMAND> := OPEN|<REGION-ID>
           | CLOSE|<REGION-ID>
           | INIT
           | TERMINATE
           | VALUE|<VALUE-ID>|<VALUE>

<KEYWORDS> := <empty>
            | |<KEYWORD> <KEYWORDS>

<ENTITY-ID> := <IDENTIFIER>
<REGION-ID> := <IDENTIFIER>
<VALUE-ID> := <IDENTIFIER>

<KEYWORD> := <IDENTIFIER>:<VALUE>

<IDENTIFIER> := [a-z A-Z 0-9 _]+

<TIME> := <INT>

<VALUE> := {<TYPE>:<LITERAL>}
<LITERAL> := <BOOL>
           | <INT>
           | <STRING>
<TYPE> := BOOL
        | INT
        | STRING
```

## Thread intermediate representation

The well-nested nature of Thread messages mean that there is a very convenient intermediate representation, given below as ML-style structs:

```ocaml
type thread = region list;

type region = {
    regionId : string;
    values : value IdentifierMap.t;
    subregions : region list;
}
```

This structure mimics many ad-hoc data formats, such as JSON, TOML, and YAML. Thread has the advantage over these formats in that, as messages are sent and received serially, the data need not be presented monolithically. Thread files can be embedded in a variety of output streams as messages are generated.

In practice, many of the analysis tools do not use the above IR directly. Instead, we partially evaluate the IR interpreter, lazily building the structure as needed by the analysis.