#!/usr/bin/env python3
"""Mapowanie ofert (plans/brelok_stan_zywy.json) na foldery serwera 089 (plans/brelok_foldery_index.csv) po nazwie rasy (bez zapytań do Etsy).
Nazwa folderu i tytuł oferty są sprowadzane do rasy z Rasy.xlsx (wszystkie kolumny nazw językowych). Wynik: plans/brelok_mapa.csv.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch as B
import batch_urny as U

ROOT = B.ROOT
SKIP = {1381486535, 1381486029}  # "Big Urn for Horse" (199 EUR): pominięte (decyzja 31.10.2026)
NAME_FIX = {"Borzoi Russian Wolfhound": "Borzoi", "Mastino Napoletano": "Neapolitan Mastiff", "Staffordshire Bullterrier": "Staffordshire Bull Terrier"}
SPECIES_OF = lambda t: "kot" if " Urn for Cat" in t else ("koń" if " Urn for Horse" in t else "pies")


def breed(title):
    n = re.split(r" (?:Urn for|Big Urn for) ", title)[0].strip()
    return NAME_FIX.get(n, n)


def main():
    stan = json.load(open(ROOT / "plans" / "brelok_stan_zywy.json", encoding="utf-8"))
    folders = list(csv.DictReader(open(ROOT / "plans" / "brelok_foldery_index.csv", encoding="utf-8")))
    R = B.rasy()
    cols = [c for c in next(iter(R.values())).keys() if "nazwa" in c.lower()]
    alias = defaultdict(set)
    for (g, rid), v in R.items():
        for c in cols:
            if v.get(c):
                alias[U.norm(str(v[c]))].add((g, rid))
    pm, by_c = U.breed_lookup(R)
    rows, used = [], defaultdict(list)
    fol = []
    for f in folders:
        n = U.norm(f["nazwa"])
        rids = alias.get(n) or alias.get(U.norm(re.sub(r"\b(classical|cat|horse)\b", "", f["nazwa"], flags=re.I)))
        fol.append((f, rids or set()))
    for lid, st in stan.items():
        lid = int(lid)
        if lid in SKIP:
            continue
        sp = SPECIES_OF(st["title"])
        name = breed(st["title"])
        rid = by_c.get((sp, U.norm(name))) or pm.get((sp, U.norm(name)))
        cand = [f for f, rids in fol if rid and (sp, rid) in rids]
        why = []
        if not rid:
            why.append("rasa nierozpoznana: " + name)
        elif not cand:
            why.append("brak folderu o tej rasie")
        elif len(cand) > 1:
            why.append(f"{len(cand)} foldery tej rasy: " + " | ".join(c["folder"] for c in cand))
        rows.append({"listing_id": lid, "wyswietlenia": st["views"], "gatunek": sp, "nazwa_w_tytule": name, "rasa_id": rid or "", "rasa_xlsx": R[(sp, rid)]["Nazwa EN (główna)"] if rid else "",
                     "folder": cand[0]["folder"] if len(cand) >= 1 else "", "liczba_folderow": len(cand), "uwagi": "; ".join(why)})
        for c in cand:
            used[c["folder"]].append(lid)
    for r in rows:
        if r["folder"] and len(used[r["folder"]]) > 1:
            r["uwagi"] = (r["uwagi"] + "; " if r["uwagi"] else "") + "folder dla kilku ofert: " + ",".join(map(str, used[r["folder"]]))
    out = ROOT / "plans" / "brelok_mapa.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["wyswietlenia"]))
    bad = [r for r in rows if r["uwagi"]]
    print("ofert:", len(rows), "| bez uwag:", len(rows) - len(bad), "| z uwagami:", len(bad))
    for r in bad:
        print(" -", r["listing_id"], r["nazwa_w_tytule"], "|", r["uwagi"])


if __name__ == "__main__":
    main()
