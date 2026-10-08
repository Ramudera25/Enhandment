#!/usr/bin/env python3
"""matriks.py — cari konfigurasi dump tercepat + uji metode tangan server u2."""
import json
import time
import urllib.request

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def rpc(method, params):
    req = urllib.request.Request(
        "http://127.0.0.1:9008/jsonrpc/0",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                         "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    t = time.time()
    try:
        with op.open(req, timeout=20) as r:
            out = json.load(r)
        return out, (time.time() - t) * 1000
    except Exception as e:
        return {"error": str(e)}, (time.time() - t) * 1000


for label, params in [("penuh kedalaman50", [False, 50]),
                      ("penuh kedalaman25", [False, 25]),
                      ("kompres kedalaman25", [True, 25]),
                      ("kompres kedalaman15", [True, 15])]:
    out, ms = rpc("dumpWindowHierarchy", params)
    print(f"{label}: {ms:6.0f} ms ({len(out.get('result') or '')} byte)")

for method, params in [("swipe", [540, 1500, 540, 900, 20]),
                       ("longClick", [540, 1500, 500]),
                       ("sendKeys", ["halo"]),
                       ("pressKey", ["back"])]:
    out, ms = rpc(method, params)
    print(f"{method}: {ms:6.0f} ms -> {out.get('result', out.get('error'))}")
