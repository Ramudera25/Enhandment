# LOG-PEMBAHARUAN.md — Jurnal Pengembangan (untuk pembaca lanjut)

> File ini adalah **jurnal kerja pengembang**: progres yang sudah dicapai,
> tantangan yang dihadapi (termasuk yang memalukan), workflow, alur sistem,
> dan cara pikir di balik keputusan teknis proyek ini.
>
> **Pemula tidak perlu membaca file ini.** Cukup ikuti `README.md` dan
> `docs/` — semua yang di sana sudah teruji. File ini sengaja dipisah ke
> `advance/` supaya perjalanan pengembangannya tidak mengintimidasi siapa
> pun, sekaligus terbuka untuk dipakai sebagai bahan upgrade berikutnya.
>
> Terakhir diperbarui: **8 Oktober 2026**.

---

## 1. Lini masa progres

### 7 Okt 2026 — kelahiran (Jalan 0)
- Eksekutor lokal pertama di Termux HP (`scripts/eksekutor.sh`): bahasa misi
  `.job` 12 perintah (BUKA, TUNGGU_TEKS, KETUK_TEKS, TEMPEL, FOTO, CEK_TEKS,
  dst.), laporan gagal-jujur per langkah, mode `--jaga` (penjaga antrean misi).
- Bukti hidup pertama: misi demo **6/6 langkah beres dalam ±33 detik** dari
  satu berkas misi yang dikirim sekali.
- Malam yang sama, kemampuan ini dipakai sungguhan: **3 lamaran Glints
  terkirim** lewat aplikasi asli di HP (18.06, 18.27, 18.41 WIB) setelah
  jalur web seharian mental di Cloudflare; 4 listing lain terverifikasi
  sudah ditutup. Jalur aplikasi HP kemudian disahkan sebagai **cadangan
  resmi Glints** dalam operasi lamaran (cron batch sore ±16.30).

### 7→8 Okt 2026 — pengujian Fase 0–9 (risiko terkecil → terbesar)
Semua 10 peningkatan di `advance/` diuji di perangkat nyata. Ringkasnya:

| Fase | Isi | Hasil |
|---|---|---|
| 0 | Baseline cara lama | Dump 160 KB dari VM = **17,1–23,8 dtk** |
| 1 | 06 Penjaga prasyarat | LULUS — sshd dibunuh paksa, hidup lagi ≤1 siklus |
| 2 | Mode `--jaga` + TEMPEL v1 | `--jaga` LULUS; TEMPEL v1 **GAGAL** (keyevent 279 tidak menempel di aplikasi target) |
| 3 | 05 Batch banyak misi | LULUS — 3/3 beres; 93 dtk batch vs 97 dtk terpisah |
| 4 | 02 Crop fokus vision | LULUS — selisih titik 8px & 23px (ambang 30px) |
| 5 | 03 Peta layar | LULUS BERSYARAT — elemen daftar dinamis bisa basi; alur lupakan→catat ulang terbukti |
| 6 | 09 Perencana + 07 Resep | LULUS PENUH — susun→dry-run (negatif tertangkap)→jalan→simpan→pakai ulang |
| 7 | 04 Router model | LULUS BERSYARAT — klasifikasi 10/10; aturan permanen: tier RENCANA wajib max_tokens ≥4000 |
| 8 | 01 Server residen (Jalan 1) | LULUS — PING 0,01 dtk, DUMP 0,56 dtk (±20–35× cara lama), stabil 60 menit melewati kematian Shizuku |
| 9 | 10 Aplikasi pendamping (Jalan 2) | TUNTAS PENUH — UserService Shizuku tersambung (lihat §5) |

### 8 Okt 2026 pagi — sesi benahi
- **Fase 9 tuntas**: akar masalah "binder tidak pernah tiba" ternyata
  deklarasi `<uses-permission android:name="moe.shizuku.manager.permission.API_V23"/>`
  yang hilang di manifest — deklarasi inilah yang dipindai manajer Shizuku.
- **TEMPEL v2 LULUS**: fokus kolom dulu → dump segar → tekan-lama → menu
  Tempel → verifikasi kata pertama tampil. `dump_xml` eksekutor kini
  mengutamakan server residen dan menolak dump basi (penjaga mtime).
