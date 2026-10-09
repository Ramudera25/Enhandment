#!/usr/bin/env python3
# ambil-bingkai.py — klien perintah BINGKAI/AMBIL server pohon 19102 (V4.3).
# BINGKAI: minta tangkapan segar; AMBIL: ambil bingkai buffer terakhir.
# Balasan server: satu baris JSON header, lalu N byte PNG mentah.
# Pakai: python3 ambil-bingkai.py [BINGKAI|AMBIL] [berkas-keluar.png]
import socket, json, sys

perintah = sys.argv[1] if len(sys.argv) > 1 else "BINGKAI"
keluar = sys.argv[2] if len(sys.argv) > 2 else "/sdcard/bingkai.png"
s = socket.create_connection(("127.0.0.1", 19102), timeout=15)
s.sendall((perintah + "\n").encode())
f = s.makefile("rb")
header = json.loads(f.readline().decode().strip())
print("header:", header)
if header.get("ok"):
    n = header["byte"]; data = b""
    while len(data) < n:
        potong = f.read(n - len(data))
        if not potong: break
        data += potong
    open(keluar, "wb").write(data)
    print("tersimpan:", keluar, len(data), "byte")
s.close()
