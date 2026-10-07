# com.android.settings — Pengaturan (Samsung)

## Kebiasaan
- **Task restoration**: membuka Pengaturan menampilkan HALAMAN TERAKHIR yang
  dikunjungi, bukan halaman utama. (Terbukti 7 Okt 2026: terbuka di Opsi
  pengembang, sisa kunjungan lama — misi demo yang mengasumsikan halaman
  utama gagal karenanya.)
- Bahasa antarmuka perangkat uji: Inggris.

## Jalan pintas resmi
- Lompat langsung ke halaman tujuan dengan intent dalam, contoh:
  `BUKA android.settings.BLUETOOTH_SETTINGS`, `android.settings.WIFI_SETTINGS`.
- Halaman Bluetooth adalah anak halaman Connections: tombol naik (Navigate up)
  dari Bluetooth mendarat di Connections, bukan di halaman utama.

## Jebakan
- Menekan Back dari halaman hasil intent dalam bisa keluar ke aplikasi
  sebelumnya, bukan ke daftar Pengaturan — jangan susun misi yang bergantung
  pada Back dari halaman dalam.