- Fitur popup izin otomatis di aplikasi pendamping (permintaan Travis):
  dialog izin resmi muncul sendiri saat binder tiba.

### 8 Okt 2026 — sesi percepatan ("potong di bawah 1 detik")
- **Eksekutor v3**: tangan (ketuk/geser/tombol/tempel) pindah ke JSON-RPC
  server residen `u2` — klik ±0,16 dtk; rish menjadi cadangan.
- **Pintu masuk**: SSH ControlMaster untuk host HP — panggilan berulang
  **4,13 dtk → ±1,5 dtk**.
- **Pendamping**: UserService AIDL `ILayananPriv` tersambung penuh —
  PING 3 ms, UID 2000 (hak shell terbukti), DUMP XML asli 488–554 ms.
- **Benchmark penutup**: siklus dump→klik→dump **di perangkat 828–968 ms**
  pada halaman wajar — target di bawah 1 detik **tercapai**; kasus terberat
  formulir berkeyboard ±1,7 dtk (lantai UiAutomation, dicatat apa adanya).
- Uji terukur di aplikasi Glints asli: dump feed 45 KB = **173 ms**
  (kemarin: 17–24 dtk); siklus lihat→ketuk→lihat **±0,5 dtk** (kemarin ±36 dtk).
- Eksekusi nyata sesudahnya: lamaran uji via aplikasi HP terkirim
  (skrining dijawab apa adanya dari CV — kemampuan yang tidak ada di CV
  tidak diklaim).

### 8 Okt 2026 siang — paket roadmap 1+2 dieksekusi (advance/11)
- **Runner makro residen `misi-cepat.py`**: SATU proses Python persisten
  per misi (koneksi HTTP keep-alive ke server u2), kueri terarah di dalam
  proses (dump tidak keluar), polling TUNGGU 250 ms, tunggu-perubahan-
  hierarki menggantikan sleep datar, gerbang masuk tidak lagi wajib rish,
  setiap langkah tercatat durasinya.
- **Benchmark misi standar 9 langkah** (navigasi Wi-Fi + TEMPEL di
  formulir berkeyboard, sesi yang sama): eksekutor lama **47,8 dtk** →
  runner baru **22,3 / 22,4 dtk** (dua putaran) — **2,1× lebih cepat**.
  TEMPEL: 23,0 → 11,7 dtk (sisanya lantai dump halaman berat — tuasnya
  roadmap butir 3/4). TOMBOL back: ±3,5 → 0,5–1,1 dtk; KETUK_TEKS:
  ±3 → 0,7 dtk; TUNGGU_TEKS: → 0,33 dtk.
- **Temuan samping**: polling TUNGGU eksekutor lama ternyata selalu 8 dtk
  — variabel `DUMP_VIA` yang diset di dalam `dump_xml` tidak pernah
  keluar dari subshell pipeline Bash, jadi jalur 1 dtk tidak pernah
  aktif. Tercatat di PENGUJIAN.md Fase 11.
- **Desain butir 4 ditulis**: `DESAIN-V3-POHON-UI.md` (arsitektur pohon
  tersimpan + aturan kebenaran anti-basi + rencana uji + target angka).
- Sesi ini juga membuktikan rantai pemulihan: ketiga kaki kendali mati
  bersamaan (pola 08.41 berulang) → Shizuku di-Start pemilik → server
  residen dihidupkan ulang lewat rish → papan hijau lagi.
- **Paket percepatan operasional (perintah pemilik, sesudah eksekusi
  manual 2 item antrean HP berhasil pukul 11.41)**: (a) cron riset pagi
  kini MEWAJIBKAN URL detail listing (`/opportunities/jobs/...`) pada
  baris antrean HP — deep link adalah satu-satunya bentuk URL yang
  diklaim aplikasi, terbukti lagi di Fase 12 (domain akar lari ke
  browser); (b) `advance/12` — misi navigasi Glints (generator
  `buat-misi.py` + template tautan/cari) + direktif `TAUTAN` di
  misi-cepat + strategi KETIK/TEMPEL diperbaiki berbasis bukti kolom
  pencarian (input text terverifikasi mengalahkan menu tempel di sana);
  misi pencarian 8 langkah tuntas **12,6 dtk**; (c) `advance/13` —
  penjaga kaki residen: server residen yang dibunuh dipulihkan penjaga
  dalam **±91 dtk**, dan notifikasi kematian Shizuku kini anti-alarm-
  palsu (probe ganda) setelah siklus pertama penjaga sempat menembak
  satu notifikasi palsu akibat timeout binder sesaat. PENGUJIAN.md
  Fase 12–13.
