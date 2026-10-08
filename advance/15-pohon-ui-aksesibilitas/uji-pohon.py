#!/usr/bin/env python3
# uji-pohon.py — klien uji server pohon UI pendamping (127.0.0.1:19102).
# Jalan DI HP (Termux). Mengukur: latensi PING, isi POHON, akurasi CARI
# terhadap dump uiautomator2 (kebenaran dasar), dan umur salinan.
#
# Pakai: python3 uji-pohon.py [teks-yang-dicari]
# Tanpa argumen: hanya ukur latensi + struktur. Dengan argumen teks:
# bandingkan bounds CARI (pohon) vs node berteks sama di dump u2.
import json
import re
import socket
import statistics
import sys
import time
import urllib.request

POHON = ("127.0.0.1", 19102)
U2 = "http://127.0.0.1:9008/jsonrpc/0"


def tanya(baris):
    t0 = time.perf_counter()
    with socket.create_connection(POHON, timeout=5) as s:
        s.sendall((baris + "\n").encode("utf-8"))
        data = b""
        while not data.endswith(b"\n"):
            potong = s.recv(65536)
            if not potong:
                break
            data += potong
    ms = (time.perf_counter() - t0) * 1000
    return json.loads(data.decode("utf-8")), ms


def dump_u2():
    req = urllib.request.Request(
        U2,
        data=json.dumps({"jsonrpc": "2.0", "id": 1,
                         "method": "dumpWindowHierarchy",
                         "params": [False, 50]}).encode(),
        headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())["result"]


def main():
    teks = sys.argv[1] if len(sys.argv) > 1 else None
    print("== server pohon 19102 ==")
    lat = []
    for _ in range(5):
        r, ms = tanya("PING")
        lat.append(ms)
    print(f"PING x5: min {min(lat):.1f} ms, median {statistics.median(lat):.1f} ms "
          f"(versi {r.get('versi')}, umur {r.get('umur_ms')} ms)")
    r, _ = tanya("PAKET?")
    print(f"PAKET?: {r.get('paket')} (umur {r.get('umur_ms')} ms)")
    r, ms = tanya("POHON")
    print(f"POHON: {len(r.get('nodes', []))} node terpilih, "
          f"versi {r.get('versi')}, umur {r.get('umur_ms')} ms, jawab {ms:.1f} ms")
    if teks:
        print(f"== akurasi CARI {teks!r} ==")
        r, ms = tanya(f"CARI {teks}")
        print(f"pohon: {r} ({ms:.1f} ms)")
        if not r.get("ada"):
            print("HASIL: teks tidak ada di salinan pohon — cek manual.")
            return
        xml = dump_u2()
        cocok = None
        for m in re.finditer(r"<node[^>]*>", xml):
            tag = m.group(0)
            t = re.search(r'text="([^"]*)"', tag)
            d = re.search(r'content-desc="([^"]*)"', tag)
            if (t and t.group(1) == teks) or (d and d.group(1) == teks):
                b = re.search(r'bounds="(\[\d+,\d+\]\[\d+,\d+\])"', tag)
                if b:
                    cocok = b.group(1)
                    break
        if cocok is None:
            print("HASIL: teks tidak ketemu di dump u2 — akurasi tak bisa dinilai.")
        elif cocok == r.get("bounds"):
            print(f"HASIL: LULUS — bounds pohon == dump ({cocok})")
        else:
            print(f"HASIL: BEDA — pohon {r.get('bounds')} vs dump {cocok}")


if __name__ == "__main__":
    main()
