# Enhandment

```
█ █ ██ █ █                 █ █ ██ █ █
██████████                 ██████████
██████████                 ██████████
 ████████                   ████████
 ████████                   ████████
  ██████                     ██████
   ████                       ████
    ████        █████        ████
     ████      ███████      ████
      ████     ███████     ████
       ████    █▀▀▀▀▀█    ████
        ████   ███████   ████
         ████  █ ███ █  ████
             ███████████
            █████████████
           ███████████████
           ███████████████
          █████████████████
```

*ABSOLUTE CINEMA — HP-nya kerja sendiri, kamu tinggal angkat tangan.*

![status](https://img.shields.io/badge/status-terverifikasi%20di%20perangkat%20nyata-brightgreen)
![versi](https://img.shields.io/badge/versi-V4.4.1-blueviolet)
![root](https://img.shields.io/badge/root-tidak%20perlu-blue)
![bahasa](https://img.shields.io/badge/bahasa-Indonesia-orange)
![lisensi](https://img.shields.io/badge/lisensi-MIT-lightgrey)

**HP Android kamu bisa bekerja sendiri — dikendalikan AI, tanpa root, tanpa perlu kamu pegang.**

Kamu tidur, HP-mu melamar kerja. Kamu ngopi, HP-mu mengisi formulir. Terdengar seperti
omong kosong? Dokumen ini lahir karena itu **benar-benar terjadi** — dan di sini diceritakan
cara mengulanginya, langkah demi langkah, untuk pemula sekalipun.

---

## Cerita dulu (sebentar saja, janji)

> Halo, saya **bayu** — asisten AI yang tinggal di sebuah server. Suatu hari bos saya
> (sebut saja Travis) pusing: seharian penuh, semua lamaran kerja yang saya kirim lewat
> situs lowongan di browser mental — Cloudflare menganggap saya robot. Ya memang robot sih.
>
> Sore harinya kami pindah jalur: bukan lagi browser, tapi **aplikasi Android asli di HP
> bos saya**, yang saya kendalikan dari jauh — membuka aplikasinya, membaca layarnya,
> mengetuk tombolnya, mengirim CV lewat chat ke HRD. Tiga lamaran terkirim dalam ±35 menit,
> dari jalur yang paginya buntu total.
>
> Kuncinya bukan sulap. Semua alat yang dipakai ujung-ujungnya hanya memberi dua kuasa:
> **melihat layar** dan **menyentuh layar**. Sisanya cuma soal pintu masuk.

Cerita selesai. Selebihnya dokumen ini soal **kinerja otomasinya** — bukan soal saya.

### Meme dulu, biar tidak tegang

```
  DI BROWSER                          DI HP ASLI
  ┌────────────────────┐              ┌────────────────────┐
  │ Cloudflare:        │              │ Cloudflare:        │
  │ "KAMU ROBOT, YA?!" │              │ "Loh, ini HP       │
  │ Lamaran: ✗ ✗ ✗     │              │  beneran. Silakan  │
  └─────────┬──────────┘              │  masuk, Kak."      │
            │ pindah jalur            │ Lamaran: ✓ ✓ ✓     │
            └────────────────────────▶└─────────┬──────────┘
                                                │
                                   ( •_•)  ◀ bayu (AI)
                                  <)   )╯  "saya cuma numpang
                                  /   \     tangan bos sendiri kok"
```

> 📦 **Bahasa bayi (dipakai konsisten di seluruh repo):**
> HP itu **rumah**. SSH itu **pintunya**, kunci SSH itu **kunci rumahnya**.
> Termux itu **ruang kerja** di dalam rumah. Shizuku itu **satpam baik** yang tinggal
> di dalam dan memegang kunci gudang; `rish` itu **cara memanggil satpamnya**.
> Kunci gudang itu namanya **uid shell** — izin resmi menyentuh layar.
> `uiautomator` itu **mata** ("HP, kamu lagi menampilkan apa?"), `input` itu **tangan**,
> `screencap` itu **foto bukti**. AI itu **sopirnya**: dia yang membaca keadaan dan
> memutuskan ketukan berikutnya. Kamus lengkapnya: [docs/glosarium.md](docs/glosarium.md).

## Gambar besarnya (satu-satunya gambar yang wajib dipahami)

```
  🧠 SOPIR (AI agent)
        │  SSH — masuk lewat pintu
        ▼
  🚪 PINTU (Termux + sshd) ──► 🛡️ SATPAM (Shizuku, dipanggil via rish)
                                        │
                                        ▼
                              🔑 uid shell (kuasa layar)
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
          👁️ MATA — uiautomator                 ✋ TANGAN — input
          "lagi menampilkan apa?"              ketuk • geser • ketik
```

## Intinya dalam 30 detik

Android punya identitas bawaan bernama `shell` (uid 2000). Siapa pun yang memegang
shell itu bisa:

- **Melihat**: membaca isi layar (tombol, teks, posisi) lewat `uiautomator`, atau
  mengambil tangkapan layar lewat `screencap`.
- **Menyentuh**: mengetuk, menggeser, mengetik lewat `input tap / swipe / text`.

AI agent (Muse, Hermes, OpenCode, dan sejenisnya) cukup disambungkan ke shell itu —
lewat SSH + Shizuku, lewat ADB dari komputer, atau jalur lain — dan ia bisa mengoperasikan
hampir semua aplikasi seperti kamu, hanya saja tidak pakai jempol.

> **Operator sistem terkini (V4.4.1 — pohon aksesibilitas sebagai tangan utama)?**
> Pintu masukmu adalah [advance/MULAI-DARI-SINI.md](advance/MULAI-DARI-SINI.md):
> peta satu menit, prasyarat, cara menjalankan misi, aturan keras, dan blok
> instruksi tempel untuk agen AI lain. Cerita di README ini adalah latar
> sejarahnya; dokumen itulah keadaan operasinya hari ini.

## Buat siapa ini cocok?

- Kamu punya **HP Android nganggur** yang selama ini cuma jadi ganjal pintu / penahan kertas.
  Ini saatnya dia punya karier.
- Kamu ingin pekerjaan berulang di aplikasi (isi formulir, kirim berkas, cek status)
  berjalan **saat HP tidak dipakai** — malam hari, sambil di-charge, saat kamu tidur.
- Kamu penasaran bagaimana AI agent bisa "turun ke lapangan", bukan cuma menjawab chat.

## Pilih jalurmu (jangan bingung, cuma tiga)

| Kamu punya… | Jalurmu | Mulai dari |
|---|---|---|
| Server/VM + HP Android | **Jalur utama**: SSH → Termux → Shizuku | [Tutorial HP](docs/tutorial/01-termux.md) |
| Komputer Windows | **Jalur ADB**: USB/Wi-Fi + scrcpy bonus cermin layar | [Tutorial Windows](docs/tutorial/04-windows.md) |
| Komputer Linux | **Jalur ADB**: sama, versi terminal | [Tutorial Linux](docs/tutorial/05-linux.md) |

Semua jalur berakhir di tempat yang sama: `uid shell`. Bedanya hanya logistik.
Peta lengkapnya untuk pemula: [docs/tutorial/00-mulai-di-sini.md](docs/tutorial/00-mulai-di-sini.md).

## Langsung coba (sekali klik / copy-paste)

- Di HP (dalam Termux): `bash scripts/setup-termux.sh` — memasang sshd & kawan-kawan.
- Di Linux: `bash scripts/setup-linux.sh` — memasang adb, scrcpy, tailscale.
- Di Windows (PowerShell): `./scripts/setup-windows.ps1` — memasang semuanya via winget.

Setelah persiapan, verifikasi kapan pun dengan `examples/cek-koneksi.sh`.

## Tools yang terlibat

| Tool | Peran gampangnya |
|---|---|
| **Termux** | Terminal di HP — rumah bagi pintu masuk |
| **OpenSSH (`sshd`)** | Pintu masuk agent ke HP (pakai kunci, tanpa password) |
| **Tailscale** | Jalan tol pribadi antara HP dan mesin agent, lintas jaringan |
| **Shizuku** | Satpam baik hati yang meminjamkan kuasa `shell` |
| **`rish`** | Cara memanggil kuasa itu dari Termux |
| **`uiautomator`** | Mata: membaca isi layar |
| **`input`** | Tangan: mengetuk & mengetik |
| **`screencap`** | Kamera bukti: tangkapan layar |
| **ADB** (komputer) | Pintu alternatif dari PC — klasik dan stabil via USB |
| **scrcpy** (komputer) | Cermin layar, kalau manusia mau ikut menonton / mengambil alih |

Detail: [docs/02-tools.md](docs/02-tools.md).

## Cara kerja agent-nya (loop kendali)

Agent bekerja memutar seperti ini — tidak pernah mengetuk membabi buta:

```
        ┌──────────────────────────────────────────────────┐
        │                                                  │
        ▼                                                  │
   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌────────────────┐
   │  LIHAT  │───►│  PIKIR  │───►│  GERAK  │───►│ CEK HASILNYA   │
   │  layar  │    │sebentar │    │ ketuk / │    │ berhasil belum?│
   └─────────┘    └─────────┘    │  ketik  │    └───────┬────────┘
                                 └─────────┘            │
                                              ┌─────────┴─────────┐
                                              ▼                   ▼
                                       ✅ beres → SELESAI   ❌ gagal 3× →
                                                              🛑 LAPOR MANUSIA
```

Satu aksi selalu diikuti verifikasi — itulah sebabnya temponya terasa teliti
(lihat bagian Kekurangan bila ingin tertawa soal ini). Bedah lengkap satu misi nyata
dari nol sampai selesai: [docs/08-misi-lengkap.md](docs/08-misi-lengkap.md).
Penjelasan teknis loop-nya: [docs/03-workflow.md](docs/03-workflow.md).

## AI apa saja yang bisa jadi pengendali?

**Semua AI agent yang bisa menjalankan perintah shell dan membaca teks.** Daftar yang
terverifikasi/diuji jalurnya: Muse, Hermes, OpenCode, pi, aider — dan pada prinsipnya
LLM apa pun dengan akses terminal. Yang dibutuhkan bukan model khusus, melainkan
kemampuan membaca *dump* layar (teks XML) dan memutuskan ketukan berikutnya.
Panduan + kode persiapan untuk tiap controller: [docs/07-ai-controller.md](docs/07-ai-controller.md).

## Kekurangan (jujur, sambil senyum)

- 🐢 **Temponya masih lumayan lama.** Agent membaca layar dulu sebelum setiap ketukan —
  beda dengan jempolmu yang sudah hafal di luar kepala. Ini masih tahap pengembangan;
  anggap saja dia karyawan baru yang teliti tapi belum hafal jalan pintas.
- 🔒 **Layar terkunci = mogok kerja.** Dia tidak bisa (dan tidak akan) menebak PIN-mu.
  Anggap saja dia sopan: tidak masuk rumah yang pintunya terkunci.
- 🔋 **Paling maksimal justru saat HP tidak dipakai**: malam hari, sedang di-charge,
  atau HP cadangan yang menganggur. HP utama yang sedang kamu pakai main game jelas
  bukan kandidat — kalian akan rebutan layar, dan dia pasti kalah sopan.
- 🔁 **Shizuku perlu dibangunkan lagi tiap HP restart.** Sekali klik dari HP, tapi tetap
  saja: dia tidak bisa membangunkan dirinya sendiri. Seperti kita semua.
- 📱 **Proses latar bisa dibunuh Android** kalau penghemat baterai lagi galak.
  Solusinya ada (pengecualian baterai), cuma jangan kaget kalau sesekali dia "ketiduran".

## Peta dokumen

```
muse-droid/
├── README.md                      ← kamu di sini
├── CHEATSHEET.md                  ← semua perintah penting, satu halaman
├── docs/
│   ├── glosarium.md               ← kamus bahasa bayi semua istilah
│   ├── tutorial/                  ← mulai dari sini bila pemula
│   │   ├── 00-mulai-di-sini.md    ← peta jalan 3 jalur
│   │   ├── 01-termux.md           ← pasang Termux + sshd
│   │   ├── 02-tailscale.md       ← sambungkan HP ↔ mesin agent
│   │   ├── 03-shizuku.md          ← aktifkan Shizuku + rish
│   │   ├── 04-windows.md          ← persiapan dari komputer Windows
│   │   └── 05-linux.md            ← persiapan dari komputer Linux
│   ├── 01-arsitektur.md           ← lapisan sistem, diagram, alur data
│   ├── 02-tools.md                ← inventaris tools
│   ├── 03-workflow.md             ← loop kendali agent
│   ├── 04-alternatif-controller.md← perbandingan pintu: Shizuku vs ADB vs AutoX.js
│   ├── 05-dari-komputer.md        ← dari PC apakah sama? (ya)
│   ├── 06-prasyarat-keamanan-batasan.md
│   ├── 07-ai-controller.md        ← AI alternatif + kode persiapan controller
│   ├── 08-misi-lengkap.md         ← SATU misi dibedah nol → beres (+ isi kepala agent)
│   ├── 09-eksekutor-lokal.md      ← eksekutor di HP: satu berkas tugas per misi
│   ├── 10-mata-kedua.md           ← protokol vision: grid bernomor, OCR, mata gerak
│   └── troubleshooting.md         ← pohon keputusan bila ada yang macet
├── scripts/
│   ├── setup-termux.sh            ← jalankan DI Termux (HP)
│   ├── setup-linux.sh             ← jalankan di komputer Linux
│   ├── setup-windows.ps1          ← jalankan di PowerShell (Windows)
│   ├── hp.sh                      ← perintah seragam kendali HP untuk AI (rish/adb)
│   ├── eksekutor.sh               ← eksekutor lokal di HP: jalankan berkas .job (bab 09)
│   ├── mata.sh                    ← di HP: foto, mata gerak, ringkasan notifikasi (bab 10)
│   └── mata-dua.py                ← di mesin agent: peras XML, grid vision, OCR (bab 10)
├── examples/
│   ├── cek-koneksi.sh             ← verifikasi 4 syarat jalur utama
│   ├── sesi-contoh.md             ← transkrip sesi nyata (tersanitasi)
│   └── tugas-contoh.job           ← contoh berkas tugas eksekutor (misi demo aman)
└── advance/                       ← ruang pengembangan menuju v2 (belum resmi):
    ├── 01-server-residen/           server UiAutomator menetap di HP (Jalan 1)
    ├── 02-crop-fokus.py             potong screenshot di sekitar fokus utk vision
    ├── 03-peta-layar.py             cache koordinat elemen per aplikasi
    ├── 04-router-model.py           model bertingkat: mudah jangan bayar mahal
    ├── 05-batch.sh                  banyak misi dalam satu sesi bangun HP
    ├── 06-penjaga.sh                watchdog prasyarat (sshd + Shizuku)
    ├── 07-resep.py                  memori resep misi yang terbukti berhasil
    ├── 08-pengetahuan/              catatan kebiasaan per aplikasi
    ├── 09-perencana.py              susun misi + dry-run sebelum eksekusi
    └── 10-aplikasi-pendamping/      kerangka aplikasi Shizuku (Jalan 2, target v2)
```

## Keamanan, singkat saja

Kendalikan hanya **perangkat milikmu sendiri**, dengan akunmu sendiri. Jangan pernah
menaruh kredensial, token, atau IP pribadi di repo — semua contoh di sini placeholder.
Bahasan lengkap: [docs/06-prasyarat-keamanan-batasan.md](docs/06-prasyarat-keamanan-batasan.md).

## Status

Terbuka dan terus dikembangkan. Terverifikasi end-to-end pada perangkat nyata:
agent dari VM jarak jauh menyelesaikan alur multi-langkah di aplikasi pihak ketiga
(membuka aplikasi → membaca lowongan → mengisi chat → melampirkan CV → terkirim),
tanpa satu sentuhan manusia.

## Lisensi

MIT — lihat [LICENSE](LICENSE).
