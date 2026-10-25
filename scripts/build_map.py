#!/usr/bin/env python3
"""Match the 302 'with a Photo' plaque listings from the Etsy export to server folders (EAN) via Rasy.xlsx.

Input : data/Rasy.xlsx, data/EtsyListingsDownload*.csv, plans/folders_index.csv (scripts/crawl_folders.py)
Output: plans/mapa_plytki_with_photo.csv, one row per listing, with a status and notes for the owner.
Nothing is sent to Etsy. Usage: python3 -I scripts/build_map.py
"""
import csv
import difflib
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
NEEDED = ["3.jpg", "4.jpg", "5.jpg", "2.jpg", "6.jpg", "7.jpg"]
SPECIES = {"194": "koń", "195": "kot", "196": "pies"}
NOISE = re.compile(r"\b(dog|cat|horse)\b$")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def strip_noise(s):
    s = norm(s)
    return NOISE.sub("", s).strip()


def load_rasy():
    wb = openpyxl.load_workbook(ROOT / "data" / "Rasy.xlsx", data_only=True)
    ws = wb["Rasy"]
    breeds, alias = {}, defaultdict(set)  # alias: normalized name -> {(species, rasa_id)}
    for r in ws.iter_rows(min_row=2, values_only=True):
        rid, sp, c = r[0], r[1], r[2]
        if not rid or sp not in ("pies", "kot", "koń"):
            continue
        breeds[(sp, rid)] = c
        names = [c, r[3], r[4], r[9], r[10], r[12], r[14], r[16], r[18], r[20], r[22], r[24]]
        for v in names:
            for part in str(v or "").split(","):
                for form in (norm(part), strip_noise(part)):
                    if form:
                        alias[form].add((sp, rid))
        for part in str(r[8] or "").split(";"):  # 'Zapisy w tytułach ofert (z eksportu)', e.g. 'Labrador (2)'
            part = re.sub(r"\(\d+\)\s*$", "", part).strip()
            for form in (norm(part), strip_noise(part)):
                if form:
                    alias[form].add((sp, rid))
    canon_ids = {c: (sp, rid) for (sp, rid), c in breeds.items()}
    wv = wb["Warianty w tytułach"]
    for r in wv.iter_rows(min_row=2, values_only=True):
        variants, canon = r[1], r[2]
        if not canon:
            continue
        key = next((k for k in breeds if breeds[k] == canon), None)
        if not key:
            continue
        for part in str(variants).split(","):
            for form in (norm(part), strip_noise(part)):
                if form:
                    alias[form].add(key)
    return breeds, alias


def load_listings():
    rows = []
    for f in ("EtsyListingsDownload.csv", "EtsyListingsDownload1.csv"):
        for i, r in enumerate(csv.DictReader(open(ROOT / "data" / f, encoding="utf-8-sig")), start=2):
            t = r["TITLE"].lower()
            if ("plaque" in t or "plate" in t or "tile" in t) and "urn" not in t and "statue" not in t \
                    and r["MATERIALS"].lower().strip() == "ceramic plate" and "photo" in t:
                r["_src"] = f"{f}:{i}"
                rows.append(r)
    return rows


def species_of(title):
    m = re.search(r"Photo of a (Dog|Cat|Horse)", title)
    return {"Dog": "pies", "Cat": "kot", "Horse": "koń"}.get(m.group(1)) if m else None


def breed_in_title(title):
    return re.split(r"\s+(?:Tombstone Plaque|Ceramic Plaque|Memorial Plaque|Plaque)\b", title, maxsplit=1)[0].strip()


def lookup(name, sp, alias):
    for form in (norm(name), strip_noise(name)):
        hits = {k for k in alias.get(form, ()) if k[0] == sp}
        if hits:
            return hits, "exact"
    forms = [k for k in alias if any(h[0] == sp for h in alias[k])]
    best = difflib.get_close_matches(strip_noise(name), forms, n=1, cutoff=0.85)
    if best:
        return {k for k in alias[best[0]] if k[0] == sp}, f"fuzzy:{best[0]}"
    return set(), "none"


