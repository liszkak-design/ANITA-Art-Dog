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
from concurrent.futures import ThreadPoolExecutor
from html import unescape as html_unescape
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
        out.append(urllib.parse.unquote(html_unescape(h)))
    return out


def process(sp, br):
    m = re.search(r"(\d{13})/?$", br)
    ean = m.group(1) if m else ""
    row = {"species_folder": sp.strip("/"), "breed_folder": br.strip("/"), "ean": ean, "videos": "", "photos": ""}
    try:
        files = children(VIDEO + urllib.parse.quote(sp) + urllib.parse.quote(br))
        row["videos"] = "|".join(f for f in files if f.endswith(".mp4"))
        if ean:
            row["photos"] = "|".join(sorted(f for f in children(PHOTOS + ean + "/") if f.lower().endswith(".jpg")))
    except Exception as e:
        row["photos"] = ("ERROR " + str(e))[-100:]
    return row


def main():
    OUT.parent.mkdir(exist_ok=True)
    FIELDS = ["species_folder", "breed_folder", "ean", "videos", "photos"]
    done = set()
    if OUT.exists():
        done = {(r["species_folder"], r["breed_folder"]) for r in csv.DictReader(open(OUT, encoding="utf-8"))
                if not r["photos"].startswith("ERROR")}
        kept = [r for r in csv.DictReader(open(OUT, encoding="utf-8")) if not r["photos"].startswith("ERROR")]
    else:
        kept = []
    jobs = []
    for sp in children(VIDEO):
        if sp.endswith("/"):
            for br in children(VIDEO + urllib.parse.quote(sp)):
                if br.endswith("/") and (sp.strip("/"), br.strip("/")) not in done:
                    jobs.append((sp, br))
    print(len(jobs), "folderów do przejrzenia", file=sys.stderr)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(kept)
        fh.flush()
        with ThreadPoolExecutor(max_workers=3) as ex:
            for row in ex.map(lambda j: process(*j), jobs):
                w.writerow(row)
                fh.flush()
                print(row["species_folder"], "|", row["breed_folder"], "|", row["photos"].count("jpg"), "zdjęć", file=sys.stderr)
    print("zapisano", OUT)


if __name__ == "__main__":
    main()
