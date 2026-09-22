"""Deterministiske SymPy-verktøy. Modellen forklarer; SymPy regner."""
from __future__ import annotations
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

def _parse(text: str, extra=None):
    text = str(text).strip().replace("^", "**")
    if not text:
        raise ValueError("Uttrykket kan ikke være tomt.")
    text = text.replace("sin^-1", "asin").replace("cos^-1", "acos").replace("tan^-1", "atan").replace("j", "I")
    local = {"E": sp.E, "I": sp.I, "pi": sp.pi, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp, "sqrt": sp.sqrt, "log": sp.log, "asin": sp.asin, "acos": sp.acos, "atan": sp.atan}
    for name in ("x", "y", "t", "z", "a", "b", "c", "n", "C1", "C2"):
        local[name] = sp.Symbol(name, real=True)
    local["y"] = sp.Function("y")
    if extra:
        local.update(extra)
    return parse_expr(text, local_dict=local, transformations=_TRANSFORMS)

def _result(value):
    if isinstance(value, sp.MatrixBase):
        return {"resultat": str(value), "latex": sp.latex(value)}
    if isinstance(value, dict):
        value = list(value.keys())
    if isinstance(value, (list, tuple)):
        return {"resultat": str(list(value)), "latex": sp.latex(sp.Tuple(*value))}
    value = sp.simplify(value) if isinstance(value, sp.Expr) else value
    return {"resultat": str(value), "latex": sp.latex(value) if isinstance(value, sp.Basic) else str(value)}

def derive(uttrykk: str, variabel: str = "x") -> dict:
    var = sp.Symbol(variabel, real=True)
    return _result(sp.diff(_parse(uttrykk, {variabel: var}), var))

def integrate(uttrykk: str, variabel: str = "x") -> dict:
    var = sp.Symbol(variabel, real=True)
    return _result(sp.integrate(_parse(uttrykk, {variabel: var}), var))

def solve_equation(ligning: str, variabel: str = "x") -> dict:
    var = sp.Symbol(variabel, real=True)
    if "=" in ligning:
        left, right = ligning.split("=", 1)
        expression = _parse(left, {variabel: var}) - _parse(right, {variabel: var})
    else:
        expression = _parse(ligning, {variabel: var})
    return _result(sp.solve(expression, var))

def solve_ode(ligning: str) -> dict:
    x = sp.Symbol("x", real=True)
    y = sp.Function("y")
    local = {"x": x, "y": y}
    if "=" in ligning:
        left, right = ligning.split("=", 1)
        equation = sp.Eq(_parse(left, local), _parse(right, local))
    else:
        equation = sp.Eq(_parse(ligning, local), 0)
    return _result(sp.dsolve(equation, y(x)))

def matrix_op(operasjon: str, matrise: list) -> dict:
    matrix = sp.Matrix(matrise)
    operation = operasjon.lower().strip()
    if operation == "determinant": result = matrix.det()
    elif operation == "invers":
        if matrix.det() == 0: raise ValueError("Matrisen er singulær og har ingen invers.")
        result = matrix.inv()
    elif operation in ("eigenvalues", "egenverdier"): result = matrix.eigenvals()
    elif operation == "trace": result = matrix.trace()
    else: raise ValueError("Støttede matriseoperasjoner: determinant, invers, eigenvalues, trace.")
    return _result(result)

def complex_op(operasjon: str, tall: str) -> dict:
    operation = operasjon.lower().strip()
    value = _parse(tall)
    if operation == "polar":
        return {"resultat": f"r = {sp.Abs(value)}, theta = {sp.arg(value)}", "latex": rf"r={sp.latex(sp.Abs(value))},\;\theta={sp.latex(sp.arg(value))}"}
    if operation == "power": return _result(sp.expand(value ** 2))
    if operation == "root": return _result(sp.solve(sp.Symbol("z") ** 2 - value, sp.Symbol("z")))
    if operation == "euler": return _result(sp.exp(sp.I * sp.Symbol("theta", real=True)))
    raise ValueError("Støttede kompleksoperasjoner: polar, power, root, euler.")

TOOL_DEFINITIONS = []
for name, description, properties, required in [
    ("derive", "Deriver et uttrykk.", {"uttrykk": {"type": "string"}, "variabel": {"type": "string"}}, ["uttrykk"]),
    ("integrate", "Integrer et uttrykk.", {"uttrykk": {"type": "string"}, "variabel": {"type": "string"}}, ["uttrykk"]),
    ("solve_equation", "Løs en ligning.", {"ligning": {"type": "string"}, "variabel": {"type": "string"}}, ["ligning"]),
    ("solve_ode", "Løs en differensialligning.", {"ligning": {"type": "string"}}, ["ligning"]),
    ("matrix_op", "Utfør en matriseoperasjon.", {"operasjon": {"type": "string"}, "matrise": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}}, ["operasjon", "matrise"]),
    ("complex_op", "Utfør en kompleks tall-operasjon.", {"operasjon": {"type": "string"}, "tall": {"type": "string"}}, ["operasjon", "tall"]),
]:
    TOOL_DEFINITIONS.append({"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": properties, "required": required}}})
