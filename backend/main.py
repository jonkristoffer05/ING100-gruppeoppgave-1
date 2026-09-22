"""FastAPI-kobling for MatteHjelpen."""
import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from backend import llm_client, validator

app = FastAPI(title="MatteHjelpen")
logger = logging.getLogger(__name__)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Oppgave(BaseModel):
    oppgave: str


def _base_response(message=""):
    return {"svar": message, "steg": [], "formler_brukt": [], "validert": False, "tokens_brukt": "ukjent", "estimert_kostnad": "ukjent"}


@app.exception_handler(RequestValidationError)
async def invalid_request(_request, _exc):
    return JSONResponse(status_code=400, content=_base_response("Forespørselen må inneholde en gyldig matteoppgave."))

@app.get("/")
async def index():
    return FileResponse("frontend/index.html")

@app.post("/solve")
async def solve(payload: Oppgave):
    base = _base_response()
    problem = (payload.oppgave or "").strip()
    if not problem:
        base["svar"] = "Oppgaven er tom."
        return JSONResponse(status_code=400, content=base)
    try:
        result = llm_client.solve_task(problem)
        base.update({key: result.get(key, base[key]) for key in ("svar", "steg", "formler_brukt", "tokens_brukt", "estimert_kostnad")})
        if any("ugyldig JSON" in str(step) or "manglet gyldig" in str(step) for step in base["steg"]):
            base["svar"] = "Modelltjenesten returnerte et ugyldig svar. Prøv igjen senere."
            base["validert"] = False
            return JSONResponse(status_code=502, content=base)
        try:
            validation = validator.validate(problem, str(base["svar"]))
            base["validert"] = bool(validation.get("validert", False))
            if not base["validert"] and validation.get("detaljer"):
                base["steg"].append(f"Validering: {validation['detaljer']}")
        except Exception as exc:
            logger.error("Validatoren feilet: %s", type(exc).__name__)
            base["validert"] = False
            base["steg"].append("Validering kunne ikke utføres; svaret er ikke verktøyverifisert.")
        return base
    except llm_client.ModelAPIError as exc:
        logger.warning("Modell-API feilet: %s", type(exc).__name__)
        base["svar"] = "Modelltjenesten er midlertidig utilgjengelig. Prøv igjen senere."
        base["steg"] = ["Oppgaven kunne ikke behandles av modelltjenesten."]
        return JSONResponse(status_code=exc.status_code, content=base)
    except Exception as exc:
        logger.error("Uventet feil i solve-endepunktet: %s", type(exc).__name__)
        base["svar"] = "En uventet intern feil oppstod. Prøv igjen senere."
        base["steg"] = ["Oppgaven kunne ikke fullføres."]
        return JSONResponse(status_code=500, content=base)
