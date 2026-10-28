#!/usr/bin/env python3
"""Mapa ofert urn z płytką "with a Photo" na foldery wideo (IV tura): plans/urny_mapa.csv. Tylko odczyt.
Dopasowanie po rasie z Rasy.xlsx (ta sama logika co build_map.py). Rasy z kilkoma ofertami lub folderami zostają do rozstrzygnięcia.
Użycie: python3 -I scripts/map_urny.py
"""
import csv
import html
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_map as bm

ROOT = bm.ROOT
PH = re.compile(r"\burn\b.*photo on a ceramic plaque", re.I)
SP_ROOT = {"091": "pies", "097": "kot", "098": "koń"}


def main():
    breeds, alias = bm.load_rasy()
    offers = []
    for r in csv.DictReader(open(ROOT / "plans" / "listing_ids_sklep.csv", encoding="utf-8")):
        t = html.unescape(r["title"])
        if PH.search(t) and not re.search(r"graphic", t, re.I):
            m = re.match(r"(.*?)\s+Urn for (Dog|Cat|Horse) Ashes", t, re.I)
            if m:
                offers.append({"lid": r["listing_id"], "breed": m.group(1).strip(), "sp": {"dog": "pies", "cat": "kot", "horse": "koń"}[m.group(2).lower()]})
    folders = list(csv.DictReader(open(ROOT / "plans" / "urny_foldery_index.csv", encoding="utf-8")))
    print("ofert:", len(offers), "| folderów:", len(folders))
    by_rid = defaultdict(lambda: {"o": [], "f": []})
    unres = {"o": [], "f": []}
    for o in offers:
        hits, how = bm.lookup(o["breed"], o["sp"], alias)
        if len(hits) == 1:
            by_rid[next(iter(hits))]["o"].append((o, how))
        else:
            unres["o"].append((o["lid"], o["breed"], o["sp"], sorted(hits)))
    for f in folders:
        sp = SP_ROOT[f["korzen"][:3]]
        hits, how = bm.lookup(f["nazwa_z_folderu"], sp, alias)
        if len(hits) == 1:
            by_rid[next(iter(hits))]["f"].append((f, how))
        else:
            unres["f"].append((f["nazwa_z_folderu"], sp, sorted(hits)))
    out, status = [], {"1:1": 0, "wiele": 0, "brak folderu": 0, "brak oferty": 0}
    for (sp, rid), d in sorted(by_rid.items()):
        no, nf = len(d["o"]), len(d["f"])
        st = "1:1" if no == 1 and nf == 1 else ("brak folderu" if nf == 0 else ("brak oferty" if no == 0 else "wiele"))
        status[st] += 1
        for o, how in d["o"] or [(None, "")]:
            for f, how2 in d["f"] or [(None, "")]:
                if st != "wiele" or True:
                    out.append([sp, rid, breeds[(sp, rid)], o["lid"] if o else "", o["breed"] if o else "", f["korzen"][:3] if f else "", f["folder"] if f else "",
                                f["ean"] if f else "", st, how if o else "", how2 if f else ""])
    with open(ROOT / "plans" / "urny_mapa.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["gatunek", "rasa_id", "rasa_kolumna_C", "listing_id", "nazwa_w_tytule", "korzen", "folder", "ean", "status", "dopasowanie_oferty", "dopasowanie_folderu"])
        w.writerows(out)
    print("rasy:", len(by_rid), status)
    print("nierozpoznane oferty:", len(unres["o"]), unres["o"][:20])
    print("nierozpoznane foldery:", len(unres["f"]), unres["f"][:20])
    fz = [r for r in out if r[8] == "wiele"]
    print("rasy z wieloma ofertami/folderami:", sorted({(r[2], ) for r in fz}))
    fuzzy = [r for r in out if "fuzzy" in r[9] or "fuzzy" in r[10]]
    print("dopasowania rozmyte (do sprawdzenia):", len(fuzzy), [(r[4], r[6][:30], r[9][:25], r[10][:25]) for r in fuzzy][:15])


if __name__ == "__main__":
    main()
