#!/usr/bin/env python3
"""Korekta tytułów z końcówką "for Your, Pet Loss Keepsake" -> "for Your Pet, Pet Loss Keepsake" (tylko pole title, tytuł EN).
  python3 -I scripts/korekta_tytulow.py <id> [...]            # podgląd zmian (nic nie zapisuje)
  python3 -I scripts/korekta_tytulow.py <id> [...] --apply    # zapis (po zgodzie właścicielki), backup + log + weryfikacja
"""
import datetime
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import backup_listing as bk

ROOT = api.ROOT
PAT = re.compile(r"for Your,( Pet Loss Keepsake)")


def main():
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    log = ROOT / "logs" / f"korekta_tytulow_{datetime.date.today()}.jsonl"
    for lid in ids:
        live = api.get(f"/v3/application/listings/{lid}")
        old = html.unescape(live["title"])
        new = PAT.sub(r"for Your Pet,\1", old)
        if old == new:
            print(lid, "bez zmian:", old[-60:]); continue
        print(f"  {lid} -{old[-75:]}\n  {lid} +{new[-75:]}")
        if "--apply" not in sys.argv:
            continue
        full = {"listing": api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization")}
        bp = ROOT / "backup" / f"{lid}_{datetime.date.today()}_przed_korekta_tytulu.json"
        bp.write_text(json.dumps(full, ensure_ascii=False, indent=1))
        r = api.request("PATCH", f"/v3/application/shops/{bk.SHOP_ID}/listings/{lid}", headers={"Content-Type": "application/x-www-form-urlencoded"},
                        data=urllib.parse.urlencode({"title": new}).encode(), retries=1)
        after = api.get(f"/v3/application/listings/{lid}")
        good = isinstance(r, dict) and "error" not in r and html.unescape(after["title"]) == new and after["description"] == live["description"] \
            and after["price"] == live["price"] and after["quantity"] == live["quantity"] and after["state"] == live["state"]
        with open(log, "a") as fh:
            fh.write(json.dumps({"listing_id": lid, "field": "title", "before": old, "after": new, "status": "ok" if good else "błąd",
                                 "backup": bp.name, "time": datetime.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")
        print(lid, "ok" if good else f"BŁĄD {str(r)[:200]}")
        if not good:
            sys.exit("Przerywam po błędzie.")


if __name__ == "__main__":
    main()
