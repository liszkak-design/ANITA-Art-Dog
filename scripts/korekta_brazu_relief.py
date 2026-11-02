#!/usr/bin/env python3
"""Korekta opisów urn z reliefem "cold cast bronze" (38 ofert): zdania z samym "bronze relief" / "z brązu" zamienione na "cold cast bronze relief" i odpowiedniki (decyzja właścicielki 02.11.2026:
określenia sugerujące podobieństwo do brązu (cold cast bronze, bronze look) są poprawne, samo "relief z brązu" jest nieprawdziwe). Zmieniamy tylko opis EN i opisy tłumaczeń z planu plans/korekta_brazu_relief.json
(tytuły i tagi bez zmian). Tryb próbny pokazuje zakres; zapis tylko z --apply po "tak" właścicielki.
  python3 -I scripts/korekta_brazu_relief.py            # dry-run: zakres zmian
  python3 -I scripts/korekta_brazu_relief.py --apply    # zapis (backup, log, weryfikacja, wznawialne)
"""
import glob
import html
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import apply_test_sphynx as base
import batch as B
import batch_urny as U

ROOT = api.ROOT
PLAN = ROOT / "plans" / "korekta_brazu_relief.json"
LOG = ROOT / "logs" / "korekta_brazu_relief.jsonl"


def old_data():
    old = {}
    for f in sorted(glob.glob(str(ROOT / "plans" / "partia_relief_*_dryrun.json"))):
        for x in json.load(open(f, encoding="utf-8")):
            old[x["listing_id"]] = x
    return old


def done_steps(lid):
    if not LOG.exists():
        return set()
    return {j["id"] for j in map(json.loads, LOG.read_text().splitlines()) if j["listing_id"] == lid and j["status"] == "ok"}


def log(lid, step, info, status):
    with open(LOG, "a") as fh:
        fh.write(json.dumps({"listing_id": lid, "id": step, "info": info, "status": status, "time": time.strftime("%Y-%m-%dT%H:%M:%S")}, ensure_ascii=False) + "\n")


def main():
    plan = json.load(open(PLAN, encoding="utf-8"))
    old = old_data()
    apply_ = "--apply" in sys.argv
    n_trans = sum(len([d for d in p["diffs"] if d != "en"]) for p in plan)
    print(f"ofert: {len(plan)}, zmian opisu EN: {sum('en' in p['diffs'] for p in plan)}, zmian opisów tłumaczeń: {n_trans}")
    if not apply_:
        sys.exit("dry-run: nic nie zapisuję")
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    for i, p in enumerate(plan, 1):
        lid = p["listing_id"]
        if "korekta_weryfikacja" in done_steps(lid):
            print(i, lid, "pomijam (już poprawiona)")
            continue
        bpath, live = B.backup_unique(lid)
        if "error" in live or live["state"] != "active":
            sys.exit(f"{lid}: odczyt/status: {str(live.get('error') or live['state'])[:100]}")
        done = done_steps(lid)
        o = old[lid]
        b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
        steps = []
        if "en" in p["diffs"]:
            steps.append(("korekta_opis_en", {"id": "x", "method": "PATCH", "path": b, "kind": "form", "fields": {"description": p["en_description"]}}))
        for code in (d for d in p["diffs"] if d != "en"):
            t = o["tlumaczenia"][code]
            steps.append((f"korekta_tlumaczenie_{code}", {"id": "x", "method": "PUT", "path": b + f"/translations/{code}", "kind": "form",
                                                         "fields": {"title": t["title"], "description": p["tlumaczenia"][code], "tags": ",".join(t["tags"])}}))
        for sid, st in steps:
            if sid in done:
                continue
            resp = base.send(st)
            ok = base.ok(resp)
            log(lid, sid, {"backup": bpath.name}, "ok" if ok else "błąd")
            if not ok:
                sys.exit(f"{lid}: BŁĄD w kroku {sid}: {str(resp)[:300]}")
            time.sleep(0.15)
        for attempt in range(4):
            after = api.get(f"/v3/application/listings/{lid}?includes=Translations")
            good = after["price"] == live["price"] and after["quantity"] == live["quantity"] and after["state"] == live["state"]
            if "en" in p["diffs"]:
                good = good and html.unescape(after["description"]) == p["en_description"]
            for code in (d for d in p["diffs"] if d != "en"):
                good = good and html.unescape((after["translations"].get(code) or {}).get("description", "")) == p["tlumaczenia"][code]
            if good:
                break
            time.sleep(3)
        log(lid, "korekta_weryfikacja", {"cena_stan_status_ok": True}, "ok" if good else "niezgodność")
        print(i, lid, "ok" if good else "NIEZGODNOŚĆ")
        if not good:
            sys.exit("Weryfikacja niezgodna, przerywam.")
    print("Korekta zakończona. Proszę sprawdzić próbkę w Etsy.")


if __name__ == "__main__":
    main()
