# 10 — Aplikasi Pendamping Shizuku (Jalan 2, target v2)

> Status: **terpasang & endpoint hidup (8 Okt 2026)** — APK terbangun,
> terpasang lewat rish, PING → PONG di 127.0.0.1:19101; DUMP masih stub
> jujur; kaki izin Shizuku menunggu satu restart server (binder tidak
> dikirim ke aplikasi yang dipasang sesudah server start). Hasil lengkap
> di [../PENGUJIAN.md](../PENGUJIAN.md) Fase 9. Bagian dari folder `advance/`.

## Kenapa aplikasi sendiri?

Semua jalur sekarang meminjam alat orang (rish, uiautomator eksternal).
Aplikasi pendamping membuat muse-droid punya **rumah sendiri** di HP:

- **Izin Shizuku resmi** lewat API-nya: aplikasi meminta izin sekali, lalu
  menjalankan layanan berhak-shell tanpa bergantung pada skrip rish.
- **API lokal resmi**: server HTTP kecil di `127.0.0.1` dengan endpoint
  `dump`, `ketuk`, `geser`, `ketik`, `foto`, `tunggu-teks` — eksekutor dan
  agent berbicara ke satu pintu yang stabil lintas versi Android.
- **Berbasis kejadian, bukan jajak**: dengan layanan aksesibilitas sendiri,
  aplikasi bisa MELAPOR saat layar berubah ("tombol Kirim muncul") alih-alih
  ditanya berulang kali — inilah akhir dari polling.
- **IME sendiri** untuk mengetik: teks panjang, emoji, dan tanda baca masuk
  sempurna (mengakhiri era `input text` dan trik clipboard).

## Isi folder ini

| Berkas | Isi |
|---|---|
| `MainActivity.kt` | Kerangka aktivitas utama: memeriksa & meminta izin Shizuku, menyalakan/mematikan layanan |
| `LayananLokal.kt` | Kerangka layanan: server socket lokal + peta endpoint ke aksi UI |

## Peta jalan build

1. Buat proyek Android (Kotlin, min SDK 26) — aktivitas + layanan dari kerangka ini.
2. Tambahkan dependensi Shizuku API (`dev.rikka.shizuku:provider` + `:api`).
3. Bangun dengan Gradle (`./gradlew assembleDebug`), pasang APK ke HP pekerja,
   beri izin Shizuku dari aplikasi Shizuku.
4. Uji endpoint satu per satu melawan perilaku `hp.sh` (hasil harus setara).
5. Setelah setara: eksekutor belajar mode `MESIN=pendamping`; rish menjadi
   jalur cadangan. Di titik inilah paket ini lulus dari `advance/` menjadi v2.

## Batasan yang disadari sejak awal

- Aplikasi yang dipasang dari luar Play Store terkena "Restricted Settings"
  untuk aksesibilitas di Android 13+ — perlu langkah izin manual tambahan
  (didokumentasikan saat build pertama).
- Layanan latar tetap bisa dibunuh OEM; perlu strategi hidup-lagi (alarm /
  foreground service dengan notifikasi tetap).
