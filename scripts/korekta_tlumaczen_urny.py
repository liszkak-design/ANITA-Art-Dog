#!/usr/bin/env python3
"""Korekta tłumaczeń urn w już zapisanych ofertach: porównuje tłumaczenia w Etsy z wygenerowanymi z aktualnych szablonów.
  python3 -I scripts/korekta_tlumaczen_urny.py 674223007            # dry-run: ile języków się różni
  python3 -I scripts/korekta_tlumaczen_urny.py 674223007 --apply    # PUT tylko różniących się języków (po zgodzie właścicielki), z logiem
Zmienia wyłącznie tłumaczenia (tytuł, opis, tagi) z szablonów; nic poza tym.
"""
import datetime
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import batch_urny as U
import batch as B

lid = int(sys.argv[1])
cs, fw = U.candidates()
c = next(x for x in cs if x["lid"] == lid)
en, trans = U.render(c, fw)
live = api.get(f"/v3/application/listings/{lid}?includes=Translations")
todo = []
for code, d in trans.items():
    cur = live["translations"].get(code) or {}
    same = html.unescape(cur.get("title", "")) == d["title"] and html.unescape(cur.get("description", "")).replace("\r", "").strip() == d["description"].strip() \
        and list(cur.get("tags", [])) == d["tags"]
    print(code, "bez zmian" if same else "RÓŻNI SIĘ")
    if not same:
        todo.append(code)
if "--apply" not in sys.argv:
    sys.exit(f"dry-run: do poprawy {len(todo)} języków: {todo}")
bk = B.ROOT / "backup" / f"{lid}_tlumaczenia_{datetime.date.today()}.json"
bk.write_text(json.dumps(live.get("translations"), ensure_ascii=False, indent=1))
import urllib.parse
for code in todo:
    d = trans[code]
    data = urllib.parse.urlencode({"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}).encode()
    r = api.request("PUT", f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}/translations/{code}", headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data, retries=1)
    ok = isinstance(r, dict) and "error" not in r
    B.zlog(lid, f"korekta_tlumaczenie_{code}", "backup/" + bk.name, {"title": d["title"]}, "ok" if ok else "błąd")
    print(code, "ok" if ok else "BŁĄD " + str(r)[:200])
    if not ok:
        sys.exit("Przerywam po błędzie.")
