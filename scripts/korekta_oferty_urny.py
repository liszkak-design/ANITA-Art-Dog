#!/usr/bin/env python3
"""Korekta już zapisanej oferty urny: porównuje tytuł, alt texty i tłumaczenia w Etsy z tym, co dają aktualne szablony i reguły.
  python3 -I scripts/korekta_oferty_urny.py 674148773            # dry-run: co się różni
  python3 -I scripts/korekta_oferty_urny.py 674148773 --apply    # poprawia tylko różniące się pola (tytuł, opis, tagi, alt, tłumaczenia), z kopią zapasową i logiem
Nie rusza cen, stanów, zdjęć (poza alt textem), filmów ani personalizacji.
"""
import html
import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import batch_urny as U
import batch as B

lid = int(sys.argv[1])
cs, fw = U.candidates()
c = next(x for x in cs if x["lid"] == lid)
c["why"] = [w for w in c["why"] if not w.startswith("już zoptymalizowana")]
if c["why"]:
    sys.exit("BŁĄD: " + "; ".join(c["why"]))
en, trans = U.render(c, fw)
live = api.get(f"/v3/application/listings/{lid}?includes=Images,Translations")
diff = []
u = lambda s: html.unescape(s or "").replace("\r", "").strip()
if u(live["title"]) != en["title"]:
    diff.append("title")
if u(live["description"]) != en["description"].strip():
    diff.append("description")
if list(live["tags"]) != en["tags"]:
    diff.append("tags")
imgs = {i["rank"]: i for i in live["images"]}
alt_diff = [k for k, v in en["alts"].items() if u(imgs.get(k, {}).get("alt_text")) != v]
tr_diff = []
for code, d in trans.items():
    cur = live["translations"].get(code) or {}
    if u(cur.get("title")) != d["title"] or u(cur.get("description")) != d["description"].strip() or list(cur.get("tags", [])) != d["tags"]:
        tr_diff.append(code)
print("różnice: pola", diff, "| alt", alt_diff, "| tłumaczenia", tr_diff)
if diff:
    print("tytuł teraz:", u(live["title"]), "\ntytuł po:   ", en["title"])
if "--apply" not in sys.argv:
    sys.exit("dry-run: nic nie zapisuję")
p, _ = B.backup_unique(lid)
base = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
form = {"Content-Type": "application/x-www-form-urlencoded"}


def done(step, fields, r):
    ok = isinstance(r, dict) and "error" not in r
    B.zlog(lid, "korekta_" + step, "backup/" + p.name, fields, "ok" if ok else "błąd")
    print(step, "ok" if ok else "BŁĄD " + str(r)[:200])
    if not ok:
        sys.exit("Przerywam po błędzie.")


if diff:
    f = {k: (",".join(en[k]) if k == "tags" else en[k]) for k in diff}
    done("listing", {k: str(v)[:120] for k, v in f.items()}, api.request("PATCH", base, headers=form, data=urllib.parse.urlencode(f).encode(), retries=1))
for k in alt_diff:
    im = imgs[k]
    f = {"listing_image_id": str(im["listing_image_id"]), "rank": str(k), "overwrite": "true", "alt_text": en["alts"][k]}
    done(f"alt_{k}", {"alt_text": en["alts"][k][:120]}, api.request("POST", base + "/images", headers=form, data=urllib.parse.urlencode(f).encode(), retries=1))
for code in tr_diff:
    d = trans[code]
    f = {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}
    done(f"tlumaczenie_{code}", {"title": d["title"]}, api.request("PUT", base + f"/translations/{code}", headers=form, data=urllib.parse.urlencode(f).encode(), retries=1))