- **Penomoran versi + gambaran konfigurasi (perintah pemilik)**: skema
  V\<Mayor\>.\<Minor\> diterapkan surut — V1.0 fondasi (jangkar
  `ded1950`), V2.0 makro residen (`37b168d`), V3.0 operasional — dengan
  tag git `v1.0`/`v2.0`/`v3.0`. Folder baru
  `advance/14-versi-dan-konfigurasi/`: `VERSI.md` (skema, riwayat,
  checklist rilis, catatan penamaan vs DESAIN-V3) + `KONFIGURASI-HP.md`
  (konfigurasi produksi tersanitasi sebagai gambaran workflow: peta
  alur, tata letak HP, SSH ControlMaster, urutan pemulihan).
  `mulai-server.sh` di advance/01 disinkronkan dengan versi HP (kait
  penjaga). Seni ASCII README utama diganti meme ABSOLUTE CINEMA (dua
  tangan terangkat) + badge versi V3.0. PENGUJIAN.md Fase 14.

### 8 Okt 2026 sore — V4.0 teruji di perangkat nyata (advance/15–17)
- **Pohon UI aksesibilitas aktif.** Layanan “muse-droid Pohon UI”
  akhirnya terikat oleh sistem sesudah reboot HP. Diagnosis sebelumnya
  terbukti: manajer aksesibilitas (AMS) macet secara global — uji
  kontrol AutoX.js pun gagal terikat — dan reboot menyembuhkannya.
  Socket pohon 127.0.0.1:19102 menjawab `PING` dalam **7–32 ms**;
  umur salinan saat layar aktif **32 ms–0,4 dtk**. `CARI` terverifikasi
  akurat terhadap tangkapan layar untuk simpul yang terlihat (tombol
  “Invite” Brave: bounds `[804,100][1049,205]`, tengah (926,152)).
  Batas jujurnya dicatat apa adanya: bounds simpul di bawah lipatan
  daftar bisa tidak andal, sehingga verifikasi pasca-ketuk §4 tetap
  menjadi bagian dari protokol.
- **Temuan arsitektur besar: pohon & u2 eksklusif.** Sesi UiAutomation
  dari server u2 menutup layanan aksesibilitas selama aktif; sesudah
  u2 berhenti, pohon mengikat kembali sendiri dalam **±12 dtk**.
  Konsekuensinya permanen untuk workflow: **pohon adalah kaki utama,
  u2 adalah cadangan on-demand** — bukan dua mata yang dinyalakan
  bersamaan.
- **Penjaga menjadi penjaga empat kaki (Fase 16).** `penjaga-kaki.sh`
  kini memantau pohon 19102, u2, rish, dan pendamping 19101; menahan
  kebangkitan u2 selama pohon hidup; dan menegakkan eksklusivitas
  dengan mematikan u2 bila pohon mati tetapi u2 hidup (maks 1× per
  5 menit per episode). Lingkar sembuh-sendiri terlihat langsung di
  log: **18:24:25** deteksi → **18:24:51** u2 dimatikan →
  **18:26:01** pohon pulih → **18:26:02** u2 ditahan. Layanan depan
  pendamping dihidupkan penjaga via rish dan 19101 menjawab **PONG**
  secara stabil.
- **Misi ad-hoc generik terbukti (Fase 17).** Misi
  `uji-adhoc-settings.job` di Pengaturan Android **LULUS 8/8** dalam
  **24,62 dtk** pada mode pohon: buka aplikasi → tunggu teks → ketuk
  ikon cari → `ISI_TEKS "bluetooth"` → tunggu/cek “Bluetooth” → foto.
  `TUNGGU_TEKS` hanya **8 ms** dan `CEK_TEKS` **7 ms**. Catatan jujur:
  `ISI_TEKS` via pohon sempat kalah balapan dengan tangkapan fokus
  snapshot dan jatuh ke `input text` rish yang terverifikasi; poles
  V4.1 adalah menunggu versi snapshot naik/fokus muncul maks 600 ms
  sebelum fallback.

