#!/usr/bin/env python3
"""Odczyt (tylko GET) stanu żywego ofert sekcji "Urn with relief" bez wideo = urna z małą posrebrzaną płaskorzeźbą.
Wejście: plans/brelok_sekcja_lista.json (lista sekcji 25445424), pomija 38 ofert z reliefem "cold cast bronze" (plans/relief_custom_urn_38.csv).
Wyjście: plans/brelok_stan_zywy.json. 1 zapytanie na ofertę (Images, Videos, Personalization, Translations w jednym wywołaniu).
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api

ROOT = api.ROOT
OUT = ROOT / "plans" / "brelok_stan_zywy.json"


def main():
    lst = json.load(open(ROOT / "plans" / "brelok_sekcja_lista.json", encoding="utf-8"))
    known = {int(r["id"]) for r in csv.DictReader(open(ROOT / "plans" / "relief_custom_urn_38.csv", encoding="utf-8"))}
    out = json.load(open(OUT, encoding="utf-8")) if OUT.exists() else {}
    for x in lst:
        lid = x["listing_id"]
        if lid in known or str(lid) in out:
            continue
        a = api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Personalization,Translations")
        if "error" in a or "listing_id" not in a:
            sys.exit(f"BŁĄD odczytu {lid}: {str(a)[:200]}")
        out[str(lid)] = {"title": a["title"], "views": a.get("views", 0), "fav": a.get("num_favorers", 0), "state": a["state"], "price": a["price"]["amount"],
                         "qty": a["quantity"], "videos": len(a.get("videos", [])), "who_made": a["who_made"], "materials": a["materials"], "tags": a["tags"],
                         "images": [[i["rank"], i["listing_image_id"], i["url_fullxfull"], i.get("alt_text")] for i in sorted(a.get("images", []), key=lambda i: i["rank"])],
                         "personalization": [[q.get("question_text"), q.get("required"), q.get("question_type")] for q in (a.get("personalization") or {}).get("personalization_questions", [])],
                         "translations": sorted(k for k, v in (a.get("translations") or {}).items() if v and k != "en-US"),
                         "shipping": a.get("shipping_profile_id"), "section": a.get("shop_section_id")}
        if len(out) % 20 == 0:
            OUT.write_text(json.dumps(out, ensure_ascii=False))
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print("zapisano", len(out), "ofert ->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
