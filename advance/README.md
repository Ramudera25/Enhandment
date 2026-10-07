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
| 01 | Server residen di HP (Jalan 1) | `01-server-residen/` | Skrip + klien Python | Server nyala via rish; dump < 500 ms; stabil 1 jam |
| 02 | Crop fokus untuk vision | `02-crop-fokus.py` | Alat Python (PIL) | Potongan + peta balik diuji ke foto nyata |
| 03 | Peta layar tersimpan | `03-peta-layar.py` | Alat Python + JSON | Ketuk dari peta berhasil di 3 layar berbeda |
| 04 | Router model bertingkat | `04-router-model.py` | Kebijakan + klasifikasi | Tersambung ke rantai model & terukur hematnya |
| 05 | Batch banyak misi satu sesi | `05-batch.sh` | Skrip Termux | 3 misi dalam 1 batch, ringkasan benar |
| 06 | Penjaga prasyarat (watchdog) | `06-penjaga.sh` | Skrip Termux | sshd mati terdeteksi & dinyalakan ulang |
| 07 | Memori resep | `07-resep.py` + `resep/` | Alat Python | Resep dipakai ulang untuk misi nyata & beres |
| 08 | Basis pengetahuan per aplikasi | `08-pengetahuan/` | Berkas catatan | Terisi dari pengalaman; dibaca sebelum misi |
| 09 | Perencana + dry-run | `09-perencana.py` | Alat Python | Dry-run menangkap misi yang salah susun |
| 10 | Aplikasi pendamping Shizuku (Jalan 2) | `10-aplikasi-pendamping/` | Kerangka Kotlin | APK terbangun, izin Shizuku didapat, 1 endpoint setara hp.sh |

## Kenapa tidak langsung jadi v2?

Karena v1 mengajarkan satu hal: yang membuat alat ini bisa dipercaya bukan
banyaknya fitur, melainkan bahwa **setiap klaimnya pernah dibuktikan di
perangkat nyata** (lihat docs/09 & docs/10 — semua angka di sana hasil uji).
Folder ini menjaga standar itu: ide boleh masuk cepat, klaim "sudah bisa"
harus menunggu bukti.
