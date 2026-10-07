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
| 01 | Server residen di HP (Jalan 1) | `01-server-residen/` | Skrip + klien Python | **DIUJI 7 Okt: BELUM LULUS** — app_process murni crash SIGABRT di HP ini; jalur benar = instrumentasi (sesi khusus). Skrip diperbaiki (berkas lokal, kelas Main, TMPDIR). PENGUJIAN.md Fase 8 |
| 02 | Crop fokus untuk vision | `02-crop-fokus.py` | Alat Python (PIL) | Potongan + peta balik diuji ke foto nyata |
| 03 | Peta layar tersimpan | `03-peta-layar.py` | Alat Python + JSON | Ketuk dari peta berhasil di 3 layar berbeda |
| 04 | Router model bertingkat | `04-router-model.py` | Kebijakan + klasifikasi | **DIUJI 7 Okt: LULUS BERSYARAT** — klasifikasi 10/10; RUTIN & VISION terhubung nyata; tier RENCANA `utama` butuh anggaran token besar. PENGUJIAN.md Fase 7 |
| 05 | Batch banyak misi satu sesi | `05-batch.sh` | Skrip Termux | **UJI 7 Okt TIDAK SAH** — layar HP terkunci di tengah sesi; ulangi setelah layar dibuka. PENGUJIAN.md Fase 3 |
| 06 | Penjaga prasyarat (watchdog) | `06-penjaga.sh` | Skrip Termux | **LULUS UJI PERANGKAT 7 Okt** — sshd dibunuh paksa, hidup lagi ≤1 siklus, status akurat. PENGUJIAN.md Fase 1 |
| 07 | Memori resep | `07-resep.py` + `resep/` | Alat Python | Resep dipakai ulang untuk misi nyata & beres |
| 08 | Basis pengetahuan per aplikasi | `08-pengetahuan/` | Berkas catatan | Terisi dari pengalaman; dibaca sebelum misi |
| 09 | Perencana + dry-run | `09-perencana.py` | Alat Python | Dry-run menangkap misi yang salah susun |
| 10 | Aplikasi pendamping Shizuku (Jalan 2) | `10-aplikasi-pendamping/` | Kerangka Kotlin + `build.sh` | **BUILD LULUS 7 Okt** — APK 700 KB tertandatangani tanpa Gradle; pasang + endpoint menunggu layar dibuka. PENGUJIAN.md Fase 9 |

## Kenapa tidak langsung jadi v2?

Karena v1 mengajarkan satu hal: yang membuat alat ini bisa dipercaya bukan
banyaknya fitur, melainkan bahwa **setiap klaimnya pernah dibuktikan di
perangkat nyata** (lihat docs/09 & docs/10 — semua angka di sana hasil uji).
Folder ini menjaga standar itu: ide boleh masuk cepat, klaim "sudah bisa"
harus menunggu bukti.
