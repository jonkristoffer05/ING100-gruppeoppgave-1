"""Symbolsk validering av vanlige matteoppgaver med SymPy."""
from __future__ import annotations

import re

import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)
_NUMERIC_TOLERANCE = 1e-6
_FUNCTIONS = {
    "E": sp.E, "I": sp.I, "pi": sp.pi, "exp": sp.exp, "sin": sp.sin,
    "cos": sp.cos, "tan": sp.tan, "log": sp.log, "sqrt": sp.sqrt,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
}


def _normalise_text(text: str) -> str:
    value = str(text).strip().replace("^", "**").replace("j", "I")
    value = re.sub(r"(?<![A-Za-z_])i(?![A-Za-z_])", "I", value)
    value = re.sub(r"(?<=\d),(?=\d)", ".", value)
    return value.replace("−", "-").replace("×", "*")


def _locals(text: str, extra=None):
    names = set(re.findall(r"\b[A-Za-z_]\w*\b", text))
    local = dict(_FUNCTIONS)
    for name in names:
        if name not in local and name != "C":
            local.setdefault(name, sp.Symbol(name, real=True))
    local.setdefault("C", sp.Symbol("C", real=True))
    local.update(extra or {})
    return local


def _parse(text: str, local=None):
    value = _normalise_text(text)
    if not value:
        raise ValueError("Uttrykket er tomt.")
    namespace = _locals(value, local)
    namespace.setdefault("y", sp.Function("y"))
    try:
        parsed = parse_expr(value, local_dict=namespace, transformations=_TRANSFORMS)
        return sp.nsimplify(parsed, rational=True)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"Ugyldig matematisk format i «{value}». Sjekk parenteser og operatorer.") from exc


def _task_kind(text: str) -> str:
    lower = _normalise_text(text).lower()
    if re.search(r"\b(bevis|forklar|vis at|begrunn)\b", lower):
        return "unsupported"
    if re.search(r"\b(løs|los)\s+(?:lignings)?system(?:et)?\b", lower) or "ligningssystem" in lower:
        return "system"
    if re.search(r"\b(løs|los)\s+ode\b|\bdifferensial", lower):
        return "ode"
    if "a*x=b" in lower or "matrise" in lower or re.search(r"\bmatrix\b", lower):
        return "matrix"
    if re.search(r"\b(deriver|deriverte)\b", lower):
        return "derivative"
    if re.search(r"\b(integrer|integralet)\b", lower):
        return "integral"
    if re.search(r"\b(løs|los|finn x når)\b", lower):
        return "equation"
    if re.search(r"\b(beregn|regn ut|forenkle)\b", lower):
        return "calculation"
    if re.search(r"\bpolarform\b|eulers formel", lower) and ("i" in lower or "j" in lower):
        return "complex"
    return "legacy"


def _strip_command(text: str, kind: str) -> str:
    value = _normalise_text(text).strip().rstrip(" .")
    patterns = {
        "derivative": r"^(?:deriver|finn den deriverte av)\s+",
        "integral": r"^(?:integrer|finn integralet av)\s+",
        "calculation": r"^(?:beregn|regn\s+ut|forenkle)\s+",
        "equation": r"^(?:løs|los)(?:\s+ligningen)?\s+",
        "system": r"^(?:løs|los)\s+(?:lignings)?systemet?\s*:?\s*",
        "ode": r"^(?:løs|los)\s+ode\s+",
    }
    return re.sub(patterns.get(kind, r"^$"), "", value, flags=re.I).strip().rstrip(" .")


def _extract_math(text: str, kind: str) -> str:
    value = _strip_command(text, kind)
    if kind == "derivative":
        value = re.sub(r"^f\s*\([^)]*\)\s*=\s*", "", value, flags=re.I)
    return value


def _extract_answer(text: str, kind: str) -> str:
    value = str(text).strip()
    value = re.sub(r"^(?:svar|resultat|den deriverte er|integralet er)\s*:?\s*", "", value, flags=re.I)
    if kind == "derivative":
        value = re.sub(r"^(?:f['′]\s*\([^)]*\)|f\s*\([^)]*\))\s*=\s*", "", value, flags=re.I)
    elif kind == "integral":
        value = re.sub(r"^[A-Za-z_]\w*\s*\([^)]*\)\s*=\s*", "", value)
    return value.strip().rstrip(" .")


def _equal(left, right) -> bool:
    try:
        return sp.simplify(left - right) == 0
    except (TypeError, ValueError):
        return False


def _split_top_level(text: str, separators=",;\n"):
    parts, current, depth = [], [], 0
    for char in text:
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        if depth == 0 and char in separators:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


