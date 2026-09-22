# Prompt: `backend/tools.py` – deterministiske SymPy-verktøy

**Fil:** `backend/tools.py`
**Prinsipp:** Modellen skal ALDRI late som den har beregnet noe et verktøy
kunne gjort. All BEREGNING (derivasjon, ligninger, matriser, komplekse tall)
skjer her, med SymPy – bevis og begrepsforklaringer er en annen kategori
(se `PROMPTS/03_llm_client.md`).

## Krav (fast – ikke forhandlingsbart)

Implementer disse funksjonene med SymPy, med **akkurat** disse navnene og
parameterne (llm_client og resten av appen forventer disse signaturene):

- `derive(uttrykk: str, variabel: str = "x") -> dict`
- `calculate(uttrykk: str) -> dict`
- `integrate(uttrykk: str, variabel: str = "x") -> dict`
- `solve_equation(ligning: str, variabel: str = "x") -> dict`
- `solve_ode(ligning: str) -> dict`
- `matrix_op(operasjon: str, matrise: list) -> dict`
- `complex_op(operasjon: str, tall: str) -> dict`

Hver funksjon returnerer `{"resultat": str, "latex": str}` ved suksess.

Definer også `TOOL_DEFINITIONS`: en liste med JSON-schema (OpenAI
function-calling-format) som beskriver disse 7 verktøyene, til bruk i
`llm_client.py`.

## Hva disse verktøyene ikke dekker

De 7 funksjonene dekker konkrete beregninger. De dekker IKKE bevisoppgaver
(f.eks. «bevis Pythagoras' læresetning») eller begrepsforklaringer – det er
like fullt legitime matteoppgaver, bare ikke noe SymPy kan «regne ut». Dere
står fritt til å utvide `tools.py` med flere funksjoner senere (f.eks.
grenseverdier, serieutvikling) – hold da samme mønster:
`{"resultat": str, "latex": str}`, og oppdater `TOOL_DEFINITIONS` tilsvarende.

## Gruppens valg

- Hvilke feilsituasjoner skal funksjonene håndtere eksplisitt? (F.eks. ugyldig
  syntaks, deling på null, matrise med feil dimensjoner.) Skriv egen liste:
  Tom input, ugyldig SymPy-syntaks, ukjente operasjoner, ugyldige variabler,
  deling på null, matriser med feil dimensjoner, singulære matriser og
  ugyldige komplekse uttrykk skal håndteres eksplisitt. Det inkluderer også
  tomme uttrykk og ugyldige parameterverdier for komplekse tall.

- Skal feil kastes som exceptions, eller returneres som del av dict
  (f.eks. `{"feil": "..."}`)? Vi bruker exceptions ved feil. Funksjonene kaster ValueError med en norsk forklaring. Dette gjør at llm_client.py og main.py kan fange feilen og vise den ærlig til brukeren.

- Hvor «smart» skal parsing av matteuttrykk være? (F.eks.: skal `sin^-1(x)`
  tolkes som invers funksjon eller som potens? Dette er et av
  «aha-punktene» i `OPPGAVE.md` – bestem en tolkning og vær eksplisitt om
  den i koden/docstringen.) Parseren støtter blant annet `+`, `-`, `*`, `/`,
  potenser med `^`, implisitt multiplikasjon som `3.5x` og `2(x+1)`, `sin`,
  `cos`, `tan`, `exp`, `sqrt`, `log`, komplekse tall og vanlige symboler.
  Parseren bruker aldri `eval`. Vi tolker `sin^-1(x)` som `asin(x)`,
  `cos^-1(x)` som `acos(x)` og `tan^-1(x)` som `atan(x)`. Denne tolkningen
  er gjort eksplisitt i parseren, og tvetydigheten undersøkes i Del B.
- Alle vellykkede verktøykall skal returnere `{"resultat": str, "latex": str}`.

## Ferdig prompt å lime inn (etter at dere har fylt inn over)

```
Implementer backend/tools.py i et FastAPI/SymPy-prosjekt. Funksjonene som
skal implementeres er: calculate, derive, integrate, solve_equation, solve_ode,
matrix_op, complex_op (se signaturer og docstrings i filen). Bruk sympy.
Returner alltid {"resultat": str, "latex": str} ved suksess.

Feilhåndtering: håndter tom input, ugyldig SymPy-syntaks, ukjente operasjoner,
ugyldige variabler, deling på null, matriser med feil dimensjoner, singulære
matriser og ugyldige komplekse uttrykk eksplisitt. Ved feil skal funksjonene
kaste `ValueError` med en kort og forståelig norsk feilmelding. API-laget skal
fange feilen slik at brukeren ikke får stack trace. Parseren skal støtte `^`,
`3.5x` og `2(x+1)` som implisitt multiplikasjon uten å bruke `eval`.
Gruppens tolkning er `sin^-1(x)` som `asin(x)`, `cos^-1(x)` som `acos(x)` og
`tan^-1(x)` som `atan(x)`. Tvetydigheten undersøkes i eksperimentet.

Legg også til TOOL_DEFINITIONS: en liste med JSON-schema for OpenAI
function-calling som beskriver disse 7 funksjonene (navn, beskrivelse,
parametere med typer).

Skriv en kort forklarende docstring per funksjon, på norsk.
```

## Kvalitetssjekk før du limer inn koden

- [x] Alle 7 funksjonsnavn og parametere er UENDRET fra skjelettet.
- [x] Ingen `NotImplementedError` igjen.
- [x] `TOOL_DEFINITIONS` finnes og er en liste.
- [x] Dere forstår hvordan feil håndteres, og det stemmer med det dere
  bestemte i gruppens valg over.
- [x] Kjør `python scripts/selftest.py` – tools-sjekkene bør nå vise ✅.

