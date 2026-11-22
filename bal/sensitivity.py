"""Variance-based global sensitivity analysis for the BAL core equation."""
from __future__ import annotations
import math
import random
from typing import Mapping

def _model(p):
    a,m,b,alpha,beta=(p[k] for k in ("a","m","b","alpha","beta"))
    if not (0.0<=a<=1.0 and 0.0<=m<1.0): raise ValueError("a must be in [0,1] and m in [0,1)")
    if min(b,alpha,beta)<=0: raise ValueError("b, alpha and beta must be positive")
    return math.log1p(alpha*a*(1.0-m))/math.log1p(beta*b)

def sobol_indices(ranges: Mapping[str,tuple[float,float]], n_samples: int=4096,
                  seed: int=2026) -> dict:
    """Estimate first-order S1 and total-order ST indices for independent uniform inputs."""
    names=("a","m","b","alpha","beta")
    if set(ranges)!=set(names): raise ValueError("ranges must define exactly a, m, b, alpha and beta")
    for name,bounds in ranges.items():
        if len(bounds)!=2 or not all(math.isfinite(float(v)) for v in bounds): raise ValueError(f"invalid range for {name}")
        lo,hi=map(float,bounds)
        if lo>=hi: raise ValueError(f"range for {name} must have lower < upper")
        if name=="a" and (lo<0 or hi>1): raise ValueError("a range must lie in [0,1]")
        if name=="m" and (lo<0 or hi>=1): raise ValueError("m range must lie in [0,1)")
        if name in ("b","alpha","beta") and lo<=0: raise ValueError(f"{name} range must be positive")
    if n_samples<128: raise ValueError("n_samples must be at least 128")
    rng=random.Random(seed)
    def draw(): return {k:rng.uniform(*ranges[k]) for k in names}
    A=[draw() for _ in range(n_samples)]; B=[draw() for _ in range(n_samples)]
    fA=[_model(x) for x in A]; fB=[_model(x) for x in B]
    pooled=fA+fB; mean=sum(pooled)/len(pooled)
    variance=sum((v-mean)**2 for v in pooled)/(len(pooled)-1)
    if variance<=0: raise ValueError("output variance is zero; sensitivity is undefined")
    results={}
    for name in names:
        AB=[]
        for ar,br in zip(A,B):
            hybrid=dict(ar); hybrid[name]=br[name]; AB.append(_model(hybrid))
        s1=sum(fB[i]*(AB[i]-fA[i]) for i in range(n_samples))/n_samples/variance
        st=sum((fA[i]-AB[i])**2 for i in range(n_samples))/(2*n_samples*variance)
        results[name]={"S1":s1,"ST":st}
    return {"method":"Saltelli first-order / Jansen total-order Monte Carlo estimators",
            "n_samples":n_samples,"seed":seed,"output_variance":variance,"indices":results,
            "note":"Monte Carlo estimates under independent uniform input ranges; assess convergence by increasing n_samples."}
