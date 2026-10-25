#!/usr/bin/env python3
"""Thin Etsy API client: Bearer token from .secrets/, auto refresh, every request counted in logs/.
Reads only unless a caller explicitly uses method POST/PUT/PATCH/DELETE (not used by backup scripts).
"""
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ROOT / ".secrets" / "etsy_token.json"
DAILY_STOP = 8000


def _count_today():
    p = ROOT / "logs" / f"api_requests_{datetime.date.today()}.log"
    return sum(1 for _ in open(p)) if p.exists() else 0


def _log(method, path):
    (ROOT / "logs").mkdir(exist_ok=True)
    with open(ROOT / "logs" / f"api_requests_{datetime.date.today()}.log", "a") as fh:
        fh.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {method} {path.split('?')[0]}\n")


def _token():
    t = json.loads(TOKEN.read_text())
    if time.time() > t["obtained_at"] + t["expires_in"] - 120:
        subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "etsy_auth.py"), "refresh"], check=True)
        t = json.loads(TOKEN.read_text())
    return t["access_token"]


def get(path, retries=3):
    if _count_today() >= DAILY_STOP:
        raise RuntimeError("limit dzienny 8000 zapytań osiągnięty, przerywam")
    for i in range(retries):
        _log("GET", path)
        r = subprocess.run(["curl", "-sS", "-m", "60", "https://api.etsy.com" + path,
                            "-H", f"Authorization: Bearer {_token()}"], capture_output=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"error": r.stderr.decode()[:200]}
        if not (isinstance(d, dict) and "error" in d and "rate" in str(d["error"]).lower()):
            return d
        time.sleep(2 * (i + 1))
    return d
