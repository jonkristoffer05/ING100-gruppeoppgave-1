# Eksperimentlogg (Del B)

Fyll ut tabellen under. Bruk de samme 10 oppgavene med minst to modeller av
ulik kvalitet, både med og uten tools. Det gir minst 40 kjøringer totalt
(10 oppgaver × 2 modeller × 2 tool-innstillinger).

## Testoppgaver

Oppgave 7 er med vilje tvetydig, mens oppgave 4 kontrollerer om appen er
ærlig om manglende verktøyvalidering.

Skriv `riktig/validert/tokens` i hver resultatkolonne, for eksempel
`ja/ja/1234`. Noter viktige forskjeller i kommentarfeltet.

| # | Oppgave | Modell A + tools | Modell A uten tools | Modell B + tools | Modell B uten tools | Kommentar |
|---|---------|------------------|----------------------|------------------|----------------------|-----------|
| 1 |Deriver: f(x) = (x^2 + 1)·sin(x)        |     ja/ja/5909            |                      |                  |                      |          |
| 2 |Deriver: f(x) = sin(3x^2)      |      ja/ja/7632            |                      |                  |                      |         |
| 3 |Integrer: ∫(3x^2 + 2x - 1) dx        |       ja/ja/5088           |                      |                  |                      |           |
| 4 |Bevis Pythagoras' læresetning        |  ja/nei/3473                |                      |                  |                      |           |
| 5 |Løs ligningssystemet: 2x + 3y = 7 og x - y = 1         |                  |                      |                  |                      |           |
| 6 |Løs differensialligningen: y'' + 2y = 0        |                  |                      |                  |                      |           |
| 7 |Beregn sin^-1(0.5)        |                  |                      |                  |                      |           |
| 8 |	Regn ut e^(iπ/2) med eulers formel    |                  |                      |                  |                      |           |
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
