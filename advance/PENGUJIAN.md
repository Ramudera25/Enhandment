# PENGUJIAN.md — Rencana & Hasil Uji muse-droid

Disetujui Travis 7 Okt 2026 (23.04: "lets go, eksekusi semua pengujiannya sekarang").

## Aturan main

- Urutan dari risiko terkecil ke terbesar. Semua uji memakai misi aman
  (Pengaturan, catatan, demo) — tidak ada lamaran sungguhan, tidak mengubah data.
- Kejujuran laporan adalah bagian dari uji: alat yang melaporkan sukses padahal
  gagal = GAGAL.
- Gagal boleh diperbaiki & diuji ulang maks 2× dalam sesi yang sama; selebihnya
  diparkir dengan catatan sebab.
- LULUS → dipindah ke `scripts/`+`docs/` (keluar dari advance/). Belum → tetap di
  sini dengan catatan hasil.

## Fase

- **Fase 0** Persiapan & baseline — latensi dump cara lama (3×) + waktu misi demo.
- **Fase 1** 06 Penjaga — `cek` akurat; sshd dimatikan sengaja harus dinyalakan
  ulang otomatis; file status akurat.
- **Fase 2** Sisa v1 — TEMPEL (teks tampil persis per karakter) + mode `--jaga`
  (2 misi beres ke `selesai/`, 1 mustahil ke `gagal/`, tanpa campur tangan).
- **Fase 3** 05 Batch — 3 misi satu sesi; ringkasan benar; total lebih cepat dari
  terpisah; jaga-layar dilepas di akhir.
- **Fase 4** 02 Crop fokus — 3 target; titik balik vs kebenaran XML selisih ≤ 30px.
- **Fase 5** 03 Peta layar — 3/3 ketuk dari peta benar; alur elemen basi
  (lupakan → catat ulang) berjalan.
- **Fase 6** Rantai 09+07 — susun → dry-run (termasuk 1 negatif tertangkap) →
  eksekusi → simpan resep → pakai ulang dengan parameter lain.
- **Fase 7** 04 Router — 10 langkah campuran ke rantai model nyata; klasifikasi
  10/10; rutin tak pernah naik kelas; angka hemat terukur.
- **Fase 8** 01 Server residen — dump rata-rata < 500 ms; stabil 60 menit;
  fallback ke cara lama terbukti saat server dimatikan.
- **Fase 9** 10 Aplikasi pendamping — APK terbangun dari kerangka; izin Shizuku;
  endpoint PING + DUMP setara hp.sh.

## Hasil — sesi uji 7→8 Okt 2026 (mulai 23.05 WIB)

**Fase 0 SELESAI.** Baseline cara lama dari VM: dump 160 KB = 17,1–23,8 dtk
(rata-rata ±19,6 dtk, 3× ukur); misi demo 6 langkah via 1× SSH = 33 dtk
(uji 21.46) s.d. ±60 dtk (padat). Inilah angka yang harus dikalahkan Jalan 1.

**Fase 1 — 06 penjaga: LULUS UJI PERANGKAT.** `cek` akurat (sshd=HIDUP,
shizuku=HIDUP); sshd dimatikan paksa → penjaga (mode `jaga 20`) menyalakannya
ulang sendiri dalam ≤ 1 siklus; SSH pulih tanpa sentuhan manusia (dibuktikan
23:13:23). File status akurat di semua siklus.

**Fase 2 — v1 sisa: SEBAGIAN.** Mode `--jaga` **LULUS**: 2 misi bagus →
`selesai/`, 1 misi mustahil → `gagal/` + `.hasil`, tanpa campur tangan.
TEMPEL **GAGAL**: keyevent 279 tidak menempel di KitaLulus (konsisten dengan
temuan Glints); perbaikan menu-tekan-lama (2× percobaan) belum berhasil
terpicu di aplikasi ini → TEMPEL kini **gagal secara jujur** (verifikasi
tampil ditambahkan: langkah dinyatakan GAGAL bila teks tak terbukti tampil —
sebelumnya melaporkan OK palsu). Jalan keluar yang terbukti tetap teknik
manual agen (clipboard + tekan-lama terkoordinat dump segar).

**Fase 3 — 05 batch: UJI TIDAK SAH, harus diulang.** Penyebab eksternal:
**layar HP terkunci sendiri ±23.30** (timeout saat jeda antar-uji) — semua
misi menabrak keyguard (BUKA menyala di balik kunci; TUNGGU_TEKS tak pernah
bisa cocok). Bukan kegagalan produk; bukan pula keberhasilan. Menunggu layar
dibuka Travis, lalu diulang penuh dengan perbandingan waktunya.

**Fase 4 & 5 — TERTUNDA** (menunggu layar dibuka; alatnya VM-side siap).

**Fase 6 — TERTUNDA** (rantai 09+07 menunggu layar; dry-run 09 sudah lulus
di uji asap).

**Fase 7 — 04 router: LULUS BERSYARAT.** Klasifikasi jenis-langkah 10/10
benar terhadap rantai nyata. Tier RUTIN (cadangan-llm7) menjawab 6,5 dtk;
tier VISION (cadangan-gemini) menjawab benar 2,2 dtk. **Temuan:** tier
RENCANA `utama` (Atria) menghabiskan seluruh anggaran token untuk
reasoning dan mengembalikan konten kosong (finish=length, 25–35 dtk) —
langkah rencana yang dirutekan ke `utama` WAJIB anggaran token besar atau
alias lain. Catatan harness: router mengklasifikasi berdasar JENIS langkah
(argumen pertama), bukan kalimat bebas.

**Fase 8 — 01 server residen: BELUM LULUS (temuan penting).** Asumsi
peluncuran prototipe **gugur di perangkat ini**: `app_process` menjalankan
`com.github.uiautomator.Main` dari APK atx → **crash SIGABRT (exit 134)**
tanpa keluaran. Server atx yang benar berjalan lewat instrumentasi
(`am instrument` + APK pasangan). Perbaikan skrip selama uji (terverifikasi
membantu, bukan menyembuhkan): JAR_URL menerima berkas lokal, kelas utama
dikoreksi ke `com.github.uiautomator.Main`, jalur staging memakai
`${TMPDIR}` khas Termux. Jalur instrumentasi = sesi khusus berikutnya.
Desain fallback terbukti bijak: eksekutor cara lama tetap tulang punggung.

**Fase 9 — 10 aplikasi pendamping: BUILD LULUS.** Tanpa Gradle (kotlinc →
d8 → aapt2 → zipalign → apksigner; resep di `build.sh` folder ini):
**APK 700.837 byte**, paket `id.musedroid.pendamping`, minSdk 24,
targetSdk 34, MainActivity launcher, tanda tangan terverifikasi. Toolchain
di VM: JDK 17 + SDK android-34 dirakit dari zip resmi (sdkmanager menyerah
pada proxy egress VM — `NoSuchElementException` saat mengambil repositori).
Sisa fase: pasang + bukti PING/DUMP — menunggu layar dibuka.

**Kejadian sesi yang tercatat jujur:** /tmp VM (tmpfs 512 MB) sempat penuh
100% oleh zip SDK → 3 berkas uji terkirim 0 byte ke HP (terdeteksi dari
ukuran, diperbaiki, diulang). Pelajaran: unduhan besar langsung ke
~/workspace, bukan /tmp.
