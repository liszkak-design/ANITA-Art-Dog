#!/usr/bin/env python3
"""Thin Etsy API client: Bearer token from .secrets/, auto refresh, every request counted in logs/.
Reads only unless a caller explicitly uses method POST/PUT/PATCH/DELETE (not used by backup scripts).
"""
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ROOT / ".secrets" / "etsy_token.json"
DAILY_STOP = 9000  # 31.10.2026: właścicielka dopuściła podniesienie z 8000 na 9000


def _count_today():
    """Zapytania z ostatnich 24 godzin (okno kroczące: Etsy liczy limit dobowy w oknie kroczącym, a nie od północy; 29.10.2026 stało się to
    przyczyną 'Exceeded daily rate limit' przy 7198 zapytaniach z datą dzisiejszą i ok. 10 700 w ostatnich 24 h)."""
    limit = datetime.datetime.now() - datetime.timedelta(hours=24)
    n = 0
    for d in (datetime.date.today() - datetime.timedelta(days=1), datetime.date.today()):
        p = ROOT / "logs" / f"api_requests_{d}.log"
        if p.exists():
            for line in open(p):
                try:
                    if datetime.datetime.fromisoformat(line.split()[0]) > limit:
                        n += 1
                except ValueError:
                    pass
    return n


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


def api_key_header():
    """x-api-key = keystring:shared_secret when the shared secret is available as ETSY_SHARED_SECRET.
    Without it the network proxy is expected to inject the header (cloud network secret). Never printed or logged."""
    sec = os.environ.get("ETSY_SHARED_SECRET")
    return {"x-api-key": f"{os.environ['ETSY_KEYSTRING']}:{sec}"} if sec else {}


def check_limit():
    """Wspólna kontrola limitu dla WSZYSTKICH wywołań Etsy (odczyty, zapisy, odświeżanie tokenu): stop przy 9000 w oknie 24 h, ostrzeżenie od 8000."""
    n = _count_today()
    if n >= DAILY_STOP:
        raise RuntimeError(f"limit {DAILY_STOP} zapytań w oknie 24 h osiągnięty ({n}), przerywam")
    if n >= 8000:
        print(f"UWAGA: {n} zapytań w ostatnich 24 h (stop przy {DAILY_STOP}, limit Etsy 10 000)", file=sys.stderr)
    return n


def request(method, path, headers=None, data=None, retries=3):
    """Single entry point for Etsy calls: counts the request in logs/, sends Authorization (and x-api-key if
    available) from Python so that nothing secret appears in command-line arguments."""
    check_limit()
    h = {"Authorization": f"Bearer {_token()}", **api_key_header(), **(headers or {})}
    d = {}
    for i in range(retries):
        if i:
            check_limit()  # ponowne próby też liczą się do limitu
        _log(method, path)
        req = urllib.request.Request("https://api.etsy.com" + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
        except urllib.error.HTTPError as e:
            body = e.read()
        except Exception as e:
            body = json.dumps({"error": str(e)[:200]}).encode()
        try:
            d = json.loads(body) if body else {}
        except Exception:
            d = {"error": body[:200].decode("utf-8", "replace")}
        if not (isinstance(d, dict) and "rate" in str(d.get("error", "")).lower()):
            return d
        time.sleep(2 * (i + 1))
    return d


def get(path, retries=3):
    return request("GET", path, retries=retries)