---

## 2. Arsitektur & alur

```
┌────────────┐  SSH (ControlMaster,   ┌───────────────── HP ANDROID ──────────────────┐
│  VM / PC   │  mux ±1,5 dtk)         │  Termux                                     │
│  (bayu /   │ ─────────────────────▶ │   ├─ eksekutor.sh — bahasa misi .job        │
│   agen AI) │  misi dikirim SEKALI,  │   ├─ server residen u2 — JSON-RPC :20128*   │
│            │  dieksekusi DI HP      │   └─ aplikasi pendamping — UserService      │
└────────────┘                        │        (AIDL, socket 127.0.0.1:19101)       │
                                      │              │                              │
                                      │   Shizuku / rish ──▶ uid 2000 (shell)       │
                                      │              │                              │
                                      │   UiAutomator (melihat) + input (menyentuh) │
                                      └─────────────────────────────────────────────┘
```
*nomor port mengikuti konfigurasi di perangkat; yang penting polanya.

**Tiga kaki kendali** (saling cadangan, tidak bergantung satu sama lain):
1. **rish/Shizuku** — pintu pertama; mati hanya bisa dihidupkan dari aplikasi
   Shizuku di HP (tangan manusia).
2. **Server residen u2** — proses `app_process` (uiautomator2) yang tinggal
   hidup di HP; tetap bekerja saat Shizuku mati.
3. **Aplikasi pendamping** — UserService Shizuku (AIDL): PING/DUMP/KETUK/
   TOMBOL dari proses uid shell sendiri.

**Alur misi**: agen menyusun berkas `.job` → dikirim sekali ke HP →
eksekutor menjalankan langkah demi langkah **di dalam HP** (polling tunggu
lokal) → setiap langkah diverifikasi (teks tampil? elemen ada?) → hasil
dilaporkan jujur: `OK`, `GAGAL <sebab>`, atau misi batal demi keamanan.

---

## 3. Workflow pengembangan

1. **Ide masuk `advance/` dulu** — tidak ada fitur yang langsung mengklaim
   diri "resmi". Angka bernomor (01–10) = urutan uji yang disarankan.
2. **Uji di perangkat nyata dengan misi aman** (Pengaturan, catatan, demo) —
   tidak pernah menguji pada data/lamaran sungguhan.
3. **Lulus = pindah** ke `scripts/` + `docs/` dan dicatat; **gagal = parkir
   dengan catatan sebab**, bukan dihapus diam-diam.
4. **Setiap klaim kecepatan menyebut angkanya dan cara mengukurnya**
   (`benchmark.py`, `matriks.py` di `01-server-residen/`).
5. Bukti layar (screenshot/dump) disimpan rapi di folder khusus
   (`~/muse-droid/bukti/` di HP) — tidak berserakan.
6. Commit kecil per tahap terverifikasi; push menunggu PAT pemilik repo.

---

## 4. Cara pikir (prinsip yang lahir dari kegagalan)

- **Ukur dulu, klaim kemudian.** Baseline cara lama (dump ±19,6 dtk) dicatat
  sebelum satu baris pun dioptimasi — tanpa itu, "lebih cepat" cuma perasaan.
- **Yang mahal itu melihat, bukan menyentuh.** Dekomposisi benchmark
  membuktikan dump pohon UI = 0,8–0,95 dtk, sedangkan klik hanya 0,16 dtk.
  Seluruh strategi percepatan lahir dari satu fakta ini.
- **Pindahkan eksekusi ke dekat layar.** Pajak jaringan (SSH/proxy ±1,5–2,6
  dtk per putaran) tidak bisa dihilangkan — jadi putarannya yang dihilangkan:
  misi berjalan di dalam HP, jaringan hanya dipakai di awal dan di akhir.
- **Gagal jujur lebih berharga daripada sukses palsu.** Alat yang melaporkan
  sukses padahal gagal = GAGAL. Eksekutor memverifikasi setiap langkah dan
  berani membatalkan misi.
