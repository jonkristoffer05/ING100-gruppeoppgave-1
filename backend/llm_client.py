"""LLM-klient med OpenAI-kompatibel tool-calling."""
from __future__ import annotations
import json, os
from dotenv import load_dotenv
from openai import OpenAI
from backend.formelsamling import FORMELSAMLING
from backend.tools import TOOL_DEFINITIONS, derive, integrate, solve_equation, solve_ode, matrix_op, complex_op

USE_TOOLS = True
_TOOL_MAP = {"derive": derive, "integrate": integrate, "solve_equation": solve_equation, "solve_ode": solve_ode, "matrix_op": matrix_op, "complex_op": complex_op}

def _formula_context():
    return "\n".join(f"{key}: {value['navn']} | {value['formel']} | {value['referanse']} | {value['bruk']}" for key, value in FORMELSAMLING.items())

def _formula_details(text):
    return [{"id": key, **FORMELSAMLING[key]} for key in FORMELSAMLING if key in (text or "")]

def solve_task(oppgave: str) -> dict:
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key: raise RuntimeError("API_KEY mangler i .env.")
    client = OpenAI(api_key=api_key, base_url=os.getenv("API_BASE_URL") or None)
    prompt = ("Du er en matematikklærer for ingeniørstudenter. Bruk SymPy-verktøyene til all symbolsk og numerisk beregning. "
              "Ikke påstå at et verktøy er brukt hvis det ikke faktisk ble kalt. For bevis og begrepsforklaringer skal du si at svaret ikke er verktøyverifisert. "
              "Forklar hvert steg på norsk, bruk formel-ID-er fra formelsamlingen og si tydelig fra ved usikkerhet.\n\nFormelsamling:\n" + _formula_context())
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": oppgave}]
    total_tokens = 0
    final = ""
    for _ in range(6):
        kwargs = {"model": os.getenv("MODEL_NAME", "gpt-4o-mini"), "messages": messages, "temperature": 0.2}
        if USE_TOOLS: kwargs.update(tools=TOOL_DEFINITIONS, tool_choice="auto")
        response = client.chat.completions.create(**kwargs)
        usage = getattr(response, "usage", None)
        total_tokens += int(getattr(usage, "total_tokens", 0) or 0)
        message = response.choices[0].message
        calls = getattr(message, "tool_calls", None)
        if not calls:
            final = message.content or ""
            break
        messages.append({"role": "assistant", "content": message.content, "tool_calls": [{"id": c.id, "type": c.type, "function": {"name": c.function.name, "arguments": c.function.arguments}} for c in calls]})
        for call in calls:
            try:
                args = json.loads(call.function.arguments or "{}")
                result = _TOOL_MAP[call.function.name](**args)
            except Exception as exc:
                result = {"resultat": f"Feil i verktøyet: {exc}", "latex": ""}
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    if not final: final = "Modellen returnerte ikke et ferdig svar."
    return {"svar": final, "steg": [final], "formler_brukt": _formula_details(final), "tokens_brukt": total_tokens, "estimert_kostnad": round(total_tokens * 0.0000005, 6)}
