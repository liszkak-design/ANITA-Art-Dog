#!/usr/bin/env python3
"""Podmiana drugiego filmu w ofercie 660384830 (Sloughi) na video/poprawki/sloughi-5056739236741.mp4.
Token nie ma zakresu listings_d, więc stary film (folder Saluki) właścicielka usuwa ręcznie w Etsy; skrypt dodaje nowy dopiero, gdy oferta ma 1 film.
  python3 -I scripts/podmien_film_sloughi.py            # dry-run: stan filmów w ofercie
  python3 -I scripts/podmien_film_sloughi.py --apply    # wgranie nowego filmu jako drugiego
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import apply_test_sphynx as base
import batch as B

LID = 660384830
F = B.ROOT / "video" / "poprawki" / "sloughi-5056739236741.mp4"
vids = api.get(f"/v3/application/listings/{LID}?includes=Videos").get("videos", [])
print("filmów w ofercie:", len(vids), [v["video_id"] for v in vids])
if "--apply" not in sys.argv:
    sys.exit("dry-run: nic nie zapisuję")
if len(vids) != 1:
    sys.exit("BŁĄD: oferta ma " + str(len(vids)) + " filmów; usuń ręcznie drugi (stary) film w Etsy, aby został 1 (film gatunku)")
data, ct = base.multipart({"name": F.name}, ("video", F.name), F.read_bytes(), "video/mp4")
r = api.request("POST", f"/v3/application/shops/{B.SHOP_ID}/listings/{LID}/videos", headers={"Content-Type": ct}, data=data, retries=1)
ok = base.ok(r)
B.zlog(LID, "podmiana_filmu_2", "film folderu Saluki (usunięty ręcznie)", F.name, "ok" if ok else "błąd")
print("ok" if ok else "BŁĄD " + str(r)[:200])
after = api.get(f"/v3/application/listings/{LID}?includes=Videos").get("videos", [])
print("filmów po zapisie:", len(after))
