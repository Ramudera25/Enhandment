# Uji Layar Virtual (Virtual Display) — 9 Okt 2026

Pertanyaan Travis: dengan satu device, bisakah eksekusi berjalan di "layar kedua" agar HP tetap bebas dipakai bersamaan? Uji split-screen lebih dulu membuktikan TIDAK (pohon hanya membaca jendela fokus; belahan pasif membeku di splash). Dokumen ini hasil sprint layar virtual sore 9 Okt (semua angka terverifikasi di perangkat Samsung A13, Android 14).

## Hasil per lapis

| Lapis | Hasil | Bukti |
|---|---|---|
| Buat VD dari shell (rish, app_process) | **MATI** — proses hilang tanpa jejak tepat di `createVirtualDisplay`, semua kombinasi flags (0/1/2/3/4/16), dengan & tanpa pembungkus `timeout`. Probe baca-saja (`getDisplays`) dari proses yang sama lolos bersih (EXIT=0) → yang dipolisikan adalah TINDAKAN membuat VD dari uid shell di build Samsung ini. | log bertahap STAGE1–3 di `/sdcard/vd*.log`; 0 proses VdServer di dumpsys |
| Buat VD dari aplikasi (VD Lab, uid app) | **BERHASIL** — flags `PUBLIC|PRESENTATION` (3) ditolak `SecurityException` (butuh CAPTURE_VIDEO_OUTPUT / token MediaProjection); flags `PRESENTATION` (2) saja BERHASIL → display id 6, lalu 7 (`muse-vd`, 720×1600@320, FLAG_PRIVATE|FLAG_PRESENTATION, state ON). | log dalam aplikasi VD Lab (`vdlog.txt`), dumpsys display |
| Luncurkan aplikasi lain ke VD | **BERHASIL via shell** — `am start --display 7 -n com.glints.candidate/.MainActivity` → Glints `topResumedActivity`, task visible di Display #7. Dari dalam aplikasi pemilik VD: `Permission Denial` (SecurityException) → peluncuran tetap tugas shell. Visibilitas paket: aplikasi butuh `<queries>` agar `getLaunchIntentForPackage` tidak null (Android 11+). | dumpsys activity activities |
| Render ke VD | **JALAN** — ImageReader pemilik VD menerima frame terus-menerus; frame PNG (simpan otomatis per 8 dtk) berhasil ditarik & dibaca: splash Glints ter-render di VD. | `bukti-layar/vd-glints-frame*.png` di VM bayu |
| Aktivasi aplikasi di VD | **GAGAL (penghambat utama)** — Glints berhenti di starting window/splash selama ber menit-menit; peluncuran Settings ke VD yang sama juga hanya mencapai starting window. Polanya: aktivitas di VD privat presentasi tidak pernah melewati starting window — jendela tidak pernah mendapat fokus/aktivasi. Ketukan `input -d 7 tap` diterima (RC=0) tapi tidak mengubah keadaan. | frame PNG berurutan identik |
| Tangkapan layar VD | `screencap -d 7` **RC=1** (display FLAG_PRIVATE milik uid lain) → satu-satunya jalur piksel yang sah = ImageReader milik aplikasi pemilik VD. | — |
| Mata pohon ke VD | Pohon (LayananAkses) hanya `rootInActiveWindow` (2 titik di kode) → buta terhadap VD. Jalur tambal teridentifikasi: enumerasi `windows` + `getDisplayId()` per jendela — BELUM diuji karena aplikasi di VD belum pernah merender UI asli untuk dibaca. | grep kode pendamping |

## Putusan sprint

Tulang konsep **terbukti**: display kedua bisa dibuat, diisi aplikasi nyata, dan dialiri frame — tanpa menyentuh layar fisik sama sekali. Penghambat tunggal sekarang: **aktivasi/fokus jendela di VD privat kelas presentasi**. Tiga kunci kandidat untuk percobaan berikutnya:

1. **VD bertoken MediaProjection** (kelas "screen sharing" yang ditunjuk pesan SecurityException itu sendiri) — butuh satu ketuk persetujuan Travis di dialog sistem; display kelas ini bersifat publik, kemungkinan semantik fokusnya berbeda.
2. Pemilik VD = layanan depan aplikasi pendamping (bukan activity lab) + pohon ditambal sadar-display, lalu uji paksa fokus (luncurkan HOME lebih dulu, injeksi UserService ber-displayId).
3. Terima VD sebagai layar *khusus aplikasi ringan* yang tidak menggantungkan aktivasi pada fokus (belum ada kandidat teruji).

