#!/usr/bin/env python3
"""Partie optymalizacji urn z płytką ceramiczną "with a Photo" (ok. 299 ofert z plans/urny_mapa_koncowa.csv).
  python3 -I scripts/batch_urny.py plan N [--size=K]    # dry-run partii N (domyślnie max 50): plans/partia_urny_00N.csv i _dryrun.json
  python3 -I scripts/batch_urny.py apply N --apply      # zapis do Etsy; tylko po wyraźnym "tak" dla partii N, token z listings_w
  python3 -I scripts/batch_urny.py raport               # tylko raport: kto się kwalifikuje, kto wymaga decyzji (plans/urny_raport.csv)
Domyślnie dry-run. Teksty z zatwierdzonych szablonów: templates/urny_propozycja_tekstow.md (pies), urny_koty_konie.md,
urny_tlumaczenie_<jezyk>.md, alt_urny_plytka.md. Każda oferta jest zapisywana raz (wpis "weryfikacja" ok w logs/zapis_<id>_*.jsonl).
Kroki oferty: tytuł/opis/tagi, właściwość Materials, how it's made, personalizacja (5 pytań), zdjęcie 1 z serwera (nadpisanie slotu 1),
alt texty zdjęć 2-6 (przez listing_image_id), zdjęcie 7 (original), film gatunku (pies/kot/koń), film rasy, 8 tłumaczeń.
Pominięte (ręcznie w Etsy): SKU, GPSR, shopping basket summary. Pola personalizacji nie są tłumaczone.
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
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api
import generators as gen
import apply_test_sphynx as base
import batch as B

ROOT = api.ROOT
TPL = ROOT / "templates"
SHOP_ID = B.SHOP_ID
TODAY = datetime.date.today()
BATCH_MAX = 50
UA = B.UA
MAP_CSV = ROOT / "plans" / "urny_mapa_koncowa.csv"
INDEX_CSV = ROOT / "plans" / "urny_foldery_index.csv"
REPORT_CSV = ROOT / "plans" / "urny_raport.csv"
VIEWS_CSV = ROOT / "plans" / "urny_wyswietlenia.csv"  # cache: liczba wyświetleń ofert (sprzedaż urn w eksporcie = 0), kolejność partii: najmniej popularne najpierw
EAN_BASE = B.EAN_BASE
VIDEO_BASE = "https://www.artdog.com.pl/VIDEO/IV%20tura/"
SPECIES_VIDEO = {"pies": ROOT / "video" / "video-urn-dogs-anita.mp4", "kot": ROOT / "video" / "video-urn-cats-anita.mp4",
                 "koń": ROOT / "video" / "video-urn-horses-anita.mp4", "kucyk": ROOT / "video" / "video-urn-horses-anita.mp4"}  # film 1: wg gatunku (28.10.2026)
ORIGINALS = {"pies": "original_pies.jpg", "kot": "original_kot.jpg", "koń": "original_kon.jpg", "kucyk": "original_kon.jpg"}
CACHE = B.CACHE.parent / "urny"
LANG_ALL = ["pl", "de", "nl", "fr", "it", "pt", "es", "sv"]
MATERIAL_VALUES = ("83,68,203,1059", "Ceramic,Brass,Pine,Birch")  # jak w ofercie 660269548
HORSE_QUOTE = "If love could have saved you, you would have lived forever."
PAW_QUOTE = "You left paw prints on my heart"
SP_EN = B.SP_EN
STOP = {"pet", "for", "in", "on", "my", "of", "a", "urn", "with", "the"}
FIXED_EN = ["pet urn for ashes", "personalized urn", "wooden urn", "urn with photo", "pet loss gift"]
FORMS = {  # formy gatunku w tłumaczeniach (jak w szablonach)
    "pl": {"kot": dict(gen="kota", loc="kocie"), "pies": dict(gen="psa", loc="psie"), "koń": dict(gen="konia", loc="koniu"), "kucyk": dict(gen="kucyka", loc="kucyku")},
    "de": {"kot": dict(S="Katze", CS="Katzen", ACC="Ihre Katze", DAT="Ihrer Katze", GEN="Ihrer Katze"),
           "pies": dict(S="Hund", CS="Hunde", ACC="Ihren Hund", DAT="Ihrem Hund", GEN="Ihres Hundes"),
           "koń": dict(S="Pferd", CS="Pferde", ACC="Ihr Pferd", DAT="Ihrem Pferd", GEN="Ihres Pferdes"),
           "kucyk": dict(S="Pony", CS="Pony", ACC="Ihr Pony", DAT="Ihrem Pony", GEN="Ihres Ponys")},
    "nl": {"kot": dict(S="kat", CS="katten"), "pies": dict(S="hond", CS="honden"), "koń": dict(S="paard", CS="paarden"), "kucyk": dict(S="pony", CS="pony")},
    "fr": {"kot": dict(S="chat"), "pies": dict(S="chien"), "koń": dict(S="cheval"), "kucyk": dict(S="poney")},
    "es": {"kot": dict(S="gato"), "pies": dict(S="perro"), "koń": dict(S="caballo"), "kucyk": dict(S="pony")},
    "sv": {"kot": dict(S="katt"), "pies": dict(S="hund"), "koń": dict(S="häst"), "kucyk": dict(S="ponny")},
    "it": {sp: dict(S=n, P="il suo " + n, DEL="del suo " + n, AL="al suo " + n) for sp, n in (("kot", "gatto"), ("pies", "cane"), ("koń", "cavallo"), ("kucyk", "pony"))},
    "pt": {sp: dict(S=n, P="o seu " + n, DO="do seu " + n, AO="ao seu " + n) for sp, n in (("kot", "gato"), ("pies", "cão"), ("koń", "cavalo"), ("kucyk", "pónei"))},
}
PAW = {  # "w kształcie łapy" -> podkowy (konie i kucyki), dla każdego języka
    "pl": [("łapy", "podkowy")],
    "de": [("Pfotenförmige", "Hufeisenförmige"), ("pfotenförmige", "hufeisenförmige")],
    "nl": [("Pootvormige", "Hoefijzervormige"), ("pootvormige", "hoefijzervormige")],
    "fr": [("en forme de patte", "en forme de fer à cheval")],
    "it": [("a forma di zampa", "a forma di ferro di cavallo")],
    "pt": [("em forma de pata", "em forma de ferradura")],
    "es": [("en forma de huella", "en forma de herradura")],
    "sv": [("Tassformad", "Hästskoformad"), ("tassformade", "hästskoformade"), ("tassformad", "hästskoformad")],
}
# rozstrzygnięcia właścicielki (28.10.2026): oferta -> ID rasy w Rasy.xlsx; długość sierści jak przy płytkach (słowa z arkusza "Słowa stałe")
OWNER_RID = {660268116: "R027", 660320524: "R048", 660383022: "R333", 674161421: "R035"}
HOLD = {660384830: "tytuł Sloughi, a folder serwera to 182. Saluki (dopasowanie po zdjęciu, brak folderu Sloughi): wymaga decyzji właścicielki"}
GENERIC_FEATURE = {"long": "Dachshund Long-haired", "short": "Chihuahua Short-haired"}
NAME_COL = dict(nl="NL nazwa", fr="FR nazwa", de="DE nazwa", it="IT nazwa", pl="PL nazwa", pt="PT nazwa", es="ES nazwa", sv="SV nazwa")
FEATURE_EN = {"cropped ears": "Cropped Ears", "uncropped (natural) ears": "Natural Ears", "foal": "Foal"}
SPECIES_TAG_ORDER = ["pies", "kot", "koń", "kucyk"]


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip()


def pick(lid, slot, n):
    return gen.pick(lid, slot, n)


# ---------- szablony EN ----------
_EN = {}


def en_templates():
    if _EN:
        return _EN
    P = (TPL / "urny_propozycja_tekstow.md").read_text(encoding="utf-8")
    K = (TPL / "urny_koty_konie.md").read_text(encoding="utf-8")

    def banks(text):
        out = {"A": [], "B": [], "C": []}
        for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", text, re.M):
            out[m.group(1)].append((m.group(2) or "", m.group(3)))
        return out

    kot_i = K.index("## KOT")
    kon_i = K.index("## KOŃ")
    fixed_i = K.index("## Sekcje stałe: kot")
    _EN["titles"] = re.findall(r"^\d\. (\{BREED\}.*)$", base.section(P, "2. Tytuły"), re.M)
    _EN["pool"] = re.findall(r"([a-z][a-z ]*[a-z]) \(\d+\)", base.section(P, "3. Tagi").split("**Pula (25):**", 1)[1].split("\n\n", 1)[0])
    _EN["banks"] = {"pies": banks(base.section(P, "4. Pierwszy akapit")), "kot": banks(K[kot_i:kon_i]), "koń": banks(K[kon_i:fixed_i])}
    _EN["fixed"] = {"pies": base.codeblock(base.section(P, "5. Sekcje stałe")), "kot": base.codeblock(K[fixed_i:])}
    assert len(_EN["titles"]) == 6 and len(_EN["pool"]) == 25, (len(_EN["titles"]), len(_EN["pool"]))
    return _EN


def en_horse_fixed(pony):
    t = en_templates()["fixed"]["kot"]
    word = "pony" if pony else "horse"
    t = re.sub(r"\bcat\b", word, t)
    t = t.replace("Paw-shaped plaque", "Horseshoe-shaped plaque").replace("the paw-shaped plaque carries", "the horseshoe-shaped plaque carries")
    return t.replace(f'"{PAW_QUOTE}"', f'"{HORSE_QUOTE}"')


def en_bank(species):
    sp = "koń" if species == "kucyk" else species
    b = en_templates()["banks"][sp]
    if species == "kucyk":
        b = {k: [(f, re.sub(r"\bhorse\b", "pony", t)) for f, t in v] for k, v in b.items()}
    return b


def en_fixed(species, breed):
    t = en_horse_fixed(species == "kucyk") if species in ("koń", "kucyk") else en_templates()["fixed"][species]
    return t.replace("{BREED}", breed)


def en_description(lid, species, breed, nick, syn):
    b = en_bank(species)
    parts, chosen, nicks = [], {}, 0
    for slot in "ABC":
        if slot == "A":
            want = "N" if nick else ("S" if syn else "")
            opts = [(f, t) for f, t in b["A"] if f == want]
        else:
            opts = [(f, t) for f, t in b[slot] if f == "" or (f == "N" and nick and nicks < 2)]
        i = pick(lid, slot, len(opts))
        chosen[slot] = (i, opts[i][0])
        nicks += opts[i][0] == "N"
        parts.append(opts[i][1].replace("{BREED}", breed).replace("{NICK}", nick).replace("{SYN}", syn))
    d = " ".join(parts) + "\n\n" + en_fixed(species, breed)
    for name in {n for n in (breed, syn) if n}:
        d = re.sub(r"\b([Aa]) (?=" + re.escape(name) + r")", lambda m, name=name: (B.article(name).capitalize() if m.group(1) == "A" else B.article(name)) + " ", d)
    d = re.sub(r"\b(\w*(?:dog|cat|horse|pony))\s+(?:dog|cat|horse|pony)\b",
               lambda m: m.group(1) if m.group(1).lower().endswith(m.group(0).split()[-1].lower()) else m.group(0), d, flags=re.I)
    assert breed in d
    return d, chosen


def en_title(lid, species, name):
    pats = en_templates()["titles"]
    s = gen.SPECIES_WORD[species]
    start = pick(lid, "T", len(pats))
    last = ""
    for k in range(6):
        i = (start + k) % 6
        pat, ss = pats[i], s
        if s.lower() in name.lower():
            ss = ""
            pat = pat.replace("for Your {S}", "for Your Pet")
        t = re.sub(r"\s+", " ", pat.replace("{BREED}", name).replace("{S}", ss)).replace(" ,", ",")
        last = t
        if len(t) <= 140:
            return t, i + 1
    return last, start + 1  # za długi: check() zgłosi


def en_tags(lid, species):
    s = gen.SPECIES_WORD[species].lower()
    fixed = FIXED_EN + [f"{s} ashes urn", f"{s} memorial"]
    used = set()
    for t in fixed:
        used |= set(t.split()) - STOP
    picked = []
    for t in sorted(en_templates()["pool"], key=lambda t: hashlib.sha256(f"{lid}:tag:{t}".encode()).hexdigest()):
        w = set(t.split()) - STOP
        if w & used:
            continue
        picked.append(t)
        used |= w
        if len(picked) == 6:
            break
    return fixed + picked


def article_species(breed, species):
    sp = SP_EN[species]
    return breed if sp in breed.lower() else f"{breed} {sp}"


def en_alts(breed_name, species, lid=0):
    t = (TPL / "alt_urny_plytka.md").read_text(encoding="utf-8")
    rows = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\| (\d) \| .*? \| (.*?) \|$", t, re.M)}
    x = article_species(breed_name, species)
    a1 = rows[1].replace("a portrait of a {BREED} {SPECIES}", f"a portrait of {B.article(x)} {x}")
    if species in ("koń", "kucyk"):
        a1 = a1.replace("a paw-shaped plaque with a quote (horses: a horseshoe-shaped plaque with a quote)", "a horseshoe-shaped plaque with a quote")
    else:
        a1 = a1.replace(" (horses: a horseshoe-shaped plaque with a quote)", "")
    assert "{" not in a1 and "horses:" not in a1, a1
    out = {1: a1, **{k: rows[k] for k in range(2, 7)}}
    key = {"pies": "Pies", "kot": "Kot", "koń": "Koń", "kucyk": "Koń"}[species]
    m = re.search(r'^- ' + key + r': "(.*)"$', t, re.M)
    out[7] = m.group(1)
    return out


# ---------- tłumaczenia z szablonów ----------
_TR = {}


def load_lang(code):
    if code in _TR:
        return _TR[code]
    p = TPL / f"urny_tlumaczenie_{code}.md"
    if not p.exists():
        _TR[code] = None
        return None
    t = p.read_text(encoding="utf-8")
    d = {"titles": re.findall(r"^\d\. (\{B\}.*)$", base.section(t, "Tytuł"), re.M)}
    banks = base.section(t, "Pierwszy akapit: banki")
    d["A"], d["B"], d["C"] = ([x for x in re.findall(r"^- " + s + r"\d: (.*)$", banks, re.M)] for s in "ABC")
    d["fixed"] = base.codeblock(base.section(t, "Sekcje stałe"))
    tg = base.section(t, "Tagi")
    if code == "pl":
        stal, pula = tg.split("**Pula**")
        d["core"] = [m for m in re.findall(r"→ ([^/\n]+?) \(\d+\)$", stal, re.M)][:5]
        d["spec"] = {}
        for key, order in (("ashes urn", 0), ("memorial", 1)):
            line = re.search(r"^- \{s\} " + key + r" → (.+)$", stal, re.M).group(1)
            d.setdefault("spec_raw", {})[key] = [re.sub(r"\s*\(\d+\)$", "", x).strip() for x in line.split(" / ")]
        for i, sp in enumerate(SPECIES_TAG_ORDER):
            d["spec"][sp] = (d["spec_raw"]["ashes urn"][i], d["spec_raw"]["memorial"][i])
        d["pool"] = re.findall(r"→ (.+?) \(\d+\)$", pula, re.M)
    else:
        item = lambda s: [re.sub(r"\s*\(\d+\)$", "", x).strip() for x in re.split(r", ", s.strip())]
        d["core"] = item(re.search(r"\*\*Stałe:\*\* (.+)", tg).group(1))
        d["spec"] = {}
        for sp, v in re.findall(r"(pies|kot|koń|kucyk): ([^;\n]+)", re.search(r"\*\*Gatunkowe:\*\* (.+)", tg).group(1)):
            a, b = item(v)
            d["spec"][sp] = (a, b)
        d["pool"] = item(re.search(r"\*\*Pula:\*\* (.+)", tg).group(1))
    assert len(d["titles"]) == 6 and len(d["core"]) == 5 and len(d["spec"]) == 4, (code, len(d["titles"]), len(d["core"]), len(d["spec"]))
    for x in d["core"] + d["pool"] + [y for v in d["spec"].values() for y in v]:
        assert len(x) <= 20, (code, x)
    _TR[code] = d
    return d


HORSE_ALT = re.compile(r'\s*\(([^()":]+): "(.*)"\)\s*$')


def tr_fill(text, code, species, breed):
    f = dict(FORMS[code][species])
    for k, v in f.items():
        text = text.replace("{" + k + "}", v)
    return re.sub(r"[ \t]+", " ", text.replace("{B}", breed)).strip()


def tr_sentence(text, species):
    m = HORSE_ALT.search(text)
    if not m:
        return text
    return m.group(2) if species in ("koń", "kucyk") else text[:m.start()]


def tr_fixed(code, species, breed, d):
    t = "\n".join(re.sub(r'\s*\(koń: [^)]*\)\s*$', "", l) for l in d["fixed"].splitlines())
    if species in ("koń", "kucyk"):
        for a, b in PAW[code]:
            t = t.replace(a, b)
        t = t.replace(f'"{PAW_QUOTE}"', f'"{HORSE_QUOTE}"')
    return "\n".join(tr_fill(l, code, species, breed) if l.strip() else "" for l in t.splitlines())


def tr_render(code, lid, species, row, ch, tidx, feat=""):
    d = load_lang(code)
    if d is None:
        return None
    b = row[NAME_COL[code]]
    name = (b + " " + feat).strip() if feat else b
    par = []
    for slot in "ABC":
        n = len(d[slot])
        i, flag = ch[slot]
        i = i if flag == "" and i < n else pick(lid, slot + "t", n)
        par.append(tr_fill(tr_sentence(d[slot][i], species), code, species, b))
    title = ""
    for k in range(6):
        title = tr_fill(d["titles"][(tidx - 1 + k) % 6], code, species, name)
        if len(title) <= 140:
            break
    tags = list(d["core"]) + list(d["spec"][species])
    tags += [x for x in sorted(d["pool"], key=lambda x: hashlib.sha256(f"{lid}:{code}:{x}".encode()).hexdigest()) if x not in tags][:6]
    return {"title": title, "description": " ".join(par) + "\n\n" + tr_fixed(code, species, b, d), "tags": tags}


# ---------- dane, rasa, odmiana ----------
def breed_lookup(R):
    m = list(csv.DictReader(open(ROOT / "plans" / "mapa_koncowa.csv", encoding="utf-8")))
    pm = {(r["gatunek"], norm(r["nazwa_w_tytule"])): r["rasa_id"] for r in m}
    by_c = {(k[0], norm(v["Nazwa EN (główna)"])): k[1] for k, v in R.items()}
    return pm, by_c


FEAT_PATTERNS = [(r"\bun-?cropped\b", "uncropped (natural) ears"), (r"\bcropped\b", "cropped ears"), (r"\bfohlen\b", "foal"),
                 (r"\blong[- ]?haired\b|\blonghaired\b", "long"), (r"\bshort[- ]?haired\b|\bshorthaired\b", "short")]


def resolve(row, R, fw, pm, by_c):
    """Zwraca (rasa_id, klucz_odmiany, powody). Odmiana tylko, gdy w arkuszu 'Słowa stałe' jest jej słowo (inaczej oferta czeka na decyzję)."""
    why, g = [], row["gatunek"]
    folder = re.sub(r"^\d+\.?\s*|\s*\d{13}\s*$", "", row["folder"])
    rid = key = None
    for name in (row["nazwa_w_tytule"], folder):
        base_name, feat = name, ""
        for pat, k in FEAT_PATTERNS:
            if re.search(pat, base_name, re.I):
                feat = k
                base_name = re.sub(pat, "", base_name, flags=re.I).strip()
        n = norm(base_name)
        rid = by_c.get((g, n)) or pm.get((g, n)) or by_c.get((g, norm(re.sub(r"\b(cat|horse)$", "", base_name.strip(), flags=re.I)))) or pm.get((g, norm(name)))
        if rid:
            key = feat
            break
    if not rid:
        return None, "", ["rasa nierozpoznana: " + row["nazwa_w_tytule"]]
    rr = R[(g, rid)]
    if key in ("long", "short"):
        cand = [k for k in fw if k.lower().startswith(rr["Nazwa EN (główna)"].lower()) and ("long" if key == "long" else "short") in k.lower()]
        key = cand[0] if cand else GENERIC_FEATURE[key]  # jak przy płytkach: Selkirk Rex, Kurilian Bobtail
    return rid, key or "", why


def feature_en(key):
    return FEATURE_EN.get(key) or key.split()[-1]


def index_rows():
    return {r["ean"]: r for r in csv.DictReader(open(INDEX_CSV, encoding="utf-8"))}


def fetch_ids_csv():
    return {r["listing_id"]: r for r in csv.DictReader(open(B.IDS_CSV, encoding="utf-8"))}


def candidates():
    R = B.rasy()
    fw = B.feature_words()
    pm, by_c = breed_lookup(R)
    idx, ids, sold = index_rows(), fetch_ids_csv(), B.sales()
    views = {int(r["listing_id"]): int(r["wyswietlenia"]) for r in csv.DictReader(open(VIEWS_CSV, encoding="utf-8"))} if VIEWS_CSV.exists() else {}
    nick_cls = B.e_class()
    out = []
    for row in csv.DictReader(open(MAP_CSV, encoding="utf-8")):
        lid = int(row["listing_id"])
        why = []
        if row["metoda"].startswith("POMINIĘTA"):
            continue
        if str(lid) not in ids:
            why.append("oferta nie jest aktywna / brak w plans/listing_ids_sklep.csv (uruchom batch.py ids)")
        if B.is_done(lid):
            why.append("już zoptymalizowana")
        if lid in HOLD:
            why.append("wstrzymana: " + HOLD[lid])
        rid, key, w2 = resolve(row, R, fw, pm, by_c)
        if lid in OWNER_RID:
            rid, w2 = OWNER_RID[lid], []
        why += w2
        if rid:
            rr = R[(row["gatunek"], rid)]
            breed = rr["Nazwa EN (główna)"]
            sp = "kucyk" if row["gatunek"] == "koń" and "pony" in breed.lower() else row["gatunek"]
            if breed in B.EXCLUDE_BREEDS and lid not in OWNER_RID:
                why.append("Pointer: sprawdza właścicielka")
            miss = [c for c in [NAME_COL[l] for l in LANG_ALL] if not rr.get(c)]
            if miss:
                why.append("brak tłumaczenia nazwy rasy: " + ",".join(miss))
            if key and key not in fw:
                why.append(f"brak słów odmiany '{key}'")
        else:
            rr, breed, sp = None, "", row["gatunek"]
        if not row["film_bez_brand"]:
            why.append("brak filmu rasy (bez 'brand')")
        if row["ean"] not in idx:
            why.append("EAN bez folderu w indeksie")
        out.append({"row": row, "lid": lid, "rr": rr, "rid": rid, "breed": breed, "species": sp, "key": key, "why": why,
                    "sales": sold.get(lid, 0), "views": views.get(lid), "rank": (sold.get(lid, 0), views.get(lid, 0)), "typ": nick_cls.get(rid, "") if rid else ""})
    return out, fw


def render(c, fw):
    lid, sp, breed, rr = c["lid"], c["species"], c["breed"], c["rr"]
    e = (rr.get("Potoczne EN") or "").strip()
    nick = e if c["typ"] == "zdrobnienie" else ""
    syn = e if c["typ"] == "synonim" else ""
    if sp != "pies":
        nick = syn = ""  # koty i konie: bez NICK/SYN (jak w płytkach)
    feat = feature_en(c["key"]) if c["key"] else ""
    name = (breed + " " + feat).strip()
    desc, ch = en_description(lid, sp, breed, nick, syn)
    title, tidx = en_title(lid, sp, name)
    en = {"title": title, "description": desc, "tags": en_tags(lid, sp), "alts": en_alts(name, sp), "wzorzec_tytulu": tidx,
          "ABC": {k: v[0] + 1 for k, v in ch.items()}, "nick": nick, "synonim": syn, "odmiana": c["key"]}
    fwd = fw.get(c["key"], {}) if c["key"] else {}
    trans = {}
    for code in LANG_ALL:
        r = tr_render(code, lid, sp, rr, ch, tidx, fwd.get(code, ""))
        if r:
            trans[code] = r
    return en, trans


def check(en, trans):
    p = []
    if len(en["title"]) > 140:
        p.append(f"tytuł EN {len(en['title'])} zn.")
    if len(en["tags"]) != 13 or len(set(en["tags"])) != 13 or any(len(x) > 20 for x in en["tags"]):
        p.append("tagi EN")
    if "{" in en["title"] + en["description"]:
        p.append("nierozwiązany znacznik EN")
    for c, d in trans.items():
        if len(d["title"]) > 140:
            p.append(f"tytuł {c} {len(d['title'])} zn.")
        if len(d["tags"]) != 13 or len(set(d["tags"])) != 13 or any(len(x) > 20 for x in d["tags"]):
            p.append(f"tagi {c}")
        if "{" in d["title"] + d["description"]:
            p.append(f"nierozwiązany znacznik {c}")
    return p


def head(url):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers=UA), timeout=30) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            time.sleep(2 * (a + 1))
    return 0


def video_url(c, idx):
    r = idx[c["row"]["ean"]]
    return VIDEO_BASE + urllib.parse.quote(r["korzen"]) + "/" + urllib.parse.quote(r["folder"]) + "/" + urllib.parse.quote(c["row"]["film_bez_brand"])


def interleave(cs):
    out, i = [], 0
    while i < len(cs):
        j = i
        while j < len(cs) and cs[j]["rank"] == cs[i]["rank"]:
            j += 1
        g = {s: [c for c in cs[i:j] if c["species"] == s] for s in ("pies", "kot", "koń", "kucyk")}
        while any(g.values()):
            for s in g:
                if g[s]:
                    out.append(g[s].pop(0))
        i = j
    return out


def started(n):
    return bool(glob.glob(str(ROOT / "logs" / f"partia_urny_{n:03d}_*.jsonl")))


def raport():
    cs, fw = candidates()
    with open(REPORT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "gatunek", "nazwa_w_tytule", "rasa_xlsx", "ean", "sprzedaz", "status", "powody"])
        for c in cs:
            en = trans = None
            why = list(c["why"])
            if not why:
                en, trans = render(c, fw)
                why += check(en, trans)
            w.writerow([c["lid"], c["row"]["gatunek"], c["row"]["nazwa_w_tytule"], c["breed"], c["row"]["ean"], c["sales"], "kandydat" if not why else "wymaga decyzji", "; ".join(why)])
    st = Counter()
    for r in csv.DictReader(open(REPORT_CSV, encoding="utf-8")):
        st[r["status"]] += 1
        for x in r["powody"].split("; "):
            if x:
                st["powód: " + x.split(":")[0]] += 1
    print(dict(st))
    miss = [l for l in LANG_ALL if load_lang(l) is None]
    print("brak szablonów tłumaczeń:", miss or "żadnych", "| filmy gatunków:", {k: v.exists() for k, v in SPECIES_VIDEO.items()})


def fetch_views():
    """Odczyt liczby wyświetleń każdej oferty urn (tylko odczyt, ok. 300 zapytań) -> plans/urny_wyswietlenia.csv."""
    cs, _ = candidates()
    with open(VIEWS_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["listing_id", "wyswietlenia", "ulubione"])
        for c in cs:
            l = api.get(f"/v3/application/listings/{c['lid']}")
            w.writerow([c["lid"], l.get("views", 0), l.get("num_favorers", 0)])
    print("zapisano", VIEWS_CSV.relative_to(ROOT))


def plan(n, size):
    if started(n):
        sys.exit(f"BŁĄD: partia {n} jest już rozpoczęta, nie nadpisuję planu")
    cs, fw = candidates()
    idx = index_rows()
    only = {int(x) for a in sys.argv if a.startswith("--lid=") for x in a[6:].split(",")}  # np. pilot na wskazanej ofercie
    free = interleave(sorted([c for c in cs if not c["why"] and (not only or c["lid"] in only)], key=lambda c: (c["rank"], c["lid"])))
    batch, skipped = [], []
    for c in free:
        if len(batch) == size:
            break
        en, trans = render(c, fw)
        prob = check(en, trans)
        if not prob:
            for f in ("1.jpg",):
                if head(f"{EAN_BASE}{c['row']['ean']}/{f}") != 200:
                    prob.append("zdjęcie 1 niedostępne na serwerze")
            if head(video_url(c, idx)) != 200:
                prob.append("film rasy niedostępny na serwerze")
        if prob:
            c["why"] = prob
            skipped.append(c)
            continue
        c.update(en=en, trans=trans, video=video_url(c, idx))
        batch.append(c)
    p = ROOT / "plans" / f"partia_urny_{n:03d}.csv"
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lp", "listing_id", "gatunek", "rasa", "ean", "sprzedaz_szt", "wyswietlenia", "tytul_po", "wzorzec_tytulu", "ABC", "zdrobnienie", "synonim", "odmiana", "tagi", "film"])
        for i, c in enumerate(batch, 1):
            e = c["en"]
            w.writerow([i, c["lid"], c["species"], c["breed"], c["row"]["ean"], c["sales"], c["views"], e["title"], e["wzorzec_tytulu"],
                        "".join(f"{k}{v}" for k, v in e["ABC"].items()), e["nick"], e["synonim"], e["odmiana"], "; ".join(e["tags"]), c["row"]["film_bez_brand"]])
    dry = [{"listing_id": c["lid"], "ean": c["row"]["ean"], "gatunek": c["species"], "rasa": c["breed"], "film_url": c["video"], "film1": SPECIES_VIDEO[c["species"]].name, "en": c["en"], "tlumaczenia": c["trans"]} for c in batch]
    (ROOT / "plans" / f"partia_urny_{n:03d}_dryrun.json").write_text(json.dumps(dry, ensure_ascii=False, indent=1))
    print(f"partia {n}: {len(batch)} ofert; wykluczonych w tym kroku {len(skipped)}; języki w tłumaczeniach: {sorted({k for c in batch for k in c['trans']})}")
    print("gatunki:", dict(Counter(c["species"] for c in batch)), "sprzedaż (szt.): min", min(c["sales"] for c in batch), "max", max(c["sales"] for c in batch))
    return batch


# ---------- zapis ----------
def personalization(species):
    shape = "horseshoe-shaped" if species in ("koń", "kucyk") else "paw-shaped"
    return [
        {"question_type": "text_input", "question_text": "Name", "required": True, "max_allowed_characters": 50},
        {"question_type": "text_input", "question_text": "Dates", "required": True, "max_allowed_characters": 50},
        {"question_type": "text_input", "question_text": "Quote on the plaque (optional)", "required": False, "max_allowed_characters": 600,
         "instructions": f"Leave empty for the default quote, or type the exact text you'd like engraved on the {shape} plaque."},
        {"question_type": "unlabeled_upload", "question_text": "Pet photo", "required": False, "max_allowed_files": 1,
         "instructions": "Please upload a high-resolution image. The better the photo quality, the better the print will look on the plaque."},
        {"question_type": "dropdown", "question_text": "How should we print the photo?", "required": False,
         "options": [{"label": "Color + background"}, {"label": "Color, no background"}, {"label": "Pencil sketch"}]},
    ]


def steps_for(c):
    en, trans, lid = c["en"], c["trans"], c["lid"]
    b = f"/v3/application/shops/{SHOP_ID}/listings/{lid}"
    s = [{"id": "listing", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"title": en["title"], "description": en["description"], "tags": ",".join(en["tags"])}},
         {"id": "wlasciwosc_materials", "method": "PUT", "path": f"{b}/properties/{B.MATERIAL_PROPERTY}", "kind": "form",
          "fields": {"value_ids": MATERIAL_VALUES[0], "values": MATERIAL_VALUES[1]}},
         {"id": "how_its_made", "method": "PATCH", "path": b, "kind": "form",
          "fields": {"who_made": "collective", "when_made": "made_to_order", "is_supply": "false"}},
         {"id": "personalizacja", "method": "POST", "path": b + "/personalization", "kind": "json",
          "fields": {"personalization_questions": personalization(c["gatunek"])}},
         {"id": "zdjecie_1_serwer", "method": "POST", "path": b + "/images", "kind": "image", "rank": 1, "src": "server",
          "fields": {"rank": "1", "overwrite": "true", "alt_text": en["alts"][1]}}]
    for k in range(2, 7):
        s.append({"id": f"alt_{k}", "method": "POST", "path": b + "/images", "kind": "alt_existing", "rank": k, "fields": {"alt_text": en["alts"][k]}})
    s.append({"id": "zdjecie_7_original", "method": "POST", "path": b + "/images", "kind": "image", "rank": 7, "src": "original",
              "fields": {"rank": "7", "overwrite": "false", "alt_text": en["alts"][7]}})
    s.append({"id": "wideo_1_gatunek", "method": "POST", "path": b + "/videos", "kind": "video", "src": str(SPECIES_VIDEO[c["gatunek"]]),
              "fields": {"name": SPECIES_VIDEO[c["gatunek"]].name}})
    s.append({"id": "wideo_2_rasa", "method": "POST", "path": b + "/videos", "kind": "video", "src": c["film_url"], "fields": {"name": c["film_name"]}})
    for code in LANG_ALL:
        d = trans[code]
        s.append({"id": f"tlumaczenie_{code}", "method": "POST", "path": b + f"/translations/{code}", "kind": "form",
                  "fields": {"title": d["title"], "description": d["description"], "tags": ",".join(d["tags"])}})
    return s


def load_frozen(n):
    jp = ROOT / "plans" / f"partia_urny_{n:03d}_dryrun.json"
    if not jp.exists():
        sys.exit(f"BŁĄD: brak zatwierdzonego planu partii urn {n} (uruchom 'plan {n}' i zatwierdź)")
    out = []
    for x in json.load(open(jp, encoding="utf-8")):
        alts = {int(k): v for k, v in x["en"]["alts"].items()}
        x["en"]["alts"] = alts
        out.append({"lid": x["listing_id"], "gatunek": x["gatunek"], "ean": x["ean"], "en": x["en"], "trans": x["tlumaczenia"],
                    "film_url": x["film_url"], "film_name": urllib.parse.unquote(x["film_url"].rsplit("/", 1)[1])})
    return out


def download(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            path.write_bytes(r.read())
    return path


def send(step, c):
    k, lid = step["kind"], c["lid"]
    if k == "image":
        path = download(f"{EAN_BASE}{c['ean']}/1.jpg", CACHE / c["ean"] / "1.jpg") if step["src"] == "server" else ROOT / "media" / "urny_with_photo" / ORIGINALS[c["gatunek"]]
        data, ct = base.multipart(step["fields"], ("image", path.name), path.read_bytes(), "image/jpeg")
        return api.request(step["method"], step["path"], headers={"Content-Type": ct}, data=data, retries=1)
    if k == "video":
        path = Path(step["src"]) if not step["src"].startswith("http") else download(step["src"], CACHE / "wideo" / c["film_name"])
        data, ct = base.multipart(step["fields"], ("video", path.name), path.read_bytes(), "video/mp4")
        return api.request(step["method"], step["path"], headers={"Content-Type": ct}, data=data, retries=1)
    return base.send(step)


def live_images(lid):
    return api.get(f"/v3/application/listings/{lid}?includes=Images").get("images", [])


def alt_existing(step, c, ids_before):
    """Alt text do istniejącego zdjęcia (listing_image_id + rank + overwrite=true): obraz zostaje ten sam, zmienia się tylko alt."""
    lid, k = c["lid"], step["rank"]
    img = next((i for i in live_images(lid) if i["rank"] == k), None)
    if not img:
        return {"error": f"brak zdjęcia o randze {k}"}
    if (img.get("alt_text") or "") == step["fields"]["alt_text"]:
        return {"ok": "alt już ustawiony"}
    if ids_before.get(k) and ids_before[k] != img["listing_image_id"]:
        return {"error": f"zdjęcie {k} zmieniło id przed zapisem alt"}
    f = {"listing_image_id": str(img["listing_image_id"]), "rank": str(k), "overwrite": "true", "alt_text": step["fields"]["alt_text"]}
    data = "&".join(f"{a}={urllib.parse.quote(b)}" for a, b in f.items()).encode()
    return api.request("POST", step["path"], headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data, retries=1)


def preflight(c, live, ids):
    pr = []
    if "error" in live:
        return ["odczyt oferty: " + str(live["error"])[:100]]
    if live["state"] != "active":
        pr.append("status " + live["state"])
    if len(live.get("images", [])) != 6:
        pr.append(f"zdjęć: {len(live.get('images', []))} (oczekiwano 6)")
    if live.get("videos"):
        pr.append("oferta ma już wideo")
    if html.unescape(live["title"]) != html.unescape(ids.get(str(c["lid"]), {}).get("title", live["title"])):
        pr.append("tytuł w Etsy inny niż w liście ofert (oferta zmieniona od ostatniego 'ids')")
    return pr


def zlog(lid, step_id, before, after, status):
    B.zlog(lid, step_id, before, after, status)


def apply_batch(n):
    tok = json.loads(api.TOKEN.read_text())
    if "listings_w" not in tok.get("scope", ""):
        sys.exit("BŁĄD: token bez listings_w")
    batch = load_frozen(n)
    if len(batch) > BATCH_MAX:
        sys.exit("BŁĄD: partia większa niż 50")
    for sp in {c["gatunek"] for c in batch}:
        if not SPECIES_VIDEO[sp].exists():
            sys.exit(f"BŁĄD: brak filmu dla gatunku {sp} ({SPECIES_VIDEO[sp].relative_to(ROOT)}); film jest pierwszy w ofercie, nie zaczynam bez niego")
    miss = [l for l in LANG_ALL if any(l not in c["trans"] for c in batch)]
    if miss:
        sys.exit("BŁĄD: brak tłumaczeń w planie: " + ",".join(miss))
    ids = fetch_ids_csv()
    summary = ROOT / "logs" / f"partia_urny_{n:03d}_{TODAY}.jsonl"
    skip = {int(x) for a in sys.argv if a.startswith("--skip=") for x in a[7:].split(",")}
    print(f"partia urn {n}: {len(batch)} ofert z zatwierdzonego planu")
    for i, c in enumerate(batch, 1):
        lid = c["lid"]
        if lid in skip:
            print(i, lid, "POMINIĘTA na żądanie (--skip)")
            continue
        if B.is_done(lid):
            print(i, lid, "pomijam (już zrobiona)")
            continue
        p, live = B.backup_unique(lid)
        pr = preflight(c, live, ids)
        done = B.done_steps(lid)
        if pr and not (done - {"weryfikacja"}):
            print(i, lid, "ZATRZYMANA przed zapisem:", "; ".join(pr))
            open(summary, "a").write(json.dumps({"listing_id": lid, "status": "pominięta", "powod": pr}, ensure_ascii=False) + "\n")
            continue
        resumed = bool(done - {"weryfikacja"})
        ids_before = {im["rank"]: im["listing_image_id"] for im in live.get("images", [])}
        for s in steps_for(c):
            if s["id"] in done:
                continue
            if resumed and s["kind"] == "image":
                imgs = live_images(lid)
                if any(im["rank"] == s["rank"] and (im.get("alt_text") or "") == s["fields"]["alt_text"] for im in imgs):
                    zlog(lid, s["id"], "backup/" + p.name, "już w ofercie (wykryte przy wznowieniu)", "ok")
                    continue
            if resumed and s["kind"] == "video" and api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos"):
                vids = api.get(f"/v3/application/listings/{lid}?includes=Videos").get("videos", [])
                if len(vids) >= (1 if s["id"] == "wideo_1_gatunek" else 2):
                    zlog(lid, s["id"], "backup/" + p.name, "już w ofercie (wykryte przy wznowieniu)", "ok")
                    continue
            resp = alt_existing(s, c, ids_before) if s["kind"] == "alt_existing" else send(s, c)
            if s["kind"] in ("image", "video") and not base.ok(resp) and re.search(r"reset|timed out|timeout|disconnect|closed", str(resp), re.I):
                time.sleep(5)
                imgs = live_images(lid)
                if s["kind"] == "image" and any(im["rank"] == s["rank"] and (im.get("alt_text") or "") == s["fields"]["alt_text"] for im in imgs):
                    resp = {"ok": "zdjęcie już w ofercie po błędzie sieciowym"}
                elif s["kind"] == "image":
                    resp = send(s, c)
            if s["id"].startswith("tlumaczenie_") and not base.ok(resp) and "exist" in str(resp).lower():
                resp = send({**s, "method": "PUT"}, c)
            st = "ok" if base.ok(resp) else "błąd"
            zlog(lid, s["id"], "backup/" + p.name, {k: (v if len(str(v)) < 200 else str(v)[:200] + "...") for k, v in s["fields"].items()}, st)
            if st != "ok":
                open(summary, "a").write(json.dumps({"listing_id": lid, "status": "błąd", "krok": s["id"], "odpowiedź": str(resp)[:300]}, ensure_ascii=False) + "\n")
                sys.exit(f"{lid}: BŁĄD w kroku {s['id']}: {str(resp)[:300]}\nPrzerywam całą partię; po wyjaśnieniu uruchom ponownie (wykonane kroki zostaną pominięte).")
            time.sleep(0.15)
        for attempt in range(4):
            after = api.get(f"/v3/application/listings/{lid}?includes=Images,Videos,Translations,Personalization")
            props = api.get(f"/v3/application/shops/{SHOP_ID}/listings/{lid}/properties")
            imgs = sorted(after.get("images", []), key=lambda x: x["rank"])
            mat = next((pp for pp in props.get("results", []) if pp["property_id"] == B.MATERIAL_PROPERTY), {})
            chk = {"cena_ok": after["price"] == live["price"], "stan_ok": after["quantity"] == live["quantity"], "status_ok": after["state"] == live["state"],
                   "zdjec": len(imgs), "alt_ok": all((im.get("alt_text") or "") == c["en"]["alts"][im["rank"]] for im in imgs) if len(imgs) == 7 else False,
                   "kolejnosc_ok": [im["listing_image_id"] for im in imgs[1:6]] == [ids_before[k] for k in range(2, 7)] if len(imgs) == 7 else False,
                   "wideo": len(after.get("videos", [])), "pytan": len(after["personalization"]["personalization_questions"]),
                   "tlumaczen": sum(1 for k, v in after["translations"].items() if v and k != "en-US"), "who_made": after["who_made"],
                   "materials_prop": sorted(mat.get("values", [])), "proba": attempt + 1}
            good = chk["cena_ok"] and chk["stan_ok"] and chk["status_ok"] and chk["zdjec"] == 7 and chk["alt_ok"] and chk["kolejnosc_ok"] and chk["wideo"] == 2 \
                and chk["pytan"] == 5 and chk["tlumaczen"] == 8 and chk["who_made"] == "collective" and chk["materials_prop"] == sorted(MATERIAL_VALUES[1].split(","))
            if good:
                break
            time.sleep(3)
        zlog(lid, "weryfikacja", {"cena": live["price"], "stan": live["quantity"]}, chk, "ok" if good else "niezgodność")
        open(summary, "a").write(json.dumps({"listing_id": lid, "status": "ok" if good else "niezgodność", **chk}, ensure_ascii=False) + "\n")
        print(i, lid, "ok" if good else "NIEZGODNOŚĆ " + str(chk))
        if not good:
            sys.exit("Weryfikacja niezgodna, przerywam partię.")
    print("Partia zakończona. Proszę sprawdzić próbkę w Etsy przed następną partią.")


def main():
    cmd = sys.argv[1]
    if cmd == "raport":
        raport()
    elif cmd == "wyswietlenia":
        fetch_views()
    elif cmd == "plan":
        size = next((int(a[7:]) for a in sys.argv if a.startswith("--size=")), BATCH_MAX)
        plan(int(sys.argv[2]), min(size, BATCH_MAX))
    elif cmd == "apply":
        if "--apply" not in sys.argv:
            sys.exit("Brak flagi --apply: nic nie zapisuję. Użyj 'plan N' do dry-run.")
        apply_batch(int(sys.argv[2]))


if __name__ == "__main__":
    main()
