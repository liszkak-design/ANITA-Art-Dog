#!/usr/bin/env python3
"""Resolve listings that match several server folders (e.g. cropped / natural ears) by comparing the
current Etsy photo of the listing with 1.jpg of each candidate folder. Read only, writes
plans/mapa_obrazy.csv with the best folder and the margin to the runner-up. The owner confirms the result.
Usage: python3 -I scripts/match_by_image.py
"""
import csv
import io
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path("/tmp/match_cache")
PHOTOS = "https://www.artdog.com.pl/allegro/zebraneEAN/"


def get(url, tries=6):
    for i in range(tries):
        r = subprocess.run(["curl", "-sS", "-m", "90", "-f", url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(1.5 * (i + 1))
    raise RuntimeError(url)


def vec(img):
    img = img.convert("L")
    w, h = img.size
    s = max(w, h)
    sq = Image.new("L", (s, s), 255)
    sq.paste(img, ((s - w) // 2, (s - h) // 2))
    a = np.asarray(sq.resize((48, 48), Image.LANCZOS), dtype=float).ravel()
    a -= a.mean()
    return a / (np.linalg.norm(a) or 1)


def main():
    CACHE.mkdir(exist_ok=True)
    rows = list(csv.DictReader(open(ROOT / "plans" / "mapa_plytki_with_photo.csv", encoding="utf-8")))
    src = {}
    for f in ("EtsyListingsDownload.csv", "EtsyListingsDownload1.csv"):
        for i, r in enumerate(csv.DictReader(open(ROOT / "data" / f, encoding="utf-8-sig")), start=2):
            src[f"{f}:{i}"] = r["IMAGE1"]
    idx = {r["breed_folder"]: r for r in csv.DictReader(open(ROOT / "plans" / "folders_index.csv", encoding="utf-8"))}
    out = []
    for r in rows:
        m = re.match(r"foldery: (.*)", r["uwagi"]) if r["status"] == "WIELE FOLDERÓW" else None
        if not m:
            continue
        cands = [c.strip() for c in m.group(1).split(";")]
        thumb = src[r["zrodlo"]].replace("il_fullxfull", "il_340x270")
        v = vec(Image.open(io.BytesIO(get(thumb))))
        scores = {}
        for c in cands:
            ean = re.search(r"(\d{13})$", c).group(1)
            p = CACHE / f"{ean}-1.jpg"
            if not p.exists():
                p.write_bytes(get(PHOTOS + ean + "/1.jpg"))
            scores[c] = float(v @ vec(Image.open(p)))
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        best, second = ranked[0], ranked[1]
        out.append({"zrodlo": r["zrodlo"], "nazwa_w_tytule": r["nazwa_w_tytule"], "folder_najlepszy": best[0],
                    "wynik": round(best[1], 3), "drugi_folder": second[0], "wynik_drugi": round(second[1], 3),
                    "przewaga": round(best[1] - second[1], 3)})
        print(r["nazwa_w_tytule"], "->", best[0], round(best[1] - second[1], 3))
    with open(ROOT / "plans" / "mapa_obrazy.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
