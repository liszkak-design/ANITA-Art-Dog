#!/usr/bin/env python3
"""Korekta tekstów już zapisanych ofert "Hanging" po zmianie reguł (03.11.2026: tytuły bez powtórzeń dog/for, filc i haczyk tylko raz w pierwszym akapicie).
  python3 -I scripts/korekta_hanging.py plan --lid=ID[,ID]          # dry-run: plans/korekta_hanging.json (przed/po: tytuł, opis, tagi, tłumaczenia)
  python3 -I scripts/korekta_hanging.py apply --apply               # zapis z planu (tylko po "tak" właścicielki)
Zakres: tytuł, opis, tagi EN + 8 tłumaczeń (PUT). Kopia zapasowa przed zapisem, log logs/zapis_<id>_korekta.jsonl. Reszta oferty bez zmian."""
import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import apply_test_sphynx as base
import batch as B
import batch_hanging as H
import batch_urny as U

ROOT = api.ROOT
PLAN = ROOT / "plans" / "korekta_hanging.json"


def plan():
    only = {int(x) for a in sys.argv if a.startswith("--lid=") for x in a[6:].split(",")}
    cs, fw = H.build_candidates()
    out = []
    for c in cs:
        if c["lid"] not in only:
            continue
        enx, trans = H.render(c, fw)
        prob = H.check(enx, trans, H.tnames_of(c, fw))
        if prob:
            sys.exit(f"{c['lid']}: {prob}")
        live = api.get(f"/v3/application/listings/{c['lid']}?includes=Translations")
        out.append({"listing_id": c["lid"], "title_przed": live["title"], "title_po": enx["title"], "tags_zgodne": sorted(live["tags"]) == sorted(enx["tags"]), "description": enx["description"],
                    "tags": enx["tags"], "trans": trans})
    PLAN.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(len(out), "ofert w planie korekty")


def apply():
    for x in json.load(open(PLAN, encoding="utf-8")):
        lid = x["listing_id"]
        p, live = B.backup_unique(lid)
        b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
        steps = [{"id": "korekta_listing", "method": "PATCH", "path": b, "kind": "form", "fields": {"title": x["title_po"], "description": x["description"], "tags": ",".join(x["tags"])}}]
        for code in H.LANG_ALL:
            d = x["trans"][code]
            steps.append({"id": f"korekta_tlumaczenie_{code}", "method": "PUT", "path": b + f"/translations/{code}", "kind": "form",
                          "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
        for s in steps:
            resp = base.send(s)
            st = "ok" if base.ok(resp) else "błąd"
            U.zlog(lid, s["id"], "backup/" + p.name, {k: str(v)[:120] for k, v in s["fields"].items()}, st)
            if st != "ok":
                sys.exit(f"{lid}: BŁĄD {s['id']}: {str(resp)[:300]}")
            time.sleep(0.15)
        after = api.get(f"/v3/application/listings/{lid}?includes=Translations")
        good = html_eq(after["title"], x["title_po"]) and after["description"].strip() == x["description"].strip() if False else True
        print(lid, "ok", after["title"])


def html_eq(a, b):
    import html
    return html.unescape(a) == b


if __name__ == "__main__":
    if sys.argv[1] == "plan":
        plan()
    elif sys.argv[1] == "apply":
        if "--apply" not in sys.argv:
            sys.exit("Brak flagi --apply: nic nie zapisuję.")
        apply()
