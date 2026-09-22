"""Deterministiske SymPy-verktøy. Modellen forklarer; SymPy regner."""
from __future__ import annotations
from tokenize import TokenError
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

def _parse(text: str, extra=None):
    text = str(text).strip().replace("^", "**")
    if not text:
        raise ValueError("Uttrykket kan ikke være tomt.")
    # Gruppens faste tolkning: sin^-1, cos^-1 og tan^-1 betyr inverse funksjoner.
    text = text.replace("sin^-1", "asin").replace("cos^-1", "acos").replace("tan^-1", "atan").replace("j", "I")
    local = {"E": sp.E, "I": sp.I, "pi": sp.pi, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp, "sqrt": sp.sqrt, "log": sp.log, "asin": sp.asin, "acos": sp.acos, "atan": sp.atan}
    for name in ("x", "y", "t", "z", "a", "b", "c", "n", "theta", "C1", "C2"):
        local[name] = sp.Symbol(name, real=True)
    local["y"] = sp.Function("y")
    if extra:
        local.update(extra)
    try:
        return parse_expr(text, local_dict=local, transformations=_TRANSFORMS)
    except (SyntaxError, TokenError, TypeError, ValueError) as exc:
        raise ValueError(f"Ugyldig matematisk uttrykk: {text}") from exc

def _result(value):
    if hasattr(value, "has") and value.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        raise ValueError("Resultatet er ikke definert.")
    if isinstance(value, sp.MatrixBase):
        return {"resultat": str(value), "latex": sp.latex(value)}
    if isinstance(value, dict):
        value = list(value.keys())
    if isinstance(value, (list, tuple)):
        return {"resultat": str(list(value)), "latex": sp.latex(sp.Tuple(*value))}
    value = sp.simplify(value) if isinstance(value, sp.Expr) else value
    return {"resultat": str(value), "latex": sp.latex(value) if isinstance(value, sp.Basic) else str(value)}

def calculate(uttrykk: str) -> dict:
    """Forenkle og beregn et vanlig matematisk uttrykk med SymPy."""
    return _result(sp.simplify(_parse(uttrykk)))

def derive(uttrykk: str, variabel: str = "x") -> dict:
    """Deriverer uttrykket med hensyn på variabelen."""
    var = sp.Symbol(variabel, real=True)
    return _result(sp.diff(_parse(uttrykk, {variabel: var}), var))

def integrate(uttrykk: str, variabel: str = "x") -> dict:
    """Integrerer uttrykket med hensyn på variabelen."""
    var = sp.Symbol(variabel, real=True)
    return _result(sp.integrate(_parse(uttrykk, {variabel: var}), var))

def solve_equation(ligning: str, variabel: str = "x") -> dict:
    """Løser en algebraisk ligning for den valgte variabelen."""
    var = sp.Symbol(variabel, real=True)
    if "=" in ligning:
        left, right = ligning.split("=", 1)
        expression = _parse(left, {variabel: var}) - _parse(right, {variabel: var})
    else:
        expression = _parse(ligning, {variabel: var})
    return _result(sp.solve(expression, var))

def solve_ode(ligning: str) -> dict:
    """Løser en differensialligning med SymPy."""
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
    """Utfører en støttet operasjon på en matrise."""
    operation = str(operasjon).lower().strip()
    if operation not in ("determinant", "invers", "eigenvalues", "egenverdier", "solve_ax_b"):
        raise ValueError("Støttede matriseoperasjoner: determinant, invers, egenverdier, solve_ax_b.")
    try:
        if operation == "solve_ax_b":
            if not isinstance(matrise, (list, tuple)) or len(matrise) != 2:
                raise ValueError("solve_ax_b krever matrise på formen [A, b].")
            matrix = sp.Matrix(matrise[0])
            vector = sp.Matrix(matrise[1])
            if matrix.rows != matrix.cols:
                raise ValueError("A i solve_ax_b må være en kvadratisk matrise.")
            if vector.cols != 1 or vector.rows != matrix.rows:
                raise ValueError("b i solve_ax_b må være en vektor med samme antall rader som A.")
            if matrix.det() == 0:
                raise ValueError("A er singulær, så Ax=b har ingen entydig løsning.")
            result = matrix.LUsolve(vector)
        else:
            matrix = sp.Matrix(matrise)
            if matrix.rows != matrix.cols:
                raise ValueError("Matriseoperasjonen krever en kvadratisk matrise.")
            if operation == "determinant":
                result = matrix.det()
            elif operation == "invers":
                if matrix.det() == 0:
                    raise ValueError("Matrisen er singulær og har ingen invers.")
                result = matrix.inv()
            else:
                result = list(matrix.eigenvals().keys())
    except ValueError:
        raise
    except (TypeError, IndexError, sp.ShapeError) as exc:
        raise ValueError("Ugyldig matriseformat. Bruk en rektangulær matrise med tall eller uttrykk.") from exc
    return _result(result)

