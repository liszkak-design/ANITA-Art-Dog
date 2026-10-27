#!/usr/bin/env python3
"""Korekta powtórzeń typu "Bulldog dog" / "Sheepdog dog" / "Ocicat cat" w opisach już zapisanych ofert (tylko pole description).
  python3 -I scripts/korekta_powtorzen.py <id> [...]            # podgląd zmian (nic nie zapisuje)
  python3 -I scripts/korekta_powtorzen.py <id> [...] --apply    # zapis (tylko po zgodzie właścicielki), backup + log
"""
import datetime
import difflib
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import backup_listing as bk

ROOT = api.ROOT
PAT = re.compile(r"\b(\w*(?:dog|cat|horse|pony))\s+(?:dog|cat|horse|pony)\b", re.I)


def fix(desc):
    return PAT.sub(lambda m: m.group(1) if m.group(1).lower().endswith(m.group(0).split()[-1].lower()) else m.group(0), desc)


def main():
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    log = ROOT / "logs" / f"korekta_opisow_{datetime.date.today()}.jsonl"
    for lid in ids:
        live = api.get(f"/v3/application/listings/{lid}")
        old, new = live["description"], fix(live["description"])
        if old == new:
            print(lid, "bez zmian"); continue
        for l in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0):
            if l[:1] in "+-" and l[:3] not in ("+++", "---"):
                print(f"  {lid} {l[:170]}")
        if "--apply" not in sys.argv:
            continue
        live_full = {"listing": api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization")}
        bp = ROOT / "backup" / f"{lid}_{datetime.date.today()}_przed_korekta.json"
        bp.write_text(json.dumps(live_full, ensure_ascii=False, indent=1))
        r = api.request("PATCH", f"/v3/application/shops/{bk.SHOP_ID}/listings/{lid}", headers={"Content-Type": "application/x-www-form-urlencoded"},
                        data=urllib.parse.urlencode({"description": new}).encode(), retries=1)
        ok = isinstance(r, dict) and "error" not in r
        after = api.get(f"/v3/application/listings/{lid}")
        good = ok and after["description"] == new and after["title"] == live["title"] and after["price"] == live["price"] and after["quantity"] == live["quantity"]
        with open(log, "a") as fh:
            fh.write(json.dumps({"listing_id": lid, "field": "description", "before": old[:300], "after": new[:300], "status": "ok" if good else "błąd",
                                 "backup": bp.name, "time": datetime.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")
        print(lid, "ok" if good else f"BŁĄD {str(r)[:200]}")
        if not good:
            sys.exit("Przerywam po błędzie.")


if __name__ == "__main__":
    main()
