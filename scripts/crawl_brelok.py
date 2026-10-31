#!/usr/bin/env python3
"""Indeks folderów urn z małą posrebrzaną płaskorzeźbą: VIDEO/IV tura/089. Urny z brelokiem duze (tylko odczyt, curl bo serwer odrzuca UA Pythona).
Zapisuje plans/brelok_foldery_index.csv: folder, nazwa, rozmiar (mały/średni/duży z nazwy), ean, pliki wideo (z rozmiarem), zdjęcia.
"""
import csv
import html
import re
import subprocess
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.artdog.com.pl/VIDEO/IV%20tura/089.%20Urny%20z%20brelokiem%20duze/"
OUT = ROOT / "plans" / "brelok_foldery_index.csv"


def fetch(url, head=False, tries=5):
    for i in range(tries):
        r = subprocess.run(["curl", "-sS", "-m", "40", "-f", "-A", "ArtDog-Etsy-Tool/1.0"] + (["-I"] if head else []) + [url], capture_output=True)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", "replace")
        time.sleep(1.5 * (i + 1))
    return ""


def kids(url):
    return [urllib.parse.unquote(html.unescape(h)) for h in re.findall(r'href="([^"?]+)"', fetch(url)) if not h.startswith(("/", "http"))]


def size(url):
    m = re.search(r"content-length:\s*(\d+)", fetch(url, head=True), re.I)
    return int(m.group(1)) if m else 0


def process(folder):
    url = BASE + urllib.parse.quote(folder.rstrip("/")) + "/"
    files = kids(url)
    vids = [f for f in files if f.lower().endswith(".mp4")]
    ean = (re.findall(r"(\d{13})", folder) or [""])[0]
    name = re.sub(r"^\d+\.?\s*|\s*\d{13}\s*/?$", "", folder).strip()
    sz = re.search(r"\((mał[ay]|średni|duż[ay])\)", name)
    return [folder.rstrip("/"), name, sz.group(1) if sz else "", ean, "|".join(f"{v}:{size(url + urllib.parse.quote(v))}" for v in vids),
            "|".join(f for f in files if f.lower().endswith(".jpg"))]


def main():
    folders = [f for f in kids(BASE) if f.endswith("/") and re.search(r"\d{13}", f)]
    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(process, folders))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["folder", "nazwa", "rozmiar", "ean", "wideo_rozmiar", "zdjecia"])
        w.writerows(rows)
    print("folderów:", len(rows), "->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
