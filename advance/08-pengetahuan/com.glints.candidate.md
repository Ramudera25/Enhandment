# com.glints.candidate — Glints (aplikasi Android)

## Kebiasaan
- Sesi login asli di aplikasi **bersih dari tantangan Cloudflare** yang
  memblokir jalur web (terbukti 7 Okt 2026: 3 lamaran terkirim lewat aplikasi
  pada hari ketika web 0 berhasil).
- Listing bisa **tutup sewaktu-waktu**: pada hari yang sama, 4 dari 7 listing
  target ternyata sudah tidak aktif saat diverifikasi di aplikasi.

## Jalan pintas resmi
- Verifikasi kesegaran listing DI APLIKASI sedini mungkin, sebelum berkas
  disiapkan — jangan menunggu giliran eksekusi.

## Jebakan
- Mengandalkan clearance CAPTCHA dari browser untuk sesi aplikasi/web lain:
  clearance tidak berpindah antar-sesi. Perlakukan kanal web dan aplikasi
  sebagai dua dunia terpisah.
