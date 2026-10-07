#!/usr/bin/env python3
"""04-router-model.py — model bertingkat: langkah mudah jangan dibayar mahal.

Status: PROTOTIPE (folder advance/) — kebijakan + klasifikasi; penyambungan ke
LiteLLM/9Router mengikuti alias yang sudah ada di instalasi masing-masing.

Kenapa: tidak semua langkah butuh otak paling besar. Membaca ringkasan layar
dan memilih ketukan yang jelas itu pekerjaan ringan; merencanakan misi dan
membaca vision pada kanvas itu pekerjaan berat. Router ini mengklasifikasikan
langkah, lalu memilih tingkat model:

  RUTIN   -> model kecil/cepat   (baca ringkas, TUNGGU/CEK, ketuk jelas)
  VISION  -> model berkemampuan gambar, kelas menengah
  RENCANA -> model terbesar yang tersedia (menyusun misi, memulihkan kegagalan)

CLI: 04-router-model.py "<jenis>" "<cuplikan konteks>"
  -> mencetak nama tingkat + saran alias (bisa ditimpa lewat MD_MODEL_*).
"""
import os
import sys

TINGKAT = {
    "RUTIN": os.environ.get("MD_MODEL_RUTIN", "model-kecil"),
    "VISION": os.environ.get("MD_MODEL_VISION", "model-vision"),
    "RENCANA": os.environ.get("MD_MODEL_RENCANA", "model-besar"),
}

KATA_RENCANA = ("susun misi", "rencana", "pulihkan", "diagnosis", "gagal",
                "kenapa", "strategi", "putuskan")


def klasifikasikan(jenis: str, konteks: str = "") -> str:
    """jenis: perintah/langkah yang akan dijalankan; konteks: teks bebas."""
    j = jenis.lower()
    k = konteks.lower()
    if j in ("foto", "vision", "kotak", "ocr-sulit") or "kanvas" in k:
        return "VISION"
    if any(kata in k for kata in KATA_RENCANA) or j in ("misi-baru", "perencana"):
        return "RENCANA"
    return "RUTIN"


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    t = klasifikasikan(a[0], a[1] if len(a) > 1 else "")
    print(f"{t} -> {TINGKAT[t]}")
