#!/usr/bin/env python3
# grounding.py — layanan grounding CADANGAN Enhandment (lapis ke-4).
#
# Latar (DESAIN-GROUNDING.md, 11 Okt 2026): bila pohon aksesibilitas
# kosong DAN OCR tidak memuat target DAN pohon sintetis gagal, lapis
# terakhir adalah model grounding (bingkai + perintah -> satu titik).
# Model: UI-TARS-2B-SFT (Apache-2.0) bentuk GGUF Q4_K_M + mmproj f16
# (konversi komunitas bartowski; GGUF resmi ByteDance sudah diturunkan
# oleh pembuatnya), dilayani llama.cpp (llama-server) di mesin server
# (f4) — TIDAK di HP dan TIDAK di VM agen (RAM tidak cukup).
#
# Pakai:
#   python3 grounding.py <bingkai.png> "<perintah>" --base-url http://127.0.0.1:18123
#   python3 grounding.py <bingkai.png> "<perintah>" --spawn \
#       --llama-dir /path/llama-bXXXX --model model.gguf --mmproj mmproj.gguf
#
# Keluaran (satu baris JSON di stdout):
#   {"x": <px>, "y": <px>, "latensi_ms": <int>, "model": "<label>"}
# Koordinat model UI-TARS v1 berskala relatif 0-1000; diubah ke piksel
# bingkai asli di sini. Keluaran mentah model ditulis ke stderr.
import argparse
import base64
import json
import re
import struct
import subprocess
import sys
import time
import urllib.request

LABEL_MODEL = "UI-TARS-2B-SFT-Q4_K_M.gguf + llama.cpp"
TEMPLATE = "Please provide the x,y coordinate of the element: {perintah}"


def ukuran_png(path):
    # Baca lebar/tinggi dari header IHDR PNG (tanpa dependensi PIL).
    with open(path, "rb") as f:
        kepala = f.read(24)
    if kepala[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("bukan berkas PNG: %s" % path)
    w, h = struct.unpack(">II", kepala[16:24])
    return w, h


def uraikan_koordinat(teks, lebar, tinggi):
    # Bentuk-bentuk keluaran UI-TARS: {"x": 123, "y": 456} /
    # click(start_box='(123,456)') / click(point='123 456') / (123, 456)
    m = re.search(r'"x"\s*:\s*(\d+)\D{0,8}?"y"\s*:\s*(\d+)', teks)
    if not m:
        m = re.search(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", teks)
    if not m:
        m = re.search(r"point='(\d+)\s+(\d+)'", teks)
    if not m:
        return None
    x, y = int(m.group(1)), int(m.group(2))
    # Skala relatif 0-1000 (konvensi UI-TARS v1/Qwen2-VL). Nilai yang
    # jelas piksel (>1000) dibiarkan apa adanya.
    if x <= 1000 and y <= 1000:
        x = round(x / 1000 * lebar)
        y = round(y / 1000 * tinggi)
    return x, y


def panggil_server(base_url, png_path, perintah, timeout=900):
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    badan = {
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": "data:image/png;base64," + b64}},
                {"type": "text", "text": TEMPLATE.format(perintah=perintah)},
            ],
        }],
        "temperature": 0,
        "max_tokens": 128,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(badan).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        hasil = json.loads(resp.read().decode())
    latensi = round((time.perf_counter() - t0) * 1000)
    return hasil["choices"][0]["message"]["content"], latensi


def tunggu_sehat(base_url, batas=600):
    t0 = time.time()
    while time.time() - t0 < batas:
        try:
            with urllib.request.urlopen(base_url.rstrip("/") + "/health",
                                        timeout=5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(3)
    return False


def main():
    ap = argparse.ArgumentParser(description="Grounding cadangan Enhandment")
    ap.add_argument("png")
    ap.add_argument("perintah")
    ap.add_argument("--base-url", default=None,
                    help="URL llama-server yang sudah jalan (mis. f4 via "
                         "tunnel SSH): http://127.0.0.1:18123")
    ap.add_argument("--spawn", action="store_true",
                    help="nyalakan llama-server sendiri lalu matikan lagi")
    ap.add_argument("--llama-dir", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--mmproj", default=None)
    ap.add_argument("--port", type=int, default=18123)
    args = ap.parse_args()

    lebar, tinggi = ukuran_png(args.png)
    proc = None
    base = args.base_url
    try:
        if args.spawn:
            if not (args.llama_dir and args.model and args.mmproj):
                print("ERROR: --spawn butuh --llama-dir/--model/--mmproj",
                      file=sys.stderr)
                return 2
            base = "http://127.0.0.1:%d" % args.port
            proc = subprocess.Popen(
                [args.llama_dir.rstrip("/") + "/llama-server",
                 "-m", args.model, "--mmproj", args.mmproj,
                 "-c", "8192", "--host", "127.0.0.1",
                 "--port", str(args.port)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not tunggu_sehat(base):
                print("ERROR: llama-server tidak kunjung sehat",
                      file=sys.stderr)
                return 2
        if not base:
            print("ERROR: beri --base-url atau --spawn", file=sys.stderr)
            return 2
        mentah, latensi = panggil_server(base, args.png, args.perintah)
    finally:
        if proc is not None:
            proc.terminate()
    print("mentah: %s" % mentah.strip(), file=sys.stderr)
    titik = uraikan_koordinat(mentah, lebar, tinggi)
    if titik is None:
        print("ERROR: koordinat tidak ditemukan di keluaran model",
              file=sys.stderr)
        return 1
    print(json.dumps({"x": titik[0], "y": titik[1],
                      "latensi_ms": latensi, "model": LABEL_MODEL}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
