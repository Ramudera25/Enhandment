#!/usr/bin/env python3
"""probe-glints.py v2 — ukur navigasi nyata di aplikasi Glints (tanpa melamar).
Penanda feed: teks "Semua Preferensi" hanya ada di header feed."""
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
    return json.load(op.open(req, timeout=8)).get("result")


def dump():
    t = time.time()
    x = rpc("dumpWindowHierarchy", [True, 50]) or ""
    return x, (time.time() - t) * 1000


x, ms = dump()
di_feed = "Semua Preferensi" in x
print("dump feed: %.0f ms (%d byte) penanda feed: %s" % (ms, len(x), di_feed))
if di_feed:
    t = time.time()
    rpc("click", [540, 950])  # badan kartu listing pertama — BUKAN tombol lamar
    print("ketuk kartu: %.0f ms" % ((time.time() - t) * 1000))
    time.sleep(3)
    x, ms = dump()
    masih_feed = "Semua Preferensi" in x
    print("dump sesudah ketuk: %.0f ms (%d byte) masih di feed: %s"
          % (ms, len(x), masih_feed))
    t = time.time()
    rpc("swipe", [540, 1500, 540, 800, 60])
    x, ms = dump()
    print("siklus geser+dump di listing: total %.0f ms (dump %.0f ms, %d byte)"
          % ((time.time() - t) * 1000, ms, len(x)))
rpc("pressKey", ["back"])
print("BACK — selesai, kembali ke feed")
