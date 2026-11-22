# BAL — Bio-Availability Language

**Independent interpreted language · development version 0.5.0.dev1**

BAL now includes its own `.bal` programming language frontend and interpreter:
lexer, parser, expression grammar, lexical scopes, functions, lists, dictionaries,
conditionals, loops, standard built-ins, a REPL, `bal run`, and `bal check`.
Its research built-ins connect the language to the BAL availability equation,
parameter fitting and global sensitivity modules.

## Independence

BAL has a separate language syntax, runtime package, command-line executable,
project metadata, documentation, tests and CI workflow. It has no BPL dependency
or BPL code. Python 3.10+ is used only as the reference implementation host.

## Install and run

```bash
python -m pip install .
bal --version
bal check examples/availability.bal
bal run examples/availability.bal
bal run examples/hello.bal
bal repl
```

## Example

```bal
let dds_rate = 0.70
let first_pass = 0.15
let feedback = 0.40
let y = availability(dds_rate, first_pass, feedback, 2.0, 1.2)
print y
```

See [the language specification](docs/BAL_LANGUAGE_SPEC.md). This is an independent
language prototype; it is not a clinical decision or dosing system.
