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


def main():
    rows = list(csv.DictReader(open(ROOT / "plans" / "mapa_plytki_with_photo.csv", encoding="utf-8")))
    img = {r["zrodlo"]: r for r in csv.DictReader(open(ROOT / "plans" / "mapa_obrazy.csv", encoding="utf-8"))}
    unr = {r["zrodlo"]: r for r in csv.DictReader(open(ROOT / "plans" / "mapa_nierozstrzygniete.csv", encoding="utf-8"))}
    out = []
    for r in rows:
        z = r["zrodlo"]
        o = {"zrodlo": z, "gatunek": r["gatunek"], "nazwa_w_tytule": r["nazwa_w_tytule"], "rasa_kolumna_C": r["rasa_kolumna_C"],
             "folder": r["folder"], "metoda": "nazwa" if r["folder"] else "", "przewaga": "", "do_decyzji": "", "tytul": r["tytul"]}
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
        out.append(o)
    with open(ROOT / "plans" / "mapa_koncowa.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    used = {o["folder"] for o in out if o["folder"]}
    idx = list(csv.DictReader(open(ROOT / "plans" / "folders_index.csv", encoding="utf-8")))
    free = [f["breed_folder"] for f in idx if f["breed_folder"] not in used]
    print("ofert:", len(out), "| bez folderu:", sum(1 for o in out if not o["folder"]),
          "| do decyzji:", sum(1 for o in out if o["do_decyzji"]), "| folderów bez oferty:", len(free))
    print("foldery bez oferty:", "; ".join(free))
    print(Counter(o["metoda"] for o in out))


if __name__ == "__main__":
    main()
