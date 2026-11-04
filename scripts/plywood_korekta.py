#!/usr/bin/env python3
"""Korekta: dodanie plywood do materiałów (tekstowych i z listy Etsy) we wszystkich zoptymalizowanych urnach (decyzja właścicielki 04.11.2026).
ZASADA: plywood jest DOPISYWANE do istniejących wartości, wszystkie obecne zapisy zostają bez zmian (odczyt na żywo przed zapisem). Nic poza materiałami nie jest zmieniane.
  python3 -I scripts/plywood_korekta.py plan                     # plan bez zapytań do Etsy: plans/plywood_plan.csv (partie po 50, od najmniej oglądanych)
  python3 -I scripts/plywood_korekta.py apply N --apply          # zapis partii N (tylko po "tak" właścicielki)
Na ofertę: odczyt (oferta + właściwości) i kopia zapasowa backup/<id>_<data>_plywood.json, PATCH materials (tekst), PUT właściwości Material z dopisanym Plywood (id 5199),
weryfikacja z odpowiedzi API, log logs/zapis_<id>_<data>.jsonl (kroki plywood_*). Pomija oferty, które już mają plywood w obu miejscach. Limit API: etsy_api (stop 9000)."""
import csv
import datetime
import glob
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
PLAN = ROOT / "plans" / "plywood_plan.csv"
PLY_ID, PLY_NAME = 5199, "Plywood"
TODAY = datetime.date.today()
# znane obecne wartości (z skryptów grup), gdy skrypt zmieniał materiały tekstowe; None = bez zmian względem kopii zapasowej z optymalizacji
GROUPS = {
    "urny_zdjecie": {"text": None, "lista": U.MATERIAL_VALUES[1]},
    "urny_grafika_psy": {"text": None, "lista": U.MATERIAL_VALUES[1]},
    "urny_relief": {"text": "wood,brass handles,silver plated metal relief", "lista": "Brass,Pine,Birch,Metal"},
    "urny_niskie": {"text": "wood,silver plated metal relief", "lista": "Pine,Birch,Metal"},
    "urny_relief_38": {"text": "wood,brass handles,cold cast bronze relief", "lista": "Brass,Pine,Birch"},
}


def add_plywood_text(mats):
    m = list(mats)
    if any(x.lower() == "plywood" for x in m):
        return m
    if "wood" in m:
        m.insert(m.index("wood") + 1, "plywood")
    else:
        m.append("plywood")
    return m


def first_backup(lid):
    fs = sorted(glob.glob(str(ROOT / "backup" / f"{lid}_*.json")))
    fs = [f for f in fs if "plywood" not in f]
    return json.load(open(fs[0], encoding="utf-8")) if fs else None


