"""Ærlig numerisk validering av enkle ligninger og ODE-er."""
from __future__ import annotations
import re
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)
_NUMERIC_TOLERANCE = 1e-5


def _normalise_text(text):
    text = str(text).strip().replace("^", "**").replace("j", "I")
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    variables = "xyz tabc n".replace(" ", "")
    pairs = [first + second for first in variables for second in variables if first != second]
    pair_pattern = r"(?<![A-Za-z_])(" + "|".join(sorted(pairs, key=len, reverse=True)) + r")(?![A-Za-z_(])"
    return re.sub(pair_pattern, lambda match: "*".join(match.group(1)), text)

def _parse(text, local=None):
    text = _normalise_text(text)
    if not text:
        raise ValueError("Uttrykket er tomt.")
    base = {"Eq": sp.Eq, "exp": sp.exp, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "sqrt": sp.sqrt, "I": sp.I, "pi": sp.pi}
    base.update(local or {})
    for name in ("x", "t", "a", "b", "c", "C1", "C2"): base.setdefault(name, sp.Symbol(name, real=True))
    if "y(" not in text and ".diff" not in text and "Derivative" not in text:
        base["y"] = sp.Symbol("y", real=True)
    else:
        base.setdefault("y", sp.Function("y"))
    try:
        parsed = parse_expr(text, local_dict=base, transformations=_TRANSFORMS)
        return sp.nsimplify(parsed, rational=True)
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


def _is_plain_expression(parsed):
    return not isinstance(parsed, sp.Equality) and not parsed.has(sp.Derivative)


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
        parsed_problem = _parse(problem, local) if "=" not in str(problem) else None
        if parsed_problem is not None and _is_plain_expression(parsed_problem) and "=" not in str(losning):
            answer = _parse(losning, local)
            points, residuals = _numeric_residuals(parsed_problem - answer, x, {"x"})
            valid = all(residual <= _NUMERIC_TOLERANCE for residual in residuals)
            return {"validert": valid, "detaljer": f"Testet uttrykket i x={points}; residualer={residuals}."}
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
        valid = all(residual <= _NUMERIC_TOLERANCE for residual in residuals)
        kind = "differensialligningen" if is_ode else "ligningen"
        return {"validert": valid, "detaljer": f"Testet {kind} i x={points}; residualer={residuals}."}
    except Exception as exc:
        return {"validert": False, "detaljer": f"Ikke verifisert: validering kunne ikke utføres ({exc})."}
