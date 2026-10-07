#!/usr/bin/env python3
"""03-peta-layar.py — peta layar tersimpan: cache koordinat elemen per aplikasi.

Status: PROTOTIPE (folder advance/).

Kenapa: banyak layar itu-itu saja. Sekali sebuah elemen ditemukan (mis. tombol
"Lamar" di aplikasi X selalu di kanan bawah), koordinatnya disimpan. Misi
berikutnya bertanya ke peta dulu — ketemu: langsung ketuk; tidak ketemu / hasil
ketuk tidak sesuai harapan: cari ulang dengan cara biasa lalu perbarui peta.
Peta disimpan sebagai JSON di folder yang sama (peta-layar.json), kuncinya
"<paket-aktivitas>|<teks elemen>".

Pakai:
  03-peta-layar.py catat <dump.xml> <paket> "<teks>"   # belajar dari dump sukses
  03-peta-layar.py cari  <paket> "<teks>"              # -> "x y" atau kosong (exit 1)
  03-peta-layar.py lupakan <paket> "<teks>"            # hapus entri (elemen pindah)
"""
import json
import re
import sys
from pathlib import Path

PETA = Path(__file__).with_name("peta-layar.json")


def muat() -> dict:
    return json.loads(PETA.read_text()) if PETA.exists() else {}


def simpan(p: dict) -> None:
    PETA.write_text(json.dumps(p, indent=1, ensure_ascii=False))


def titik_dari_dump(path: str, teks: str):
    data = Path(path).read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"<node[^>]*>", data):
        tag = m.group(0)
        t = re.search(r'text="([^"]*)"', tag)
        d = re.search(r'content-desc="([^"]*)"', tag)
        if (t and teks in t.group(1)) or (d and teks in d.group(1)):
            b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', tag)
            if b:
                x1, y1, x2, y2 = map(int, b.groups())
                return (x1 + x2) // 2, (y1 + y2) // 2
    return None


if __name__ == "__main__":
    a = sys.argv[1:]
    peta = muat()
    if a and a[0] == "catat" and len(a) == 4:
        titik = titik_dari_dump(a[1], a[3])
        if not titik:
            print("elemen tidak ditemukan di dump", file=sys.stderr)
            sys.exit(1)
        peta[f"{a[2]}|{a[3]}"] = {"x": titik[0], "y": titik[1]}
        simpan(peta)
        print(f"tercatat: {a[2]}|{a[3]} -> {titik[0]} {titik[1]}")
    elif a and a[0] == "cari" and len(a) == 3:
        e = peta.get(f"{a[1]}|{a[2]}")
        if not e:
            sys.exit(1)
        print(f"{e['x']} {e['y']}")
    elif a and a[0] == "lupakan" and len(a) == 3:
        peta.pop(f"{a[1]}|{a[2]}", None)
        simpan(peta)
        print("terhapus")
    else:
        print(__doc__)
        sys.exit(2)
