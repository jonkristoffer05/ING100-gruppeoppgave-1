# Eksperimentlogg (Del B)

Fyll ut tabellen under. Bruk de samme 10 oppgavene med minst to modeller av
ulik kvalitet, både med og uten tools. Det gir minst 40 kjøringer totalt
(10 oppgaver × 2 modeller × 2 tool-innstillinger).

## Forslag til testoppgaver

Velg gjerne 10 oppgaver der noen er enkle og noen krever eksakt regning. Et
godt sett er en blanding av:

- derivasjon med produktregelen og kjerneregelen
- integrasjon med brøk-/potensuttrykk
- lineære ligninger med flere ukjente
- differensialligninger med eksakte koeffisienter
- komplekse tall eller matriser med brøker

Eksempler som ofte viser forskjell mellom modell og SymPy, også for sterke
modeller:

- `Eq(diff(x(t), t, 2) + 2*x(t), 0)`
- `solve_equation("x**2 - 2*x - 8", "x")`
- `matrix_op("solve_ax_b", [[[1, 1/2, 1/3], [1/2, 1/3, 1/4], [1/3, 1/4, 1/5]], [1, 1, 1]])`
- `complex_op("polar", "1+I")`

Tips: bruk minst én oppgave der dere kan regne svaret for hånd, og minst én
oppgave der tallene er litt «stygge», slik at modellens små regnefeil blir
synlige. Test også gjerne én bevis-/begrepsoppgave (f.eks. «bevis Pythagoras'
læresetning») for å se om appen er ærlig om at den ikke kan verktøy-verifisere
svaret.

Skriv `riktig/validert/tokens` i hver resultatkolonne, for eksempel
`ja/ja/1234`. Noter viktige forskjeller i kommentarfeltet.

| # | Oppgave | Modell A + tools | Modell A uten tools | Modell B + tools | Modell B uten tools | Kommentar |
|---|---------|------------------|----------------------|------------------|----------------------|-----------|
| 1 |Deriver: f(x) = (x^2 + 1)·si(x)        |                  |                      |                  |                      |           |
| 2 |Deriver: f(x) = sin(3x^2)      |                  |                      |                  |                      |           |
| 3 |Integrer: ∫(3x^2 + 2x - 1) dx        |                  |                      |                  |                      |           |
| 4 |Integrer: ∫ dx/(x+2)        |                  |                      |                  |                      |           |
| 5 |Løs ligningssystemet: 2x + 3y = 7, x - y = 1         |                  |                      |                  |                      |           |
| 6 |Løs differensialligningen: y'' + 2y = 0        |                  |                      |                  |                      |           |
| 7 |Karakteristisk ligning for y'' - 3y' + 2y = 0        |                  |                      |                  |                      |           |
| 8 |	Regn ut Eulers formel for e^(iπ/2)      |                  |                      |                  |                      |           |
| 9 |	Skriv 1 + i i polarform       |                  |                      |                  |                      |           |
| 10 |Løs matriseproblem: A x = b med A = [[1, 1/2, 1/3],[1/2,1/3,1/4],[1/3,1/4,1/5]] og b = [1,1,1]        |                  |                      |                  |                      |           |

## Kostnadsberegning

- Totalt tokenforbruk for 10 oppgaver: …
- Estimert kostnad: …
- Ekstrapolert: 1000 studenter × 50 oppgaver = …

## Observasjoner fra aha-bryterne

1. Tools av: …
2. Uten stegvis forklaring: …
3. Modellbytte: …
4. Tvetydig oppgave: …
5. Valideringsfeil: …
