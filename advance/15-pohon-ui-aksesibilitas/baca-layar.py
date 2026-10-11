#!/usr/bin/env python3
# baca-layar.py — klien perintah BACA server pohon 19102 (V4.4 "Mata Baca").
# Minta OCR di perangkat atas bingkai segar. Balasan server: satu baris
# JSON header (ok, versi_bingkai, latensi_ms, jumlah_baris), lalu
# baris-baris "teks<TAB>x1,y1,x2,y2<TAB>skor" sampai koneksi ditutup.
# Pakai: python3 baca-layar.py [ambang] [STATUSBAR]
#   ambang     ambang skor minimum (bawaan server 0,5)
#   STATUSBAR  sertakan pita status bar (bawaan server: diabaikan)
import socket, json, sys

argumen = " ".join(sys.argv[1:])
perintah = "BACA" + ((" " + argumen) if argumen else "")
s = socket.create_connection(("127.0.0.1", 19102), timeout=120)
s.sendall((perintah + "\n").encode())
f = s.makefile("rb")
header = json.loads(f.readline().decode().strip())
print("header:", header)
if header.get("ok"):
    for mentah in f:
        baris = mentah.decode("utf-8", "replace").rstrip("\n")
        if not baris:
            continue
        bagian = baris.split("\t")
        if len(bagian) == 3:
            teks, kotak, skor = bagian
            x1, y1, x2, y2 = kotak.split(",")
            print(f"[{skor}] ({x1},{y1})-({x2},{y2}) {teks}")
        else:
            print(baris)
s.close()
