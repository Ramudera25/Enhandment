# DESAIN V4.4 — "Mata Baca" (OCR di perangkat)

Status: desain resmi, menunggu implementasi · Ditulis 11 Oktober 2026
Dasar bukti: prototipe OCR terverifikasi di VM (laporan `enhandment-ocr-proto/LAPORAN.md` di workspace VM): model PP-OCRv5 mobile deteksi + pengenal Latin, total unduhan 12,73 MB, latensi rata-rata 1,23 detik/bingkai di CPU x86, akurasi teks UI Bahasa Indonesia 55/57 baris terbaca persis (96,5%), 2 sebagian, 0 salah total; seluruh 11 kesalahan adalah positif palsu ikon non-teks.

## Tujuan

Melengkapi perintah BINGKAI/AMBIL (V4.3) dengan kemampuan MEMBACA isi bingkai sebagai teks berkoordinat, agar layar yang pohon aksesibilitasnya kosong atau miskin (WebView, kanvas, daftar yang dirender gambar) tetap bisa dipahami dan ditindaklanjuti secara terverifikasi.

## Definisi lulus (uji penerimaan)

1. Perintah baru `BACA` di socket 19102 mengembalikan hasil OCR bingkai segar: header JSON satu baris (`ok`, `versi_bingkai`, `latensi_ms`, `jumlah_baris`) diikuti baris hasil format `teks <TAB> x1,y1,x2,y2 <TAB> skor`.
2. Uji hidup di Samsung A13 pada 3 layar nyata — beranda tamu KitaLulus, halaman grup Facebook, satu layar WebView/kanvas — teks utama tiap layar terbaca persis (penilaian manual terhadap bingkai yang sama).
3. Latensi A13 terukur atas ≥5 bingkai dan tercatat apa adanya; target layak ≤4 detik/bingkai (OCR adalah penasihat sesuai permintaan, bukan jalur per-langkah misi).
4. Regresi: seluruh baterai perintah V4.2/V4.3 (PING, PAKET?, TEKS?, CARI, POHON, ISI, KETUK, TAHAN, GESER, GLOBAL, TOMBOL, BINGKAI, AMBIL) sehat sesudah upgrade; pemasangan `install -r` dari V4.3.2 tanpa uninstall, ditandatangani kunci kanonis proyek.
5. Penyaring positif-palsu v1 aktif dan teruji pada bingkai uji standar: baris simbol ≤2 karakter dibuang; zona status bar (pita atas layar) diabaikan kecuali diminta eksplisit; ambang skor minimum dapat diatur.

## Keputusan arsitektur

- **Model:** PP-OCRv5 mobile — deteksi `ch_PP-OCRv5_det_mobile.onnx` (4.819.576 B) + pengenal Latin `latin_PP-OCRv5_rec_mobile.onnx` (7.904.513 B) + kamus Latin (1.634 B) + model klasifikasi arah bawaan pipeline (585.532 B). Total di cakram ±13,31 MB. Lisensi Apache-2.0 (PaddleOCR & RapidOCR). SHA256 kedua berkas utama cocok dengan `default_models.yaml` resmi RapidOCR (tercatat di laporan prototipe).
- **Runtime:** ONNX Runtime Mobile (AAR) di dalam aplikasi pendamping; integrasi build mengikuti pola AAR Shizuku yang sudah dipakai toolchain `musedroid-app` (kotlinc → d8 → aapt2 → zipalign → apksigner). Model dibundel sebagai aset aplikasi; APK membesar ±13 MB — diterima.
- **Penempatan utama: di perangkat.** Bingkai tidak pernah keluar HP untuk dibaca; OCR tetap jalan tanpa jaringan. **Cadangan terdokumentasi:** OCR sisi server di VM lewat bingkai yang sudah ada (terbukti 1,23 detik/bingkai) — hanya dipakai bila angka latensi A13 gagal target pada uji penerimaan butir 3; pergantian keputusan wajib berdasar angka itu, bukan selera.
- **Doktrin pemakaian (warisan V4.3, tidak berubah):** pohon aksesibilitas tetap hakim untuk keputusan mengetuk; OCR adalah penasihat. Koordinat hasil OCR hanya boleh dipakai bila pohon tidak memiliki targetnya; setiap ketuk berbasis OCR wajib diverifikasi sesudahnya (versi salinan pohon naik dan/atau bingkai sesudah berubah) dan dicatat sebagai aksi berlabel keyakinan-OCR. OCR hanya sesuai permintaan — tidak ada OCR otomatis per ganti bingkai — dan mati sendiri pada baterai <30% tanpa cas (pengaman warisan desain Mata).
- **Klien:** perluasan peralatan di `advance/15` — klien `baca-layar.py` yang meminta BACA dan mencetak baris teks + koordinat, sejajar dengan `ambil-bingkai.py`.

