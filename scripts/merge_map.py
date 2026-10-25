#!/usr/bin/env python3
"""Merge name-based and image-based matches into plans/mapa_koncowa.csv (one row per offer). Read only.
Usage: python3 -I scripts/merge_map.py
"""
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# offers whose folder was found by comparing with ALL folders of the species (scripts/match_all_folders.py)
ALL_FOLDERS = {
    "EtsyListingsDownload.csv:131": ("198 Brittany spaniel 5055882489431", "TYTUŁ NIE PASUJE DO ZDJĘCIA: obraz oferty odpowiada folderowi Brittany spaniel"),
    "EtsyListingsDownload.csv:65": ("", "brak pasującego folderu (najlepszy wynik bez przewagi)"),
    "EtsyListingsDownload.csv:139": ("", "brak pasującego folderu (najlepszy wynik bez przewagi)"),
}


# Owner's decisions (25.10.2026): name used in the offer title -> column C of Rasy.xlsx
NAME_TO_C = {"Akita Inu": "Akita", "Russian Tsvetnaya Bolonka": "Bolonka", "Catahoula Cur": "Catahoula Leopard Dog",
             "Laekenois Dog": "Laekenois Belgian Shepherd", "Scottish Deerhound": "Deerhound",
             "Pyrenean Shepherd": "Pyrenean Sheepdog", "Schnauzer Cropped": "Schnauzer", "Jagdterrier": "Jagdterrier",
             "Percheron": "Percheron", "German pointer": "German Pointer", "Vizsla": "Vizsla", "Basset Hound": "Basset Hound",
             "Tosa Inu": "Tosa Inu"}
# offers to skip: no matching folder (Clydesdale #1, Laekenois #1)
SKIP = {"EtsyListingsDownload.csv:65": "POMIŃ: brak pasującego folderu", "EtsyListingsDownload.csv:139": "POMIŃ: brak pasującego folderu"}
# the title says Fox Terrier, the picture is Brittany Spaniel: the offer is optimised as Brittany Spaniel
SOURCE_TO_C = {"EtsyListingsDownload.csv:131": "Brittany Spaniel"}


def load_ids():
    import openpyxl
    ws = openpyxl.load_workbook(ROOT / "data" / "Rasy.xlsx", data_only=True)["Rasy"]
    return {(r[1], r[2]): r[0] for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}


def main():
    ids = load_ids()
    rows = list(csv.DictReader(open(ROOT / "plans" / "mapa_plytki_with_photo.csv", encoding="utf-8")))
    img = {r["zrodlo"]: r for r in csv.DictReader(open(ROOT / "plans" / "mapa_obrazy.csv", encoding="utf-8"))}
    unr = {r["zrodlo"]: r for r in csv.DictReader(open(ROOT / "plans" / "mapa_nierozstrzygniete.csv", encoding="utf-8"))}
    out = []
    for r in rows:
        z = r["zrodlo"]
        o = {"zrodlo": z, "gatunek": r["gatunek"], "nazwa_w_tytule": r["nazwa_w_tytule"], "rasa_kolumna_C": r["rasa_kolumna_C"],
             "folder": r["folder"], "metoda": "nazwa" if r["folder"] else "", "przewaga": "", "do_decyzji": "", "tytul": r["tytul"], "rasa_id": "", "decyzja": ""}
        if z in img:
            o.update(folder=img[z]["folder_najlepszy"], metoda="obraz (pary)", przewaga=img[z]["przewaga"])
            if float(img[z]["przewaga"]) < 0.1:
                o["do_decyzji"] = "mała przewaga, potwierdź parę"
        elif z in ALL_FOLDERS:
            o.update(folder=ALL_FOLDERS[z][0], metoda="obraz (wszystkie foldery)", do_decyzji=ALL_FOLDERS[z][1])
        elif z in unr:
            u = unr[z]
            o.update(folder=u["najlepszy_folder"], metoda="obraz (wolne foldery)", przewaga=u["przewaga"])
            o["do_decyzji"] = "potwierdź" if not r["rasa_kolumna_C"] else ""
        if not o["rasa_kolumna_C"]:
            o["do_decyzji"] = (o["do_decyzji"] + "; " if o["do_decyzji"] else "") + "rasa bez wiersza w Rasy.xlsx"
        if r["status"] == "BRAK ZDJĘĆ":
            o["do_decyzji"] += "; brak zdjęć w folderze"
        c = SOURCE_TO_C.get(z) or o["rasa_kolumna_C"] or NAME_TO_C.get(o["nazwa_w_tytule"], "")
        o["rasa_kolumna_C"] = c
        o["rasa_id"] = ids.get((o["gatunek"], c), "")
        o["decyzja"] = "OPTYMALIZUJ"
        if z in SKIP:
            o["decyzja"] = SKIP[z]
        out.append(o)
    seen = {}
    for o in out:  # duplicate offers sharing one folder (Bengal): optimise only the first
        if o["decyzja"] == "OPTYMALIZUJ" and o["nazwa_w_tytule"] == "Bengal":
            if o["folder"] in seen:
                o["decyzja"] = "POMIŃ: duplikat oferty " + seen[o["folder"]]
            else:
                seen[o["folder"]] = o["zrodlo"]
    for o in out:
        if o["decyzja"] == "OPTYMALIZUJ":
            o["do_decyzji"] = ""  # all open points were settled by the owner
    with open(ROOT / "plans" / "mapa_koncowa.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    used = {o["folder"] for o in out if o["folder"]}
    idx = list(csv.DictReader(open(ROOT / "plans" / "folders_index.csv", encoding="utf-8")))
    free = [f["breed_folder"] for f in idx if f["breed_folder"] not in used]
    print(Counter(o["decyzja"] for o in out))
    print("ofert:", len(out), "| bez folderu:", sum(1 for o in out if not o["folder"]),
          "| do decyzji:", sum(1 for o in out if o["do_decyzji"]), "| folderów bez oferty:", len(free))
    print("foldery bez oferty:", "; ".join(free))
    print(Counter(o["metoda"] for o in out))


if __name__ == "__main__":
    main()