def _equation_parts(text: str, local):
    if "=" not in text:
        raise ValueError("Ligningen må inneholde et likhetstegn.")
    left, right = text.split("=", 1)
    return _parse(left, local), _parse(right, local)


def _parse_solution_values(text: str, variables, local):
    value = _extract_answer(text, "equation").strip().strip("{}[]()")
    assignments = re.findall(r"([A-Za-z_]\w*)\s*=\s*([^,;]+)", value)
    if assignments:
        found = {name: _parse(expression, local) for name, expression in assignments}
        if not all(variable.name in found for variable in variables):
            raise ValueError("Svaret mangler verdi for minst én variabel.")
        return [found[variable.name] for variable in variables]
    values = [part.strip() for part in re.split(r"\s*(?:,|;|eller|og)\s*", value, flags=re.I) if part.strip()]
    if len(variables) == 1:
        candidate = re.sub(r"^[A-Za-z_]\w*\s*(?:∈|in)\s*", "", value)
        candidates = candidate.strip("{}[]()")
        return [_parse(part, local) for part in re.split(r"\s*,\s*", candidates) if part.strip()]
    if len(values) != len(variables):
        raise ValueError("Svaret må oppgi alle variabelverdiene.")
    return [_parse(item, local) for item in values]


def _validate_equation(problem: str, answer: str, local):
    parts = _split_top_level(problem)
    if len(parts) == 1 and re.search(r"\s+og\s+", problem, re.I):
        parts = re.split(r"\s+og\s+", problem, flags=re.I)
    equations = [_equation_parts(part.strip(), local) for part in parts]
    variables = sorted(set().union(*(left.free_symbols | right.free_symbols for left, right in equations)), key=lambda item: item.name)
    variables = [variable for variable in variables if variable.name not in {"C", "I", "pi"}]
    if not variables:
        raise ValueError("Fant ingen løsningsvariabel i ligningen.")
    values = _parse_solution_values(answer, variables, local)
    substitutions = dict(zip(variables, values))
    for left, right in equations:
        if not _equal((left - right).subs(substitutions), 0):
            return {"validert": False, "detaljer": "Svaret ble kontrollert, men minst én oppgitt løsning oppfyller ikke ligningen."}
    if len(equations) == 1 and len(variables) == 1:
        expected = sp.solve(equations[0][0] - equations[0][1], variables[0])
        if len(values) != len(expected) or any(not any(_equal(value, candidate) for candidate in expected) for value in values):
            return {"validert": False, "detaljer": "Svaret ble kontrollert, men mangler løsninger eller inneholder feil løsninger."}
    return {"validert": True, "detaljer": "Alle oppgitte løsninger ble satt inn i ligningen(e) og oppfylte dem."}


def _validate_ode(problem: str, answer: str):
    x = sp.Symbol("x", real=True)
    y = sp.Function("y")
    local = {"x": x, "y": y, "Derivative": sp.Derivative, "Eq": sp.Eq}

    expression = _strip_ode_command(problem)
    expression = _normalise_ode_expression(expression)
    left, right = _equation_parts(expression, local)
    proposed = _parse_ode_answer(answer, local, y, x)
    residual = sp.simplify((left - right).subs(y(x), proposed).doit())
    if residual == 0:
        return {"validert": True, "detaljer": "ODE-løsningen ble satt inn; residual = 0."}
    if _numeric_residual_is_small(residual, x):
        return {"validert": True, "detaljer": f"ODE-løsningen ble satt inn; residual = {residual} (under toleransen {_NUMERIC_TOLERANCE})."}
    return {"validert": False, "detaljer": f"ODE-løsningen ble kontrollert, men residual = {residual}."}


def _strip_ode_command(text: str) -> str:
    value = _normalise_text(text).strip().rstrip(" .")
    command = (
        r"^(?:finn\s+løsningen\s+av\s+differensialligningen|"
        r"løs\s+differensialligningen|løs\s+ode)\s*:?[\s]*"
    )
    stripped = re.sub(command, "", value, flags=re.I)
    if stripped == value:
        raise ValueError("ODE-oppgaven må starte med «Løs ODE», «Løs differensialligningen» eller «Finn løsningen av differensialligningen».")
    return stripped.strip().rstrip(" .")


