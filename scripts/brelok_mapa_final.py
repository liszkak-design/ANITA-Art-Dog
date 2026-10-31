#!/usr/bin/env python3
"""Mapa końcowa grupy "urna z małą posrebrzaną płaskorzeźbą": plans/brelok_mapa_obraz.csv + decyzje właścicielki (plans/brelok_decyzje.json),
nazwy ras przez Rasy.xlsx (jak w pozostałych grupach). Bez zapytań do Etsy. Wynik: plans/brelok_mapa_final.csv + lista otwartych spraw.
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch as B
import batch_urny as U

ROOT = B.ROOT


def main():
    dec = json.load(open(ROOT / "plans" / "brelok_decyzje.json", encoding="utf-8"))
    stan = json.load(open(ROOT / "plans" / "brelok_stan_zywy.json", encoding="utf-8"))
    obraz = {int(r["listing_id"]): r for r in csv.DictReader(open(ROOT / "plans" / "brelok_mapa_obraz.csv", encoding="utf-8"))}
    nm = {int(r["listing_id"]): r for r in csv.DictReader(open(ROOT / "plans" / "brelok_mapa.csv", encoding="utf-8"))}
    R = B.rasy()
    fw = B.feature_words()
    pm, by_c = U.breed_lookup(R)
    skip = set(dec["oferta_usunieta_przez_wlascicielke"]) | set(dec["pominiete_big_horse"])
    rows = []
    for lid, o in obraz.items():
        if lid in skip:
            continue
        sp = nm[lid]["gatunek"]
        name = dec["podpis_rasy_reczny"].get(str(lid), o["nazwa_w_tytule"])
        folder = dec["folder_reczny"].get(str(lid), o["folder"])
        row = {"gatunek": sp, "nazwa_w_tytule": name, "folder": folder}
        rid, key, why = U.resolve(row, R, fw, pm, by_c)
        why = list(why)
        if key and key not in fw:
            why.append("odmiana bez słowa w 'Słowa stałe': " + key)
        rows.append({"listing_id": lid, "wyswietlenia": o["wyswietlenia"], "gatunek": sp, "nazwa_w_tytule": name, "rasa_id": rid or "",
                     "rasa_xlsx": R[(sp, rid)]["Nazwa EN (główna)"] if rid else "", "odmiana": key, "folder": folder, "film_2": "nie" if lid in dec["bez_filmu_2"] else "tak",
                     "uwagi": "; ".join(why)})
    out = ROOT / "plans" / "brelok_mapa_final.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: int(r["wyswietlenia"])))
    bad = [r for r in rows if r["uwagi"]]
    print("ofert:", len(rows), "| gatunki:", {g: sum(1 for r in rows if r["gatunek"] == g) for g in ("pies", "kot", "koń")}, "| bez filmu 2:", sum(r["film_2"] == "nie" for r in rows), "| z uwagami:", len(bad))
    for r in bad:
        print(" -", r["listing_id"], r["nazwa_w_tytule"], "|", r["uwagi"])
    print("odmiany:", [(r["listing_id"], r["nazwa_w_tytule"], r["odmiana"]) for r in rows if r["odmiana"]])


if __name__ == "__main__":
    main()
