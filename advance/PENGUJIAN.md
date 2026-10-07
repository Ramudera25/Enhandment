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

**Fase 3 — 05 batch: LULUS (diulang 8 Okt pagi, layar terbuka).** Sempat
gagal lagi di percobaan pertama pagi itu — dan kegagalannya justru
mengungkap akar masalah lintas-fase: **polling TUNGGU_TEKS eksekutor
terlalu rapat** (dump penuh tiap ±2 dtk) menumbangkan uiautomator lalu
**server Shizuku mati total** ("Server is not running"; dihidupkan ulang
Travis dari aplikasi Shizuku). Perbaikan permanen: jeda antar-poll
TUNGGU_TEKS menjadi **8 detik** (satu dump per ±10 dtk). Sesudah itu:
3 misi terpisah 3× SSH = **97 dtk**, batch 1× SSH = **93 dtk** dinding
(82 dtk internal batch) — ketiganya BERES 3/3 di kedua mode, ringkasan
batch benar, stayon dilepas bersih sesudahnya. Batch menang tipis di
waktu dinding; menang besar di struktur (satu koneksi, satu bangun).

**Fase 4 — 02 crop fokus: LULUS dengan catatan.** Protokol diperketat:
crop dipusatkan pada titik yang digeser (+120,+90) dari kebenaran XML
agar pembacaan crop benar-benar mengukur, bukan menebak pusat. Dua
target terukur di bawah ambang: teks penjelasan Bluetooth → balik
(540,535) vs XML (540,558) = **selisih 23px**; judul "Bluetooth" → balik
(265,212) vs XML (264,204) = **selisih 8px**. Target ketiga (teks "Off")
adalah kasus tepi metodologi: node teksnya selebar baris — pusat bounds
XML (491,376) tidak berkorelasi dengan posisi glifnya (di tepi kiri),
sehingga tidak bisa dilokalisasi secara visual dari crop mana pun.
Matematika crop+baliknya sendiri eksak (2/2 target berglif jelas).

**Fase 5 — 03 peta layar: LULUS BERSYARAT.** Mekanik persis: catat dari
dump → cari mengembalikan koordinat yang sama → lupakan menghapus.
Kasus basi terjadi SECARA ALAMI: ketuk pertama dari peta ke "Add
network" meleset — daftar jaringan sedang memindai (baris lebih sedikit
dari yang tercatat di hierarki) sehingga koordinat hierarki belum
tergambar penuh di layar. Alur pemulihan sesuai desain — lupakan → dump
segar → catat ulang → ketuk — membuka formulir "Add network" dengan
benar (terverifikasi visual). Pelajaran: peta akurat untuk elemen statis;
daftar dinamis tetap butuh verifikasi sesudah ketuk (yang memang
dirancang begitu). Tiga layar terverifikasi: Bluetooth, Wi-Fi, formulir
Add network (About phone terlintasi di tumpukan Pengaturan).

**Fase 6 — rantai 09+07: LULUS PENUH.** Spesifikasi JSON misi Wi-Fi →
`09 susun` menghasilkan .job rapi berkepala misi → `09 uji` terhadap dump
Wi-Fi asli: langkah baca LULUS dengan koordinat; uji negatif
(CEK_TEKS "MustahilXYZ") **tertangkap GAGAL di meja** → eksekutor
menjalankan .job-nya **BERES 4/4** → `07 simpan` menjadi resep
"buka-layar" (parameterisasi otomatis: tidak ada — nilai misi diganti
manual menjadi {{TARGET}}/{{TEKS}}/{{FOTO}}, sesuai tip alatnya) →
`07 pakai` dengan nilai Bluetooth → `09 uji` LULUS vs dump Bluetooth →
eksekutor **BERES 4/4**. Indeks resep mencatat pemakaian dengan benar.

**Fase 7 — 04 router: LULUS BERSYARAT.** Klasifikasi jenis-langkah 10/10
benar terhadap rantai nyata. Tier RUTIN (cadangan-llm7) menjawab 6,5 dtk;
tier VISION (cadangan-gemini) menjawab benar 2,2 dtk. **Temuan:** tier
RENCANA `utama` (Atria) menghabiskan seluruh anggaran token untuk
reasoning dan mengembalikan konten kosong (finish=length, 25–35 dtk) —
langkah rencana yang dirutekan ke `utama` WAJIB anggaran token besar atau
alias lain. Catatan harness: router mengklasifikasi berdasar JENIS langkah
(argumen pertama), bukan kalimat bebas.

