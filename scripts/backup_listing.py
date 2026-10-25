#!/usr/bin/env python3
"""Read-only backup of one listing to backup/<listing_id>_<date>.json (rule 4).
Usage: python3 -I scripts/backup_listing.py <listing_id> [...]
"""
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api

ROOT = api.ROOT
SHOP_ID = 19255336


def backup(lid):
    out = {"listing": api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization"),
           "properties": api.get(f"/v3/application/shops/{SHOP_ID}/listings/{lid}/properties"),
           "inventory": api.get(f"/v3/application/listings/{lid}/inventory")}
    d = ROOT / "backup"
    d.mkdir(exist_ok=True)
    p = d / f"{lid}_{datetime.date.today()}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return p, out


if __name__ == "__main__":
    for lid in sys.argv[1:]:
        p, o = backup(lid)
        l = o["listing"]
        print(p.name, "| błąd:" if "error" in l else "| ok:", l.get("error") or l.get("title", "")[:70])
