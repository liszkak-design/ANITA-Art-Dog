#!/usr/bin/env python3
"""Podgląd dopasowań ofert do folderów ze zdjęciami (oferty dopasowane przez porównanie zdjęć, bez EAN w tabeli).
Tylko odczyt: pobiera zdjęcie oferty (i.etsystatic.com) i zdjęcia z folderu (artdog.com.pl), robi miniatury i zapisuje
plans/podglad_dopasowan_zdjec.html (miniatury wbudowane, strona do przeglądu przez właścicielkę).
Usage: python3 -I scripts/preview_obrazy.py
"""
import base64
import csv
import html
import io
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch as b

ROOT = b.ROOT
UA = {"User-Agent": "ArtDog-Etsy-Tool/1.0"}
OUT = ROOT / "plans" / "podglad_dopasowan_zdjec.html"


def thumb(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
            im = Image.open(io.BytesIO(r.read())).convert("RGB")
        im.thumbnail((260, 260))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=72)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def export_image(zrodlo):
    f, n = zrodlo.split(":")
    rows = list(csv.DictReader(open(ROOT / "data" / f, encoding="utf-8-sig")))
    return rows[int(n) - 2]["IMAGE1"]


def main():
    cands, _ = b.build_candidates()
    ean_tab = {r["zrodlo"]: r["ean"] for r in csv.DictReader(open(ROOT / "plans" / "mapa_plytki_with_photo.csv", encoding="utf-8"))}
    obr = {r["zrodlo"]: r for r in csv.DictReader(open(ROOT / "plans" / "mapa_obrazy.csv", encoding="utf-8"))}
    items = []
    for c in cands:
        r = c["row"]
        if ean_tab.get(r["zrodlo"]):
            continue
        ean = (re.findall(r"\b(\d{13})\b", r["folder"]) or [""])[0]
        why = [w for w in c["why"] if not w.startswith("ID oferty")]
        ids = b.title_index().get(r["tytul"], [])
        items.append({"zrodlo": r["zrodlo"], "gatunek": r["gatunek"], "rasa": r["rasa_kolumna_C"], "tytul": r["tytul"],
                      "lid": ids[0] if len(ids) == 1 else None, "n_ids": len(ids), "folder": r["folder"], "ean": ean,
                      "metoda": r["metoda"], "obr": obr.get(r["zrodlo"]), "inne": why})
    jobs = []
    for it in items:
        jobs += [(it, "oferta", export_image(it["zrodlo"])),
                 (it, "f1", f"{b.EAN_BASE}{it['ean']}/1.jpg"), (it, "f3", f"{b.EAN_BASE}{it['ean']}/3.jpg")]
    with ThreadPoolExecutor(6) as ex:
        for (it, k, _), data in zip(jobs, ex.map(lambda j: thumb(j[2]), jobs)):
            it[k] = data
    items.sort(key=lambda i: (i["gatunek"], i["rasa"], i["zrodlo"]))
    groups = {}
    for it in items:
        groups.setdefault((it["gatunek"], it["rasa"]), []).append(it)
    cards = []
    for (g, rasa), lst in groups.items():
        cards.append(f'<section class="grp"><h2>{html.escape(rasa)} <span class="sp">{html.escape(g)}, {len(lst)} {"oferta" if len(lst) == 1 else "oferty"}</span></h2><div class="row">')
        for it in lst:
            o = it["obr"]
            score = (f'wynik {o["wynik"]}, przewaga {o["przewaga"]} nad „{html.escape(o["drugi_folder"])}” ({o["wynik_drugi"]})' if o else "folder wolny (jedyna oferta tej rasy bez pary)")
            flags = "".join(f'<li>{html.escape(w)}</li>' for w in it["inne"])
            lid = it["lid"] or f'niejednoznaczne ({it["n_ids"]} dopasowań po tytule)'
            cid = it["lid"] or it["zrodlo"]
            img = lambda k, cap: (f'<figure><img alt="{cap}" src="{it[k]}"><figcaption>{cap}</figcaption></figure>' if it[k] else f'<figure class="nofoto"><span>brak zdjęcia</span><figcaption>{cap}</figcaption></figure>')
            cards.append(f'''<article class="card" data-id="{html.escape(str(cid))}" data-name="{html.escape(rasa)} ({html.escape(str(lid))})">
<header><b>{html.escape(rasa)}</b> <span class="mono">oferta {html.escape(str(lid))}</span></header>
<div class="imgs">{img("oferta", "zdjęcie oferty w Etsy teraz")}{img("f1", "folder 1.jpg (porównywane)")}{img("f3", "folder 3.jpg (przyszłe główne)")}</div>
<p class="meta"><span class="mono">{html.escape(it["folder"])}</span><br>{html.escape(it["metoda"])}: {score}</p>
{f'<ul class="flags">{flags}</ul>' if flags else ''}
<div class="vote" role="radiogroup" aria-label="Ocena dopasowania">
<label><input type="radio" name="v-{html.escape(str(cid))}" value="ok"><span>Zgadza się</span></label>
<label><input type="radio" name="v-{html.escape(str(cid))}" value="zle"><span>Nie zgadza się</span></label>
<label><input type="radio" name="v-{html.escape(str(cid))}" value="nie"><span>Niepewne</span></label></div></article>''')
        cards.append("</div></section>")
    page = TEMPLATE.replace("{{CARDS}}", "\n".join(cards)).replace("{{N}}", str(len(items)))
    OUT.write_text(page, encoding="utf-8")
    print(f"zapisano {OUT.relative_to(ROOT)}: {len(items)} ofert w {len(groups)} grupach, {OUT.stat().st_size // 1024} KB; bez zdjęcia:",
          sum(1 for i in items for k in ("oferta", "f1", "f3") if not i[k]))