- **Jangan rebut layar pengguna.** HP ini milik manusia yang sedang memakainya
  juga. Lahirlah **penjaga TARGET**: misi menyebut paket tujuannya; bila layar
  berpindah tangan, langkah buta dibatalkan — bukan diteruskan berharap-harap.
- **Satu ketukan per putaran, lalu lihat lagi.** Tata letak aplikasi bergeser
  setelah tiap jawaban (grup formulir menciut). Koordinat hafalan adalah
  sumber ketukan nyasar; dump segar adalah obatnya.
- **Batas kejujuran berlaku juga ke mesin pencari kerja**: pertanyaan
  skrining dijawab dari CV apa adanya — kemampuan/sertifikat yang tidak
  dimiliki tidak pernah diklaim, walau itu berarti lamaran lebih lemah.

---

## 5. Tantangan & kejadian jujur (dan obat permanennya)

| Kejadian | Akar masalah | Obat permanen |
|---|---|---|
| Misi TEMPEL menempel teks ke **bilah alamat Brave yang sedang dipakai pemilik HP** (8 Okt 07.34; teks langsung dibersihkan) | Layar berpindah tangan di tengah jendela uji; verifikasi misi benar tapi aplikasinya salah | Penjaga TARGET di eksekutor + aturan: tidak ada uji perangkat saat HP dipakai pemiliknya; uji negatif penjaga LULUS |
| Polling TUNGGU_TEKS rapat (±2 dtk) **menumbangkan uiautomator lalu server Shizuku** | Frekuensi dump berlebihan membebani layanan | Jeda polling 8 dtk di jalur jembatan; polling adaptif 1 dtk hanya di jalur server |
| **Shizuku mati 3× dalam satu hari** (termasuk sekali bersamaan dengan server residen + pendamping, 08.41) | Optimasi baterai Android + layanan latar biasa; umur hidup <1 jam pada satu kejadian | Bebaskan Termux + Shizuku dari optimasi baterai (sisi pemilik, sudah dilakukan); penjaga-server.sh; rencana: pendamping jadi *foreground service* |
| Binder pendamping "tidak pernah tiba" berhari-hari | Manifest kehilangan deklarasi izin `API_V23` | Deklarasi ditambah; pelajaran: yang dipindai manajer Shizuku adalah deklarasi itu, bukan meta-data lain; jalur Sui.init (Magisk) tidak berlaku & dihapus |
| Endpoint server dikira `/jsonrpc` | 404 — endpoint yang benar `/jsonrpc/0` | Dikoreksi di kode + komentar; dugaan "proxy membelokkan" terbukti keliru dan dicabut |
| TEMPEL v1 gagal total | `input keyevent 279` (PASTE) tidak bekerja di aplikasi target & Android 14 membatasi clipboard-get | TEMPEL v2: clipboard-set → fokus → tekan-lama → menu Tempel → verifikasi tampil |
| Dump basi terbaca sebagai layar sekarang | Jembatan berkas membaca dump lama | `dump_xml` server-residen-first + penjaga mtime: dump basi ditolak |
| Berburu berkas di pemilih file HP lama sekali (±20 mnt dari total 25 mnt satu eksekusi) | Pemilih file Samsung sulit dinavigasi buta; folder baru belum terindeks | Berkas misi disiapkan di folder tetap `Download/lamaran-<tanggal>/` + `termux-media-scan`; gulir langkah kecil |

Dua catatan ketahanan yang belum tertutup saat jurnal ini ditulis:
- **Layanan pendamping masih layanan latar biasa** — Android bisa
  mematikannya saat lama menganggur. Rencana perbaikan: *foreground service*.
- **Umur Shizuku tidak stabil** bila optimasi baterai aktif — satu-satunya
  kaki yang hanya bisa dihidupkan manusia dari aplikasinya. Tiga kaki
  kendali yang saling cadangan adalah mitigasi arsitekturalnya.

