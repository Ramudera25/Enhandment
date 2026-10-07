#!/usr/bin/env python3
"""07-resep.py — memori resep: misi yang berhasil jangan diimprovisasi ulang.

Status: PROTOTIPE (folder advance/).

Cara berpikirnya: berkas .job yang terbukti BERES adalah aset. Alat ini:
  simpan  — salin .job sukses menjadi resep bernama, dengan nilai-nilai khusus
            misi itu diganti penanda {{PARAM}} (mis. nama perusahaan, tautan).
  pakai   — tuang resep menjadi .job baru dengan mengisi parameternya.
  gagal   — catat kegagalan (misi, langkah, penyebab) ke indeks kegagalan,
            supaya pola gagal yang sama tidak diulang buta.
  daftar  — lihat semua resep + hitungan pakai/beres/gagalnya.

Penyimpanan: folder resep/ di sebelah skrip ini; indeks di resep/indeks.json.

Pakai:
  07-resep.py simpan <nama> <file.job>
  07-resep.py pakai <nama> KUNCI=NILAI ... > misi-baru.job
  07-resep.py gagal <nama> <langkah> "<penyebab>"
  07-resep.py daftar
"""
import json
import re
import sys
from pathlib import Path

DASAR = Path(__file__).with_name("resep")
INDEKS = DASAR / "indeks.json"


def muat() -> dict:
    return json.loads(INDEKS.read_text()) if INDEKS.exists() else {}


def simpan_indeks(idx: dict) -> None:
    DASAR.mkdir(exist_ok=True)
    INDEKS.write_text(json.dumps(idx, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    a = sys.argv[1:]
    idx = muat()
    if a and a[0] == "simpan" and len(a) == 3:
        DASAR.mkdir(exist_ok=True)
        isi = Path(a[2]).read_text()
        (DASAR / f"{a[1]}.job").write_text(isi)
        idx.setdefault(a[1], {"pakai": 0, "beres": 0, "gagal": []})
        simpan_indeks(idx)
        params = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", isi)))
        print(f"resep '{a[1]}' tersimpan. parameter: {', '.join(params) or '(tidak ada)'}")
        print("tip: sunting resepnya, ganti nilai khusus misi dengan {{PARAM}} bila belum.")
    elif a and a[0] == "pakai" and len(a) >= 2:
        berkas = DASAR / f"{a[1]}.job"
        if not berkas.exists():
            print(f"resep tidak ada: {a[1]}", file=sys.stderr)
            sys.exit(1)
        isi = berkas.read_text()
        for kv in a[2:]:
            kunci, _, nilai = kv.partition("=")
            isi = isi.replace("{{" + kunci + "}}", nilai)
        sisa = re.findall(r"\{\{[A-Z_]+\}\}", isi)
        if sisa:
            print(f"parameter belum diisi: {', '.join(sorted(set(sisa)))}", file=sys.stderr)
            sys.exit(1)
        idx.setdefault(a[1], {"pakai": 0, "beres": 0, "gagal": []})
        idx[a[1]]["pakai"] += 1
        simpan_indeks(idx)
        print(isi, end="")
    elif a and a[0] == "gagal" and len(a) == 4:
        idx.setdefault(a[1], {"pakai": 0, "beres": 0, "gagal": []})
        idx[a[1]]["gagal"].append({"langkah": a[2], "penyebab": a[3]})
        simpan_indeks(idx)
        print(f"kegagalan '{a[1]}' tercatat (total {len(idx[a[1]]['gagal'])})")
    elif a and a[0] == "daftar":
        if not idx:
            print("(belum ada resep)")
        for nama, v in sorted(idx.items()):
            print(f"{nama}: dipakai {v['pakai']}x, kegagalan tercatat {len(v['gagal'])}")
    else:
        print(__doc__)
        sys.exit(2)
