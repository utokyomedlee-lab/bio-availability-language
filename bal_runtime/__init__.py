"""Independent BAL language lexer, parser and interpreter."""
__version__ = "0.5.0.dev1"
from .interpreter import Interpreter, BALRuntimeError
from .parser import parse
__all__ = ["Interpreter", "BALRuntimeError", "parse", "__version__"]
