# 15 — Pohon UI Aksesibilitas (V4.0) + Layanan Depan

Implementasi `DESAIN-V3-POHON-UI.md`: aplikasi pendamping memelihara
**salinan pohon UI jendela aktif** dari peristiwa aksesibilitas dan
menyajikannya lokal, menggantikan dump UiAutomation (0,5–0,95 dtk)
sebagai mata utama misi. Paket ini juga memuat **layanan depan**
(foreground service) — jangkar hidup pendamping dari butir peningkatan
V3.x — karena keduanya hidup di APK yang sama.

> Status: **TERUJI di perangkat nyata 8 Okt 2026** — hasil lengkap di
> `advance/PENGUJIAN.md` Fase 15 (pohon) dan Fase 16 (layanan depan +
> penjaga). Layanan aksesibilitas terikat sesudah reboot HP; diagnosis
> lapangannya adalah manajer aksesibilitas (AMS) macet global (uji
> kontrol AutoX.js juga gagal terikat) dan reboot menyembuhkannya.
> `PING` 19102 terukur **7–32 ms**; umur salinan **32 ms–0,4 dtk**
> saat layar aktif. `CARI` terverifikasi terhadap tangkapan layar
> untuk simpul yang terlihat — “Invite” di Brave pada bounds
> `[804,100][1049,205]`, tengah (926,152). Batas jujur: bounds simpul
> di bawah lipatan daftar bisa tidak andal; verifikasi pasca-ketuk §4
> tetap wajib. **Aturan eksklusivitas:** sesi UiAutomation/u2 menutup
> layanan aksesibilitas selama aktif, dan pohon mengikat kembali
> sendiri ±12 dtk sesudah u2 berhenti — pohon adalah kaki utama, u2
> cadangan on-demand. Layanan depan dihidupkan penjaga via rish dan
> socket pendamping 19101 menjawab PONG stabil pada uji yang sama.

## Kode (di advance/10 — rumah aplikasi pendamping)

- `LayananAkses.kt` — `AccessibilityService` + penyaji socket.
  Dikonfigurasi programatik di `onServiceConnected()` (tanpa berkas
  xml meta-data): peristiwa jendela/konten/fokus/teks/klik/skrol,
  debounce 40 ms, salinan disimpan sebagai model datar (paket, kelas,
  teks, desc, bounds, klik/edit/fokus) + nomor versi + stempel waktu.
  Penyaji di **127.0.0.1:19102**: **satu baris per koneksi** — klien
  membuka koneksi baru untuk tiap perintah dan menerima satu baris
  balasan JSON. Perintah observasi: `PING`, `PAKET?`, `TEKS? <teks>`,
  `CARI <teks>` (persis dulu, lalu substring), `POHON` (maks 800 node
  bermakna), `ISI <teks>` (ACTION_SET_TEXT pada node edit fokus —
  dikerjakan pada node HIDUP, bukan salinan). Sejak **V4.1** `ISI`
  menunggu kolom edit yang FOKUS muncul maks ±600 ms (5 percobaan ×
  jeda 120 ms) sebelum jatuh ke kolom cadangan, dan balasannya memuat
  `tunggu_ms`. Server hanya ada selama layanan aktif: ketiadaannya
  adalah sinyal turun-kelas yang jujur.
- **Perintah gestur (V4.1, `LayananAkses.kt`)** — pohon kini juga
  tangan: `KETUK x y`, `TAHAN x y` (tekan 650 ms),
  `GESER x1 y1 x2 y2 [ms]`, dan `GLOBAL BACK|HOME|RECENTS`,
  dieksekusi `dispatchGesture`/`performGlobalAction` oleh layanan
  aksesibilitas sendiri — tanpa rish, tanpa Shizuku. Pra-syaratnya
  `android:canPerformGestures="true"` pada meta-data layanan di
  `res/xml/layanan_akses.xml` (di advance/10): properti
  `capabilities` hanya-baca dari Kotlin, jadi **XML adalah sumber
  otoritatif** kemampuan ini. Balasan gestur berbentuk
  `{ok, versi_sblm, versi_ssdh, naik, latensi_ms}` dan baru dikirim
  sesudah **versi salinan naik** (batas tunggu 1,2 dtk) — aksi dan
  verifikasi dalam satu perjalanan socket. Angka perangkat: KETUK
  satu layar 234–237 ms, GESER 332–358 ms, GLOBAL BACK 374–441 ms
  (PENGUJIAN.md Fase 18).
- `LayananDepan.kt` — foreground service (tipe `specialUse`, notifikasi
  tetap "Pendamping siaga"). `onStartCommand` menyalakan
  `LayananLokal` sekalian — satu pintu masuk untuk seluruh tumpukan.
- `MainActivity.kt` — tombol nyala kini menyalakan layanan depan
  (`startForegroundService`), meminta izin POST_NOTIFICATIONS (API 33+),
  dan menampilkan status pohon UI (aktif/belum + cara mengaktifkan).
- `AndroidManifest.xml` — izin FOREGROUND_SERVICE(+_SPECIAL_USE) &
  POST_NOTIFICATIONS; deklarasi kedua layanan. `build.sh` kini menyalin
  manifest dari repo (sumber tunggal) + kedua berkas .kt baru.

Penjaga kaki (advance/13) diperbarui: kaki pendamping tidak lagi
"dicatat saja" — bila socket 19101 mati dan rish hidup, penjaga
menghidupkan layanan depan via `am start-foreground-service` (tanpa
menyentuh layar), dibatasi 1 percobaan per 5 menit.

## Aktivasi (satu kali, pemilik HP)

1. Pasang APK baru: `pm install -r muse-droid-pendamping.apk` via rish.
2. Nyalakan layanan depan: buka pendamping → "Nyalakan Layanan
   (depan + lokal 19101)" — atau penjaga kaki akan menyalakannya.
3. Aktifkan aksesibilitas: Pengaturan → Aksesibilitas → Aplikasi
   terpasang → **muse-droid Pohon UI** → Aktifkan. Bila terkunci
   "setelan dibatasi" (Android 13+, aplikasi luar Play Store):
   Pengaturan → Aplikasi → muse-droid Pendamping → menu ⋮ →
   "Izinkan setelan terbatas", lalu kembali ke langkah 3.

## Rencana uji (dari desain §7, disesuaikan sesi)

1. **Akurasi**: `uji-pohon.py <teks>` pada ≥5 aplikasi — bounds CARI
   harus sama persis dengan node dump u2 untuk node yang sama.
2. **Kecepatan**: latensi PING/CARI (target <50 ms) vs dump u2 (±500 ms+).
3. **Kebasian**: ketuk pengubah layar → versi naik; jawaban pasca-ketuk
   benar ≤300 ms (9/10 percobaan).
4. **Set-text**: `ISI` pada kolom pencarian/chat — teks tampil utuh,
   bandingkan dengan waktu KETIK lama (±5,7 dtk di misi navigasi).
5. **Layanan depan**: bunuh proses latar aplikasi lain / diamkan —
   notifikasi tetap ada, 19101/19102 tetap menjawab; matikan paksa
   pendamping → penjaga menghidupkannya lagi ≤±5 menit.
6. **Turun kelas**: nonaktifkan layanan aksesibilitas di tengah misi
   ad-hoc (advance/16) → runner melaporkan mode dump dan misi beres.
7. **Benchmark**: misi standar advance/11 sebelum/sesudah (mode pohon).
