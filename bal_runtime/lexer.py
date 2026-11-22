"""Lexer for the independent BAL scripting language."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int

class BALSyntaxError(Exception):
    pass

class Lexer:
    KEYWORDS = {"let", "print", "if", "else", "while", "fn", "return", "true", "false", "null", "and", "or", "not"}
    TWO_CHAR = {"==", "!=", "<=", ">=", "**"}
    SINGLE = set("+-*/%(){}[],:;.=<>!")

    def __init__(self, source: str):
        self.source, self.i, self.line, self.column = source, 0, 1, 1
        self.tokens = []

    def _peek(self, offset=0):
        pos = self.i + offset
        return self.source[pos] if pos < len(self.source) else ""

    def _advance(self):
        ch = self._peek()
        self.i += 1
        if ch == "\n": self.line += 1; self.column = 1
        else: self.column += 1
        return ch

    def tokenize(self):
        while self._peek():
            ch = self._peek()
            if ch in " \t\r": self._advance(); continue
            if ch == "\n" or ch == ";":
                line, col = self.line, self.column
                self._advance(); self.tokens.append(Token("SEP", ";", line, col)); continue
            if ch == "#":
                while self._peek() and self._peek() != "\n": self._advance()
                continue
            if ch.isdigit() or (ch == "." and self._peek(1).isdigit()):
                self._number(); continue
            if ch.isalpha() or ch == "_":
                self._identifier(); continue
            if ch in "\"'":
                self._string(); continue
            pair = ch + self._peek(1)
            if pair in self.TWO_CHAR:
                line, col = self.line, self.column
                self._advance(); self._advance(); self.tokens.append(Token(pair, pair, line, col)); continue
            if ch in self.SINGLE:
                line, col = self.line, self.column
                self._advance(); self.tokens.append(Token(ch, ch, line, col)); continue
            raise BALSyntaxError(f"Unexpected character {ch!r} at {self.line}:{self.column}")
        self.tokens.append(Token("EOF", None, self.line, self.column))
        return self.tokens

    def _number(self):
        line, col, start = self.line, self.column, self.i
        seen_dot = False
        while self._peek() and (self._peek().isdigit() or (self._peek() == "." and not seen_dot)):
            if self._peek() == ".": seen_dot = True
            self._advance()
        if self._peek() in ("e", "E"):
            self._advance()
            if self._peek() in ("+", "-"): self._advance()
            if not self._peek().isdigit(): raise BALSyntaxError(f"Invalid exponent at {line}:{col}")
            while self._peek().isdigit(): self._advance()
        raw = self.source[start:self.i]
        value = float(raw) if any(c in raw for c in ".eE") else int(raw)
        self.tokens.append(Token("NUMBER", value, line, col))

    def _identifier(self):
        line, col, start = self.line, self.column, self.i
        while self._peek() and (self._peek().isalnum() or self._peek() == "_"): self._advance()
        value = self.source[start:self.i]
        self.tokens.append(Token(value if value in self.KEYWORDS else "IDENT", value, line, col))

    def _string(self):
        line, col = self.line, self.column
        quote = self._advance()
        chars = []
        escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "\"": "\""}
        while self._peek() and self._peek() != quote:
            ch = self._advance()
            if ch == "\n": raise BALSyntaxError(f"Unterminated string at {line}:{col}")
            if ch == "\\":
                nxt = self._advance()
                if not nxt: break
                chars.append(escapes.get(nxt, nxt))
            else: chars.append(ch)
        if self._peek() != quote: raise BALSyntaxError(f"Unterminated string at {line}:{col}")
        self._advance()
        self.tokens.append(Token("STRING", "".join(chars), line, col))