def _normalise_ode_expression(text: str) -> str:
    value = _normalise_text(text)
    for order in (3, 2, 1):
        apostrophes = "'" * order
        pattern = rf"\by\s*{re.escape(apostrophes)}\s*(?:\(\s*x\s*\))?"
        replacement = "Derivative(y(x), x)" if order == 1 else f"Derivative(y(x), (x, {order}))"
        value = re.sub(pattern, replacement, value)
    value = re.sub(r"\by\s*\(\s*x\s*\)", "y(x)", value)
    return re.sub(r"\by(?!\s*\()", "y(x)", value)


def _parse_ode_answer(answer: str, local, y, x):
    value = str(answer).strip().rstrip(" .")
    try:
        parsed = _parse(_normalise_ode_expression(value), local)
    except ValueError:
        parsed = None
    if isinstance(parsed, sp.Equality):
        if parsed.lhs == y(x):
            return parsed.rhs
        raise ValueError("ODE-svaret i Eq-format må ha y(x) på venstre side.")
    if "=" in value:
        name, expression = value.split("=", 1)
        if not re.fullmatch(r"y(?:\s*\(\s*x\s*\))?", name.strip(), re.I):
            raise ValueError("ODE-svaret må ha formatet y(x) = uttrykk eller y = uttrykk.")
        return _parse(_normalise_ode_expression(expression), local)
    if parsed is None:
        raise ValueError("ODE-svaret kunne ikke parses som y(x) = uttrykk, Eq(y(x), uttrykk) eller et uttrykk.")
    return parsed


def _numeric_residual_is_small(residual, x) -> bool:
    symbols = residual.free_symbols - {x}
    substitutions = {symbol: 1 for symbol in symbols}
    for point in (-1, 0, 1):
        value = sp.N(residual.subs(substitutions).subs(x, point))
        if value.free_symbols:
            return False
        try:
            if abs(complex(value)) > _NUMERIC_TOLERANCE:
                return False
        except (TypeError, ValueError, OverflowError):
            return False
    return True


def _validate_complex(problem: str, answer: str):
    match = re.search(r"(?:skriv|konverter)\s+(.+)\s+polarform", problem, re.I)
    expression_text = match.group(1) if match else problem
    expression_text = re.sub(r"\s+i\s*$", "", expression_text, flags=re.I)
    expression = _parse(expression_text)
    proposed = _parse_polar_answer(answer)
    if _equal(sp.re(proposed), sp.re(expression)) and _equal(sp.im(proposed), sp.im(expression)):
        return {"validert": True, "detaljer": "Polarformen ble kontrollert ved å konvertere tilbake til reell og imaginær del."}
    try:
        difference = complex((expression - proposed).evalf())
        if abs(difference) <= _NUMERIC_TOLERANCE:
            return {"validert": True, "detaljer": "Polarformen ble kontrollert ved å konvertere tilbake til reell og imaginær del."}
    except (TypeError, ValueError, OverflowError):
        pass
    return {"validert": False, "detaljer": "Polarformen tilsvarer ikke det opprinnelige komplekse tallet."}


def _normalise_polar_text(text: str) -> str:
    """Begrenset normalisering for de polarformene modellen vanligvis bruker."""
    value = str(text).strip()
    value = value.replace("\\left", "").replace("\\right", "")
    value = value.replace("\\,", "").replace("\\;", "")
    value = re.sub(r"\\(cos|sin)\s*\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1((\2)/(\3))", value)
    value = value.replace("\\sqrt", "sqrt").replace("\\pi", "pi")
    value = value.replace("\\cos", "cos").replace("\\sin", "sin")
    value = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", value)
    value = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", value)
    value = re.sub(r"sqrt\{([^{}]+)\}", r"sqrt(\1)", value)
    value = re.sub(r"e\s*\^\s*\{([^{}]+)\}", r"exp(\1)", value)
    value = value.replace("^", "**")
    value = re.sub(r"\be\s*\*\*\s*\(([^()]*)\)", r"exp(\1)", value)
    value = value.replace("θ", "theta")
    value = re.sub(r"(?<![A-Za-z_])i(?=(?:sin|cos)\()", "I*", value)
    value = re.sub(r"(?<![A-Za-z_])i(?![A-Za-z_])", "I", value)
    return value


def _polar_segments(text: str):
    return [part.strip() for part in re.split(r"\s*=\s*", text) if part.strip()]


def _parse_polar_answer(answer: str):
    text = _normalise_polar_text(answer)
    radius = re.search(r"\br\s*=\s*(.*?)(?=\s*,\s*|\s*;\s*)", text, re.I)
    angle = re.search(r"\btheta\s*=\s*(.+)$", text, re.I)
    if radius and angle:
        return _parse(radius.group(1)) * sp.exp(sp.I * _parse(angle.group(1)))

    candidates = [text]
    candidates.extend(_polar_segments(text)[1:])
    for candidate in candidates:
        if "exp(" not in candidate and "cos(" not in candidate:
            continue
        try:
            return _parse(candidate)
        except ValueError:
            continue
    raise ValueError("Polarformen kunne ikke tolkes. Bruk for eksempel r=sqrt(2), theta=pi/4.")


