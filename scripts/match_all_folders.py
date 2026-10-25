#!/usr/bin/env python3
"""Compare chosen offers (by source id) with 1.jpg of ALL server folders of the same species. Read only.
Usage: python3 -I scripts/match_all_folders.py <source> [<source> ...]   e.g. EtsyListingsDownload.csv:65
"""
import csv
import io
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import match_by_image as mbi

ROOT = mbi.ROOT
SP = {"194": "koń", "195": "kot", "196": "pies"}


def main():
    mp = {r["zrodlo"]: r for r in csv.DictReader(open(ROOT / "plans" / "mapa_plytki_with_photo.csv", encoding="utf-8"))}
    idx = list(csv.DictReader(open(ROOT / "plans" / "folders_index.csv", encoding="utf-8")))
    src = {}
    for fn in ("EtsyListingsDownload.csv", "EtsyListingsDownload1.csv"):
        for i, r in enumerate(csv.DictReader(open(ROOT / "data" / fn, encoding="utf-8-sig")), start=2):
            src[f"{fn}:{i}"] = r["IMAGE1"]
    need = {}
    for s in sys.argv[1:]:
        sp = mp[s]["gatunek"]
        for f in idx:
            if SP[f["species_folder"][:3]] == sp:
                need[f["ean"]] = f
    def dl(ean):
        p = mbi.CACHE / f"{ean}-1.jpg"
        if not p.exists():
            p.write_bytes(mbi.get(mbi.PHOTOS + ean + "/1.jpg"))
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(dl, list(need)))
    for s in sys.argv[1:]:
        v = mbi.vec(Image.open(io.BytesIO(mbi.get(src[s].replace("il_fullxfull", "il_340x270")))))
        sc = []
        for f in idx:
            if SP[f["species_folder"][:3]] == mp[s]["gatunek"]:
                sc.append((float(v @ mbi.vec(Image.open(mbi.CACHE / f"{f['ean']}-1.jpg"))), f["breed_folder"]))
        sc.sort(reverse=True)
        print(s, mp[s]["nazwa_w_tytule"], "->", [(round(a, 3), b) for a, b in sc[:3]])


if __name__ == "__main__":
    main()
