#!/usr/bin/env python3
"""Mapa 38 ofert "plakietki same" -> EAN (arkusz wymiarów) -> folder 219. Dopasowanie po rasie i wymiarach odczytanych ze zdjęcia 3 oferty
(szerokość = pierwsza wartość, wysokość = druga; w arkuszu kolumny są zamienione: "Height" = szerokość, "Width" = wysokość; potwierdzone przez właścicielkę 02.11.2026).
Odczyty ze zdjęć 3 wpisane ręcznie z arkuszy kontrolnych (plans/plakietki_kontrola). Bez zapytań do Etsy. Wynik: plans/plakietki_mapa.csv.
"""
import csv
import json
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
READ = {  # listing_id: (szerokość, wysokość) ze zdjęcia 3 oferty
    1366902842: (10, 12.5), 1380892321: (12.5, 12), 1380895791: (11.5, 14), 1380884619: (15, 13), 1366903722: (11.5, 14), 1380896375: (6.5, 7.5),
    1366889402: (12.5, 12), 1380882665: (7, 6.5), 1366889026: (11, 10.5), 1380885299: (13, 12), 1380895381: (12, 12.5), 1366900894: (16, 12.5),
    1380897399: (12, 15), 1380884233: (11, 13), 1366889778: (7, 8), 1366885786: (7.5, 7.5), 1366886450: (10, 14.5), 1366886094: (7, 8),
    1380882347: (11, 16), 1380882099: (6.5, 10), 1366900154: (12, 12), 1366886840: (7.5, 9), 1380881483: (13, 15), 1380896583: (9, 8.5),
    1366904132: (15, 11.5), 1366887678: (8, 7), 1380879147: (12, 16), 1380875733: (7, 10), 1380894471: (12, 12), 1380895031: (13, 13),
    1380879511: (8, 9), 1380891835: (14, 13), 1380892897: (7.5, 6.5), 1366902014: (8, 8), 1362333074: (7, 8.5), 1380884945: (10, 13),
    1380893289: (14.5, 13), 1380893741: (13, 10)}
import unicodedata
NORM = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s.lower().replace("ł", "l")).encode("ascii", "ignore").decode())
ALIAS = {"staffordshirebullterrier": "staffordshirebullterrier", "americanstaffordshireterrier": "amerykanskistaffordshireterrier", "boxer": "bokser", "bulldog": "bulldog",
         "dachshund": "jamnikszorstkowlosy", "frenchbulldog": "buldogfrancuski", "germanshepherd": "owczarekniemiecki", "greatdane": "dogniemiecki", "irishwolfhound": "wilczarzirlandzki",
         "mastinonapoletano": "mastifneapolitanski", "shapei": "sharpei", "saintbernard": "bernardyn", "bullterrier": "bulterier", "dogue": "dogzbordeaux", "borzoi": "chartrosyjski",
         "newfoundland": "nowofundland", "englishcockerspaniel": "cockerspanielangielski", "afghanhound": "chartafganski", "presacanario": "presacanario", "filabrasileiro": "filabrasileiro",
         "bullmastiff": "bullmastiff", "chowchow": "chowchow", "goldenretriever": "goldenretriever", "hovawart": "hovawart", "rottweiler": "rottweiler", "schnauzer": "sznaucer",
         "bassethound": "bassethound", "weimaraner": "wyzelweimarski", "sharpei": "sharpei"}


def main():
    stan = json.load(open(ROOT / "plans" / "plakietki_stan_zywy.json", encoding="utf-8"))
    wb = openpyxl.load_workbook(ROOT / "data" / "plakietki_wymiary.xlsx", data_only=True)
    xl = [(str(r[0]).strip(), str(r[1]), r[2], r[3], r[4]) for r in list(wb.active.iter_rows(values_only=True))[1:]]  # (nazwa, ean, kol_pierwsza=SZER, kol_druga=WYS, grubosc)
    fol = {x["ean"]: x["folder"] for x in csv.DictReader(open(ROOT / "plans" / "plakietki_foldery_index.csv", encoding="utf-8"))}
    rows, used = [], {}
    for lid, (w, h) in READ.items():
        title = stan[str(lid)]["title"].split(" Bust")[0]
        key = NORM(title)
        cand = [r for r in xl if (key in NORM(r[0]) or NORM(title.split()[0]) in NORM(r[0]) or (ALIAS.get(key) and NORM(ALIAS[key]) in NORM(r[0])))]
        exact = [r for r in cand if (r[2], r[3]) == (w, h)]
        note = ""
        if len(exact) == 1:
            r = exact[0]
        elif lid == 1366902842:  # Afghan Hound: szerokość 10 ze zdjęcia (decyzja właścicielki), wysokość 12,5 zgodna
            r = [x for x in xl if x[1] == "5060383449112"][0]
            note = "szerokość 10 ze zdjęcia (arkusz 9), decyzja właścicielki"
        elif lid == 1380892897:  # Rottweiler mały: zdjęcie 7,5 x 6,5, arkusz 12,5 x 12 (błąd)
            r = [x for x in xl if x[1] == "5060383448993"][0]
            note = "arkusz podaje 12,5 x 12 (błąd), zdjęcie 7,5 x 6,5; grubość nieznana, do potwierdzenia"
        else:
            r, note = None, f"brak jednoznacznego dopasowania ({len(exact)} wierszy z {len(cand)} kandydatów)"
        ean = r[1] if r else ""
        if ean:
            used.setdefault(ean, []).append(lid)
        rows.append({"listing_id": lid, "wyswietlenia": stan[str(lid)]["views"], "rasa_w_tytule": title, "szerokosc_zdjecie": w, "wysokosc_zdjecie": h, "ean": ean,
                     "nazwa_arkusz": r[0] if r else "", "szerokosc_arkusz": r[2] if r else "", "wysokosc_arkusz": r[3] if r else "", "grubosc_arkusz": r[4] if r else "",
                     "folder": fol.get(ean, ""), "uwagi": note})
    for r in rows:
        if r["ean"] and len(used[r["ean"]]) > 1:
            r["uwagi"] = (r["uwagi"] + "; " if r["uwagi"] else "") + "EAN użyty przez kilka ofert: " + ",".join(map(str, used[r["ean"]]))
    out = ROOT / "plans" / "plakietki_mapa.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: -int(r["wyswietlenia"])))
    eans = {r[1] for r in xl}
    print("ofert:", len(rows), "| bez dopasowania:", [r["listing_id"] for r in rows if not r["ean"]], "| EAN bez oferty:", sorted(eans - set(used)),
          "| EAN z >1 ofertą:", {k: v for k, v in used.items() if len(v) > 1})
    for r in rows:
        if r["uwagi"]:
            print(" -", r["listing_id"], r["rasa_w_tytule"], r["uwagi"])


if __name__ == "__main__":
    main()
