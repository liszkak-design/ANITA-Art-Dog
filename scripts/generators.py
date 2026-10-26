#!/usr/bin/env python3
"""Deterministic generators for the ceramic plaque 'with a Photo' offers: title, description, tags.
Everything is built from the approved templates in templates/ (single source of truth); the choice of variants
is seeded by the Etsy listing ID so it is repeatable and can be logged.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates"
SPECIES_FILE = {"kot": "opis_plytka_kot.md", "pies": "opis_plytka_pies.md", "koń": "opis_plytka_kon.md"}
SPECIES_WORD = {"kot": "Cat", "pies": "Dog", "koń": "Horse"}
STOP = {"pet", "for", "in", "on", "my", "of", "a"}


def pick(listing_id, slot, n):
    return int(hashlib.sha256(f"{listing_id}:{slot}".encode()).hexdigest(), 16) % n


def banks(species):
    text = (TPL / SPECIES_FILE[species]).read_text(encoding="utf-8")
    text = text.split("## 1a.")[0] if species == "koń" else text  # pony variants are separate
    out = {"A": [], "B": [], "C": []}
    for m in re.finditer(r"^- ([ABC])\d+(?: \[([NS])\])?: (.*)$", text, re.M):
        out[m.group(1)].append((m.group(2) or "", m.group(3)))  # flaga: "" zwykły, "N" zdrobnienie, "S" synonim
    return out


def fixed_sections(species):
    text = (TPL / SPECIES_FILE[species]).read_text(encoding="utf-8")
    block = text.split("## 2.", 1)[1]
    return re.search(r"```\n(.*?)\n```", block, re.S).group(1)


def description(listing_id, species, breed, nick="", syn=""):
    b = banks(species)
    parts, chosen, nicks = [], {}, 0
    for slot in "ABC":
        # zdrobnienie [N]: także w A, max 2 w akapicie; synonim [S]: tylko w A, a gdy rasa ma synonim, zdanie A zawsze go zawiera
        opts = [(f, t) for f, t in b[slot]
                if (f == "" and not (slot == "A" and syn)) or (f == "N" and nick and nicks < 2)
                or (f == "S" and syn and slot == "A")]
        i = pick(listing_id, slot, len(opts))
        chosen[slot] = i
        nicks += opts[i][0] == "N"
        parts.append(opts[i][1].replace("{BREED}", breed).replace("{NICK}", nick).replace("{SYN}", syn))
    return " ".join(parts) + "\n\n" + fixed_sections(species).replace("{BREED}", breed), chosen


def title(listing_id, species, breed, feature=""):
    text = (TPL / "tytuly_tagi_plytka.md").read_text(encoding="utf-8")
    pats = re.findall(r"^\d\. (\{B\}.*)$", text, re.M)
    i = pick(listing_id, "T", len(pats))
    s = SPECIES_WORD[species]
    if s.lower() in breed.lower():
        s = ""
    name = (breed + " " + feature).strip()
    t = re.sub(r"\s+", " ", pats[i].replace("{B}", name).replace("{S}", s)).replace(" ,", ",")
    return t, i + 1


def tags(listing_id, species):
    text = (TPL / "tytuly_tagi_plytka.md").read_text(encoding="utf-8")
    core = re.findall(r"^- ([a-z ]+) \(\d+\)$", text.split("**Stałe", 1)[1].split("**Pula", 1)[0], re.M)
    pool = re.findall(r"^- ([a-z ]+) \(\d+\)$", text.split("**Pula", 1)[1], re.M)
    s = SPECIES_WORD[species].lower()
    fixed = core + [f"{s} memorial", f"{s} grave marker"]
    order = sorted(pool, key=lambda t: hashlib.sha256(f"{listing_id}:tag:{t}".encode()).hexdigest())
    picked, used = [], set()
    for t in order:
        words = set(t.split()) - STOP
        if words & used:
            continue
        picked.append(t)
        used |= words
        if len(picked) == 6:
            break
    allt = fixed + picked
    assert len(allt) == 13 and all(len(t) <= 20 for t in allt), allt
    return allt
