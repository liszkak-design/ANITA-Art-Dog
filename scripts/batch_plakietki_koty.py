#!/usr/bin/env python3
"""Optymalizacja 38 tablic pamiątkowych "Memorial Board" (deska MDF 34 x 24 cm, relief z cold cast bronze, tabliczka z grawerem; sekcja "Plaques with dog").
  python3 -I scripts/batch_hanging.py raport                      # kontrola wszystkich ofert bez zapisu (plans/hanging_raport.csv)
  python3 -I scripts/batch_hanging.py plan N [--lid=ID[,ID]] [--size=K]   # dry-run partii N (plans/partia_plakietki_koty_00N.csv i _dryrun.json)
  python3 -I scripts/batch_hanging.py apply N --apply             # zapis do Etsy (tylko po "tak" właścicielki dla partii N)
Zakres na ofertę: kopia zapasowa; tytuł (do 14 słów), opis, tagi (5 stałych + 8), materiały tekstowe (cold cast bronze, MDF board, engraving laminate), Materials (Bronze, Resin, Composite),
atrybuty Height 34 i Width 24 (cm; bez Depth), personalizacja (Name 50 i Dates 50, wymagane; Quote 1024, opcjonalne), 6 alt textów (bez wymiany zdjęć),
2 filmy z folderu 218 (bez "brand" pierwszy), 8 tłumaczeń. Home style bez zmian. Kolejność: od najmniej do najczęściej oglądanych. Limit API: etsy_api (stop 9000).
"""
import csv
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
BASE_V = "https://www.artdog.com.pl/VIDEO/XIII%20tura/14%20.%20Koty%20obrazkowe/036.%20P%C5%82ytka%20nagrobna%20obrazkowe/"
STAN = ROOT / "plans" / "plakietki_koty_stan_zywy.json"
MAPA = ROOT / "plans" / "plakietki_koty_mapa.csv"
INDEX = ROOT / "plans" / "plakietki_koty_foldery_index.csv"
VIDEO1 = ROOT / "video" / "video-ceramic-geom-cats-anita.mp4"
NEW_IMAGES = [(ROOT / "media" / "plakietki_grafika" / "tyl_plytki.jpg", "Back of the ceramic plaque, flat and plain, with no hole or hook"),
              (ROOT / "media" / "plakietki_grafika" / "oryginal_kolorowe.jpg", "Unedited photo of a finished ceramic oval plaque printed with a colour photo of a dog and a quote")]
CACHE = B.CACHE.parent / "plakietki_koty"
LANG_ALL = U.LANG_ALL
MAX_WORDS = 14
MAT_VALUES = ("83", "Ceramic")  # lista Etsy: Ceramic
NAME_FIX = {"Li Hua, Dragon Li": "Dragon Li", "Norwegian Forest": "Norwegian Forest Cat"}
FEATURE_BY_LID = {}
EN_CORE = ["cat memorial plaque", "cartoon cat", "pet loss gift", "grave marker", "tombstone plaque"]
EN_POOL = ["ceramic plaque", "personalized plaque", "custom photo plaque", "pet headstone", "memorial keepsake", "sympathy gift", "in loving memory", "garden memorial", "cartoon cat art",
           "cat portrait plaque", "cat cemetery marker", "pet remembrance", "weatherproof plaque", "oval memorial plaque", "outdoor memorial", "pet memorial stone", "rainbow bridge"]
ALT12 = {1: "Oval ceramic memorial plaque with a cartoon-style portrait of a {BREED} cat on a white marble surface",
         2: "Ceramic oval plaque with a cartoon-style {BREED} cat portrait seen at an angle, showing the smooth rounded edge"}
STOP = U.STOP | {"cat"}
_EN, _TR = {}, {}


def sec(t, a, b=None):
    return R.sec(t, a, b)


