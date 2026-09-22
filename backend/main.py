"""FastAPI-kobling for MatteHjelpen."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend import llm_client, validator

app = FastAPI(title="MatteHjelpen")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Oppgave(BaseModel):
    oppgave: str

@app.get("/")
async def index():
    return FileResponse("frontend/index.html")

@app.post("/solve")
async def solve(payload: Oppgave):
    base = {"svar": "", "steg": [], "formler_brukt": [], "validert": False, "tokens_brukt": 0, "estimert_kostnad": 0.0}
    problem = (payload.oppgave or "").strip()
    if not problem:
        base["svar"] = "Oppgaven er tom."
        return base
    try:
        result = llm_client.solve_task(problem)
        base.update({key: result.get(key, base[key]) for key in ("svar", "steg", "formler_brukt", "tokens_brukt", "estimert_kostnad")})
        validation = validator.validate(problem, str(base["svar"]))
        base["validert"] = bool(validation.get("validert", False))
        return base
    except Exception as exc:
        base["svar"] = f"Feil: {exc}"
        base["steg"] = ["Klarte ikke å fullføre oppgaven. Se feilmeldingen i svaret."]
        return base
