# 10 — Mata Kedua: Melihat Apa yang Tidak Terlihat XML

> 📦 **Bahasa bayi:** Mata pertama (uiautomator, bab 03) membaca layar seperti
> membaca daftar isi buku — cepat dan tepat, tapi hanya untuk yang tertulis.
> Mata kedua adalah **melihat halaman bukunya beneran**: foto layar dibaca
> sebagai gambar. Dipakai hanya saat daftar isi tidak cukup.

## Protokol dua mata (aturannya)

1. **XML dulu, selalu.** Murah, presisi piksel, memberi koordinat pasti.
   Perkakas: `hp.sh dump`, diperas oleh `mata-dua.py ringkas` (dump 36 KB lazimnya
   menyusut jadi ±1 KB daftar elemen berguna — otak agent tidak tenggelam).
2. **Vision menyala bila salah satu terpenuhi:**
   - teks/elemen yang dicari **tidak ada** di XML (kanvas: CapCut, Canva, game),
   - yang perlu diverifikasi adalah **keadaan visual** (unggahan selesai? saklar
     menyala? bilah progres sampai mana?),
   - XML dan kenyataan **tidak cocok** (ketukan meleset dua kali berturut-turut).
3. **Hasil vision selalu diterjemahkan ke koordinat** sebelum bertindak —
   tidak ada "ketuk kira-kira". Caranya: grid bernomor (di bawah).
4. **Kedua mata sepakat = percaya diri.** Bila koordinat dari grid cocok dengan
   bounds dari XML untuk elemen yang sama, ketuk tanpa ragu. Bila bertengkar,
   berhenti dan foto ulang.

## Grid bernomor (Set-of-Mark) — `mata-dua.py kotak`

Screenshot dibagi kotak-kotak bernomor (bawaan 6×12). Model vision cukup
menyebut **nomor sel** — dan bila perlu sub-posisi pola keypad 1–9 di dalam sel —
lalu `mata-dua.py ketuk` menerjemahkannya ke koordinat pasti:

```bash
python3 scripts/mata-dua.py kotak layar.png        # -> layar-kotak.png + layar-kotak.json
python3 scripts/mata-dua.py ketuk layar-kotak.json 27 5   # -> "540 1250"
```

Kenapa ini bekerja: model vision buruk dalam menebak angka piksel, tapi bagus
dalam membaca "objek X ada di kotak nomor berapa". Grid mengubah tebakan
menjadi bacaan.

## OCR lokal — mata rabun yang cepat — `mata-dua.py ocr`

Teks yang digambar di dalam kanvas/gambar lolos dari uiautomator, tapi tertangkap
OCR. Mesin: RapidOCR (pip, model menyatu) atau tesseract bila terpasang. Hasilnya
teks + titik tengahnya — cukup untuk menemukan dan mengetuk teks di wilayah
kanvas, tanpa memanggil model vision besar. Murah, luring, cepat.

## Mata gerak — `mata.sh jaga`

Selama operasi panjang (render video, unggah besar), dump penuh tiap detik itu
boros. `mata.sh jaga <interval> <jumlah>` mengambil foto berkala ke
`bukti/gerak/` — agent cukup membuka foto terakhir untuk tahu "sudah sampai
mana", seperti mengawasi ketel dari jauh.

## Telinga — `mata.sh notif`

Indra ketiga yang bukan mata: **notifikasi**. Banyak kejadian penting berbunyi
dulu sebelum terlihat ("unggahan selesai", "pesan masuk"). `mata.sh notif`
meringkas notifikasi aktif dari `dumpsys notification` — **sengaja hanya nama
aplikasi dan jumlahnya, bukan isi pesan**: telinga ini mendengar ada yang
berbunyi, bukan menguping isinya. (Mendengarkan kejadian secara langsung/*live*
butuh layanan pendengar notifikasi — pekerjaan rumah untuk v2.)

## Batasan jujur

- Vision membaca foto **diam**; untuk gestur kontinu (menggeser trim video)
  ia tetap meraba — grid menolong menemukan, bukan menghaluskan gerakan.
- OCR rabun pada huruf kecil/kontras rendah dan tidak paham ikon tanpa teks.
- Semua mata kalah oleh layar terkunci dan layar FLAG_SECURE (bab 04) — itu
  bukan kekurangan alat, itu pagar yang memang tidak boleh dilompati.
