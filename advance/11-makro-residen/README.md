# 11 — Runner Makro Residen + Kueri Terarah

Penggabungan roadmap `LOG-PEMBAHARUAN.md` §8 butir 1 & 2:

- **Butir 1 (makro penuh di perangkat)**: `misi-cepat.py` adalah SATU
  proses Python yang hidup selama misi — menghilangkan spawn `python3`
  per panggilan RPC yang dilakukan `eksekutor.sh` (±100–300 ms/langkah),
  polling TUNGGU 250 ms (dari 1 dtk), dan tunggu-perubahan-hierarki
  (≤1,2 dtk) menggantikan sleep datar 1 dtk sesudah ketukan.
- **Butir 2 (kueri terarah)**: dump tidak pernah keluar dari proses;
  pencarian teks mengurai pohon di tempat dan hanya memakai bounds-nya.

Bahasa misi kompatibel penuh dengan `.job` eksekutor lama
(`misi-uji-standar.job` di folder ini adalah misi benchmark bersama).
Setiap langkah dilaporkan dengan durasinya — perbandingan sebelum/
sesudah tinggal membaca log kedua runner pada misi yang sama.

Perbedaan gerbang: misi-cepat **tidak lagi mewajibkan rish** — server
residen yang sehat cukup (mode server); rish menjadi cadangan
(mode jembatan, polling dilambatkan otomatis ke 8 dtk sesuai pelajaran
Fase 6). Penjaga TARGET dipertahankan persis.

## Hasil uji

*(diisi sesudah pengujian perangkat — angka dari log misi standar yang
sama untuk kedua runner, pada sesi yang sama)*

| Misi standar 9 langkah | Total | Catatan |
|---|---|---|
| eksekutor.sh (sebelum) | **47,8 dtk** | 1 putaran; TEMPEL menyumbang 23,0 dtk; TOMBOL back ±3,5 dtk/langkah |
| misi-cepat.py (sesudah) | **22,3 / 22,4 dtk** | 2 putaran konsisten; TEMPEL 11,7 dtk; KETUK_TEKS 0,69 dtk; TUNGGU_TEKS 0,33 dtk; TOMBOL back 0,5–1,1 dtk |

Sisa terbesar sesudah paket ini adalah TEMPEL di formulir berkeyboard
(11,7 dtk) — didominasi dump berulang atas halaman berat (±130 KB,
lantai UiAutomation ±0,8 dtk per dump). Tuas berikutnya memang butir 3
(set-text) dan butir 4 (pohon tersimpan) di roadmap jurnal.

## Berkas

- `misi-cepat.py` — runner-nya (di HP: `~/muse-droid/misi-cepat.py`).
- `misi-uji-standar.job` — misi benchmark (navigasi Pengaturan; aman).

## ERA u2 — JANGAN dipakai saat pohon terikat (A4, 9 Okt 2026)
misi-cepat.py bekerja lewat server u2/uiautomator; dump-nya MELEPAS
ikatan pohon (LayananAkses). Runner sekarang MENOLAK jalan (exit 3,
pesan "DITOLAK (A4)") bila 19102 menjawab PONG. Untuk misi saat pohon
terikat: pakai misi-ad-hoc.py (advance/16, mode pohon).
