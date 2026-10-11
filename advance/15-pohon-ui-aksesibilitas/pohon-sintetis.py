#!/usr/bin/env python3
# pohon-sintetis.py — "Pohon Sintetis" Enhandment: parser bingkai →
# daftar elemen berbentuk simpul POHON, untuk layar yang pohon
# aksesibilitasnya kosong/nyaris kosong (kanvas/WebView).
#
# Pipa: bingkai PNG → detektor elemen interaktif icon_detect_v3
# (YOLOv9-E, TorchScript) → kotak elemen; teks elemen dari PP-OCRv5
# (RapidOCR, model sama dengan baca-server.py) yang dipasangkan ke
# kotak; baris OCR tanpa kotak detektor tetap diterbitkan sebagai
# elemen teks. Keluaran meniru bentuk simpul POHON asli:
# {t, d, k, b:"[x1,y1][x2,y2]", klik} + penanda sintetis:true + skor.
#
# LISENSI MODEL (gerbang keras desain, terverifikasi 11 Okt 2026):
# icon_detect_v3 dari microsoft/OmniParser-v2.0 berlisensi MIT —
# berkas LICENSE di folder icon_detect_v3/ adalah teks MIT License
# (Copyright (c) Microsoft Corporation) dan README repo menyatakan
# v3 berbasis implementasi YOLOv9 berlisensi MIT. Detektor lama
# berbasis Ultralytics (icon_detect v1/v2) berlisensi AGPL dan
# DILARANG dipakai di sini. Model dimuat sebagai TorchScript
# (torch.jit.load) — tanpa kode Ultralytics/YOLOv9 sama sekali.
#
# DOKTRIN: pohon sintetis adalah penasihat lapis ketiga. Ia hanya
# dikonsultasikan bila POHON asli <5 simpul atau diminta eksplisit;
# ia tidak pernah mengalahkan pohon asli, dan ketukan dari elemen
# sintetis wajib diverifikasi pasca-ketuk seperti biasa.
#
# Pakai (WAJIB python dari venv prototipe yang memuat rapidocr+torch):
#   ~/workspace/enhandment-ocr-proto/venv/bin/python pohon-sintetis.py \
#       <bingkai.png> [--conf 0.25] [--keluaran elemen.json]
# Tanpa --keluaran, JSON elemen dicetak ke stdout sesudah baris
# header {ok, latensi_ms, jumlah_elemen, jalur:"sintetis"}.
import argparse
import json
import sys
import time
from pathlib import Path

PROTO = Path.home() / "workspace" / "enhandment-ocr-proto"
MODELS = PROTO / "models"
MODEL_DET = PROTO / "models-det" / "icon_detect_v3.pt"
STRIDES = (8, 16, 32)


def muat_detektor():
    import torch
    model = torch.jit.load(str(MODEL_DET), map_location="cpu").eval()
    return model


