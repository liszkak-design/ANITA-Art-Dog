#!/usr/bin/env python3
"""(Popiersia wiszące, "Hanging Statue", 79 ofert w sekcji 25604726.) Odczyt (tylko GET) stanu żywego ofert sekcji "Plaques with dog": 38 ofert "{rasa} Bust, Cold Cast Bronze Sculpture, Small dog bust ..." (plakietki same) = niska urna z małą posrebrzaną płaskorzeźbą.
Wejście: plans/hanging_sekcja_lista.json (oferty z lokalnej listy tytułów "Dog Loss Board"), nic nie pomija.
Wyjście: plans/hanging_stan_zywy.json. 1 zapytanie na ofertę (Images, Videos, Personalization, Translations w jednym wywołaniu).
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api

ROOT = api.ROOT
OUT = ROOT / "plans" / "hanging_stan_zywy.json"


def main():
    lst = [x for x in json.load(open(ROOT / "plans" / "hanging_sekcja_lista.json", encoding="utf-8")) if "Hanging Statue" in x["title"]]
    known = set()  # w tej sekcji nic nie pomijamy (decyzja właścicielki 01.11.2026)
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
                         "shipping": a.get("shipping_profile_id"), "section": a.get("shop_section_id"), "sku": a.get("skus", []), "dim": [a.get("item_length"), a.get("item_width"), a.get("item_height"), a.get("item_dimensions_unit")]}
        if len(out) % 20 == 0:
            OUT.write_text(json.dumps(out, ensure_ascii=False))
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print("zapisano", len(out), "ofert ->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
