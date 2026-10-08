# 16 — Misi Ad-Hoc Generik (playbook + runner)

Untuk tugas dadakan di aplikasi yang **belum punya misi khusus**: agen
menyusun berkas `.job` pendek dari hasil rekognisi, `misi-ad-hoc.py`
menjalankan perjalanan deterministiknya **di dalam HP**, dan titik
keputusan — terutama langkah destruktif — tetap di tangan agen.

Latar: selama ini aplikasi selain Glints dikemudikan interaktif dari
jarak jauh (amati → bertindak, 15–25 detik per langkah, didominasi
pulang-pergi SSH + screenshot). Misi khusus (advance/12) memangkas itu
untuk Glints, tetapi menulis misi khusus untuk setiap tugas sekali
jalan tidak masuk akal. Paket ini menggeneralisasi polanya.

> Status: **TERUJI di perangkat nyata 8 Okt 2026** — hasil lengkap di
> `advance/PENGUJIAN.md` Fase 17. Misi `uji-adhoc-settings.job` di
> Pengaturan Android **LULUS 8/8 langkah** dalam **24,62 dtk** pada
> mode pohon: `BUKA_APLIKASI` → `TUNGGU_TEKS` → ketuk ikon cari →
> `ISI_TEKS "bluetooth"` → `TUNGGU`/`CEK "Bluetooth"` → `FOTO`.
> `TUNGGU_TEKS` terukur **8 ms** dan `CEK_TEKS` **7 ms**. Catatan
> jujur: `ISI_TEKS` via pohon sempat gagal karena snapshot belum
> menangkap fokus kolom (balapan timing), lalu jatuh ke `input text`
> rish yang terverifikasi; poles V4.1 adalah menunggu versi snapshot
> naik/fokus muncul maks 600 ms sebelum fallback. Daftar di akhir
> dokumen kini dibaca sebagai cakupan uji lanjutan, bukan bukti bahwa
> misi dasar belum pernah jalan.

## Isi

- `misi-ad-hoc.py` — runner: satu proses Python persisten di HP,
  bahasa `.job` kompatibel `misi-cepat.py` (advance/11) ditambah
  `BUKA_APLIKASI <paket>` dan `ISI_TEKS <teks>`. Setiap langkah dicatat
  durasinya (ms) di log, sama seperti misi-cepat.
- `template-adhoc.job` — kerangka misi kosong berkomentar untuk
  aplikasi sembarang; titik awal setiap tugas ad-hoc.

## Kapan misi ad-hoc, kapan misi khusus

| Situasi | Pakai |
|---|---|
| Tugas berulang, jalurnya deterministik (mis. navigasi lowongan Glints) | **Misi khusus** (advance/12): template + generator, teruji per fase |
| Tugas sekali jalan / dadakan di aplikasi tanpa misi khusus | **Misi ad-hoc** (paket ini) |
| Eksplorasi aplikasi baru: melihat struktur layar sebelum memutuskan otomasi | **Misi ad-hoc** pendek (BUKA_APLIKASI + CEK_TEKS + FOTO) |
| Isian formulir panjang yang tata letaknya bergeser | Ad-hoc **satu ketukan per berkas** + verifikasi agen di antaranya (lihat aturan formulir) |
| Tugas ad-hoc yang sama terulang ≥ 3 kali | Promosikan jadi misi khusus: bekukan `.job`-nya, tulis template + uji fasenya |

Pembagian kerja tidak berubah: misi (khusus maupun ad-hoc) hanya
menjalankan perjalanan; **titik keputusan tetap di agen** — verifikasi
keadaan, penilaian isi, dan semua langkah destruktif.

## Alur kerja (4 tahap)

1. **Rekognisi.** Sebelum menulis satu baris pun: ambil dump teks
   dan/atau screenshot SEGAR dari layar yang akan disentuh. Catat tiga
   hal — nama paket aplikasi, teks jangkar yang unik di tiap layar
   tujuan, dan geometri hanya bila terpaksa (koordinat buta adalah
   pilihan terakhir). Jangan menyusun misi dari ingatan atau tangkapan
   lama: salinan pohon dan dump sama-sama bisa basi.
