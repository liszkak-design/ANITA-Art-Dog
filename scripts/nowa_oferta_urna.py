#!/usr/bin/env python3
"""Nowa oferta urny dla folderu "155. Laekenois Dog" (EAN 5056739236475) jako SZKIC (publikacja po akceptacji właścicielki).
  python3 -I scripts/nowa_oferta_urna.py            # dry-run: plans/nowa_oferta_155_dryrun.json
  python3 -I scripts/nowa_oferta_urna.py --apply    # tworzy szkic i wgrywa wszystkie elementy (wznawialne po logu logs/nowa_oferta_155.jsonl)
Ustawienia (cena, ilość, kategoria, profil wysyłki, polityka zwrotów, sekcja, czas realizacji) skopiowane z działającej urny 674223007;
teksty z tych samych szablonów co pozostałe urny; zdjęcia 1-6 z serwera (zdjęcia 2-6 identyczne z istniejącymi w ofertach), 7 = original psa.
Nie ustawiamy: SKU, GPSR, shopping basket summary (ręcznie w Etsy).
"""
import csv
import datetime
import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import apply_test_sphynx as base
import batch as B
import batch_urny as U

ROOT = api.ROOT
SHOP = B.SHOP_ID
EAN = "5056739236475"
FOLDER = ("091. urna z plytka ceramiczna", "155. Laekenois Dog 5056739236475")
FILM = "laekenois-dog-5056739236475.mp4"
RID, SPECIES = "R281", "pies"
SEED = 155000  # stały, żeby warianty tekstów były powtarzalne (nowa oferta nie ma jeszcze ID)
SRC_LISTING = 674223007
LOG = ROOT / "logs" / "nowa_oferta_155.jsonl"
DRY = ROOT / "plans" / "nowa_oferta_155_dryrun.json"
PROPS = [(200, "3", "Brown"), (46803063641, "28", "Pet loss"), (B.MATERIAL_PROPERTY, U.MATERIAL_VALUES[0], U.MATERIAL_VALUES[1])]
FORM = {"Content-Type": "application/x-www-form-urlencoded"}


