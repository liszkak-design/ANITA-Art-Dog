#!/usr/bin/env python3
"""Końcowa mapa ofert urn z płytką "with a Photo" na foldery wideo (IV tura): plans/urny_mapa_koncowa.csv. Tylko odczyt.
Etapy: (1) rasa z Rasy.xlsx 1:1, (2) równe nazwy dla nierozpoznanych, (3) nazwy w grupach wieloznacznych,
(4) porównanie zdjęć oferty (Etsy, do 6) ze zdjęciami z folderu (foto-1..4), (5) resztki (oferty bez folderu, foldery bez oferty) po zdjęciach.
Użycie: python3 -I scripts/map_urny2.py
"""
import csv
import io
import itertools
import re
import subprocess
import sys
import time
import urllib.parse
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_map as bm
import etsy_api as api
import map_urny as mu
import plaque_match as pm

ROOT = bm.ROOT
VBASE = "https://www.artdog.com.pl/VIDEO/IV%20tura/"
CACHE = Path("/tmp/claude-0/-home-user-ANITA-Art-Dog/ffe4a3b0-655f-591d-929b-05322fdfe73b/scratchpad/urny_cache")
SP_ROOT = mu.SP_ROOT


def curl(url, tries=5):
    for i in range(tries):
        r = subprocess.run(["curl", "-sS", "-m", "60", "-f", url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(1.5 * (i + 1))
    return b""


def vec(img):
    img = img.convert("L")
    w, h = img.size
    s = max(w, h)
    sq = Image.new("L", (s, s), 255)
    sq.paste(img, ((s - w) // 2, (s - h) // 2))
    a = np.asarray(sq.resize((48, 48), Image.LANCZOS), dtype=float).ravel()
    a -= a.mean()
    return a / (np.linalg.norm(a) or 1)


_ov, _fv = {}, {}


def offer_vecs(lid):
    """Wektor rysunku w płytce na zdjęciu nr 1 oferty (tylko to zdjęcie zależy od rasy; zdjęcia 2-6 są ogólne)."""
    if lid not in _ov:
        res = sorted(api.get(f"/v3/application/listings/{lid}/images").get("results", []), key=lambda i: i["rank"])
        v = None
        if res:
            b = curl(res[0]["url_fullxfull"].replace("il_fullxfull", "il_340x270"))
            v = pm.plaque_vec(Image.open(io.BytesIO(b)), False) if b else None
        _ov[lid] = [v[0]] if v else []
    return _ov[lid]


def folder_vecs(f):
    """Wektor rysunku w płytce na zdjęciu foto-1 z folderu (zestaw: urna po lewej, tekst po prawej)."""
    key = f["ean"]
    if key not in _fv:
        ph = sorted(f["zdjecia"].split("|"))[0]
        p = CACHE / f"{key}-{ph}"
        if not p.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            p.write_bytes(curl(VBASE + urllib.parse.quote(f["korzen"]) + "/" + urllib.parse.quote(f["folder"]) + "/" + urllib.parse.quote(ph)))
        v = pm.plaque_vec(Image.open(p), True) if p.stat().st_size else None
        _fv[key] = [v[0]] if v else []
    return _fv[key]


def score(o, f):
    ov, fv = offer_vecs(o["lid"]), folder_vecs(f)
    return max((float(a @ b) for a in ov for b in fv), default=0.0)


def assign(offers, folders):
    """Najlepsze przypisanie (brute force, grupy małe). Zwraca listę (oferta, folder|None, wynik, przewaga)."""
    S = [[score(o, f) for f in folders] for o in offers]
    n, m = len(offers), len(folders)
    best, bp = -1e9, None
    k = min(n, m)
    for oi in itertools.permutations(range(n), k):
        for fi in itertools.permutations(range(m), k):
            tot = sum(S[o][f] for o, f in zip(oi, fi))
            if tot > best:
                best, bp = tot, dict(zip(oi, fi))
    res = []
    for oi, o in enumerate(offers):
        if oi in bp:
            fi = bp[oi]
            alt = sorted((S[oi][j] for j in range(m) if j != fi), reverse=True)
            res.append((o, folders[fi], S[oi][fi], S[oi][fi] - (alt[0] if alt else 0)))
        else:
            res.append((o, None, 0.0, 0.0))
    return res


def main():
    breeds, alias = bm.load_rasy()
    offers = []
    import csv as _c, html
    for r in _c.DictReader(open(ROOT / "plans" / "listing_ids_sklep.csv", encoding="utf-8")):
        t = html.unescape(r["title"])
        if mu.PH.search(t) and not re.search(r"graphic", t, re.I):
            m = re.match(r"(.*?)\s+Urn for (Dog|Cat|Horse) Ashes", t, re.I)
            if m:
                offers.append({"lid": r["listing_id"], "breed": m.group(1).strip(), "sp": {"dog": "pies", "cat": "kot", "horse": "koń"}[m.group(2).lower()], "title": t})
    folders = list(_c.DictReader(open(ROOT / "plans" / "urny_foldery_index.csv", encoding="utf-8")))
    for f in folders:
        f["sp"] = SP_ROOT[f["korzen"][:3]]
    result = []  # (oferta, folder, metoda, wynik, przewaga)
    groups = defaultdict(lambda: {"o": [], "f": []})
    unres_o, unres_f = [], []
    for o in offers:
        hits, _ = bm.lookup(o["breed"], o["sp"], alias)
        (groups[next(iter(hits))]["o"].append(o) if len(hits) == 1 else unres_o.append(o))
    for f in folders:
        hits, _ = bm.lookup(f["nazwa_z_folderu"], f["sp"], alias)
        (groups[next(iter(hits))]["f"].append(f) if len(hits) == 1 else unres_f.append(f))
    nm = lambda s: bm.strip_noise(s)
    # (2) nierozpoznane: równe nazwy
    for o in list(unres_o):
        c = [f for f in unres_f if f["sp"] == o["sp"] and nm(f["nazwa_z_folderu"]) == nm(o["breed"])]
        if not c:
            c = [f for f in unres_f if f["sp"] == o["sp"] and nm(f["nazwa_z_folderu"]).startswith(nm(o["breed"]))]
        if len(c) == 1:
            result.append((o, c[0], "nazwa (nierozpoznana rasa)", 1.0, 1.0)); unres_o.remove(o); unres_f.remove(c[0])
    leftover_o, leftover_f = list(unres_o), list(unres_f)
    for rid, g in groups.items():
        O, F = g["o"], g["f"]
        if len(O) == 1 and len(F) == 1:
            result.append((O[0], F[0], "rasa 1:1", 1.0, 1.0)); continue
        if not O:
            leftover_f += F; continue
        if not F:
            leftover_o += O; continue
        # (3) nazwy w grupie
        names = {}
        ok = True
        for o in O:
            c = [f for f in F if nm(f["nazwa_z_folderu"]) == nm(o["breed"])]
            if len(c) == 1 and c[0]["ean"] not in names.values():
                names[o["lid"]] = c[0]["ean"]
            else:
                ok = False
        if ok and len(names) == len(O) == len(F):
            for o in O:
                result.append((o, next(f for f in F if f["ean"] == names[o["lid"]]), "nazwa w grupie", 1.0, 1.0))
            continue
        # (4) zdjęcia
        for o, f, s, mgn in assign(O, F):
            if f is None:
                leftover_o.append(o)
            else:
                result.append((o, f, "zdjęcia (grupa)", s, mgn))
        used = {x[1]["ean"] for x in result if x[1]}
        leftover_f += [f for f in F if f["ean"] not in used]
    # (5) resztki po zdjęciach, w obrębie gatunku
    for sp in ("pies", "kot", "koń"):
        O = [o for o in leftover_o if o["sp"] == sp]
        F = [f for f in leftover_f if f["sp"] == sp and f["ean"] not in {x[1]["ean"] for x in result if x[1]}]
        if O and F:
            for o, f, s, mgn in assign(O, F):
                if f:
                    result.append((o, f, "zdjęcia (resztki)", s, mgn))
                else:
                    result.append((o, None, "brak folderu", 0.0, 0.0))
        else:
            for o in O:
                result.append((o, None, "brak folderu", 0.0, 0.0))
    used = {x[1]["ean"] for x in result if x[1]}
    extra_f = [f for f in folders if f["ean"] not in used]
    with open(ROOT / "plans" / "urny_mapa_koncowa.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "gatunek", "nazwa_w_tytule", "folder", "ean", "metoda", "wynik", "przewaga", "film_bez_brand"])
        for o, f, how, s, mgn in sorted(result, key=lambda x: (x[0]["sp"], x[0]["breed"])):
            nb = next((v.split(":")[0] for v in (f["wideo_rozmiar"].split("|") if f else []) if v and "brand" not in v.split(":")[0]), "")
            w.writerow([o["lid"], o["sp"], o["breed"], f["folder"] if f else "", f["ean"] if f else "", how, round(s, 3), round(mgn, 3), nb])
    import collections
    print("ofert:", len(offers), "| przypisanych:", sum(1 for x in result if x[1]), "| metody:", dict(collections.Counter(x[2] for x in result)))
    print("oferty bez folderu:", [(x[0]["lid"], x[0]["breed"]) for x in result if not x[1]])
    print("foldery bez oferty:", [(f["folder"][:40]) for f in extra_f])
    unsure = [(x[0]["breed"], x[1]["folder"][:34], x[2][:16], round(x[3], 2), round(x[4], 2)) for x in result if x[1] and x[2].startswith("zdj")]
    print("dopasowania po zdjęciach (do potwierdzenia):", len(unsure))
    for u in unsure: print("  ", u)


if __name__ == "__main__":
    main()
