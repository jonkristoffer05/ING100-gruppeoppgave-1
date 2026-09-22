"""Innebygd formelsamling for MatteHjelpen."""

FORMELSAMLING = {
    "D1": {"navn": "Produktregelen", "formel": r"(uv)' = u'v + uv'", "referanse": "Thomas' Calculus, kap. 3", "bruk": "Derivasjon av et produkt."},
    "D2": {"navn": "Kjerneregelen", "formel": r"\frac{dy}{dx}=\frac{dy}{du}\frac{du}{dx}", "referanse": "Thomas' Calculus, kap. 3", "bruk": "Derivasjon av en sammensatt funksjon."},
    "D3": {"navn": "Potensregelen", "formel": r"\frac{d}{dx}x^n=nx^{n-1}", "referanse": "Thomas' Calculus, kap. 3", "bruk": "Derivasjon av potenser."},
    "D4": {"navn": "Sumregelen", "formel": r"(u+v)'=u'+v'", "referanse": "Thomas' Calculus, kap. 3", "bruk": "Derivasjon av en sum eller differanse."},
    "D5": {"navn": "Trigonometriske derivasjoner", "formel": r"(\sin x)'=\cos x,\ (\cos x)'=-\sin x", "referanse": "Thomas' Calculus, kap. 3", "bruk": "Derivasjon av sinus og cosinus."},
    "D6": {"navn": "Eksponentialderivasjon", "formel": r"(e^{ax})'=ae^{ax}", "referanse": "Thomas' Calculus, kap. 3", "bruk": "Derivasjon av eksponentialfunksjoner."},
    "I1": {"navn": "Delvis integrasjon", "formel": r"\int u\,dv=uv-\int v\,du", "referanse": "Thomas' Calculus, kap. 8", "bruk": "Integrasjon av produkter."},
    "I2": {"navn": "Potensintegrasjon", "formel": r"\int x^n dx=\frac{x^{n+1}}{n+1}+C", "referanse": "Thomas' Calculus, kap. 5", "bruk": "Integrasjon av potenser."},
    "I3": {"navn": "Eksponentialintegrasjon", "formel": r"\int e^{ax}dx=\frac1a e^{ax}+C", "referanse": "Thomas' Calculus, kap. 5", "bruk": "Integrasjon av eksponentialfunksjoner."},
    "I4": {"navn": "Trigonometrisk integrasjon", "formel": r"\int\sin xdx=-\cos x+C", "referanse": "Thomas' Calculus, kap. 5", "bruk": "Integrasjon av trigonometriske funksjoner."},
    "O1": {"navn": "Karakteristisk ligning", "formel": r"ar^2+br+c=0", "referanse": "Edwards & Penney, kap. 3", "bruk": "Homogene lineære ODE-er med konstante koeffisienter."},
    "O2": {"navn": "ODE-løsningsform", "formel": r"y=C_1e^{r_1x}+C_2e^{r_2x}", "referanse": "Edwards & Penney, kap. 3", "bruk": "To reelle røtter i karakteristisk ligning."},
    "L1": {"navn": "Determinant (2x2)", "formel": r"\det A=ad-bc", "referanse": "Edwards & Penney, kap. 4", "bruk": "Determinant og inverterbarhet."},
    "L2": {"navn": "Invers matrise", "formel": r"A^{-1}=\frac1{\det(A)}\operatorname{adj}(A)", "referanse": "Edwards & Penney, kap. 4", "bruk": "Invertering av matriser."},
    "L3": {"navn": "Lineært system", "formel": r"Ax=b\Rightarrow x=A^{-1}b", "referanse": "Edwards & Penney, kap. 4", "bruk": "Løsning av lineære ligningssystemer."},
    "C1": {"navn": "Eulers formel", "formel": r"e^{i\theta}=\cos\theta+i\sin\theta", "referanse": "Buanes: Komplekse tall", "bruk": "Eksponentialform og trigonometrisk form."},
    "C2": {"navn": "Komplekst tall i polarform", "formel": r"z=r(\cos\theta+i\sin\theta)", "referanse": "Buanes: Komplekse tall", "bruk": "Konvertering til polarform."},
    "C3": {"navn": "De Moivres formel", "formel": r"(\cos\theta+i\sin\theta)^n=\cos(n\theta)+i\sin(n\theta)", "referanse": "Buanes: Komplekse tall", "bruk": "Potenser av komplekse tall."},
}
