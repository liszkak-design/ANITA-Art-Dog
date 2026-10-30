#!/usr/bin/env python3
"""Optymalizacja 38 urn z reliefem ("... Custom urn for dog's ashes", plans/relief_custom_urn_38.csv, stan żywy plans/relief_stan_zywy.json).
  python3 -I scripts/batch_relief.py raport                      # mapowanie oferta -> folder serwera, wariant A/B (plans/relief_mapa.csv), bez zapisu
  python3 -I scripts/batch_relief.py plan N [--lid=ID[,ID]]      # dry-run partii N (plans/partia_relief_00N.csv i _dryrun.json)
  python3 -I scripts/batch_relief.py apply N --apply             # zapis do Etsy (tylko po "tak" właścicielki dla partii N)
Zakres na ofertę: kopia zapasowa; tytuł, opis, 13 tagów, materiały tekstowe (wood, brass handles, cold cast bronze relief), Materials (Brass, Pine, Birch),
personalizacja (A: imię i daty wymagane + cytat opcjonalny; B: imię i daty opcjonalne), alt texty zdjęć 1-6 (zdjęcia NIE są wymieniane),
film 1 = video/video-urn-relief-dogs-anita.mp4, film 2 = z folderu rasy (bez "brand"), 8 tłumaczeń. Limit API: etsy_api liczy okno 24 h dla wszystkich wywołań.
"""
import csv
import datetime
import glob
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import time
import urllib.parse
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import generators as gen
import apply_test_sphynx as base
import batch as B
import batch_urny as U

ROOT = api.ROOT
TPL = ROOT / "templates"
BASE_V = "https://www.artdog.com.pl/VIDEO/V%20tura/109.%20Plakietki%20na%20urnie/"
STAN = ROOT / "plans" / "relief_stan_zywy.json"
INDEX = ROOT / "plans" / "relief_foldery_index.csv"
GROUP = ROOT / "plans" / "relief_custom_urn_38.csv"
MAPA = ROOT / "plans" / "relief_mapa.csv"
CACHE = B.CACHE.parent / "relief"
VIDEO1 = ROOT / "video" / "video-urn-relief-dogs-anita.mp4"
ROTTWEILER_FIX = ROOT / "video" / "poprawki" / "rottweiler-5056739246399.mp4"
MATERIALS_TEXT = "wood,brass handles,cold cast bronze relief"
MAT_VALUES = ("68,203,1059", "Brass,Pine,Birch")  # bez Ceramic (zatwierdzone 30.10.2026)
B_FOLDERS = {18, 21, 23, 24, 28, 29, 38}  # foldery bez tabliczki na zdjęciu 1 (wariant B)
OWNER_EAN = {1380245139: "5056739246375", 1380245821: "5056739246399"}  # poprawki właścicielki 29.10.2026
OWNER_VIDEO2 = {1380245821: ROTTWEILER_FIX}
NAME_FIX = {"Borzoi Russian Wolfhound": "Borzoi", "Mastino Napoletano": "Neapolitan Mastiff", "Staffordshire Bullterrier": "Staffordshire Bull Terrier"}
FEATURE_OFFER = {1380247435: "Dachshund Wire-haired"}  # Dachshund wire: "Wire-haired" w tytule
TOP4 = {1366245946, 1380250289, 1380245821, 1366250756}  # German Shepherd, Dogue de Bordeaux, Rottweiler, Golden Retriever: na końcu
LANG_ALL = U.LANG_ALL
QUOTE = "When I needed a hand, you gave me your paw"
TODAY = datetime.date.today()


def sec(text, head, nxt=None):
    a = text.index(head)
    b = text.index(nxt, a + 1) if nxt and nxt in text[a + 1:] else len(text)
    return text[a:b]


# ---------- szablony EN ----------
_EN = {}


