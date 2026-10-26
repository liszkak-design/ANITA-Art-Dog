#!/usr/bin/env python3
"""Etsy OAuth helper. Tokens live only in .secrets/ (git-ignored) and are never printed.
  python3 -I scripts/etsy_auth.py exchange '<full redirect URL pasted by the owner>'
  python3 -I scripts/etsy_auth.py refresh
The x-api-key header is added by the network proxy.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / ".secrets"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"


def post(data):
    sec = os.environ.get("ETSY_SHARED_SECRET")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if sec:  # local / environment-variable mode; in the cloud proxy mode the proxy adds x-api-key
        headers["x-api-key"] = f"{os.environ['ETSY_KEYSTRING']}:{sec}"
    req = urllib.request.Request(TOKEN_URL, data=urllib.parse.urlencode(data).encode(), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


def save(tok, scope):
    tok["obtained_at"] = int(time.time())
    tok["scope"] = scope
    p = SEC / "etsy_token.json"
    p.write_text(json.dumps(tok))
    os.chmod(p, 0o600)
    print("token zapisany w .secrets/etsy_token.json; ważny", tok.get("expires_in"), "s; zakres:", scope)


def main():
    cmd = sys.argv[1]
    cid = os.environ["ETSY_KEYSTRING"]
    if cmd == "exchange":
        pend = json.loads((SEC / "oauth_pending.json").read_text())
        q = urllib.parse.parse_qs(urllib.parse.urlparse(sys.argv[2]).query)
        if q.get("state", [""])[0] != pend["state"]:
            sys.exit("BŁĄD: state z adresu nie zgadza się z zapisanym, przerywam")
        tok = post({"grant_type": "authorization_code", "client_id": cid, "redirect_uri": pend["redirect_uri"],
                    "code": q["code"][0], "code_verifier": pend["verifier"]})
        if "access_token" not in tok:
            sys.exit("BŁĄD wymiany kodu: " + str({k: v for k, v in tok.items() if k in ("error", "error_description")}))
        save(tok, pend["scope"])
        (SEC / "oauth_pending.json").unlink()
    elif cmd == "refresh":
        old = json.loads((SEC / "etsy_token.json").read_text())
        tok = post({"grant_type": "refresh_token", "client_id": cid, "refresh_token": old["refresh_token"]})
        if "access_token" not in tok:
            sys.exit("BŁĄD odświeżania: " + str({k: v for k, v in tok.items() if k in ("error", "error_description")}))
        save(tok, old.get("scope", ""))


if __name__ == "__main__":
    main()
