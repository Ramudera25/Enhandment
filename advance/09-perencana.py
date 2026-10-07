#!/usr/bin/env python3
"""09-perencana.py — susun draf misi dari spesifikasi + dry-run terhadap dump.

Status: PROTOTIPE (folder advance/).

Dua pekerjaan:
  susun <spesifikasi.json>  — ubah spesifikasi tingkat-tinggi menjadi draf
    berkas .job yang rapi & terverifikasi kosa-katanya. Format spesifikasi:
      {"tujuan": "Lamar posisi X di aplikasi Y",
       "aplikasi": "com.contoh.app",
       "langkah": [["BUKA", "com.contoh.app/.MainActivity"],
                   ["TUNGGU_TEKS", "\"Lamar\"", 30],
                   ["KETUK_TEKS", "\"Lamar Sekarang\""]]}
  uji <file.job> <dump.xml> — DRY-RUN: jalan-jalan di atas kertas. Setiap
    langkah yang bersifat membaca (TUNGGU_TEKS/CEK_TEKS/KETUK_TEKS) dievaluasi
    terhadap dump yang diberikan: lolos/gagal + koordinatnya. Langkah aksi
    ditandai "nyata (tidak disimulasikan)". Tidak ada satu pun perintah yang
    dikirim ke HP.

Kenapa dry-run penting: misi yang salah susun ketahuan di meja, bukan di layar
HP orang. Untuk misi sensitif, jalankan `uji` dulu terhadap dump layar awal.
"""
import json
import re
import sys
from pathlib import Path

KOSA_KATA = {"BUKA", "TUNGGU_TEKS", "KETUK_TEKS", "KETUK", "GESER", "KETIK",
             "TEMPEL", "TOMBOL", "JEDA", "FOTO", "CEK_TEKS"}


def cari_titik(xml: str, teks: str):
    for m in re.finditer(r"<node[^>]*>", xml):
        tag = m.group(0)
        t = re.search(r'text="([^"]*)"', tag)
        if t and teks in t.group(1):
            b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', tag)
            if b:
                x1, y1, x2, y2 = map(int, b.groups())
                return (x1 + x2) // 2, (y1 + y2) // 2
    return None


def susun(path: str) -> None:
    spec = json.loads(Path(path).read_text())
    print(f"# MISI: {spec.get('tujuan', '(tanpa judul)')}")
    if spec.get("aplikasi"):
        print(f"# Aplikasi: {spec['aplikasi']} — baca dulu 08-pengetahuan/{spec['aplikasi']}.md")
    for langkah in spec["langkah"]:
        cmd = str(langkah[0]).upper()
        if cmd not in KOSA_KATA:
            print(f"# PERINGATAN: perintah tidak dikenal: {cmd}", file=sys.stderr)
            sys.exit(1)
        print(" ".join([cmd] + [str(x) for x in langkah[1:]]))


def uji(job_path: str, dump_path: str) -> None:
    xml = Path(dump_path).read_text(encoding="utf-8", errors="replace")
    n = 0
    for baris in Path(job_path).read_text().splitlines():
        baris = baris.strip()
        if not baris or baris.startswith("#"):
            continue
        n += 1
        cmd, _, sisa = baris.partition(" ")
        sisa = sisa.strip()
        if cmd == "TUNGGU_TEKS":   # bentuk: "teks" [timeout]
            mq = re.match(r'"([^"]*)"', sisa)
            teks = mq.group(1) if mq else sisa.split()[0]
        else:
            teks = sisa.strip('"')
        if cmd in ("TUNGGU_TEKS", "CEK_TEKS", "KETUK_TEKS"):
            titik = cari_titik(xml, teks)
            if titik:
                print(f"{n:>2} {cmd:<12} LULUS — \"{teks}\" ada @ {titik[0]},{titik[1]}")
            else:
                print(f"{n:>2} {cmd:<12} GAGAL — \"{teks}\" tidak ada di dump ini")
        elif cmd in KOSA_KATA:
            print(f"{n:>2} {cmd:<12} nyata (tidak disimulasikan) — {sisa}")
        else:
            print(f"{n:>2} {cmd:<12} PERINGATAN: perintah tidak dikenal")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "susun" and len(a) == 2:
        susun(a[1])
    elif a and a[0] == "uji" and len(a) == 3:
        uji(a[1], a[2])
    else:
        print(__doc__)
        sys.exit(2)