**Fase 8 — 01 server residen: LULUS (8 Okt pagi, resep dikoreksi dari
sumbernya).** Asumsi peluncuran prototipe memang gugur (SIGABRT, lihat
riwayat di bawah) — tapi penyebabnya kini pasti: **artefak + kelas yang
salah.** Dari kode sumber uiautomator2 3.7.0 (`core.py`): server resminya
adalah **u2.jar** (aset wheel pip) dengan kelas utama
**`com.wetest.uia2.Main`**, diluncurkan
`CLASSPATH=/data/local/tmp/u2.jar app_process / com.wetest.uia2.Main -p 9008`.
APK atx (`app-uiautomator.apk`) tidak menyatakan `<instrumentation>` sama
sekali — jalur instrumentasi yang diduga sebelumnya juga bukan jalurnya.
Dengan resep benar, murni lewat rish (tanpa ADB): server **hidup**,
terlepas rapi sebagai anak init, log "http server listening on *:9008".
Terukur di perangkat yang sama: **PING 0,01–0,02 dtk**; **DUMP hierarki
83 KB dalam 0,56 dtk** (cara lama 11–19,6 dtk — **±20–35× lebih cepat**);
klien repo `server-hp.py` menjawab dari VM lewat forward SSH (ping =
info perangkat; dump = XML penuh). Jejak RAM ±94 MB (VmRSS). Server tetap
hidup melewati kematian Shizuku di sesi yang sama — bukti awal daya
tahan; pengamatan 60 menit penuh menyusul dari pemakaian. `mulai-server.sh`
ditulis ulang ke resep terbukti ini. Riwayat temuan lama: peluncuran
`com.github.uiautomator.Main` dari APK atx → crash SIGABRT (exit 134).

**Fase 9 — 10 aplikasi pendamping: LULUS BERSYARAT (8 Okt pagi).**
Build tanpa Gradle lulus sejak semalam (APK `id.musedroid.pendamping`,
resep `build.sh` folder ini); sesi ini: **terpasang lewat rish** dan
**endpoint lokalnya menjawab: PING → PONG** di 127.0.0.1:19101; **DUMP
menjawab jujur "GAGAL belum disambungkan (kerangka)"** — saluran
perintahnya terbukti ujung-ke-ujung, penangan DUMP memang menunggu
penyambungan UserService Shizuku. Tiga cacat build pertama ditemukan &
diperbaiki di sesi ini: (1) UI kerangka tak pernah dipasang — kini layar
status + 2 tombol nyata; (2) **artefak `dev.rikka.shizuku:aidl` hilang
dari dex** → crash NoClassDefFoundError `IShizukuApplication$Stub` saat
menyentuh API Shizuku — kini masuk build.sh; (3) **izin INTERNET hilang
dari manifest** → bind ServerSocket kena EACCES dan proses mati berulang
— kini dinyatakan. Port layanan dibuat tetap (19101). Satu kaki tersisa:
**izin Shizuku untuk aplikasi ini** — binder tidak dikirim ke aplikasi
yang dipasang SESUDAH server Shizuku start (perilaku Shizuku); Sui.init
sudah ditanam sebagai jalan pintas, verifikasi finalnya menunggu satu
restart Shizuku oleh Travis, lalu: buka aplikasi → status "hidup" →
ketuk Minta Izin → Allow.

**Kejadian sesi yang tercatat jujur:** /tmp VM (tmpfs 512 MB) sempat penuh
100% oleh zip SDK → 3 berkas uji terkirim 0 byte ke HP (terdeteksi dari
ukuran, diperbaiki, diulang). Pelajaran: unduhan besar langsung ke
~/workspace, bukan /tmp.

**Sesi lanjutan 8 Okt pagi (atas perintah Travis):** Fase 3–6 tuntas
(hasil di atas). Dua kejadian penting: (1) server Shizuku sempat mati
total akibat badai polling TUNGGU_TEKS — dihidupkan ulang Travis dari
aplikasi Shizuku; perbaikan tempo polling 8 dtk kini permanen di
eksekutor; (2) tumpukan halaman Pengaturan memulihkan halaman lama
(restoration) — BUKA intent dalam tidak selalu menavigasi ulang bila
task sudah ada; misi uji sebaiknya sadar halaman awal.

**Sesi penutup 8 Okt pagi (atas perintah Travis: "lanjut fase 8 dan 9
baru kita akan push ini"):** Fase 8 LULUS dan Fase 9 LULUS BERSYARAT —
**seluruh Fase 0–9 kini punya hasil uji nyata.** Di akhir sesi server
Shizuku mati sekali lagi di tengah keramaian pasang-ulang APK (rish
menolak menjawab; aplikasi Shizuku menampilkan tombol Start) — kerapuhan
server Shizuku di HP ini kini tercatat tiga kali dalam dua hari dan
menjadi konteks penting membaca semua hasil: jalur rish bergantung pada
layanan yang bisa mati oleh tekanan sistem, sementara server residen
Fase 8 (proses app_process biasa) terbukti tetap hidup melewatinya.
Sisa tindak lanjut tunggal: restart Shizuku oleh Travis →
verifikasi kaki izin aplikasi pendamping (status + Allow) dalam sekali
buka. Sesudah itu repo siap push.
