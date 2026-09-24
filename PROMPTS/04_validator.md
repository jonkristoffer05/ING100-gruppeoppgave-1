# Prompt: `backend/validator.py` – numerisk validering

**Fil:** `backend/validator.py`
**Hvorfor:** Etterprøvbarhet er ikke valgfritt for ingeniører. Hvis appen
sier at en løsning stemmer, skal det være fordi dere faktisk sjekket det.

## Krav (fast)

- `validate(problem: str, losning: str) -> {"validert": bool, "detaljer": str}`
- Sett løsningen inn i det originale problemet og evaluer numerisk i (minst)
  3 punkter med SymPy `subs`/`evalf`.
- Vær ærlig: hvis validering ikke er mulig for denne oppgavetypen, **si det**
  i `detaljer` – ikke returner `validert: True` fordi det ser bra ut.

## Gruppens valg

- Hva er «nært nok null»/riktig verdi numerisk (toleranse)? Flyttallregning
  er ikke eksakt. Bestem en toleranse (f.eks. `1e-6`) og begrunn kort hvorfor
  akkurat den:
  Gruppen bruker toleransen `1e-6`. Den er liten nok for vanlige førsteårsoppgaver,
  men tåler små avrundingsfeil fra flyttallsregning.
- Hvilke oppgavetyper klarer dere IKKE å validere med denne metoden (f.eks.
  åpne/ubestemte integraler, symbolske svar uten tallverdi)? List dem opp –
  dette skal appen si ærlig fra om, ikke skjule:
  Appen kan ikke pålitelig validere tekstlige bevis, begrepsforklaringer,
  tvetydige oppgaver som ikke er presisert, oppgaver med utilstrekkelig
  informasjon, ugyldige uttrykk eller oppgavetyper validatoren ikke har
  implementert. For ubestemte integraler må en eventuell integrasjonskonstant
  behandles særskilt; validatoren skal ikke hevde at et svar er validert
  dersom dette ikke faktisk er kontrollert. Ved slike tilfeller skal
  `validert` være `False`, og `detaljer` skal forklare hvorfor kontrollen ikke
  kunne utføres.
- Bruk faste, reproduserbare testpunkter fremfor tilfeldige testpunkter.
- SymPy skal brukes til parsing og kontroll; aldri `eval`.

## Ferdig prompt å lime inn (etter at dere har fylt inn over)

```
Implementer backend/validator.py sin funksjon
validate(problem: str, losning: str) -> dict som:
1. Bruker SymPy til å tolke problem og losning.
2. Setter løsningen inn i problemet og evaluerer numerisk i minst 3 faste,
   reproduserbare testpunkter (subs + evalf).
3. Bruker toleranse `1e-6` for å avgjøre om det stemmer.
4. Returnerer {"validert": bool, "detaljer": str} der detaljer forklarer
   HVA som ble sjekket og i hvilke punkter.
5. For oppgavetyper som ikke kan valideres slik (f.eks.
  tekstlige bevis, begrepsforklaringer, tvetydige eller utilstrekkelig
  spesifiserte oppgaver, ugyldige uttrykk, ikke-implementerte oppgavetyper
  og ubestemte integraler uten særskilt kontroll av integrasjonskonstant):
  returner `validert=False` med en ÆRLIG forklaring i `detaljer` om AT og
  HVORFOR validering ikke var mulig – ikke lat som alt er OK.
```

## Kvalitetssjekk før du limer inn koden

- [ ] `validert` er aldri `True` uten at en faktisk numerisk sjekk ble gjort.
- [ ] Når validering ikke er mulig, sier `detaljer` det eksplisitt (ikke bare
      `"Feil"` uten forklaring).
- [ ] Dere har testet med en løsning dere VET er feil, og sett at
      `validert` faktisk blir `False`.
- [ ] Kjør `python scripts/selftest.py` – validator-sjekken bør nå vise ✅.

## Faktisk løsning i MatteHjelpen

Validatoren identifiserer oppgavetype før SymPy-parsing og normaliserer `^`,
desimalkomma, implisitt multiplikasjon og frittstående `i`. Den støtter nå
derivasjon, ubestemte integraler, beregning/forenkling, én ligning,
ligningssystemer og enkel polarform for komplekse tall. ODE-svar kontrolleres
ved å sette løsningen inn og forenkle residualen.

Returformatet er fortsatt `{"validert": bool, "detaljer": str}`. Detaljteksten
skiller mellom matematisk verifisert, matematisk avvist, ikke automatisk
verifiserbart og ugyldig format. Bevis og åpne resonnementer får derfor ikke
status som feil svar, men krever manuell vurdering.

Modellens sluttrespons må være ett JSON-objekt med `svar`, `steg` og
`formel_ider`. Ved ugyldig JSON sendes én korrigerende melding innenfor den
eksisterende grensen på maksimalt åtte modellrunder. Rå modelltekst brukes
ikke som matematisk svar dersom formatet fortsatt er ugyldig.