def collect():
    rows = []
    # urny ze zdjęciem (partie 0-6): id z planów, wyświetlenia z CSV
    for f in sorted(glob.glob(str(ROOT / "plans" / "partia_urny_00*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            rows.append(("urny_zdjecie", int(r["listing_id"]), int(r.get("wyswietlenia") or 0), r["tytul_po"]))
    for grp, fn in (("urny_grafika_psy", "grafika_stan_zywy.json"), ("urny_relief", "brelok_stan_zywy.json"), ("urny_niskie", "brelok_niskie_stan_zywy.json"), ("urny_relief_38", "relief_stan_zywy.json")):
        d = json.load(open(ROOT / "plans" / fn, encoding="utf-8"))
        for lid, v in d.items():
            rows.append((grp, int(lid), int(v.get("views", 0)), v["title"]))
    seen, out = set(), []
    for g, lid, views, title in rows:
        if lid in seen or not B.is_done(lid):
            continue
        seen.add(lid)
        out.append((g, lid, views, title))
    return out


def plan():
    rows = collect()
    rows.sort(key=lambda r: (r[2], r[1]))  # od najmniej do najczęściej oglądanych
    with open(PLAN, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "partia", "listing_id", "grupa", "wyswietlenia", "tytul", "tekst_oczekiwany_przed", "tekst_po", "lista_oczekiwana_przed", "lista_po", "uwagi"])
        for i, (g, lid, views, title) in enumerate(rows, 1):
            bk = first_backup(lid)
            cur_text = GROUPS[g]["text"].split(",") if GROUPS[g]["text"] else (bk["listing"]["materials"] if bk else [])
            uw = "" if (GROUPS[g]["text"] or bk) else "brak kopii zapasowej"
            lista = GROUPS[g]["lista"].split(",")
            new_lista = lista + ([PLY_NAME] if PLY_NAME not in lista else [])
            w.writerow([i, (i - 1) // 50 + 1, lid, g, views, title[:90], ",".join(cur_text), ",".join(add_plywood_text(cur_text)), ",".join(lista), ",".join(new_lista), uw])
    r = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    from collections import Counter
    print("ofert:", len(r), "| partii:", max(int(x["partia"]) for x in r), "| grupy:", dict(Counter(x["grupa"] for x in r)))
    print("lista Material po zmianie, liczba wartości:", dict(Counter(len(x["lista_po"].split(",")) for x in r)))
    print("uwagi:", Counter(x["uwagi"] for x in r if x["uwagi"]))


def apply_batch(n):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    rows = [r for r in csv.DictReader(open(PLAN, encoding="utf-8")) if int(r["partia"]) == n]
    if not rows or len(rows) > 50:
        sys.exit("BŁĄD: brak partii w planie albo większa niż 50")
    summary = ROOT / "logs" / f"partia_plywood_{n:03d}_{TODAY}.jsonl"
    print(f"plywood, partia {n}: {len(rows)} ofert")
    for i, r in enumerate(rows, 1):
        lid = int(r["listing_id"])
        if "plywood_weryfikacja" in B.done_steps(lid):
            print(i, lid, "pomijam (już zrobiona)")
            continue
        live = api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization")
        props = api.get(f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}/properties")
        if "error" in live or "error" in props:
            sys.exit(f"{lid}: błąd odczytu: {str(live.get('error') or props.get('error'))[:150]}")
        if live["state"] != "active":
            print(i, lid, "ZATRZYMANA: status", live["state"])
            open(summary, "a").write(json.dumps({"listing_id": lid, "status": "pominięta", "powod": "status " + live["state"]}, ensure_ascii=False) + "\n")
            continue
        bp = ROOT / "backup" / f"{lid}_{TODAY}_plywood.json"
        k = 1
        while bp.exists():
            k += 1
            bp = ROOT / "backup" / f"{lid}_{TODAY}_plywood_{k}.json"
        bp.write_text(json.dumps({"listing": live, "properties": props}, ensure_ascii=False, indent=1))
        mat = next((p for p in props.get("results", []) if p["property_id"] == B.MATERIAL_PROPERTY), None)
        cur_text = list(live["materials"])
        cur_ids = list(mat["value_ids"]) if mat else []
        cur_names = list(mat["values"]) if mat else []
        new_text = add_plywood_text(cur_text)
        new_ids = cur_ids + ([PLY_ID] if PLY_ID not in cur_ids else [])
        new_names = cur_names + ([PLY_NAME] if PLY_ID not in cur_ids else [])
        b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
        if new_text != cur_text:
            resp = base.send({"kind": "form", "method": "PATCH", "path": b, "fields": {"materials": ",".join(new_text)}})
            ok = base.ok(resp) and sorted(resp.get("materials", [])) == sorted(new_text)
            B.zlog(lid, "plywood_tekst", {"materials": cur_text}, {"materials": new_text}, "ok" if ok else "błąd")
            if not ok:
                open(summary, "a").write(json.dumps({"listing_id": lid, "status": "błąd", "krok": "plywood_tekst", "odpowiedź": str(resp)[:300]}, ensure_ascii=False) + "\n")
                sys.exit(f"{lid}: BŁĄD plywood_tekst: {str(resp)[:300]}")
            time.sleep(0.15)
        if PLY_ID not in cur_ids:
            resp = base.send({"kind": "form", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "fields": {"value_ids": ",".join(map(str, new_ids)), "values": ",".join(new_names)}})
            ok = base.ok(resp) and sorted(resp.get("value_ids", [])) == sorted(new_ids)
            B.zlog(lid, "plywood_lista", {"value_ids": cur_ids, "values": cur_names}, {"value_ids": new_ids, "values": new_names}, "ok" if ok else "błąd")
            if not ok:
                open(summary, "a").write(json.dumps({"listing_id": lid, "status": "błąd", "krok": "plywood_lista", "odpowiedź": str(resp)[:300]}, ensure_ascii=False) + "\n")
                sys.exit(f"{lid}: BŁĄD plywood_lista: {str(resp)[:300]}")
            time.sleep(0.15)
        B.zlog(lid, "plywood_weryfikacja", {"tekst": cur_text, "lista": cur_names}, {"tekst": new_text, "lista": new_names}, "ok")
        open(summary, "a").write(json.dumps({"listing_id": lid, "status": "ok", "tekst_przed": cur_text, "tekst_po": new_text, "lista_przed": cur_names, "lista_po": new_names}, ensure_ascii=False) + "\n")
        print(i, lid, "ok", ",".join(new_names))
    print("Partia zakończona. Proszę sprawdzić próbkę w Etsy przed następną partią.")


if __name__ == "__main__":
    if sys.argv[1] == "plan":
        plan()
    elif sys.argv[1] == "apply":
        if "--apply" not in sys.argv:
            sys.exit("Brak flagi --apply: nic nie zapisuję.")
        apply_batch(int(sys.argv[2]))
