#!/usr/bin/env python3
"""Podgląd dopasowań ofert urn do folderów po zdjęciach (do potwierdzenia przez właścicielkę): plans/podglad_dopasowan_urn.html.
Tylko odczyt. Użycie: python3 -I scripts/preview_urny.py
"""
import base64
import csv
import html
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import map_urny2 as m
import preview_obrazy as po

ROOT = api.ROOT
OUT = ROOT / "plans" / "podglad_dopasowan_urn.html"


def uri(img, w=300):
    img = img.convert("RGB")
    img.thumbnail((w, w))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=74)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "plans" / "urny_mapa_koncowa.csv", encoding="utf-8")) if r["metoda"].startswith("zdj")]
    idx = {r["ean"]: r for r in csv.DictReader(open(ROOT / "plans" / "urny_foldery_index.csv", encoding="utf-8"))}
    rows.sort(key=lambda r: (float(r["przewaga"]) >= 0.3 and float(r["wynik"]) >= 0.9, r["nazwa_w_tytule"]))
    cards = []
    for r in rows:
        res = sorted(api.get(f"/v3/application/listings/{r['listing_id']}/images").get("results", []), key=lambda i: i["rank"])
        a = Image.open(io.BytesIO(m.curl(res[0]["url_fullxfull"].replace("il_fullxfull", "il_340x270")))) if res else None
        f = idx[r["ean"]]
        p = m.CACHE / f"{r['ean']}-{sorted(f['zdjecia'].split('|'))[0]}"
        fi = Image.open(p) if p.exists() and p.stat().st_size else None
        if fi:
            fi = fi.crop((0, 0, int(fi.size[0] * 0.55), fi.size[1]))
        wynik, prz = float(r["wynik"]), float(r["przewaga"])
        pewnosc = "wysoka" if wynik >= 0.9 and prz >= 0.3 else ("średnia" if wynik >= 0.9 else "NISKA, sprawdź")
        fig = lambda im, cap: f'<figure><img alt="{cap}" src="{uri(im)}"><figcaption>{cap}</figcaption></figure>' if im else f'<figure class="nofoto"><span>brak zdjęcia</span><figcaption>{cap}</figcaption></figure>'
        cid = r["listing_id"]
        cards.append(f'''<article class="card" data-id="{cid}" data-name="{html.escape(r["nazwa_w_tytule"])} ({cid} -> {html.escape(f["folder"][:30])})">
<header><b>{html.escape(r["nazwa_w_tytule"])}</b> <span class="mono">oferta {cid}</span></header>
<div class="imgs">{fig(a, "zdjęcie nr 1 oferty w Etsy")}{fig(fi, "folder: foto-1 (urna)")}<figure class="nofoto"><span>{pewnosc}</span><figcaption>pewność dopasowania</figcaption></figure></div>
<p class="meta"><span class="mono">{html.escape(f["folder"])}</span><br>{html.escape(r["metoda"])}: wynik {r["wynik"]}, przewaga {r["przewaga"]}</p>
<div class="vote" role="radiogroup" aria-label="Ocena dopasowania">
<label><input type="radio" name="v-{cid}" value="ok"><span>Zgadza się</span></label>
<label><input type="radio" name="v-{cid}" value="zle"><span>Nie zgadza się</span></label>
<label><input type="radio" name="v-{cid}" value="nie"><span>Niepewne</span></label></div></article>''')
    page = po.TEMPLATE.replace("Podgląd dopasowań zdjęć", "Podgląd dopasowań urn").replace("{{N}}", str(len(rows))) \
        .replace("{{CARDS}}", '<section class="grp"><h2>Oferty urn z płytką dopasowane po zdjęciach <span class="sp">najpierw te najmniej pewne</span></h2><div class="row">' + "\n".join(cards) + "</div></section>")
    page = page.replace("ofert płytek dopasowanych do folderów przez porównanie zdjęć. Dla każdej porównaj zdjęcie oferty w Etsy z <b>1.jpg</b> z folderu (to ono było porównywane). Jeśli to ten sam projekt, folder jest dobry, a oferta dostanie zdjęcia z folderu (3.jpg jako główne). Przy parach tej samej rasy sprawdź, czy dwie oferty nie zamieniły się folderami.",
                        "ofert urn dopasowanych do folderów wideo przez porównanie rysunku na płytce (zdjęcie nr 1 oferty z foto-1 z folderu). Jeśli to ten sam rysunek, folder jest dobry i oferta dostanie z niego film. Przy parach tej samej rasy sprawdź, czy oferty nie zamieniły się folderami. Karty z niską pewnością są pierwsze.")
    OUT.write_text(page, encoding="utf-8")
    print(f"zapisano {OUT.relative_to(ROOT)}: {len(rows)} ofert, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
