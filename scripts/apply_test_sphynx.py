#!/usr/bin/env python3
"""Test zapisu na JEDNEJ ofercie (Sphynx, 678653467). Domyślnie dry-run (plans/zapis_sfinks_678653467_dryrun.json).
  python3 -I scripts/apply_test_sphynx.py            # dry-run, nic nie idzie do Etsy
  python3 -I scripts/apply_test_sphynx.py --apply    # zapis, wymaga zgody właścicielki i tokenu z listings_w
Kroki: tytuł/opis/tagi/materiały, personalizacja, zdjęcia (nadpisanie slotów), wideo, tłumaczenia (8 języków).
Pominięte w tym teście (decyzja 26.10.2026): SKU, shopping basket summary, GPSR, how it's made, occasion.
Wznawialność: kroki ze statusem ok w logs/zapis_<id>_<data>.jsonl są pomijane.
"""
import datetime
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import backup_listing

ROOT = api.ROOT
LID = 678653467
SHOP_ID = backup_listing.SHOP_ID
EAN_URL = "https://www.artdog.com.pl/allegro/zebraneEAN/5055882486553/"
CACHE = Path("/tmp/claude-0/-home-user-ANITA-Art-Dog/ffe4a3b0-655f-591d-929b-05322fdfe73b/scratchpad/img")
IMAGE_ORDER = ["3.jpg", "4.jpg", "5.jpg", "2.jpg", "6.jpg", "7.jpg", "original.jpg"]
VIDEO = ROOT / "video" / "video-ceramic-plaques-anita.mp4"
LANGS = ["de", "nl", "fr", "it", "pl", "pt", "es", "sv"]
TODAY = datetime.date.today()
LOG = ROOT / "logs" / f"zapis_{LID}_{TODAY}.jsonl"
DRY = ROOT / "plans" / f"zapis_sfinks_{LID}_dryrun.json"

PERSONALIZATION = [
    {"question_type": "dropdown", "question_text": "Do you want to personalize the plaque?", "required": False,
     "options": [{"label": "No, as shown"}, {"label": "Yes, personalize it"}]},
    {"question_type": "unlabeled_upload", "question_text": "Your photo (optional)", "required": False, "max_allowed_files": 1,
     "instructions": "Attach a clear photo of your pet, or send it later by Etsy message. Leave empty if you chose No."},
    {"question_type": "dropdown", "question_text": "Print style (if personalizing)", "required": False,
     "options": [{"label": "Original photo"}, {"label": "No background"}, {"label": "Sketch style"}]},
    {"question_type": "text_input", "question_text": "Name and dates (optional)", "required": False, "max_allowed_characters": 50,
     "instructions": "Name, or name and dates, as they should appear, e.g. Felix 12/29/2013 - 11/9/2026. Leave empty for no text."},
    {"question_type": "dropdown", "question_text": "Plaque orientation (if own photo)", "required": False,
     "options": [{"label": "Vertical"}, {"label": "Horizontal"}]},
]


