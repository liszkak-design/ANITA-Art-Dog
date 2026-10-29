#!/usr/bin/env python3
"""Stan licznika zapytań Etsy w oknie kroczącym 24 h (bez wywołań API): python3 -I scripts/api_licznik.py"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import etsy_api as api

n = api._count_today()
print(f"zapytań w ostatnich 24 h: {n} (stop skryptów: {api.DAILY_STOP}, limit Etsy: 10000); wolnych do stopu: {max(0, api.DAILY_STOP - n)}")
if n >= api.DAILY_STOP:
    now = datetime.datetime.now()
    ts = []
    for d in (datetime.date.today() - datetime.timedelta(days=1), datetime.date.today()):
        p = api.ROOT / "logs" / f"api_requests_{d}.log"
        if p.exists():
            for line in open(p):
                try:
                    t = datetime.datetime.fromisoformat(line.split()[0])
                    if t > now - datetime.timedelta(hours=24):
                        ts.append(t)
                except ValueError:
                    pass
    ts.sort()
    need = n - api.DAILY_STOP + 200  # zapas 200 zapytań
    if need < len(ts):
        print("limit zejdzie poniżej stopu (z zapasem 200) ok.", (ts[need] + datetime.timedelta(hours=24)).isoformat(timespec="minutes"), "(czas z logów)")
