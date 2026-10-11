# DESAIN — Pengawas Misi: Verifier Pasca-Aksi + Memori per Aplikasi

Status: desain, implementasi menunggu giliran sesudah uji hidup V4.4 · Ditulis 11 Oktober 2026
Sumber pola: riset GitHub/Hugging Face 11 Okt 2026 (Mobilerun/DroidRun — manager/executor + tracing; Mobile-Agent — Reflector; MobileUse — refleksi hierarkis + anggaran langkah) disaring ke kegagalan nyata kita sendiri di bawah.

## Masalah (bukti dari operasi kita)

1. **Kegagalan diam-diam.** Misi pernah "berhasil" di atas kertas sementara layar sebenarnya tidak berubah: varian pohon membeku (versi tidak bergerak), jebakan BUKA (paket benar, halaman salah — intent tertelan tumpukan), dan langkah TEMPEL yang tidak pernah menempel. Runner kini berhenti jujur saat gagal, tetapi untuk banyak langkah ia belum bisa MEMBUKTIKAN hasil, hanya ketiadaan galat.
2. **Pengetahuan per aplikasi tersebar di kepala agen, bukan di mesin.** Keanehan yang sudah dibayar mahal — tata letak formulir Glints bergeser tiap jawaban; status centang KitaLulus tidak terekspos pohon (wajib bingkai); panel cari JobStreet dua kolom dengan kotak describe tidak andal; koordinat ikon "Laporkan Loker" Glints yang haram diketuk — hidup di catatan chat/skill, tidak dibaca runner saat misi berjalan.

## Rancangan

### 1. Klausa VERIFIKASI per langkah (verifier pasca-aksi)

- Format misi v2 menambah klausa opsional sesudah langkah aksi:
  `VERIFIKASI TEKS_ADA "<teks>"` · `VERIFIKASI TEKS_TIDAK_ADA "<teks>"` · `VERIFIKASI PAKET <paket>` · `VERIFIKASI BACA_ADA "<teks>"` (baris OCR dari perintah BACA V4.4 — untuk layar yang pohonnya kosong) · `VERIFIKASI HALAMAN "<jangkar>"` (teks jangkar identitas halaman dari kartu aplikasi, menutup jebakan BUKA).
- Hasil tiap langkah dicatat sebagai pasangan {aksi_ok, verifikasi_ok, bukti} — bukti = versi pohon sebelum/sesudah, teks yang ditemukan, atau baris OCR. Laporan misi menampilkan bukti per langkah, bukan hanya sukses/gagal.
- Kebijakan gagal: verifikasi gagal = misi berhenti dan melapor pada langkah itu juga. TANPA coba-ulang buta, TANPA turun kelas ke dump/u2 (doktrin V4.2 tetap: fallback dump destruktif di mode pohon). Satu-satunya pengecualian: bila klausa menyatakan `LEMBUT`, kegagalan dicatat sebagai peringatan dan misi lanjut.
- Kompatibilitas mundur: misi tanpa klausa VERIFIKASI berjalan persis seperti sekarang.

### 2. Kartu memori per aplikasi

- Satu berkas per paket di `advance/08-pengetahuan/kartu/<paket>.md`, format terstruktur sederhana: titik masuk andal (deep link/intent), jangkar halaman (teks pembuktian tiap halaman penting), jebakan terverifikasi (koordinat/perilaku yang dihindari + alasannya), catatan formulir (kolom bergeser, pemilih berkas, dsb.), tanggal verifikasi terakhir.
- Runner membaca kartu pada langkah BUKA: prakondisi kartu (mis. "dinginkan aplikasi dulu") dijalankan, dan jangkar halaman kartu menjadi VERIFIKASI bawaan langkah BUKA — menutup akar gagal langkah-2 yang berulang 9 Okt.
- Kartu hanya boleh ditulis dari bukti operasi terverifikasi (bukan karangan), dan setiap entri membawa tanggalnya; entri basi (>30 hari tanpa verifikasi ulang) ditandai, bukan dipercaya buta.
- Kartu awal yang ditulis dari catatan operasi yang sudah terverifikasi: KitaLulus, Glints, JobStreet.

### 3. Anggaran langkah & waktu

- Setiap berkas misi menyatakan anggaran (bawaan: 2× jumlah langkah manusia yang wajar untuk tugas itu, dan batas durasi). Melampaui anggaran = berhenti + laporan keadaan terakhir (paket teratas, versi pohon, bingkai terakhir) — tidak mengembara. Pola ini meniru batas keras di Mobilerun/MobileUse dan menutup mode gagal "misi berputar sampai baterai habis".

## Definisi lulus

1. misi-uji-standar berjalan dengan klausa VERIFIKASI di semua langkah pengubah layar; laporan memuat bukti per langkah.
2. Uji negatif: satu misi dengan jangkar yang sengaja salah berhenti TEPAT di langkah itu dengan laporan verifikasi gagal (bukan timeout, bukan sukses palsu).
3. Tiga kartu awal (KitaLulus, Glints, JobStreet) terisi dari catatan terverifikasi dan dipakai runner pada BUKA (teramati di log: prakondisi + jangkar kartu).
4. Misi lama tanpa klausa baru berjalan tanpa perubahan perilaku (regresi format v1).

## Bukan cakupan

Tangga sembuh-sendiri dan gerbang prasyarat penuh (itu DESAIN-V5-SEMBUH-SENDIRI), perubahan perencana/LLM, dan grounding visual. Desain ini adalah jembatan: verifier + kartu adalah dua komponen yang juga dipakai V5, dibangun lebih dulu karena menutup kegagalan yang sudah pernah terjadi.
