# MULAI DARI SINI — Panduan Operator Enhandment

Dokumen ini pintu masuk tunggal untuk siapa pun — manusia atau agen
AI — yang akan MENGOPERASIKAN Enhandment. Baca ini lebih dulu,
seluruhnya, sebelum menyentuh perangkat. Isinya diringkas dari
keadaan terverifikasi di perangkat nyata (Samsung Galaxy A13,
Android 14) per 11 Oktober 2026.

## 1. Peta satu menit

Enhandment = cara mengendalikan HP Android dari jarak jauh TANPA
root, memakai layanan aksesibilitas sebagai tangan utama.

Pemainnya:

- **Pohon UI** (layanan aksesibilitas di aplikasi pendamping,
  soket 127.0.0.1:19102 di HP): membaca layar sebagai daftar simpul
  (teks, posisi, bisa-diketuk) dan mengeksekusi ketukan/geser/isi.
  Ini KAKI UTAMA. Perintahnya satu baris per koneksi: PING, PAKET?,
  TEKS?, CARI, POHON, KETUK, TAHAN, GESER, ISI, GLOBAL, TOMBOL,
  BINGKAI/AMBIL (foto layar), BACA (OCR di perangkat — lambat,
  cadangan terakhir).
- **Runner misi** (`16-misi-ad-hoc/misi-ad-hoc.py`, berjalan di
  Termux HP): menjalankan berkas .job baris demi baris dalam MODE
  POHON. Format v2 menambahkan klausa `VERIFIKASI` sesudah langkah
  pengubah layar (TEKS_ADA / TEKS_TIDAK_ADA / PAKET / HALAMAN /
  BACA_ADA, varian LEMBUT = peringatan saja), direktif `ANGGARAN
  <langkah> <detik>`, dan kartu aplikasi yang dibaca saat BUKA.
- **OCR server** (`15-pohon-ui-aksesibilitas/baca-server.py`,
  berjalan di komputer operator): foto layar dari BINGKAI dibaca
  PP-OCRv5 dalam ±2–3 detik. Inilah jalur baca utama untuk
  permukaan web/kanvas. (BACA di perangkat terukur 19–40 detik —
  jangan jadikan jalur utama.)
- **Pohon sintetis** (`15-pohon-ui-aksesibilitas/pohon-sintetis.py`):
  menyusun simpul perkiraan dari foto (detektor MIT + OCR) bila
  pohon asli kosong. Kedudukan: penasihat, bukan hakim ketuk.
- **Grounding** (`15-pohon-ui-aksesibilitas/grounding.py`): lapis
  terakhir — foto + perintah bahasa alami → satu titik koordinat,
  dilayani model UI-TARS-2B di mesin pendamping (f4) lewat
  llama.cpp. Model tidak pernah bisa abstain; verifikasi sesudah
  ketuk tetap wajib.
- **rish/Shizuku**: kunci kontak + kotak perkakas SAJA — pasang
  aplikasi, tulis setelan aksesibilitas, force-stop, diagnostik.
  Bukan tangan harian.
- **Server u2 (port 9008)**: CADANGAN on-demand. Sesi
  UiAutomation-nya MENUTUP layanan aksesibilitas selama aktif —
  pohon dan u2 TIDAK PERNAH hidup bersamaan.

## 2. Prasyarat

Di HP: Termux (+ `sshd` dijalankan manual sesudah reboot),
Shizuku (di-Start manual sesudah reboot; pairing tersimpan),
aplikasi Tailscale (Connected), aplikasi pendamping terpasang dan
layanan aksesibilitasnya terikat, folder `~/muse-droid/` berisi
runner + klien (`uji-v44.py`, `ambil-bingkai.py`, `baca-layar.py`)
+ folder `kartu/`.
Di operator: akses SSH ke Termux HP; untuk OCR server sebuah venv
RapidOCR (PP-OCRv5 Latin); untuk grounding sebuah mesin CPU kelas
4c/8t + RAM ≥8 GB bebas yang menjalankan llama-server.

Ritual pasca-reboot HP (sisi manusia): colok cas → buka Termux →
Shizuku Start → Tailscale Connected → ketik `sshd`.

## 3. Cara menjalankan misi

1. Klaim sesi: tulis penanda `~/muse-droid/.sesi-aktif` di HP.
2. Probe SEBELUM menyentuh layar: PING menjawab? Versi pohon
   BERGERAK (bukan hanya menjawab)? Paket teratas apa? Baterai?
   **Bila manusia sedang memakai HP-nya sendiri, berhenti** —
   paket depan yang berpindah-pindah di luar perintahmu adalah
   tanda tangan manusia.
3. Jalankan: `cd ~/muse-droid && python3 misi-ad-hoc.py <misi>.job`
4. Baca keluaran + berkas `.hasil`: setiap langkah pengubah layar
   harus punya baris BUKTI dengan `verifikasi_ok: true`.
5. Tutup sesi: hapus penanda `.sesi-aktif`.

Misi pertama yang aman untuk operator baru:
`11-makro-residen/misi-uji-standar.job` — membuka Pengaturan Wi-Fi,
mengisi formulir Add network dengan teks uji, lalu mundur tanpa
menyimpan. Hasil sehat: 9/9 langkah, semua BUKTI ok, ±7 detik.

## 4. Aturan keras (melanggar = berhenti dan lapor)

