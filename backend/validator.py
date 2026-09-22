"""Ærlig numerisk validering av enkle ligninger og ODE-er."""
from __future__ import annotations
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

def _parse(text, local=None):
    text = str(text).strip().replace("^", "**").replace("j", "I")
    if not text:
        raise ValueError("Uttrykket er tomt.")
    base = {"Eq": sp.Eq, "exp": sp.exp, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "sqrt": sp.sqrt, "I": sp.I, "pi": sp.pi}
    base.update(local or {})
    for name in ("x", "t", "a", "b", "c", "C1", "C2"): base.setdefault(name, sp.Symbol(name, real=True))
    base.setdefault("y", sp.Function("y"))
    try:
        return parse_expr(text, local_dict=base, transformations=_TRANSFORMS)
    except (SyntaxError, TypeError, ValueError) as exc:
        raise ValueError(f"Ugyldig matematisk syntaks: {text}") from exc


def _equation(text, local):
    text = str(text).strip()
    if "=" in text:
        left, right = text.split("=", 1)
        return sp.Eq(_parse(left, local), _parse(right, local))
    parsed = _parse(text, local)
    if isinstance(parsed, sp.Equality):
        return parsed
    return sp.Eq(parsed, 0)


def _solution(text, local):
    if str(text).count("=") != 1:
        raise ValueError("Løsningen må ha formatet venstreside = høyreside.")
    left, right = str(text).split("=", 1)
    return _parse(left, local), _parse(right, local)


def _unknown_symbols(expression, allowed):
    return sorted(
        symbol.name for symbol in expression.free_symbols if symbol.name not in allowed
    )


def _numeric_residuals(expression, x, allowed_symbols):
    expression = sp.simplify(expression)
    unknown = _unknown_symbols(expression, allowed_symbols | {x.name})
    if unknown:
        raise ValueError(f"Ukjente symbolske parametre kan ikke testes numerisk: {', '.join(unknown)}.")

    constants = {sp.Symbol(name, real=True): 1 for name in ("C1", "C2")}
    residuals = []
    points = []
    for point in (-2, -1, 0, 1, 2, 3, 4, 5):
        current = sp.simplify(expression.subs(constants).subs(x, point))
        if current in (sp.zoo, sp.nan, sp.oo, -sp.oo) or current.is_finite is False:
            continue
        value = current.evalf()
        if value.free_symbols:
            continue
        try:
            numeric = complex(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if not (abs(numeric.real) < float("inf") and abs(numeric.imag) < float("inf")):
            continue
        points.append(point)
        residuals.append(abs(numeric))
        if len(points) == 3:
            break
    if len(points) < 3:
        raise ValueError("Fant ikke tre reproduserbare testpunkter der uttrykket er definert.")
    return points, residuals

def validate(problem: str, losning: str) -> dict:
    try:
        x = sp.Symbol("x", real=True)
        y = sp.Function("y")
        local = {"x": x, "y": y}
        equation = _equation(problem, local)
        left, solution = _solution(losning, local)
        expression = equation.lhs - equation.rhs

        is_ode = expression.has(sp.Derivative) or expression.has(y(x))
        if is_ode:
            if left != y(x):
                return {"validert": False, "detaljer": "ODE-løsningen må ha formatet y(x) = uttrykk."}
            substituted = expression.subs(y(x), solution).doit()
            allowed = {"x", "C1", "C2"}
        else:
            if left != x:
                return {"validert": False, "detaljer": "Den algebraiske løsningen må ha formatet x = uttrykk."}
            substituted = expression.subs(x, solution)
            allowed = {"x"}

        points, residuals = _numeric_residuals(substituted, x, allowed)
        valid = all(residual < 1e-6 for residual in residuals)
        kind = "differensialligningen" if is_ode else "ligningen"
        return {"validert": valid, "detaljer": f"Testet {kind} i x={points}; residualer={residuals}."}
    except Exception as exc:
        return {"validert": False, "detaljer": f"Ikke verifisert: validering kunne ikke utføres ({exc})."}
