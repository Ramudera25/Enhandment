# DESAIN V5 — "Sembuh Sendiri" (ketahanan penuh)

Status: DRAF DESAIN (9 Okt 2026, bayu). Belum ada kode. Versi V5 hanya
dinyatakan bila uji penerimaan di bagian akhir lulus di perangkat.

## 1. Tujuan

Musuh terbesar Enhandment bukan kecepatan langkah, melainkan kendali
yang TUMBANG: layanan pohon mati, salinan membeku sesudah layar mati,
ikatan aksesibilitas lepas, aplikasi ter-uninstall di tengah perbaikan.
Pada 8-9 Okt sebagian besar jam kerja habis untuk menghidupkan alat,
bukan memakainya. V5 membuat tumpukan kendali menyembuhkan dirinya
sendiri bertingkat, dan hanya memanggil manusia pada anak tangga
terakhir yang memang tidak bisa diotomatiskan.

Definisi lulus (uji penerimaan, semua tanpa sentuhan manusia):
pohon dibunuh tiga cara — (a) force-stop aplikasi pendamping,
(b) salinan dibekukan lewat episode layar mati, (c) layanan dimatikan
dari pengaturan aksesibilitas — dan sistem kembali menjawab PING
19102 dengan versi pohon BERGERAK dalam <= 5 menit untuk ketiganya.

## 2. Pola referensi yang dipinjam (tata bahasa, bukan kode)

- Home Assistant: tangga watchdog — deteksi, perbaiki bertingkat,
  eskalasi ke manusia hanya bila semua tangga gagal, dan setiap
  tindakan tercatat. Penjaga kaki kita sekarang baru sampai
  "deteksi + lapor"; V5 melengkapi tangganya.
- Tasker/MacroDroid: prasyarat sebelum aksi (pemicu -> syarat ->
  aksi). Misi hanya dimulai bila syarat kesehatan terpenuhi; misi
  yang ditolak prasyaratnya menulis alasan, bukan berjalan untuk
  gagal.
- Automate: langkah yang bercabang. Kegagalan satu langkah tidak
  selalu mematikan misi; format misi v2 membawa kebijakan per
  langkah.
- IFTTT: hanya kemasannya — satu otomatisasi = satu resep bernama
  jelas yang bisa dibagikan (perpustakaan misi di repo ini).

Yang SENGAJA tidak dipinjam: pemicu awan (latensi + ketergantungan),
mesin pihak lain (masalah tersulit kita adalah perut Android di
perangkat ini: ikatan, binder, pembunuhan proses oleh One UI —
tidak ada referensi yang menyelesaikannya untuk kita).

## 3. Arsitektur

### 3.1 Detektor kesehatan (di aplikasi pendamping)
- Detak: layanan pohon mencatat waktu kejadian terakhir + versi.
  Detektor membedakan tiga keadaan yang selama ini tertukar:
  (1) SEHAT — versi bergerak atau layar memang diam wajar;
  (2) BEKU — layar menyala/berubah tapi versi diam melewati ambang
  (pola terbukti 9 Okt: beku sesudah episode layar mati);
  (3) MATI — socket menolak / layanan tidak terikat.
- Sumber kebenaran keadaan: gabungan socket 19102 + dumpsys
  accessibility (Bound?) + wakefulness. Tidak pernah vonis dari
  satu lapis saja (aturan yang lahir dari dump fosil 9 Okt).

### 3.2 Penjaga v2 — tangga pemulihan otomatis
- Anak tangga 1 (ringan): gerakan global via pohon (GLOBAL HOME)
  untuk melepas beku; verifikasi versi bergerak <= 30 detik.
- Anak tangga 2 (sedang): tulis ulang pengaturan aksesibilitas +
  jalankan MainActivity; tunggu ikatan <= 90 detik, verifikasi PING.
- Anak tangga 3 (berat, butuh kanal istimewa/Shizuku hidup):
  force-stop pendamping lalu ulangi tangga 2; bila paket hilang,
  pasang ulang dari APK cadangan yang tersimpan di perangkat.
- Anak tangga 4 (eskalasi manusia): berhenti mencoba, kirim
  notifikasi yang menyebut SATU tindakan persis yang dibutuhkan
  (mis. "tekan Mulai di aplikasi Shizuku") — bukan laporan umum.
- Setiap anak tangga: maksimal percobaan, jeda membesar, semua
  tercatat di log penjaga dengan cap waktu dan hasil verifikasi.
  Tidak ada anak tangga yang memakai dump UiAutomation/u2 saat
  pohon terikat (aturan A1 tetap berlaku).

### 3.3 Gerbang prasyarat misi (di runner)
Sebelum langkah pertama, runner memeriksa dan menulis hasilnya:
versi pohon bergerak (bukan hanya PING menjawab); baterai di atas
ambang atau sedang mengisi; tidak ada penanda sesi operator lain
yang masih segar; aplikasi target dalam keadaan awal yang
dibutuhkan misi (dingin, atau halaman terverifikasi dari isi
pohon — bukan dari paket saja; jebakan BUKA 9 Okt). Gagal gerbang
= misi ditolak dengan alasan tertulis di berkas .hasil.

### 3.4 Format misi v2 (subset minimal)
- Kepala misi: prasyarat (baterai minimum, aplikasi target).
- Per langkah: batas waktu sendiri + kebijakan gagal:
  `henti` (bawaan), `lanjut`, atau `ke <label>`.
- TEMPEL dinyatakan usang; padanannya ISI (terbukti 9 Okt).
  misi-uji-standar diperbarui ke v2 sesudah format ini lulus uji.

## 4. Batasan jujur

- Menyalakan server Shizuku tetap butuh ketukan manusia (pairing
  tersimpan). Tangga 3 hanya bekerja bila Shizuku hidup; bila mati,
  eskalasi langsung ke tangga 4 dengan permintaan yang tepat.
- Izin "restricted settings" untuk aplikasi sideload sesudah install
  ulang besar bisa membutuhkan persetujuan pemilik sekali; desain
  tidak mencoba mengakali gerbang keamanan Android.
- One UI tetap bisa membunuh proses dengan cara baru; desain ini
  memangkas waktu pulih dan menghilangkan kebutuhan operator,
  bukan menjanjikan kematian proses tidak terjadi lagi.

## 5. Tahapan pembangunan (tiap fase teruji sendiri)

- Fase A — Detektor + gerbang prasyarat (mode amati saja):
  penjaga mencatat vonis BEKU/MATI dan ketepatannya diverifikasi
  manual selama 24 jam tanpa tindakan otomatis.
- Fase B — Tangga 1-2 otomatis + eskalasi tangga 4.
- Fase C — Tangga 3 (pasang ulang dari APK cadangan) + uji
  penerimaan tiga cara membunuh. Lulus Fase C = tag V5.

## 6. Di luar cakupan

Perencana bahasa manusia (Skenario 4), mata OCR (Skenario 3),
antrean misi terjadwal penuh (Skenario 2 — sebagian kecilnya,
gerbang prasyarat, adalah prasyarat V5 ini), dan armada banyak
perangkat (Skenario 5). Masing-masing skenario terpisah.
