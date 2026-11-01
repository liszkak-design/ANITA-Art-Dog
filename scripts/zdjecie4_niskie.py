#!/usr/bin/env python3
"""Wymiana zdjęcia 4 (widok wnętrza) w ofertach niskiej urny, które są już zoptymalizowane (np. test 673157877), na plik media/urny_brelok_niskie/zdjecie_4.jpg.
  python3 -I scripts/zdjecie4_niskie.py plan N [--lid=ID[,ID]] [--size=K]   # dry-run: plans/zdjecie4_niskie_00N.json
  python3 -I scripts/zdjecie4_niskie.py apply N --apply                      # zapis (tylko po "tak" właścicielki dla partii N)
Wymiana przez uploadListingImage: rank=4, overwrite=true, bez usuwania (bez listings_d). Alt text zostaje (zatwierdzony). Zdjęcia 1-3 bez zmian (id i kolejność).
Stop przy pierwszej niezgodności (np. gdyby powstało 5 zdjęć). Kopia zapasowa przed zapisem, log logs/zdjecie4_niskie_<id>.jsonl. Limit API: etsy_api (stop 9000).
"""
import csv
import datetime
import html
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import apply_test_sphynx as base
import batch as B

ROOT = api.ROOT
PHOTO = ROOT / "media" / "urny_brelok_niskie" / "zdjecie_4.jpg"
ALT4 = "View of the inside of the urn with the lid removed."


def plan_file(n):
    return ROOT / "plans" / f"zdjecie4_niskie_{n:03d}.json"


def log(lid, step, info, status):
    with open(ROOT / "logs" / f"zdjecie4_niskie_{lid}.jsonl", "a") as fh:
        fh.write(json.dumps({"listing_id": lid, "id": step, "info": info, "status": status, "time": datetime.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")


def done4(lid):
    p = ROOT / "logs" / f"zdjecie4_niskie_{lid}.jsonl"
    return p.exists() and any(j["id"] == "weryfikacja" and j["status"] == "ok" for j in map(json.loads, p.read_text().splitlines()))


def plan(n, size):
    stan = json.load(open(ROOT / "plans" / "brelok_niskie_stan_zywy.json", encoding="utf-8"))
    only = {int(x) for a in sys.argv if a.startswith("--lid=") for x in a[6:].split(",")}
    out = []
    for r in sorted(csv.DictReader(open(ROOT / "plans" / "brelok_niskie_mapa_final.csv", encoding="utf-8")), key=lambda r: (int(r["wyswietlenia"]), int(r["listing_id"]))):
        lid = int(r["listing_id"])
        if (only and lid not in only) or not B.is_done(lid) or done4(lid):
            continue
        out.append({"listing_id": lid, "wyswietlenia": int(r["wyswietlenia"]), "images_before": {str(i[0]): i[1] for i in stan[str(lid)]["images"]}})
        if len(out) == min(size, 50):
            break
    plan_file(n).write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(out)} ofert", [o["listing_id"] for o in out])


def apply_batch(n):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    batch = json.load(open(plan_file(n), encoding="utf-8"))
    if len(batch) > 50 or not PHOTO.exists():
        sys.exit("BŁĄD: partia > 50 albo brak pliku zdjęcia")
    for i, c in enumerate(batch, 1):
        lid = c["listing_id"]
        if done4(lid):
            print(i, lid, "pomijam (już zrobiona)")
            continue
        p, live = B.backup_unique(lid)
        if "error" in live or live["state"] != "active":
            print(i, lid, "ZATRZYMANA przed zapisem:", str(live.get("error") or live["state"])[:100])
            log(lid, "preflight", str(live.get("error") or live["state"])[:100], "pominięta")
            continue
        imgs = sorted(live.get("images", []), key=lambda x: x["rank"])
        before = {str(im["rank"]): im["listing_image_id"] for im in imgs}
        alts_before = [html.unescape(im.get("alt_text") or "") for im in imgs]
        if len(imgs) != 4 or any(before.get(k) != v for k, v in c["images_before"].items() if k != "4"):
            print(i, lid, "ZATRZYMANA przed zapisem: zdjęcia inne niż w planie", len(imgs))
            log(lid, "preflight", f"zdjęć {len(imgs)}", "pominięta")
            continue
        data, ct = base.multipart({"rank": "4", "overwrite": "true", "alt_text": ALT4}, ("image", PHOTO.name), PHOTO.read_bytes(), "image/jpeg")
        resp = api.request("POST", f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}/images", headers={"Content-Type": ct}, data=data, retries=1)
        ok = base.ok(resp)
        log(lid, "zdjecie_4_wymiana", {"backup": p.name, "id_przed": before.get("4")}, "ok" if ok else "błąd")
        if not ok:
            sys.exit(f"{lid}: BŁĄD wymiany zdjęcia: {str(resp)[:300]}")
        time.sleep(2)
        for attempt in range(4):
            after = api.get(f"/v3/application/listings/{lid}?includes=Images")
            im2 = sorted(after.get("images", []), key=lambda x: x["rank"])
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(im2), "zdj_1_3_ok": [x["listing_image_id"] for x in im2[:3]] == [before[k] for k in "123"],
                   "zdj_4_nowe": len(im2) == 4 and im2[3]["listing_image_id"] != before["4"], "id_4_przed": before["4"], "id_4_po": im2[3]["listing_image_id"] if len(im2) >= 4 else None,
                   "alt_ok": len(im2) == 4 and [html.unescape(x.get("alt_text") or "") for x in im2] == alts_before[:3] + [ALT4], "proba": attempt + 1}
            good = all(chk[k] for k in ("cena_ok", "stan_ok", "status_ok", "zdj_1_3_ok", "zdj_4_nowe", "alt_ok")) and chk["zdjec"] == 4
            if good:
                break
            time.sleep(3)
        log(lid, "weryfikacja", chk, "ok" if good else "niezgodność")
        print(i, lid, "ok" if good else "NIEZGODNOŚĆ " + str(chk))
        if not good:
            sys.exit("Weryfikacja niezgodna, przerywam.")
    print("Partia zakończona. Proszę sprawdzić próbkę w Etsy przed następną partią.")


if __name__ == "__main__":
    if sys.argv[1] == "plan":
        plan(int(sys.argv[2]), next((int(a[7:]) for a in sys.argv if a.startswith("--size=")), 50))
    elif sys.argv[1] == "apply":
        if "--apply" not in sys.argv:
            sys.exit("Brak flagi --apply: nic nie zapisuję.")
        apply_batch(int(sys.argv[2]))
