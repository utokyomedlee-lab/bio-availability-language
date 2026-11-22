"""BAL language evaluator with lexical scopes and guarded execution."""
import csv, json, math
from pathlib import Path
from .parser import parse

class BALRuntimeError(Exception): pass
class Environment:
    def __init__(self,parent=None): self.values,self.parent={},parent
    def define(self,name,value): self.values[name]=value; return value
    def get(self,name):
        if name in self.values: return self.values[name]
        if self.parent: return self.parent.get(name)
        raise BALRuntimeError(f"Undefined variable: {name}")
    def assign(self,name,value):
        if name in self.values: self.values[name]=value; return value
        if self.parent: return self.parent.assign(name,value)
        raise BALRuntimeError(f"Cannot assign undefined variable: {name}")
class ReturnSignal(Exception):
    def __init__(self,value): self.value=value
class BALFunction:
    def __init__(self,name,params,body,closure,interpreter): self.name,self.params,self.body,self.closure,self.interpreter=name,params,body,closure,interpreter
    def __call__(self,*args):
        if len(args)!=len(self.params): raise BALRuntimeError(f"{self.name} expects {len(self.params)} arguments, got {len(args)}")
        env=Environment(self.closure)
        for key,value in zip(self.params,args): env.define(key,value)
        try: self.interpreter.execute_block(self.body,env)
        except ReturnSignal as signal: return signal.value
        return None

class Interpreter:
    MAX_STEPS=1_000_000
    def __init__(self,output=print):
        self.output,self.steps=output,0; self.globals=Environment(); self._install_builtins()
    def _install_builtins(self):
        funcs={"print":lambda *xs:self.output(" ".join(str(x) for x in xs)),
        "sqrt":math.sqrt,"log":math.log,"log10":math.log10,"exp":math.exp,
        "abs":abs,"min":min,"max":max,"sum":sum,"len":len,"round":round,
        "floor":math.floor,"ceil":math.ceil,"range":self._range,"str":str,
        "int":int,"float":float,"bool":bool,"type":lambda x:type(x).__name__,
        "read_json":self._read_json,"write_json":self._write_json,"read_csv":self._read_csv,
        "availability":self._availability,"threshold":self._threshold,
        "fit_alpha_beta":self._fit_alpha_beta,"sobol_indices":self._sobol_indices}
        for name,value in funcs.items(): self.globals.define(name,value)
    @staticmethod
    def _range(*args):
        values=list(range(*[int(x) for x in args]))
        if len(values)>100_000: raise BALRuntimeError("range is limited to 100000 items")
        return values
    @staticmethod
    def _read_json(path):
        with Path(str(path)).open("r",encoding="utf-8") as f: return json.load(f)
    @staticmethod
    def _write_json(path,value):
        with Path(str(path)).open("w",encoding="utf-8") as f: json.dump(value,f,ensure_ascii=False,indent=2)
        return str(path)
    @staticmethod
    def _read_csv(path):
        with Path(str(path)).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
    @staticmethod
    def _availability(a,m,b,alpha,beta):
        from bal.fitting import availability
        return availability(float(a),float(m),float(b),float(alpha),float(beta))
    @staticmethod
    def _threshold(a,m,b,alpha,beta):
        y=Interpreter._availability(a,m,b,alpha,beta)
        return {"value":y,"above":y>1.0,"boundary":y==1.0,"margin":y-1.0}
    @staticmethod
    def _fit_alpha_beta(rows):
        from bal.fitting import fit_alpha_beta
        return fit_alpha_beta(rows)
    @staticmethod
    def _sobol_indices(ranges,n_samples=4096,seed=2026):
        from bal.sensitivity import sobol_indices
        return sobol_indices({k:tuple(float(x) for x in v) for k,v in ranges.items()},int(n_samples),int(seed))
    def run(self,source):
        tree=parse(source); self.steps=0
        try: self.execute_block(tree[1],self.globals)
        except ReturnSignal as exc: raise BALRuntimeError("'return' used outside a function") from exc
    def execute_block(self,statements,env):
        for statement in statements:
            self.steps+=1
            if self.steps>self.MAX_STEPS: raise BALRuntimeError("Execution step limit exceeded")
            self.execute(statement,env)
    def execute(self,node,env):
        kind=node[0]
        if kind=="let": env.define(node[1],self.evaluate(node[2],env)); return
        if kind=="assign": env.assign(node[1],self.evaluate(node[2],env)); return
        if kind=="print": self.output(str(self.evaluate(node[1],env))); return
        if kind=="expr": self.evaluate(node[1],env); return
        if kind=="if":
            branch=node[2] if self.evaluate(node[1],env) else node[3]
            if branch is not None: self.execute_block(branch,Environment(env))
            return
        if kind=="while":
            loops=0
            while self.evaluate(node[1],env):
                loops+=1; self.steps+=1
                if loops>self.MAX_STEPS or self.steps>self.MAX_STEPS: raise BALRuntimeError("Loop iteration limit exceeded")
                self.execute_block(node[2],Environment(env))
            return
        if kind=="fn": env.define(node[1],BALFunction(node[1],node[2],node[3],env,self)); return
        if kind=="return": raise ReturnSignal(self.evaluate(node[1],env))
        raise BALRuntimeError(f"Unknown statement node: {kind}")
    def evaluate(self,node,env):
        kind=node[0]
        if kind=="literal": return node[1]
        if kind=="variable": return env.get(node[1])
        if kind=="list": return [self.evaluate(x,env) for x in node[1]]
        if kind=="dict": return {self.evaluate(k,env):self.evaluate(v,env) for k,v in node[1]}
        if kind=="unary":
            value=self.evaluate(node[2],env)
            if node[1]=="-": return -value
            if node[1]=="+": return +value
            if node[1] in ("!","not"): return not value
        if kind=="binary":
            op=node[1]; left=self.evaluate(node[2],env)
            if op=="and": return bool(left) and bool(self.evaluate(node[3],env))
            if op=="or": return bool(left) or bool(self.evaluate(node[3],env))
            right=self.evaluate(node[3],env)
            ops={"+":lambda:left+right,"-":lambda:left-right,"*":lambda:left*right,
            "/":lambda:left/right,"%":lambda:left%right,"**":lambda:left**right,
            "==":lambda:left==right,"!=":lambda:left!=right,"<":lambda:left<right,
            "<=":lambda:left<=right,">":lambda:left>right,">=":lambda:left>=right}
            try: return ops[op]()
            except (KeyError,TypeError,ValueError,ZeroDivisionError,OverflowError) as exc: raise BALRuntimeError(f"Invalid operation {op}: {exc}") from exc
        if kind=="call":
            callee=self.evaluate(node[1],env); args=[self.evaluate(x,env) for x in node[2]]
            if not callable(callee): raise BALRuntimeError("Attempted to call a non-function value")
            try: return callee(*args)
            except (BALRuntimeError,ReturnSignal): raise
            except Exception as exc: raise BALRuntimeError(f"Function call failed: {exc}") from exc
        if kind=="index":
            target=self.evaluate(node[1],env); index=self.evaluate(node[2],env)
            try: return target[index]
            except (KeyError,IndexError,TypeError) as exc: raise BALRuntimeError(f"Invalid index: {exc}") from exc
        if kind=="member":
            target=self.evaluate(node[1],env)
            if isinstance(target,dict) and node[2] in target: return target[node[2]]
            if node[2]=="length" and hasattr(target,"__len__"): return len(target)
            raise BALRuntimeError(f"Unknown member: {node[2]}")
        raise BALRuntimeError(f"Unknown expression node: {kind}")