def en():
    if _EN:
        return _EN
    t = (TPL / "relief_propozycja_tekstow.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| \d \| (.*?) \| (.*?) \|$", t, re.M)
    _EN["tA"] = [a for a, b in rows]
    _EN["tB"] = [a if b.startswith("(jak A)") else b for a, b in rows]
    s4 = sec(t, "## 4. Pierwszy akapit", "## 5.")
    def bank(s):
        return [(m.group(2) or "", m.group(3)) for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", s, re.M)]
    iA = s4.index("**A bez NICK/SYN**")
    iB = s4.index("**B (zastosowanie)")
    iCA = s4.index("**C wariant A")
    iCB = s4.index("**C wariant B")
    _EN["A"] = bank(s4[iA:iB])
    _EN["B"] = bank(s4[iB:iCA])
    _EN["CA"] = bank(s4[iCA:iCB])
    _EN["CB"] = bank(s4[iCB:])
    s5 = sec(t, "## 5. Sekcje stałe", "## 6.")
    _EN["fixed"] = re.search(r"```\n(.*?)\n```", s5, re.S).group(1)
    s6 = sec(t, "## 6. Alt texty", "## 7.")
    _EN["alt1"] = {v: re.search(r'^1 \(' + v + r'\): "(.*)"$', s6, re.M).group(1) for v in "AB"}
    s3 = sec(t, "## 3. Tagi", "## 4.")
    fx = re.search(r"\*\*Stałe \(7\):\*\* (.*?)\.\n", s3).group(1)
    _EN["core"] = [re.sub(r" \(\d+\)$", "", x).strip() for x in fx.split("), ")]
    _EN["core"] = [re.sub(r"\s*\(\d+\)?$", "", x).strip() for x in _EN["core"]]
    pl = re.search(r"\*\*Pula[^\n]*?:\*\* (.*)\n", s3).group(1)
    items = re.findall(r"([a-z][a-z ]*[a-z]) \((\d+)(?:, tylko wariant A)?\)", pl)
    _EN["pool"] = [a for a, b in items if a != "urn with quote"]
    _EN["quote"] = "urn with quote"
    assert len(_EN["tA"]) == 6 and len(_EN["core"]) == 7 and len(_EN["pool"]) >= 15, (len(_EN["tA"]), _EN["core"], len(_EN["pool"]))
    return _EN


def fixed_block(text, variant, subs):
    paras = text.split("\n\n")
    out = []
    for p in paras:
        first = p.split("\n")[0]
        m = re.search(r"\s+\[([AB])\]$", first)
        if m:
            if m.group(1) != variant:
                continue
            p = p.replace(first, first[:m.start()], 1)
        lines = []
        for l in p.split("\n"):
            m2 = re.match(r"^- \[([AB])\] (.*)$", l)
            if m2:
                if m2.group(1) != variant:
                    continue
                l = "- " + m2.group(2)
            lines.append(l)
        out.append("\n".join(lines))
    r = "\n\n".join(out)
    for k, v in subs.items():
        r = r.replace(k, v)
    return r


def en_description(lid, breed, nick, syn, variant):
    E = en()
    parts, chosen, nicks = [], {}, 0
    for slot in "ABC":
        if slot == "A":
            want = "N" if nick else ("S" if syn else "")
            opts = [(f, x) for f, x in E["A"] if f == want]
        else:
            src = E["B"] if slot == "B" else E["CA" if variant == "A" else "CB"]
            opts = [(f, x) for f, x in src if f == "" or (f == "N" and nick and nicks < 2)]
        i = U.pick(lid, slot, len(opts))
        chosen[slot] = (i, opts[i][0])
        nicks += opts[i][0] == "N"
        parts.append(opts[i][1].replace("{BREED}", breed).replace("{NICK}", nick).replace("{SYN}", syn))
    d = " ".join(parts) + "\n\n" + fixed_block(E["fixed"], variant, {"{BREED}": breed})
    for name in {n for n in (breed, syn) if n}:
        d = re.sub(r"\b([Aa]) (?=" + re.escape(name) + r")", lambda m, name=name: (B.article(name).capitalize() if m.group(1) == "A" else B.article(name)) + " ", d)
    d = re.sub(r"\b(\w*(?:dog|cat|horse|pony))\s+(?:dog|cat|horse|pony)\b",
               lambda m: m.group(1) if m.group(1).lower().endswith(m.group(0).split()[-1].lower()) else m.group(0), d, flags=re.I)
    assert breed in d
    return d, chosen


def pick_title(lid, pats, name, variant_pats_len=6):
    s = "Dog"
    start = U.pick(lid, "T", len(pats))
    last = ""
    for k in range(len(pats)):
        i = (start + k) % len(pats)
        pat, ss = pats[i], s
        if pat is None:
            continue
        if s.lower() in name.lower() or re.search(r"hound|dog", name, re.I):
            ss = ""
            pat = pat.replace("for Your {S}", "for Your Pet")
        t = re.sub(r"\s+", " ", pat.replace("{BREED}", name).replace("{S}", ss)).replace(" ,", ",")
        last = t
        if len(t) <= 140:
            return t, i + 1
    return last, start + 1


STOP = U.STOP


def en_tags(lid, variant):
    E = en()
    fixed = list(E["core"])
    used = set()
    for t in fixed:
        used |= set(t.split()) - STOP
    pool = E["pool"] + ([E["quote"]] if variant == "A" else [])
    picked = []
    for t in sorted(pool, key=lambda t: hashlib.sha256(f"{lid}:tag:{t}".encode()).hexdigest()):
        w = set(t.split()) - STOP
        if w & used:
            continue
        picked.append(t)
        used |= w
        if len(picked) == 6:
            break
    return fixed + picked


def en_alts(breed_name, variant):
    t = (TPL / "alt_urny_plytka.md").read_text(encoding="utf-8")
    rows = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\| (\d) \| .*? \| (.*?) \|$", t, re.M)}
    a1 = en()["alt1"][variant].replace("{BREED}", breed_name)
    a1 = re.sub(r"\b(a) (?=[AEIOU])", "an ", a1) if False else a1
    m = re.search(r"cold cast bronze relief of (a) (" + re.escape(breed_name) + ")", a1)
    if m:
        a1 = a1.replace(f"relief of a {breed_name}", f"relief of {B.article(breed_name)} {breed_name}")
    return {1: a1, **{k: rows[k] for k in range(2, 7)}}


# ---------- tłumaczenia ----------
_TR = {}


def tr_load(code):
    if code in _TR:
        return _TR[code]
    t = (TPL / f"relief_tlumaczenie_{code}.md").read_text(encoding="utf-8")
    d = {}
    s = sec(t, "## Tytuł", "## Pierwszy akapit")
    a = s.index("A:\n")
    b = s.index("\nB")
    d["tA"] = re.findall(r"^\d\. (\{B\}.*)$", s[a:b], re.M)
    d["tB"] = {int(n): x for n, x in re.findall(r"^(\d)\. (\{B\}.*)$", s[b:], re.M)}
    sb = sec(t, "## Pierwszy akapit", "## Sekcje stałe")
    idx = {k: sb.index(k) for k in ("**A**", "**B**", "**C wariant A", "**C wariant B")}
    cut = lambda lo, hi: sb[idx[lo]:idx[hi] if hi else len(sb)]
    bank = lambda s_: re.findall(r"^- [ABC]\d: (.*)$", s_, re.M)
    d["A"], d["B"] = bank(cut("**A**", "**B**")), bank(cut("**B**", "**C wariant A"))
    d["CA"], d["CB"] = bank(cut("**C wariant A", "**C wariant B")), bank(cut("**C wariant B", None))
    d["fixed"] = re.search(r"```\n(.*?)\n```", t, re.S).group(1)
    tg = sec(t, "## Tagi", "## Pytania") if "## Pytania" in t else sec(t, "## Tagi")
    item = lambda s_: [x.strip() for x, _ in re.findall(r"([^,:*()\n]+?) \((\d+)(?:, tylko A)?\)", s_)]
    if code == "pl":
        st = re.search(r"\*\*Stałe:\*\* (.*)", tg).group(1).split(" (EN:")[0]
        po = re.search(r"\*\*Pula:\*\* (.*)", tg).group(1)
        d["core"] = item(st)
        allp = item(po)
        d["quote"] = [x for x in allp if x == "urna z cytatem"][0]
        d["pool"] = [x for x in allp if x != d["quote"]]
    else:
        d["core"] = item(re.search(r"\*\*Stałe:\*\* (.*)", tg).group(1))
        d["pool"] = item(re.search(r"\*\*Pula:\*\* (.*)", tg).group(1))
        d["quote"] = item(re.search(r"\*\*Tylko wariant A:\*\* (.*)", tg).group(1))[0]
    assert len(d["tA"]) == 6 and len(d["core"]) == 7 and len(d["A"]) == 5 and len(d["CA"]) == 4 and len(d["CB"]) == 4, (code, len(d["tA"]), len(d["core"]), len(d["A"]), len(d["CA"]), len(d["CB"]))
    for x in d["core"] + d["pool"] + [d["quote"]]:
        assert len(x) <= 20, (code, x)
    _TR[code] = d
    return d


def tr_fill(text, code, name):
    f = dict(U.FORMS[code]["pies"])
    for k, v in f.items():
        text = text.replace("{" + k + "}", v)
    return re.sub(r"[ \t]+", " ", text.replace("{B}", name)).strip()


def tr_render(code, lid, rr, ch, tidx, variant, feat=""):
    d = tr_load(code)
    b = rr[U.NAME_COL[code]]
    name = (b + " " + feat).strip() if feat else b
    par = []
    for slot in "ABC":
        bank = d["A"] if slot == "A" else (d["B"] if slot == "B" else d["CA" if variant == "A" else "CB"])
        i, flag = ch[slot]
        i = i if flag == "" and i < len(bank) else U.pick(lid, slot + "t", len(bank))
        par.append(tr_fill(U.tr_sentence(bank[i], "pies"), code, b))
    pats = d["tA"] if variant == "A" else [d["tB"].get(i + 1, d["tA"][i] if i + 1 in (2, 6) else None) for i in range(6)]
    start = tidx - 1
    title = ""
    for k in range(6):
        pat = pats[(start + k) % 6]
        if pat is None:
            continue
        title = tr_fill(pat, code, name)
        if len(title) <= 140:
            break
    fx = fixed_block(d["fixed"], variant, {})
    fx = "\n".join(tr_fill(l, code, b) if l.strip() else "" for l in fx.split("\n"))
    tags = list(d["core"]) + [x for x in sorted(d["pool"] + ([d["quote"]] if variant == "A" else []), key=lambda x: hashlib.sha256(f"{lid}:{code}:{x}".encode()).hexdigest())][:6]
    return {"title": title, "description": " ".join(par) + "\n\n" + fx, "tags": tags}


# ---------- mapowanie oferta -> folder ----------
def bbox_vec(im):
    a = np.asarray(im.convert("L"), dtype=float)
    ys, xs = np.where(a < 235)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    v = np.asarray(im.convert("L").resize((72, 56)), dtype=float).ravel()
    v -= v.mean()
    return v / np.linalg.norm(v)


def curl_to(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        for i in range(4):
            r = subprocess.run(["curl", "-sS", "-f", "-m", "120", "-A", "ArtDog-Etsy-Tool/1.0", "-o", str(path), url], capture_output=True)
            if r.returncode == 0:
                break
            time.sleep(2 * (i + 1))
    return path


def folder_vec(f):
    n = f["folder"].split(".")[0]
    fn = f["zdjecia"].split("|")[0]
    p = curl_to(BASE_V + urllib.parse.quote(f["folder"]) + "/" + urllib.parse.quote(fn), CACHE / "foto1" / f"{n}.jpg")
    im = Image.open(p)
    w, h = im.size
    return bbox_vec(im.crop((int(w * 0.04), int(h * 0.15), int(w * 0.50), int(h * 0.88))))


def mapping():
    stan = json.load(open(STAN, encoding="utf-8"))
    folders = list(csv.DictReader(open(INDEX, encoding="utf-8")))
    fv = [folder_vec(f) for f in folders]
    lids = list(stan)
    ev = {}
    for lid in lids:
        url = stan[lid]["images"][0][2]
        ev[lid] = bbox_vec(Image.open(curl_to(url, CACHE / "live1" / f"{lid}.jpg")))
    S = {(lid, i): float(ev[lid] @ fv[i]) for lid in lids for i in range(len(folders))}
    ean2i = {f["ean"]: i for i, f in enumerate(folders)}
    res, used_f, used_l = {}, set(), set()
    for lid, ean in OWNER_EAN.items():
        i = ean2i[ean]
        res[str(lid)] = (i, S[(str(lid), i)], "właścicielka")
        used_f.add(i)
        used_l.add(str(lid))
    for (lid, i), s in sorted(S.items(), key=lambda kv: -kv[1]):
        if lid in used_l or i in used_f:
            continue
        # tylko foldery o podobnej nazwie rasy do tytułu oferty (unikamy zamiany ras o podobnych zdjęciach)
        res[lid] = (i, s, "zdjęcie")
        used_l.add(lid)
        used_f.add(i)
    return stan, folders, res, S


def breed_name(title):
    return title.split(" Urn for")[0].strip()


def build_candidates():
    stan, folders, res, S = mapping()
    R = B.rasy()
    fw = B.feature_words()
    pm, by_c = U.breed_lookup(R)
    cls = B.e_class()
    sales = {}
    out = []
    for lid, st in stan.items():
        i, sim, how = res[lid]
        f = folders[i]
        fnum = int(f["folder"].split(".")[0])
        name = NAME_FIX.get(breed_name(st["title"]), breed_name(st["title"]))
        row = {"gatunek": "pies", "nazwa_w_tytule": name, "folder": f["folder"]}
        rid, key, why = U.resolve(row, R, fw, pm, by_c)
        if int(lid) in FEATURE_OFFER:
            key = FEATURE_OFFER[int(lid)]
        why = list(why)
        if not rid:
            why.append("rasa nierozpoznana: " + name)
        rr = R[("pies", rid)] if rid else None
        if rr:
            miss = [c for c in [U.NAME_COL[l] for l in LANG_ALL] if not rr.get(c)]
            if miss:
                why.append("brak tłumaczenia nazwy rasy: " + ",".join(miss))
        titles_name = re.sub(r"[^a-z]", "", breed_name(st["title"]).lower())
        film = [x for x in f["wideo_rozmiar"].split("|") if "-brand" not in x.split(":")[0]]
        if len(film) != 1:
            why.append("film rasy bez 'brand': " + str(len(film)))
        fname = re.sub(r"^\d+\.\s*|\s*\d{13}$", "", f["folder"])
        same_name = re.sub(r"[^a-z]", "", fname.lower())[:6] == re.sub(r"[^a-z]", "", breed_name(st["title"]).lower())[:6]
        if sim < 0.9 and not same_name:
            why.append(f"niska zgodność zdjęcia 1 z folderem ({sim:.2f}) i inna nazwa rasy")
        if B.is_done(int(lid)):
            why.append("już zoptymalizowana")
        out.append({"lid": int(lid), "st": st, "folder": f, "fnum": fnum, "sim": sim, "how": how, "variant": "B" if fnum in B_FOLDERS else "A",
                    "rid": rid, "rr": rr, "breed": rr["Nazwa EN (główna)"] if rr else name, "key": key, "typ": cls.get(rid, "") if rid else "", "why": why,
                    "film2": film[0].split(":")[0] if film else ""})
    return out, fw


def render(c, fw):
    lid, rr, variant = c["lid"], c["rr"], c["variant"]
    e = (rr.get("Potoczne EN") or "").strip()
    nick = e if c["typ"] == "zdrobnienie" else ""
    syn = e if c["typ"] == "synonim" else ""
    feat = U.feature_en(c["key"]) if c["key"] else ""
    name = (c["breed"] + " " + feat).strip()
    desc, ch = en_description(lid, c["breed"], nick, syn, variant)
    E = en()
    pats = E["tA"] if variant == "A" else E["tB"]
    title, tidx = pick_title(lid, pats, name)
    enx = {"title": title, "description": desc, "tags": en_tags(lid, variant), "alts": en_alts(name, variant), "wzorzec_tytulu": tidx,
           "ABC": {k: v[0] + 1 for k, v in ch.items()}, "nick": nick, "synonim": syn, "odmiana": c["key"]}
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    trans = {code: tr_render(code, lid, rr, ch, tidx, variant, fwd.get(code, "")) for code in LANG_ALL}
    return enx, trans


def check(enx, trans, variant):
    p = []
    if len(enx["title"]) > 140:
        p.append("tytuł EN za długi")
    if len(enx["tags"]) != 13 or len(set(enx["tags"])) != 13 or any(len(x) > 20 for x in enx["tags"]):
        p.append("tagi EN")
    if "{" in enx["title"] + enx["description"] or "[A]" in enx["description"] or "[B]" in enx["description"]:
        p.append("znacznik w opisie EN")
    for code, d in trans.items():
        if len(d["title"]) > 140:
            p.append(f"tytuł {code} {len(d['title'])} zn.")
        if len(d["tags"]) != 13 or len(set(d["tags"])) != 13 or any(len(x) > 20 for x in d["tags"]):
            p.append(f"tagi {code}")
        if "{" in d["title"] + d["description"] or "[A]" in d["description"] or "[B]" in d["description"]:
            p.append(f"znacznik w {code}")
    return p


def raport():
    cs, fw = build_candidates()
    with open(MAPA, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "tytul_zywy", "rasa_xlsx", "folder", "ean", "zgodnosc", "metoda", "wariant", "odmiana", "film_rasy", "uwagi"])
        for c in cs:
            why = list(c["why"])
            if not why:
                enx, trans = render(c, fw)
                why += check(enx, trans, c["variant"])
            w.writerow([c["lid"], c["st"]["title"][:70], c["breed"], c["folder"]["folder"], c["folder"]["ean"], f"{c['sim']:.3f}", c["how"], c["variant"], c["key"], c["film2"], "; ".join(why)])
    r = list(csv.DictReader(open(MAPA, encoding="utf-8")))
    print("ofert:", len(r), "| z uwagami:", sum(1 for x in r if x["uwagi"]), "| warianty:", Counter(x["wariant"] for x in r))
    for x in r:
        if x["uwagi"]:
            print(" -", x["listing_id"], x["rasa_xlsx"], "|", x["uwagi"])


def plan(n, size):
    if glob.glob(str(ROOT / "logs" / f"partia_relief_{n:03d}_*.jsonl")):
        sys.exit(f"BŁĄD: partia {n} rozpoczęta, nie nadpisuję planu")
    cs, fw = build_candidates()
    only = {int(x) for a in sys.argv if a.startswith("--lid=") for x in a[6:].split(",")}
    batch = []
    for c in cs:
        if only and c["lid"] not in only:
            continue
        if c["why"]:
            print("pomijam", c["lid"], c["breed"], c["why"])
            continue
        enx, trans = render(c, fw)
        prob = check(enx, trans, c["variant"])
        if prob:
            print("pomijam", c["lid"], c["breed"], prob)
            continue
        c.update(en=enx, trans=trans)
        batch.append(c)
        if len(batch) == size:
            break
    views = {r["id"]: int(r["views"]) for r in csv.DictReader(open(GROUP, encoding="utf-8"))}
    batch.sort(key=lambda c: (c["lid"] in TOP4, views.get(str(c["lid"]), 0)))  # najpopularniejsze (top 4) na końcu
    p = ROOT / "plans" / f"partia_relief_{n:03d}.csv"
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "listing_id", "rasa", "wariant", "folder", "ean", "tytul_przed", "tytul_po", "wzorzec", "ABC", "tagi", "film2"])
        for i, c in enumerate(batch, 1):
            e = c["en"]
            w.writerow([i, c["lid"], c["breed"], c["variant"], c["folder"]["folder"], c["folder"]["ean"], c["st"]["title"], e["title"], e["wzorzec_tytulu"],
                        "".join(f"{k}{v}" for k, v in e["ABC"].items()), "; ".join(e["tags"]), c["film2"]])
    dry = []
    for c in batch:
        v2 = str(OWNER_VIDEO2.get(c["lid"], BASE_V + urllib.parse.quote(c["folder"]["folder"]) + "/" + urllib.parse.quote(c["film2"])))
        dry.append({"listing_id": c["lid"], "rasa": c["breed"], "wariant": c["variant"], "ean": c["folder"]["ean"], "film2": v2, "film2_nazwa": Path(v2).name if not v2.startswith("http") else urllib.parse.unquote(v2.rsplit("/", 1)[1]),
                    "images_before": {str(r[0]): r[1] for r in c["st"]["images"]}, "tytul_przed": c["st"]["title"], "en": c["en"], "tlumaczenia": c["trans"]})
    (ROOT / "plans" / f"partia_relief_{n:03d}_dryrun.json").write_text(json.dumps(dry, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(batch)} ofert, warianty {Counter(c['variant'] for c in batch)}, jezyki {sorted({k for c in batch for k in c['trans']})}")
    return batch


# ---------- zapis ----------
def personalization(variant):
    if variant == "A":
        return [{"question_type": "text_input", "question_text": "Name", "required": True, "max_allowed_characters": 50},
                {"question_type": "text_input", "question_text": "Dates", "required": True, "max_allowed_characters": 50},
                {"question_type": "text_input", "question_text": "Quote on the nameplate (optional)", "required": False, "max_allowed_characters": 600,
                 "instructions": "Leave empty for the default quote, or type the exact text you'd like engraved."}]
    return [{"question_type": "text_input", "question_text": "Name", "required": False, "max_allowed_characters": 50,
             "instructions": "Optional: the name for a small engraved nameplate, included in the price."},
            {"question_type": "text_input", "question_text": "Dates", "required": False, "max_allowed_characters": 50,
             "instructions": "Optional: dates in any format for the nameplate."}]


def steps_for(c):
    en_, tr, lid = c["en"], c["trans"], c["lid"]
    b = f"/v3/application/shops/{B.SHOP_ID}/listings/{lid}"
    s = [{"id": "listing", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"title": en_["title"], "description": en_["description"], "tags": ",".join(en_["tags"]), "materials": MATERIALS_TEXT}},
         {"id": "wlasciwosc_materials", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "kind": "form",
          "fields": {"value_ids": MAT_VALUES[0], "values": MAT_VALUES[1]}},
         {"id": "how_its_made", "method": "PATCH", "path": b, "kind": "form", "fields": {"who_made": "collective", "when_made": "made_to_order", "is_supply": "false"}},
         {"id": "personalizacja", "method": "POST", "path": b + "/personalization", "kind": "json", "fields": {"personalization_questions": personalization(c["wariant"])}}]
    for k in range(1, 7):
        s.append({"id": f"alt_{k}", "method": "POST", "path": b + "/images", "kind": "alt_existing", "rank": k, "fields": {"alt_text": en_["alts"][k]}})
    s.append({"id": "wideo_1_relief", "method": "POST", "path": b + "/videos", "kind": "video", "src": str(VIDEO1), "fields": {"name": VIDEO1.name}})
    s.append({"id": "wideo_2_rasa", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film2"], "fields": {"name": c["film2_nazwa"]}})
    for code in LANG_ALL:
        d = tr[code]
        s.append({"id": f"tlumaczenie_{code}", "method": "POST", "path": b + f"/translations/{code}", "kind": "form",
                  "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return s


def load_frozen(n):
    jp = ROOT / "plans" / f"partia_relief_{n:03d}_dryrun.json"
    if not jp.exists():
        sys.exit(f"BŁĄD: brak zatwierdzonego planu partii relief {n}")
    out = []
    for x in json.load(open(jp, encoding="utf-8")):
        x["en"]["alts"] = {int(k): v for k, v in x["en"]["alts"].items()}
        out.append({"lid": x["listing_id"], "wariant": x["wariant"], "ean": x["ean"], "en": x["en"], "trans": x["tlumaczenia"], "film2": x["film2"],
                    "film2_nazwa": x["film2_nazwa"], "gatunek": "pies", "tytul_przed": x["tytul_przed"], "images_before": {int(k): v for k, v in x["images_before"].items()}})
    return out


def preflight(c, live):
    pr = []
    if "error" in live:
        return ["odczyt oferty: " + str(live["error"])[:100]]
    if live["state"] != "active":
        pr.append("status " + live["state"])
    if len(live.get("images", [])) != 6:
        pr.append(f"zdjęć: {len(live.get('images', []))} (oczekiwano 6)")
    if live.get("videos"):
        pr.append("oferta ma już wideo")
    if html.unescape(live["title"]) != c["tytul_przed"]:
        pr.append("tytuł w Etsy inny niż w odczycie planu")
    ids = {im["rank"]: im["listing_image_id"] for im in live.get("images", [])}
    if any(ids.get(k) != v for k, v in c["images_before"].items()):
        pr.append("zdjęcia zmieniły się od odczytu planu")
    return pr


def send(step, c):
    if step["kind"] == "video":
        src = step["src"]
        path = Path(src) if not src.startswith("http") else curl_to(src, CACHE / "wideo" / step["fields"]["name"])
        data, ct = base.multipart({"name": step["fields"]["name"]}, ("video", path.name), path.read_bytes(), "video/mp4")
        return api.request(step["method"], step["path"], headers={"Content-Type": ct}, data=data, retries=1)
    return base.send(step)


def apply_batch(n):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    batch = load_frozen(n)
    if len(batch) > 50:
        sys.exit("BŁĄD: partia większa niż 50")
    if not VIDEO1.exists():
        sys.exit("BŁĄD: brak filmu 1 " + str(VIDEO1))
    for c in batch:
        if c["film2"] and not c["film2"].startswith("http") and not Path(c["film2"]).exists():
            sys.exit("BŁĄD: brak pliku " + c["film2"])
    summary = ROOT / "logs" / f"partia_relief_{n:03d}_{TODAY}.jsonl"
    print(f"partia relief {n}: {len(batch)} ofert z planu")
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
        ids_before = {k: v for k, v in c["images_before"].items()}
        for s in steps_for(c):
            if s["id"] in done:
                continue
            if resumed and s["kind"] == "video":
                vids = api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos", [])
                if len(vids) >= (1 if s["id"] == "wideo_1_relief" else 2):
                    U.zlog(lid, s["id"], "backup/" + p.name, "już w ofercie (wykryte przy wznowieniu)", "ok")
                    continue
            resp = U.alt_existing(s, c, ids_before) if s["kind"] == "alt_existing" else send(s, c)
            if s["kind"] == "video" and not base.ok(resp) and re.search(r"reset|timed out|timeout|disconnect|closed", str(resp), re.I):
                time.sleep(5)
                vids = api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos", [])
                if len(vids) >= (1 if s["id"] == "wideo_1_relief" else 2):
                    resp = {"ok": "film już w ofercie po błędzie sieciowym"}
            if s["id"].startswith("tlumaczenie_") and not base.ok(resp) and "exist" in str(resp).lower():
                resp = send({**s, "method": "PUT"}, c)
            st = "ok" if base.ok(resp) else "błąd"
            U.zlog(lid, s["id"], "backup/" + p.name, {k: (v if len(str(v)) < 200 else str(v)[:200] + "...") for k, v in s["fields"].items()}, st)
            if st != "ok":
                open(summary, "a").write(json.dumps({"listing_id": lid, "status": "błąd", "krok": s["id"], "odpowiedź": str(resp)[:300]}, ensure_ascii=False) + "\n")
                sys.exit(f"{lid}: BŁĄD w kroku {s['id']}: {str(resp)[:300]}\nPrzerywam partię; po wyjaśnieniu uruchom ponownie (wykonane kroki zostaną pominięte).")
            time.sleep(0.15)
        want_q = 3 if c["wariant"] == "A" else 2
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
                   "materialy_ok": sorted(after["materials"]) == sorted(MATERIALS_TEXT.split(",")), "materials_prop": sorted(mat.get("values", [])), "proba": attempt + 1}
            good = chk["cena_ok"] and chk["stan_ok"] and chk["status_ok"] and chk["zdjec"] == 6 and chk["alt_ok"] and chk["kolejnosc_ok"] and chk["wideo"] == 2 \
                and chk["pytan"] == want_q and chk["tlumaczen"] == 8 and chk["who_made"] == "collective" and chk["materialy_ok"] and chk["materials_prop"] == sorted(MAT_VALUES[1].split(","))
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
