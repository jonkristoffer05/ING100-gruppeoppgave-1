"""Innebygd formelsamling – à la Jarle Johannessen: «Tekniske Tabeller».

Modellen skal referere til formler herfra i sine forklaringer.
Utvid gjerne med formler fra Edwards & Penney og Thomas' Calculus.

Feltet «bruk» hjelper modellen å velge regel. Modellen oppgir formel-ID i
løsningssteget; appen kontrollerer ID-en og henter navn og referanse herfra.

HVORFOR: Sporbarhet. «Hvilken formel brukte du, og hvor står den?» er et
spørsmål enhver ingeniør må kunne svare på.
"""

FORMELSAMLING = {
    "D1": {
        "navn": "Produktregelen",
        "formel": r"(uv)' = u'v + uv'",
        "referanse": "Thomas' Calculus, kap. 3",
        "bruk": "Når et produkt av to funksjoner skal deriveres.",
    },
    "D2": {
        "navn": "Kjerneregelen",
        "formel": r"\frac{dy}{dx} = \frac{dy}{du}\cdot\frac{du}{dx}",
        "referanse": "Thomas' Calculus, kap. 3",
        "bruk": "Når en sammensatt funksjon skal deriveres.",
    },
    "D3": {
        "navn": "Kvotientregelen",
        "formel": r"\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}",
        "referanse": "Thomas' Calculus, kap. 3",
        "bruk": "Når en kvotient av to deriverbare funksjoner skal deriveres.",
    },
    "D4": {
        "navn": "Potensregelen for derivasjon",
        "formel": r"\frac{d}{dx}x^n = nx^{n-1}",
        "referanse": "Thomas' Calculus, kap. 3",
        "bruk": "Når en potensfunksjon skal deriveres.",
    },
    "I1": {
        "navn": "Delvis integrasjon",
        "formel": r"\int u\,dv = uv - \int v\,du",
        "referanse": "Thomas' Calculus, kap. 8",
        "bruk": "Når integralet inneholder et produkt som blir enklere etter derivasjon av én faktor.",
    },
    "I2": {
        "navn": "Substitusjon ved integrasjon",
        "formel": r"\int f(g(x))g'(x)\,dx = \int f(u)\,du,\quad u=g(x)",
        "referanse": "Thomas' Calculus, kap. 5",
        "bruk": "Når et integral kan forenkles ved å bytte variabel til en indre funksjon.",
    },
    "I3": {
        "navn": "Potensregelen for integrasjon",
        "formel": r"\int x^n\,dx = \frac{x^{n+1}}{n+1}+C,\quad n\ne -1",
        "referanse": "Thomas' Calculus, kap. 4",
        "bruk": "Når en potens av x skal integreres og eksponenten ikke er -1.",
    },
    "O1": {
        "navn": "Karakteristisk ligning (2. ordens lineær ODE)",
        "formel": r"ar^2 + br + c = 0 \text{ for } ay'' + by' + cy = 0",
        "referanse": "Edwards & Penney, kap. 3",
        "bruk": "Når en homogen lineær differensialligning med konstante koeffisienter skal løses.",
    },
    "O2": {
        "navn": "Førsteordens lineær differensialligning",
        "formel": r"y' + p(x)y = q(x),\quad y=e^{-\int p(x)\,dx}\left(\int q(x)e^{\int p(x)\,dx}\,dx+C\right)",
        "referanse": "Edwards & Penney, kap. 2",
        "bruk": "Når en førsteordens differensialligning er lineær i y og y'.",
    },
    "K1": {
        "navn": "Eulers formel",
        "formel": r"e^{i\theta} = \cos\theta + i\sin\theta",
        "referanse": "Buanes: Komplekse tall",
        "bruk": "Når komplekse tall skal kobles mellom eksponentialform og trigonometrisk form.",
    },
    "K2": {
        "navn": "Polarform for komplekse tall",
        "formel": r"z = r(\cos\theta+i\sin\theta) = re^{i\theta},\quad r=|z|",
        "referanse": "Buanes: Komplekse tall",
        "bruk": "Når et komplekst tall skal uttrykkes ved modulus og argument.",
    },
    "K3": {
        "navn": "de Moivres formel",
        "formel": r"(r(\cos\theta+i\sin\theta))^n = r^n(\cos(n\theta)+i\sin(n\theta))",
        "referanse": "Buanes: Komplekse tall",
        "bruk": "Når potenser av komplekse tall skal beregnes i polarform.",
    },
    "M1": {
        "navn": "Determinant (2x2)",
        "formel": r"\det\begin{pmatrix}a & b\\ c & d\end{pmatrix} = ad - bc",
        "referanse": "Edwards & Penney, kap. 4",
        "bruk": "Når determinanten til en 2x2-matrise skal beregnes eller inverterbarhet vurderes.",
    },
    "M2": {
        "navn": "Invers av 2x2-matrise",
        "formel": r"\begin{pmatrix}a & b\\ c & d\end{pmatrix}^{-1} = \frac{1}{ad-bc}\begin{pmatrix}d & -b\\ -c & a\end{pmatrix},\quad ad-bc\ne 0",
        "referanse": "Edwards & Penney, kap. 4",
        "bruk": "Når inversen til en inverterbar 2x2-matrise skal finnes.",
    },
    "M3": {
        "navn": "Karakteristisk ligning for egenverdier",
        "formel": r"\det(A-\lambda I)=0",
        "referanse": "Edwards & Penney, kap. 4",
        "bruk": "Når egenverdiene til en matrise skal bestemmes.",
    },
}