def kotak_surat(img, sisi_maks=1280):
    """Letterbox: skala gambar agar sisi terpanjang <= sisi_maks dan
    kedua sisi kelipatan 32, beri bantalan abu-abu 114 di tengah.
    Mengembalikan (tensor, skala, pad_kiri, pad_atas)."""
    import numpy as np
    import torch
    from PIL import Image

    w, h = img.size
    skala = min(sisi_maks / max(w, h), 1.0)
    rw, rh = int(w * skala), int(h * skala)
    tw = max(32, (rw // 32) * 32)
    th = max(32, (rh // 32) * 32)
    skala_x, skala_y = tw / w, th / h
    resized = img.resize((tw, th), Image.Resampling.LANCZOS)
    kanvas = Image.new("RGB", (tw, th), (114, 114, 114))
    kanvas.paste(resized, (0, 0))
    arr = np.asarray(kanvas, dtype=np.float32).transpose(2, 0, 1) / 255.0
    tensor = torch.from_numpy(arr).unsqueeze(0)
    return tensor, skala_x, skala_y


def nms(kotak, skor, ambang_iou=0.7, maks=300):
    """NMS kelas-tunggal sederhana (urut skor menurun)."""
    import torch

    if len(kotak) == 0:
        return []
    urut = skor.argsort(descending=True)
    simpan = []
    while len(urut) > 0 and len(simpan) < maks:
        i = int(urut[0])
        simpan.append(i)
        if len(urut) == 1:
            break
        sisa = urut[1:]
        b = kotak[i]
        bs = kotak[sisa]
        x1 = torch.maximum(b[0], bs[:, 0])
        y1 = torch.maximum(b[1], bs[:, 1])
        x2 = torch.minimum(b[2], bs[:, 2])
        y2 = torch.minimum(b[3], bs[:, 3])
        luas_iris = (x2 - x1).clamp(0) * (y2 - y1).clamp(0)
        luas = (b[2] - b[0]) * (b[3] - b[1]) + \
            (bs[:, 2] - bs[:, 0]) * (bs[:, 3] - bs[:, 1]) - luas_iris
        iou = luas_iris / luas.clamp(min=1)
        urut = sisa[iou <= ambang_iou]
    return simpan


def deteksi(model, img, conf=0.25):
    """Jalankan detektor; kembalikan daftar (x1,y1,x2,y2,skor) pada
    koordinat gambar asli."""
    import torch

    tensor, sx, sy = kotak_surat(img)
    with torch.inference_mode():
        keluaran = model(tensor)
    semua_kotak, semua_skor = [], []
    for idx, stride in enumerate(STRIDES):
        logits = keluaran[idx * 2][0, 0]        # (H, W) 1 kelas
        jarak = keluaran[idx * 2 + 1][0]         # (4, H, W) l,t,r,b
        hh, ww = logits.shape
        skor_grid = torch.sigmoid(logits).reshape(-1)
        jarak = jarak.permute(1, 2, 0).reshape(-1, 4) * stride
        gy, gx = torch.meshgrid(torch.arange(hh), torch.arange(ww),
                                indexing="ij")
        jangkar = (torch.stack((gx, gy), dim=-1).reshape(-1, 2) + 0.5) * stride
        kotak = torch.cat((jangkar - jarak[:, :2], jangkar + jarak[:, 2:]),
                          dim=-1)
        lolos = skor_grid > conf
        semua_kotak.append(kotak[lolos])
        semua_skor.append(skor_grid[lolos])
    if not semua_kotak:
        return []
    kotak = torch.cat(semua_kotak)
    skor = torch.cat(semua_skor)
    # Kembalikan ke koordinat asli (letterbox tanpa bantalan asimetris:
    # gambar ditempel di (0,0) sesudah resize ke kelipatan 32).
    kotak[:, [0, 2]] = (kotak[:, [0, 2]] / sx).clamp(0, img.size[0])
    kotak[:, [1, 3]] = (kotak[:, [1, 3]] / sy).clamp(0, img.size[1])
    hasil = []
    for i in nms(kotak, skor):
        x1, y1, x2, y2 = (float(v) for v in kotak[i])
        if x2 - x1 < 8 or y2 - y1 < 8:
            continue
        hasil.append((round(x1), round(y1), round(x2), round(y2),
                      round(float(skor[i]), 3)))
    return hasil


def ocr_baris(path_png):
    """PP-OCRv5 lewat RapidOCR — pola sama dengan baca-server.py.
    Kembalikan daftar (teks, x1, y1, x2, y2, skor)."""
    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR(
        det_model_path=str(MODELS / "ch_PP-OCRv5_det_mobile.onnx"),
        rec_model_path=str(MODELS / "latin_PP-OCRv5_rec_mobile.onnx"),
        rec_keys_path=str(MODELS / "ppocrv5_latin_dict.txt"),
    )
    hasil, _ = engine(str(path_png))
    baris = []
    for kotak, teks, skor in (hasil or []):
        xs = [p[0] for p in kotak]
        ys = [p[1] for p in kotak]
        baris.append((teks, round(min(xs)), round(min(ys)),
                      round(max(xs)), round(max(ys)), round(float(skor), 3)))
    return baris


def gabung(kotak_det, baris_ocr, w, h):
    """Pasangkan baris OCR ke kotak detektor (pusat baris di dalam
    kotak), lalu susun elemen bentuk simpul POHON. Elemen yang
    pusatnya di pita status bar (3,5% teratas) dibuang — penyaring
    yang sama dengan baca-server.py; isinya jam/glyph, bukan UI."""
    terpakai = set()
    pasangan = {i: [] for i in range(len(kotak_det))}
    for j, (_, x1, y1, x2, y2, _) in enumerate(baris_ocr):
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        kandidat = None
        for i, (a1, b1, a2, b2, _) in enumerate(kotak_det):
            if a1 <= cx <= a2 and b1 <= cy <= b2:
                luas = (a2 - a1) * (b2 - b1)
                if kandidat is None or luas < kandidat[1]:
                    kandidat = (i, luas)
        if kandidat is not None:
            pasangan[kandidat[0]].append(j)
            terpakai.add(j)

    elemen = []
    luas_layar = w * h
    for i, (x1, y1, x2, y2, skor) in enumerate(kotak_det):
        if (x2 - x1) * (y2 - y1) > 0.9 * luas_layar and len(kotak_det) > 1:
            continue  # kotak sebesar layar = bukan elemen
        isi = sorted((baris_ocr[j] for j in pasangan[i]),
                     key=lambda b: (b[2], b[1]))
        teks = " ".join(b[0] for b in isi).strip()
        if teks:
            elemen.append({
                "t": teks, "d": "elemen interaktif berteks (detektor+OCR)",
                "k": "sintetis/teks", "b": f"[{x1},{y1}][{x2},{y2}]",
                "klik": True, "sintetis": True, "skor": skor})
        else:
            elemen.append({
                "t": "", "d": "elemen interaktif tanpa teks (detektor)",
                "k": "sintetis/ikon", "b": f"[{x1},{y1}][{x2},{y2}]",
                "klik": True, "sintetis": True, "skor": skor})
    for j, (teks, x1, y1, x2, y2, skor) in enumerate(baris_ocr):
        if j in terpakai:
            continue
        elemen.append({
            "t": teks, "d": "teks OCR tanpa kotak detektor",
            "k": "sintetis/teks", "b": f"[{x1},{y1}][{x2},{y2}]",
            "klik": False, "sintetis": True, "skor": skor})
    def koord(e):
        import re
        return [int(v) for v in re.findall(r"\d+", e["b"])]  # x1,y1,x2,y2

    strip = h * 0.035
    elemen = [e for e in elemen if (koord(e)[1] + koord(e)[3]) / 2 >= strip]
    elemen.sort(key=lambda e: (koord(e)[1], koord(e)[0]))
    return elemen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bingkai")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--keluaran", default=None)
    args = ap.parse_args()

    from PIL import Image

    mulai = time.perf_counter()
    img = Image.open(args.bingkai).convert("RGB")
    model = muat_detektor()
    t_det = time.perf_counter()
    kotak_det = deteksi(model, img, conf=args.conf)
    t_ocr = time.perf_counter()
    baris_ocr = ocr_baris(args.bingkai)
    elemen = gabung(kotak_det, baris_ocr, img.size[0], img.size[1])
    latensi = round((time.perf_counter() - mulai) * 1000)
    header = {"ok": True, "jalur": "sintetis", "latensi_ms": latensi,
              "latensi_deteksi_ms": round((t_ocr - t_det) * 1000),
              "latensi_ocr_ms": round((time.perf_counter() - t_ocr) * 1000),
              "jumlah_elemen": len(elemen),
              "jumlah_kotak_detektor": len(kotak_det),
              "jumlah_baris_ocr": len(baris_ocr)}
    print(json.dumps(header))
    teks_json = json.dumps(elemen, ensure_ascii=False, indent=1)
    if args.keluaran:
        Path(args.keluaran).write_text(teks_json, encoding="utf-8")
    else:
        print(teks_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