## Risiko & mitigasi

- Positif palsu ikon (baterai terbaca "0", centang terbaca "V", skor keyakinan bisa tetap tinggi 0,95–1,0): mitigasi = penyaring v1 (butir 5) + silang-cek pohon sebelum bertindak; skor model TIDAK pernah jadi bukti tunggal.
- Latensi A13 belum diketahui (angka prototipe dari CPU x86 VM): gerbang angka pada uji penerimaan butir 3; cadangan server sudah terbukti bila gagal.
- Layar FLAG_SECURE tetap menolak tangkapan (batas desain Android): di luar cakupan, tidak diakali.

## Urutan kerja

1. Integrasi runtime + model dan perintah BACA di aplikasi pendamping (salinan kerja `musedroid-app`, lalu sinkron ke `advance/10-aplikasi-pendamping`).
2. Klien `baca-layar.py` di `advance/15`.
3. Uji hidup A13 + baterai regresi; dokumentasi hasil di PENGUJIAN.md.
4. Tag `v4.4` hanya sesudah definisi lulus terpenuhi di perangkat.

## Bukan cakupan

OCR otomatis terus-menerus, penerjemahan teks, model grounding visual (jalur upgrade terpisah), dan perubahan runner misi (paket V5/verifier). Tidak ada perubahan pada protokol V4.3 selain penambahan perintah BACA.

## Adendum 11 Okt 2026 — hasil uji & keputusan penempatan

Uji perangkat tuntas (catatan lengkap di advance/PENGUJIAN.md
bagian V4.4/V4.4.1). Ringkasnya: BACA akurat tetapi latensi
perangkat 19–40 dtk/bingkai pada semua konfigurasi terukur —
target ≤4 dtk pada butir 3 GAGAL, dan V4.4.1 (plafon resize
deteksi 960 yang semula terlewat) tidak menutup jurangnya.
Sesuai klausa butir 3, penempatan utama RESMI pindah:

- **Jalur utama: OCR sisi server.** BINGKAI (V4.3) dari HP,
  PP-OCRv5 di VM lewat `advance/15/baca-server.py` — keluaran
  format yang sama dengan BACA. Terukur 1,98–3,24 dtk per
  bingkai aplikasi biasa; Facebook padat 6,56 dtk.
- **BACA di perangkat: cadangan luring terakhir** — dipertahankan
  di aplikasi (V4.4.1, kode 47) untuk keadaan tanpa jalur ke VM,
  dengan kesadaran penuh latensinya kelas puluhan detik.
- Konsekuensi privasi diterima sadar: pada jalur utama bingkai
  KELUAR dari HP ke VM milik Travis sendiri lewat Tailscale —
  pengecualian terbatas pada bingkai yang diminta perintah BACA,
  bukan aliran layar. Doktrin butir 5 tidak berubah: pohon tetap
  hakim ketuk; hasil OCR (jalur mana pun) adalah penasihat
  berlabel skor yang wajib diverifikasi sebelum memandu ketukan.
