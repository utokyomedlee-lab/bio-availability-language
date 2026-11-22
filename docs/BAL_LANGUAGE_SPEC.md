# BAL Language Specification — 0.5.0 development

BAL is an independent interpreted programming language. It has its own `.bal`
source format, lexer, parser, expression grammar, lexical scopes, evaluator,
standard built-ins, command-line interface and release version. It does not
import, compile, embed or require BPL. The reference implementation is written
in Python 3.10+ and uses the Python standard library; this is the implementation
host, not BAL source syntax.

## Statements
- `let name = expression` declares a variable; `name = expression` updates it.
- `print expression` writes a value.
- `if expression { ... } else { ... }` and `while expression { ... }` control flow.
- `fn name(parameter, ...) { ... }` declares a function; `return expression` returns.
- `#` starts a line comment. Newlines and semicolons separate statements.

## Values and operators
Numbers, strings, booleans (`true`, `false`), `null`, lists and string-keyed
dictionaries are supported. Lists and dictionaries support indexing; dictionaries
also support dot access. Operators: unary `+ - ! not`; arithmetic
`+ - * / % **`; comparisons `== != < <= > >=`; logical `and or`.

## Standard library
General: `sqrt`, `log`, `log10`, `exp`, `abs`, `min`, `max`, `sum`,
`len`, `round`, `floor`, `ceil`, `range`, `str`, `int`, `float`,
`bool`, `type`. Data I/O: `read_json`, `write_json`, `read_csv`.
BAL domain: `availability(a,m,b,alpha,beta)`, `threshold(a,m,b,alpha,beta)`,
`fit_alpha_beta(observations)`, and `sobol_indices(ranges,n_samples,seed)`.

## Execution
Install with `python -m pip install .`, then use `bal run file.bal`,
`bal check file.bal`, or `bal repl`. `python -m bal_runtime` is also available.
No third-party runtime libraries are required after installation.

## Safety and scientific scope
Execution has a one-million-step guard and a bounded `range`. The interpreter
is not a sandbox for untrusted scripts. File I/O built-ins use the process's local
filesystem permissions. Biological results depend on model assumptions and
inputs; the language does not establish clinical validity or provide dosing advice.
