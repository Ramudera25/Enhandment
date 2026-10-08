# DESAIN V3 — Pohon UI Tersimpan (observasi tanpa dump)

> Dokumen DESAIN — belum dibangun, belum diuji. Ditulis 8 Okt 2026 sebagai
> bahan lompatan besar berikutnya (roadmap `LOG-PEMBAHARUAN.md` §8 butir 4).
> Status: menunggu keputusan Travis (syarat aktivasi satu kali oleh
> pemilik HP ada di §5).
>
> Catatan penamaan (8 Okt 2026): "V3" pada judul ini adalah nomor
> generasi *desain eksekutor*, bukan versi rilis proyek. Versi proyek
> diatur di `14-versi-dan-konfigurasi/VERSI.md` (saat ini V3.0); bila
> desain ini dibangun & teruji, ia terbit sebagai **V4.0**.

## 1. Masalah yang diserang

Pengukuran berulang membuktikan: **langkah termahal dalam satu siklus
otomasi adalah mengambil pohon UI** (dump UiAutomation 0,5–0,95 dtk di
Samsung A13; kasus formulir berkeyboard ±0,8 dtk untuk dump tunggal).
Klik hanya ±0,16 dtk. Semua kerangka otomasi (termasuk Appium) duduk di
atas mekanisme yang sama — dump adalah permintaan *sinkron* ke
UiAutomation yang menyusun ulang seluruh hierarki jendela dari nol
setiap kali diminta. Tidak ada optimasi transport yang bisa menembusnya.

Satu-satunya jalan menembus lantai ini: **berhenti meminta pohon dari
nol**. Pelihara salinannya, perbarui dari peristiwa.

## 2. Idenya

Android menyediakan **AccessibilityService**: layanan yang menerima
*peristiwa* perubahan UI (jendela berubah, konten berubah, fokus
berpindah) dan dapat membaca hierarki jendela aktif lewat
`rootInActiveWindow`. Sebuah layanan yang selalu hidup dapat:

1. Memelihara **salinan pohon UI terakhir** di memori (model node:
   paket, class, teks, content-desc, bounds, clickable, focused,
   editable).
2. Memperbaruinya secara **inkremental** setiap peristiwa aksesibilitas
   tiba (debounce 30–50 ms), bukan menyusun ulang atas permintaan.
3. Menjawab kueri agen ("di mana teks X", "apakah teks Y tampil",
   "paket apa di depan") **dari salinan** — latensi milidetik, tanpa
   menyentuh UiAutomation sama sekali.

Dump penuh tetap tersedia sebagai **cadangan kebenaran** bila salinan
diragukan (lihat §4).

## 3. Arsitektur yang diusulkan

```
┌──────────────────────── HP ANDROID ────────────────────────┐
│ Aplikasi pendamping (yang sudah ada, diperluas):           │
│  ├─ LayananAkses (AccessibilityService)                    │
│  │    • onAccessibilityEvent → jadwalkan segarkan salinan  │
│  │    • segarkan: rootInActiveWindow → model pohon         │
│  │    • simpan: pohon + stempel waktu + nomor urut versi   │
│  ├─ Penyaji lokal (socket 127.0.0.1:19102, JSON):          │
│  │    • CARI "teks"     → bounds | TIDAK-ADA               │
│  │    • TEKS? "teks"    → YA/TIDAK + umur salinan (ms)     │
│  │    • PAKET?          → paket jendela depan              │
│  │    • POHON           → XML salinan (untuk cadangan)     │
│  └─ UserService Shizuku (sudah ada) → tangan: klik/geser/  │
│     tombol tetap lewat u2/rish seperti sekarang            │
│                                                            │
│ Konsumen: misi-cepat.py (advance/11) — mode kueri:         │
│  observasi → Penyaji lokal; hanya bertindak lewat tangan;  │
│  verifikasi pasca-langkah tetap dari salinan yang segar.   │
└────────────────────────────────────────────────────────────┘
```

Kenapa di aplikasi pendamping: ia sudah terpasang, sudah punya jalur
build (`build.sh`), sudah dikenal Shizuku. Layanan aksesibilitas adalah
komponen terpisah di APK yang sama — tidak mengubah UserService yang
sudah teruji.

