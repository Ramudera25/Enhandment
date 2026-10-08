#!/usr/bin/env python3
"""uji-klien.py — uji protokol layanan lokal pendamping dari Termux."""
import socket
import sys


def kirim(perintah, baca_sampai_akhir=False):
    s = socket.create_connection(("127.0.0.1", 19101), timeout=15)
    s.sendall((perintah + "\n").encode())
    data = b""
    if baca_sampai_akhir:
        while b".AKHIR" not in data:
            potong = s.recv(65536)
            if not potong:
                break
            data += potong
    else:
        data = s.recv(65536)
    s.close()
    return data.decode(errors="replace")


print("PING ->", kirim("PING").strip())
print("UID  ->", kirim("UID").strip())
x = kirim("DUMP", baca_sampai_akhir=True)
print(f"DUMP -> {len(x)} karakter; mulai: {x[:60]!r}; ada .AKHIR: {'.AKHIR' in x}")
print("TOMBOL 4 (back) ->", kirim("TOMBOL 4").strip())
