"""Recursive-descent statement parser and Pratt expression parser for BAL."""
from .lexer import Lexer, Token, BALSyntaxError

class Parser:
    PRECEDENCE = {"or": 1, "and": 2, "==": 3, "!=": 3, "<": 4, "<=": 4, ">": 4, ">=": 4, "+": 5, "-": 5, "*": 6, "/": 6, "%": 6, "**": 7}
    def __init__(self, tokens): self.tokens, self.i = tokens, 0
    def peek(self, offset=0): return self.tokens[min(self.i+offset, len(self.tokens)-1)]
    def advance(self): token=self.peek(); self.i+=1; return token
    def match(self,*kinds):
        if self.peek().kind in kinds: self.advance(); return True
        return False
    def expect(self,kind,message=None):
        token=self.peek()
        if token.kind != kind: raise BALSyntaxError(message or f"Expected {kind}, got {token.kind} at {token.line}:{token.column}")
        return self.advance()
    def parse(self):
        statements=[]; self._separators()
        while self.peek().kind!="EOF":
            before=self.i; statements.append(self.statement())
            if self.i==before: raise BALSyntaxError("Parser made no progress")
            self._separators()
        return ("program",statements)
    def _separators(self):
        while self.match("SEP"): pass
    def statement(self):
        if self.match("let"):
            name=self.expect("IDENT","Expected variable name after 'let'").value
            self.expect("=","Expected '=' after variable name")
            return ("let",name,self.expression())
        if self.match("print"): return ("print",self.expression())
        if self.match("if"):
            condition=self.expression(); then_block=self.block(); self._separators()
            else_block=self.block() if self.match("else") else None
            return ("if",condition,then_block,else_block)
        if self.match("while"):
            condition=self.expression(); return ("while",condition,self.block())
        if self.match("fn"):
            name=self.expect("IDENT","Expected function name").value; self.expect("("); params=[]
            if self.peek().kind!=")":
                params.append(self.expect("IDENT","Expected parameter name").value)
                while self.match(","): params.append(self.expect("IDENT","Expected parameter name").value)
            self.expect(")")
            if len(params)!=len(set(params)): raise BALSyntaxError(f"Duplicate parameter in function {name}")
            return ("fn",name,params,self.block())
        if self.match("return"):
            if self.peek().kind in ("SEP","}","EOF"): return ("return",("literal",None))
            return ("return",self.expression())
        if self.peek().kind=="IDENT" and self.peek(1).kind=="=":
            name=self.advance().value; self.advance(); return ("assign",name,self.expression())
        return ("expr",self.expression())
    def block(self):
        self.expect("{","Expected '{' to begin block"); statements=[]; self._separators()
        while self.peek().kind not in ("}","EOF"):
            statements.append(self.statement()); self._separators()
        self.expect("}","Expected '}' to close block"); return statements
    def expression(self,min_precedence=1):
        left=self.prefix()
        while True:
            if self.peek().kind=="(":
                self.advance(); args=[]
                if self.peek().kind!=")":
                    args.append(self.expression())
                    while self.match(","): args.append(self.expression())
                self.expect(")"); left=("call",left,args); continue
            if self.match("["):
                index=self.expression(); self.expect("]"); left=("index",left,index); continue
            if self.match("."):
                name=self.expect("IDENT","Expected property name after '.'").value; left=("member",left,name); continue
            op=self.peek().kind; precedence=self.PRECEDENCE.get(op,0)
            if precedence<min_precedence: break
            self.advance(); right=self.expression(precedence if op=="**" else precedence+1)
            left=("binary",op,left,right)
        return left
    def prefix(self):
        token=self.advance()
        if token.kind in ("NUMBER","STRING"): return ("literal",token.value)
        if token.kind=="true": return ("literal",True)
        if token.kind=="false": return ("literal",False)
        if token.kind=="null": return ("literal",None)
        if token.kind=="IDENT": return ("variable",token.value)
        if token.kind in ("-","!","not","+"): return ("unary",token.kind,self.expression(8))
        if token.kind=="(":
            expr=self.expression(); self.expect(")"); return expr
        if token.kind=="[":
            items=[]
            if self.peek().kind!="]":
                items.append(self.expression())
                while self.match(","):
                    if self.peek().kind=="]": break
                    items.append(self.expression())
            self.expect("]"); return ("list",items)
        if token.kind=="{":
            pairs=[]
            if self.peek().kind!="}":
                while True:
                    kt=self.advance()
                    if kt.kind=="IDENT": key=("literal",kt.value)
                    elif kt.kind=="STRING": key=("literal",kt.value)
                    else: raise BALSyntaxError(f"Dictionary key must be identifier or string at {kt.line}:{kt.column}")
                    self.expect(":","Expected ':' after dictionary key"); pairs.append((key,self.expression()))
                    if not self.match(",") or self.peek().kind=="}": break
            self.expect("}"); return ("dict",pairs)
        raise BALSyntaxError(f"Unexpected token {token.kind} at {token.line}:{token.column}")

def parse(source): return Parser(Lexer(source).tokenize()).parse()
