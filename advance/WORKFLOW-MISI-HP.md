# WORKFLOW MISI HP — pola standar sejak V4.1

> Dibakukan 8 Okt 2026 malam sesudah misi uji langsung di aplikasi
> Facebook (telusur grup loker Pati), yang membuktikan alur ini ujung ke
> ujung. Berlaku untuk misi ad-hoc interaktif yang diarahkan dari chat;
> misi terjadwal tetap memakai runner berkas `.job` (`11`, `16`).

## Alur

1. **Probe kaki dulu.** Pohon 19102 (`PING`, catat versi + umur),
   pendamping 19101, rish/Shizuku (`id` → uid=2000), dan level baterai.
   Berkas status penjaga bisa tertinggal — probe langsung adalah
   kebenaran. **Ambang jaga: baterai <20% tanpa cas → berhenti dan lapor
   dulu**; lanjut hanya atas perintah eksplisit pemilik HP.
2. **Penjaga target.** Cek paket teratas (`PAKET?`/dumpsys) sebelum
   sentuhan pertama dan sesudah setiap jeda — pemilik bisa sedang
   memakai HP-nya. Jangan berebut layar tanpa penyerahan eksplisit.
3. **Buka aplikasi via rish** (`am start` / monkey LAUNCHER). rish kini
   khusus tugas yang memang hanya bisa dia: membuka/menghentikan
   aplikasi, `input keyevent`, `screencap`, `pm install/uninstall`,
   menulis `settings`. Bukan lagi tangan per langkah.
4. **Amati berlapis.** Utama: pohon (`PAKET?`, `CARI <teks>`, `POHON`,
   `TEKS?` — milidetik, selalu bawa versi + umur). Bila pohon buta pada
   suatu aplikasi, **screenshot adalah kebenaran** — contoh teruji:
   teks postingan Facebook (komponen Litho) tidak terekspos ke pohon,
   sehingga panen berjalan lewat jalur visual (screenshot per gulir).
   Dump teks juga bisa basi; saat dump dan konteks bertabrakan, percaya
   screenshot.
5. **Bertindak dengan tangan pohon (V4.1).** `KETUK`/`TAHAN`/`GESER`
   lewat socket 19102; koordinat SELALU dari hasil `CARI` pada saat itu
   juga — tidak pernah koordinat hafalan (pelajaran misi Facebook:
   header aplikasi bergeser saat mengkerut, ketukan hafalan mendarat
   di tab lain). `GLOBAL BACK|HOME|RECENTS` untuk navigasi sistem.
   `ISI` untuk teks (layanan menunggu fokus ≤±600 ms). Setiap balasan
   gestur membawa bukti versi salinan NAIK — aksi + verifikasi dalam
   satu perjalanan, dan seluruhnya tetap jalan walau Shizuku mati.
6. **Saring dengan aturan tetap pemilik.** Hasil panen dinilai terhadap
   profil dan mandat yang berlaku (keluarga posisi, gaji minimum,
   wilayah, filter khusus) — termasuk penilaian jujur "kurang cocok".
   Langkah destruktif/pengiriman tidak pernah diputuskan dari salinan
   pohon saja (aturan kebenaran §4 desain pohon).
7. **Tulis hasil + bersihkan.** Deliverable rapi ke folder tujuannya;
   berkas uji (screenshot/dump/skrip sekali pakai) di HP dan di VM
   dibersihkan atau diarsipkan ke folder bukti — tidak berserakan.
8. **Lapor hasil terverifikasi.** Ringkasan + berkas, termasuk batas
   cakupan misi (mis. "baru 1 dari 3 grup ditelusur") dan kegagalan
   apa adanya.

## Pembagian kaki (ringkasan)

| Kaki | Peran sejak V4.1 | Tanpa Shizuku? |
|---|---|---|
| Pohon aksesibilitas 19102 | Mata utama + tangan utama (gestur, ISI, GLOBAL) | — (ia penggantinya) |
| rish/Shizuku | Kunci kontak: buka aplikasi, screenshot, install, settings, pemulihan | — |
| Server u2 9008 | Cadangan on-demand (eksklusif terhadap pohon — jangan bersamaan) | Perlu rish untuk menyalakan |
| Pendamping 19101 + penjaga | Jangkar proses + sembuh sendiri 4 kaki | Penjaga memulihkan via rish |

## Bukti acuan

- Angka gestur & misi uji tangan pohon: `PENGUJIAN.md` Fase 18.
- Desain tangan aksesibilitas: `DESAIN-V4.1-TANGAN-AKSESIBILITAS.md`.
- Protokol pohon + gestur: `15-pohon-ui-aksesibilitas/README.md`.
- Presedensi tangan runner: `16-misi-ad-hoc/README.md`.