def complex_op(operasjon: str, tall: str) -> dict:
    """Utfører en operasjon på et komplekst tall eller uttrykk."""
    operation = str(operasjon).lower().strip()
    if operation not in ("polar", "power", "root", "euler"):
        raise ValueError("Støttede kompleksoperasjoner: polar, power, root, euler.")
    if operation == "polar":
        value = _parse(tall)
        if value == 0:
            raise ValueError("Argumentet til 0 er ikke definert i polarform.")
        return {"resultat": f"r = {sp.Abs(value)}, theta = {sp.arg(value)}", "latex": rf"r={sp.latex(sp.Abs(value))},\;\theta={sp.latex(sp.arg(value))}"}
    if operation == "power":
        return _result(sp.expand_complex(_parse(tall)))
    if operation == "root":
        parts = [part.strip() for part in str(tall).split(";")]
        if len(parts) > 2 or not parts[0]:
            raise ValueError("root krever 'tall' eller 'tall;grad', for eksempel '1;3'.")
        value = _parse(parts[0])
        degree = 2
        if len(parts) == 2:
            try:
                degree = int(parts[1])
            except ValueError as exc:
                raise ValueError("Graden i root må være et positivt heltall.") from exc
        if degree < 1:
            raise ValueError("Graden i root må være et positivt heltall.")
        variable = sp.Symbol("z")
        try:
            roots = sp.solve(variable ** degree - value, variable)
        except (NotImplementedError, ValueError, TypeError) as exc:
            raise ValueError("Klarte ikke å beregne de komplekse røttene.") from exc
        return _result(roots)
    return _result(sp.expand_complex(sp.exp(sp.I * _parse(tall))))

TOOL_DEFINITIONS = []
for name, description, properties, required in [
    ("calculate", "Beregn vanlig aritmetikk som 7-5, brøker, potenser og andre numeriske uttrykk.", {"uttrykk": {"type": "string"}}, ["uttrykk"]),
    ("derive", "Deriver et uttrykk.", {"uttrykk": {"type": "string"}, "variabel": {"type": "string"}}, ["uttrykk"]),
    ("integrate", "Integrer et uttrykk.", {"uttrykk": {"type": "string"}, "variabel": {"type": "string"}}, ["uttrykk"]),
    ("solve_equation", "Løs en ligning.", {"ligning": {"type": "string"}, "variabel": {"type": "string"}}, ["ligning"]),
    ("solve_ode", "Løs en differensialligning.", {"ligning": {"type": "string"}}, ["ligning"]),
    ("matrix_op", "Støtter determinant, invers, egenverdier og solve_ax_b. For solve_ax_b skal matrise være [A, b], for eksempel [[[2, 1], [1, -1]], [5, 1]], for å løse Ax=b.", {"operasjon": {"type": "string", "enum": ["determinant", "invers", "egenverdier", "solve_ax_b"]}, "matrise": {"oneOf": [{"type": "array", "items": {"type": "array", "items": {"type": "number"}}}, {"type": "array", "prefixItems": [{"type": "array", "items": {"type": "array", "items": {"type": "number"}}}, {"type": "array", "items": {"type": "number"}}], "minItems": 2, "maxItems": 2}]}}, ["operasjon", "matrise"]),
    ("complex_op", "Støtter polar, power, root og euler. tall er et komplekst uttrykk; power forenkler hele uttrykket, root bruker 'tall;grad' eller grad 2 som standard, og euler tolker tall som vinkelen theta i e^(i*theta).", {"operasjon": {"type": "string", "enum": ["polar", "power", "root", "euler"]}, "tall": {"type": "string"}}, ["operasjon", "tall"]),
]:
    TOOL_DEFINITIONS.append({"type": "function", "function": {"name": name, "description": description, "parameters": {"type": "object", "properties": properties, "required": required}}})
