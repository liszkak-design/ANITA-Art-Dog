#!/usr/bin/env python3
"""Index the plaque folders on artdog.com.pl (read only).

Writes plans/folders_index.csv: species folder, breed folder name as on the server, EAN, video files,
photo files found in allegro/zebraneEAN/<EAN>/. Safe to re-run: EANs already in the CSV are skipped.
Usage: python3 -I scripts/crawl_folders.py
"""
import csv
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "plans" / "folders_index.csv"
BASE = "https://www.artdog.com.pl"
VIDEO = BASE + "/VIDEO/VII%20tura/38.%20SUBLIMACJA/6.%20Plyta%20Nagrobna/"
PHOTOS = BASE + "/allegro/zebraneEAN/"
HREF = re.compile(r'href="([^"?]+)"')


def fetch(url, tries=6):
    # curl is used instead of urllib: the server answers 403 to the default Python user agent
    err = ""
    for i in range(tries):
        r = subprocess.run(["curl", "-sS", "-m", "40", "-f", url], capture_output=True)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", "replace")
        err = r.stderr.decode()[:120]
        time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"{url}: {err}")


def children(url):
    html = fetch(url)
    out = []
    for h in HREF.findall(html):
        if h.startswith("/") or h.startswith("http"):
            continue
        out.append(urllib.parse.unquote(h))
    return out


def main():
    OUT.parent.mkdir(exist_ok=True)
    done = set()
    rows = []
    if OUT.exists():
        rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
        done = {r["ean"] for r in rows}
    for sp in children(VIDEO):
        if not sp.endswith("/"):
            continue
        for br in children(VIDEO + urllib.parse.quote(sp)):
            if not br.endswith("/"):
                continue
            m = re.search(r"(\d{13})/?$", br)
            ean = m.group(1) if m else ""
            if ean in done and ean:
                continue
            files = children(VIDEO + urllib.parse.quote(sp) + urllib.parse.quote(br))
            videos = [f for f in files if f.endswith(".mp4")]
            photos = []
            if ean:
                try:
                    photos = [f for f in children(PHOTOS + ean + "/") if f.lower().endswith(".jpg")]
                except Exception as e:
                    photos = [f"ERROR {e}"[:80]]
            rows.append({"species_folder": sp.strip("/"), "breed_folder": br.strip("/"), "ean": ean,
                         "videos": "|".join(videos), "photos": "|".join(sorted(photos))})
            print(sp.strip("/"), "|", br.strip("/"), "|", len(photos), "zdjęć", file=sys.stderr)
            time.sleep(0.15)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["species_folder", "breed_folder", "ean", "videos", "photos"])
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "folderów zapisano do", OUT)


if __name__ == "__main__":
    main()
