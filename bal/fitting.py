"""Parameter estimation for the BAL normalized availability equation.

Uses only the Python standard library and damped Gauss-Newton least squares.
"""
from __future__ import annotations
import math
from typing import Iterable, Mapping, Any

def availability(a: float, m: float, b: float, alpha: float, beta: float) -> float:
    """Evaluate y = ln(1 + alpha*a*(1-m)) / ln(1 + beta*b)."""
    if not (0.0 <= a <= 1.0): raise ValueError("a must be in [0, 1]")
    if not (0.0 <= m < 1.0): raise ValueError("m must be in [0, 1)")
    if b <= 0 or alpha <= 0 or beta <= 0: raise ValueError("b, alpha and beta must be positive")
    return math.log1p(alpha*a*(1.0-m)) / math.log1p(beta*b)

def fit_alpha_beta(observations: Iterable[Mapping[str, float]], initial_alpha: float = 1.0,
                   initial_beta: float = 1.0, max_iterations: int = 200,
                   tolerance: float = 1e-10) -> dict[str, Any]:
    """Fit positive alpha and beta to rows containing a, m, b and observed y."""
    rows = list(observations)
    if len(rows) < 3: raise ValueError("at least three observations are required")
    if initial_alpha <= 0 or initial_beta <= 0: raise ValueError("initial parameters must be positive")
    for row in rows:
        for key in ("a", "m", "b", "y"):
            if key not in row or not math.isfinite(float(row[key])):
                raise ValueError(f"each observation needs a finite {key}")
        if float(row["y"]) < 0: raise ValueError("observed y must be non-negative")
    x = [math.log(initial_alpha), math.log(initial_beta)]
    def residuals(z):
        alpha, beta = math.exp(z[0]), math.exp(z[1])
        return [availability(float(r["a"]), float(r["m"]), float(r["b"]), alpha, beta)-float(r["y"]) for r in rows]
    def cost(rs): return 0.5*sum(v*v for v in rs)
    damping, converged, iteration = 1e-3, False, 0
    for iteration in range(1, max_iterations+1):
        r = residuals(x); base_cost = cost(r); h = 1e-5; jac = []
        for j in range(2):
            xp=x.copy(); xp[j]+=h; rp=residuals(xp)
            jac.append([(rp[i]-r[i])/h for i in range(len(rows))])
        j00=sum(v*v for v in jac[0]); j11=sum(v*v for v in jac[1])
        j01=sum(jac[0][i]*jac[1][i] for i in range(len(rows)))
        g0=sum(jac[0][i]*r[i] for i in range(len(rows)))
        g1=sum(jac[1][i]*r[i] for i in range(len(rows)))
        a00,a11=j00+damping,j11+damping; det=a00*a11-j01*j01
        if abs(det)<1e-24: break
        step=[(-g0*a11+g1*j01)/det,(-g1*a00+g0*j01)/det]
        candidate=[x[0]+step[0],x[1]+step[1]]
        if cost(residuals(candidate)) < base_cost:
            x=candidate; damping=max(damping/3.0,1e-12)
            if max(abs(step[0]),abs(step[1]))<tolerance:
                converged=True; break
        else:
            damping=min(damping*10.0,1e12)
            if damping>=1e12: break
    alpha,beta=math.exp(x[0]),math.exp(x[1]); final=residuals(x)
    return {"alpha":alpha,"beta":beta,"rmse":math.sqrt(sum(v*v for v in final)/len(rows)),
            "converged":converged,"iterations":iteration,"n_observations":len(rows)}
