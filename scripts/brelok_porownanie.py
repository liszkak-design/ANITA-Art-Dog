#!/usr/bin/env python3
"""Arkusze porównawcze dla niepewnych dopasowań ofert do folderów 089 (bez zapytań do Etsy; zdjęcia z cache).
Wiersz = oferta: zdjęcie 1 z Etsy (po lewej, ramka niebieska) i kandydaci: przypisany folder (ramka czerwona), foldery o tej samej nazwie i 3 najbardziej podobne.
Wynik: plans/porownanie_brelok/arkusz_NN.jpg
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch as B

ROOT = B.ROOT
CACHE = B.CACHE.parent / "brelok"
OUT = ROOT / "plans" / "porownanie_brelok"
W, H = 260, 240
FIRST = ["1394181431", "674107939", "660267206", "1394183167", "1394177227", "1380175976", "1380176110"]  # wyraźnie błędne dopasowania na początek


def urn_tile(path, left=1.0):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    im = im.crop((0, 0, int(w * left), h))
    a = np.asarray(im.convert("L"), dtype=float)
    ys, xs = np.where(a < 200)
    x0, y0, uw, uh = xs.min(), ys.min(), xs.max() + 1 - xs.min(), ys.max() + 1 - ys.min()
    im = im.crop((int(x0 + uw * 0.36), int(y0 + uh * 0.16), int(x0 + uw * 0.64), int(y0 + uh * 0.50)))  # sam relief, powiększony
    im = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
    im.thumbnail((W, H))
    t = Image.new("RGB", (W, H), "white")
    t.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return t


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(ROOT / "plans" / "brelok_mapa_obraz.csv", encoding="utf-8")))
    folders = {f["folder"].split(".")[0]: f for f in csv.DictReader(open(ROOT / "plans" / "brelok_foldery_index.csv", encoding="utf-8"))}
    def fn(x):
        return re.sub(r"^\d+\.\s*|\s*\d{13}$", "", x["folder"]).lower()
    mis = lambda x: x["nazwa_w_tytule"].lower().split()[0][:4] not in fn(x)
    unc = [x for x in rows if x["nazwa_zgodna"] == "nie" or float(x["zgodnosc"]) < 0.6 or mis(x)]
    cnt = {}
    for x in rows:
        k = x["nazwa_w_tytule"].lower().split()[0]
        cnt[k] = cnt.get(k, 0) + 1
    unc += [x for x in rows if cnt[x["nazwa_w_tytule"].lower().split()[0]] > 1 and x not in unc]  # rasy z kilkoma ofertami (warianty)
    unc.sort(key=lambda x: (x["listing_id"] not in FIRST, x["nazwa_w_tytule"].lower().split()[0], int(x["listing_id"])))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    per = 6
    for s in range(0, len(unc), per):
        chunk = unc[s:s + per]
        sheet = Image.new("RGB", (W * 7 + 30, (H + 70) * len(chunk)), "white")
        d = ImageDraw.Draw(sheet)
        for r, x in enumerate(chunk):
            y = r * (H + 70)
            sheet.paste(urn_tile(CACHE / "live" / f"{x['listing_id']}.jpg"), (0, y + 66))
            d.rectangle((0, y + 66, W - 1, y + 66 + H - 1), outline="blue", width=4)
            d.text((4, y + 2), f"OFERTA {x['listing_id']}  {x['nazwa_w_tytule']}  ({x['wyswietlenia']} wyśw.)", fill="black", font=font)
            d.text((4, y + 24), "zdjęcie 1 z Etsy", fill="blue", font=font)
            first = x["nazwa_w_tytule"].lower().split()[0][:4]
            cand = [x["folder"].split(".")[0]]
            cand += [n for n, f in folders.items() if first in f["nazwa"].lower() and n not in cand]
            cand += [t.split()[0].rstrip(".") for t in x["najlepsze_3"].split(" | ") if t.split()[0].rstrip(".") not in cand]
            for k, n in enumerate(cand[:6]):
                f = folders[n]
                px = W + 20 + k * W if k else W + 10
                px = W + 10 + k * W
                p = CACHE / "foto1" / f"{n}.jpg"
                sheet.paste(urn_tile(p, 0.58), (px, y + 66))
                mine = k == 0
                d.rectangle((px, y + 66, px + W - 1, y + 66 + H - 1), outline="red" if mine else "gray", width=4 if mine else 1)
                d.text((px + 2, y + 24 + (0 if mine else 0)), ("PRZYPISANY " if mine else "") + f["folder"].rsplit(" ", 1)[0][:30], fill="red" if mine else "black", font=font)
        sheet.convert("RGB").save(OUT / f"arkusz_{s // per + 1:02d}.jpg", quality=85)
    print("niepewnych ofert:", len(unc), "| arkuszy:", (len(unc) + per - 1) // per)


if __name__ == "__main__":
    main()