Artefak: aplikasi uji `VD Lab` (`id.musedroid.vdlab`, terpasang di HP, sumber di `advance/vd-lab/vdlab/`) dan server shell `VdServer` (sumber di `advance/vd-lab/vdserver/`, jar di HP `/data/local/tmp/vdserver.jar`). VD Lab dihentikan (force-stop) sesudah uji — tidak ada display sisa di perangkat.

## Sesi 3 (sore, lanjutan atas perintah Travis): pemilik layanan depan + baterai aktivasi

- VD Lab v0.4: pemilik VD dipindah ke **foreground service** (VdHostService, tipe dataSync + WakeLock). Dua jebakan Android 14 terbukti & teratasi: (1) FGS tanpa `foregroundServiceType` di manifest → `MissingForegroundServiceTypeException` (targetSdk 34); (2) activity yang finish terlalu cepat + start FGS lambat (delay terukur 10,5–12,8 dtk di A13 sarat beban) → startForeground ditolak sebagai "background started". Obat: tipe dinyatakan + activity bertahan 25 dtk. Hasil: **VD HOST BERHASIL DISPLAY_ID=9**, layar fisik bebas sesudahnya.
- Baterai aktivasi di VD presentasi (pemilik FGS) — SEMUA GAGAL, frame = bukti:
  1. Baseline Glints: starting window (sama seperti sesi 1). Keadaan jendela dari dumpsys: `mViewVisibility=0x0`, `mHaveFrame=true`, `isOnScreen=true` — jendela "di layar", tapi frame-nya selamanya starting window.
  2. Resize-kick (`vd.resize()` ke 1080×2408 via saluran perintah berkas): starting window ter-render ulang di kanvas baru, aplikasi tetap tidak mulai.
  3. Denyut fokus (`input -d` KEYCODE_WAKEUP + tap + `am start` ulang): tidak berubah.
  4. HOME lebih dulu di VD segar (Display 10): intent HOME diterima, tetapi tidak ada frame launcher sama sekali (>30 dtk, nol frame tersimpan dari reader baru).
- **Putusan sesi 3: VD presentasi milik aplikasi di build Samsung ini TIDAK mengaktifkan UI asli aplikasi tamu — titik.** Semua jalur dalam amplop hak no-root sudah dicoba: shell (dibunuh), aplikasi presentasi (hosting ya, aktivasi tidak), MediaProjection (cermin). Yang tersisa di luar amplop: flags sistem/trusted, API proprietary DeX/Knox, atau root — semuanya di luar arsitektur Enhandment.
- Tambal pohon sadar-display DIBATALKAN untuk sekarang: target ujinya (UI asli di VD) tidak pernah ada untuk dibaca; desain tambalannya (enumerasi `windows` + `getDisplayId`) tercatat di dokumen ini bila aktivasi suatu hari terpecahkan.
- VD Lab dihentikan sesudah uji; perangkat bersih (Display 0).

## Sesi 4 (17.20-17.35, perintah Travis: uji VD pakai KitaLulus, BUKAN Glints; cari Pati, apply 1 lamaran bebas)

- **KitaLulus AKTIF PENUH di VD** (Display 11, pemilik FGS VD Lab): cold-start langsung merender UI asli — beranda, filter lokasi "Kabupaten Pati" (sudah tersetel), kategori, feed loker. Berbeda total dari Glints/Settings yang membeku di starting window.
- Interaksi di aktivitas PERTAMA bekerja: swipe feed OK, ketuk kartu loker membuka detail (Account Executive — NEXA, Pati, Rp2,485–3,0 jt, diperbarui hari ini).
- **Temboknya pindah satu lapis**: di aktivitas KEDUA (halaman detail), SEMUA ketukan mati — tombol "Lamar" (4x ketuk + 1x tekan-geser + tunggu 25 dtk) dan panah kembali tidak merespons. Formulir lamar tidak pernah muncul; di display utama juga tidak ada formulir nyasar (terverifikasi dumpsys).
- Kesimpulan sesi 4: transisi aktivitas di VD kehilangan fokus input — aktivitas pertama bisa dioperasikan, anaknya tidak. Apply lewat VD BELUM bisa; tidak ada lamaran terkirim pada uji ini.
- Perangkat dibersihkan lagi (Display 0 saja).
