# advance/ — Ruang Pengembangan Menuju v2

Semua yang ada di folder ini adalah **peningkatan yang masih tahap
pengembangan**: sudah ditulis dan ditata, **belum** menjadi bagian resmi
muse-droid, dan **belum semuanya diuji di perangkat**. Aturannya sederhana:

- Tidak ada skrip produksi (`scripts/`) yang bergantung pada isi folder ini.
- Sesuatu lulus dari sini hanya setelah diuji langsung di HP dan terbukti —
  lalu ia dipindah ke `scripts/`/`docs/` dan dicatat di riwayat versi.
- Urutan uji yang disarankan mengikuti nomornya.

## Papan status

| # | Peningkatan | Isi | Bentuk | Bukti yang dibutuhkan untuk lulus |
|---|---|---|---|---|
| 01 | Server residen di HP (Jalan 1) | `01-server-residen/` | Skrip + klien Python | **Teruji ✓ 8 Okt** — resep benar dari sumber uiautomator2 (u2.jar + com.wetest.uia2.Main): PING 0,01 dtk, DUMP 0,56 dtk (±20–35× cara lama); `mulai-server.sh` ditulis ulang. PENGUJIAN.md Fase 8 |
| 02 | Crop fokus untuk vision | `02-crop-fokus.py` | Alat Python (PIL) | **Teruji ✓ 8 Okt** — 2 target berglif jelas: selisih 8px & 23px (ambang 30px); kasus tepi: node teks selebar baris. PENGUJIAN.md Fase 4 |
| 03 | Peta layar tersimpan | `03-peta-layar.py` | Alat Python + JSON | **Teruji ✓ 8 Okt** — catat/cari/lupakan persis; ketuk basi (daftar dinamis) pulih lewat alur resminya. PENGUJIAN.md Fase 5 |
| 04 | Router model bertingkat | `04-router-model.py` | Kebijakan + klasifikasi | **DIUJI 7 Okt: LULUS BERSYARAT** — klasifikasi 10/10; RUTIN & VISION terhubung nyata; tier RENCANA `utama` butuh anggaran token besar. PENGUJIAN.md Fase 7 |
| 05 | Batch banyak misi satu sesi | `05-batch.sh` | Skrip Termux | **Teruji ✓ 8 Okt** — 3/3 beres; batch 93 dtk vs 97 dtk terpisah (dinding). PENGUJIAN.md Fase 3 |
| 06 | Penjaga prasyarat (watchdog) | `06-penjaga.sh` | Skrip Termux | **LULUS UJI PERANGKAT 7 Okt** — sshd dibunuh paksa, hidup lagi ≤1 siklus, status akurat. PENGUJIAN.md Fase 1 |
| 07 | Memori resep | `07-resep.py` + `resep/` | Alat Python | **Teruji ✓ 8 Okt** — resep "buka-layar" dipakai ulang (parameter Bluetooth) & beres. PENGUJIAN.md Fase 6 |
| 08 | Basis pengetahuan per aplikasi | `08-pengetahuan/` | Berkas catatan | Terisi dari pengalaman; dibaca sebelum misi |
| 09 | Perencana + dry-run | `09-perencana.py` | Alat Python | **Teruji ✓ 8 Okt** — rantai penuh susun→uji (negatif tertangkap)→jalan→simpan→pakai→jalan. PENGUJIAN.md Fase 6 |
| 10 | Aplikasi pendamping Shizuku (Jalan 2) | `10-aplikasi-pendamping/` | Kerangka Kotlin + `build.sh` | **Terpasang ✓ 8 Okt** — PING → PONG di 127.0.0.1:19101; 3 cacat build diperbaiki (UI, artefak aidl, izin INTERNET); DUMP stub; izin Shizuku menunggu restart server. PENGUJIAN.md Fase 9 |

## Kenapa tidak langsung jadi v2?

Karena v1 mengajarkan satu hal: yang membuat alat ini bisa dipercaya bukan
banyaknya fitur, melainkan bahwa **setiap klaimnya pernah dibuktikan di
perangkat nyata** (lihat docs/09 & docs/10 — semua angka di sana hasil uji).
Folder ini menjaga standar itu: ide boleh masuk cepat, klaim "sudah bisa"
harus menunggu bukti.
