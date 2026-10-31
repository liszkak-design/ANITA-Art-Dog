#!/usr/bin/env python3
"""Dodanie zdjęcia 7 (oryginał bez edycji, urna z posrebrzaną płaskorzeźbą) do ofert tej grupy zoptymalizowanych BEZ zdjęcia 7 (np. koty z partii 2, zanim zdjęcie 7 weszło do skryptu).
  python3 -I scripts/zdjecie7_brelok.py plan N [--lid=ID[,ID]] [--size=K]   # dry-run: plans/zdjecie7_brelok_00N.json
  python3 -I scripts/zdjecie7_brelok.py apply N --apply                      # zapis (tylko po "tak" właścicielki dla partii N)
Zdjęcia 1-6 nie są zmieniane (te same id i kolejność). Nowe zdjęcie: rank 7, overwrite=false, alt text zatwierdzony przez właścicielkę.
Kopia zapasowa przed zapisem, log logs/zdjecie7_brelok_<id>.jsonl, wznowienie pomija zrobione. Limit API: etsy_api (okno 24 h).
"""
import csv
import datetime
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

ROOT = api.ROOT
PHOTO = ROOT / "media" / "urny_brelok" / "original_pies.jpg"
ALT7 = ("Unedited photo of the front of the wooden urn with a small silver plated relief of a dog, two small plaques with a name and dates, "
        "and a large plaque with a quote.")
TODAY = datetime.date.today()


def plan_file(n):
    return ROOT / "plans" / f"zdjecie7_brelok_{n:03d}.json"


def log(lid, step, info, status):
    with open(ROOT / "logs" / f"zdjecie7_brelok_{lid}.jsonl", "a") as fh:
        fh.write(json.dumps({"listing_id": lid, "id": step, "info": info, "status": status, "time": datetime.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")


def done7(lid):
    p = ROOT / "logs" / f"zdjecie7_brelok_{lid}.jsonl"
    return p.exists() and any(j["id"] == "weryfikacja" and j["status"] == "ok" for j in map(json.loads, p.read_text().splitlines()))


def plan(n, size):
    import csv as _csv
    stan = json.load(open(ROOT / "plans" / "brelok_stan_zywy.json", encoding="utf-8"))
    only = {int(x) for a in sys.argv if a.startswith("--lid=") for x in a[6:].split(",")}
    out = []
    for r in sorted(_csv.DictReader(open(ROOT / "plans" / "brelok_mapa_final.csv", encoding="utf-8")), key=lambda r: (int(r["wyswietlenia"]), int(r["listing_id"]))):
        lid = int(r["listing_id"])
        if (only and lid not in only) or not B.is_done(lid) or done7(lid):
            continue
        if any(x["step"] == "zdjecie_7" for x in _steps(lid)):
            continue
        out.append({"listing_id": lid, "wyswietlenia": int(r["wyswietlenia"]), "images_before": {str(i[0]): i[1] for i in stan[str(lid)]["images"]}, "alt_7": ALT7})
        if len(out) == min(size, 50):
            break
    plan_file(n).write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(out)} ofert", [o["listing_id"] for o in out])


def _steps(lid):
    res = []
    for f in glob.glob(str(ROOT / "logs" / f"zapis_{lid}_*.jsonl")):
        res += [{"step": j["id"]} for j in map(json.loads, open(f).read().splitlines()) if j["status"] == "ok"]
    return res


def apply_batch(n):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    if not plan_file(n).exists():
        sys.exit(f"BŁĄD: brak planu partii {n}")
    batch = json.load(open(plan_file(n), encoding="utf-8"))
    if len(batch) > 50 or not PHOTO.exists():
        sys.exit("BŁĄD: partia > 50 albo brak pliku zdjęcia")
    for i, c in enumerate(batch, 1):
        lid = c["listing_id"]
        if done7(lid):
            print(i, lid, "pomijam (już zrobiona)")
            continue
        p, live = B.backup_unique(lid)
        if "error" in live or live["state"] != "active":
            print(i, lid, "ZATRZYMANA przed zapisem:", str(live.get("error") or live["state"])[:100])
            log(lid, "preflight", str(live.get("error") or live["state"])[:100], "pominięta")
            continue
        imgs = sorted(live.get("images", []), key=lambda x: x["rank"])
        ids_before = {str(im["rank"]): im["listing_image_id"] for im in imgs[:6]}
        if len(imgs) not in (6, 7) or ids_before != {k: v for k, v in c["images_before"].items()}:
            print(i, lid, "ZATRZYMANA przed zapisem: zdjęcia inne niż w planie", len(imgs))
            log(lid, "preflight", f"zdjęć {len(imgs)}", "pominięta")
            continue
        if len(imgs) == 6:
            data, ct = base.multipart({"rank": "7", "overwrite": "false", "alt_text": c["alt_7"]}, ("image", PHOTO.name), PHOTO.read_bytes(), "image/jpeg")
            resp = api.request("POST", f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}/images", headers={"Content-Type": ct}, data=data, retries=1)
            st = "ok" if base.ok(resp) else "błąd"
            log(lid, "zdjecie_7", {"backup": p.name}, st)
            if st != "ok":
                sys.exit(f"{lid}: BŁĄD dodania zdjęcia: {str(resp)[:300]}\nPrzerywam; po wyjaśnieniu uruchom ponownie (wykonane oferty zostaną pominięte).")
            time.sleep(0.15)
        for attempt in range(4):
            after = api.get(f"/v3/application/listings/{lid}?includes=Images")
            im2 = sorted(after.get("images", []), key=lambda x: x["rank"])
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(im2), "zdj_1_6_ok": {str(x["rank"]): x["listing_image_id"] for x in im2[:6]} == ids_before,
                   "alt_7_ok": len(im2) == 7 and html.unescape(im2[6].get("alt_text") or "") == c["alt_7"],
                   "alt_1_6_ok": all(html.unescape(x.get("alt_text") or "") == html.unescape(y.get("alt_text") or "") for x, y in zip(im2[:6], imgs[:6])), "proba": attempt + 1}
            good = all(chk[k] for k in ("cena_ok", "stan_ok", "status_ok", "zdj_1_6_ok", "alt_7_ok", "alt_1_6_ok")) and chk["zdjec"] == 7
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
