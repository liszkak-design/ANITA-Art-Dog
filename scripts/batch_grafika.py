#!/usr/bin/env python3
"""Optymalizacja urn z płytką "with Graphics", tylko psy (100 ofert; mapowanie plans/grafika_mapa_wstepna.csv, stan żywy plans/grafika_stan_zywy.json).
  python3 -I scripts/batch_grafika.py raport                      # kontrola wszystkich 100 ofert bez zapisu (plans/grafika_mapa.csv)
  python3 -I scripts/batch_grafika.py plan N [--lid=ID[,ID]] [--size=K]   # dry-run partii N (plans/partia_grafika_00N.csv i _dryrun.json)
  python3 -I scripts/batch_grafika.py apply N --apply             # zapis do Etsy (tylko po "tak" właścicielki dla partii N)
Zakres na ofertę: kopia zapasowa; tytuł (do 14 słów), opis, 13 tagów, Materials (Ceramic, Brass, Pine, Birch; materiały tekstowe bez zmian),
personalizacja (5 pytań: imię i daty wymagane, cytat, zdjęcie, styl wydruku), alt texty zdjęć 1-6 (zdjęcia NIE są wymieniane),
film 1 = video/video-urn-graphics-dogs-anita.mp4, film 2 = z folderu rasy (bez "brand"), 8 tłumaczeń. Kolejność: od najmniej do najczęściej oglądanych.
Limit API: etsy_api liczy okno 24 h dla wszystkich wywołań.
"""
import csv
import datetime
import glob
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import apply_test_sphynx as base
import batch as B
import batch_urny as U
import batch_relief as R

ROOT = api.ROOT
TPL = ROOT / "templates"
BASE_V = "https://www.artdog.com.pl/VIDEO/IV%20tura/096.%20Urny%20psy%20geom/"
STAN = ROOT / "plans" / "grafika_stan_zywy.json"
INDEX = ROOT / "plans" / "grafika_foldery_index.csv"
MAPA_W = ROOT / "plans" / "grafika_mapa_wstepna.csv"
MAPA = ROOT / "plans" / "grafika_mapa.csv"
CACHE = B.CACHE.parent / "grafika"
VIDEO1 = ROOT / "video" / "video-urn-graphics-dogs-anita.mp4"
MAT_VALUES = U.MATERIAL_VALUES  # Ceramic, Brass, Pine, Birch (zatwierdzone 30.10.2026)
NAME_FIX = {"Borzoi Russian Wolfhound": "Borzoi", "Mastino Napoletano": "Neapolitan Mastiff", "Staffordshire Bullterrier": "Staffordshire Bull Terrier"}
# decyzje właścicielki 30.10.2026: słowa odmian w tytule; nigdy "Natural Ears"
OWNER_FEATURE = {661086082: "cropped ears", 661028156: "cropped ears", 661092134: "cropped ears", 674937239: "cropped ears",
                 674927183: "Chihuahua Long-haired", 674865781: "Chihuahua Short-haired",
                 661025192: "Dachshund Smooth-haired", 674868753: "Dachshund Long-haired", 661100430: "Dachshund Wire-haired"}
# skróty z tytułów ofert -> rasa z Rasy.xlsx (jak w już zatwierdzonych urnach i płytkach: Amstaff = R027, Labrador = R002, Dachshund = R025); do potwierdzenia
RID_OVERRIDE = {660991342: "R027", 661030046: "R002", 661100430: "R025"}
LANG_ALL = U.LANG_ALL
TODAY = datetime.date.today()
MAX_WORDS = 14
PHOTO_TAG = re.compile(r"foto|zdj|photo|fotograf", re.I)
EN_CORE = ["urn for pet ashes", "personalized urn", "wooden urn", "cremation urn", "pet loss gift", "unique dog urn", "dog memorial"]
EN_POOL = ["handmade urn", "keepsake box", "in loving memory", "rainbow bridge", "pet bereavement", "custom pet urn", "always in my heart", "pet remembrance",
           "pet sympathy", "faithful friend", "furry friend", "last goodbye", "pet funeral", "best friend", "pet tribute", "forever loved",
           "urn with quote", "urn with photo", "photo urn"]
