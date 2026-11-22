"""Command-line interface for the BAL language runtime."""
import argparse, sys
from pathlib import Path
from . import __version__
from .interpreter import Interpreter, BALRuntimeError
from .parser import parse
from .lexer import BALSyntaxError

def main(argv=None):
    parser=argparse.ArgumentParser(prog="bal",description="BAL — Bio-Availability Language interpreter")
    parser.add_argument("command",nargs="?",choices=("run","check","repl"),default="run")
    parser.add_argument("file",nargs="?")
    parser.add_argument("--version",action="version",version=f"BAL {__version__}")
    args=parser.parse_args(argv)
    if args.command=="repl": return repl()
    if not args.file: parser.error("a .bal source file is required (or use: bal repl)")
    path=Path(args.file)
    if path.suffix.lower()!=".bal":
        print("BAL source files must use the .bal extension",file=sys.stderr); return 2
    try:
        source=path.read_text(encoding="utf-8")
        if args.command=="check": parse(source); print(f"OK: {path}"); return 0
        Interpreter().run(source); return 0
    except (OSError,BALSyntaxError,BALRuntimeError) as exc:
        print(f"BAL error: {exc}",file=sys.stderr); return 1

def repl():
    runtime=Interpreter()
    print(f"BAL {__version__} interactive shell. Type :quit to exit.")
    while True:
        try: line=input("bal> ")
        except EOFError: print(); return 0
        if line.strip() in (":quit",":q","exit"): return 0
        if not line.strip(): continue
        try: runtime.run(line)
        except (BALSyntaxError,BALRuntimeError) as exc: print(f"BAL error: {exc}",file=sys.stderr)

if __name__=="__main__": raise SystemExit(main())
