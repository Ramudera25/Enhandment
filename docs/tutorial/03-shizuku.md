# Tutorial 03 — Shizuku: Membuka Kuasa Shell

**Tujuan akhir bab ini:** dari mesin agent, perintah ini berhasil:

```bash
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'id'"
# → uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),…
```

Itu momen "pintu terbuka": agent resmi bisa melihat dan menyentuh layar.
Waktu: ±15 menit, dan aktivasi Shizuku-nya perlu diulang sekali tiap HP restart
(menangis sedikit boleh, memang begitu desain Android).

## Apa itu Shizuku & `rish`?

- **Shizuku**: aplikasi yang menjalankan server kecil dengan hak `shell` Android.
  Ia tidak mengubah sistem; ia hanya meminjam hak yang memang disediakan Android.
- **`rish`**: jembatan dari Termux untuk memakai server itu — setiap perintah yang
  dijalankan lewat `rish` berjalan sebagai `uid shell`.

## Langkah 1 — Pasang Shizuku

Unduh **Shizuku** dari Play Store / GitHub (moe.shizuku.privileged.api).
Buka aplikasinya — tampilannya akan memandumu, tapi ringkasannya di bawah ini.

## Langkah 2 — Aktifkan Shizuku (sekali per restart HP)

Pilih cara **Wireless Debugging** (tanpa komputer):

1. Di HP: **Pengaturan → Tentang → ketuk "Nomor build" 7×** (mengaktifkan Opsi Pengembang).
2. **Pengaturan → Opsi Pengembang → aktifkan "Wireless debugging"**.
3. Di aplikasi Shizuku: **Pairing** → Shizuku menampilkan notifikasi meminta kode →
   buka panel Wireless debugging → "Pair device with pairing code" → masukkan kode
   yang diberikan Shizuku. (Pairing ini cukup **sekali seumur pemasangan**.)
4. Kembali ke Shizuku → **Start** (via Wireless debugging).
5. Status Shizuku berubah menjadi **running**. 🎉

> Alternatif: "Start via ADB" dari komputer — perintah persisnya ditampilkan aplikasi
> Shizuku itu sendiri; salin-tempel saja.

## Langkah 3 — Pasang `rish` ke Termux

Masih di aplikasi Shizuku:

1. Menu **"Use Shizuku in terminal apps"** → ekspor/ikuti petunjuknya: ada dua file,
   `rish` dan `rish_shizuku.dex`.
2. Simpan kedua file itu ke folder yang bisa dijangkau Termux (mis. Download),
   lalu di Termux:

```bash
cp /sdcard/Download/rish /sdcard/Download/rish_shizuku.dex ~/
chmod +x ~/rish
```

3. Sesuaikan ID aplikasi di dalam file `rish` bila diminta petunjuk Shizuku
   (biasanya baris `RISH_APPLICATION_ID=`), atau teruskan lewat environment
   seperti contoh di repo ini: `RISH_APPLICATION_ID=com.termux`.

## Langkah 4 — Tes kuasa shell

Dari Termux langsung:

```bash
RISH_APPLICATION_ID=com.termux ./rish -c 'id'
```

Harus menjawab `uid=2000(shell) … groups=…,1004(input),…`.
Grup `input` itulah yang mengizinkan ketukan.

## Langkah 5 — Tes melihat & menyentuh (dari mesin agent)

```bash
# melihat: baca isi layar saat ini
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'uiautomator dump /sdcard/d.xml; cat /sdcard/d.xml'" | head -c 500

# menyentuh: buka aplikasi Pengaturan lalu kembali (uji aman)
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'am start -a android.settings.SETTINGS'"
ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'input keyevent 3'"   # HOME
```

Layar HP bergerak sendiri? Selamat — **HP-mu resmi bisa dioperasikan dari jauh.**
Tinggal beri dia otak: [../07-ai-controller.md](../07-ai-controller.md),
dan pahami loop kerjanya: [../03-workflow.md](../03-workflow.md).

## Perawatan rutin

- **Setelah HP restart**: ulangi Langkah 2 (Start saja, pairing tidak perlu diulang).
- **Agar Shizuku & Termux tidak dibunuh sistem**: kecualikan keduanya dari
  penghemat baterai; jalankan `termux-wake-lock`.
- **Wireless debugging boleh dimatikan** setelah Shizuku start — ia hanya dibutuhkan
  saat aktivasi.

## Kalau gagal

- **`RISH_APPLICATION_ID is not set`** → kamu lupa meneruskan variabelnya. Pakai
  bentuk lengkap seperti contoh di atas.
- **`rish` menolak jalan / binder tidak ditemukan** → Shizuku belum running.
  Buka aplikasi Shizuku, cek status, Start ulang.
- **Pairing gagal terus** → pastikan HP dan panel pairing-nya: kode pairing cepat
  kedaluwarsa; ulangi dari pembuatan kode baru, dan jangan tutup panelnya di tengah.
- **`id` menjawab uid Termux, bukan 2000** → file `rish` yang dipakai bukan dari
  Shizuku versi terpasang. Ekspor ulang kedua file dari aplikasi Shizuku.
