#!/usr/bin/env python3
"""Mapowanie ofert na foldery 089 po wyglądzie reliefu (bez zapytań do Etsy; zdjęcia z i.etsystatic.com i www.artdog.com.pl).
Porównuje wycinek z reliefem ze zdjęcia 1 oferty ze zdjęciem 1 folderu (kafelek z urną po lewej), przydział jednoznaczny (zachłanny) z podpowiedzią nazwy.
Wynik: plans/brelok_mapa_obraz.csv (propozycja do sprawdzenia przez właścicielkę).
"""
import csv
import json
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch as B
import batch_relief as R

ROOT = B.ROOT
BASE = "https://www.artdog.com.pl/VIDEO/IV%20tura/089.%20Urny%20z%20brelokiem%20duze/"
CACHE = B.CACHE.parent / "brelok"


def urn_relief_vec(im, left=1.0):
    im = im.convert("RGB")
    w, h = im.size
    im = im.crop((0, 0, int(w * left), h))
    a = np.asarray(im.convert("L"), dtype=float)
    ys, xs = np.where(a < 200)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    uw, uh = x1 - x0, y1 - y0
    crop = im.crop((int(x0 + uw * 0.40), int(y0 + uh * 0.28), int(x0 + uw * 0.60), int(y0 + uh * 0.52)))
    v = np.asarray(crop.convert("L").resize((40, 48)), dtype=float).ravel()
    v -= v.mean()
    return v / (np.linalg.norm(v) + 1e-9)


def main():
    stan = json.load(open(ROOT / "plans" / "brelok_stan_zywy.json", encoding="utf-8"))
    mapa = {int(r["listing_id"]): r for r in csv.DictReader(open(ROOT / "plans" / "brelok_mapa.csv", encoding="utf-8"))}
    folders = list(csv.DictReader(open(ROOT / "plans" / "brelok_foldery_index.csv", encoding="utf-8")))
    lids = [int(k) for k in stan if int(k) in mapa]

    def dl_live(lid):
        return R.curl_to(stan[str(lid)]["images"][0][2], CACHE / "live" / f"{lid}.jpg")

    def dl_fol(f):
        fn = f["zdjecia"].split("|")[0]
        return R.curl_to(BASE + urllib.parse.quote(f["folder"]) + "/" + urllib.parse.quote(fn), CACHE / "foto1" / (f["folder"].split(".")[0] + ".jpg"))

    with ThreadPoolExecutor(6) as ex:
        lp = list(ex.map(dl_live, lids))
        fp = list(ex.map(dl_fol, folders))
    LV = np.array([urn_relief_vec(Image.open(p)) for p in lp])
    FV = np.array([urn_relief_vec(Image.open(p), left=0.58) for p in fp])
    S = LV @ FV.T
    # podpowiedź nazwy: +0.15 dla folderów o rasie z mapy nazw
    alias = {r["listing_id"]: r["folder"] for r in mapa.values()}
    bonus = np.zeros_like(S)
    for i, lid in enumerate(lids):
        nm = mapa[lid]["folder"]
        if nm:
            for j, f in enumerate(folders):
                if f["folder"].split(" ")[1:-1] and mapa[lid]["rasa_xlsx"] and mapa[lid]["rasa_xlsx"].lower().split()[0] in f["nazwa"].lower():
                    bonus[i, j] = 0.15
    T = S + bonus
    pairs, ui, uj = [], set(), set()
    for i, j in sorted(np.ndindex(*T.shape), key=lambda ij: -T[ij]):
        if i in ui or j in uj:
            continue
        pairs.append((i, j))
        ui.add(i)
        uj.add(j)
        if len(ui) == len(lids):
            break
    r_, c_ = zip(*pairs)
    out = []
    for i, j in zip(r_, c_):
        lid = lids[i]
        top = np.argsort(-S[i])[:3]
        out.append({"listing_id": lid, "wyswietlenia": mapa[lid]["wyswietlenia"], "nazwa_w_tytule": mapa[lid]["nazwa_w_tytule"], "folder": folders[j]["folder"], "zgodnosc": f"{S[i, j]:.3f}",
                    "nazwa_zgodna": "tak" if bonus[i, j] else "nie", "najlepsze_3": " | ".join(f"{folders[k]['folder'].split(' ', 1)[0]} {S[i, k]:.2f}" for k in top)})
    with open(ROOT / "plans" / "brelok_mapa_obraz.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(sorted(out, key=lambda x: int(x["wyswietlenia"])))
    z = [float(o["zgodnosc"]) for o in out]
    print("ofert:", len(out), "| zgodność min/mediana:", min(z), float(np.median(z)), "| nazwa zgodna:", sum(o["nazwa_zgodna"] == "tak" for o in out))
    for o in out:
        if o["nazwa_zgodna"] == "nie" or float(o["zgodnosc"]) < 0.6:
            print(" ?", o["listing_id"], o["nazwa_w_tytule"], "->", o["folder"], o["zgodnosc"], "|", o["najlepsze_3"])


if __name__ == "__main__":
    main()
