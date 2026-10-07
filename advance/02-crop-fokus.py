#!/usr/bin/env python3
"""02-crop-fokus.py — potong screenshot di sekitar titik fokus untuk vision.

Status: PROTOTIPE (folder advance/).

Kenapa: mengirim foto layar utuh (1080x2400) ke model vision itu lambat dan
mahal, padahal yang dicari biasanya satu wilayah kecil. Alat ini memotong
wilayah di sekitar titik (atau sel grid), memperbesarnya, memberi bingkai +
penanda silang di titik fokus, dan — penting — mencatat PEMETAAN BALIK:
koordinat di gambar potongan bisa diterjemahkan kembali ke koordinat layar.

Pakai:
  02-crop-fokus.py <foto.png> <x> <y> [jari-jari-px=350]
Hasil: <foto>-fokus.png dan <foto>-fokus.json (isi: offset & skala).
Terjemahkan titik hasil bacaan vision:
  02-crop-fokus.py --balik <foto>-fokus.json <x-potongan> <y-potongan>  -> "x y" layar
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def fokus(path: str, x: int, y: int, r: int = 350) -> None:
    img = Image.open(path).convert("RGB")
    W, H = img.size
    x1, y1 = max(0, x - r), max(0, y - r)
    x2, y2 = min(W, x + r), min(H, y + r)
    potong = img.crop((x1, y1, x2, y2))
    skala = 2 if potong.width < 700 else 1
    if skala != 1:
        potong = potong.resize((potong.width * skala, potong.height * skala))
    d = ImageDraw.Draw(potong)
    fx, fy = (x - x1) * skala, (y - y1) * skala
    d.ellipse([fx - 14, fy - 14, fx + 14, fy + 14], outline=(255, 60, 60), width=4)
    d.line([fx - 30, fy, fx + 30, fy], fill=(255, 60, 60), width=3)
    d.line([fx, fy - 30, fx, fy + 30], fill=(255, 60, 60), width=3)
    p = Path(path)
    gambar = p.with_name(p.stem + "-fokus.png")
    meta = p.with_name(p.stem + "-fokus.json")
    potong.save(gambar)
    meta.write_text(json.dumps({"offset_x": x1, "offset_y": y1, "skala": skala}))
    print(f"gambar: {gambar} ({potong.width}x{potong.height} dari {W}x{H})\npeta  : {meta}")


def balik(meta_path: str, xp: int, yp: int) -> None:
    m = json.loads(Path(meta_path).read_text())
    print(f"{m['offset_x'] + xp // m['skala']} {m['offset_y'] + yp // m['skala']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--balik":
        balik(a[1], int(a[2]), int(a[3]))
    elif len(a) >= 3:
        fokus(a[0], int(a[1]), int(a[2]), int(a[3]) if len(a) > 3 else 350)
    else:
        print(__doc__)
        sys.exit(2)