**Pembaruan catatan 8 Okt 2026 sore (V4.0):** butir *foreground
service* di atas sudah dikerjakan dan teruji pada Fase 16 — layanan
depan pendamping dihidupkan penjaga via rish dan socket 19101 menjawab
PONG stabil selama uji. Catatan baru yang menggantikan sebagian cara
pandang lama adalah **eksklusivitas pohon–u2**: sesi UiAutomation
menutup layanan aksesibilitas selama aktif, sedangkan pohon mengikat
kembali sendiri ±12 dtk sesudah u2 berhenti. Karena itu susunan kaki
sekarang dibaca sebagai pohon utama + u2 cadangan on-demand, dengan
rish dan pendamping sebagai jalur pendukung/pemulihan.

---

## 6. Angka benchmark (semua terukur di perangkat)

| Metrik | Cara lama | Sekarang | Catatan |
|---|---|---|---|
| Dump layar 160 KB dari VM | 17,1–23,8 dtk | — | baseline Fase 0 |
| Siklus dump→klik→dump dari VM | 4.063 ms | ±2.577 ms | pajak RTT proxy tetap ada |
| Siklus dump→klik→dump **di perangkat** | 1.628 ms (keep-alive) | **828–968 ms** | halaman wajar |
| Dump tunggal halaman berat (formulir + keyboard, ±130 KB) | — | ±0,8 dtk | lantai UiAutomation |
| Klik via server residen | 1.126 ms (RPC lama) | **±0,16 dtk** | |
| PING pendamping (AIDL) | — | **3 ms** | UID terbukti 2000 |
| Dump via pendamping | — | 488–554 ms | |
| Panggilan SSH berulang | 4,13 dtk | **±1,5 dtk** | ControlMaster |
| Siklus lihat→ketuk→lihat di aplikasi nyata (Glints) | ±36 dtk | **±0,5 dtk** | dump feed 45 KB = 173 ms |

---

## 7. Bacaan pendamping — repo relevan & nilai jujurnya bagi proyek ini

Lima repo berikut sering disebut orang untuk topik yang sama. Penilaian di
sini spesifik untuk **arsitektur dan leher botol proyek ini** (lantai dump
UiAutomation 0,8–0,95 dtk; jalur Shizuku; tanpa root; tanpa adb permanen) —
bukan penilaian kualitas repo-nya secara umum.

| Repo | Apa itu | Nilai untuk proyek ini |
|---|---|---|
| **Appium** — `appium/appium` | Kerangka otomasi mobile lintas platform berbasis protokol WebDriver, di atas UiAutomator2 | **Bukan pemercepat**: duduk di atas UiAutomator yang sama (lantai dump sama) + overhead HTTP & pembuatan sesi. Layak dibaca untuk *pola locator & tata kelola test suite* bila suatu hari proyek ini butuh regresi terstruktur |
| **Mobile-Agent** — `OpenBMB/Mobile-Agent` | Kerangka agen otonom berbasis model vision (perencanaan–keputusan–refleksi) | Lapisan **kecerdasan**, bukan kecepatan: tiap langkah memanggil model (detikan). Layak dibaca untuk ide *perencanaan multi-langkah & refleksi diri* — mengurangi langkah salah, bukan mempercepat langkah |
| **AutoDroid** — `Autonomous-Agents/AutoDroid` | Agen Android berbasis LLM + graf pengetahuan fungsi aplikasi | Idenya sejalan dengan `03-peta-layar` & `08-pengetahuan` kita: hafalan struktur aplikasi mengurangi coba-coba. Layak dibaca untuk *desain basis pengetahuan per aplikasi* |
| **AppAgent** — `mnotgod96/AppAgent` | Agen GPT-4V yang belajar dari eksplorasi & demonstrasi, lalu mengeksekusi | Pola "belajar sekali, ulangi berkali-kali" sudah kita wujudkan secara deterministik lewat **resep** (`07-resep`) + misi `.job`. Layak dibaca untuk *strategi eksplorasi otomatis* |
| **pure-python-adb** — `Guanjin/pure-python-adb` | Klien protokol ADB murni Python (tanpa binary adb) | Manfaat **marjinal** di sini: jalur kita bekerja via Shizuku/rish, nyaris tanpa adb; hematnya hanya waktu spawn proses (±50–150 ms). Layak dibaca untuk memahami *protokol ADB di balik layar* |

Kesimpulan jujur: tidak satu pun menyerang leher botol terukur kita.
Framework otomasi berbagi lantai UiAutomator yang sama; kerangka agen
menambah kecerdasan di atasnya dengan harga latensi per langkah. Yang bisa
dipinjam dari mereka adalah **idenya**, bukan mesinnya.

