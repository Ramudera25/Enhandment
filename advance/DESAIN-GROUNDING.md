# DESAIN — Layanan Grounding Cadangan: bingkai + perintah → koordinat

Status: desain, prototipe kelayakan dibangun sesudah dokumen ini · Ditulis 11 Oktober 2026
Sumber pola: riset GitHub/Hugging Face 11 Okt 2026 (UI-TARS, OS-Atlas, GUI-Owl, UGround — semua angka latensi CPU adalah estimasi sumber; akurasi grounding Bahasa Indonesia tidak dilaporkan kandidat mana pun).

## Masalah

Ada target yang tidak ditemukan tiga lapis yang sudah ada: pohon kosong DAN OCR tidak memuat teksnya (ikon tanpa label, elemen bergambar) DAN detektor pohon sintetis tidak mengotakkannya. Untuk keadaan itu dibutuhkan penunjuk koordinat terakhir: diberi bingkai + perintah bahasa alami, model mengembalikan satu titik (x, y).

## Rancangan

1. **Kedudukan: lapis KEEMPAT, terakhir.** Hanya dipanggil bila pohon, OCR server, dan pohon sintetis gagal menemukan target. Keluaran = SATU titik + skor/keyakinan bila tersedia; ketukan dari titik ini wajib diverifikasi pasca-ketuk seperti lapis lain. Ia tidak pernah menjadi jalur utama — latensi dan akurasinya kelas cadangan.
2. **Penempatan: server (VM).** Tidak ada kandidat yang sanggup hidup di A13. Rute prototipe, berurutan: (A) UI-TARS-2B GGUF lewat Ollama/llama.cpp bila artefak + lisensinya terverifikasi dari sumber; (B) OS-Atlas-Base-4B (Apache-2.0) lewat transformers CPU. Satu rute dicoba sampai gerbangnya jelas (jalan/gagal), lalu rute berikutnya hanya bila yang pertama gagal gerbang teknis — bukan gagal akurasi.
3. **Gerbang keras prototipe:** (a) lisensi bobot terverifikasi dari repo sumber; (b) sumber daya VM cukup (RAM/disk diukur dulu, dilaporkan); (c) satu panggilan grounding tuntas di CPU VM dengan latensi terukur — batas kelayakan praktis ≤120 dtk/panggilan untuk lapis cadangan; (d) uji akurasi pada bingkai arsip kita dengan target yang kotak benarnya diketahui: titik hasil harus jatuh DI DALAM kotak elemen sasaran. Di bawah 50% tepat dari ±9 target = belum layak.
4. **Privasi:** bingkai tidak keluar dari mesin Travis pada rute lokal. Rute cloud (VLM lewat API) BUKAN bagian dari prototipe ini — bila rute lokal gagal, laporan menyebutnya sebagai opsi keputusan terpisah untuk Travis, tidak dibangun diam-diam.
5. **Bukan cakupan:** integrasi runner, penyetelan prompt produksi, model 7B penuh (UI-TARS-2 hanya akses-riset; GUI-Owl/UGround lisensinya belum terkonfirmasi — keduanya dikeluarkan dari prototipe sampai lisensinya jelas).

## Definisi lulus prototipe

Laporan kelayakan berisi: rute yang terpasang (atau titik gagalnya), bukti lisensi, latensi terukur per panggilan, tabel akurasi per target (tepat di dalam kotak / meleset + jaraknya), dan vonis layak / layak bersyarat / belum layak — angka yang memutuskan, bukan kesan.
