#!/usr/bin/env python3
"""server-hp.py — klien tipis ke server UiAutomator residen di HP (Jalan 1).

Status: PROTOTIPE (folder advance/) — ditulis mengikuti antarmuka JSON-RPC
uiautomator2 (port 9008, /jsonrpc/0); belum diuji ke server sungguhan.

Pakai:
  server-hp.py ping                 -> cek server hidup
  server-hp.py dump                 -> XML layar saat ini
  server-hp.py ketuk <x> <y>        -> klik koordinat
  server-hp.py tunggu "<teks>" [s]  -> tunggu teks tampil (jajak lokal via server)

Alamat server: MD_SERVER (bawaan http://127.0.0.1:9008) — arahkan lewat
SSH port-forward / Tailscale sesuai topologi (lihat docs/01-arsitektur.md).
"""
import json
import os
import sys
import time
import urllib.request

BASE = os.environ.get("MD_SERVER", "http://127.0.0.1:9008")
_id = 0


def rpc(method: str, params: list):
    global _id
    _id += 1
    data = json.dumps({"jsonrpc": "2.0", "id": _id, "method": method, "params": params}).encode()
    req = urllib.request.Request(BASE + "/jsonrpc/0", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        jawab = json.loads(r.read())
    if "error" in jawab:
        raise RuntimeError(jawab["error"])
    return jawab.get("result")


def dump() -> str:
    return rpc("dumpWindowHierarchy", [False])


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    if a[0] == "ping":
        print(rpc("deviceInfo", []))
    elif a[0] == "dump":
        print(dump())
    elif a[0] == "ketuk":
        print(rpc("click", [int(a[1]), int(a[2])]))
    elif a[0] == "tunggu":
        teks, batas = a[1], int(a[2]) if len(a) > 2 else 30
        t0 = time.time()
        while time.time() - t0 < batas:
            if teks in dump():
                print(f"tampil setelah ±{time.time()-t0:.1f} dtk")
                break
            time.sleep(0.3)   # server residen: jajak boleh rapat, ongkosnya kecil
        else:
            print(f"timeout {batas} dtk", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"perintah tidak dikenal: {a[0]}", file=sys.stderr)
        sys.exit(2)
