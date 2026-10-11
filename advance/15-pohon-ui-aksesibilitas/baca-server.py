#!/usr/bin/env python3
# baca-server.py — "Mata Baca" jalur SERVER untuk Enhandment.
#
# Latar (terverifikasi 11 Okt 2026, uji V4.4/V4.4.1 di A13): OCR di
# perangkat (perintah BACA di aplikasi pendamping) akurat tetapi
# latensinya 19–40 dtk/bingkai — jauh di atas target desain <=4 dtk.
# Keputusan penempatan: jalur utama BACA = bingkai dari HP (perintah
# BINGKAI V4.3) di-OCR di VM ini (PP-OCRv5 via RapidOCR, 1,2–3,5 dtk
# per bingkai pada layar aplikasi biasa). Perintah BACA di perangkat
# tetap ada sebagai cadangan luring terakhir.
#
# Pakai (WAJIB python dari venv prototipe yang memuat rapidocr):
#   ~/workspace/enhandment-ocr-proto/venv/bin/python baca-server.py [ambang]
# Keluaran: format sama persis dengan perintah BACA di perangkat —
# baris header JSON {ok, latensi_ms, jumlah_baris, jalur:"server"}
# lalu satu baris per teks: "teks<TAB>x1,y1,x2,y2<TAB>skor".
# Penyaring positif-palsu v1 yang sama dengan di perangkat: buang
# baris simbol-saja <=2 karakter dan baris di pita status bar.
import json
import subprocess
import sys
import time
from pathlib import Path

SSH = ["ssh", "-F", "/home/hatch/.ssh/config", "-o", "ConnectTimeout=25"]
SCP = ["scp", "-F", "/home/hatch/.ssh/config", "-o", "ConnectTimeout=25"]
PROTO = Path.home() / "workspace" / "enhandment-ocr-proto"
MODELS = PROTO / "models"
LOKAL = Path("/tmp/bingkai-server.png")
JAUH = "~/muse-droid/bukti/bingkai-server.png"


def ambil_bingkai() -> bool:
    # Di HP: minta BINGKAI segar lewat klien uji socket, salin hasilnya.
    perintah = (
        "cd ~/muse-droid && python3 uji-v44.py BINGKAI >/dev/null 2>&1; "
        f"cp ~/muse-droid/bukti/bingkai-v44.png {JAUH}"
    )
    r = subprocess.run(SSH + ["termux-hp", perintah],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return False
    r = subprocess.run(SCP + [f"termux-hp:{JAUH}", str(LOKAL)],
                       capture_output=True, text=True, timeout=120)
    return r.returncode == 0 and LOKAL.exists()


def main() -> int:
    ambang = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    mulai = time.perf_counter()
    if not ambil_bingkai():
        print(json.dumps({"ok": False, "sebab": "bingkai gagal diambil",
                          "jalur": "server", "jumlah_baris": 0}))
        return 1
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR(
        det_model_path=str(MODELS / "ch_PP-OCRv5_det_mobile.onnx"),
        rec_model_path=str(MODELS / "latin_PP-OCRv5_rec_mobile.onnx"),
        rec_keys_path=str(MODELS / "ppocrv5_latin_dict.txt"),
    )
    hasil, _ = engine(str(LOKAL))
    # Tinggi bingkai untuk pita status bar (~3% teratas, sama seperti
    # pendekatan tinggiStatusBar di perangkat secara praktis).
    from PIL import Image
    tinggi = Image.open(LOKAL).height
    strip = int(tinggi * 0.035)
    baris = []
    for kotak, teks, skor in (hasil or []):
        if float(skor) < ambang:
            continue
        t = teks.strip()
        if len(t) <= 2 and not any(c.isalnum() for c in t):
            continue
        xs = [p[0] for p in kotak]
        ys = [p[1] for p in kotak]
        x1, y1, x2, y2 = round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))
        if (y1 + y2) / 2 < strip:
            continue
        baris.append((teks, x1, y1, x2, y2, float(skor)))
    latensi = round((time.perf_counter() - mulai) * 1000)
    print(json.dumps({"ok": True, "jalur": "server",
                      "latensi_ms": latensi, "jumlah_baris": len(baris)}))
    for teks, x1, y1, x2, y2, skor in baris:
        print(f"{teks}\t{x1},{y1},{x2},{y2}\t{skor:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