def en():
    if _EN:
        return _EN
    t = (TPL / "plakietki_koty_propozycja_tekstow.md").read_text(encoding="utf-8")
    for x in EN_CORE + EN_POOL:
        assert x in t, x
    _EN["titles"] = re.findall(r"^\d\. (\{BREED\}.*)$", sec(t, "## 1. Tytuły", "## 2."), re.M)
    s3 = sec(t, "## 3. Pierwszy akapit", "## 4.")
    bank = lambda s: [(m.group(2) or "", m.group(3)) for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", s, re.M)]
    iA, iB, iC = s3.index("**A bez"), s3.index("**B (zast"), s3.index("**C (pers")
    _EN["A"], _EN["B"], _EN["C"] = bank(s3[iA:iB]), bank(s3[iB:iC]), bank(s3[iC:])
    _EN["fixed"] = re.search(r"```\n(.*?)\n```", sec(t, "## 4. Sekcje stałe", "## 5."), re.S).group(1)
    assert len(_EN["titles"]) == 6 and len(_EN["A"]) == 11 and len(_EN["B"]) == 4 and len(_EN["C"]) == 4, (len(_EN["titles"]), len(_EN["A"]), len(_EN["B"]), len(_EN["C"]))
    assert "{BREED}" in _EN["fixed"] and "Geometric portrait" not in t.split("## 5.")[1].split("## 6.")[0].split("3. dropdown")[1].split("\n")[0].replace("usunięty","")
    return _EN


def num(x, comma=False):
    t = f"{x:.1f}".rstrip("0").rstrip(".") if x != int(x) else str(int(x))
    return t.replace(".", ",") if comma else t


def fill_dims(txt, dm, comma=False):
    r = {"H": dm[0], "W": dm[1], "D": dm[2]}
    for k, v in r.items():
        txt = txt.replace("{" + k + "_IN}", num(round(v / 2.54, 1), comma)).replace("{" + k + "}", num(v, comma))
    return txt


def words(t):
    return len(t.replace(",", " ").split())


SKIP_REP = {"or", "and", "with", "the", "of", "a", "to", "in", "for_"}


def repeated(t, name=""):
    """Etsy: unikaj powtórzeń słów w tytule (zwłaszcza dog i for). Zwraca listę powtórzonych słów (bez krótkich spójników)."""
    nw = set(re.findall(r"[\w'-]+", name.lower()))
    ws = [w for w in re.findall(r"[\w'-]+", t.lower()) if w not in SKIP_REP and w not in nw]
    return sorted({w for w in ws if ws.count(w) > 1})


FOR_WORDS = {"para", "pour", "für", "voor", "dla", "per", "för", "till", "for"}


def repeated_tr(t, name):
    """Jak repeated(), ale dla tłumaczeń: bez słów nazwy rasy i bez krótkich słów funkcyjnych (de, da, z, à...), z wyjątkiem słów 'dla/für/pour...'."""
    nw = {w for w in re.findall(r"[\w'-]+", name.lower())}
    ws = [w for w in re.findall(r"[\w'-]+", t.lower()) if w not in nw and (len(w) >= 4 or w in FOR_WORDS)]
    return sorted({w for w in ws if ws.count(w) > 1})


def pick_title(lid, pats, name):
    start = U.pick(lid, "T", len(pats))
    fb = None
    for k in range(len(pats)):
        i = (start + k) % len(pats)
        t = re.sub(r"\s+", " ", pats[i].replace("{BREED}", name)).strip()
        fb = fb or (t, i + 1)
        if len(t) <= 140 and words(t) <= MAX_WORDS and not repeated(t, name):
            return t, i + 1
    return fb


def en_description(lid, name, nick, syn):
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
        parts.append(opts[i][1].replace("{BREED}", name).replace("{NICK}", nick).replace("{SYN}", syn))
    txt = " ".join(parts) + "\n\n" + E["fixed"].replace("{BREED}", name)
    for nm in {n for n in (name, syn) if n}:
        txt = re.sub(r"\b([Aa]n?) (?=" + re.escape(nm) + r")", lambda m, nm=nm: (B.article(nm).capitalize() if m.group(1)[0] == "A" else B.article(nm)) + " ", txt)
    assert (name in txt or (syn and syn in txt) or (nick and nick in txt)) and "{" not in txt, txt[:300]
    return txt, chosen


def en_tags(lid):
    """5 stałych + 8 z puli; ten sam słowo kluczowe (poza "dog" i słowami STOP) nie więcej niż 3 razy w całym zestawie 13 tagów."""
    fixed = list(EN_CORE)
    cnt = Counter(w for t in fixed for w in set(t.split()) - STOP)
    picked = []
    for t in sorted(EN_POOL, key=lambda t: hashlib.sha256(f"{lid}:tag:{t}".encode()).hexdigest()):
        ws = set(t.split()) - STOP
        if t in fixed or any(cnt[w] >= 3 for w in ws):
            continue
        picked.append(t)
        cnt.update(ws)
        if len(picked) == 8:
            break
    return fixed + picked


def en_alts(name):
    out = {}
    for k, v in ALT12.items():
        t = v.replace("{BREED}", name)
        t = re.sub(r"\b([Aa]n?) (?=" + re.escape(name) + ")", lambda m: (B.article(name).capitalize() if m.group(1)[0] == "A" else B.article(name)) + " ", t)
        out[k] = t
    return out


def tr_load(code):
    if code in _TR:
        return _TR[code]
    t = (TPL / f"plakietki_koty_tlumaczenie_{code}.md").read_text(encoding="utf-8")
    d = {"titles": re.findall(r"^\d\. (\{B\}.*)$", sec(t, "## Tytuł", "## Pierwszy akapit"), re.M)}
    sb = sec(t, "## Pierwszy akapit", "## Sekcje stałe")
    ia, ib, ic = sb.index("**A**"), sb.index("**B**"), sb.index("**C**")
    bank = lambda s_: re.findall(r"^- [ABC]\d: (.*)$", s_, re.M)
    d["A"], d["B"], d["C"] = bank(sb[ia:ib]), bank(sb[ib:ic]), bank(sb[ic:])
    d["fixed"] = re.search(r"```\n(.*?)\n```", t, re.S).group(1)
    tg = sec(t, "## Tagi")
    item = lambda s_: [x.strip() for x, _ in re.findall(r"([^,:*()\n]+?) \((\d+)\)", s_)]
    d["core"] = item(re.search(r"\*\*Stałe:\*\* (.*)", tg).group(1).split(" (EN:")[0])
    d["pool"] = item(re.search(r"\*\*Pula:\*\* (.*)", tg).group(1))
    assert len(d["titles"]) == 6 and len(d["core"]) == 5 and len(d["A"]) == 5 and len(d["B"]) == 3 and len(d["C"]) == 3 and len(d["pool"]) in (18,), \
        (code, len(d["titles"]), len(d["core"]), len(d["A"]), len(d["B"]), len(d["C"]), len(d["pool"]))
    _TR[code] = d
    return d


def tr_render(code, lid, rr, ch, tidx, feat):
    d = tr_load(code)
    b = rr[U.NAME_COL[code]]
    name = (b + " " + feat).strip() if feat else b
    par = []
    for slot in "ABC":
        bank = d[slot]
        i, flag = ch[slot]
        i = i if flag == "" and i < len(bank) else U.pick(lid, slot + "t", len(bank))
        par.append(bank[i].replace("{B}", b))
    title = ""
    for k in range(6):
        title = re.sub(r"\s+", " ", d["titles"][(tidx - 1 + k) % 6].replace("{B}", name)).strip()
        if len(title) <= 140 and not repeated_tr(title, name):
            break
    order = sorted(d["pool"], key=lambda x: hashlib.sha256(f"{lid}:{code}:{x}".encode()).hexdigest())
    pool, used = [], set()
    for x in order:
        w = {t.lower() for t in re.findall(r"\w{5,}", x)}
        if w & used:
            continue
        pool.append(x)
        used |= w
        if len(pool) == 8:
            break
    for x in order:
        if len(pool) == 8:
            break
        if x not in pool:
            pool.append(x)
    return {"title": title, "description": " ".join(par) + "\n\n" + d["fixed"].replace("{B}", b), "tags": d["core"] + pool}


def build_candidates():
    stan = json.load(open(STAN, encoding="utf-8"))
    rows = list(csv.DictReader(open(MAPA, encoding="utf-8")))
    folders = {f["ean"]: f for f in csv.DictReader(open(INDEX, encoding="utf-8"))}
    Rr = B.rasy()
    fw = B.feature_words()
    pm, by_c = U.breed_lookup(Rr)
    cls = B.e_class()
    out = []
    for m in rows:
        lid = int(m["listing_id"])
        st = stan[str(lid)]
        why = []
        raw = html.unescape(st["title"]).split(" Tombstone Plaque")[0]
        name = NAME_FIX.get(raw, raw)
        rid, key, w2 = U.resolve({"gatunek": "kot", "nazwa_w_tytule": name, "folder": folders[m["ean"]]["nazwa"]}, Rr, fw, pm, by_c)
        why += list(w2)
        if lid in FEATURE_BY_LID:
            key = FEATURE_BY_LID[lid]
        rr = Rr.get(("kot", rid)) if rid else None
        if not rr:
            why.append("rasa nierozpoznana: " + name)
        else:
            miss = [c for c in [U.NAME_COL[l] for l in LANG_ALL] if not rr.get(c)]
            if miss:
                why.append("brak tłumaczenia nazwy rasy: " + ",".join(miss))
        if key and key not in fw:
            why.append("odmiana bez słowa: " + key)
        if len(st["images"]) != 2:
            why.append(f"zdjęć w stanie żywym: {len(st['images'])} (oczekiwano 2)")
        f = folders.get(m["ean"])
        vids = [x.split(":")[0] for x in (f["wideo_rozmiar"].split("|") if f else []) if x]
        nb = [v for v in vids if "-brand" not in v]
        br = [v for v in vids if "-brand" in v]
        if len(nb) != 1:
            why.append(f"filmy bez brand w folderze: {len(nb)}")
        if st["videos"]:
            why.append("oferta ma już wideo")
        if B.is_done(lid):
            why.append("już zoptymalizowana")
        out.append({"lid": lid, "st": st, "views": int(m["wyswietlenia"]), "rr": rr, "breed": rr["Nazwa EN (główna)"] if rr else name, "key": key, "typ": cls.get(rid, "") if rid else "",
                    "ean": m["ean"], "folder": m["folder"], "film2": nb[0] if nb else "", "why": why})
    out.sort(key=lambda c: (c["views"], c["lid"]))
    return out, fw


def tnames_of(c, fw):
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    d = {code: (c["rr"][U.NAME_COL[code]] + " " + fwd.get(code, "")).strip() for code in LANG_ALL}
    d["en"] = (c["breed"] + " " + (U.feature_en(c["key"]) if c["key"] else "")).strip()
    return d


def render(c, fw):
    lid, rr = c["lid"], c["rr"]
    e = (rr.get("Potoczne EN") or "").strip()
    nick = e if c["typ"] == "zdrobnienie" else ""
    syn = e if c["typ"] == "synonim" else ""
    feat = U.feature_en(c["key"]) if c["key"] else ""
    name = (c["breed"] + " " + feat).strip()
    desc, ch = en_description(lid, c["breed"], nick, syn)
    title, tidx = pick_title(lid, en()["titles"], name)
    enx = {"title": title, "description": desc, "tags": en_tags(lid), "alts": en_alts(name), "wzorzec_tytulu": tidx, "ABC": {k: v[0] + 1 for k, v in ch.items()},
           "nick": nick, "synonim": syn, "odmiana": c["key"], "slow_w_tytule": words(title)}
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    trans = {code: tr_render(code, lid, rr, ch, tidx, fwd.get(code, "")) for code in LANG_ALL}
    return enx, trans


def check(enx, trans, tnames):
    p = []
    if len(enx["title"]) > 140 or enx["slow_w_tytule"] > MAX_WORDS:
        p.append(f"tytuł EN {len(enx['title'])} zn. / {enx['slow_w_tytule']} słów")
    if repeated(enx["title"], tnames["en"]):
        p.append("powtórzone słowa w tytule EN: " + ",".join(repeated(enx["title"], tnames["en"])))
    first = enx["description"].split("\n\n")[0]
    if sum(1 for x in re.split(r"(?<=[.!?]) ", first) if re.search(r"\bfelt\b|\bhook\b", x)) > 1:
        p.append("filc/haczyk w więcej niż jednym zdaniu pierwszego akapitu")
    if re.search(r"\bbust\b|sketch|\bgeometric portrait\b.{0,40}(on request|made to order)", enx["description"], re.I):
        p.append("zakazane sformułowanie w opisie (bust / sketch)")
    if len(enx["tags"]) != 13 or len(set(enx["tags"])) != 13 or any(len(x) > 20 for x in enx["tags"]):
        p.append("tagi EN")
    if "{" in enx["title"] + enx["description"]:
        p.append("znacznik w opisie EN")
    for code, d in trans.items():
        if len(d["title"]) > 140:
            p.append(f"tytuł {code} {len(d['title'])} zn.")
        if repeated_tr(d["title"], tnames[code]):
            p.append(f"powtórzone słowa w tytule {code}: " + ",".join(repeated_tr(d["title"], tnames[code])))
        if len(d["tags"]) != 13 or len(set(d["tags"])) != 13 or any(len(x) > 20 for x in d["tags"]):
            p.append(f"tagi {code}")
        if "{" in d["title"] + d["description"]:
            p.append(f"znacznik w {code}")
    return p


def raport():
    cs, fw = build_candidates()
    out = ROOT / "plans" / "plakietki_koty_raport.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "wyswietlenia", "rasa", "odmiana", "ean", "tytul_nowy", "slow", "film2", "uwagi"])
        for c in cs:
            why, nt, nw = list(c["why"]), "", ""
            if not [x for x in why if x != "już zoptymalizowana"] and c["rr"]:
                enx, trans = render(c, fw)
                why += check(enx, trans, tnames_of(c, fw))
                nt, nw = enx["title"], enx["slow_w_tytule"]
            w.writerow([c["lid"], c["views"], c["breed"], c["key"], c["ean"], nt, nw, c["film2"], "; ".join(why)])
    r = list(csv.DictReader(open(out, encoding="utf-8")))
    print("ofert:", len(r), "| z uwagami:", sum(1 for x in r if x["uwagi"]), "| słów w tytule:", sorted(Counter(x["slow"] for x in r).items()))
    for x in r:
        if x["uwagi"]:
            print(" -", x["listing_id"], x["rasa"], "|", x["uwagi"])


def plan(n, size):
    if glob.glob(str(ROOT / "logs" / f"partia_plakietki_koty_{n:03d}_*.jsonl")):
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
        prob = check(enx, trans, tnames_of(c, fw))
        if prob:
            print("pomijam", c["lid"], c["breed"], prob)
            continue
        c.update(en=enx, trans=trans)
        batch.append(c)
        if len(batch) == size:
            break
    with open(ROOT / "plans" / f"partia_plakietki_koty_{n:03d}.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "listing_id", "wyswietlenia", "rasa", "odmiana", "ean", "tytul_przed", "tytul_po", "slow", "wzorzec", "ABC", "tagi", "film2"])
        for i, c in enumerate(batch, 1):
            e = c["en"]
            w.writerow([i, c["lid"], c["views"], c["breed"], c["key"], c["ean"], c["st"]["title"], e["title"], e["slow_w_tytule"], e["wzorzec_tytulu"], "".join(f"{k}{v}" for k, v in e["ABC"].items()),
                        "; ".join(e["tags"]), c["film2"]])
    dry = []
    for c in batch:
        u = lambda fn: BASE_V + urllib.parse.quote(c["folder"]) + "/" + urllib.parse.quote(fn)
        dry.append({"listing_id": c["lid"], "rasa": c["breed"], "ean": c["ean"], "film1_nazwa": VIDEO1.name, "film2": u(c["film2"]), "film2_nazwa": c["film2"],
                    "images_before": {str(r[0]): r[1] for r in c["st"]["images"]}, "tytul_przed": c["st"]["title"], "en": c["en"], "tlumaczenia": c["trans"]})
    (ROOT / "plans" / f"partia_plakietki_koty_{n:03d}_dryrun.json").write_text(json.dumps(dry, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(batch)} ofert")
    return batch


def personalization():
    return [
        {"question_type": "dropdown", "question_text": "Do you want to personalize the plaque?", "required": False, "options": [{"label": "No, as shown"}, {"label": "Yes, personalize it"}]},
        {"question_type": "unlabeled_upload", "question_text": "Your photo (optional)", "required": False, "max_allowed_files": 1,
         "instructions": "Attach a clear photo of your pet, or send it later by Etsy message. Leave empty if you chose No."},
        {"question_type": "dropdown", "question_text": "Print style (if own photo)", "required": False, "options": [{"label": "Original photo"}, {"label": "No background"}]},
        {"question_type": "text_input", "question_text": "Name and dates (optional)", "required": False, "max_allowed_characters": 50,
         "instructions": "Name, or name and dates, as they should appear, e.g. Felix 12/29/2013 - 11/9/2026. Leave empty for no text."},
        {"question_type": "dropdown", "question_text": "Plaque orientation (if own photo)", "required": False, "options": [{"label": "Vertical"}, {"label": "Horizontal"}]},
    ]


def steps_for(c):
    en_, tr, lid = c["en"], c["trans"], c["lid"]
    b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
    s = [{"id": "listing", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"title": en_["title"], "description": en_["description"], "tags": ",".join(en_["tags"])}},  # materiały tekstowe bez zmian ("ceramic plate")
         {"id": "wlasciwosc_materials", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "kind": "form", "fields": {"value_ids": MAT_VALUES[0], "values": MAT_VALUES[1]}},
         {"id": "how_its_made", "method": "PATCH", "path": b, "kind": "form", "fields": {"who_made": "collective", "when_made": "made_to_order", "is_supply": "false"}},
         {"id": "personalizacja", "method": "POST", "path": b + "/personalization", "kind": "json", "fields": {"personalization_questions": personalization()}}]
    for k in sorted(c["images_before"]):
        s.append({"id": f"alt_{k}", "method": "POST", "path": b + "/images", "kind": "alt_existing", "rank": k, "fields": {"alt_text": en_["alts"][k]}})
    for i, (path, alt) in enumerate(NEW_IMAGES, 1):
        s.append({"id": f"zdjecie_{len(c['images_before']) + i}", "method": "POST", "path": b + "/images", "kind": "image_new", "rank": len(c["images_before"]) + i, "file": str(path), "fields": {"alt_text": alt}})
    s.append({"id": "wideo_1_grafika", "method": "POST", "path": b + "/videos", "kind": "video", "src": str(VIDEO1), "fields": {"name": VIDEO1.name}})
    s.append({"id": "wideo_2_rasa", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film2"], "fields": {"name": c["film2_nazwa"]}})
    for code in LANG_ALL:
        d = tr[code]
        s.append({"id": f"tlumaczenie_{code}", "method": "POST", "path": b + f"/translations/{code}", "kind": "form",
                  "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return s


def load_frozen(n):
    jp = ROOT / "plans" / f"partia_plakietki_koty_{n:03d}_dryrun.json"
    if not jp.exists():
        sys.exit(f"BŁĄD: brak zatwierdzonego planu partii {n}")
    out = []
    for x in json.load(open(jp, encoding="utf-8")):
        x["en"]["alts"] = {int(k): v for k, v in x["en"]["alts"].items()}
        out.append({"lid": x["listing_id"], "en": x["en"], "trans": x["tlumaczenia"], "film2": x["film2"], "film2_nazwa": x["film2_nazwa"],
                    "tytul_przed": x["tytul_przed"], "images_before": {int(k): v for k, v in x["images_before"].items()}})
    return out


def preflight(c, live):
    pr = []
    if "error" in live:
        return ["odczyt oferty: " + str(live["error"])[:100]]
    if live["state"] != "active":
        pr.append("status " + live["state"])
    n0 = len(c["images_before"])
    if len(live.get("images", [])) not in range(n0, n0 + len(NEW_IMAGES) + 1):
        pr.append(f"zdjęć: {len(live.get('images', []))} (oczekiwano {n0})")
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
    summary = ROOT / "logs" / f"partia_plakietki_koty_{n:03d}_{time.strftime('%Y-%m-%d')}.jsonl"
    print(f"partia plakietki grafika {n}: {len(batch)} ofert z planu")
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
            elif s["kind"] == "image_new":
                cur = api.get(f"/v3/application/listings/{lid}?includes=Images").get("images", [])
                if len(cur) >= s["rank"]:
                    resp = {"ok": "zdjęcie już w ofercie (wykryte)"}
                else:
                    fp = Path(s["file"])
                    data, ct = base.multipart({"rank": str(s["rank"]), "overwrite": "false", "alt_text": s["fields"]["alt_text"]}, ("image", fp.name), fp.read_bytes(), "image/jpeg")
                    resp = api.request("POST", s["path"], headers={"Content-Type": ct}, data=data, retries=1)
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
            n0 = len(ids_before)
            exp_alts = dict(c["en"]["alts"])
            for i, (path, alt) in enumerate(NEW_IMAGES, 1):
                exp_alts[n0 + i] = alt
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(imgs), "zdjec_ok": len(imgs) == n0 + len(NEW_IMAGES),
                   "alt_ok": all(html.unescape(im.get("alt_text") or "") == exp_alts.get(im["rank"]) for im in imgs) if len(imgs) == len(exp_alts) else False,
                   "kolejnosc_ok": [im["listing_image_id"] for im in imgs[:n0]] == [ids_before[k] for k in sorted(ids_before)] if len(imgs) >= n0 else False,
                   "wideo": len(after.get("videos", [])), "pytan": len((after.get("personalization") or {}).get("personalization_questions", [])),
                   "tlumaczen": sum(1 for k, v in after["translations"].items() if v and k != "en-US"), "who_made": after["who_made"],
                   "materialy_ok": sorted(after["materials"]) == sorted(live["materials"]), "materials_prop": sorted(mat.get("values", [])), "proba": attempt + 1}
            good = chk["cena_ok"] and chk["stan_ok"] and chk["status_ok"] and chk["zdjec_ok"] and chk["alt_ok"] and chk["kolejnosc_ok"] and chk["wideo"] == 2 and chk["pytan"] == 5 \
                and chk["tlumaczen"] >= 8 and chk["who_made"] == "collective" and chk["materialy_ok"] and chk["materials_prop"] == sorted(MAT_VALUES[1].split(","))
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
