# DESAIN V4.1 — Tangan Aksesibilitas (gestur lewat socket pohon)

> Dokumen DESAIN — ditulis 8 Okt 2026 malam sebagai jawaban tertulis
> atas pertanyaan Travis: "lebih efisien mana agar satu aksi bisa di
> bawah 1 detik?" Status: **DISETUJUI Travis 19.55, DIBANGUN & TERUJI
> malam yang sama — rilis V4.1, PENGUJIAN.md Fase 18.**

## 1. Masalah yang diserang

V4.0 menuntaskan sisi MATA: pohon aksesibilitas menjawab 7–32 ms
(TUNGGU_TEKS 8 ms, CEK_TEKS 7 ms pada uji misi ad-hoc 8 Okt).
Sisa waktu siklus satu aksi kini habis di sisi TANGAN:

- Ketukan masih lewat rish dari VM: RTT SSH + spawn proses ±0,3–0,7 dtk
  per langkah, di atas siklus yang sebenarnya sudah bisa <1 dtk.
- Tangan rish bergantung pada Shizuku — dan Shizuku hidup-mati oleh
  manajemen baterai Samsung (kasus nyata 8 Okt sore: uninstall AutoX.js
  tertahan semata karena Shizuku sedang mati, padahal mata tetap hidup).
- ISI teks via pohon sesekali kalah balapan fokus (catatan poles V4.1
  dari pengujian Fase 15–17).

Animasi aplikasi itu sendiri adalah fisika — tidak bisa diubah dan
bukan target desain ini.

## 2. Idenya

AccessibilityService yang sama (LayananAkses, sudah terikat & teruji
di V4.0) secara API memang boleh mengirim gestur:
`dispatchGesture(GestureDescription)` — ketuk, geser, tekan-lama —
dieksekusi sistem di proses layanan itu sendiri.

Tambahkan perintah gestur ke socket pohon 19102 yang sudah ada:

| Perintah baru | Arti |
|---|---|
| `KETUK <x> <y>` | tap di koordinat (dari bounds simpul TERLIHAT) |
| `KETUK_TEKS <teks>` | CARI simpul terlihat → KETUK pusat bounds-nya, satu panggilan |
| `GESER <x1> <y1> <x2> <y2> <ms>` | swipe |
| `TEKAN_LAMA <x> <y> <ms>` | long-press |
| `ISI2 <teks>` | ISI dengan tunggu fokus/versi (lihat §4) |

Siklus perintah → gestur terkirim → verifikasi dari salinan berversi
NAIK seluruhnya di dalam HP: target terukur **±0,2–0,3 dtk**, tanpa SSH
per langkah, tanpa bergantung Shizuku.

## 3. Aturan yang TIDAK berubah

- **Penjaga target tetap berlaku**: probe paket teratas sebelum ketukan
  pertama sesudah jeda — jangan berebut layar dengan Travis.
- **Verifikasi pasca-ketuk wajib**: gestur hanya dianggap berhasil bila
  `versi` pohon naik / keadaan yang diharapkan terbaca dari salinan
  segar (umur ≤500 ms untuk langkah pengubah layar).
- **Langkah destruktif** (hapus, kirim, uninstall) tetap butuh dump
  segar/screenshot sebagai kebenaran — tidak pernah dari salinan saja.
- **Bounds off-screen tidak dipercaya**: gulir sampai simpul terlihat
  sebelum KETUK_TEKS.
- **Eksklusivitas pohon↔u2 utuh**: desain ini tidak menyentuh u2.

## 4. Poles ISI (balapan fokus)

`ISI2`: fokuskan simpul editable → tunggu `versi` naik ATAU peristiwa
fokus terbaca (maks 600 ms) → baru kirim teks → verifikasi isi terbaca
di salinan. Gagal verifikasi → jatuh ke jalur input-text terverifikasi
(perilaku sekarang), dicatat di log misi.

## 5. Peran kaki sesudah V4.1

- Pohon + tangan aksesibilitas = **kaki utama lengkap** (mata + tangan
  navigasi dalam aplikasi), hidup sesudah reboot tanpa Shizuku.
- rish/Shizuku = tangan istimewa cadangan: `am start`, `pm`,
  screencap, dan hal di luar jangkauan gestur. Shizuku mati tidak lagi
  melumpuhkan navigasi — hanya menunda pekerjaan istimewa (contoh:
  uninstall tetap menunggu Shizuku).
- u2 = cadangan on-demand seperti sekarang. Layanan depan 19101 dan
  penjaga 4 kaki tidak berubah tugasnya.

## 6. Uji penerimaan (mengikuti pola PENGUJIAN.md)

1. Siklus CARI→KETUK_TEKS→verifikasi di aplikasi Pengaturan:
   ≤0,3 dtk median dari 10× percobaan.
2. Misi ad-hoc generik (advance/16) lulus 8/8 dalam mode tangan
   aksesibilitas penuh, Shizuku sengaja dimatikan.
3. ISI2 pada formulir berkeyboard: 10/10 terverifikasi tanpa fallback.
4. Uji negatif: KETUK_TEKS pada teks off-screen harus menolak, bukan
   mengetuk koordinat basi.

## 7. Yang dibutuhkan dari Travis

Satu persetujuan untuk membangun. Tidak ada aktivasi manual baru:
layanan aksesibilitas sudah Enabled & terikat sejak V4.0 — izin gestur
melekat pada layanan yang sama. Build + pasang APK mengikuti jalur
teruji (staging `/data/local/tmp` via rish, perlu satu jendela Shizuku
hidup untuk pemasangan saja).
