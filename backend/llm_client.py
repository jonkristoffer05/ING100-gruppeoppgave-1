"""LLM-klient med OpenAI-kompatibel tool-calling."""
from __future__ import annotations
import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from backend.formelsamling import FORMELSAMLING
from backend.tools import TOOL_DEFINITIONS, calculate, derive, integrate, solve_equation, solve_ode, matrix_op, complex_op

USE_TOOLS = True
_TOOL_MAP = {"calculate": calculate, "derive": derive, "integrate": integrate, "solve_equation": solve_equation, "solve_ode": solve_ode, "matrix_op": matrix_op, "complex_op": complex_op}
_MAX_TOOL_ROUNDS = 8

def _formula_context():
    return "\n".join(f"{key}: {value['navn']} | {value['formel']} | {value['referanse']} | {value['bruk']}" for key, value in FORMELSAMLING.items())

def _empty_result(svar=""):
    return {"svar": str(svar), "steg": [], "formler_brukt": [], "tokens_brukt": 0, "estimert_kostnad": 0.0}


def _parse_final_json(content):
    text = str(content or "").strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    candidates = [fenced.group(1).strip()] if fenced else []
    candidates.append(text)
    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            try:
                start = candidate.index("{")
                parsed, _ = decoder.raw_decode(candidate[start:])
            except (ValueError, json.JSONDecodeError):
                continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _normalise_final(content):
    parsed = _parse_final_json(content)
    if parsed is None:
        text = str(content or "").strip()
        steps = [line.strip(" -*\t") for line in text.splitlines() if line.strip()]
        if not steps and text:
            steps = [text]
        steps.append("Svaret kunne ikke verktøyverifiseres fordi sluttresponsen ikke var gyldig JSON.")
        return text or "Modellen returnerte ingen lesbar sluttrespons.", steps, []

    svar = parsed.get("svar")
    steg = parsed.get("steg")
    formula_ids = parsed.get("formel_ider", [])
    if not isinstance(svar, str) or not isinstance(steg, list) or not all(isinstance(step, str) for step in steg):
        text = str(content or "").strip()
        return text or "Modellens JSON manglet gyldig svar eller steg.", [
            "Svaret kunne ikke verktøyverifiseres fordi JSON-feltene svar og steg hadde feil format."
        ], []
    if not isinstance(formula_ids, list):
        formula_ids = []
    return svar, [step for step in steg if step.strip()], [item for item in formula_ids if isinstance(item, str)]


def _formula_details(formula_ids, steps):
    details = []
    for index, formula_id in enumerate(formula_ids):
        if formula_id not in FORMELSAMLING:
            continue
        step_number = next((number for number, step in enumerate(steps, 1) if formula_id in step), min(index + 1, max(len(steps), 1)))
        formula = FORMELSAMLING[formula_id]
        details.append(f"{formula_id} – {formula['navn']} – {formula['referanse']} – brukt i steg {step_number}")
    return details


def _usage_counts(response):
    usage = getattr(response, "usage", None)
    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    if not prompt_tokens and not completion_tokens:
        return int(getattr(usage, "total_tokens", 0) or 0), 0
    return prompt_tokens, completion_tokens


def _estimated_cost(prompt_tokens, completion_tokens):
    try:
        input_price = float(os.getenv("INPUT_PRICE_PER_MILLION", "0") or 0)
        output_price = float(os.getenv("OUTPUT_PRICE_PER_MILLION", "0") or 0)
    except ValueError:
        input_price = output_price = 0.0
    return round((prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000, 6)

def solve_task(oppgave: str) -> dict:
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        return _empty_result("API-nøkkel mangler; oppgaven kunne ikke sendes til modellen.")
    try:
        client = OpenAI(api_key=api_key, base_url=os.getenv("API_BASE_URL") or None)
    except Exception as exc:
        return _empty_result(f"Modellklienten kunne ikke startes: {exc}")
    prompt = ("Du er en matematikklærer for ingeniørstudenter. Svar alltid på norsk og forklar med flere korte, pedagogiske steg. "
              "Bruk SymPy-verktøyene til all symbolsk og numerisk beregning, og bruk calculate-verktøyet alltid for vanlig tallregning som 7-5, brøker, potenser og andre numeriske uttrykk. "
              "Du skal ikke regne ut slik aritmetikk selv. "
              "Knytt hver brukt formel-ID til det konkrete steget der den brukes. Ikke påstå at et verktøy er brukt hvis det ikke faktisk ble kalt. "
              "For bevis, begrepsoppgaver eller tvetydig input skal du forklare tekstlig, men si tydelig at svaret ikke er verktøyverifisert. "
              "Den endelige responsen skal være gyldig JSON uten ekstra tekst, med nøyaktig feltene svar (string), steg (liste med strings) og formel_ider (liste med gyldige ID-strenger).\n\n"
              "Formelsamling:\n" + _formula_context())
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": oppgave}]
    prompt_tokens = 0
    completion_tokens = 0
    tool_log = []
    final = ""
    try:
        for _ in range(_MAX_TOOL_ROUNDS):
            kwargs = {"model": os.getenv("MODEL_NAME", "gpt-4o-mini"), "messages": messages, "temperature": 0.2}
            if USE_TOOLS:
                kwargs.update(tools=TOOL_DEFINITIONS, tool_choice="auto")
            response = client.chat.completions.create(**kwargs)
            prompt_count, completion_count = _usage_counts(response)
            prompt_tokens += prompt_count
            completion_tokens += completion_count
            message = response.choices[0].message
            calls = getattr(message, "tool_calls", None) or []
            if not calls:
                final = message.content or ""
                break
            serialised_calls = []
            for call in calls:
                serialised_calls.append({"id": call.id, "type": call.type, "function": {"name": call.function.name, "arguments": call.function.arguments}})
            messages.append({"role": "assistant", "content": message.content, "tool_calls": serialised_calls})
            for call in calls:
                name = call.function.name
                tool_log.append(name)
                try:
                    args = json.loads(call.function.arguments or "{}")
                    function = _TOOL_MAP.get(name)
                    if function is None:
                        raise ValueError(f"Ukjent verktøy: {name}")
                    result = function(**args)
                except Exception as exc:
                    result = {"resultat": f"Feil i verktøyet: {exc}", "latex": ""}
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)})
        if not final:
            final = "Modellen fullførte ikke en sluttrespons innen maksimalt antall verktøyrunder."
    except Exception as exc:
        final = f"Modellkallet kunne ikke fullføres: {exc}"

    svar, steps, formula_ids = _normalise_final(final)
    if not steps:
        steps = ["Modellen ga ingen pedagogiske steg."]
    if tool_log:
        steps.append("Faktiske verktøykall: " + ", ".join(tool_log) + ".")
    else:
        steps.append("Ingen verktøykall ble utført; svaret er ikke verktøyverifisert.")
    total_tokens = prompt_tokens + completion_tokens
    return {"svar": svar, "steg": steps, "formler_brukt": _formula_details(formula_ids, steps), "tokens_brukt": total_tokens, "estimert_kostnad": _estimated_cost(prompt_tokens, completion_tokens)}
