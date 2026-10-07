#!/usr/bin/env python3
"""mata-dua.py — perkakas Mata Kedua muse-droid (berjalan di mesin agent).

Subperintah:
  ringkas <dump.xml>            XML uiautomator mentah -> daftar elemen ringkas
  kotak <foto.png> [K] [B]      gambar grid bernomor (Set-of-Mark) + peta .json
  ketuk <peta.json> <sel> [sub] koordinat ketuk dari nomor sel (+ sub 1-9, pola keypad)
  ocr <foto.png>                teks + titik tengah tiap teks (RapidOCR / tesseract)

Prinsipnya: XML adalah mata utama (murah & presisi). Alat-alat di sini menyala
saat XML buta — kanvas, gambar, verifikasi visual. Lihat docs/10-mata-kedua.md.
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def cmd_ringkas(path: str) -> None:
    data = Path(path).read_text(encoding="utf-8", errors="replace")
    out = []
    for m in re.finditer(r"<node[^>]*>", data):
        tag = m.group(0)
        def ambil(k):
            mm = re.search(k + r'="([^"]*)"', tag)
            return mm.group(1) if mm else ""
        teks, desc, klik = ambil("text"), ambil("content-desc"), ambil("clickable") == "true"
        b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', tag)
        if not b or not (teks or desc or klik):
            continue
        x1, y1, x2, y2 = map(int, b.groups())
        label = teks or desc
        out.append(f"@{ (x1+x2)//2 },{ (y1+y2)//2 } {'[KLIK] ' if klik else ''}{label}".rstrip())
    ringkas = "\n".join(out)
    print(f"# {len(out)} elemen berguna dari {len(data)} byte XML -> {len(ringkas)} byte ringkasan")
    print(ringkas)


def cmd_kotak(path: str, kolom: int = 6, baris: int = 12) -> None:
    from PIL import Image, ImageDraw
    img = Image.open(path).convert("RGB")
    W, H = img.size
    cw, ch = W // kolom, H // baris
    d = ImageDraw.Draw(img)
    sel = {}
    n = 0
    for r in range(baris):
        for c in range(kolom):
            n += 1
            x1, y1, x2, y2 = c * cw, r * ch, (c + 1) * cw, (r + 1) * ch
            d.rectangle([x1, y1, x2, y2], outline=(255, 60, 60), width=3)
            d.rectangle([x1 + 4, y1 + 4, x1 + 54, y1 + 34], fill=(255, 60, 60))
            d.text((x1 + 10, y1 + 10), str(n), fill=(255, 255, 255))
            sel[str(n)] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "cx": (x1 + x2) // 2, "cy": (y1 + y2) // 2}
    p = Path(path)
    gambar = p.with_name(p.stem + "-kotak.png")
    peta = p.with_name(p.stem + "-kotak.json")
    img.save(gambar)
    peta.write_text(json.dumps({"lebar": W, "tinggi": H, "kolom": kolom, "baris": baris, "sel": sel}, indent=1))
    print(f"gambar: {gambar}\npeta  : {peta}\n{kolom}x{baris} = {n} sel, ukuran sel ±{cw}x{ch}px")


def cmd_ketuk(peta_path: str, nomor: str, sub: int = 5) -> None:
    peta = json.loads(Path(peta_path).read_text())
    s = peta["sel"][str(nomor)]
    # sub-posisi pola keypad 1-9 di dalam sel (1=kiri-atas ... 5=tengah ... 9=kanan-bawah)
    fx = {1: .25, 2: .5, 3: .75, 4: .25, 5: .5, 6: .75, 7: .25, 8: .5, 9: .75}[sub]
    fy = {1: .25, 2: .25, 3: .25, 4: .5, 5: .5, 6: .5, 7: .75, 8: .75, 9: .75}[sub]
    x = int(s["x1"] + (s["x2"] - s["x1"]) * fx)
    y = int(s["y1"] + (s["y2"] - s["y1"]) * fy)
    print(f"{x} {y}")


def cmd_ocr(path: str) -> None:
    try:
        from rapidocr_onnxruntime import RapidOCR
        hasil, _ = RapidOCR()(path)
        if hasil:
            for kotak, teks, _percaya in hasil:
                xs = [t[0] for t in kotak]; ys = [t[1] for t in kotak]
                print(f"@{int(sum(xs)/len(xs))},{int(sum(ys)/len(ys))} {teks}")
            return
        print("(OCR tidak menemukan teks)")
        return
    except ImportError:
        pass
    r = subprocess.run(["tesseract", path, "stdout", "--psm", "11"],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        print(r.stdout.strip())
        return
    print("Tidak ada mesin OCR: pasang rapidocr-onnxruntime (pip) atau tesseract.", file=sys.stderr)
    sys.exit(3)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    if a[0] == "ringkas":
        cmd_ringkas(a[1])
    elif a[0] == "kotak":
        cmd_kotak(a[1], int(a[2]) if len(a) > 2 else 6, int(a[3]) if len(a) > 3 else 12)
    elif a[0] == "ketuk":
        cmd_ketuk(a[1], a[2], int(a[3]) if len(a) > 3 else 5)
    elif a[0] == "ocr":
        cmd_ocr(a[1])
    else:
        print(f"subperintah tidak dikenal: {a[0]}", file=sys.stderr)
        sys.exit(2)