## 4. Aturan kebenaran (bagian terpenting)

Salinan bisa basi — peristiwa bisa terlewat, animasi bisa mengecoh.
Desain ini hanya aman dengan aturan keras:

- **Umur salinan selalu dilaporkan** bersama setiap jawaban. Konsumen
  menolak jawaban berumur > 500 ms untuk langkah yang mengubah layar.
- **Verifikasi pasca-ketuk wajib dari salinan versi baru** (nomor urut
  naik), bukan dari salinan yang sama dengan sebelum ketuk. Bila versi
  tidak naik dalam 1,2 dtk → jatuh ke dump UiAutomation (cadangan).
- **Langkah destruktif/sensitif tidak pernah** diputuskan dari salinan:
  kirim formulir, konfirmasi pembayaran, hapus — wajib dump segar atau
  screenshot verifikasi, sama seperti disiplin sekarang.
- **TARGET guard membaca paket dari salinan** (murah, selalu segar
  untuk jendela depan) + dikonfirmasi dump pada langkah buta pertama.
- Bila layanan mati/dinonaktifkan: sistem **turun kelas dengan jujur**
  ke mode sekarang (dump per langkah) dan melaporkannya — tidak pura-
  pura cepat.

## 5. Syarat & biaya

- **Satu tindakan pemilik HP, satu kali**: Pengaturan → Aksesibilitas →
  Aplikasi terpasang → aktifkan layanan pendamping. Android menampilkan
  peringatan baku (layanan bisa membaca isi layar) — wajar, dan memang
  itu pekerjaannya; layanan ini hanya berjalan lokal, tanpa jaringan
  keluar (socket hanya 127.0.0.1, sama seperti pendamping sekarang).
- **Pembangunan**: komponen terbesar sejauh ini di proyek — perkiraan
  1–2 sesi kerja: layanan + model pohon + penyaji + integrasi
  misi-cepat + rangkaian uji (akurasi bounds vs dump, kebasian,
  ketahanan baterai).
- **Risiko**: konsumsi baterai dari penyegaran per peristiwa (dimitigasi
  debounce + hanya menyalin jendela aktif); beberapa aplikasi (bank,
  layar FLAG_SECURE) memang mengaburkan hierarki dari aksesibilitas —
  di sana dump pun terbatas; fallback tetap berlaku.
- **Privasi**: salinan pohon hanya di memori proses, tidak ditulis ke
  berkas, tidak dikirim keluar HP kecuali potongan bounds/teks yang
  diminta misi — sama seperti dump hari ini yang memang sudah dibaca
  agen.

## 6. Target angka (untuk dibuktikan, bukan dijanjikan)

| Metrik | Sekarang | Target v3 |
|---|---|---|
| Observasi "di mana teks X" | 0,5–0,95 dtk (dump) | **< 0,05 dtk** (salinan) |
| Siklus lihat→ketuk→lihat (halaman wajar) | 0,83–0,97 dtk | **±0,2 dtk** |
| Misi standar 10 langkah (advance/11) | diukur di pengujian 11 | turun ≥ 3× |
| Dump penuh | tetap ada | hanya cadangan/verifikasi |

## 7. Rencana uji (bila disetujui)

1. Akurasi: 20 kueri CARI pada 5 aplikasi — bounds dari salinan vs dump
   UiAutomation harus sama persis (toleransi 0 px untuk node yang sama).
2. Kebasian: ketuk yang mengubah layar → versi salinan naik & jawaban
   pasca-ketuk benar dalam ≤ 300 ms pada 9 dari 10 percobaan.
3. Ketahanan: layanan hidup 24 jam (foreground notification tidak
   dipakai; andalkan prioritas aksesibilitas) + konsumsi baterai
   tercatat.
4. Turun kelas: nonaktifkan layanan di tengah misi → runner melaporkan
   mode dump dan misi tetap beres.
5. Benchmark misi standar yang sama dengan advance/11, sebelum/sesudah.

---

*Desain ini sengaja ditulis sebelum ada kode: keputusan terbesarnya
(aturan kebenaran §4) adalah keputusan desain, bukan keputusan
implementasi.*
