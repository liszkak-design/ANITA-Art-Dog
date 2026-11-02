#!/usr/bin/env python3
"""Mapa 38 ofert "Memorial Board" -> folder 218 (EAN). Rasa po nazwie; warianty rozmiaru (mała/duża głowa) po podobieństwie zdjęcia 1 oferty do zdjęcia 1 folderu
(deska: bbox, wycinek, korelacja). Bez zapytań do Etsy (zdjęcia z i.etsystatic.com i artdog.com.pl). Wynik: plans/deski_mapa.csv + arkusze plans/porownanie_deski/*.jpg.
"""
import csv
import json
import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch as B
import batch_relief as R

ROOT = B.ROOT
BASE = "https://www.artdog.com.pl/VIDEO/IX%20tura/218.%20Plakietki%20MDF/"
CACHE = B.CACHE.parent / "deski"
NORM = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s.lower().replace("ł", "l")).encode("ascii", "ignore").decode())


def board_vec(path, left=1.0):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    im = im.crop((0, 0, int(w * left), h))
    a = np.asarray(im.convert("L"), dtype=float)
    ys, xs = np.where(a < 225)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    bw, bh = x1 - x0, y1 - y0
    c = im.crop((int(x0 + bw * 0.1), int(y0 + bh * 0.05), int(x0 + bw * 0.9), int(y0 + bh * 0.62))).convert("L").resize((60, 56))
    v = np.asarray(c, dtype=float).ravel()
    v -= v.mean()
    return v / (np.linalg.norm(v) + 1e-9)


def main():
    stan = json.load(open(ROOT / "plans" / "plakietki_deski_stan_zywy.json", encoding="utf-8"))
    folders = list(csv.DictReader(open(ROOT / "plans" / "deski_foldery_index.csv", encoding="utf-8")))
    fparts = []
    for f in folders:
        parts = [NORM(p) for p in re.sub(r"\(.*?\)|\d", "", f["nazwa"]).split(",")]
        fparts.append(set(p for p in parts if p))
    rows, sheets = [], []
    for lid, v in stan.items():
        raw = v["title"].split(" Memorial Board")[0]
        key = NORM(raw)
        cand = [i for i, ps in enumerate(fparts) if key in ps]
        p1 = R.curl_to(v["images"][0][2], CACHE / "live" / f"{lid}.jpg")
        best, sims = None, {}
        if len(cand) == 1:
            best = cand[0]
        elif len(cand) > 1:
            lv = board_vec(p1)
            for i in cand:
                f = folders[i]
                fp = R.curl_to(BASE + urllib.parse.quote(f["folder"]) + "/" + urllib.parse.quote(f["zdjecia"].split("|")[0]), CACHE / "foto1" / f"{f['ean']}.jpg")
                sims[i] = float(lv @ board_vec(fp, 0.5))
            best = max(sims, key=sims.get)
        rows.append({"listing_id": lid, "wyswietlenia": v["views"], "rasa_w_tytule": raw, "kandydaci": len(cand), "folder": folders[best]["folder"] if best is not None else "", "ean": folders[best]["ean"] if best is not None else "",
                     "podobienstwa": " | ".join(f"{folders[i]['folder'].split(' ',1)[0]} {s:.3f}" for i, s in sims.items()), "uwagi": "" if best is not None else "brak folderu"})
    out = ROOT / "plans" / "deski_mapa.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: -int(r["wyswietlenia"])))
    used = {}
    for r in rows:
        used.setdefault(r["ean"], []).append(r["listing_id"])
    print("ofert:", len(rows), "| bez folderu:", [r["listing_id"] for r in rows if not r["ean"]], "| z wariantami rozmiaru:", sum(r["kandydaci"] > 1 for r in rows), "| EAN użyty >1:", {k: v for k, v in used.items() if len(v) > 1})
    return rows


if __name__ == "__main__":
    main()