def main():
    breeds, alias = load_rasy()
    idx = list(csv.DictReader(open(ROOT / "plans" / "folders_index.csv", encoding="utf-8")))
    by_breed = defaultdict(list)  # (sp, rid) -> folder rows
    folder_status = {}
    for f in idx:
        sp = SPECIES.get(f["species_folder"][:3])
        name = re.sub(r"^\d+\.?\s*", "", f["breed_folder"])
        name = re.sub(r"\s*\d{13}$", "", name)
        hits, how = lookup(name, sp, alias)
        f["_name"], f["_how"] = name, how
        if len(hits) == 1:
            by_breed[next(iter(hits))].append(f)
        folder_status[f["breed_folder"]] = (sorted(breeds[h] for h in hits), how)

    out = []
    used = set()
    for r in load_listings():
        title = r["TITLE"]
        sp = species_of(title)
        raw = breed_in_title(title)
        hits, how = lookup(raw, sp, alias) if sp else (set(), "none")
        notes = []
        status, canon, rid, folder, ean = "OK", "", "", "", ""
        if how.startswith("fuzzy"):
            notes.append(f"dopasowanie przybliżone ({how})")
        if len(hits) != 1:
            status = "BRAK RASY W RASY.XLSX" if not hits else "NIEJEDNOZNACZNA RASA"
            if hits:
                notes.append("kilka możliwych: " + ", ".join(sorted(breeds[h] for h in hits)))
        else:
            key = next(iter(hits))
            canon, rid = breeds[key], key[1]
            fs = by_breed.get(key, [])
            if not fs:
                status = "BRAK FOLDERU"
            elif len(fs) > 1:
                status = "WIELE FOLDERÓW"
                notes.append("foldery: " + "; ".join(f["breed_folder"] for f in fs))
            else:
                f = fs[0]
                folder, ean = f["breed_folder"], f["ean"]
                used.add(f["breed_folder"])
                photos = f["photos"].split("|") if f["photos"] else []
                missing = [n for n in NEEDED if n not in photos]
                if missing:
                    status = "BRAK ZDJĘĆ"
                    notes.append("brakuje: " + ", ".join(missing))
                if not f["videos"]:
                    notes.append("folder bez wideo")
        out.append({"zrodlo": r["_src"], "gatunek": sp or "", "nazwa_w_tytule": raw, "rasa_id": rid,
                    "rasa_kolumna_C": canon, "status": status, "folder": folder, "ean": ean,
                    "uwagi": "; ".join(notes), "tytul": title})

    # duplicates: two listings pointing to the same folder (e.g. smooth / long-haired varieties)
    cnt = defaultdict(int)
    for o in out:
        if o["ean"]:
            cnt[o["ean"]] += 1
    for o in out:
        if o["ean"] and cnt[o["ean"]] > 1:
            o["uwagi"] = (o["uwagi"] + "; " if o["uwagi"] else "") + f"ten sam folder dla {cnt[o['ean']]} ofert"
            if o["status"] == "OK":
                o["status"] = "DO SPRAWDZENIA (ten sam folder)"

    path = ROOT / "plans" / "mapa_plytki_with_photo.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    unused = [f for f in idx if f["breed_folder"] not in used]
    with open(ROOT / "plans" / "foldery_bez_oferty.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["folder", "ean", "dopasowana_rasa_w_Rasy", "jak"])
        for f in unused:
            nm, how = folder_status[f["breed_folder"]]
            w.writerow([f["species_folder"] + "/" + f["breed_folder"], f["ean"], "; ".join(nm), how])
    from collections import Counter
    print(Counter(o["status"] for o in out))
    print("folderów bez oferty:", len(unused), "z", len(idx))


if __name__ == "__main__":
    main()
