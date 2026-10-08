# 12 — Misi Navigasi Glints

Memindahkan segmen navigasi yang deterministik dari ritme amati→bertindak
jarak jauh (15–25 detik per langkah, didominasi pulang-pergi SSH + screenshot)
ke misi `misi-cepat` yang berjalan di dalam HP (0,3–0,7 detik per langkah).

Latar: eksekusi manual 8 Okt 2026 (2 item antrean HP, 15 menit dinding).
Analisis waktunya menunjukkan biaya terbesar BUKAN di HP, melainkan di loop
observasi agen. Misi ini menyerang tepat biaya itu — tanpa mengambil alih
titik keputusan.

## Isi

- `template-tautan.job` — jalur deep link: satu direktif `TAUTAN` (intent
  VIEW, direktif baru misi-cepat sejak paket ini) membuka URL detail
  lowongan `/opportunities/jobs/...` langsung di aplikasi, lalu menunggu &
  memastikan judul posisi tampil. Berhenti di sana.
- `template-cari.job` — jalur cadangan untuk link explore (tidak diklaim
  aplikasi): buka aplikasi → ketuk Cari (979,160 — HANYA aman di beranda) →
  ketik nama perusahaan → ketuk saran perusahaan → berhenti di halaman hasil
  berisi kartu perusahaan.
- `buat-misi.py` — generator: pilih template dari bentuk `--link`, isi
  placeholder dari `--perusahaan/--cari/--posisi`, tulis `.job` hasil.

## Pembagian kerja (aturan keras)

Misi navigasi TIDAK PERNAH melamar. Yang dikerjakan misi hanya perjalanan
menuju listing. Titik keputusan tetap di agen:

1. Verifikasi kesegaran & kecocokan listing (banner tutup, posisi, lokasi,
   gaji) — dari dump teks; screenshot hanya untuk bukti/anomali.
2. Ganti CV profil (untuk LAMAR 1x TAP) / isi formulir (CHAT UNTUK MELAMAR).
3. KIRIM, verifikasi "Telah Melamar", kirim surat via chat, pembukuan.

## Prasyarat jalur cari

Aplikasi Glints diluncurkan ulang dulu oleh pemanggil (force-stop + start)
supaya misi mulai dari beranda yang bersih — tombol Cari (979,160) hanya
ada di beranda; di halaman detail koordinat yang sama adalah ikon
"Laporkan Loker".

## Pakai

Di HP (folder ini terpasang di `~/muse-droid/navigasi-glints/`):

```sh
python3 ~/muse-droid/navigasi-glints/buat-misi.py \
  --perusahaan "PT. Ungaran Sari Garments" \
  --posisi "Warehouse Coordinator" \
  --link "https://glints.com/id/opportunities/jobs/..."
python3 ~/muse-droid/misi-cepat.py ~/muse-droid/misi/nav-glints.job
```

Log misi-cepat mencatat durasi per langkah — bandingkan dengan ritme manual.
Hasil uji pertama dicatat di `../PENGUJIAN.md` (Fase 12).

## Catatan terukur dari uji pertama (8 Okt, PENGUJIAN.md Fase 12)

- Misi pencarian penuh: **12,6 dtk** untuk 8 langkah — perjalanan yang
  sama secara interaktif memakan ±4–5 menit pulang-pergi.
- `TAUTAN https://glints.com/id` terbuka di browser: klaim aplikasi
  bersifat per-jalur URL, hanya `/opportunities/jobs/...` yang diklaim.
  Karena itu sesudah misi tautan agen WAJIB memastikan paket depan adalah
  `com.glints.candidate` sebelum melanjutkan (CEK_TEKS memeriksa teks,
  bukan paket).
- Di kolom pencarian Glints, menu tempel tekan-lama dan chip clipboard
  TIDAK muncul. KETIK mode server karena itu memakai `input text` via
  rish ke kolom fokus (diverifikasi dari dump) dengan TEMPEL sebagai
  cadangan; TEMPEL mencoba chip clipboard lebih dulu, lalu menu
  tekan-lama (keduanya terverifikasi di kolom chat/formulir).
