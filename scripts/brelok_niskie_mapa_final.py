#!/usr/bin/env python3
"""Mapa końcowa niskiej urny z małą posrebrzaną płaskorzeźbą: plans/brelok_niskie_mapa_obraz.csv + decyzje (plans/brelok_niskie_decyzje.json).
Nazwy ras przez Rasy.xlsx; ustalenia po nazwie jak w wysokiej urnie. Bez zapytań do Etsy. Wynik: plans/brelok_niskie_mapa_final.csv.
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
# ustalenia właścicielki (31.10-01.11.2026): nazwa w ofercie -> (ID rasy w Rasy.xlsx, klucz odmiany, nazwa EN w tytule)
BY_NAME = {
    "Basset Vendeen": ("R127", "", ""), "Soft-coated Wheatan Terrier": ("R076", "", ""), "York Terrier": ("R111", "", ""), "Grey Hound": ("R088", "", ""),
    "Japan Chin": ("R129", "", ""), "Silky Terrier": ("R235", "", ""), "Neapolitan Mastiff, Mastino Napoletano": ("R048", "", ""), "Hungarian vizsla": ("R093", "", ""),
    "Dachshund wirehaired": ("R025", "Dachshund Wire-haired", ""), "Dachshund smooth haired": ("R025", "Dachshund Smooth-haired", ""),
    "American Staffordshire Terrier Amstaff": ("R027", "", ""), "Chihuahua smooth haired": ("R039", "", ""),  # Chihuahua smooth haired: bez słowa odmiany (jak w wysokiej urnie), do potwierdzenia
    "Collie Smooth Haired": ("R059", "Collie Smooth", ""), "Rough Collie": ("R059", "Collie Rough", "Rough Collie"), "Ibizan Hound wirehaired": ("R134", "Dachshund Wire-haired", ""),
}
SAME_ALL = {"Lagotto Romagnolo", "Spitz", "Bobtail"}  # nazwa bez tłumaczeń we wszystkich językach
SYN_EN = {"Bobtail": "Old English Sheepdog"}


def main():
    dec = json.load(open(ROOT / "plans" / "brelok_niskie_decyzje.json", encoding="utf-8"))
    idx = {x["folder"].split(".")[0]: x["folder"] for x in csv.DictReader(open(ROOT / "plans" / "brelok_niskie_foldery_index.csv", encoding="utf-8"))}
    obraz = list(csv.DictReader(open(ROOT / "plans" / "brelok_niskie_mapa_obraz.csv", encoding="utf-8")))
    nm = {int(r["listing_id"]): r for r in csv.DictReader(open(ROOT / "plans" / "brelok_niskie_mapa.csv", encoding="utf-8"))}
    R = B.rasy()
    fw = B.feature_words()
    pm, by_c = U.breed_lookup(R)
    rows = []
    for o in obraz:
        lid = int(o["listing_id"])
        sp = nm[lid]["gatunek"]
        name = dec["podpis_rasy_reczny"].get(str(lid), o["nazwa_w_tytule"])
        name = re.sub(r" \(.*\)$", "", name)
        folder = idx[str(dec["folder_reczny"][str(lid)])] if str(lid) in dec["folder_reczny"] else o["folder"]
        film2 = "nie" if lid in dec["bez_filmu_2"] else "tak"
        why, rid, key, breed_en = [], "", "", ""
        if name in BY_NAME:
            rid, key, breed_en = BY_NAME[name]
        elif name in SAME_ALL:
            pass
        else:
            row = {"gatunek": sp, "nazwa_w_tytule": name, "folder": folder}
            rid, key, w2 = U.resolve(row, R, fw, pm, by_c)
            why += list(w2)
            rid = rid or ""
        if key and key not in fw:
            why.append("odmiana bez słowa: " + key)
        if not rid and name not in SAME_ALL:
            why.append("rasa nierozpoznana: " + name)
        rows.append({"listing_id": lid, "wyswietlenia": o["wyswietlenia"], "gatunek": sp, "nazwa_w_tytule": name, "rasa_id": rid, "rasa_xlsx": R[(sp, rid)]["Nazwa EN (główna)"] if rid else "",
                     "odmiana": key, "folder": folder, "film_2": film2, "nazwa_stala": "tak" if name in SAME_ALL else "", "syn_en": SYN_EN.get(name, ""), "breed_en": breed_en,
                     "uwagi": "; ".join(why)})
    out = ROOT / "plans" / "brelok_niskie_mapa_final.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: int(r["wyswietlenia"])))
    bad = [r for r in rows if r["uwagi"]]
    used = {}
    for r in rows:
        if r["film_2"] == "tak":
            used.setdefault(r["folder"], []).append(r["listing_id"])
    print("ofert:", len(rows), "| bez filmu 2:", sum(r["film_2"] == "nie" for r in rows), "| z uwagami:", len(bad), "| foldery użyte >1:", {k: v for k, v in used.items() if len(v) > 1})
    for r in bad:
        print(" -", r["listing_id"], r["nazwa_w_tytule"], "|", r["uwagi"])
    print("odmiany:", [(r["listing_id"], r["nazwa_w_tytule"], r["odmiana"]) for r in rows if r["odmiana"]])


if __name__ == "__main__":
    main()
