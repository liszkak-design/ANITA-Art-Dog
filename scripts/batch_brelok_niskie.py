#!/usr/bin/env python3
"""Optymalizacja niskich urn z małą posrebrzaną płaskorzeźbą (sekcja "Lower urn with relief", 154 oferty: psy, koty, konie).
  python3 -I scripts/batch_brelok_niskie.py raport                      # kontrola wszystkich ofert bez zapisu (plans/brelok_niskie_raport.csv)
  python3 -I scripts/batch_brelok_niskie.py plan N [--lid=ID[,ID]] [--size=K]   # dry-run partii N (plans/partia_brelok_niskie_00N.csv i _dryrun.json)
  python3 -I scripts/batch_brelok_niskie.py apply N --apply             # zapis do Etsy (tylko po "tak" właścicielki dla partii N)
Zakres na ofertę: kopia zapasowa; tytuł (do 14 słów), opis, 13 tagów, materiały tekstowe (wood, silver plated metal relief), Materials (Pine, Birch, Metal),
personalizacja (3 pytania), alt texty 4 zdjęć (bez wymiany zdjęć, bez zdjęcia 7), film 1 (video-urn-low-brelok-dogs-anita.mp4), film 2 z folderu 090
(poza ofertami bez filmu 2), 8 tłumaczeń. Teksty: templates/brelok_niskie_propozycja_tekstow.md i brelok_niskie_tlumaczenie_<język>.md.
Kolejność: od najmniej do najczęściej oglądanych. Limit API: etsy_api (okno 24 h, stop 9000).
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
BASE_V = "https://www.artdog.com.pl/VIDEO/IV%20tura/090.%20Urny%20z%20brelokiem%20niskie/"
STAN = ROOT / "plans" / "brelok_niskie_stan_zywy.json"
INDEX = ROOT / "plans" / "brelok_niskie_foldery_index.csv"
MAPA = ROOT / "plans" / "brelok_niskie_mapa_final.csv"
CACHE = B.CACHE.parent / "brelok_niskie"
VIDEO1 = ROOT / "video" / "video-urn-low-brelok-dogs-anita.mp4"
MATERIALS_TEXT = "wood,silver plated metal relief"
MAT_VALUES = ("203,1059,174", "Pine,Birch,Metal")  # bez Brass (niska urna nie ma uchwytów), Metal id 174, zatwierdzone 01.11.2026
LANG_ALL = U.LANG_ALL
TODAY = datetime.date.today()
MAX_WORDS = 14
WORDS_EXCEPTION = {673570971, 659251386, 659251218}  # dłuższy tytuł dozwolony (zgoda właścicielki 31.10 i 01.11.2026): Irish Soft Coated Wheaten Terrier, Cavalier King Charles Spaniel, West Highland White Terrier; limit 140 znaków
SPW = {"pies": "dog", "kot": "cat", "koń": "horse"}
QUOTE = "You left our lives, but you will never leave our hearts"
NAME_ALL, BREED_EN, SYN_EN, FEATURE_KEY, NO_FEAT_EN = {}, {}, {}, {}, set()  # uzupełniane z plans/brelok_niskie_mapa_final.csv (nazwy po decyzjach właścicielki)
EN_CORE = ["tribute urn", "{sp} cremation urn", "personalised pet urn", "compact urn", "low wooden urn", "memorial keepsake", "urn with plaques"]
EN_POOL = ["pet remembrance gift", "forever loved", "in loving memory", "rainbow bridge", "furry family member", "pet sympathy gift", "beloved companion", "engraved nameplate",
           "bereavement keepsake", "last farewell", "home memorial", "silver portrait", "handmade pet urn", "name and dates", "cherished friend", "always remembered", "memory box"]
ALT1 = "Compact wooden urn for ashes with a small silver plated relief of {ART} {BREED} {SP}, a plaque with a quote above a plaque with a name and dates."
STOP = U.STOP
_EN = {}


def en():
    if _EN:
        return _EN
    t = (TPL / "brelok_niskie_propozycja_tekstow.md").read_text(encoding="utf-8")
    for x in EN_CORE[:1] + EN_CORE[2:] + EN_POOL:
        assert x in t, x
    s1 = R.sec(t, "## 1. Tytuły", "## 2.")
    _EN["titles"] = re.findall(r"^\d\. (\{BREED\}.*)$", s1, re.M)
    s3 = R.sec(t, "## 3. Pierwszy akapit", "## 4.")
    bank = lambda s: [(m.group(2) or "", m.group(3)) for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", s, re.M)]
    iA, iB, iC = s3.index("**A bez"), s3.index("**B (zast"), s3.index("**C (pers")
    _EN["A"], _EN["B"], _EN["C"] = bank(s3[iA:iB]), bank(s3[iB:iC]), bank(s3[iC:])
    _EN["fixed"] = re.search(r"```\n(.*?)\n```", R.sec(t, "## 4. Sekcje stałe", "## 5."), re.S).group(1)
    assert len(_EN["titles"]) == 6 and len(_EN["A"]) == 15 and len(_EN["B"]) == 4 and len(_EN["C"]) == 5, (len(_EN["titles"]), len(_EN["A"]), len(_EN["B"]), len(_EN["C"]))
    assert QUOTE in _EN["fixed"]
    return _EN


def words(t):
    return len(t.replace(",", " ").split())


def title_fill(pat, name, sp):
    t = pat.replace("{BREED}", name)
    if sp.lower() in name.lower() or (sp == "dog" and re.search(r"hound|dog", name, re.I)):
        t = t.replace("for Your {SP}", "for Your Pet").replace("for {SP} Ashes", "for Ashes").replace("{SP} ", "")
    else:
        t = t.replace("{SP}", sp.capitalize())
    return re.sub(r"\s+", " ", t).strip()


def pick_title(lid, pats, name, sp):
    max_w = 99 if lid in WORDS_EXCEPTION else MAX_WORDS
    start = U.pick(lid, "T", len(pats))
    fb = None
    for k in range(len(pats)):
        i = (start + k) % len(pats)
        t = title_fill(pats[i], name, sp)
        fb = fb or (t, i + 1)
        if len(t) <= 140 and words(t) <= max_w:
            return t, i + 1
    return fb


def en_description(lid, name, sp, nick, syn):
    E = en()
    parts, chosen, nicks = [], {}, 0
    for slot in "ABC":
        if slot == "A":
            want = "N" if nick else ("S" if syn else "")
            opts = [(f, x) for f, x in E["A"] if f == want]
        else:
            opts = [(f, x) for f, x in E[slot] if f == "" or (f == "N" and nick and nicks < 2)]
        i = U.pick(lid, slot, len(opts))
        if slot == "B" and "compact" in " ".join(parts).lower():  # zakaz A2 + B1: powtórzenie "compact" (decyzja 01.11.2026)
            while "compact" in opts[i][1].lower():
                i = (i + 1) % len(opts)
        chosen[slot] = (i, opts[i][0])
        nicks += opts[i][0] == "N"
        parts.append(opts[i][1].replace("{BREED}", name).replace("{NICK}", nick).replace("{SYN}", syn).replace("{sp}", sp))
    d = " ".join(parts) + "\n\n" + E["fixed"].replace("{BREED}", name)
    d = d.replace("{sp}", sp)
    for nm in {n for n in (name, syn) if n}:
        d = re.sub(r"\b([Aa]n?) (?=" + re.escape(nm) + r")", lambda m, nm=nm: (B.article(nm).capitalize() if m.group(1)[0] == "A" else B.article(nm)) + " ", d)
    d = re.sub(r"\b(\w*(?:dog|cat|horse|pony))\s+(?:dog|cat|horse|pony)\b",
               lambda m: m.group(1) if m.group(1).lower().endswith(m.group(0).split()[-1].lower()) else m.group(0), d, flags=re.I)
    assert name in d
    return d, chosen


def en_tags(lid, sp):
    fixed = [x.replace("{sp}", sp) for x in EN_CORE]
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


def en_alts(name, sp):
    t = (TPL / "alt_urny_plytka.md").read_text(encoding="utf-8")
    rows = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\| (\d) \| .*? \| (.*?) \|$", t, re.M)}
    nm = name[:-len(sp) - 1] if name.lower().endswith(" " + sp) else name  # "Persian Cat" + "cat" bez dubletu
    a1 = ALT1.replace("{ART}", B.article(nm)).replace("{BREED}", nm).replace("{SP}", sp)
    return {1: a1, 2: rows[4], 3: rows[5], 4: rows[6]}  # zdjęcia 2-4 = alt 4-6 z urn z płytką (listwa, narożnik, wnętrze)


# ---------- tłumaczenia ----------
_TR = {}


def tr_load(code):
    if code in _TR:
        return _TR[code]
    t = (TPL / f"brelok_niskie_tlumaczenie_{code}.md").read_text(encoding="utf-8")
    d = {"titles": re.findall(r"^\d\. (\{B\}.*)$", R.sec(t, "## Tytuł", "## Pierwszy akapit"), re.M)}
    sb = R.sec(t, "## Pierwszy akapit", "## Sekcje stałe")
    ia, ib, ic = sb.index("**A**"), sb.index("**B**"), sb.index("**C**")
    bank = lambda s_: re.findall(r"^- [ABC]\d: (.*)$", s_, re.M)
    d["A"], d["B"], d["C"] = bank(sb[ia:ib]), bank(sb[ib:ic]), bank(sb[ic:])
    d["fixed"] = re.search(r"```\n(.*?)\n```", t, re.S).group(1)
    tg = R.sec(t, "## Tagi")
    def item(s_):
        s_ = re.sub(r" \((?:psa|psie)[^)]*\)", " (0)", s_)
        return [x.strip() for x, _ in re.findall(r"([^,:*()\n]+?) \((\d+)\)", s_)]
    st = re.search(r"\*\*Stałe:\*\* (.*)", tg).group(1).split(" (EN:")[0]
    d["core"] = item(st)
    d["pool"] = item(re.search(r"\*\*Pula:\*\* (.*)", tg).group(1))
    assert len(d["titles"]) == 6 and len(d["core"]) == 7 and len(d["A"]) == 5 and len(d["B"]) == 3 and len(d["C"]) == 4 and len(d["pool"]) == 17, \
        (code, len(d["titles"]), len(d["core"]), len(d["A"]), len(d["B"]), len(d["C"]), len(d["pool"]))
    _TR[code] = d
    return d


def tr_fill(text, code, sp, name):
    for k, v in U.FORMS[code][sp].items():
        text = text.replace("{" + k + "}", v)
    return re.sub(r"[ \t]+", " ", text.replace("{B}", name)).strip()


def tr_render(code, lid, sp, rr, ch, tidx, feat=""):
    d = tr_load(code)
    b = NAME_ALL.get(lid) or rr[U.NAME_COL[code]]
    name = (b + " " + feat).strip() if feat else b
    par = []
    for slot in "ABC":
        bank = d[slot]
        i, flag = ch[slot]
        i = i if flag == "" and i < len(bank) else U.pick(lid, slot + "t", len(bank))
        par.append(tr_fill(bank[i], code, sp, b))
    title = ""
    for k in range(6):
        title = tr_fill(d["titles"][(tidx - 1 + k) % 6], code, sp, name)
        if len(title) <= 140:
            break
    fx = "\n".join(tr_fill(l, code, sp, b) if l.strip() else "" for l in d["fixed"].split("\n"))
    pool = sorted(d["pool"], key=lambda x: hashlib.sha256(f"{lid}:{code}:{x}".encode()).hexdigest())[:6]
    tags = [tr_fill(x, code, sp, b) for x in d["core"] + pool]
    return {"title": title, "description": " ".join(par) + "\n\n" + fx, "tags": tags}


# ---------- kandydaci ----------
def build_candidates():
    stan = json.load(open(STAN, encoding="utf-8"))
    rows = list(csv.DictReader(open(MAPA, encoding="utf-8")))
    folders = {f["folder"]: f for f in csv.DictReader(open(INDEX, encoding="utf-8"))}
    Rr = B.rasy()
    fw = B.feature_words()
    cls = B.e_class()
    out = []
    for m in rows:
        lid = int(m["listing_id"])
        st = stan[str(lid)]
        sp = m["gatunek"]
        why = []
        rid = m["rasa_id"]
        if m["nazwa_stala"] == "tak":
            NAME_ALL[lid] = m["nazwa_w_tytule"]
        if m["syn_en"]:
            SYN_EN[lid] = m["syn_en"]
        if m["breed_en"]:
            BREED_EN[lid] = m["breed_en"]
            NO_FEAT_EN.add(lid)
        if m["odmiana"]:
            FEATURE_KEY[lid] = m["odmiana"]
        rr = Rr.get((sp, rid)) if rid else None
        if not rr and lid not in NAME_ALL:
            why.append("rasa nierozpoznana: " + m["nazwa_w_tytule"])
        if lid in NAME_ALL and not rr:
            rr = {c: NAME_ALL[lid] for c in U.NAME_COL.values()} | {"Nazwa EN (główna)": NAME_ALL[lid], "Potoczne EN": SYN_EN.get(lid, "")}
        key = FEATURE_KEY.get(lid) or m["odmiana"]
        if key and key not in fw:
            why.append("odmiana bez słowa: " + key)
        if rr and lid not in NAME_ALL:
            miss = [c for c in [U.NAME_COL[l] for l in LANG_ALL] if not rr.get(c)]
            if miss:
                why.append("brak tłumaczenia nazwy rasy: " + ",".join(miss))
        f = folders.get(m["folder"])
        film2 = ""
        if m["film_2"] == "tak":
            film = [x for x in (f["wideo_rozmiar"].split("|") if f else []) if x and "-brand" not in x.split(":")[0]]
            if len(film) != 1:
                why.append("film rasy bez 'brand': " + str(len(film)))
            else:
                film2 = film[0].split(":")[0]
        if len(st["images"]) != 4:
            why.append(f"zdjęć w stanie żywym: {len(st['images'])} (oczekiwano 4)")
        if B.is_done(lid):
            why.append("już zoptymalizowana")
        breed = BREED_EN.get(lid) or (rr["Nazwa EN (główna)"] if rr else m["nazwa_w_tytule"])
        out.append({"lid": lid, "st": st, "sp": sp, "views": int(m["wyswietlenia"]), "folder": m["folder"], "rr": rr, "breed": breed, "key": key,
                    "typ": cls.get(rid, "") if rid and lid not in NAME_ALL else "", "film2": film2, "why": why})
    out.sort(key=lambda c: (c["views"], c["lid"]))
    return out, fw


def render(c, fw):
    lid, rr, sp = c["lid"], c["rr"], c["sp"]
    spw = SPW[sp]
    e = (rr.get("Potoczne EN") or "").strip()
    nick = e if c["typ"] == "zdrobnienie" else ""
    syn = SYN_EN.get(lid, e if c["typ"] == "synonim" else "")
    feat = "" if lid in NO_FEAT_EN else (U.feature_en(c["key"]) if c["key"] else "")
    name = (c["breed"] + " " + feat).strip()
    desc, ch = en_description(lid, c["breed"], spw, nick, syn)
    title, tidx = pick_title(lid, en()["titles"], name, spw)
    enx = {"title": title, "description": desc, "tags": en_tags(lid, spw), "alts": en_alts(name, spw), "wzorzec_tytulu": tidx,
           "ABC": {k: v[0] + 1 for k, v in ch.items()}, "nick": nick, "synonim": syn, "odmiana": c["key"], "slow_w_tytule": words(title)}
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    trans = {code: tr_render(code, lid, sp, rr, ch, tidx, fwd.get(code, "")) for code in LANG_ALL}
    return enx, trans


def check(enx, trans, sp, lid=0):
    p = []
    if len(enx["title"]) > 140 or (enx["slow_w_tytule"] > MAX_WORDS and lid not in WORDS_EXCEPTION):
        p.append(f"tytuł EN {len(enx['title'])} zn. / {enx['slow_w_tytule']} słów")
    if re.search(r"natural ears", enx["title"] + enx["description"], re.I):
        p.append("Natural Ears")
    if len(enx["tags"]) != 13 or len(set(enx["tags"])) != 13 or any(len(x) > 20 for x in enx["tags"]):
        p.append("tagi EN")
    if "{" in enx["title"] + enx["description"]:
        p.append("znacznik w opisie EN")
    for code, d in trans.items():
        if len(d["title"]) > 140:
            p.append(f"tytuł {code} {len(d['title'])} zn.")
        if len(d["tags"]) != 13 or len(set(d["tags"])) != 13 or any(len(x) > 20 for x in d["tags"]):
            p.append(f"tagi {code}: " + ", ".join(x for x in d["tags"] if len(x) > 20))
        if "{" in d["title"] + d["description"] or "{" in "".join(d["tags"]):
            p.append(f"znacznik w {code}")
    return p


def raport():
    cs, fw = build_candidates()
    out = ROOT / "plans" / "brelok_niskie_raport.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "wyswietlenia", "gatunek", "tytul_zywy", "rasa", "odmiana", "tytul_nowy", "slow", "film2", "uwagi"])
        for c in cs:
            why, nt, nw = list(c["why"]), "", ""
            if not [x for x in why if x != "już zoptymalizowana"] and c["rr"]:
                enx, trans = render(c, fw)
                why += check(enx, trans, c["sp"], c["lid"])
                nt, nw = enx["title"], enx["slow_w_tytule"]
            w.writerow([c["lid"], c["views"], c["sp"], c["st"]["title"][:60], c["breed"], c["key"], nt, nw, c["film2"], "; ".join(why)])
    r = list(csv.DictReader(open(out, encoding="utf-8")))
    print("ofert:", len(r), "| z uwagami:", sum(1 for x in r if x["uwagi"]), "| słów w tytule:", sorted(Counter(x["slow"] for x in r).items()))
    for x in r:
        if x["uwagi"]:
            print(" -", x["listing_id"], x["rasa"], "|", x["uwagi"])


def plan(n, size):
    if glob.glob(str(ROOT / "logs" / f"partia_brelok_niskie_{n:03d}_*.jsonl")):
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
        prob = check(enx, trans, c["sp"], c["lid"])
        if prob:
            print("pomijam", c["lid"], c["breed"], prob)
            continue
        c.update(en=enx, trans=trans)
        batch.append(c)
        if len(batch) == size:
            break
    with open(ROOT / "plans" / f"partia_brelok_niskie_{n:03d}.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "listing_id", "wyswietlenia", "gatunek", "rasa", "odmiana", "folder", "tytul_przed", "tytul_po", "slow", "wzorzec", "ABC", "tagi", "film2"])
        for i, c in enumerate(batch, 1):
            e = c["en"]
            w.writerow([i, c["lid"], c["views"], c["sp"], c["breed"], c["key"], c["folder"], c["st"]["title"], e["title"], e["slow_w_tytule"], e["wzorzec_tytulu"],
                        "".join(f"{k}{v}" for k, v in e["ABC"].items()), "; ".join(e["tags"]), c["film2"]])
    dry = []
    for c in batch:
        v2 = BASE_V + urllib.parse.quote(c["folder"]) + "/" + urllib.parse.quote(c["film2"]) if c["film2"] else ""
        dry.append({"listing_id": c["lid"], "rasa": c["breed"], "gatunek": c["sp"], "film2": v2, "film2_nazwa": c["film2"], "zdjecie_7": False,
                    "images_before": {str(r[0]): r[1] for r in c["st"]["images"]}, "tytul_przed": c["st"]["title"], "en": c["en"], "tlumaczenia": c["trans"]})
    (ROOT / "plans" / f"partia_brelok_niskie_{n:03d}_dryrun.json").write_text(json.dumps(dry, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(batch)} ofert, gatunki {Counter(c['sp'] for c in batch)}")
    return batch


# ---------- zapis ----------
def personalization():
    return [{"question_type": "text_input", "question_text": "Name", "required": True, "max_allowed_characters": 50},
            {"question_type": "text_input", "question_text": "Dates", "required": True, "max_allowed_characters": 50},
            {"question_type": "text_input", "question_text": "Quote on the plaque", "required": False, "max_allowed_characters": 600,
             "instructions": "Leave empty for the default verse, or type the exact text you'd like engraved on the upper plaque."}]


def steps_for(c):
    en_, tr, lid = c["en"], c["trans"], c["lid"]
    b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
    s = [{"id": "listing", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"title": en_["title"], "description": en_["description"], "tags": ",".join(en_["tags"]), "materials": MATERIALS_TEXT}},
         {"id": "wlasciwosc_materials", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "kind": "form",
          "fields": {"value_ids": MAT_VALUES[0], "values": MAT_VALUES[1]}},
         {"id": "how_its_made", "method": "PATCH", "path": b, "kind": "form", "fields": {"who_made": "collective", "when_made": "made_to_order", "is_supply": "false"}},
         {"id": "personalizacja", "method": "POST", "path": b + "/personalization", "kind": "json", "fields": {"personalization_questions": personalization()}}]
    for k in range(1, 5):
        s.append({"id": f"alt_{k}", "method": "POST", "path": b + "/images", "kind": "alt_existing", "rank": k, "fields": {"alt_text": en_["alts"][k]}})
    s.append({"id": "wideo_1_brelok", "method": "POST", "path": b + "/videos", "kind": "video", "src": str(VIDEO1), "fields": {"name": VIDEO1.name}})
    if c["film2"]:
        s.append({"id": "wideo_2_rasa", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film2"], "fields": {"name": c["film2_nazwa"]}})
    for code in LANG_ALL:
        d = tr[code]
        s.append({"id": f"tlumaczenie_{code}", "method": "POST", "path": b + f"/translations/{code}", "kind": "form",
                  "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return s


def load_frozen(n):
    jp = ROOT / "plans" / f"partia_brelok_niskie_{n:03d}_dryrun.json"
    if not jp.exists():
        sys.exit(f"BŁĄD: brak zatwierdzonego planu partii brelok niskie {n}")
    out = []
    for x in json.load(open(jp, encoding="utf-8")):
        x["en"]["alts"] = {int(k): v for k, v in x["en"]["alts"].items()}
        out.append({"lid": x["listing_id"], "sp": x["gatunek"], "en": x["en"], "trans": x["tlumaczenia"], "film2": x["film2"], "film2_nazwa": x["film2_nazwa"],
                    "zdjecie_7": x["zdjecie_7"], "tytul_przed": x["tytul_przed"], "images_before": {int(k): v for k, v in x["images_before"].items()}})
    return out


def preflight(c, live):
    pr = []
    if "error" in live:
        return ["odczyt oferty: " + str(live["error"])[:100]]
    if live["state"] != "active":
        pr.append("status " + live["state"])
    if len(live.get("images", [])) != 4:
        pr.append(f"zdjęć: {len(live.get('images', []))} (oczekiwano 4)")
    if live.get("videos"):
        pr.append("oferta ma już wideo")
    if html.unescape(live["title"]) != c["tytul_przed"]:
        pr.append("tytuł w Etsy inny niż w odczycie planu")
    ids = {im["rank"]: im["listing_image_id"] for im in live.get("images", [])}
    if any(ids.get(k) != v for k, v in c["images_before"].items()):
        pr.append("zdjęcia zmieniły się od odczytu planu")
    return pr


def apply_batch(n):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    batch = load_frozen(n)
    if len(batch) > 50:
        sys.exit("BŁĄD: partia większa niż 50")
    if not VIDEO1.exists():
        sys.exit("BŁĄD: brak filmu 1")
    summary = ROOT / "logs" / f"partia_brelok_niskie_{n:03d}_{TODAY}.jsonl"
    print(f"partia brelok niskie {n}: {len(batch)} ofert z planu")
    for i, c in enumerate(batch, 1):
        lid = c["lid"]
        if B.is_done(lid):
            print(i, lid, "pomijam (już zrobiona)")
            continue
        p, live = B.backup_unique(lid)
        done = B.done_steps(lid)
        pr = preflight(c, live)
        if pr and not (done - {"weryfikacja"}):
            print(i, lid, "ZATRZYMANA przed zapisem:", "; ".join(pr))
            open(summary, "a").write(json.dumps({"listing_id": lid, "status": "pominięta", "powod": pr}, ensure_ascii=False) + "\n")
            continue
        resumed = bool(done - {"weryfikacja"})
        ids_before = dict(c["images_before"])
        n_vid = 2 if c["film2"] else 1
        for s in steps_for(c):
            if s["id"] in done:
                continue
            if resumed and s["kind"] == "video":
                vids = api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos", [])
                if len(vids) >= (1 if s["id"] == "wideo_1_brelok" else 2):
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
                    if len(vids) >= (1 if s["id"] == "wideo_1_brelok" else 2):
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
        n_img = 4
        for attempt in range(4):
            after = api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization")
            props = api.get(f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}/properties")
            imgs = sorted(after.get("images", []), key=lambda x: x["rank"])
            mat = next((pp for pp in props.get("results", []) if pp["property_id"] == B.MATERIAL_PROPERTY), {})
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(imgs), "alt_ok": all(html.unescape(im.get("alt_text") or "") == c["en"]["alts"][im["rank"]] for im in imgs) if len(imgs) == n_img else False,
                   "kolejnosc_ok": [im["listing_image_id"] for im in imgs] == [ids_before[k] for k in range(1, 5)] if len(imgs) == 4 else False,
                   "wideo": len(after.get("videos", [])), "pytan": len(after["personalization"]["personalization_questions"]),
                   "tlumaczen": sum(1 for k, v in after["translations"].items() if v and k != "en-US"), "who_made": after["who_made"],
                   "materialy_ok": sorted(after["materials"]) == sorted(MATERIALS_TEXT.split(",")), "materials_prop": sorted(mat.get("values", [])), "proba": attempt + 1}
            good = chk["cena_ok"] and chk["stan_ok"] and chk["status_ok"] and chk["zdjec"] == n_img and chk["alt_ok"] and chk["kolejnosc_ok"] and chk["wideo"] == n_vid \
                and chk["pytan"] == 3 and chk["tlumaczen"] == 8 and chk["who_made"] == "collective" and chk["materialy_ok"] and chk["materials_prop"] == sorted(MAT_VALUES[1].split(","))
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
