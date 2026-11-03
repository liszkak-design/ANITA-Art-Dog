#!/usr/bin/env python3
"""Optymalizacja 38 tablic pamiątkowych "Memorial Board" (deska MDF 34 x 24 cm, relief z cold cast bronze, tabliczka z grawerem; sekcja "Plaques with dog").
  python3 -I scripts/batch_hanging.py raport                      # kontrola wszystkich ofert bez zapisu (plans/hanging_raport.csv)
  python3 -I scripts/batch_hanging.py plan N [--lid=ID[,ID]] [--size=K]   # dry-run partii N (plans/partia_hanging_00N.csv i _dryrun.json)
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
BASE_V = "https://www.artdog.com.pl/VIDEO/III%20tura/022.%20Hanging/"
STAN = ROOT / "plans" / "hanging_stan_zywy.json"
MAPA = ROOT / "plans" / "hanging_mapa.csv"
INDEX = ROOT / "plans" / "hanging_foldery_index.csv"
DECYZJE = ROOT / "plans" / "hanging_decyzje.json"
CLOSEUP = ROOT / "media" / "hanging" / "zblizenie_haczyk_filc.jpg"
CACHE = B.CACHE.parent / "hanging"
LANG_ALL = U.LANG_ALL
MAX_WORDS = 14
MATERIALS_TEXT = "cold cast bronze"
MAT_VALUES = ("71,227", "Bronze,Resin")  # Bronze, Resin
DIM_PROPS = (("h", 47626759834, "Height"), ("w", 47626759898, "Width"), ("d", 54142602037, "Depth"))  # cm, scale_id 7
SCALE_CM = 7
NAME_FIX = {"Fila Brasileiro, Brazilian Mastiff": "Fila Brasileiro", "Grand Basset Griffo Vendeen": "Basset Griffon Vendéen", "Mastino Napoletano, Neapolitan Mastiff": "Neapolitan Mastiff",
            "Dog de Bordeaux": "Dogue de Bordeaux", "English Bulldog": "Bulldog", "Japan Chin": "Japanese Chin", "Dachshund wirehaired": "Dachshund", "Dachshund long haired": "Dachshund",
            "Dachshund smothhaired": "Dachshund", "Fox Terrier wirehaired": "Fox Terrier", "Wheaten Terrier Soft Coated": "Irish Soft Coated Wheaten Terrier", "Corgi Pembroke": "Pembroke Welsh Corgi",
            "Chihuahua long haired": "Chihuahua", "Miniature Pincher, Pinscher": "Miniature Pinscher", "Scottish Sheep Dog": "Collie", "Sheltie, Shetland Sheepdog": "Shetland Sheepdog",
            "Borzoi Russian Wolfhound": "Borzoi", "Saint Bernard": "St. Bernard", "English Staffordshire Terrier": "Staffordshire Bull Terrier", "Staffordshire Terrier": "Staffordshire Bull Terrier",
            "Belgian Shepherd": "Belgian Shepherd", "Bouvier des Flandres": "Bouvier", "Malinois": "Malinois Belgian Shepherd"}
FEATURE_BY_LID = {971371492: "Dachshund Wire-haired", 985333223: "Dachshund Long-haired", 985358693: "Dachshund Smooth-haired", 985331775: "Chihuahua Long-haired",
                  985331389: "Chihuahua Short-haired", 985339913: "Fox Terrier Wire", 971390684: "Collie Rough", 971366156: "cropped ears", 971380106: "cropped ears", 985351947: "cropped ears"}
HOLD = {971376774: "English Staffordshire Terrier: do potwierdzenia rasa (Staffordshire Bull Terrier czy American Staffordshire Terrier)", 971393258: "Staffordshire Terrier: do potwierdzenia rasa (Staffordshire Bull Terrier czy American Staffordshire Terrier)"}
# zdjęcia z filcem rozpoznane wzrokowo (03.11.2026): zbliżenie haczyka i widok tyłu (listing_id, ranga)
CLOSE_RANKS = {(985357391, 7), (971399078, 7), (985360373, 8), (971399904, 8), (971372844, 7), (971392262, 7)}
BACK_RANKS = {(985357391, 6), (971399078, 6), (971367252, 6), (985360373, 7), (971399904, 7), (971372844, 6), (1362981052, 8), (985327151, 5), (971392262, 6)}
EN_CORE = ["hanging dog bust", "dog head wall decor", "dog lover gift", "wall hanging dog", "dog memorial gift"]
EN_POOL = ["dog trophy", "dog owner gift", "bronze look decor", "dog bust", "office decor dog", "pet loss gift", "dog wall art", "dog head bust", "dog show gift", "housewarming gift",
           "dog figurine", "dog statuette", "pet memorial gift", "hunter gift", "dog sculpture gift", "dog statue decor", "animal wall hanging"]
ALT = {"dims": "The {BREED} bust with its height, width, depth and weight.", "back": "Back of the {BREED} bust, protected with soft green felt and fitted with a hanging hook.",
       "close": "Close-up of the metal hanging hook and the soft felt on the back of the bust.", "main": "{BREED} hanging dog bust with a bronze-look finish.",
       "other": "The {BREED} hanging bust with a bronze-look finish, seen from another angle."}
STOP = U.STOP | {"dog"}
_EN, _TR = {}, {}


def sec(t, a, b=None):
    return R.sec(t, a, b)


def en():
    if _EN:
        return _EN
    t = (TPL / "hanging_propozycja_tekstow.md").read_text(encoding="utf-8")
    for x in EN_CORE + EN_POOL:
        assert x in t, x
    _EN["titles"] = re.findall(r"^\d\. (\{BREED\}.*)$", sec(t, "## 1. Tytuły", "## 2."), re.M)
    s3 = sec(t, "## 3. Pierwszy akapit", "## 4.")
    bank = lambda s: [(m.group(2) or "", m.group(3)) for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", s, re.M)]
    iA, iB, iC = s3.index("**A bez"), s3.index("**B (zast"), s3.index("**C (zaw")
    _EN["A"], _EN["B"], _EN["C"] = bank(s3[iA:iB]), bank(s3[iB:iC]), bank(s3[iC:])
    _EN["fixed"] = re.search(r"```\n(.*?)\n```", sec(t, "## 4. Sekcje stałe", "## 5."), re.S).group(1)
    assert len(_EN["titles"]) == 6 and len(_EN["A"]) == 11 and len(_EN["B"]) == 4 and len(_EN["C"]) == 3, (len(_EN["titles"]), len(_EN["A"]), len(_EN["B"]), len(_EN["C"]))
    assert "{H}" in _EN["fixed"] and "plaque" not in _EN["fixed"].lower()
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


def pick_title(lid, pats, name):
    start = U.pick(lid, "T", len(pats))
    fb = None
    for k in range(len(pats)):
        i = (start + k) % len(pats)
        t = re.sub(r"\s+", " ", pats[i].replace("{BREED}", name)).strip()
        fb = fb or (t, i + 1)
        if len(t) <= 140 and words(t) <= MAX_WORDS:
            return t, i + 1
    return fb


def en_description(lid, name, nick, syn, dm):
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
    txt = " ".join(parts) + "\n\n" + fill_dims(E["fixed"].replace("{BREED}", name), dm)
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


def en_alts(name, kinds):
    return {k: ALT[v].replace("{BREED}", name) for k, v in kinds.items()}


def image_kinds(lid, ranks):
    out = {}
    for r in ranks:
        out[r] = "close" if (lid, r) in CLOSE_RANKS else "back" if (lid, r) in BACK_RANKS else "dims" if r == 2 else "main" if r == 1 else "other"
    return out


def tr_load(code):
    if code in _TR:
        return _TR[code]
    t = (TPL / f"hanging_tlumaczenie_{code}.md").read_text(encoding="utf-8")
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
    assert len(d["titles"]) == 6 and len(d["core"]) == 5 and len(d["A"]) == 5 and len(d["B"]) == 3 and len(d["C"]) == 3 and len(d["pool"]) == 17, \
        (code, len(d["titles"]), len(d["core"]), len(d["A"]), len(d["B"]), len(d["C"]), len(d["pool"]))
    _TR[code] = d
    return d


def tr_render(code, lid, rr, ch, tidx, feat, dm):
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
        if len(title) <= 140:
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
    return {"title": title, "description": " ".join(par) + "\n\n" + fill_dims(d["fixed"].replace("{B}", b), dm, code != "en"), "tags": d["core"] + pool}


def dims_all():
    sys.path.insert(0, str(ROOT / "scripts"))
    from hanging_wymiary_zdjecia import DIM
    d = {k: tuple(v) for k, v in DIM.items()}
    for k, v in json.load(open(DECYZJE, encoding="utf-8"))["wymiary_cm_HxWxD"].items():
        d[int(k)] = tuple(v)
    return d


def build_candidates():
    stan = json.load(open(STAN, encoding="utf-8"))
    rows = list(csv.DictReader(open(MAPA, encoding="utf-8")))
    folders = {f["ean"]: f for f in csv.DictReader(open(INDEX, encoding="utf-8"))}
    DM = dims_all()
    Rr = B.rasy()
    fw = B.feature_words()
    pm, by_c = U.breed_lookup(Rr)
    cls = B.e_class()
    out = []
    for m in rows:
        lid = int(m["listing_id"])
        st = stan[str(lid)]
        why = []
        raw = html.unescape(st["title"]).split(" Hanging Statue")[0]
        name = NAME_FIX.get(raw, raw)
        rid, key, w2 = U.resolve({"gatunek": "pies", "nazwa_w_tytule": name, "folder": name}, Rr, fw, pm, by_c)
        why += list(w2)
        if lid in FEATURE_BY_LID:
            key = FEATURE_BY_LID[lid]
        if lid in HOLD:
            why.append(HOLD[lid])
        rr = Rr.get(("pies", rid)) if rid else None
        if not rr:
            why.append("rasa nierozpoznana: " + name)
        else:
            miss = [c for c in [U.NAME_COL[l] for l in LANG_ALL] if not rr.get(c)]
            if miss:
                why.append("brak tłumaczenia nazwy rasy: " + ",".join(miss))
        if key and key not in fw:
            why.append("odmiana bez słowa: " + key)
        dm = DM.get(lid)
        if not dm or None in dm:
            why.append("brak wymiarów")
        f = folders.get(m["ean"])
        vids = [x.split(":")[0] for x in (f["wideo_rozmiar"].split("|") if f else []) if x]
        nb = [v for v in vids if "-brand" not in v]
        br = [v for v in vids if "-brand" in v]
        if len(nb) != 1 or len(br) != 1:
            why.append(f"filmy: bez brand {len(nb)}, brand {len(br)}")
        if st["videos"]:
            why.append("oferta ma już wideo")
        if B.is_done(lid):
            why.append("już zoptymalizowana")
        out.append({"lid": lid, "st": st, "views": int(m["wyswietlenia"]), "rr": rr, "breed": rr["Nazwa EN (główna)"] if rr else name, "key": key, "typ": cls.get(rid, "") if rid else "",
                    "dm": dm, "ean": m["ean"], "folder": m["folder"], "film1": nb[0] if nb else "", "film2": br[0] if br else "", "why": why})
    out.sort(key=lambda c: (c["views"], c["lid"]))
    return out, fw


def render(c, fw):
    lid, rr = c["lid"], c["rr"]
    e = (rr.get("Potoczne EN") or "").strip()
    nick = e if c["typ"] == "zdrobnienie" else ""
    syn = e if c["typ"] == "synonim" else ""
    feat = U.feature_en(c["key"]) if c["key"] else ""
    name = (c["breed"] + " " + feat).strip()
    desc, ch = en_description(lid, c["breed"], nick, syn, c["dm"])
    title, tidx = pick_title(lid, en()["titles"], name)
    enx = {"title": title, "description": desc, "tags": en_tags(lid), "alts": en_alts(name, image_kinds(lid, [r[0] for r in c["st"]["images"]])), "wzorzec_tytulu": tidx, "ABC": {k: v[0] + 1 for k, v in ch.items()},
           "nick": nick, "synonim": syn, "odmiana": c["key"], "slow_w_tytule": words(title)}
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    trans = {code: tr_render(code, lid, rr, ch, tidx, fwd.get(code, ""), c["dm"]) for code in LANG_ALL}
    return enx, trans


def check(enx, trans):
    p = []
    if len(enx["title"]) > 140 or enx["slow_w_tytule"] > MAX_WORDS:
        p.append(f"tytuł EN {len(enx['title'])} zn. / {enx['slow_w_tytule']} słów")
    if "cold cast bronze" in enx["title"].lower() or re.search(r"plaque", enx["title"] + enx["description"] + " ".join(enx["tags"]), re.I):
        p.append("zakazane słowo (cold cast bronze w tytule / plaque)")
    if len(enx["tags"]) != 13 or len(set(enx["tags"])) != 13 or any(len(x) > 20 for x in enx["tags"]):
        p.append("tagi EN")
    if "{" in enx["title"] + enx["description"]:
        p.append("znacznik w opisie EN")
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
    out = ROOT / "plans" / "hanging_raport.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "wyswietlenia", "rasa", "odmiana", "ean", "tytul_nowy", "slow", "film1", "film2", "uwagi"])
        for c in cs:
            why, nt, nw = list(c["why"]), "", ""
            if not [x for x in why if x != "już zoptymalizowana"] and c["rr"]:
                enx, trans = render(c, fw)
                why += check(enx, trans)
                nt, nw = enx["title"], enx["slow_w_tytule"]
            w.writerow([c["lid"], c["views"], c["breed"], c["key"], c["ean"], nt, nw, c["film1"], c["film2"], "; ".join(why)])
    r = list(csv.DictReader(open(out, encoding="utf-8")))
    print("ofert:", len(r), "| z uwagami:", sum(1 for x in r if x["uwagi"]), "| słów w tytule:", sorted(Counter(x["slow"] for x in r).items()))
    for x in r:
        if x["uwagi"]:
            print(" -", x["listing_id"], x["rasa"], "|", x["uwagi"])


def plan(n, size):
    if glob.glob(str(ROOT / "logs" / f"partia_hanging_{n:03d}_*.jsonl")):
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
    with open(ROOT / "plans" / f"partia_hanging_{n:03d}.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "listing_id", "wyswietlenia", "rasa", "odmiana", "ean", "tytul_przed", "tytul_po", "slow", "wzorzec", "ABC", "tagi", "film1", "film2"])
        for i, c in enumerate(batch, 1):
            e = c["en"]
            w.writerow([i, c["lid"], c["views"], c["breed"], c["key"], c["ean"], c["st"]["title"], e["title"], e["slow_w_tytule"], e["wzorzec_tytulu"], "".join(f"{k}{v}" for k, v in e["ABC"].items()),
                        "; ".join(e["tags"]), c["film1"], c["film2"]])
    dry = []
    for c in batch:
        u = lambda fn: BASE_V + urllib.parse.quote(c["folder"]) + "/" + urllib.parse.quote(fn)
        dry.append({"listing_id": c["lid"], "rasa": c["breed"], "ean": c["ean"], "film1": u(c["film1"]), "film1_nazwa": c["film1"], "film2": u(c["film2"]), "film2_nazwa": c["film2"],
                    "images_before": {str(r[0]): r[1] for r in c["st"]["images"]}, "tytul_przed": c["st"]["title"], "wymiary_HxWxD_cm": list(c["dm"]),
                    "dodac_zblizenie": not any((c["lid"], r[0]) in CLOSE_RANKS for r in c["st"]["images"]), "en": c["en"], "tlumaczenia": c["trans"]})
    (ROOT / "plans" / f"partia_hanging_{n:03d}_dryrun.json").write_text(json.dumps(dry, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(batch)} ofert")
    return batch


def has_close(lid, n):
    return any((lid, r) in CLOSE_RANKS for r in range(1, n + 1))


def steps_for(c):
    en_, tr, lid = c["en"], c["trans"], c["lid"]
    b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
    n = len(c["images_before"])
    s = [{"id": "listing", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"title": en_["title"], "description": en_["description"], "tags": ",".join(en_["tags"]), "materials": MATERIALS_TEXT}},
         {"id": "wlasciwosc_materials", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "kind": "form", "fields": {"value_ids": MAT_VALUES[0], "values": MAT_VALUES[1]}}]
    for i, (key, pid, nm) in enumerate(DIM_PROPS):
        s.append({"id": f"atrybut_{nm.lower()}", "method": "PUT", "path": f"{b}/properties/{pid}", "kind": "form", "fields": {"value_ids": "", "values": num(c["dm"][i]), "scale_id": str(SCALE_CM)}})
    for k in sorted(c["images_before"]):
        s.append({"id": f"alt_{k}", "method": "POST", "path": b + "/images", "kind": "alt_existing", "rank": k, "fields": {"alt_text": en_["alts"][k]}})
    if not has_close(lid, n):
        s.append({"id": "zdjecie_zblizenie", "method": "POST", "path": b + "/images", "kind": "image_new", "rank": n + 1, "fields": {"alt_text": ALT["close"]}})
    s.append({"id": "wideo_1_bez_brand", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film1"], "fields": {"name": c["film1_nazwa"]}})
    s.append({"id": "wideo_2_brand", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film2"], "fields": {"name": c["film2_nazwa"]}})
    for code in LANG_ALL:
        d = tr[code]
        s.append({"id": f"tlumaczenie_{code}", "method": "POST", "path": b + f"/translations/{code}", "kind": "form",
                  "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return s


def load_frozen(n):
    jp = ROOT / "plans" / f"partia_hanging_{n:03d}_dryrun.json"
    if not jp.exists():
        sys.exit(f"BŁĄD: brak zatwierdzonego planu partii hanging {n}")
    out = []
    for x in json.load(open(jp, encoding="utf-8")):
        x["en"]["alts"] = {int(k): v for k, v in x["en"]["alts"].items()}
        out.append({"lid": x["listing_id"], "en": x["en"], "trans": x["tlumaczenia"], "film1": x["film1"], "film1_nazwa": x["film1_nazwa"], "film2": x["film2"], "film2_nazwa": x["film2_nazwa"],
                    "tytul_przed": x["tytul_przed"], "dm": x["wymiary_HxWxD_cm"], "images_before": {int(k): v for k, v in x["images_before"].items()}})
    return out


def preflight(c, live):
    pr = []
    if "error" in live:
        return ["odczyt oferty: " + str(live["error"])[:100]]
    if live["state"] != "active":
        pr.append("status " + live["state"])
    if len(live.get("images", [])) not in (len(c["images_before"]), len(c["images_before"]) + 1):
        pr.append(f"zdjęć: {len(live.get('images', []))} (oczekiwano {len(c['images_before'])})")
    if live.get("personalization", {}) and live["personalization"].get("personalization_questions"):
        pr.append("oferta ma personalizację")
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
    summary = ROOT / "logs" / f"partia_hanging_{n:03d}_{time.strftime('%Y-%m-%d')}.jsonl"
    print(f"partia hanging {n}: {len(batch)} ofert z planu")
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
                if len(vids) >= (1 if s["id"] == "wideo_1_bez_brand" else 2):
                    U.zlog(lid, s["id"], "backup/" + p.name, "już w ofercie (wykryte przy wznowieniu)", "ok")
                    continue
            if s["kind"] == "alt_existing":
                resp = U.alt_existing(s, c, ids_before)
            elif s["kind"] == "image_new":
                cur = api.get(f"/v3/application/listings/{lid}?includes=Images").get("images", [])
                if len(cur) > len(ids_before):
                    resp = {"ok": "zbliżenie już w ofercie (wykryte)"}
                else:
                    data, ct = base.multipart({"rank": str(s["rank"]), "overwrite": "false", "alt_text": s["fields"]["alt_text"]}, ("image", CLOSEUP.name), CLOSEUP.read_bytes(), "image/jpeg")
                    resp = api.request("POST", s["path"], headers={"Content-Type": ct}, data=data, retries=1)
            elif s["kind"] == "video":
                path = R.curl_to(s["src"], CACHE / "wideo" / s["fields"]["name"])
                data, ct = base.multipart({"name": s["fields"]["name"]}, ("video", path.name), path.read_bytes(), "video/mp4")
                resp = api.request(s["method"], s["path"], headers={"Content-Type": ct}, data=data, retries=1)
                if not base.ok(resp) and re.search(r"reset|timed out|timeout|disconnect|closed", str(resp), re.I):
                    time.sleep(5)
                    vids = api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos", [])
                    if len(vids) >= (1 if s["id"] == "wideo_1_bez_brand" else 2):
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
            add = not has_close(lid, n0)
            exp_alts = dict(c["en"]["alts"])
            if add:
                exp_alts[n0 + 1] = ALT["close"]
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(imgs), "zdjec_ok": len(imgs) == n0 + (1 if add else 0),
                   "alt_ok": all(html.unescape(im.get("alt_text") or "") == exp_alts.get(im["rank"]) for im in imgs) if len(imgs) == len(exp_alts) else False,
                   "kolejnosc_ok": [im["listing_image_id"] for im in imgs[:n0]] == [ids_before[k] for k in sorted(ids_before)] if len(imgs) >= n0 else False,
                   "wideo": len(after.get("videos", [])), "pytan": len((after.get("personalization") or {}).get("personalization_questions", [])),
                   "tlumaczen": sum(1 for k, v in after["translations"].items() if v and k != "en-US"), "who_made": after["who_made"],
                   "materialy_ok": sorted(after["materials"]) == sorted(MATERIALS_TEXT.split(",")), "materials_prop": sorted(mat.get("values", [])),
                   "wymiary_ok": all(any(pp["property_id"] == pid and pp.get("values") == [num(c["dm"][i])] and pp.get("scale_id") == SCALE_CM for pp in props.get("results", [])) for i, (key, pid, nm) in enumerate(DIM_PROPS)),
                   "proba": attempt + 1}
            good = chk["cena_ok"] and chk["stan_ok"] and chk["status_ok"] and chk["zdjec_ok"] and chk["alt_ok"] and chk["kolejnosc_ok"] and chk["wideo"] == 2 and chk["pytan"] == 0 \
                and chk["tlumaczen"] >= 8 and chk["materialy_ok"] and chk["materials_prop"] == sorted(MAT_VALUES[1].split(",")) and chk["wymiary_ok"]
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
