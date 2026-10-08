#!/usr/bin/env python3
"""benchmark.py — ukur latensi jalur cepat muse-droid di perangkat.

Jalankan DI HP (Termux) atau dari VM dengan MD_SERVER menunjuk forward:
  MD_SERVER=http://127.0.0.1:9008 python3 benchmark.py

Mengukur: dump penuh vs kompres, click koneksi-baru vs keep-alive, dan
siklus penuh dump->click->dump. Target proyek: siklus < 1000 ms.
"""
import json
import os
import time
import urllib.request
import http.client

BASE = os.environ.get("MD_SERVER", "http://127.0.0.1:9008")
HOSTPORT = BASE.replace("http://", "").replace("https://", "")
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def rpc_baru(method, params):
    req = urllib.request.Request(
        BASE + "/jsonrpc/0",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                         "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    t = time.time()
    with _opener.open(req, timeout=20) as r:
        out = json.load(r)
    return out, (time.time() - t) * 1000


def main():
    host, _, port = HOSTPORT.partition(":")
    for label, params in [("dump penuh  ", [False, 50]),
                          ("dump kompres", [True, 50])]:
        for i in range(2):
            out, ms = rpc_baru("dumpWindowHierarchy", params)
            print(f"{label} #{i}: {ms:6.0f} ms  ({len(out.get('result') or '')} byte)")
    out, ms = rpc_baru("click", [540, 1500])
    print(f"click koneksi-baru : {ms:6.0f} ms  -> {out.get('result')}")

    conn = http.client.HTTPConnection(host, int(port or 9008), timeout=20)

    def rpc_hidup(method, params):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                           "params": params})
        t = time.time()
        conn.request("POST", "/jsonrpc/0", body,
                     {"Content-Type": "application/json"})
        resp = conn.getresponse()
        data = resp.read()
        return (time.time() - t) * 1000, len(data)

    for i in range(2):
        ms, n = rpc_hidup("dumpWindowHierarchy", [True, 50])
        print(f"dump kompres keep-alive #{i}: {ms:6.0f} ms  ({n} byte)")
    ms, _ = rpc_hidup("click", [540, 1500])
    print(f"click keep-alive   : {ms:6.0f} ms")
    t = time.time()
    rpc_hidup("dumpWindowHierarchy", [True, 50])
    rpc_hidup("click", [540, 1500])
    rpc_hidup("dumpWindowHierarchy", [True, 50])
    print(f"SIKLUS dump-klik-dump (keep-alive, kompres): {(time.time() - t) * 1000:.0f} ms")


if __name__ == "__main__":
    main()