1. Pohon adalah hakim ketuk. Foto/OCR/sintetis/grounding hanya
   penasihat. `ok=false` dari layanan DIPERCAYA — jangan diulang
   dengan jalur lain.
2. Mode pohon TIDAK PERNAH memakai dump UiAutomation / u2 / rish
   sebagai fallback aksi. Gagal = berhenti jujur.
3. Sesudah BUKA, yang diverifikasi adalah HALAMAN (isi pohon /
   jangkar kartu), bukan sekadar paket teratas — aplikasi yang
   sudah terbuka di halaman lain menelan intent BUKA.
4. Dinginkan aplikasi target (force-stop via rish) sebelum misi,
   atau verifikasi halamannya dari isi pohon.
5. Verifikasi menilai dengan jendela tenang 3 detik (penilaian
   diulang, AKSI tidak). Jangan "memperbaiki" kegagalan verifikasi
   dengan mengulang aksinya.
6. Pasang APK hanya lewat staging `/data/local/tmp/` (salin dari
   /sdcard via rish lalu `pm install` di sana); jalur /sdcard
   langsung gagal diam-diam. Build rilis WAJIB ditandatangani
   keystore kanonis proyek (lihat `10-aplikasi-pendamping/`).
7. Jendela FLAG_SECURE menolak tangkapan layar — itu batas sah
   desain Android, bukan untuk diakali.
8. Jangan pernah menjalankan `hermes setup` penuh di HP dan
   jangan menyalakan tunnel/reverse-SSH apa pun tanpa perintah
   eksplisit pemilik perangkat.
9. Kredensial tidak pernah ditulis ke repo, log, atau chat —
   dipakai transien saja.
10. Semua tangkapan layar bukti masuk folder `bukti/` (HP) /
    `bukti-layar/` (operator), tidak berserakan.

## 5. Bila pohon mati (ringkasan pemulihan)

Gejala: soket 19102 menolak / versi tidak bergerak. Resep
terverifikasi: force-stop aplikasi pendamping via rish →
jalankan MainActivity-nya → di Pengaturan Aksesibilitas buka
layanan "muse-droid Pohon UI" → siklus saklar mati→nyala → ikatan
terjadi ±35 detik → uji PING + versi BERGERAK. Sesudah
uninstall+install ulang, tulis ulang
`enabled_accessibility_services` via rish dulu, lalu siklus
saklar UI tetap wajib. Dialog "Allow full control" hanya bisa
diketuk manusia. Koordinat menu di resep ini khas One UI Samsung
— di merek lain, cari baris layanannya secara visual dari pohon/
bingkai, jangan hafalkan koordinat.

## 6. Instruksi tempel untuk agen AI lain

Salin blok ini sebagai instruksi pembuka saat menugaskan agen
lain (Hermes, opencode, pi, atau lainnya) mengoperasikan sistem
ini:

---
Kamu mengoperasikan Enhandment (kendali HP Android via layanan
aksesibilitas). SEBELUM bertindak: (1) baca
`advance/MULAI-DARI-SINI.md` di repo ini sampai selesai; (2) baca
`advance/PENGUJIAN.md` untuk keadaan terverifikasi terakhir;
(3) laporkan ringkasan pemahamanmu dalam 5 baris: kaki utama,
mode misi, tiga aturan keras yang paling relevan dengan tugas,
dan prasyarat yang belum terpenuhi. JANGAN menjalankan apa pun
sebelum ringkasan itu. Selama bekerja: pohon adalah hakim ketuk;
gagal verifikasi = berhenti dan lapor dengan bukti, tanpa
coba-ulang aksi dan tanpa fallback dump/u2/rish; probe paket
teratas sebelum ketukan pertama sesudah jeda apa pun; klaim
sesi dengan penanda `.sesi-aktif`. Laporan akhir per butir:
status, jalur artefak, bukti angka (versi pohon, latensi,
verifikasi_ok), dan satu baris "Yang belum".
---

## 7. Portabilitas (jujur)

Arsitekturnya generik Android: layanan aksesibilitas, Termux,
Shizuku, dan soket lokal tidak bergantung merek. Lantai praktis
sistem penuh: **Android 11+** (API tangkapan layar aksesibilitas
butuh API 30+). Yang BARU terverifikasi hanya Samsung A13 /
One UI — harapkan penyesuaian per merek: daftar putih baterai
(pembunuh proses agresif berbeda tiap OEM), tata letak menu
Pengaturan Aksesibilitas (koordinat resep pemulihan khas
Samsung), perilaku papan ketik, dan kecepatan OCR di perangkat
(bergantung SoC). Di perangkat kedua, perlakukan
`misi-uji-standar.job` sebagai gerbang penerimaan sebelum misi
apa pun.

## 8. Peta berkas

- Aplikasi pendamping + build: `10-aplikasi-pendamping/`
- Runner misi + harness luring: `16-misi-ad-hoc/`
  (`uji-pengawas-luring.py`, 21 asersi)
- Klien pohon + perkakas server: `15-pohon-ui-aksesibilitas/`
  (`ambil-bingkai.py`, `baca-layar.py`, `baca-server.py`,
  `pohon-sintetis.py`, `grounding.py`)
- Kartu aplikasi: `08-pengetahuan/kartu/<paket>.md`
- Desain per kemampuan: `DESAIN-*.md` di folder ini
- Catatan pengujian (bukti, bukan klaim): `PENGUJIAN.md`
