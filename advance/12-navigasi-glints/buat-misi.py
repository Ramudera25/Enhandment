#!/usr/bin/env python3
"""buat-misi.py — generator misi navigasi Glints (Enhandment advance/12).

Menghasilkan berkas .job untuk misi-cepat.py dari data satu item antrean:
- Bila --link berisi /opportunities/jobs/  -> misi DEEP LINK (template-tautan.job):
  satu intent VIEW langsung ke halaman detail lowongan di aplikasi.
- Selain itu (link explore / kosong)      -> misi PENCARIAN (template-cari.job):
  buka aplikasi, ketuk Cari, ketik nama perusahaan, ketuk saran perusahaan,
  berhenti di halaman hasil yang memuat kartu perusahaan.

Misi navigasi TIDAK PERNAH melamar. Titik keputusan (verifikasi listing,
jawaban skrining, KIRIM) tetap di tangan agen.

Pakai:
  python3 buat-misi.py --perusahaan "PT. Ungaran Sari Garments" \
      --posisi "Warehouse Coordinator" \
      --link "https://glints.com/id/opportunities/jobs/.../..." \
      [--cari "Ungaran Sari Garments"] [--keluaran ~/muse-droid/misi/nav.job]
"""
import argparse
import os
import sys

DIREKTORI = os.path.dirname(os.path.abspath(__file__))


def baca_template(nama):
    with open(os.path.join(DIREKTORI, nama), encoding="utf-8") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perusahaan", required=True,
                    help="nama perusahaan persis seperti tampil di saran/hasil aplikasi")
    ap.add_argument("--cari", default=None,
                    help="teks yang diketik di kolom pencarian (default: perusahaan tanpa awalan PT./CV.)")
    ap.add_argument("--posisi", required=True, help="judul posisi persis di listing")
    ap.add_argument("--link", default="", help="URL dari antrean (detail atau explore)")
    ap.add_argument("--keluaran", default=None,
                    help="berkas .job tujuan (default: ~/muse-droid/misi/nav-glints.job)")
    a = ap.parse_args()

    cari = a.cari
    if not cari:
        cari = a.perusahaan
        for awalan in ("PT. ", "PT ", "CV. ", "CV "):
            if cari.startswith(awalan):
                cari = cari[len(awalan):]
                break

    if "/opportunities/jobs/" in a.link:
        isi = (baca_template("template-tautan.job")
               .replace("{{URL}}", a.link)
               .replace("{{POSISI}}", a.posisi))
        jenis = "tautan (deep link)"
    else:
        isi = (baca_template("template-cari.job")
               .replace("{{PERUSAHAAN_CARI}}", cari)
               .replace("{{PERUSAHAAN_TAMPIL}}", a.perusahaan))
        jenis = "cari (pencarian perusahaan)"

    keluar = a.keluaran or os.path.expanduser("~/muse-droid/misi/nav-glints.job")
    os.makedirs(os.path.dirname(keluar), exist_ok=True)
    with open(keluar, "w", encoding="utf-8") as f:
        f.write(isi)
    print("misi %s tertulis: %s" % (jenis, keluar))
    return 0


if __name__ == "__main__":
    sys.exit(main())
