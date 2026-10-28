#!/usr/bin/env python3
"""Indeks folderów urn na artdog.com.pl (tylko odczyt): VIDEO/IV tura/{091 urna z plytka ceramiczna, 097 Urny kocie, 098 Urny konie}.
Zapisuje plans/urny_foldery_index.csv: korzeń, folder rasy, nazwa rasy z folderu, EAN, pliki wideo (z rozmiarem) i zdjęcia.
Użycie: python3 -I scripts/crawl_urny.py
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
OUT = ROOT / "plans" / "urny_foldery_index.csv"
BASE = "https://www.artdog.com.pl/VIDEO/IV%20tura/"
ROOTS = ["091. urna z plytka ceramiczna", "097. Urny kocie", "098. Urny konie"]


def fetch(url, tries=5, head=False):
    for i in range(tries):  # curl: serwer odrzuca domyślny UA Pythona
        cmd = ["curl", "-sS", "-m", "40", "-f"] + (["-I"] if head else []) + [url]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", "replace")
        time.sleep(1.5 * (i + 1))
    return ""


def kids(url):
    return [urllib.parse.unquote(html.unescape(h)) for h in re.findall(r'href="([^"?]+)"', fetch(url)) if not h.startswith(("/", "http"))]


def size(url):
    m = re.search(r"content-length:\s*(\d+)", fetch(url, head=True), re.I)
    return int(m.group(1)) if m else 0


def process(args):
    root, folder = args
    url = BASE + urllib.parse.quote(root) + "/" + urllib.parse.quote(folder.rstrip("/")) + "/"
    files = kids(url)
    vids = [f for f in files if f.lower().endswith(".mp4")]
    ean = (re.findall(r"(\d{13})", folder) or [""])[0]
    name = re.sub(r"^\d+\.?\s*|\s*\d{13}\s*/?$", "", folder).strip()
    return [root, folder.rstrip("/"), name, ean,
            "|".join(f"{v}:{size(url + urllib.parse.quote(v))}" for v in vids), "|".join(f for f in files if f.lower().endswith(".jpg"))]


def main():
    jobs = []
    for r in ROOTS:
        for f in kids(BASE + urllib.parse.quote(r) + "/"):
            if f.endswith("/") and re.search(r"\d{13}", f):
                jobs.append((r, f))
    print("folderów rasy:", len(jobs))
    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(process, jobs))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["korzen", "folder", "nazwa_z_folderu", "ean", "wideo_rozmiar", "zdjecia"])
        w.writerows(rows)
    print("zapisano", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
