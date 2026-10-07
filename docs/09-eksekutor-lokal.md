# 09 — Eksekutor Lokal (Jalan 0)

> 📦 **Bahasa bayi:** Selama ini sopir menelepon satpam untuk setiap satu ketukan:
> "Satpam, tolong ketuk ini." — "Sudah." — "Satpam, sekarang ketuk itu." Telepon
> terus. Eksekutor lokal mengubahnya: sopir menyerahkan **satu surat tugas berisi
> seluruh misi**, dan satpam menjalankannya sendiri di dalam rumah, lalu melapor
> "beres" atau "macet di langkah sekian".

## Masalah yang diselesaikan

Loop kendali biasa (bab 03) membayar ongkos penuh di setiap langkah: satu koneksi
SSH + satu putaran berpikir model, bahkan untuk hal mekanis seperti *menunggu
tombol muncul*. Padahal sebagian besar langkah misi itu tidak butuh otak — hanya
butuh kesabaran lokal. Eksekutor lokal memindahkan kesabaran itu ke dalam HP.

```
SEBELUM:  agent ──SSH──► ketuk ──SSH──► baca ──SSH──► tunggu ──SSH──► ketuk …  (per langkah)
SESUDAH:  agent ──SSH 1×──► [ berkas tugas ] ──► eksekutor di HP menjalankan semuanya
                                                    └──► laporan .hasil (per langkah)
```

## Bentuknya

Satu skrip: `scripts/eksekutor.sh`, berjalan **di dalam Termux**. Dua mode:

| Mode | Perintah | Perilaku |
|---|---|---|
| Sekali jalan | `eksekutor.sh <berkas.job>` | Jalankan satu tugas, tulis laporan, selesai |
| Residen (jaga) | `eksekutor.sh --jaga` | Pantau `~/muse-droid/antrean/*.job`; tugas yang masuk dijalankan berurutan; hasil dipindah ke `selesai/` atau `gagal/` beserta laporannya |

## Bahasa tugas (.job)

Satu perintah per baris; baris `#` adalah komentar. Disengaja kecil — ini bahasa
surat tugas, bukan bahasa pemrograman.

| Perintah | Arti | Contoh |
|---|---|---|
| `BUKA <paket>/<aktivitas>` atau `BUKA <aksi-intent>` | Buka aplikasi | `BUKA android.settings.SETTINGS` |
| `TUNGGU_TEKS "teks" [detik]` | Tunggu sampai teks tampil di layar (jajak dump lokal) | `TUNGGU_TEKS "Kirim" 30` |
| `KETUK_TEKS "teks"` | Temukan elemen berteks itu, ketuk tengahnya | `KETUK_TEKS "Lamar Sekarang"` |
| `KETUK <x> <y>` | Ketuk koordinat | `KETUK 540 1200` |
| `GESER <x1> <y1> <x2> <y2> [ms]` | Geser/swipe | `GESER 540 1600 540 700` |
| `KETIK "teks"` | Mengetik (spasi diubah `%s` otomatis) | `KETIK "Halo, saya melamar"` |
| `TEMPEL "teks"` | Isi clipboard (Termux:API) lalu paste — untuk teks panjang | `TEMPEL "<surat lamaran utuh>"` |
| `TOMBOL home\|back\|enter\|wakeup` | Tombol sistem | `TOMBOL back` |
| `JEDA <detik>` | Tidur sebentar | `JEDA 3` |
| `FOTO <nama.png>` | Screenshot ke folder `bukti/` | `FOTO bukti-terkirim.png` |
| `CEK_TEKS "teks"` | Nyatakan gagal bila teks tidak tampil | `CEK_TEKS "Lamaran Terkirim"` |

Sifat eksekusi: **fail-fast** — langkah pertama yang gagal menghentikan misi dan
ditulis persis di laporan (langkah ke berapa, perintah apa, kenapa). Tidak ada
misi yang "gagal diam-diam".

Contoh berkas nyata: [../examples/tugas-contoh.job](../examples/tugas-contoh.job)
(misi demo aman: buka Pengaturan → tunggu "Bluetooth" → foto → pulang).

## Memasang & memakai

Di HP (Termux), setelah repo ada di HP:

```bash
pkg install -y python        # dipakai parser koordinat KETUK_TEKS
bash scripts/eksekutor.sh examples/tugas-contoh.job
```

Dari mesin agent, pola titip-tugas untuk mode jaga:

```bash
scp misi-lamaran.job termux-hp:'~/muse-droid/antrean/'
# beberapa saat kemudian:
ssh termux-hp 'ls ~/muse-droid/selesai/ ~/muse-droid/gagal/; cat ~/muse-droid/selesai/*.hasil | tail'
```

## Batasan jujur prototipe ini

- Di dalam HP pun, setiap `TUNGGU_TEKS`/`KETUK_TEKS` tetap memanggil `uiautomator`
  (ratusan milidetik per panggilan) — jauh lebih murah daripada putaran jaringan +
  model, tapi bukan secepat server residen khusus (lihat Jalan 1 di bawah).
- Yang dipindahkan ke lokal adalah **langkah mekanis**. Keputusan tetap di agent:
  ia menyusun misi, membaca laporan, dan menyusun misi berikutnya. Eksekutor yang
  baik itu patuh, bukan pintar.
- `TEMPEL` bergantung Termux:API dan perilaku paste tiap aplikasi berbeda;
  `KETIK` tetap jalan sebagai cadangan.
- `BUKA` membuka aplikasi pada **halaman terakhirnya** (Android memang begitu —
  *task restoration*). Misi yang deterministik menunjuk langsung ke halaman tujuan
  memakai intent dalam, mis. `BUKA android.settings.BLUETOOTH_SETTINGS`. Pelajaran
  ini didapat dari uji langsung: demo yang mengasumsikan Pengaturan selalu mulai
  dari halaman utama gagal — ia terbuka di Opsi pengembang, sisa kunjungan lama.
- Layar terkunci di tengah misi tetap menghentikan misi — fail-fast melaporkannya.
- **Output lewat rish terpotong di ±8 KB.** Dump XML besar tidak boleh dibaca dari
  stdout `rish` — ia harus dipindah sebagai berkas lewat **jembatan folder
  Download** (rish menulis ke Download, sisi Termux membacanya dari sana).
  `dump_xml()` di skrip ini dan perintah `dump` di `hp.sh` sudah memakai pola itu.
  Bukti uji langsung: dump 140 KB terbaca utuh lewat jembatan; lewat stdout hanya
  8 KB yang sampai (elemen layar bawah hilang tanpa pesan kesalahan).

## Ke mana setelah Jalan 0

- **Jalan 1 — adopsi server residen yang sudah matang**: openatx/uiautomator2
  (server HTTP menetap di HP berbasis UiAutomator; aksi semantik tanpa ongkos
  panggil shell berulang) atau Portal milik DroidRun (aksesibilitas + screenshot).
  Dievaluasi setelah pola .job terbukti dipakai.
- **Jalan 2 — aplikasi pendamping Shizuku** (target v2): aplikasi kecil berizin
  Shizuku yang membuka API lokal resmi untuk muse-droid — paling kokoh, paling
  banyak pekerjaan. Lihat diskusi di [07-ai-controller.md](07-ai-controller.md).
