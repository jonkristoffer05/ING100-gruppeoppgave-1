"""Ærlig numerisk validering av enkle ligninger og ODE-er."""
from __future__ import annotations
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

def _parse(text, local=None):
    text = str(text).strip().replace("^", "**").replace("j", "I")
    base = {"Eq": sp.Eq, "exp": sp.exp, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "sqrt": sp.sqrt, "I": sp.I, "pi": sp.pi}
    base.update(local or {})
    for name in ("x", "t", "a", "b", "c", "C1", "C2"): base.setdefault(name, sp.Symbol(name, real=True))
    base.setdefault("y", sp.Function("y"))
    return parse_expr(text, local_dict=base, transformations=_TRANSFORMS)

def validate(problem: str, losning: str) -> dict:
    try:
        x = sp.Symbol("x", real=True); y = sp.Function("y")
        local = {"x": x, "y": y}
        if "=" in problem:
            left, right = problem.split("=", 1); equation = sp.Eq(_parse(left, local), _parse(right, local))
        else: equation = sp.Eq(_parse(problem, local), 0)
        if "=" not in losning: return {"validert": False, "detaljer": "Løsningen har ikke formen venstreside = høyreside og kan ikke valideres trygt."}
        left, right = losning.split("=", 1); solution = _parse(right, local)
        expression = equation.lhs - equation.rhs
        expression = expression.subs(y(x), solution)
        values = []
        for point in (-1, 0, 1):
            current = expression.subs(x, point)
            current = current.subs({symbol: 1 for symbol in current.free_symbols})
            values.append(float(sp.N(current)))
        valid = all(abs(value) < 1e-6 for value in values)
        return {"validert": valid, "detaljer": f"Testet numerisk i x={[-1, 0, 1]}; residualer={values}."}
    except Exception as exc:
        return {"validert": False, "detaljer": f"Ikke verifisert: validering kunne ikke utføres ({exc})."}