def section(text, head):
    m = re.search(r"^## " + re.escape(head) + r".*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else None


def codeblock(s):
    return re.search(r"```\n(.*?)\n```", s, re.S).group(1)


def parse_en():
    t = (ROOT / "plans" / f"test_sfinks_{LID}.md").read_text()
    title = re.search(r"^- po \(\d+ zn\.\): (.+)$", section(t, "Tytuł"), re.M).group(1).strip()
    tags = [x.strip() for x in section(t, "Tagi (po").split("\n")[0].split(",")]
    mat = re.search(r"^- po: (.+)$", section(t, "Materiały"), re.M).group(1).strip()
    alts = {}
    for f, alt in re.findall(r"^\d+\. `([^`]+)`(?: \(główne\))?: (.+)$", section(t, "Zdjęcia"), re.M):
        alts[f] = alt.strip()
    return {"title": title, "description": codeblock(section(t, "Opis (po)")), "tags": tags, "materials": [mat], "alts": alts}


def parse_lang(code):
    t = (ROOT / "plans" / f"test_sfinks_{LID}_{code.upper()}.md").read_text()
    title = section(t, "Tytuł").strip()
    tags = [re.sub(r"\s*\(\d+\)$", "", x.strip()) for x in section(t, "Tagi").split("\n")[0].split(", ")]
    return {"title": title, "description": codeblock(section(t, "Opis")), "tags": tags}


def validate(en, trans):
    prob = []
    if len(en["title"]) > 140:
        prob.append(f"tytuł EN {len(en['title'])} zn.")
    if len(en["tags"]) != 13 or any(len(x) > 20 for x in en["tags"]):
        prob.append("tagi EN: nie 13 lub za długie: " + str([x for x in en["tags"] if len(x) > 20]))
    for f in IMAGE_ORDER:
        if f not in en["alts"]:
            prob.append(f"brak alt textu dla {f}")
        elif len(en["alts"][f]) > 500:
            prob.append(f"alt {f} za długi")
    for q in PERSONALIZATION:
        if not 1 <= len(q["question_text"]) <= 45:
            prob.append("pytanie >45: " + q["question_text"])
        if len(q.get("instructions", "")) > 120:
            prob.append("instrukcja >120: " + q["question_text"])
        for o in q.get("options", []):
            if not 1 <= len(o["label"]) <= 20:
                prob.append("opcja >20: " + o["label"])
    for c, d in trans.items():
        if len(d["title"]) > 140:
            prob.append(f"tytuł {c} {len(d['title'])} zn.")
        if len(d["tags"]) != 13 or any(len(x) > 20 for x in d["tags"]):
            prob.append(f"tagi {c}: " + str([x for x in d["tags"] if len(x) > 20]) + f" (liczba {len(d['tags'])})")
    if not VIDEO.exists():
        prob.append("brak pliku wideo")
    return prob


def build_steps(en, trans):
    base = f"/v3/application/shops/{SHOP_ID}/listings/{LID}"
    steps = [{"id": "listing", "method": "PATCH", "path": base, "kind": "form",
              "fields": {"title": en["title"], "description": en["description"], "tags": ",".join(en["tags"]),
                         "materials": ",".join(en["materials"])}},
             {"id": "personalizacja", "method": "POST", "path": base + "/personalization", "kind": "json",
              "fields": {"personalization_questions": PERSONALIZATION}}]
    for rank, f in enumerate(IMAGE_ORDER, 1):
        steps.append({"id": f"zdjecie_{rank}_{f}", "method": "POST", "path": base + "/images", "kind": "multipart",
                      "fields": {"rank": str(rank), "overwrite": "true" if rank == 1 else "false", "alt_text": en["alts"][f]},
                      "file": ("image", f)})
    steps.append({"id": "wideo", "method": "POST", "path": base + "/videos", "kind": "multipart",
                  "fields": {"name": VIDEO.name}, "file": ("video", str(VIDEO))})
    for c in LANGS:
        d = trans[c]
        steps.append({"id": f"tlumaczenie_{c}", "method": "POST", "path": base + f"/translations/{c}", "kind": "form",
                      "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return steps


def multipart(fields, fname, fbytes, ctype):
    b = uuid.uuid4().hex
    out = b""
    for k, v in fields.items():
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    out += f'--{b}\r\nContent-Disposition: form-data; name="{fname[0]}"; filename="{fname[1]}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
    return out + fbytes + f"\r\n--{b}--\r\n".encode(), f"multipart/form-data; boundary={b}"


def fetch_image(f):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f
    if f == "original.jpg":
        return ROOT / "media" / "plytki_with_photo" / "original.jpg"
    if not p.exists():
        with urllib.request.urlopen(EAN_URL + f, timeout=120) as r:
            p.write_bytes(r.read())
    return p


def send(step):
    k = step["kind"]
    if k == "json":
        data, ct = json.dumps(step["fields"]).encode(), "application/json"
    elif k == "form":
        data, ct = urllib.parse.urlencode(step["fields"]).encode(), "application/x-www-form-urlencoded"
    else:
        part, src = step["file"]
        path = fetch_image(src) if part == "image" else Path(src)
        ctype = "image/jpeg" if part == "image" else "video/mp4"
        data, ct = multipart(step["fields"], (part, path.name), path.read_bytes(), ctype)
    return api.request(step["method"], step["path"], headers={"Content-Type": ct}, data=data, retries=1)


def done_ids():
    if not LOG.exists():
        return set()
    return {j["id"] for j in map(json.loads, LOG.read_text().splitlines()) if j["status"] == "ok"}


def log(step_id, field, before, after, status):
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(json.dumps({"listing_id": LID, "id": step_id, "field": field, "before": before, "after": after,
                             "status": status, "time": datetime.datetime.now().isoformat(timespec="seconds")},
                            ensure_ascii=False) + "\n")


def ok(resp):
    return isinstance(resp, dict) and "error" not in resp


def apply(steps):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token nie ma zakresu listings_w. Najpierw autoryzacja z listings_w.")
    p, before = backup_listing.backup(LID)
    print("backup:", p.name)
    bl = before["listing"]
    if bl.get("videos"):
        sys.exit("BŁĄD: oferta ma już wideo, zgłoś i nie dodawaj (DECYZJE.md, 9)")
    done = done_ids()
    for s in steps:
        if s["id"] in done:
            print("pomijam (wykonane):", s["id"])
            continue
        resp = send(s)
        if s["id"].startswith("tlumaczenie_") and not ok(resp) and "exist" in str(resp).lower():
            s = {**s, "method": "PUT"}
            resp = send(s)
        status = "ok" if ok(resp) else "błąd"
        field = s["id"]
        log(s["id"], field, "backup/" + p.name, {k: (v if len(str(v)) < 200 else str(v)[:200] + "...") for k, v in s["fields"].items()}, status)
        print(s["id"], status, "" if status == "ok" else str(resp)[:300])
        if status != "ok":
            sys.exit("Przerywam po błędzie (po poprawce uruchom ponownie, wykonane kroki zostaną pominięte).")
        time.sleep(0.2)
    after = api.get(f"/v3/application/listings/{LID}?includes=Images,Videos,Translations,Personalization")
    chk = {"price_przed": bl["price"], "price_po": after["price"], "quantity_przed": bl["quantity"], "quantity_po": after["quantity"],
           "state_przed": bl["state"], "state_po": after["state"],
           "zdjecia": [(i["rank"], (i.get("alt_text") or "")[:40]) for i in after.get("images", [])],
           "wideo": len(after.get("videos", []))}
    log("weryfikacja", "cena/stan/status", {k: v for k, v in chk.items() if k.endswith("przed")}, chk, "ok")
    print(json.dumps(chk, ensure_ascii=False, indent=1))


def main():
    en = parse_en()
    trans = {c: parse_lang(c) for c in LANGS}
    prob = validate(en, trans)
    steps = build_steps(en, trans)
    DRY.write_text(json.dumps({"listing_id": LID, "uwagi_walidacji": prob, "pominiete": ["SKU", "shopping basket summary", "GPSR", "how it's made", "occasion"],
                               "kroki": steps}, ensure_ascii=False, indent=1))
    print(f"kroków: {len(steps)}; problemy walidacji: {len(prob)}")
    for x in prob:
        print(" -", x)
    print("dry-run zapisany:", DRY.relative_to(ROOT))
    if "--apply" in sys.argv:
        if prob:
            sys.exit("BŁĄD: są problemy walidacji, nie zapisuję.")
        apply(steps)


if __name__ == "__main__":
    main()
