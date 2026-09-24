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
| 1 |Deriver: f(x) = (x^2 + 1)·sin(x)        |     ja/ja/4308            |      nei/nei/3987                |        ja/ja/5523          |             ja/ja/2480         |    Gemma uten tools returnerte ugyldig JSON.      |
| 2 |Deriver: f(x) = sin(3x^2)      |      ja/ja/4250            |           ja/ja/1650           |          ja/ja/8166        |           ja/ja/1845           |         |
| 3 |Integrer: ∫(3x^2 + 2x - 1) dx        |       ja/ja/10633           |            ja/manuell/1674          |        ja/ja/5314          |           ja/ja/1956           |      Gemma uten tools måtte vurderes manuelt.     |
| 4 |Bevis Pythagoras' læresetning        |  ja/manuell/2316                |       ja/manuell/1792               |          ja/manuell/2995        |           ja/manuell/2357           |     Bevisoppgave – alle svar måtte vurderes manuelt.     |
| 5 |Løs ligningssystemet: 2x + 3y = 7 og x - y = 1         |         ja/ja/4189         |            ja/ja/1848          |        ja/ja/17430          |          ja/ja/2440            |     NVIDIA med tools brukte uvanlig mange tokens.      |
| 6 |Løs differensialligningen: y'' + 2y = 0        |         nei/nei/17452        |             ja/ja/1678         |         ja/ja/17242         |              ja/ja/1900        |      Gemma med tools svarte feil; NVIDIA med tools brukte svært mange tokens.     |
| 7 |Beregn sin^-1(0.5)        |       ja/manuell/10813           |          ja/manuell/1565            |         ja/feil-negativ/5286         |           ja/feil-negativ/2163           |      Tvetydig sin^-1 ble tolket som arcsin; NVIDIA fikk falsk negativ validering.     |
| 8 |	Regn ut e^(iπ/2) med eulers formel    |           ja/feil-negativ/4132       |           ja/nei/1550           |           ja/feil-negativ/5303       |           ja/feil-negativ/2740           |      Riktig svar i, men validatoren avviste flere av forsøkene.     |
| 9 |	Skriv 1 + i i polarform       |         ja/falsk-negativ/4124         |         ja/ja/1572             |         ja/ja/10689         |             ja/ja/1697         |     Gemma med tools fikk falsk negativ på korrekt polarform.      |
| 10 |Løs matriseproblem: A x = b med A = [[1, 1/2, 1/3],[1/2,1/3,1/4],[1/3,1/4,1/5]] og b = [1,1,1]        |       ja/ja/4558           |          nei/nei/1797            |         nei/nei/26127         |          ja/ja/4202            |      Gemma uten tools svarte feil; NVIDIA med tools endte med ugyldig JSON etter gjentatte verktøykall.     |


## Kostnadsberegning

- Totalt tokenforbruk for 10 oppgaver: Gemma med tools: 66 775, Gemma uten tools: 19 113, NVIDIA med tools: 104 075 og NVIDIA uten tools: 23 780.
- Gjennomsnittlig tokenforbruk per oppgave: 8 542,5 med tools og 2 144,65 uten tools.
- Ekstrapolert til 1000 studenter med 50 oppgaver hver: ca. 427 125 000 tokens med tools og 107 232 500 tokens uten tools.

## Observasjoner fra aha-bryterne

1. Tools av: Effekten varierte mellom modellene. Gemma gikk fra 9/10 riktige med tools til 8/10 uten tools. NVIDIA gikk derimot fra 9/10 med tools til 10/10 uten tools. Verktøybruk ga derfor ikke automatisk bedre resultater. NVIDIA brukte også mange verktøykall på matriseoppgaven uten å produsere et gyldig sluttsvar.
2. Uten stegvis forklaring: Det ble vanskeligere å oppdage hvordan modellen hadde kommet fram til svaret. Stegvis forklaring gjorde det lettere å finne regnefeil, feil tolkning og tilfeller der konklusjonen ikke stemte med utregningen.
3. Modellbytte: Google Gemma fikk 9/10 riktige med tools og 8/10 uten tools. NVIDIA Nemotron fikk 9/10 med tools og 10/10 uten tools. NVIDIA presterte dermed best uten tools, men brukte gjennomgående flere tokens med tools.
4. Tvetydig oppgave: Oppgaven sin^-1(0.5) ble tolket som arcsin(0.5), med svaret 30 grader eller pi/6. Svaret var matematisk riktig etter denne tolkningen, men validatoren håndterte oppgaven ulikt og ga flere falske negative resultater.
5. Valideringsfeil: Validatoren avviste flere matematisk riktige svar. Dette skjedde blant annet for e^(i*pi/2) = i og enkelte svar om komplekse tall. Resultatene viser derfor at automatisk validering må kombineres med manuell matematisk vurdering.
