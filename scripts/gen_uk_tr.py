#!/usr/bin/env python3
"""Generuje templates/urny_koty_grafika_tlumaczenie_<język>.md (PL + 7) z zatwierdzonych szablonów urn "with Graphics" dla psów (grafika_tlumaczenie_<język>.md):
zamiana pies -> kot, geometryczny -> kreskówkowy. Formy gatunku w innych językach ({S}, {GEN}...) podstawia skrypt wg gatunku kot."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates"
R = {
 "pl": [("wspomnienia spacerów, zabawy i cichych wieczorów", "wspomnienia zabawy, pieszczot i cichych wieczorów"), ("z nowoczesnym geometrycznym portretem", "z uroczym kreskówkowym portretem"), ("geometrycznym portretem", "kreskówkowym portretem"), ("geometryczny portret", "kreskówkowy portret")],
 "de": [("Erinnerungen an Spaziergänge, Spiel und ruhige Abende", "Erinnerungen an Spiel, Kuscheln und ruhige Abende"), ("für Ihren {S}", "für Ihre {S}"), ("mit modernem geometrischem Rassenporträt", "mit niedlichem Cartoon-Rassenporträt"), ("mit geometrischem Rassenporträt", "mit Cartoon-Rassenporträt"), ("das geometrische Rassenporträt", "das Cartoon-Rassenporträt"),
        ("Abschied von einem Hund", "Abschied von einer Katze"), ("Name Ihres Hundes", "Name Ihrer Katze"), ("Hunde Andenken", "Katzen Andenken")],
 "nl": [("herinneringen aan wandelingen, spel en rustige avonden", "herinneringen aan spel, knuffels en rustige avonden"), ("een modern geometrisch rasportret", "een schattig cartoon-rasportret"), ("met geometrisch rasportret", "met cartoon-rasportret"), ("het geometrische rasportret", "het cartoon-rasportret"),
        ("van een hond", "van een kat"), ("uw hond", "uw kat"), ("unieke hondenurn", "unieke katurn"), ("hond aandenken", "kat aandenken")],
 "fr": [("souvenirs des promenades, des jeux et des soirées tranquilles", "souvenirs des jeux, des câlins et des soirées tranquilles"), ("au portrait géométrique moderne de la race", "à l'adorable portrait de style dessin animé de la race"), ("au portrait géométrique de la race", "au portrait de style dessin animé de la race"),
        ("avec portrait géométrique de la race", "avec portrait de style dessin animé de la race"), ("le portrait géométrique de la race", "le portrait de style dessin animé de la race"),
        ("à un chien qui", "à un chat qui"), ("votre chien", "votre chat"), ("urne unique chien", "urne unique chat"), ("souvenir de chien", "souvenir de chat")],
 "it": [("ricordi di passeggiate, giochi e serate tranquille", "ricordi di giochi, coccole e serate tranquille"), ("con un moderno ritratto geometrico della razza", "con un grazioso ritratto in stile cartoon della razza"), ("con ritratto geometrico della razza", "con ritratto in stile cartoon della razza"),
        ("il ritratto geometrico della razza", "il ritratto in stile cartoon della razza"), ("a un cane che", "a un gatto che"), ("urna unica per cane", "urna unica per gatto"), ("ricordo del cane", "ricordo del gatto"), ("del suo cane", "del suo gatto")],
 "pt": [("memórias de passeios, brincadeiras e serões tranquilos", "memórias de brincadeiras, miminhos e serões tranquilos"), ("com um retrato geométrico moderno da raça", "com um retrato fofo em estilo de desenho animado da raça"), ("com retrato geométrico da raça", "com retrato em estilo de desenho animado da raça"),
        ("o retrato geométrico da raça", "o retrato em estilo de desenho animado da raça"), ("de um cão que", "de um gato que"), ("do seu cão", "do seu gato"), ("urna única cão", "urna única gato"), ("lembrança de cão", "lembrança de gato")],
 "es": [("recuerdos de paseos, juegos y tardes tranquilas", "recuerdos de juegos, mimos y tardes tranquilas"), ("con un retrato geométrico moderno de la raza", "con un adorable retrato de estilo dibujos animados de la raza"), ("con retrato geométrico de la raza", "con retrato de estilo dibujos animados de la raza"),
        ("el retrato geométrico de la raza", "el retrato de estilo dibujos animados de la raza"), ("de un perro que", "de un gato que"), ("de tu perro", "de tu gato"), ("urna única perro", "urna única gato"), ("recuerdo de perro", "recuerdo de gato")],
 "sv": [("minnena av promenader, lek och lugna kvällar", "minnena av lek, gos och lugna kvällar"), ("ett modernt geometriskt rasporträtt", "ett gulligt tecknat rasporträtt"), ("med geometriskt rasporträtt", "med tecknat rasporträtt"), ("det geometriska rasporträttet", "det tecknade rasporträttet"),
        ("av en hund som", "av en katt som"), ("din hunds", "din katts"), ("unik hundurna", "unik katturna"), ("hundminne", "kattminne")],
}


def main():
    for code, pairs in R.items():
        t = (TPL / f"grafika_tlumaczenie_{code}.md").read_text(encoding="utf-8")
        for a, b in pairs:
            t = t.replace(a, b)
        if code == "pl":
            t = re.sub(r"\bpsa\b", "kota", t)
            t = re.sub(r"\bpsie\b", "kocie", t)
            t = re.sub(r"\bpsem\b", "kotem", t)
            t = re.sub(r"\bpsu\b", "kotu", t)
            t = t.replace("Wszystkie oferty to psy ({gen} = psa, {loc} = psie).", "Wszystkie oferty to koty (wersja na podstawie zatwierdzonej wersji dla psów, 04.11.2026).")
        t = t.replace("(EN: urn for pet ashes, personalized urn, wooden urn, cremation urn, pet loss gift, unique dog urn, dog memorial", "(EN: urn for pet ashes, personalized urn, wooden urn, cremation urn, pet loss gift, unique cat urn, cat memorial")
        out = []
        for ln in t.split("\n"):
            if ln.startswith("**Stałe:**") or ln.startswith("**Pula:**"):
                head, rest = ln.split("** ", 1)
                en = ""
                if " (EN:" in rest:
                    rest, en = rest.split(" (EN:", 1)
                    en = " (EN:" + en
                items = [re.sub(r" \(\d+\)$", "", x.strip()) for x in rest.split(", ")]
                ln = head + "** " + ", ".join(f"{x} ({len(x)})" for x in items) + en
            out.append(ln)
        (TPL / f"urny_koty_grafika_tlumaczenie_{code}.md").write_text("\n".join(out), encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
