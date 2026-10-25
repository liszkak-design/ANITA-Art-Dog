#!/usr/bin/env python3
"""For offers the name-based map could not settle, compare the current Etsy photo of the listing with
1.jpg of every server folder that no offer has claimed yet (plus the folder the offer already points to).
Read only. Writes plans/mapa_nierozstrzygniete.csv for the owner to confirm.
Usage: python3 -I scripts/match_unresolved.py
"""
import csv
import io
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import match_by_image as mbi

ROOT = mbi.ROOT
SP = {"194": "koń", "195": "kot", "196": "pies"}


def main():
    mbi.CACHE.mkdir(exist_ok=True)
    rows = list(csv.DictReader(open(ROOT / "plans" / "mapa_plytki_with_photo.csv", encoding="utf-8")))
    claimed = {r["folder"] for r in rows if r["folder"]}
    # folders chosen for offers resolved by image
    for r in csv.DictReader(open(ROOT / "plans" / "mapa_obrazy.csv", encoding="utf-8")):
        claimed.add(r["folder_najlepszy"])
    idx = list(csv.DictReader(open(ROOT / "plans" / "folders_index.csv", encoding="utf-8")))
    free = {}
    for f in idx:
        if f["breed_folder"] not in claimed:
            free.setdefault(SP[f["species_folder"][:3]], []).append(f)
    src = {}
    for fn in ("EtsyListingsDownload.csv", "EtsyListingsDownload1.csv"):
        for i, r in enumerate(csv.DictReader(open(ROOT / "data" / fn, encoding="utf-8-sig")), start=2):
            src[f"{fn}:{i}"] = r["IMAGE1"]
    todo = [r for r in rows if r["status"] in ("BRAK RASY W RASY.XLSX", "BRAK FOLDERU", "NIEJEDNOZNACZNA RASA")
            or r["status"].startswith("DO SPRAWDZENIA")]
    out = []
    for r in todo:
        cands = {f["breed_folder"]: f["ean"] for f in free.get(r["gatunek"], [])}
        if r["folder"]:
            cands[r["folder"]] = r["ean"]
        v = mbi.vec(Image.open(io.BytesIO(mbi.get(src[r["zrodlo"]].replace("il_fullxfull", "il_340x270")))))
        scores = {}
        for name, ean in cands.items():
            p = mbi.CACHE / f"{ean}-1.jpg"
            if not p.exists():
                p.write_bytes(mbi.get(mbi.PHOTOS + ean + "/1.jpg"))
            scores[name] = float(v @ mbi.vec(Image.open(p)))
        top = sorted(scores.items(), key=lambda kv: -kv[1])[:3]
        out.append({"zrodlo": r["zrodlo"], "gatunek": r["gatunek"], "nazwa_w_tytule": r["nazwa_w_tytule"],
                    "status_mapy": r["status"],
                    "najlepszy_folder": top[0][0], "wynik": round(top[0][1], 3),
                    "drugi_folder": top[1][0] if len(top) > 1 else "", "wynik_drugi": round(top[1][1], 3) if len(top) > 1 else "",
                    "przewaga": round(top[0][1] - top[1][1], 3) if len(top) > 1 else ""})
        print(r["nazwa_w_tytule"], "->", top[0][0], round(top[0][1], 3), "| 2.:", top[1][0] if len(top) > 1 else "-",
              round(top[1][1], 3) if len(top) > 1 else "")
    with open(ROOT / "plans" / "mapa_nierozstrzygniete.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