ALT1 = ("Wooden urn for ashes with an oval ceramic plaque showing a geometric portrait of {ART} {BREED} dog, a paw-shaped plaque with a quote, "
        "and a name and dates.")
QUOTE_DEFAULT = "You left paw prints on my heart"

_EN = {}


def en():
    if _EN:
        return _EN
    t = (TPL / "grafika_propozycja_tekstow.md").read_text(encoding="utf-8")
    for x in EN_CORE + EN_POOL:
        assert x in t, x
    s1 = R.sec(t, "## 1. Tytuły", "## 2.")
    _EN["titles"] = re.findall(r"^\d\. (\{BREED\}.*?) \(\d+\)$", s1, re.M)
    s3 = R.sec(t, "## 3. Pierwszy akapit", "## 4.")
    bank = lambda s: [(m.group(2) or "", m.group(3)) for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", s, re.M)]
    iA, iB, iC = s3.index("**A bez"), s3.index("**B (zast"), s3.index("**C (pełna")
    _EN["A"], _EN["B"], _EN["C"] = bank(s3[iA:iB]), bank(s3[iB:iC]), bank(s3[iC:])
    s4 = R.sec(t, "## 4. Sekcje stałe", "## 5.")
    _EN["fixed"] = re.search(r"```\n(.*?)\n```", s4, re.S).group(1)
    assert len(_EN["titles"]) == 6 and len(_EN["A"]) == 15 and len(_EN["B"]) == 4 and len(_EN["C"]) == 5, (len(_EN["titles"]), len(_EN["A"]), len(_EN["B"]), len(_EN["C"]))
    assert QUOTE_DEFAULT in _EN["fixed"]
    return _EN


def words(t):
    return len(t.replace(",", " ").split())


def pick_title(lid, pats, name):
    start = U.pick(lid, "T", len(pats))
    fallback = None
    for k in range(len(pats)):
        i = (start + k) % len(pats)
        t = re.sub(r"\s+", " ", pats[i].replace("{BREED}", name))
        if name.lower().endswith(" dog"):
            t = t.replace(name + " Dog ", name + " ", 1)  # bez "Dog Dog"
        if fallback is None:
            fallback = (t, i + 1)
        if len(t) <= 140 and words(t) <= MAX_WORDS:
            return t, i + 1
    return fallback[0], fallback[1]  # żaden wzorzec nie mieści się: oferta zostanie zgłoszona w check()


def en_description(lid, breed, nick, syn):
    E = en()
    parts, chosen, nicks = [], {}, 0
    for slot in "ABC":
        if slot == "A":
            want = "N" if nick else ("S" if syn else "")
            opts = [(f, x) for f, x in E["A"] if f == want]
        else:
            opts = [(f, x) for f, x in E[slot] if f == "" or (f == "N" and nick and nicks < 2)]
        i = U.pick(lid, slot, len(opts))
        chosen[slot] = (i, opts[i][0])
        nicks += opts[i][0] == "N"
        parts.append(opts[i][1].replace("{BREED}", breed).replace("{NICK}", nick).replace("{SYN}", syn))
    d = " ".join(parts) + "\n\n" + E["fixed"].replace("{BREED}", breed)
    for name in {n for n in (breed, syn) if n}:
        d = re.sub(r"\b([Aa]) (?=" + re.escape(name) + r")", lambda m, name=name: (B.article(name).capitalize() if m.group(1) == "A" else B.article(name)) + " ", d)
    d = re.sub(r"\b(\w*(?:dog|cat|horse|pony))\s+(?:dog|cat|horse|pony)\b",
               lambda m: m.group(1) if m.group(1).lower().endswith(m.group(0).split()[-1].lower()) else m.group(0), d, flags=re.I)
    assert breed in d
    return d, chosen


STOP = U.STOP


def en_tags(lid):
    fixed = list(EN_CORE)
    used = set()
    for t in fixed:
        used |= set(t.split()) - STOP
    picked = []
    for t in sorted(EN_POOL, key=lambda t: hashlib.sha256(f"{lid}:tag:{t}".encode()).hexdigest()):
        w = set(t.split()) - STOP
        if w & used:
            continue
        picked.append(t)
        used |= w
        if len(picked) == 6:
            break
    return fixed + picked


def en_alts(name):
    t = (TPL / "alt_urny_plytka.md").read_text(encoding="utf-8")
    rows = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\| (\d) \| .*? \| (.*?) \|$", t, re.M)}
    b = name[:-4].strip() if name.lower().endswith(" dog") else name  # "... Dog" + " dog" -> bez dubletu
    a1 = ALT1.replace("{ART}", B.article(b)).replace("{BREED}", b)
    return {1: a1, **{k: rows[k] for k in range(2, 7)}}


# ---------- tłumaczenia ----------
_TR = {}


def tr_load(code):
    if code in _TR:
        return _TR[code]
    t = (TPL / f"grafika_tlumaczenie_{code}.md").read_text(encoding="utf-8")
    d = {}
    d["titles"] = re.findall(r"^\d\. (\{B\}.*)$", R.sec(t, "## Tytuł", "## Pierwszy akapit"), re.M)
    sb = R.sec(t, "## Pierwszy akapit", "## Sekcje stałe")
    ia, ib, ic = sb.index("**A**"), sb.index("**B**"), sb.index("**C**")
    bank = lambda s_: re.findall(r"^- [ABC]\d: (.*)$", s_, re.M)
    d["A"], d["B"], d["C"] = bank(sb[ia:ib]), bank(sb[ib:ic]), bank(sb[ic:])
    d["fixed"] = re.search(r"```\n(.*?)\n```", t, re.S).group(1)
    tg = R.sec(t, "## Tagi")
    item = lambda s_: [x.strip() for x, _ in re.findall(r"([^,:*()\n]+?) \((\d+)\)", s_)]
    st = re.search(r"\*\*Stałe:\*\* (.*)", tg).group(1).split(" (EN:")[0]
    d["core"] = item(st)
    d["pool"] = item(re.search(r"\*\*Pula:\*\* (.*)", tg).group(1))
    assert len(d["titles"]) == 6 and len(d["core"]) == 7 and len(d["A"]) == 5 and len(d["B"]) == 3 and len(d["C"]) == 4 and len(d["pool"]) == 19, \
        (code, len(d["titles"]), len(d["core"]), len(d["A"]), len(d["B"]), len(d["C"]), len(d["pool"]))
    for x in d["core"] + d["pool"]:
        assert len(x) <= 20, (code, x)
    _TR[code] = d
    return d


def tr_tags(lid, code, d):
    picked, photo = [], False
    for x in sorted(d["pool"], key=lambda x: hashlib.sha256(f"{lid}:{code}:{x}".encode()).hexdigest()):
        if PHOTO_TAG.search(x):
            if photo:
                continue  # jeden tag o zdjęciu (dwa warianty tego samego)
            photo = True
        picked.append(x)
        if len(picked) == 6:
            break
    return list(d["core"]) + picked


def tr_render(code, lid, rr, ch, tidx, feat=""):
    d = tr_load(code)
    b = rr[U.NAME_COL[code]]
    name = (b + " " + feat).strip() if feat else b
    par = []
    for slot in "ABC":
        bank = d[slot]
        i, flag = ch[slot]
        i = i if flag == "" and i < len(bank) else U.pick(lid, slot + "t", len(bank))
        par.append(R.tr_fill(bank[i], code, b))
    title = ""
    for k in range(6):
        title = R.tr_fill(d["titles"][(tidx - 1 + k) % 6], code, name)
        if len(title) <= 140:
            break
    fx = "\n".join(R.tr_fill(l, code, b) if l.strip() else "" for l in d["fixed"].split("\n"))
    return {"title": title, "description": " ".join(par) + "\n\n" + fx, "tags": tr_tags(lid, code, d)}


# ---------- kandydaci ----------
def breed_name(title):
    return title.split(" Urn for")[0].strip()


def build_candidates():
    stan = json.load(open(STAN, encoding="utf-8"))
    folders = {f["folder"]: f for f in csv.DictReader(open(INDEX, encoding="utf-8"))}
    mapa = list(csv.DictReader(open(MAPA_W, encoding="utf-8")))
    Rr = B.rasy()
    fw = B.feature_words()
    pm, by_c = U.breed_lookup(Rr)
    cls = B.e_class()
    out = []
    for m in mapa:
        lid = int(m["listing_id"])
        st = stan[str(lid)]
        f = folders.get(m["folder"])
        why = []
        if not f:
            why.append("brak folderu w indeksie: " + m["folder"])
            f = {"folder": m["folder"], "ean": "", "wideo_rozmiar": ""}
        name = NAME_FIX.get(m["nazwa_w_tytule"], m["nazwa_w_tytule"])
        row = {"gatunek": "pies", "nazwa_w_tytule": name, "folder": f["folder"]}
        rid, key, w2 = U.resolve(row, Rr, fw, pm, by_c)
        if not rid and lid in RID_OVERRIDE:
            rid, w2 = RID_OVERRIDE[lid], []
        why += w2
        if lid in OWNER_FEATURE:
            key = OWNER_FEATURE[lid]
        elif key:
            why.append("odmiana wykryta w nazwie/folderze, brak decyzji właścicielki: " + key)
        rr = Rr[("pies", rid)] if rid else None
        if rr:
            miss = [c for c in [U.NAME_COL[l] for l in LANG_ALL] if not rr.get(c)]
            if miss:
                why.append("brak tłumaczenia nazwy rasy: " + ",".join(miss))
        if key and key not in fw:
            why.append("brak słowa odmiany w 'Słowa stałe': " + key)
        film = [x for x in f["wideo_rozmiar"].split("|") if x and "-brand" not in x.split(":")[0]]
        if len(film) != 1:
            why.append("film rasy bez 'brand': " + str(len(film)))
        if len(st["images"]) != 6:
            why.append(f"zdjęć w stanie żywym: {len(st['images'])}")
        if B.is_done(lid):
            why.append("już zoptymalizowana")
        out.append({"lid": lid, "st": st, "folder": f, "views": int(m["wyswietlenia"]), "how": m["metoda"], "rid": rid, "rr": rr,
                    "breed": rr["Nazwa EN (główna)"] if rr else name, "key": key, "typ": cls.get(rid, "") if rid else "", "why": why,
                    "film2": film[0].split(":")[0] if film else ""})
    out.sort(key=lambda c: (c["views"], c["lid"]))  # od najmniej do najczęściej oglądanych
    return out, fw


def render(c, fw):
    lid, rr = c["lid"], c["rr"]
    e = (rr.get("Potoczne EN") or "").strip()
    nick = e if c["typ"] == "zdrobnienie" else ""
    syn = e if c["typ"] == "synonim" else ""
    feat = U.feature_en(c["key"]) if c["key"] else ""
    name = (c["breed"] + " " + feat).strip()
    desc, ch = en_description(lid, c["breed"], nick, syn)
    title, tidx = pick_title(lid, en()["titles"], name)
    enx = {"title": title, "description": desc, "tags": en_tags(lid), "alts": en_alts(name), "wzorzec_tytulu": tidx,
           "ABC": {k: v[0] + 1 for k, v in ch.items()}, "nick": nick, "synonim": syn, "odmiana": c["key"], "slow_w_tytule": words(title)}
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    trans = {code: tr_render(code, lid, rr, ch, tidx, fwd.get(code, "")) for code in LANG_ALL}
    return enx, trans


def check(enx, trans):
    p = []
    if len(enx["title"]) > 140:
        p.append("tytuł EN za długi")
    if enx["slow_w_tytule"] > MAX_WORDS:
        p.append(f"tytuł EN {enx['slow_w_tytule']} słów (limit {MAX_WORDS})")
    if re.search(r"natural ears", enx["title"] + enx["description"], re.I):
        p.append("Natural Ears")
    if len(enx["tags"]) != 13 or len(set(enx["tags"])) != 13 or any(len(x) > 20 for x in enx["tags"]):
        p.append("tagi EN")
    if "{" in enx["title"] + enx["description"]:
        p.append("znacznik w opisie EN")
    for k, a in enx["alts"].items():
        if len(a) > 500:
            p.append(f"alt {k} za długi")
    for code, d in trans.items():
        if len(d["title"]) > 140:
            p.append(f"tytuł {code} {len(d['title'])} zn.")
        if len(d["tags"]) != 13 or len(set(d["tags"])) != 13 or any(len(x) > 20 for x in d["tags"]):
            p.append(f"tagi {code}")
        if "{" in d["title"] + d["description"]:
            p.append(f"znacznik w {code}")
    return p


def raport():
    cs, fw = build_candidates()
    with open(MAPA, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "wyswietlenia", "tytul_zywy", "rasa_xlsx", "folder", "ean", "odmiana", "tytul_nowy", "slow", "film_rasy", "uwagi"])
        for c in cs:
            why, nt, nw = list(c["why"]), "", ""
            if not [x for x in why if x != "już zoptymalizowana"] and c["rr"]:
                enx, trans = render(c, fw)
                why += check(enx, trans)
                nt, nw = enx["title"], enx["slow_w_tytule"]
            w.writerow([c["lid"], c["views"], c["st"]["title"][:70], c["breed"], c["folder"]["folder"], c["folder"]["ean"], c["key"], nt, nw, c["film2"], "; ".join(why)])
    r = list(csv.DictReader(open(MAPA, encoding="utf-8")))
    print("ofert:", len(r), "| z uwagami:", sum(1 for x in r if x["uwagi"]), "| rozkład słów w tytule:", sorted(Counter(x["slow"] for x in r).items()))
    for x in r:
        if x["uwagi"]:
            print(" -", x["listing_id"], x["rasa_xlsx"], "|", x["uwagi"])