def _matrix_literal(text: str):
    raw = text.strip()
    if raw.startswith("[[") and raw.endswith("]]" ):
        rows = _split_top_level(raw[1:-1], separators=",")
        matrix_rows = [[_parse(cell) for cell in _split_top_level(row.strip().strip("[]"), separators=",")] for row in rows]
    else:
        matrix_rows = [[_parse(cell) for cell in _split_top_level(raw.strip("[]"), separators=",")]]
    if not matrix_rows or not matrix_rows[0] or any(len(row) != len(matrix_rows[0]) for row in matrix_rows):
        raise ValueError("Matrisen må være rektangulær.")
    return sp.Matrix(matrix_rows)


def _validate_matrix(problem: str, answer: str):
    matrix_match = re.search(r"\bA\s*=\s*(\[\[.*?\]\])", problem, re.I | re.S)
    vector_match = re.search(r"\bb\s*=\s*(\[[^\]]*\])", problem, re.I | re.S)
    answer_match = re.search(r"(?:x\s*=\s*)?(\[[^\]]*\])", str(answer), re.I | re.S)
    if not matrix_match or not vector_match or not answer_match:
        raise ValueError("Matriseoppgaven må oppgi A, b og løsningsvektoren i tydelig listeformat.")
    matrix = _matrix_literal(matrix_match.group(1))
    vector = _matrix_literal(vector_match.group(1))
    proposed = _matrix_literal(answer_match.group(1))
    if vector.rows == 1:
        vector = vector.T
    if proposed.rows == 1:
        proposed = proposed.T
    if vector.cols != 1 or proposed.cols != 1:
        raise ValueError("b og løsningsvektoren må være kolonnevektorer.")
    if matrix.rows != matrix.cols or vector.rows != matrix.rows or proposed.rows != matrix.cols:
        raise ValueError("Matrise og vektorer har dimensjoner som ikke passer sammen.")
    if all(_equal(left, right) for left, right in zip(matrix * proposed, vector)):
        return {"validert": True, "detaljer": "Løsningsvektoren ble satt inn i A*x og ga b."}
    return {"validert": False, "detaljer": "Løsningsvektoren ble kontrollert i A*x, men ga ikke b."}


def validate(problem: str, losning: str) -> dict:
    try:
        kind = _task_kind(problem)
        if kind == "unsupported":
            return {"validert": False, "detaljer": "Denne oppgaven krever manuell vurdering av beviset og kan ikke verifiseres automatisk av den symbolske validatoren."}
        if kind == "complex":
            return _validate_complex(problem, losning)
        if kind == "matrix":
            return _validate_matrix(problem, losning)
        if kind == "ode":
            return _validate_ode(problem, losning)
        if kind in {"equation", "system"}:
            math_problem = _extract_math(problem, kind)
            return _validate_equation(math_problem, losning, _locals(math_problem))
        math_problem = _extract_math(problem, kind)
        local = _locals(math_problem)
        expected = _parse(math_problem, local)
        answer = _parse(_extract_answer(losning, kind), local)
        if kind == "derivative":
            variable = next(iter(sorted(expected.free_symbols, key=lambda item: item.name)), local.get("x", sp.Symbol("x", real=True)))
            checked = _equal(sp.diff(expected, variable), answer)
        elif kind == "integral":
            variable = next(iter(sorted(expected.free_symbols, key=lambda item: item.name)), local.get("x", sp.Symbol("x", real=True)))
            checked = _equal(sp.diff(answer, variable), expected)
        else:
            checked = _equal(expected, answer)
            if not checked:
                try:
                    checked = abs(complex((expected - answer).evalf())) <= _NUMERIC_TOLERANCE
                except (TypeError, ValueError):
                    checked = False
        if checked:
            return {"validert": True, "detaljer": "Svaret ble matematisk kontrollert med SymPy og er ekvivalent med forventet uttrykk."}
        return {"validert": False, "detaljer": "Svaret ble matematisk kontrollert, men stemmer ikke med oppgaven."}
    except Exception as exc:
        return {"validert": False, "detaljer": f"Valideringen kunne ikke gjennomføres fordi oppgaven eller svaret har ugyldig format: {exc}"}
