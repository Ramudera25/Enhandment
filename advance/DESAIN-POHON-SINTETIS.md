# DESAIN — Pohon Sintetis: parser bingkai → daftar elemen

Status: desain, prototipe dibangun sesudah dokumen ini · Ditulis 11 Oktober 2026
Sumber pola: riset GitHub/Hugging Face 11 Okt 2026 (OmniParser — detektor elemen + OCR; jebakan lisensi bobot V2 = AGPL, detektor varian MIT yang dipakai).

## Masalah

Pohon aksesibilitas buta pada permukaan kanvas/WebView tertentu: simpul kosong atau nyaris kosong sementara layar jelas berisi tombol dan teks. BACA (OCR server) memberi teks + koordinat, tetapi tidak memberi ELEMEN: tidak ada klasifikasi ikon/tombol, tidak ada kotak elemen non-teks. Agen membutuhkan daftar elemen semirip mungkin dengan keluaran POHON agar nalar ketuknya tidak berubah.

## Rancangan

1. **Pipa (sisi server/VM, di samping baca-server.py):** bingkai PNG → detektor elemen ONNX (kelas ikon/elemen UI) → untuk tiap kotak: label kelas dari detektor + teks dari PP-OCRv5 (mesin yang sama dengan baca-server.py) bila kotak memuat teks → daftar elemen JSON bentuk SAMA dengan simpul POHON: {t, d, k, b, klik} + penanda `sintetis: true` dan skor deteksi. Perkakas: `advance/15-pohon-ui-aksesibilitas/pohon-sintetis.py`.
2. **Lisensi adalah gerbang keras:** detektor yang dipakai WAJIB berlisensi permisif (MIT/Apache) pada BOBOT-nya, diverifikasi dari repo sumber sebelum unduh. Bobot detektor OmniParser V2 (AGPL, Ultralytics) DILARANG. Bila artefak MIT tidak dapat diverifikasi, prototipe berhenti dan melapor — tidak ada pengganti diam-diam.
3. **Aturan pakai (doktrin):** pohon sintetis adalah PENASIHAT lapis ketiga — hanya dikonsultasikan bila POHON asli kosong/nyaris kosong (<5 simpul) atau agen memintanya eksplisit untuk permukaan kanvas. Ia tidak pernah mengalahkan pohon asli; ketukan dari elemen sintetis wajib diverifikasi pasca-ketuk lewat versi pohon/bingkai seperti biasa.
4. **Bukan cakupan:** pelatihan/fine-tuning detektor, deteksi di perangkat, dan penggabungan otomatis ke dalam runner misi (integrasi runner menyusul sesudah prototipe terbukti; tahap ini keluaran berupa berkas JSON + laporan evaluasi).

## Definisi lulus prototipe

1. Artefak detektor terverifikasi lisensinya (nama repo, berkas lisensi, hash model tercatat).
2. Berjalan di VM pada 3 bingkai arsip nyata (beranda KitaLulus, beranda Facebook, satu bingkai WebView/Brave): daftar elemen keluar, latensi tercatat.
3. Evaluasi jujur per bingkai: elemen UI utama yang dikenali (kotak ± benar) vs yang terlewat/dibuat-buat — dinilai dari daftar elemen yang diketahui ada di bingkai itu. Ambang kelayakan: elemen interaktif utama (bilah cari, tab, tombol jelas) mayoritas tertangkap; bila tidak, vonisnya "belum layak" dan dicatat apa adanya.