TEMPLATE = """<title>Podgląd dopasowań zdjęć</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
/* Układ: lista grup po rasie, w każdej karty ofert; karta = 3 miniatury obok siebie + ocena. Narzędzie robocze, spokojna paleta. */
:root{--bg:#f5f6f4;--surface:#ffffff;--fg:#1f2a28;--muted:#5c6b68;--line:#d9dfdc;--accent:#2f6f62;--accent-fg:#ffffff;--ok:#2e7d4f;--bad:#b3392f;--unsure:#a66a00;--chip:#e8eeeb;
--font-body:"Source Sans 3",system-ui,-apple-system,"Segoe UI",sans-serif;--font-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#151b1a;--surface:#1e2625;--fg:#e6ece9;--muted:#9aaaa6;--line:#334140;--accent:#6fc3b0;--accent-fg:#10201c;--ok:#6fcf97;--bad:#f08a80;--unsure:#e5b04d;--chip:#2a3533;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#151b1a;--surface:#1e2625;--fg:#e6ece9;--muted:#9aaaa6;--line:#334140;--accent:#6fc3b0;--accent-fg:#10201c;--ok:#6fcf97;--bad:#f08a80;--unsure:#e5b04d;--chip:#2a3533;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--font-body);font-size:15px;line-height:1.45;padding-block:20px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:1180px;margin:0 auto;display:flex;flex-direction:column;gap:22px}
h1{font-size:1.5rem;margin:0;text-wrap:balance}
.lead{margin:6px 0 0;color:var(--muted);max-width:70ch}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 14px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
.bar .cnt{display:flex;gap:14px;flex-wrap:wrap;font-variant-numeric:tabular-nums}
.bar .cnt span b{font-weight:700}
.bar button{margin-left:auto;background:var(--accent);color:var(--accent-fg);border:0;border-radius:6px;padding:8px 14px;font:inherit;font-weight:600;cursor:pointer}
.bar button:focus-visible,.vote input:focus-visible+span{outline:2px solid var(--accent);outline-offset:2px}
.grp h2{font-size:1.05rem;margin:0 0 10px;display:flex;flex-wrap:wrap;gap:6px 12px;align-items:baseline}
.grp .sp{font-size:.85rem;font-weight:400;color:var(--muted)}
.row{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:10px;min-width:0}
.card header{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline}
.mono{font-family:var(--font-mono);font-size:.8rem;color:var(--muted);overflow-wrap:anywhere}
.imgs{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
figure{margin:0;display:flex;flex-direction:column;gap:4px;min-width:0}
figure img{width:100%;aspect-ratio:1;object-fit:contain;background:var(--chip);border-radius:4px;display:block}
.nofoto span{aspect-ratio:1;display:grid;place-items:center;background:var(--chip);border-radius:4px;color:var(--muted)}
figcaption{font-size:.75rem;color:var(--muted);line-height:1.3}
.meta{margin:0;font-size:.85rem;color:var(--muted)}
.flags{margin:0;padding-left:18px;font-size:.82rem;color:var(--unsure)}
.vote{display:flex;flex-wrap:wrap;gap:6px}
.vote label{cursor:pointer}
.vote input{position:absolute;opacity:0;pointer-events:none}
.vote span{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:.88rem;background:var(--bg)}
.vote input:checked+span{color:#fff;border-color:transparent}
.vote input[value="ok"]:checked+span{background:var(--ok)}
.vote input[value="zle"]:checked+span{background:var(--bad)}
.vote input[value="nie"]:checked+span{background:var(--unsure)}
.out{white-space:pre-wrap;font-family:var(--font-mono);font-size:.82rem;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px;min-width:0}
@media (max-width:520px){.imgs{grid-template-columns:repeat(3,minmax(0,1fr))}}
</style>
<div class="wrap">
<div><h1>Podgląd dopasowań zdjęć</h1>
<p class="lead">{{N}} ofert płytek dopasowanych do folderów przez porównanie zdjęć. Dla każdej porównaj zdjęcie oferty w Etsy z <b>1.jpg</b> z folderu (to ono było porównywane). Jeśli to ten sam projekt, folder jest dobry, a oferta dostanie zdjęcia z tego folderu (3.jpg jako główne). Przy parach tej samej rasy sprawdź, czy dwie oferty nie zamieniły się folderami.</p></div>
<div class="bar" role="status"><div class="cnt"><span>Zgadza się: <b id="c-ok">0</b></span><span>Nie zgadza się: <b id="c-zle">0</b></span><span>Niepewne: <b id="c-nie">0</b></span><span>Bez oceny: <b id="c-brak">0</b></span></div><button id="copy" type="button">Kopiuj wynik</button></div>
{{CARDS}}
<div class="out" id="out" hidden></div>
</div>
<script>
(function(){
  var cards=[].slice.call(document.querySelectorAll('.card'));
  function tally(){
    var c={ok:0,zle:0,nie:0};
    cards.forEach(function(k){var r=k.querySelector('input:checked'); if(r) c[r.value]++;});
    document.getElementById('c-ok').textContent=c.ok;document.getElementById('c-zle').textContent=c.zle;document.getElementById('c-nie').textContent=c.nie;
    document.getElementById('c-brak').textContent=cards.length-c.ok-c.zle-c.nie;
  }
  function summary(){
    var g={ok:[],zle:[],nie:[],brak:[]};
    cards.forEach(function(k){var r=k.querySelector('input:checked'); g[r?r.value:'brak'].push(k.dataset.name);});
    return 'Zgadza się ('+g.ok.length+'): '+g.ok.join('; ')+'\\nNie zgadza się ('+g.zle.length+'): '+g.zle.join('; ')+'\\nNiepewne ('+g.nie.length+'): '+g.nie.join('; ')+'\\nBez oceny ('+g.brak.length+'): '+g.brak.join('; ');
  }
  document.addEventListener('change',tally);
  document.getElementById('copy').addEventListener('click',function(){
    var t=summary(), out=document.getElementById('out');
    out.textContent=t; out.hidden=false;
    try{ navigator.clipboard.writeText(t).catch(function(){}); }catch(e){}
    var r=document.createRange(); r.selectNodeContents(out); var s=window.getSelection(); s.removeAllRanges(); s.addRange(r);
  });
  tally();
})();
</script>
"""

if __name__ == "__main__":
    main()
