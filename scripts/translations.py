#!/usr/bin/env python3
"""Draft translations (DE, NL) of the plaque templates, rendered to templates/ and the Sphynx test plan.
Texts are drafts by Claude and need a native check. Breed names always come from Rasy.xlsx (never translated here).
Usage: python3 -I scripts/translations.py
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
CORE_EN = ["pet memorial plaque", "grave marker", "tombstone plaque", "pet loss gift", "custom photo plaque"]
POOL_EN = ["ceramic plaque", "personalized plaque", "pet headstone", "outdoor memorial", "garden memorial", "memorial keepsake",
           "sympathy gift", "remembrance gift", "in loving memory", "rainbow bridge", "pet remembrance", "photo on ceramic",
           "pet sympathy gift", "grave decoration", "weatherproof plaque", "oval memorial plaque", "pet grave plaque",
           "cemetery marker", "pet bereavement", "pet memorial gift", "memorial for pet", "pet memorial stone", "pet photo plaque",
           "custom memorial", "headstone plaque", "always in my heart", "pet loss keepsake", "grave plaque", "memorial plaque",
           "pet tombstone"]
SPECIES = ["kot", "pies", "koń", "kucyk"]

L = {}
L["de"] = dict(
    name="Deutsch", col="DE nazwa", basket="Gedenkplatte aus Keramik",
    sp={  # nominative, compound prefix, accusative/dative/genitive with possessive
        "kot": dict(S="Katze", CS="Katzen", ACC="Ihre Katze", DAT="Ihrer Katze", GEN="Ihrer Katze"),
        "pies": dict(S="Hund", CS="Hunde", ACC="Ihren Hund", DAT="Ihrem Hund", GEN="Ihres Hundes"),
        "koń": dict(S="Pferd", CS="Pferde", ACC="Ihr Pferd", DAT="Ihrem Pferd", GEN="Ihres Pferdes"),
        "kucyk": dict(S="Pony", CS="Pony", ACC="Ihr Pony", DAT="Ihrem Pony", GEN="Ihres Ponys")},
    titles=["{B} {CS}-Gedenkplatte, personalisierte Keramik-Grabplatte mit Foto, Andenken an das Haustier",
            "{B} Haustier-Gedenkplatte, individuelle Keramik-Grabplatte mit Ihrem Foto, Trauergeschenk",
            "{B} {CS}-Grabplatte, Keramik-Grabschild mit Foto, personalisiertes Andenken an das Haustier",
            "{B} Grabschmuck mit Foto, individuelle Keramikplatte für Tiergrab oder Garten, Andenken",
            "{B} {CS}-Gedenkplatte mit Foto, personalisierte Keramik-Grabplatte, in liebevoller Erinnerung",
            "{B} Keramik-Gedenkplatte, individuelles Foto-Grabschild für Ihr Tier, Andenken an das Haustier"],
    A=["{B}: Gedenkplatte aus Keramik mit einem Skizzenporträt, gestaltet zur Erinnerung an {ACC}.",
       "Keramik-Gedenkplatte für {ACC} (Rasse: {B}) mit Skizzenporträt.",
       "Grabplatte als Andenken, Rasse: {B}. Eine Erinnerung aus Keramik an {ACC}.",
       "Keramik-Gedenkplatte mit Skizzenporträt, Rasse: {B}. Geschaffen, um einem geliebten Begleiter die letzte Ehre zu erweisen.",
       "{B} – Gedenkplatte aus Keramik: ein Skizzenporträt, das die Erinnerung an {ACC} bewahrt."],
    B=["Platzieren Sie sie auf einem Grab oder an einem anderen Ort des Gedenkens, als Hommage an Ihren Liebling, der Teil Ihres Lebens war.",
       "Sie kann ein Grab kennzeichnen oder an einem stillen, für Sie bedeutsamen Ort stehen, als Erinnerung an {ACC}.",
       "Sie dient als Grabkennzeichnung oder als Erinnerungsstück an einem Ort des Gedenkens, eine Hommage an {ACC}.",
       "Eine würdige Hommage für ein Grab oder jeden Ort, an dem Sie sich an {ACC} erinnern, wetterbeständig."],
    C=["Wenn Sie lieber Ihr eigenes Tier in Erinnerung behalten möchten, senden Sie uns ein Foto, und wir drucken es anstelle des Motivs.",
       "Lieber das Porträt Ihres eigenen Tieres? Fügen Sie ein Foto bei, und wir drucken es auf die Platte.",
       "Sie können die Platte auch mit einem Foto Ihres eigenen Tieres bedrucken lassen.",
       "Statt des Motivs können wir Ihr Foto drucken, fügen Sie es einfach bei der Bestellung bei."],
    fixed='''KURZ ZUSAMMENGEFASST
- Ovale Keramikplatte, ca. 10,5 x 7,5 cm (4,13 x 2,95 Zoll), ca. 0,5 cm (0,2 Zoll) dick
- Skizzenporträt (Rasse: {B}) oder mit Ihrem eigenen Foto
- Wetterbeständiger Druck, der nicht verblasst
- Glatte, abgerundete Kante, keine zusätzliche Fassung nötig
- Ohne Loch oder Haken auf der Rückseite, mit handelsüblichem Universalkleber zu befestigen
- Personalisierung möglich: Ihr Foto, Druckstil, Name und Daten

ERINNERUNG AN IHREN FREUND
Eine Keramikplatte ist eine behutsame und bleibende Art, die Erinnerung an {ACC} zu bewahren. Die glatte Kante braucht keine besondere Fassung, der hochwertige Druck ist auf lange Haltbarkeit ausgelegt, und die Personalisierung macht die Platte zu etwas ganz Persönlichem.

PERSONALISIERUNG
Bestellen Sie die Platte genau wie abgebildet oder personalisieren Sie sie. Jede der folgenden Optionen ist freiwillig.
- Ihr Foto: Wir drucken jedes Foto, das Sie uns senden. Fügen Sie es bei der Bestellung im Personalisierungsfeld bei oder senden Sie es per Etsy-Nachricht.
- Stil: Wählen Sie das Originalfoto, Farbe mit entferntem Hintergrund oder einen Bleistiftskizzen-Stil wie auf den Angebotsfotos.
- Name und Daten: Fügen Sie den Namen {GEN} hinzu, oder Name und Lebensdaten, oder lassen Sie die Platte ohne Schrift.
- Ausrichtung: Eine Platte mit Ihrem Foto kann hoch- oder querformatig gestaltet werden.

Haben Sie Fragen zur Personalisierung? Schreiben Sie uns, wir helfen gern.

Es wäre uns eine Ehre, Sie dabei zu unterstützen, würdevoll von {DAT} Abschied zu nehmen.

INTERNATIONALE BESTELLUNGEN
Unsere Produkte werden aus Polen versendet, daher können in einigen Ländern Einfuhrabgaben anfallen. Diese Abgaben gelten nicht für EU-Länder, das Vereinigte Königreich und die USA. Bei Fragen kontaktieren Sie uns gerne, wir nennen Ihnen die Details.''',
    core=["Gedenkplatte", "Grabschild", "Grabplatte", "Trauergeschenk", "Foto Gedenkplatte"],
    spec={"kot": ("Katzen Gedenkplatte", "Katzen Grabschild"), "pies": ("Hunde Gedenkplatte", "Hunde Grabschild"),
          "koń": ("Pferde Gedenkplatte", "Pferde Grabschild"), "kucyk": ("Pony Gedenkplatte", "Pony Grabschild")},
    pool=['Keramikplatte', 'Individuelle Platte', 'Grabstein Haustier', 'Outdoor Gedenken', 'Gedenken im Garten', 'Erinnerungsstück', 'Beileidsgeschenk', 'Erinnerungsgeschenk', 'Zur Erinnerung', 'Regenbogenbrücke', 'Haustier Erinnerung', 'Foto auf Keramik', 'Haustier Beileid', 'Grabdekoration', 'Wetterfeste Platte', 'Ovale Gedenkplatte', 'Tiergrab Platte', 'Friedhof Schild', 'Tiertrauer', 'Gedenkgeschenk', 'Haustier Gedenken', 'Gedenkschild', 'Haustier Fotoplatte', 'Andenken mit Foto', 'Grabstein Platte', 'Immer im Herzen', 'Trauer Andenken', 'Grabplatte Keramik', 'Gedenktafel', 'Tiergrab'])
L["nl"] = dict(
    name="Nederlands", col="NL nazwa", basket="Keramische gedenkplaat",
    sp={"kot": dict(S="kat"), "pies": dict(S="hond"), "koń": dict(S="paard"), "kucyk": dict(S="pony")},
    titles=["{B} gedenkplaat voor uw {S}, gepersonaliseerde keramische grafplaat met foto, aandenken",
            "{B} huisdier gedenkplaat, keramische grafplaat met uw eigen foto, rouwcadeau",
            "{B} grafplaat voor uw {S}, keramisch grafbordje met foto, gepersonaliseerd aandenken",
            "{B} grafversiering met foto, keramische plaat op maat voor graf of tuin, aandenken aan uw huisdier",
            "{B} gedenkplaat voor {S} met foto, gepersonaliseerde keramische grafplaat, ter herinnering",
            "{B} keramische gedenkplaat, grafbordje met uw foto voor uw {S}, aandenken aan uw huisdier"],
    A=["{B}: keramische grafplaat met een schetsportret, gemaakt ter nagedachtenis aan uw {S}.",
       "Keramische gedenkplaat voor uw {S} (ras: {B}) met een schetsportret.",
       "Gedenkplaat als aandenken, ras: {B}. Een herinnering in keramiek aan uw {S}.",
       "Keramische gedenkplaat met een schetsportret, ras: {B}. Gemaakt om een geliefde metgezel te eren.",
       "{B} – gedenkplaat van keramiek: een schetsportret dat de herinnering aan uw {S} bewaart."],
    B=["Plaats hem op een graf of op een andere plek van herinnering, als eerbetoon aan uw geliefde dier dat deel uitmaakte van uw leven.",
       "Hij kan een graf markeren of op een stille, voor u betekenisvolle plek staan, als herinnering aan uw {S}.",
       "Hij dient als grafmarkering of als aandenken op een plek van herinnering, een eerbetoon aan uw {S}.",
       "Een waardig eerbetoon voor een graf of elke plek waar u aan uw {S} denkt, bestand tegen weer en wind."],
    C=["Wilt u liever uw eigen dier herdenken? Stuur ons een foto en wij drukken die af in plaats van het ontwerp.",
       "Liever het portret van uw eigen dier? Voeg een foto toe en wij drukken die op de plaat.",
       "U kunt de plaat ook laten bedrukken met een foto van uw eigen dier.",
       "In plaats van het ontwerp kunnen wij uw foto afdrukken, voeg die gewoon toe bij de bestelling."],
    fixed='''IN HET KORT
- Ovale keramische plaat, ca. 10,5 x 7,5 cm (4,13 x 2,95 inch), ca. 0,5 cm (0,2 inch) dik
- Portret in schetsstijl (ras: {B}) of met uw eigen foto
- Weerbestendige print die niet verbleekt
- Gladde, afgeronde rand, geen extra omlijsting nodig
- Zonder gat of haakje aan de achterkant, te bevestigen met gewone universele lijm
- Personalisatie mogelijk: uw foto, printstijl, naam en data

HERINNERING AAN UW VRIEND
Een keramische plaat is een zachte en blijvende manier om de herinnering aan uw {S} te bewaren. De gladde rand heeft geen speciale omlijsting nodig, de hoogwaardige print is gemaakt om lang mee te gaan en met personalisatie maakt u de plaat helemaal van uzelf.

PERSONALISATIE
Bestel de plaat precies zoals afgebeeld of personaliseer hem. Elke optie hieronder is vrijwillig.
- Uw foto: wij drukken elke foto af die u ons stuurt. Voeg hem bij de bestelling toe in het personalisatieveld of stuur hem via een Etsy-bericht.
- Stijl: kies de originele foto, volledige kleur met verwijderde achtergrond of een potloodschets-stijl zoals op de foto's bij dit aanbod.
- Naam en data: voeg de naam van uw {S} toe, of naam en levensdata, of laat de plaat zonder tekst.
- Oriëntatie: een plaat met uw foto kan staand of liggend worden uitgevoerd.

Heeft u vragen over personalisatie? Stuur ons een bericht, wij helpen u graag.

Het zou ons een eer zijn om u te helpen op waardige wijze afscheid te nemen van uw {S}.

INTERNATIONALE BESTELLINGEN
Onze producten worden vanuit Polen verzonden, daarom kunnen in sommige landen invoerkosten worden berekend. Deze kosten gelden niet voor EU-landen, het Verenigd Koninkrijk en de VS. Heeft u twijfels, neem dan contact met ons op voor details.''',
    core=["gedenkplaat", "grafbordje", "grafplaat", "rouwcadeau", "gedenkplaat met foto"],
    spec={"kot": ("katten gedenkplaat", "kattengraf bordje"), "pies": ("honden gedenkplaat", "hondengraf bordje"),
          "koń": ("paarden gedenkplaat", "paardengraf bordje"), "kucyk": ("pony gedenkplaat", "pony grafbordje")},
    pool=['keramische plaat', 'plaat op maat', 'grafsteen huisdier', 'outdoor herdenking', 'herdenken in tuin', 'herinneringsstuk', 'condoleance cadeau', 'herinneringscadeau', 'ter herinnering', 'regenboogbrug', 'huisdier herinnering', 'foto op keramiek', 'huisdier condoleance', 'grafdecoratie', 'weerbestendige plaat', 'ovale gedenkplaat', 'huisdiergraf plaat', 'begraafplaats bord', 'rouw om huisdier', 'gedenkcadeau', 'huisdier herdenken', 'gedenkbordje', 'huisdier fotoplaat', 'aandenken met foto', 'grafsteen plaat', 'altijd in mijn hart', 'rouw aandenken', 'grafplaat keramiek', 'gedenktafel', 'huisdiergraf'])


sys.path.insert(0, str(Path(__file__).resolve().parent))
from translations_more import MORE  # noqa: E402

L["de"]["feat"] = "langhaarig"
L["nl"]["feat"] = "langharig"
L.update(MORE)


FEAT = re.compile(r"long|short|wire|smooth|fohlen|cropped|curly", re.I)


def breed_names(col):
    ws = openpyxl.load_workbook(ROOT / "data" / "Rasy.xlsx", data_only=True)["Rasy"]
    h = [c.value for c in ws[1]]
    i = h.index(col)
    return {(r[1], r[0]): r[i] for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}


def fill(t, sp, b):
    return re.sub(r"\s+", " ", t.format(B=b, **sp)).strip()


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "plans" / "mapa_koncowa.csv", encoding="utf-8")) if r["decyzja"] == "OPTYMALIZUJ"]
    gk = {"pies": "pies", "kot": "kot", "koń": "koń"}
    for code, d in L.items():
        names = breed_names(d["col"])
        mx, ex = 0, ""
        for r in rows:
            sp = d["sp"][r["gatunek"]]
            b = names[(r["gatunek"], r["rasa_id"])]
            if FEAT.search(r["folder"] + " " + r["nazwa_w_tytule"]):  # offers whose title carries a coat or age word
                b += " " + d["feat"]
            for t in d["titles"]:
                x = fill(t, sp, b)
                if len(x) > mx:
                    mx, ex = len(x), x
        all_tags = d["core"] + d["pool"] + [x for v in d["spec"].values() for x in v]
        long_tags = [(t, len(t)) for t in all_tags if len(t) > 20]
        md = f"# Tłumaczenie {d['name']}: płytka ceramiczna \"with a Photo\" (szkic Claude'a, wymaga kontroli osoby natywnej)\n\n"
        md += "Forma grzecznościowa (zgodnie z ustaleniem). Nazwa rasy w tekście zawsze w mianowniku, z arkusza Rasy (kolumna " + d["col"] + "). Zdrobnień nie używamy. Nagłówek sekcji to analog polskiego \"Pamiątka po Twoim przyjacielu\".\n\n"
        md += "## Tytuł (6 wzorców)\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(d["titles"])) + f"\n\nNajdłuższy tytuł wśród 299 ofert (z dopisaną odmianą sierści tam, gdzie oferta ją ma): {mx} znaków (limit 140).\n\n"
        md += "## Pierwszy akapit: banki\n**A**\n" + "\n".join(f"- A{i+1}: {t}" for i, t in enumerate(d["A"]))
        md += "\n\n**B**\n" + "\n".join(f"- B{i+1}: {t}" for i, t in enumerate(d["B"])) + "\n\n**C**\n" + "\n".join(f"- C{i+1}: {t}" for i, t in enumerate(d["C"]))
        md += "\n\nFormy gatunku: " + "; ".join(f"{k}: " + ", ".join(f"{a}={b}" for a, b in v.items()) for k, v in d["sp"].items()) + "\n\n"
        md += "## Sekcje stałe (szablon ze zmiennymi: {B} = rasa z arkusza, pozostałe zmienne to formy gatunku z tabeli powyżej)\n```\n" + d["fixed"] + "\n```\n\n"
        md += "### Przykład wypełnienia dla psa (rasa: {B})\n```\n" + fill_block(d["fixed"], d["sp"]["pies"], "{B}") + "\n```\n\n"
        md += f"## Shopping basket summary\n{d['basket']}\n\n## Tagi (max 20 znaków)\n**Stałe:** " + ", ".join(f"{t} ({len(t)})" for t in d["core"]) + "\n"
        md += "**Gatunkowe:** " + "; ".join(f"{k}: {a} ({len(a)}), {b} ({len(b)})" for k, (a, b) in d["spec"].items()) + "\n"
        md += "**Pula:** " + ", ".join(f"{t} ({len(t)})" for t in d["pool"]) + "\n"
        md += ("\n**Tagi powyżej 20 znaków (do skrócenia, nie obcinam):** " + ", ".join(f"{t} ({n})" for t, n in long_tags) + "\n") if long_tags else "\nWszystkie tagi mają do 20 znaków.\n"
        (ROOT / "templates" / f"tlumaczenie_{code}_plytka.md").write_text(md, encoding="utf-8")
        print(code, "najdłuższy tytuł", mx, "| tagi >20:", long_tags)
        # Sphynx test
        names_c = names[("kot", "R145")]
        sp = d["sp"]["kot"]
        f = lambda t: fill(t, sp, names_c)
        par = " ".join(f(x) for x in (d["A"][4], d["B"][2], d["C"][1]))
        body = par + "\n\n" + fill_block(d["fixed"], sp, names_c)
        # tags: 5 core + 2 species + the same 6 pool positions as the English test
        pick = [POOL_EN.index(x) for x in ("custom memorial", "grave decoration", "cemetery marker", "photo on ceramic", "headstone plaque", "in loving memory")]
        tags = d["core"] + list(d["spec"]["kot"]) + [d["pool"][i] for i in pick]
        title = f(d["titles"][0])
        out = f"# Tłumaczenie testowe {d['name']} (szkic do sprawdzenia): Sphynx, listing 678653467\n\nOdpowiada planowi angielskiemu (tytuł 1, A5 + B3 + C2). Wymaga kontroli osoby natywnej.\n\n## Tytuł ({len(title)} znaków)\n{title}\n\n## Opis\n```\n{body}\n```\n\n## Tagi ({len(tags)})\n" + ", ".join(f"{t} ({len(t)})" for t in tags) + f"\n\n## Shopping basket summary\n{d['basket']}\n"
        (ROOT / "plans" / f"test_sfinks_678653467_{code.upper()}.md").write_text(out, encoding="utf-8")


def fill_block(t, sp, b):
    for k, v in sp.items():
        t = t.replace("{" + k + "}", v)
    return t.replace("{B}", b)


if __name__ == "__main__":
    main()