2. **Susun `.job`.** Mulai dari `template-adhoc.job`. `TARGET <paket>`
   selalu baris pertama yang aktif. Langkah sekecil mungkin, jangkar
   teks sespesifik mungkin (`TUNGGU_TEKS`/`CEK_TEKS` mengapit setiap
   perpindahan layar). Berhenti **sebelum** langkah destruktif.
3. **Jalankan.** `python3 misi-ad-hoc.py <berkas.job>` di HP. Baris
   `MULAI` log menyatakan mode observasi yang benar-benar dipakai
   (pohon/dump/jembatan) — bila mode-nya di bawah harapan, itu fakta
   yang harus terbaca, bukan ditebak dari kecepatan.
4. **Verifikasi.** Agen membaca log sampai `BERES` (atau `GAGAL`
   langkah ke berapa dan kenapa), memastikan `CEK_TEKS` penutup lolos,
   dan mengambil screenshot bukti untuk keadaan akhir yang penting.
   Misi yang `GAGAL` tidak diulang buta: rekognisi ulang dulu.

## Observasi berlapis & aturan kebenaran

Runner mengobservasi lewat lapisan tercepat yang hidup, dan turun
kelas dengan jujur (tercatat di log) bila lapisan itu mati:

1. **Server pohon** (aplikasi pendamping, TCP 127.0.0.1:19102) —
   menjawab `CARI`/`TEKS?`/`PAKET?` dari salinan pohon aksesibilitas
   yang dipelihara dari peristiwa: milidetik, tanpa dump. `ISI`
   melakukan set-text pada node edit yang sedang fokus.
2. **Dump uiautomator2** (127.0.0.1:9008) — kebenaran dasar per
   langkah, identik perilaku misi-cepat.
3. **Jembatan rish** — `uiautomator dump` + `input` via rish/Shizuku;
   lambat, hanya darurat.

Aturan `DESAIN-V3-POHON-UI.md` §4 yang **ditegakkan runner di kode**:

- Jawaban pohon membawa `umur_ms` + `versi`. Umur **> 500 ms ditolak**
  sebagai dasar langkah pengubah layar: koordinat `KETUK_TEKS`
  dikueri ulang, tetap basi → dump segar yang memutuskan.
- Sesudah ketukan, keadaan baru hanya dipercaya bila **versi pohon
  naik** dari versi pra-ketuk (gerbang versi di `TUNGGU_TEKS`/
  `CEK_TEKS`). Versi tidak naik dalam 1,2 dtk → verifikasi dialihkan
  ke dump cadangan, tercatat di log.
- Penjaga `TARGET`: paket depan dibaca murah dari `PAKET?` dan
  **dikonfirmasi dump pada langkah buta pertama**; paket berpindah
  tangan → langkah buta dibatalkan jujur.
- `ISI_TEKS` yang mengaku berhasil tetapi teksnya tidak terlihat =
  misi berhenti jujur — tidak jatuh ke `KETIK` (risiko ketik ganda).

## Aturan formulir yang tata letaknya bergeser

Warisan disiplin formulir Glints (advance/12): sesudah satu jawaban,
posisi pertanyaan berikutnya berubah. Karena itu untuk formulir:

- **Satu ketukan per putaran.** Satu `.job` hanya boleh memuat satu
  tindakan pengisi/penjawab, diakhiri `CEK_TEKS` atas keadaan hasil.
- Agen **memverifikasi dari dump/screenshot segar** sebelum menyusun
  `.job` putaran berikutnya — atribut terpilih/terisi dibaca dari
  dump, bukan dari asumsi urutan.
- Jangan pernah merangkai banyak isian formulir dalam satu berkas
  buta, dan jangan menekan tombol lanjut/kirim dari rangkaian seperti
  itu. Tombol lanjut pun satu putaran tersendiri sesudah verifikasi.

## Larangan: langkah destruktif dari salinan pohon

