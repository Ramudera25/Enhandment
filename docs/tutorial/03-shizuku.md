# Tutorial 03 — Shizuku: Membuka Kuasa Shell

> 📦 **Bahasa bayi:** Pintu sudah terpasang (bab 01), jalan tol sudah jadi (bab 02).
> Sekarang kita perkenalkan sopir ke satpamnya: Shizuku. Sekali satpamnya bertugas,
> sopir cukup membunyikan bel (`rish`) untuk menjalankan perintah dengan kunci
> gudang (uid shell).

**Tujuan akhir bab ini:** dari mesin agent, perintah ini berhasil:

```bash
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'id'"
# → uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),…
```

Itu momen "pintu terbuka": agent resmi bisa melihat dan menyentuh layar.
Waktu: ±15 menit. Aktivasi Shizuku perlu diulang sekali tiap HP restart
(menangis sedikit boleh, memang begitu desain Android).

## Apa itu Shizuku & `rish`?

- **Shizuku**: aplikasi yang menjalankan server kecil dengan hak `shell` Android.
  Ia tidak mengubah sistem; ia hanya meminjam hak yang memang disediakan Android.
- **`rish`**: jembatan dari Termux untuk memakai server itu — setiap perintah yang
  dijalankan lewat `rish` berjalan sebagai `uid shell`.

## Checklist

### Bagian 1 — Pasang Shizuku

- [ ] Unduh **Shizuku** dari Play Store / GitHub (moe.shizuku.privileged.api)
- [ ] Buka aplikasinya — abaikan dulu tampilannya, ikuti bagian berikut

### Bagian 2 — Aktifkan Shizuku (sekali per restart HP)

Cara **Wireless Debugging** (tanpa komputer):

- [ ] Di HP: **Pengaturan → Tentang → ketuk "Nomor build" 7×** (Opsi Pengembang aktif)
- [ ] **Pengaturan → Opsi Pengembang → aktifkan "Wireless debugging"**
- [ ] Di aplikasi Shizuku: pilih **Pairing** → Shizuku memberi tahu ia menunggu kode
- [ ] Buka panel Wireless debugging → **"Pair device with pairing code"** → masukkan
  kode yang diberikan Shizuku *(pairing ini cukup sekali seumur pemasangan)*
- [ ] Kembali ke Shizuku → **Start** (via Wireless debugging)
- [ ] Status Shizuku berubah menjadi **running** 🎉

> Alternatif: "Start via ADB" dari komputer — perintah persisnya ditampilkan aplikasi
> Shizuku itu sendiri; salin-tempel saja.

### Bagian 3 — Pasang `rish` ke Termux

- [ ] Di aplikasi Shizuku: menu **"Use Shizuku in terminal apps"** → ekspor dua file:
  `rish` dan `rish_shizuku.dex`
- [ ] Simpan kedua file ke folder yang terjangkau Termux (mis. Download)
- [ ] Di Termux:

```bash
cp /sdcard/Download/rish /sdcard/Download/rish_shizuku.dex ~/
chmod +x ~/rish
```

- [ ] Bila petunjuk Shizuku memintamu menyesuaikan `RISH_APPLICATION_ID` di file `rish`,
  lakukan; atau teruskan lewat environment seperti contoh-contoh di repo ini.

### Bagian 4 — Tes kuasa shell

- [ ] Dari Termux langsung:

```bash
RISH_APPLICATION_ID=com.termux ./rish -c 'id'
```

- [ ] Jawabannya harus `uid=2000(shell) … groups=…,1004(input),…`
  (grup `input` itulah izin mengetuknya)

### Bagian 5 — Tes melihat & menyentuh (dari mesin agent)

- [ ] Melihat — baca isi layar saat ini:

```bash
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'uiautomator dump /sdcard/d.xml; cat /sdcard/d.xml'" | head -c 500
```

- [ ] Menyentuh — uji aman buka Pengaturan lalu pulang:

```bash
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'am start -a android.settings.SETTINGS'"
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'input keyevent 3'"   # HOME
```

Layar HP bergerak sendiri? Selamat — **HP-mu resmi bisa dioperasikan dari jauh.** 🎉
Tinggal beri dia otak: [../07-ai-controller.md](../07-ai-controller.md),
dan pahami loop kerjanya: [../03-workflow.md](../03-workflow.md).

## Perawatan rutin

- [ ] **Setelah HP restart**: ulangi Bagian 2 (Start saja — pairing tidak diulang)
- [ ] Kecualikan Shizuku & Termux dari penghemat baterai; jalankan `termux-wake-lock`
- [ ] Wireless debugging **boleh dimatikan** setelah Shizuku start — ia hanya
  dibutuhkan saat aktivasi

## Kalau gagal

- **`RISH_APPLICATION_ID is not set`** → variabelnya lupa diteruskan; pakai bentuk lengkap.
- **`rish` menolak jalan / binder tidak ditemukan** → Shizuku belum running; Start ulang.
- **Pairing gagal terus** → kode pairing cepat kedaluwarsa; buat kode baru dan jangan
  tutup panelnya di tengah jalan.
- **`id` menjawab uid Termux, bukan 2000** → file `rish` basi; ekspor ulang dari Shizuku.
- Masih buntu? → [../troubleshooting.md](../troubleshooting.md)