def plan(n, size):
    if glob.glob(str(ROOT / "logs" / f"partia_grafika_{n:03d}_*.jsonl")):
        sys.exit(f"BŁĄD: partia {n} rozpoczęta, nie nadpisuję planu")
    cs, fw = build_candidates()
    only = {int(x) for a in sys.argv if a.startswith("--lid=") for x in a[6:].split(",")}
    batch = []
    for c in cs:
        if only and c["lid"] not in only:
            continue
        if "już zoptymalizowana" in c["why"]:
            continue
        if c["why"]:
            print("pomijam", c["lid"], c["breed"], c["why"])
            continue
        enx, trans = render(c, fw)
        prob = check(enx, trans)
        if prob:
            print("pomijam", c["lid"], c["breed"], prob)
            continue
        c.update(en=enx, trans=trans)
        batch.append(c)
        if len(batch) == size:
            break
    p = ROOT / "plans" / f"partia_grafika_{n:03d}.csv"
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "listing_id", "wyswietlenia", "rasa", "odmiana", "folder", "ean", "tytul_przed", "tytul_po", "slow", "wzorzec", "ABC", "tagi", "film2"])
        for i, c in enumerate(batch, 1):
            e = c["en"]
            w.writerow([i, c["lid"], c["views"], c["breed"], c["key"], c["folder"]["folder"], c["folder"]["ean"], c["st"]["title"], e["title"], e["slow_w_tytule"],
                        e["wzorzec_tytulu"], "".join(f"{k}{v}" for k, v in e["ABC"].items()), "; ".join(e["tags"]), c["film2"]])
    dry = []
    for c in batch:
        v2 = BASE_V + urllib.parse.quote(c["folder"]["folder"]) + "/" + urllib.parse.quote(c["film2"])
        dry.append({"listing_id": c["lid"], "rasa": c["breed"], "ean": c["folder"]["ean"], "film2": v2, "film2_nazwa": c["film2"],
                    "images_before": {str(r[0]): r[1] for r in c["st"]["images"]}, "tytul_przed": c["st"]["title"], "en": c["en"], "tlumaczenia": c["trans"]})
    (ROOT / "plans" / f"partia_grafika_{n:03d}_dryrun.json").write_text(json.dumps(dry, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(batch)} ofert, języki {sorted({k for c in batch for k in c['trans']})}")
    return batch


# ---------- zapis ----------
def personalization():
    return [
        {"question_type": "text_input", "question_text": "Name", "required": True, "max_allowed_characters": 50},
        {"question_type": "text_input", "question_text": "Dates", "required": True, "max_allowed_characters": 50},
        {"question_type": "text_input", "question_text": "Quote on the plaque (optional)", "required": False, "max_allowed_characters": 600,
         "instructions": "Leave empty for the default quote, or type the exact text you'd like engraved on the paw-shaped plaque."},
        {"question_type": "unlabeled_upload", "question_text": "Pet photo", "required": False, "max_allowed_files": 1,
         "instructions": "Please upload a high-resolution image. The better the photo quality, the better the print will look on the plaque."},
        {"question_type": "dropdown", "question_text": "How should we print the photo?", "required": False,
         "options": [{"label": "Color + background"}, {"label": "Color, no background"}]},
    ]


def steps_for(c):
    en_, tr, lid = c["en"], c["trans"], c["lid"]
    b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
    s = [{"id": "listing", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"title": en_["title"], "description": en_["description"], "tags": ",".join(en_["tags"])}},  # materiały tekstowe bez zmian
         {"id": "wlasciwosc_materials", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "kind": "form",
          "fields": {"value_ids": MAT_VALUES[0], "values": MAT_VALUES[1]}},
         {"id": "how_its_made", "method": "PATCH", "path": b, "kind": "form", "fields": {"who_made": "collective", "when_made": "made_to_order", "is_supply": "false"}},
         {"id": "personalizacja", "method": "POST", "path": b + "/personalization", "kind": "json", "fields": {"personalization_questions": personalization()}}]
    for k in range(1, 7):
        s.append({"id": f"alt_{k}", "method": "POST", "path": b + "/images", "kind": "alt_existing", "rank": k, "fields": {"alt_text": en_["alts"][k]}})
    s.append({"id": "wideo_1_grafika", "method": "POST", "path": b + "/videos", "kind": "video", "src": str(VIDEO1), "fields": {"name": VIDEO1.name}})
    s.append({"id": "wideo_2_rasa", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film2"], "fields": {"name": c["film2_nazwa"]}})
    for code in LANG_ALL:
        d = tr[code]
        s.append({"id": f"tlumaczenie_{code}", "method": "POST", "path": b + f"/translations/{code}", "kind": "form",
                  "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return s


def load_frozen(n):
    jp = ROOT / "plans" / f"partia_grafika_{n:03d}_dryrun.json"
    if not jp.exists():
        sys.exit(f"BŁĄD: brak zatwierdzonego planu partii grafika {n}")
    out = []
    for x in json.load(open(jp, encoding="utf-8")):
        x["en"]["alts"] = {int(k): v for k, v in x["en"]["alts"].items()}
        out.append({"lid": x["listing_id"], "ean": x["ean"], "en": x["en"], "trans": x["tlumaczenia"], "film2": x["film2"], "film2_nazwa": x["film2_nazwa"],
                    "gatunek": "pies", "tytul_przed": x["tytul_przed"], "images_before": {int(k): v for k, v in x["images_before"].items()}})
    return out


def apply_batch(n):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    batch = load_frozen(n)
    if len(batch) > 50:
        sys.exit("BŁĄD: partia większa niż 50")
    if not VIDEO1.exists():
        sys.exit("BŁĄD: brak filmu 1 " + str(VIDEO1))
    summary = ROOT / "logs" / f"partia_grafika_{n:03d}_{TODAY}.jsonl"
    print(f"partia grafika {n}: {len(batch)} ofert z planu")
    for i, c in enumerate(batch, 1):
        lid = c["lid"]
        if B.is_done(lid):
            print(i, lid, "pomijam (już zrobiona)")
            continue
        p, live = B.backup_unique(lid)
        done = B.done_steps(lid)
        pr = R.preflight(c, live)
        if pr and not (done - {"weryfikacja"}):
            print(i, lid, "ZATRZYMANA przed zapisem:", "; ".join(pr))
            open(summary, "a").write(json.dumps({"listing_id": lid, "status": "pominięta", "powod": pr}, ensure_ascii=False) + "\n")
            continue
        resumed = bool(done - {"weryfikacja"})
        ids_before = dict(c["images_before"])
        for s in steps_for(c):
            if s["id"] in done:
                continue
            if resumed and s["kind"] == "video":
                vids = api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos", [])
                if len(vids) >= (1 if s["id"] == "wideo_1_grafika" else 2):
                    U.zlog(lid, s["id"], "backup/" + p.name, "już w ofercie (wykryte przy wznowieniu)", "ok")
                    continue
            if s["kind"] == "alt_existing":
                resp = U.alt_existing(s, c, ids_before)
            elif s["kind"] == "video":
                path = Path(s["src"]) if not s["src"].startswith("http") else R.curl_to(s["src"], CACHE / "wideo" / s["fields"]["name"])
                data, ct = base.multipart({"name": s["fields"]["name"]}, ("video", path.name), path.read_bytes(), "video/mp4")
                resp = api.request(s["method"], s["path"], headers={"Content-Type": ct}, data=data, retries=1)
                if not base.ok(resp) and re.search(r"reset|timed out|timeout|disconnect|closed", str(resp), re.I):
                    time.sleep(5)
                    vids = api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos", [])
                    if len(vids) >= (1 if s["id"] == "wideo_1_grafika" else 2):
                        resp = {"ok": "film już w ofercie po błędzie sieciowym"}
            else:
                resp = base.send(s)
            if s["id"].startswith("tlumaczenie_") and not base.ok(resp) and "exist" in str(resp).lower():
                resp = base.send({**s, "method": "PUT"})
            st = "ok" if base.ok(resp) else "błąd"
            U.zlog(lid, s["id"], "backup/" + p.name, {k: (v if len(str(v)) < 200 else str(v)[:200] + "...") for k, v in s["fields"].items()}, st)
            if st != "ok":
                open(summary, "a").write(json.dumps({"listing_id": lid, "status": "błąd", "krok": s["id"], "odpowiedź": str(resp)[:300]}, ensure_ascii=False) + "\n")
                sys.exit(f"{lid}: BŁĄD w kroku {s['id']}: {str(resp)[:300]}\nPrzerywam partię; po wyjaśnieniu uruchom ponownie (wykonane kroki zostaną pominięte).")
            time.sleep(0.15)
        for attempt in range(4):
            after = api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization")
            props = api.get(f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}/properties")
            imgs = sorted(after.get("images", []), key=lambda x: x["rank"])
            mat = next((pp for pp in props.get("results", []) if pp["property_id"] == B.MATERIAL_PROPERTY), {})
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(imgs), "alt_ok": all(html.unescape(im.get("alt_text") or "") == c["en"]["alts"][im["rank"]] for im in imgs) if len(imgs) == 6 else False,
                   "kolejnosc_ok": [im["listing_image_id"] for im in imgs] == [ids_before[k] for k in range(1, 7)] if len(imgs) == 6 else False,
                   "wideo": len(after.get("videos", [])), "pytan": len(after["personalization"]["personalization_questions"]),
                   "tlumaczen": sum(1 for k, v in after["translations"].items() if v and k != "en-US"), "who_made": after["who_made"],
                   "materialy_ok": sorted(after["materials"]) == sorted(live["materials"]), "materials_prop": sorted(mat.get("values", [])), "proba": attempt + 1}
            good = chk["cena_ok"] and chk["stan_ok"] and chk["status_ok"] and chk["zdjec"] == 6 and chk["alt_ok"] and chk["kolejnosc_ok"] and chk["wideo"] == 2 \
                and chk["pytan"] == 5 and chk["tlumaczen"] == 8 and chk["who_made"] == "collective" and chk["materialy_ok"] and chk["materials_prop"] == sorted(MAT_VALUES[1].split(","))
            if good:
                break
            time.sleep(3)
        U.zlog(lid, "weryfikacja", {"cena": live["price"], "stan": live["quantity"]}, chk, "ok" if good else "niezgodność")
        open(summary, "a").write(json.dumps({"listing_id": lid, "status": "ok" if good else "niezgodność", **chk}, ensure_ascii=False) + "\n")
        print(i, lid, "ok" if good else "NIEZGODNOŚĆ " + str(chk))
        if not good:
            sys.exit("Weryfikacja niezgodna, przerywam.")
    print("Partia zakończona. Proszę sprawdzić próbkę w Etsy przed następną partią.")


def main():
    cmd = sys.argv[1]
    if cmd == "raport":
        raport()
    elif cmd == "plan":
        size = next((int(a[7:]) for a in sys.argv if a.startswith("--size=")), 50)
        plan(int(sys.argv[2]), min(size, 50))
    elif cmd == "apply":
        if "--apply" not in sys.argv:
            sys.exit("Brak flagi --apply: nic nie zapisuję.")
        apply_batch(int(sys.argv[2]))


if __name__ == "__main__":
    main()
