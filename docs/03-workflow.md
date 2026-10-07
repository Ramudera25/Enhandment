# 03 — Workflow

Loop kendali agent untuk menyelesaikan satu tugas di aplikasi Android, langkah demi langkah.
Contoh berjalan: **mengirim lamaran lewat aplikasi lowongan** (alur yang terverifikasi nyata).

## Fase 0 — Pra-kondisi (cek sebelum mulai)

Jalankan `examples/cek-koneksi.sh` dari mesin agent. Empat syarat:

1. SSH ke Termux tersambung (jaringan + `sshd` hidup).
2. `rish` menjawab `uid=2000(shell)`.
3. Layar tidak terkunci (`dumpsys window policy` → keyguard tidak tampil).
4. Aplikasi target terpasang (`pm list packages | grep <paket>`).

Bila ada yang gagal: hentikan dan laporkan syarat mana yang kurang — jangan memaksa.

## Fase 1 — Buka aplikasi secara deterministik

```sh
rish -c 'am start -n <paket>/<aktivitas-utama>'
```

Jangan mengandalkan mengetuk ikon di launcher: `am start` lebih pasti dan bisa
diulang dengan hasil yang sama.

## Fase 2 — Baca layar sebelum bertindak

```sh
rish -c 'uiautomator dump /sdcard/window_dump.xml; cat /sdcard/window_dump.xml'
# atau verifikasi visual:
rish -c 'screencap -p /sdcard/cek.png'
```

Agent mengekstrak dari XML: teks yang tampil, elemen yang bisa diketuk (`clickable="true"`),
dan `bounds`-nya → titik tengah bounds = koordinat ketuk.

## Fase 3 — Aksi kecil, satu per satu

Untuk tiap langkah alur (mis. ketuk tombol "Lamar", isi kolom, lampirkan CV):

```sh
rish -c 'input tap <x> <y>'          # ketuk
rish -c 'input text "<teks>"'        # mengetik (hati-hati spasi & karakter khusus)
rish -c 'input swipe 540 1600 540 700 300'   # gulir
rish -c 'input keyevent 4'           # BACK bila perlu mundur
```

Aturan mainnya:

- **Satu aksi → satu verifikasi.** Setelah setiap aksi, ulangi Fase 2. Tampilan aplikasi
  berubah karena banyak hal (dialog, loading, papan ketik) — asumsi buta adalah sumber gagal.
- **Tempo manusiawi.** Beri jeda wajar antar aksi; selain sopan ke server, ini menghindari
  event yang hilang karena UI belum siap.
- **Kenali layar berhenti.** Dialog izin, papan ketik menutupi tombol, atau layar kunci
  muncul — semuanya terbaca di dump; tangani eksplisit, jangan diabaikan.

## Fase 4 — Verifikasi hasil akhir

Sebuah tugas hanya "selesai" bila ada bukti di layar: halaman konfirmasi
("Lamaran terkirim"), entri baru di daftar, atau status yang berubah.
Ambil `screencap` sebagai bukti, lalu catat hasilnya (waktu, target, status)
ke log di sisi agent.

## Fase 5 — Pencatatan

Pola yang dipakai pada operasi nyata:

- Setiap aksi eksternal yang berhasil langsung dicatat (log terstruktur:
  tanggal, jam, aplikasi, target, hasil) — bukan di akhir sesi.
- Kegagalan dicatat apa adanya beserta penyebab teramati (listing tutup,
  dialog tak terduga, sesi mati) agar tidak diulang membabi buta.

## Kondisi berhenti (stop conditions)

Berhenti dan lapor ke manusia bila:

- Muncul kebutuhan yang hanya bisa diputuskan manusia (OTP, CAPTCHA di aplikasi,
  persetujuan yang belum pernah diberikan).
- Layar terkunci di tengah jalan.
- Aplikasi meminta kredensial yang tidak termasuk otorisasi tugas.
- Jumlah percobaan wajar untuk satu langkah terlampaui — UI berubah / alur berbeda
  dari dugaan. Menerka-neka pada titik ini berisiko mengirim aksi yang salah.

## Contoh alur lengkap (lamaran via aplikasi lowongan)

```
cek-koneksi ✓ → am start (aplikasi lowongan)
→ dump: daftar lowongan → tap lowongan target
→ dump: detail lowongan → tap "Lamar/Chat"
→ dump: percakapan HRD → input text (surat lamaran)
→ lampirkan berkas CV lewat menu lampiran aplikasi
→ dump: pesan + lampiran terkirim terlihat → screencap (bukti)
→ catat log: TERKIRIM
```

Alur ini menyelesaikan dalam hitungan menit apa yang di jalur web terblokir seharian —
karena sesi aplikasinya asli dan tidak ada lapisan anti-bot web di tengahnya.