def log(step, info, status):
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(json.dumps({"id": step, "info": info, "status": status, "time": datetime.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")


def done():
    if not LOG.exists():
        return {}
    out = {}
    for j in map(json.loads, LOG.read_text().splitlines()):
        if j["status"] == "ok":
            out[j["id"]] = j["info"]
    return out


def build():
    R = B.rasy()
    rr = R[(SPECIES, RID)]
    fw = B.feature_words()
    typ = B.e_class().get(RID, "")
    breed = rr["Nazwa EN (główna)"]
    row = {"gatunek": SPECIES, "ean": EAN, "nazwa_w_tytule": "Laekenois Dog", "folder": FOLDER[1], "film_bez_brand": FILM}
    c = {"lid": SEED, "rr": rr, "breed": breed, "species": SPECIES, "key": "", "typ": typ, "row": row}
    en, trans = U.render(c, fw)
    prob = U.check(en, trans) + (["brak języków"] if len(trans) != 8 else [])
    return c, en, trans, prob


def film_url():
    return U.VIDEO_BASE + urllib.parse.quote(FOLDER[0]) + "/" + urllib.parse.quote(FOLDER[1]) + "/" + FILM


def main():
    c, en, trans, prob = build()
    src = api.get(f"/v3/application/listings/{SRC_LISTING}")
    draft = {"quantity": src["quantity"], "title": en["title"], "description": en["description"], "price": f"{src['price']['amount'] / src['price']['divisor']:.2f}",
             "who_made": "collective", "when_made": "made_to_order", "taxonomy_id": src["taxonomy_id"], "shipping_profile_id": src["shipping_profile_id"],
             "readiness_state_id": src["readiness_state_id"], "return_policy_id": src["return_policy_id"], "shop_section_id": src["shop_section_id"],
             "materials": ",".join(src["materials"]), "tags": ",".join(en["tags"]), "is_supply": "false", "should_auto_renew": "true", "type": "physical"}
    plan = {"szkic": draft, "alts": en["alts"], "film_rasy": film_url(), "film_gatunku": str(U.SPECIES_VIDEO[SPECIES].name), "problemy": prob,
            "zdjecia": [f"{U.EAN_BASE}{EAN}/{k}.jpg" for k in range(1, 7)] + ["media/urny_with_photo/" + U.ORIGINALS[SPECIES]],
            "ABC": en["ABC"], "synonim": en["synonim"], "zdrobnienie": en["nick"], "tlumaczenia": trans}
    DRY.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print("tytuł:", en["title"], len(en["title"]), "| problemy:", prob or "brak")
    print("szkic:", {k: v for k, v in draft.items() if k not in ("description",)})
    if prob:
        sys.exit("BŁĄD: problemy kontroli")
    if "--apply" not in sys.argv:
        sys.exit("dry-run: nic nie zapisuję")
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    d = done()
    if "szkic" in d:
        lid = d["szkic"]
        print("szkic już istnieje:", lid)
    else:
        r = api.request("POST", f"/v3/application/shops/{SHOP}/listings", headers=FORM, data=urllib.parse.urlencode(draft).encode(), retries=1)
        if not (isinstance(r, dict) and r.get("listing_id")):
            log("szkic", str(r)[:300], "błąd")
            sys.exit("BŁĄD tworzenia szkicu: " + str(r)[:400])
        lid = r["listing_id"]
        log("szkic", lid, "ok")
        print("utworzono szkic:", lid, "stan:", r.get("state"))
    b = f"/v3/application/shops/{SHOP}/listings/{lid}"
    steps = []
    for pid, vid, val in PROPS:
        steps.append((f"wlasciwosc_{pid}", "PUT", f"{b}/properties/{pid}", "form", {"value_ids": vid, "values": val}))
    steps.append(("how_its_made", "PATCH", b, "form", {"who_made": "collective", "when_made": "made_to_order", "is_supply": "false"}))
    steps.append(("personalizacja", "POST", b + "/personalization", "json", {"personalization_questions": U.personalization(SPECIES)}))
    for k in range(1, 7):
        steps.append((f"zdjecie_{k}", "POST", b + "/images", "image", {"rank": str(k), "overwrite": "false", "alt_text": en["alts"][k], "_file": f"{k}.jpg"}))
    steps.append(("zdjecie_7_original", "POST", b + "/images", "image", {"rank": "7", "overwrite": "false", "alt_text": en["alts"][7], "_file": "original"}))
    steps.append(("wideo_1_gatunek", "POST", b + "/videos", "video", {"name": U.SPECIES_VIDEO[SPECIES].name, "_src": str(U.SPECIES_VIDEO[SPECIES])}))
    steps.append(("wideo_2_rasa", "POST", b + "/videos", "video", {"name": FILM, "_src": film_url()}))
    for code, t in trans.items():
        steps.append((f"tlumaczenie_{code}", "POST", b + f"/translations/{code}", "form", {"title": t["title"], "description": t["description"], "tags": ",".join(t["tags"])}))
    for sid, method, path, kind, fields in steps:
        if sid in d:
            continue
        if kind == "json":
            data, hd = json.dumps(fields).encode(), {"Content-Type": "application/json"}
        elif kind == "form":
            data, hd = urllib.parse.urlencode(fields).encode(), FORM
        elif kind == "image":
            f = {k: v for k, v in fields.items() if k != "_file"}
            if fields["_file"] == "original":
                p = ROOT / "media" / "urny_with_photo" / U.ORIGINALS[SPECIES]
            else:
                p = U.download(f"{U.EAN_BASE}{EAN}/{fields['_file']}", U.CACHE / EAN / fields["_file"])
            data, ct = base.multipart(f, ("image", p.name), p.read_bytes(), "image/jpeg")
            hd = {"Content-Type": ct}
        else:
            src = fields["_src"]
            p = Path(src) if not src.startswith("http") else U.download(src, U.CACHE / "wideo" / fields["name"])
            data, ct = base.multipart({"name": fields["name"]}, ("video", p.name), p.read_bytes(), "video/mp4")
            hd = {"Content-Type": ct}
        r = api.request(method, path, headers=hd, data=data, retries=1)
        if sid.startswith("tlumaczenie_") and not base.ok(r) and "exist" in str(r).lower():
            r = api.request("PUT", path, headers=hd, data=data, retries=1)
        ok = base.ok(r)
        log(sid, "" if ok else str(r)[:300], "ok" if ok else "błąd")
        print(sid, "ok" if ok else "BŁĄD " + str(r)[:300])
        if not ok:
            sys.exit("Przerywam po błędzie; po wyjaśnieniu uruchom ponownie (wykonane kroki zostaną pominięte).")
        time.sleep(0.15)
    for attempt in range(4):
        a = api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization")
        imgs = sorted(a.get("images", []), key=lambda x: x["rank"])
        import html
        chk = {"stan": a["state"], "tytul_ok": html.unescape(a["title"]) == en["title"], "zdjec": len(imgs),
               "alt_ok": all(html.unescape(i.get("alt_text") or "") == en["alts"][i["rank"]] for i in imgs) if len(imgs) == 7 else False,
               "wideo": len(a.get("videos", [])), "pytan": len(a["personalization"]["personalization_questions"]),
               "tlumaczen": sum(1 for k, v in a["translations"].items() if v and k != "en-US"), "cena": a["price"]["amount"], "ilosc": a["quantity"]}
        good = chk["stan"] == "draft" and chk["tytul_ok"] and chk["zdjec"] == 7 and chk["alt_ok"] and chk["wideo"] == 2 and chk["pytan"] == 5 and chk["tlumaczen"] == 8
        if good:
            break
        time.sleep(3)
    log("weryfikacja", chk, "ok" if good else "niezgodność")
    print("listing_id:", lid, "weryfikacja:", "ok" if good else "NIEZGODNOŚĆ", chk)
    print("podgląd (szkic):", f"https://www.etsy.com/your/shops/me/tools/listings/{lid}")


if __name__ == "__main__":
    main()