---

## 8. Roadmap terbuka (bahan upgrade berikutnya)

Diurutkan dari dampak terbesar terhadap durasi ujung-ke-ujung. Daftar ini
**terbuka untuk pembaharuan** — siapa pun boleh mengusulkan, menguji, dan
memperbarui statusnya di file ini.

1. **Eksekusi makro penuh di perangkat** — misi dikirim sekali; server
   residen menjalankan semua langkah dengan polling tunggu lokal
   100–200 ms; laporan hanya hasil akhir. Perkiraan hemat: ±20–35 dtk
   per misi 15 langkah (pajak jaringan per langkah hilang total).
   **STATUS 8 Okt siang: DITERAPKAN** sebagai `advance/11` (runner
   `misi-cepat.py`) — polling TUNGGU 250 ms; misi standar 9 langkah
   47,8 → 22,3 dtk bersama butir 2 (lihat lini masa §1).
2. **Kueri terarah menggantikan dump penuh** — server menjawab "di mana
   teks X" dengan bounds saja (<1 KB) alih-alih pohon XML 60–130 KB.
   Target: siklus cari→ketuk ±0,9 dtk → ±0,3–0,5 dtk di halaman wajar.
   **STATUS 8 Okt siang: DITERAPKAN** di runner yang sama — pencarian
   mengurai pohon di dalam proses runner dan hanya memakai bounds;
   langkah KETUK_TEKS terukur 0,69 dtk termasuk ketuk + verifikasi
   perubahan layar (misi standar advance/11).
3. **Isi teks tanpa keyboard** — set-text langsung via pendamping / tempel
   terverifikasi; menghilangkan kasus terberat (formulir berkeyboard
   ±1,7 dtk).
4. **Pohon UI tersimpan (lompatan v3)** — layanan aksesibilitas di aplikasi
   pendamping memelihara salinan pohon UI secara *live*; observasi turun
   ke puluhan milidetik dan siklus total berpotensi ±0,2 dtk. Syarat:
   pemilik HP mengaktifkan layanan itu sekali di Pengaturan; ini satu-
   satunya jalan menembus lantai UiAutomator.
   **STATUS 8 Okt 2026 sore: DITERAPKAN & TERUJI sebagai V4.0**
   (`advance/15`, PENGUJIAN.md Fase 15) — layanan terikat sesudah
   reboot menyembuhkan AMS yang macet global; PING 7–32 ms; umur
   salinan 32 ms–0,4 dtk saat layar aktif; CARI akurat untuk simpul
   terlihat. Aturan arsitektur hasil ujinya: pohon dan u2 eksklusif,
   jadi pohon adalah kaki utama dan u2 hanya cadangan on-demand.
5. **Ketahanan** — pendamping menjadi *foreground service*; penjaga yang
   lebih proaktif untuk server residen; pemulihan berjenjang yang jujur
   saat kaki kendali mati (yang bisa dipulihkan mesin dipulihkan, yang
   butuh manusia dilaporkan apa adanya).
   **STATUS 8 Okt siang: SEBAGIAN DITERAPKAN** — penjaga residen
   `advance/13` terpasang & teruji (server residen dipulihkan otomatis
   ±91 dtk; kematian Shizuku diberitahukan ±1 menit dengan probe ganda
   anti-alarm-palsu).
   **STATUS 8 Okt 2026 sore: DIPERBARUI (Fase 16)** — *foreground
   service* pendamping sudah menjadi bagian paket V4.0: penjaga
   menghidupkannya via rish dan socket 19101 menjawab PONG stabil.
   Penjaga juga naik kelas menjadi penjaga empat kaki (pohon, u2, rish,
   pendamping) yang menahan kebangkitan u2 selama pohon hidup dan
   menegakkan eksklusivitas pohon–u2 bila keadaan terbalik.

---

*Jurnal ini ditulis oleh bayu (agen AI pengelola proyek) bersama Travis
(pemilik perangkat & repo). Angka-angkanya berasal dari log pengujian
`PENGUJIAN.md` dan catatan sesi harian proyek — bukan dari brosur.*
