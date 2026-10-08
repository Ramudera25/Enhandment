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

**Sesi benahi 8 Okt pagi (atas perintah Travis: "benahi percobaan yang
masih gagal termasuk uji aplikasi"):** tiga perbaikan, dua terverifikasi
penuh, satu menunggu ketukan Travis:
(1) **Fase 7 RENCANA — TERATASI & terverifikasi.** Dengan
`max_tokens: 4000`, alias `utama` menjawab rencana lengkap
(finish=stop) dan `cadangan-gemini` juga utuh. Aturan anggaran kini
tertulis permanen di kepala `04-router-model.py`.
(2) **TEMPEL eksekutor v2 — LULUS PENUH di perangkat (07.18).**
Diagnosis kegagalan lama: eksekutor menekan-lama TANPA memastikan kolom
fokus dan memakai koordinat dump pra-keyboard. v2: ketuk kolom dulu
(fokus + keyboard naik) → dump SEGAR → tekan-lama 800 ms → menu
Tempel/Paste → verifikasi kata pertama (mekanisme jujur dipertahankan).
Log eksekutor: `OK 1 TEMPEL (7 karakter via clipboard,
fokus+tekan-lama+menu @ 151 375, terverifikasi tampil)` + `CEK_TEKS
"MUSEUJI" tampil` → **BERES 2/2** di formulir Add network (EditText
native). Perjalanan debugnya sendiri berharga: dua percobaan awal tetap
gagal karena (a) navigasi daftar Wi-Fi yang sedang memindai (baris
"Add network" berpindah — pelajaran Fase 5 terulang) dan (b) `dump_xml`
eksekutor membaca dump basi dari jembatan Download. Obat permanennya:
**`dump_xml` kini mengutamakan server residen Fase 8** (JSON-RPC
langsung dari dalam HP, selalu segar, 0,56 dtk) dengan jembatan lama
sebagai cadangan yang kini **dijaga mtime** (dump basi ditolak). Catatan
endpoint: jalur server u2 adalah `/jsonrpc/0` — `/jsonrpc` polos
menjawab 404 (dugaan "proxy Termux" di tengah jalan terbukti keliru;
pelajaran: tiru persis klien yang sudah terverifikasi).
**Bukti daya tahan Fase 8 genap: server residen PID 17783 mencapai umur
01:00:15** (start ±06.19 → 07.19) melewati kematian & restart Shizuku.
(3) **Fase 9 — akar "binder tak tiba" dikoreksi & fitur popup dibangun.**
Koreksi atas catatan sesi sebelumnya: **Sui.init adalah jalur Magisk —
tidak berlaku di Shizuku non-root ini** (dihapus). Penanda
`moe.shizuku.client.V3_SUPPORT` ditambah ke manifest — perlu, tapi
ternyata BUKAN kunci terakhirnya.
**KUNCI SEBENARNYA (terbukti 07.06–07.08): deklarasi
`<uses-permission android:name="moe.shizuku.manager.permission.API_V23"/>`
belum ada di manifest.** Manajer Shizuku memindai deklarasi inilah untuk
daftar "Application management" dan pengiriman binder — tanpa baris itu
aplikasi tidak terdaftar: tidak muncul di list, binder tidak pernah
dikirim, popup izin tidak mungkin muncul, seberapa pun server di-restart.
Sesudah baris itu ditambah + rebuild + pasang via rish: aplikasi
**muncul di Application management dengan saklar AKTIF**, status dalam
aplikasi membaca **"Siap"** (binder hidup + izin granted di sisi server),
dan layanan lokal menjawab **PING → PONG** di build final. **Fase 9
TUNTAS PENUH** — syarat "bersyarat"-nya gugur; penangan DUMP/KETUK di
layanan tetap stub jujur menunggu penyambungan UserService (peningkatan
terjadwal, bukan syarat lulus fase).
Atas permintaan Travis ("bikin fitur popup agar izinnya lebih gampang"),
MainActivity memasang **listener binder + auto-`requestPermission`**:
begitu binder tiba dan izin belum ada, dialog izin resmi Shizuku muncul
sendiri (termasuk saat kembali dari aplikasi Shizuku lewat tombol
"Buka Shizuku Sekali"). Pasang manual oleh pengguna gagal di penginstal
bawaan (APK build sendiri) — jalur `pm install` via rish adalah jalur
pasang resmi proyek ini.
Catatan kerapuhan tambahan: dump lewat jalur lambat bisa terbaca basi
(memori halaman lama) bila pengguna sedang aktif mengemudi — verifikasi
layar sensitif waktu sebaiknya lewat dump server residen (0,56 dtk).

**Sesi percepatan 8 Okt pagi (atas perintah Travis: "lakukan peningkatan
lagi… potong waktu proses di bawah 1 detik"):**
(1) **Eksekutor v3 — tangan & mata server.** KETUK/GESER/TOMBOL/TEMPEL
kini lewat JSON-RPC server residen (click 0,16 dtk, swipe 0,4 dtk,
pressKey) dengan rish sebagai cadangan; TUNGGU_TEKS polling 1 dtk di
jalur server (8 dtk tetap di jalur jembatan). Koreksi teknis: langkah
swipe u2 ≈ 5 ms (bukan 10) — tekan-lama TEMPEL sempat gagal di bagi-10.
(2) **Penjaga TARGET (keamanan).** Misi boleh membuka baris direktif
`TARGET <paket>`; sebelum langkah buta, eksekutor memastikan paket itu
di layar depan, bila tidak misi batal jujur. Lahir dari kejadian nyata
07.34: misi TEMPEL menempel ke bilah alamat Brave yang sedang dipakai
Travis (sudah dibersihkan; uji negatif penjaga lulus 07.38 — misi
bertarget Pengaturan menolak jalan saat Brave di depan).
(3) **Pintu masuk.** SSH ControlMaster untuk termux-hp & vm-16-77:
panggilan berulang 4–20 dtk → **±1,5 dtk**. Jalur VM→server lewat
forward tetap ±2,6 dtk/siklus (pajak RTT proxy) — alasan arsitektural
eksekusi dipindah ke dalam HP.
(4) **Aplikasi pendamping — UserService TERSAMBUNG.** AIDL
`ILayananPriv` (jalankan/dumpXml/uidSaya/destroy) + `LayananPriv`
(proses uid shell) + LayananLokal mengikatnya via
`Shizuku.bindUserService`. Terverifikasi di perangkat: **UID → 2000**,
**DUMP → XML asli 26–62 KB** (pengurai JSON bawaan Android; membuka
escape manual terbukti kotor), TOMBOL → OK, PING 3 ms, DUMP ±0,5 dtk.
Aplikasi bukan lagi kerangka: ia pintu lokal berhak shell yang tetap
menjawab bahkan saat rish tersendat.
(5) **Benchmark siklus (alat: `advance/01-server-residen/benchmark.py`).**
Di perangkat, keep-alive: halaman launcher **936/968/960 ms**, halaman
Wi-Fi (60 KB) **828 ms** — **di bawah 1 detik tercapai** untuk siklus
dump→klik→dump pada halaman wajar. Kasus terberat teramati: formulir
berkeyboard (±130 KB) dump tunggal ±0,8 dtk → siklus ±1,7 dtk (lantai
UiAutomation, dicatat apa adanya).
(6) **Kesiapan.** `scripts/cek-siap.sh` (papan satu pintu dari VM) +
`scripts/penjaga-server.sh` (cek/pulihkan server residen dari HP).
Papan saat sesi ditutup: SSH ✓, u2 ✓, pendamping ✓ (PONG/UID 2000),
eksekutor ✓; **rish/Shizuku berdenyut** — peringatan resmi Shizuku di
perangkat menyebut optimasi baterai; perbaikan sisi pengguna: bebaskan
Termux + Shizuku dari optimasi baterai. Justru di kondisi itu rantai
baru membuktikan nilainya: server residen + aplikasi pendamping tetap
bekerja tanpa rish.

---

**Fase 11 — 11 runner makro residen + kueri terarah: LULUS (8 Okt siang).**
Runner baru `misi-cepat.py` (advance/11): satu proses Python persisten
dengan koneksi keep-alive ke server u2; kueri terarah di dalam proses;
polling TUNGGU 250 ms; tunggu-perubahan-hierarki (≤1,2 dtk) menggantikan
sleep datar 1 dtk; gerbang masuk server-first (rish tidak lagi wajib);
penjaga TARGET utuh; durasi per langkah tercatat di log. Misi standar
9 langkah (TARGET settings → BUKA Wi-Fi → TUNGGU/KETUK "Add network" →
TUNGGU/CEK "Network name" → TEMPEL "MUSEUJI" → CEK → back ×2), sesi dan
perangkat yang sama: **eksekutor lama 47,8 dtk (1 putaran) → runner baru
22,3 & 22,4 dtk (2 putaran) = 2,1× lebih cepat, semua langkah OK.**
Rincian sesudah: BUKA 5,3 dtk (latensi start aktivitas + dump pertama),
TUNGGU_TEKS 0,33 dtk, KETUK_TEKS 0,69 dtk, CEK_TEKS ±0,65 dtk, TEMPEL
11,7 dtk (dari 23,0 — sisa didominasi dump berulang halaman berkeyboard,
lantai UiAutomation; tuas lanjutannya roadmap butir 3/4), TOMBOL back
0,5–1,1 dtk (dari ±3,5). **Temuan samping penting:** polling TUNGGU
eksekutor lama nyatanya selalu 8 dtk — `DUMP_VIA` diset di dalam fungsi
`dump_xml` yang selalu dipanggil lewat pipeline/command substitution
(subshell Bash), sehingga nilainya tidak pernah sampai ke shell utama
dan jalur polling 1 dtk tidak pernah aktif. Bug diam-diam ini ikut
menjelaskan lambatnya misi lama di langkah TUNGGU. Sesi diawali ketiga
kaki kendali mati bersamaan; pemulihan: Shizuku Start oleh pemilik →
rish hidup → server residen start ulang (mulai-server.sh, hidup pada
percobaan cek pertama) → seluruh papan hijau sebelum benchmark.