Kirim formulir, konfirmasi pembayaran, hapus entri, keluar akun —
langkah destruktif/sensitif **tidak pernah** diputuskan dari salinan
pohon, dan misi ad-hoc **berhenti tepat sebelum** langkah itu. Agen
memutuskan dari dump segar atau screenshot verifikasi (disiplin yang
sama dengan `DESAIN-V3-POHON-UI.md` §4), lalu mengeksekusi langkah
terakhirnya sendiri secara interaktif. Alasannya praktis: salinan bisa
terlewat satu peristiwa; dialog konfirmasi yang tidak terpetakan
adalah tempat termahal untuk salah.

## Direktif yang didukung

Kompatibel misi-cepat: `TARGET`, `BUKA`, `TAUTAN`, `TUNGGU_TEKS`,
`KETUK_TEKS`, `KETUK x y`, `GESER x1 y1 x2 y2 [ms]`, `KETIK`, `TEMPEL`,
`TOMBOL`, `JEDA`, `FOTO`. Baru di sini:

| Direktif | Makna |
|---|---|
| `BUKA_APLIKASI <paket>` | Buka aplikasi dari nama paket; activity dicari runner via `cmd package resolve-activity` (cadangan: monkey). Menunggu paket benar-benar di depan. |
| `ISI_TEKS <teks>` | Fokus kolom edit lewat ketuk, lalu perintah `ISI` ke server pohon (set-text node hidup). Cadangan berjenjang: `KETIK` (input text terverifikasi → `TEMPEL`). |

## Studi kasus "sebelum": LinkedIn, 8 Okt 2026

Pemilik HP meminta satu entri pengalaman yang keliru di aplikasi
LinkedIn dihapus. Tanpa playbook ini, agen mengemudikan dari jarak
jauh per screenshot: membuka aplikasi, menutup sheet notifikasi yang
muncul, membuka laci profil, masuk halaman profil, menggulir ke seksi
pengalaman, membuka entri, mengetuk ikon hapus, sampai dialog
konfirmasi muncul — **±9 menit** pulang-pergi untuk pekerjaan yang
isinya ±8 langkah deterministik ditambah **satu** titik keputusan
(tombol hapus pada dialog). Dengan playbook ad-hoc, bagian
deterministiknya menjadi satu berkas `.job` pendek
(`BUKA_APLIKASI` → `TUNGGU_TEKS` → gulir → `KETUK_TEKS` entri → ikon
hapus) yang berhenti tepat sebelum dialog konfirmasi; agen memeriksa
screenshot segar, lalu memutuskan sendiri langkah destruktifnya.
Perjalanan yang sama menjadi pekerjaan runner belasan detik (perkiraan
dari angka advance/11–12) plus satu keputusan agen — dan pola yang
sama berlaku untuk aplikasi berikutnya, apa pun itu.

## Prasyarat & pakai

- Di HP (Termux): server pohon pendamping di 19102 dan/atau server
  residen u2 di 9008 hidup (penjaga kaki advance/13 menjaganya);
  jembatan darurat butuh rish/Shizuku.
- `python3 misi-ad-hoc.py <berkas.job>` — kode keluar 0 = beres,
  1 = gagal di langkah tercatat, 2 = salah pakai.

## Yang masih harus diuji di perangkat (belum dilakukan)

1. Mode pohon penuh: misi template di satu aplikasi non-Glints —
   `CARI` segar vs basi (umur > 500 ms harus tertolak & jatuh ke
   dump), gerbang versi pada `TUNGGU_TEKS` sesudah ketuk.
2. `ISI_TEKS` end-to-end: fokus lewat ketuk → `ISI` → verifikasi;
   dan jalur cadangannya (server pohon menolak `ISI` → `KETIK`).
3. Turun kelas di tengah misi: matikan layanan pohon saat misi jalan
   → log harus mencatat transisi dan misi tetap beres via dump.
4. `BUKA_APLIKASI` pada 3 aplikasi berbeda (resolve-activity vs jalur
   monkey) + penjaga TARGET saat paket berpindah tangan di tengah misi.
5. Benchmark misi standar advance/11 dijalankan misi-ad-hoc mode
   pohon vs mode dump — selisihnya adalah bukti nilai server pohon.
