# 06 — Prasyarat, Keamanan, Batasan

> 📦 **Bahasa bayi:** Empat hal harus hidup bersamaan: jalan tol tersambung,
> pintu terpasang dan terbuka, satpam sedang bertugas, dan pintu rumah tidak
> dikunci dari dalam (layar tidak terkunci). Bab ini juga soal siapa saja yang
> boleh memegang kunci rumahmu — dan apa yang sopir tidak akan pernah lakukan.

## Prasyarat operasional (jalur utama)

Empat syarat di sisi HP, semuanya harus benar **bersamaan**:

1. **Jaringan** — HP terjangkau dari mesin agent (Tailscale aktif, atau satu LAN).
2. **`sshd` Termux berjalan** — tanpa ini pintu masuk tertutup total.
   (Gejala khas bila mati: semua koneksi SSH gagal dan notifikasi agent berhenti.)
3. **Shizuku hidup** — mati bila HP restart atau prosesnya dibunuh penghemat baterai;
   aktivasi ulang satu kali dari HP (Wireless Debugging) atau dari komputer (ADB).
4. **Layar tidak terkunci** — `uid shell` bisa membangunkan layar, tetapi ketukan
   menabrak layar kunci. PIN/pola/biometrik **tidak dapat dan tidak boleh ditembus**
   oleh jalur ini. Praktiknya: operasikan saat HP terbuka, atau pakai Smart Lock
   di lokasi tepercaya.

Tips keandalan:

- Aktifkan *wake lock* Termux dan kecualikan Termux/Shizuku dari penghemat baterai,
  agar proses latar tidak dibunuh di tengah operasi.
- Perlakukan "Shizuku mati setelah restart" sebagai pemeliharaan rutin, bukan insiden.

## Keamanan

- **Autentikasi kunci saja** untuk SSH; jangan aktifkan login password Termux.
- Kunci privat agent tidak pernah meninggalkan mesin agent; yang dipasang di HP
  hanya kunci publik (`authorized_keys`).
- **Jangan pernah** menulis kredensial, token, IP pribadi, atau data akun asli
  ke repo/dokumentasi — selalu pakai placeholder. (Repo ini disanitasi dengan aturan itu.)
- Batasi siapa yang memegang kunci: setiap pemegang kunci SSH + `rish` setara
  "bisa mengoperasikan HP". Cabut akses = hapus baris kunci dari `authorized_keys`
  Termux (dan/atau cabut pasangan ADB di pengaturan Wireless Debugging).
- Shizuku memberikan kuasa `shell`, bukan root — tetapi `shell` tetap kuasa besar
  (baca banyak status sistem, suntik input ke aplikasi apa pun yang tampil).
  Perlakukan seperti akses operator, bukan akses mainan.

## Batasan jujur

| Batasan | Penjelasan |
|---|---|
| Bukan root | Tidak bisa membaca data privat aplikasi lain (kotak pasir Android tetap berlaku); tidak bisa mengubah sistem |
| Layar kunci | Tugas berhenti di lockscreen aman; tidak ada jalan pintas yang sah |
| Proses latar rapuh | Android dapat membunuh Termux/Shizuku kapan pun (manajemen baterai agresif memperparah) |
| UI berubah-ubah | Pembaruan aplikasi dapat mengubah alur/layar; loop agent harus verifikasi per langkah dan berhenti saat bingung |
| Tidak semua aplikasi ramah | Aplikasi dengan proteksi anti-otomasi (FLAG_SECURE, deteksi aksesibilitas) bisa membatasi sebagian aksi |
| Satu operator pada satu waktu | Dua pengendali menyentuh layar bersamaan = kekacauan; koordinasikan kepemilikan sesi |

## Etika pemakaian

Dokumentasi ini untuk mengoperasikan **perangkat milik sendiri**, dengan akun sendiri,
untuk tugas yang memang diotorisasi pemiliknya. Ia bukan alat untuk mengakses perangkat
orang lain, mengakali verifikasi identitas, atau mengotomasi layanan dengan cara yang
melanggar ketentuan layanan pihak ketiga — nilai sendiri risikonya untuk tiap target.
