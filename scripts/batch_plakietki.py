#!/usr/bin/env python3
"""Optymalizacja 38 płaskorzeźb "plakietki same" (oferty "{rasa} Bust, Cold Cast Bronze Sculpture, Small dog bust ..."; sekcja "Plaques with dog").
  python3 -I scripts/batch_plakietki.py raport                      # kontrola wszystkich ofert bez zapisu (plans/plakietki_raport.csv)
  python3 -I scripts/batch_plakietki.py plan N [--lid=ID[,ID]] [--size=K]   # dry-run partii N (plans/partia_plakietki_00N.csv i _dryrun.json)
  python3 -I scripts/batch_plakietki.py apply N --apply             # zapis do Etsy (tylko po "tak" właścicielki dla partii N)
Zakres na ofertę: kopia zapasowa; tytuł (do 14 słów), opis, 13 tagów, materiały tekstowe ("cold cast bronze"), Materials (Bronze, Resin), wymiary w atrybutach
(item_width = szerokość, item_height = wysokość, item_length = grubość, cm), alt texty 3 zdjęć (bez wymiany zdjęć), 2 filmy z folderu 219 (bez "brand" pierwszy, "brand" drugi),
8 tłumaczeń. Bez personalizacji. Teksty: templates/plakietki_propozycja_tekstow.md i plakietki_tlumaczenie_<język>.md. Kolejność: od najmniej do najczęściej oglądanych.
Limit API: etsy_api (okno 24 h, stop 9000).
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
BASE_V = "https://www.artdog.com.pl/VIDEO/IX%20tura/219.%20Plakietki%20same/"
STAN = ROOT / "plans" / "plakietki_stan_zywy.json"
MAPA = ROOT / "plans" / "plakietki_mapa.csv"
INDEX = ROOT / "plans" / "plakietki_foldery_index.csv"
MATIDS = json.load(open(ROOT / "plans" / "plakietki_material_ids.json"))
MAT_VALUES = (",".join(str(v[0]) for v in MATIDS["values"] if v[1] in ("Bronze", "Resin")), "Bronze,Resin")
MATERIALS_TEXT = "cold cast bronze"
CACHE = B.CACHE.parent / "plakietki"
LANG_ALL = U.LANG_ALL
MAX_WORDS = 14
NAME_FIX = {"Borzoi Russian Wolfhound": "Borzoi", "Staffordshire Bullterrier": "Staffordshire Bull Terrier", "Mastino Napoletano": "Neapolitan Mastiff"}
FEATURE_BY_LID = {1366900894: "Dachshund Wire-haired"}  # Dachshund: plakietka szorstkowłosa (arkusz "Jamnik szorstkowłosy", folder "Dachshund (wire)"), do potwierdzenia
EN_CORE = ["pet loss gift", "dog wall plaque", "dog keepsake", "flat dog relief", "dog lover gift", "sympathy gift", "dog remembrance"]
EN_POOL = ["dog memorial gift", "dog show trophy", "dog trophy", "home office decor", "dog bas relief", "dog memorial plaque", "bronze dog plaque", "pet memorial", "dog loss gift",
           "in memory of dog", "bronze look plaque", "garden memorial", "dog owner gift", "desk decor", "dog art", "dog head relief", "dog relief plaque", "breed trophy",
           "memorial keepsake", "dog head wall art"]
STOP = U.STOP
_EN, _TR = {}, {}


def sec(text, head, nxt=None):
    return R.sec(text, head, nxt)


def num(x, dec=False):
    s = f"{float(x):g}"
    return s.replace(".", ",") if dec else s


def inch(x, dec=False):
    s = f"{round(float(x) / 2.54 + 1e-9, 1):.1f}"
    return s.replace(".", ",") if dec else s


def en():
    if _EN:
        return _EN
    t = (TPL / "plakietki_propozycja_tekstow.md").read_text(encoding="utf-8")
    for x in EN_CORE + EN_POOL:
        assert x in t, x
    _EN["titles"] = re.findall(r"^\d\. (\{BREED\}.*)$", sec(t, "## 1. Tytuły", "## 2."), re.M)
    s3 = sec(t, "## 3. Pierwszy akapit", "## 4.")
    bank = lambda s: [(m.group(2) or "", m.group(3)) for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", s, re.M)]
    iA, iB, iC = s3.index("**A bez"), s3.index("**B (zast"), s3.index("**C (prakt")
    _EN["A"], _EN["B"], _EN["C"] = bank(s3[iA:iB]), bank(s3[iB:iC]), bank(s3[iC:])
    _EN["fixed"] = re.search(r"```\n(.*?)\n```", sec(t, "## 4. Sekcje stałe", "## 5."), re.S).group(1)
    assert len(_EN["titles"]) == 6 and len(_EN["A"]) == 12 and len(_EN["B"]) == 4 and len(_EN["C"]) == 4, (len(_EN["titles"]), len(_EN["A"]), len(_EN["B"]), len(_EN["C"]))
    return _EN


def words(t):
    return len(t.replace(",", " ").split())


def dims_fill(text, d, dec):
    for k, v in (("{W}", num(d["w"], dec)), ("{H}", num(d["h"], dec)), ("{D}", num(d["d"], dec)), ("{Win}", inch(d["w"], dec)), ("{Hin}", inch(d["h"], dec)), ("{Din}", inch(d["d"], dec))):
        text = text.replace(k, v)
    return text


def article_fix(d, names):
    for nm in {n for n in names if n}:
        d = re.sub(r"\b([Aa]n?) (?=" + re.escape(nm) + r")", lambda m, nm=nm: (B.article(nm).capitalize() if m.group(1)[0] == "A" else B.article(nm)) + " ", d)
    return d


def pick_title(lid, pats, name, small):
    start = U.pick(lid, "T", len(pats))
    fb = None
    for k in range(len(pats)):
        i = (start + k) % len(pats)
        t = re.sub(r"\s+", " ", pats[i].replace("{BREED}", name).replace("{SIZE}", "Small" if small else "")).replace(" ,", ",").strip()
        fb = fb or (t, i + 1)
        if len(t) <= 140 and words(t) <= MAX_WORDS:
            return t, i + 1
    return fb


def en_description(lid, name, nick, syn, d):
    E = en()
    parts, chosen, nicks = [], {}, 0
    size = "small" if d["small"] else "compact"
    for slot in "ABC":
        if slot == "A":
            want = "N" if nick else ("S" if syn else "")
            opts = [(f, x) for f, x in E["A"] if f == want]
        else:
            opts = [(f, x) for f, x in E[slot] if f == "" or (f == "N" and nick and nicks < 2)]
        i = U.pick(lid, slot, len(opts))
        chosen[slot] = (i, opts[i][0])
        nicks += opts[i][0] == "N"
        parts.append(opts[i][1].replace("{BREED}", name).replace("{NICK}", nick).replace("{SYN}", syn).replace("{SIZE}", size))
    txt = " ".join(parts) + "\n\n" + dims_fill(E["fixed"].replace("{BREED}", name), d, False)
    txt = article_fix(txt, (name, syn))
    assert name in txt and "{" not in txt, txt[:200]
    return txt, chosen


def en_tags(lid):
    """7 stałych + 6 z puli; w puli bez wspólnych słów kluczowych między wybranymi tagami (poza "dog" i słowami z STOP); pula zawiera słowa ze stałych tagów (np. gift, plaque), więc filtr dotyczy tylko par z puli."""
    fixed = list(EN_CORE)
    used = set()
    picked = []
    for t in sorted(EN_POOL, key=lambda t: hashlib.sha256(f"{lid}:tag:{t}".encode()).hexdigest()):
        w = set(t.split()) - STOP - {"dog"}
        if t in fixed or (w & used):
            continue
        picked.append(t)
        used |= w
        if len(picked) == 6:
            break
    return fixed + picked


def en_alts(name, d):
    return {1: f"Front view of a hand-finished {name} dog head relief on a white background.", 2: f"Side view of the {name} relief showing its low profile.",
            3: f"Front view of the {name} relief with its width and height, {num(d['w'])} cm by {num(d['h'])} cm."}


def tr_load(code):
    if code in _TR:
        return _TR[code]
    t = (TPL / f"plakietki_tlumaczenie_{code}.md").read_text(encoding="utf-8")
    d = {"titles": re.findall(r"^\d\. (\{B\}.*)$", sec(t, "## Tytuł", "## Pierwszy akapit"), re.M)}
    d["small"] = re.search(r'`\{SMALL\}` = "(.*?)"', t).group(1)
    sb = sec(t, "## Pierwszy akapit", "## Sekcje stałe")
    ia, ib, ic = sb.index("**A**"), sb.index("**B**"), sb.index("**C**")
    bank = lambda s_: re.findall(r"^- [ABC]\d: (.*)$", s_, re.M)
    d["A"], d["B"], d["C"] = bank(sb[ia:ib]), bank(sb[ib:ic]), bank(sb[ic:])
    d["fixed"] = re.search(r"```\n(.*?)\n```", t, re.S).group(1)
    tg = sec(t, "## Tagi")
    item = lambda s_: [x.strip() for x, _ in re.findall(r"([^,:*()\n]+?) \((\d+)\)", s_)]
    d["core"] = item(re.search(r"\*\*Stałe:\*\* (.*)", tg).group(1).split(" (EN:")[0])
    d["pool"] = item(re.search(r"\*\*Pula:\*\* (.*)", tg).group(1))
    assert len(d["titles"]) == 6 and len(d["core"]) == 7 and len(d["A"]) == 5 and len(d["B"]) == 3 and len(d["C"]) == 4 and len(d["pool"]) == 20, \
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
        title = re.sub(r"\s+", " ", d["titles"][(tidx - 1 + k) % 6].replace("{B}", name).replace("{SMALL}", d["small"] if dm["small"] else "")).strip()
        title = dims_fill(title, dm, True)
        if len(title) <= 140:
            break
    fx = dims_fill(d["fixed"].replace("{B}", b), dm, True)
    order = sorted(d["pool"], key=lambda x: hashlib.sha256(f"{lid}:{code}:{x}".encode()).hexdigest())
    pool, used = [], set()
    for x in order:  # bez powtórzeń tego samego słowa kluczowego (min. 5 liter) między wybranymi tagami z puli
        w = {t.lower() for t in re.findall(r"\w{5,}", x)}
        if w & used:
            continue
        pool.append(x)
        used |= w
        if len(pool) == 6:
            break
    for x in order:  # uzupełnienie, gdyby filtr zostawił mniej niż 6
        if len(pool) == 6:
            break
        if x not in pool:
            pool.append(x)
    return {"title": title, "description": " ".join(par) + "\n\n" + fx, "tags": d["core"] + pool}


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
        raw = st["title"].split(" Bust")[0]
        name = NAME_FIX.get(raw, raw)
        rid, key, w2 = U.resolve({"gatunek": "pies", "nazwa_w_tytule": name, "folder": name}, Rr, fw, pm, by_c)
        why += list(w2)
        if lid in FEATURE_BY_LID:
            key = FEATURE_BY_LID[lid]
        rr = Rr.get(("pies", rid)) if rid else None
        if not rr:
            why.append("rasa nierozpoznana: " + name)
        else:
            miss = [c for c in [U.NAME_COL[l] for l in LANG_ALL] if not rr.get(c)]
            if miss:
                why.append("brak tłumaczenia nazwy rasy: " + ",".join(miss))
        if key and key not in fw:
            why.append("odmiana bez słowa: " + key)
        f = folders.get(m["ean"])
        vids = [x.split(":")[0] for x in (f["wideo_rozmiar"].split("|") if f else []) if x]
        nb = [v for v in vids if "-brand" not in v]
        br = [v for v in vids if "-brand" in v]
        if len(nb) != 1 or len(br) != 1:
            why.append(f"filmy: bez brand {len(nb)}, brand {len(br)}")
        if len(st["images"]) != 3:
            why.append(f"zdjęć w stanie żywym: {len(st['images'])} (oczekiwano 3)")
        if B.is_done(lid):
            why.append("już zoptymalizowana")
        w, h, d = float(m["szerokosc_zdjecie"]), float(m["wysokosc_zdjecie"]), float(m["grubosc_arkusz"])
        out.append({"lid": lid, "st": st, "views": int(m["wyswietlenia"]), "rr": rr, "breed": rr["Nazwa EN (główna)"] if rr else name, "key": key, "typ": cls.get(rid, "") if rid else "",
                    "dims": {"w": w, "h": h, "d": d, "small": max(w, h) <= 10}, "ean": m["ean"], "folder": m["folder"], "film1": nb[0] if nb else "", "film2": br[0] if br else "", "why": why})
    out.sort(key=lambda c: (c["views"], c["lid"]))
    return out, fw


def render(c, fw):
    lid, rr, dm = c["lid"], c["rr"], c["dims"]
    e = (rr.get("Potoczne EN") or "").strip()
    nick = e if c["typ"] == "zdrobnienie" else ""
    syn = e if c["typ"] == "synonim" else ""
    feat = U.feature_en(c["key"]) if c["key"] else ""
    name = (c["breed"] + " " + feat).strip()
    desc, ch = en_description(lid, c["breed"], nick, syn, dm)
    title, tidx = pick_title(lid, en()["titles"], name, dm["small"])
    enx = {"title": title, "description": desc, "tags": en_tags(lid), "alts": en_alts(name, dm), "wzorzec_tytulu": tidx, "ABC": {k: v[0] + 1 for k, v in ch.items()},
           "nick": nick, "synonim": syn, "odmiana": c["key"], "slow_w_tytule": words(title)}
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    trans = {code: tr_render(code, lid, rr, ch, tidx, fwd.get(code, ""), dm) for code in LANG_ALL}
    return enx, trans


def check(enx, trans):
    p = []
    if len(enx["title"]) > 140 or enx["slow_w_tytule"] > MAX_WORDS:
        p.append(f"tytuł EN {len(enx['title'])} zn. / {enx['slow_w_tytule']} słów")
    if re.search(r"\bbust\b|cold cast bronze sculpture", enx["title"], re.I):
        p.append("zakazane słowo w tytule")
    if "cold cast bronze" in enx["title"].lower():
        p.append("cold cast bronze w tytule")
    if len(enx["tags"]) != 13 or len(set(enx["tags"])) != 13 or any(len(x) > 20 for x in enx["tags"]):
        p.append("tagi EN")
    if re.search(r"sculpture|statue|bust", " ".join(enx["tags"]), re.I):
        p.append("zakazany tag")
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
    out = ROOT / "plans" / "plakietki_raport.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "wyswietlenia", "rasa", "odmiana", "wymiary_WxHxD", "tytul_nowy", "slow", "film1", "film2", "uwagi"])
        for c in cs:
            why, nt, nw = list(c["why"]), "", ""
            if not [x for x in why if x != "już zoptymalizowana"] and c["rr"]:
                enx, trans = render(c, fw)
                why += check(enx, trans)
                nt, nw = enx["title"], enx["slow_w_tytule"]
            dm = c["dims"]
            w.writerow([c["lid"], c["views"], c["breed"], c["key"], f"{num(dm['w'])}x{num(dm['h'])}x{num(dm['d'])}", nt, nw, c["film1"], c["film2"], "; ".join(why)])
    r = list(csv.DictReader(open(out, encoding="utf-8")))
    print("ofert:", len(r), "| z uwagami:", sum(1 for x in r if x["uwagi"]), "| słów w tytule:", sorted(Counter(x["slow"] for x in r).items()))
    for x in r:
        if x["uwagi"]:
            print(" -", x["listing_id"], x["rasa"], "|", x["uwagi"])


def plan(n, size):
    if glob.glob(str(ROOT / "logs" / f"partia_plakietki_{n:03d}_*.jsonl")):
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
    with open(ROOT / "plans" / f"partia_plakietki_{n:03d}.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "listing_id", "wyswietlenia", "rasa", "odmiana", "ean", "wymiary_WxHxD", "tytul_przed", "tytul_po", "slow", "wzorzec", "ABC", "tagi", "film1", "film2"])
        for i, c in enumerate(batch, 1):
            e, dm = c["en"], c["dims"]
            w.writerow([i, c["lid"], c["views"], c["breed"], c["key"], c["ean"], f"{num(dm['w'])}x{num(dm['h'])}x{num(dm['d'])}", c["st"]["title"], e["title"], e["slow_w_tytule"], e["wzorzec_tytulu"],
                        "".join(f"{k}{v}" for k, v in e["ABC"].items()), "; ".join(e["tags"]), c["film1"], c["film2"]])
    dry = []
    for c in batch:
        u = lambda fn: BASE_V + urllib.parse.quote(c["folder"]) + "/" + urllib.parse.quote(fn)
        dry.append({"listing_id": c["lid"], "rasa": c["breed"], "ean": c["ean"], "dims": c["dims"], "film1": u(c["film1"]), "film1_nazwa": c["film1"], "film2": u(c["film2"]), "film2_nazwa": c["film2"],
                    "images_before": {str(r[0]): r[1] for r in c["st"]["images"]}, "tytul_przed": c["st"]["title"], "en": c["en"], "tlumaczenia": c["trans"]})
    (ROOT / "plans" / f"partia_plakietki_{n:03d}_dryrun.json").write_text(json.dumps(dry, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(batch)} ofert")
    return batch


def steps_for(c):
    en_, tr, lid, dm = c["en"], c["trans"], c["lid"], c["dims"]
    b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
    s = [{"id": "listing", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"title": en_["title"], "description": en_["description"], "tags": ",".join(en_["tags"]), "materials": MATERIALS_TEXT,
                     "item_width": num(dm["w"]), "item_height": num(dm["h"]), "item_length": num(dm["d"]), "item_dimensions_unit": "cm"}},
         {"id": "wlasciwosc_materials", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "kind": "form", "fields": {"value_ids": MAT_VALUES[0], "values": MAT_VALUES[1]}}]
    for k in range(1, 4):
        s.append({"id": f"alt_{k}", "method": "POST", "path": b + "/images", "kind": "alt_existing", "rank": k, "fields": {"alt_text": en_["alts"][k]}})
    s.append({"id": "wideo_1_bez_brand", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film1"], "fields": {"name": c["film1_nazwa"]}})
    s.append({"id": "wideo_2_brand", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film2"], "fields": {"name": c["film2_nazwa"]}})
    for code in LANG_ALL:
        d = tr[code]
        s.append({"id": f"tlumaczenie_{code}", "method": "POST", "path": b + f"/translations/{code}", "kind": "form",
                  "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return s


def load_frozen(n):
    jp = ROOT / "plans" / f"partia_plakietki_{n:03d}_dryrun.json"
    if not jp.exists():
        sys.exit(f"BŁĄD: brak zatwierdzonego planu partii plakietki {n}")
    out = []
    for x in json.load(open(jp, encoding="utf-8")):
        x["en"]["alts"] = {int(k): v for k, v in x["en"]["alts"].items()}
        out.append({"lid": x["listing_id"], "dims": x["dims"], "en": x["en"], "trans": x["tlumaczenia"], "film1": x["film1"], "film1_nazwa": x["film1_nazwa"], "film2": x["film2"],
                    "film2_nazwa": x["film2_nazwa"], "tytul_przed": x["tytul_przed"], "images_before": {int(k): v for k, v in x["images_before"].items()}})
    return out


def preflight(c, live):
    pr = []
    if "error" in live:
        return ["odczyt oferty: " + str(live["error"])[:100]]
    if live["state"] != "active":
        pr.append("status " + live["state"])
    if len(live.get("images", [])) != 3:
        pr.append(f"zdjęć: {len(live.get('images', []))} (oczekiwano 3)")
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
    summary = ROOT / "logs" / f"partia_plakietki_{n:03d}_{time.strftime('%Y-%m-%d')}.jsonl"
    print(f"partia plakietki {n}: {len(batch)} ofert z planu")
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
        dm = c["dims"]
        for attempt in range(4):
            after = api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations")
            props = api.get(f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}/properties")
            imgs = sorted(after.get("images", []), key=lambda x: x["rank"])
            mat = next((pp for pp in props.get("results", []) if pp["property_id"] == B.MATERIAL_PROPERTY), {})
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(imgs), "alt_ok": all(html.unescape(im.get("alt_text") or "") == c["en"]["alts"][im["rank"]] for im in imgs) if len(imgs) == 3 else False,
                   "kolejnosc_ok": [im["listing_image_id"] for im in imgs] == [ids_before[k] for k in (1, 2, 3)] if len(imgs) == 3 else False,
                   "wideo": len(after.get("videos", [])), "tlumaczen": sum(1 for k, v in after["translations"].items() if v and k != "en-US"),
                   "materialy_ok": sorted(after["materials"]) == sorted(MATERIALS_TEXT.split(",")), "materials_prop": sorted(mat.get("values", [])),
                   "wymiary_ok": [after.get("item_width"), after.get("item_height"), after.get("item_length"), after.get("item_dimensions_unit")] == [dm["w"], dm["h"], dm["d"], "cm"], "proba": attempt + 1}
            good = chk["cena_ok"] and chk["stan_ok"] and chk["status_ok"] and chk["zdjec"] == 3 and chk["alt_ok"] and chk["kolejnosc_ok"] and chk["wideo"] == 2 \
                and chk["tlumaczen"] == 8 and chk["materialy_ok"] and chk["materials_prop"] == sorted(MAT_VALUES[1].split(",")) and chk["wymiary_ok"]
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
