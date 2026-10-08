# advance/ — Ruang Pengembangan Menuju v2

Semua yang ada di folder ini adalah **peningkatan yang masih tahap
pengembangan**: sudah ditulis dan ditata, **belum** menjadi bagian resmi
muse-droid, dan **belum semuanya diuji di perangkat**. Aturannya sederhana:

- Tidak ada skrip produksi (`scripts/`) yang bergantung pada isi folder ini.
- Sesuatu lulus dari sini hanya setelah diuji langsung di HP dan terbukti —
  lalu ia dipindah ke `scripts/`/`docs/` dan dicatat di riwayat versi.
- Urutan uji yang disarankan mengikuti nomornya.
- **Jurnal pengembangan lengkap** — progres, tantangan, workflow, cara pikir, angka benchmark, bacaan pendamping, dan roadmap: [`LOG-PEMBAHARUAN.md`](LOG-PEMBAHARUAN.md). Ditulis untuk pembaca lanjut & calon pengembang; pemula tidak perlu membacanya.

## Papan status

| # | Peningkatan | Isi | Bentuk | Bukti yang dibutuhkan untuk lulus |
|---|---|---|---|---|
| 01 | Server residen di HP (Jalan 1) | `01-server-residen/` | Skrip + klien Python | **Teruji ✓ 8 Okt** — resep benar dari sumber uiautomator2 (u2.jar + com.wetest.uia2.Main): PING 0,01 dtk, DUMP 0,56 dtk (±20–35× cara lama); `mulai-server.sh` ditulis ulang. PENGUJIAN.md Fase 8 |
| 02 | Crop fokus untuk vision | `02-crop-fokus.py` | Alat Python (PIL) | **Teruji ✓ 8 Okt** — 2 target berglif jelas: selisih 8px & 23px (ambang 30px); kasus tepi: node teks selebar baris. PENGUJIAN.md Fase 4 |
| 03 | Peta layar tersimpan | `03-peta-layar.py` | Alat Python + JSON | **Teruji ✓ 8 Okt** — catat/cari/lupakan persis; ketuk basi (daftar dinamis) pulih lewat alur resminya. PENGUJIAN.md Fase 5 |
| 04 | Router model bertingkat | `04-router-model.py` | Kebijakan + klasifikasi | **DIUJI 7 Okt: LULUS BERSYARAT** — klasifikasi 10/10; RUTIN & VISION terhubung nyata; tier RENCANA `utama` butuh anggaran token besar. PENGUJIAN.md Fase 7 |
| 05 | Batch banyak misi satu sesi | `05-batch.sh` | Skrip Termux | **Teruji ✓ 8 Okt** — 3/3 beres; batch 93 dtk vs 97 dtk terpisah (dinding). PENGUJIAN.md Fase 3 |
| 06 | Penjaga prasyarat (watchdog) | `06-penjaga.sh` | Skrip Termux | **LULUS UJI PERANGKAT 7 Okt** — sshd dibunuh paksa, hidup lagi ≤1 siklus, status akurat. PENGUJIAN.md Fase 1 |
| 07 | Memori resep | `07-resep.py` + `resep/` | Alat Python | **Teruji ✓ 8 Okt** — resep "buka-layar" dipakai ulang (parameter Bluetooth) & beres. PENGUJIAN.md Fase 6 |
| 08 | Basis pengetahuan per aplikasi | `08-pengetahuan/` | Berkas catatan | Terisi dari pengalaman; dibaca sebelum misi |
| 09 | Perencana + dry-run | `09-perencana.py` | Alat Python | **Teruji ✓ 8 Okt** — rantai penuh susun→uji (negatif tertangkap)→jalan→simpan→pakai→jalan. PENGUJIAN.md Fase 6 |
| 10 | Aplikasi pendamping Shizuku (Jalan 2) | `10-aplikasi-pendamping/` | Kotlin + AIDL + `build.sh` | **TUNTAS 8 Okt** — terdaftar & terotorisasi di Shizuku (kunci: deklarasi API_V23), status "Siap", popup izin otomatis, **UserService tersambung: UID 2000, DUMP XML asli, KETUK/TOMBOL nyata** via socket 127.0.0.1:19101. PENGUJIAN.md Fase 9 + sesi percepatan |
| 11 | Runner makro residen + kueri terarah | `11-makro-residen/` | Python (persisten, keep-alive) | **TERUJI 8 Okt** — roadmap jurnal butir 1+2 diterapkan: misi standar 9 langkah **47,8 → 22,3 dtk (2,1×)**; desain butir 4 (pohon UI tersimpan) di `DESAIN-V3-POHON-UI.md`. PENGUJIAN.md Fase 11 |
| 12 | Misi navigasi Glints | `12-navigasi-glints/` | Template .job + generator Python | **TERUJI 8 Okt** — misi pencarian perusahaan 8 langkah **12,6 dtk** (perjalanan yang sama ±4–5 mnt secara interaktif); direktif baru `TAUTAN` (deep link) + strategi KETIK diperbaiki di misi-cepat. PENGUJIAN.md Fase 12 |
| 13 | Penjaga kaki residen | `13-penjaga-kaki/` | Bash (loop 60 dtk di HP) | **TERUJI 8 Okt + DIPERBARUI V4.0** — uji bunuh server residen: pulih **±91 dtk** tanpa manusia; notifikasi kematian Shizuku teruji via simulasi + probe ganda anti-alarm-palsu. Versi V4.0 memantau 4 kaki (pohon 19102, u2, rish, pendamping 19101), menahan kebangkitan u2 selama pohon hidup, dan menegakkan eksklusivitas pohon–u2. PENGUJIAN.md Fase 13 + Fase 16 |
| 14 | Versi & gambaran konfigurasi | `14-versi-dan-konfigurasi/` | Dokumen | **SELESAI 8 Okt** — skema versi V1.0/V2.0/V3.0 + tag git; KONFIGURASI-HP.md tersanitasi (peta alur, tata letak HP, SSH ControlMaster, urutan pemulihan). PENGUJIAN.md Fase 14 |
| 15 | Pohon UI aksesibilitas + layanan depan | `15-pohon-ui-aksesibilitas/` | Dokumen + rujukan kode di `10-aplikasi-pendamping/` | **TERUJI 8 Okt** — layanan terikat sesudah reboot menyembuhkan AMS macet global; PING 7–32 ms; umur salinan 32 ms–0,4 dtk; CARI akurat untuk simpul terlihat; pohon & u2 eksklusif (pohon utama, u2 cadangan on-demand). PENGUJIAN.md Fase 15 |
| 16 | Misi ad-hoc generik | `16-misi-ad-hoc/` | Runner Python + template `.job` | **TERUJI 8 Okt** — misi Pengaturan Android LULUS 8/8 dalam 24,62 dtk mode pohon; TUNGGU_TEKS 8 ms, CEK_TEKS 7 ms; catatan: ISI_TEKS pohon sempat jatuh ke input text rish terverifikasi. PENGUJIAN.md Fase 17 |

## Kenapa tidak langsung jadi v2?

Karena v1 mengajarkan satu hal: yang membuat alat ini bisa dipercaya bukan
banyaknya fitur, melainkan bahwa **setiap klaimnya pernah dibuktikan di
perangkat nyata** (lihat docs/09 & docs/10 — semua angka di sana hasil uji).
Folder ini menjaga standar itu: ide boleh masuk cepat, klaim "sudah bisa"
harus menunggu bukti.
