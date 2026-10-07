# Glosarium — Kamus Bahasa Bayi

Semua istilah di repo ini, diterjemahkan ke benda sehari-hari.
Analogi ini dipakai konsisten di semua dokumen — sekali hafal, semua bab terasa ringan.

| Istilah | Bahasa bayi | Maksud sebenarnya |
|---|---|---|
| HP Android | 🏠 **Rumah** | Perangkat yang akan dikendalikan |
| Agent / AI | 🧠 **Sopir** | Otak yang membaca keadaan & memutuskan aksi |
| SSH | 🚪 **Pintu depan** | Cara masuk yang resmi & aman ke Termux |
| `sshd` | 🚪 **Pintunya itu sendiri** | Server SSH di HP; kalau belum dipasang/dibuka, sopir menunggu di luar |
| Kunci SSH (publik/privat) | 🔑 **Kunci rumah** | Pasangan kunci kriptografi; yang publik dititip di HP, yang privat dipegang sopir |
| Termux | 🛋️ **Ruang kerja** | Aplikasi terminal di HP, tempat alat-alat disimpan |
| Tailscale | 🛣️ **Jalan tol pribadi** | Jaringan privat agar sopir bisa sampai ke rumah dari mana pun |
| Proxy egress | 🚧 **Gerbang tol** | Jalan keluar wajib pada sebagian VM; SSH bisa dititipkan lewat sini |
| Shizuku | 🛡️ **Satpam baik** | Aplikasi yang memegang izin khusus dan mau menjalankannya untuk kita |
| `rish` | 🔔 **Bel satpam** | Cara memanggil satpam dari Termux agar perintahmu dijalankan dengan izinnya |
| `uid shell` (2000) | 🔑 **Kunci gudang** | Identitas resmi Android yang boleh membaca & menyentuh layar |
| ADB | 🚪 **Pintu samping** | Cara masuk dari komputer (USB/Wi-Fi); akhirnya memegang kunci gudang yang sama |
| Wireless Debugging | 📶 **Menyalakan pintu samping** | Pengaturan HP agar ADB nirkabel mau menerima tamu |
| `uiautomator dump` | 👁️ **Bertanya ke mata** | "HP, kamu lagi menampilkan apa?" — jawabannya daftar isi layar (XML) |
| Dump XML | 📋 **Daftar isi layar** | Teks berisi semua tombol/teks di layar + alamat (koordinat) masing-masing |
| `bounds` | 📍 **Alamat tombol** | Kotak koordinat sebuah elemen di layar; ketuk tengahnya |
| `input tap/swipe/text` | ✋ **Tangan** | Menyuntikkan ketukan, geseran, dan ketikan |
| `screencap` | 📸 **Foto bukti** | Tangkapan layar untuk memastikan hasil |
| `am start` | 🎯 **Teleport ke ruangan** | Membuka aplikasi langsung, tanpa mengetuk ikon berputar-putar |
| Lockscreen | 🔒 **Pintu dikunci dari dalam** | Sopir sopan: menunggu di luar, tidak akan menebak PIN |
| Loop kendali | 🔁 **Lihat–Pikir–Gerak–Cek** | Putaran kerja agent; tidak ada ketukan buta |
| scrcpy | 🪟 **Jendela intip** | Cermin layar di komputer; manusia bisa ikut melihat / mengambil alih |
| AutoX.js | 🤖 **Robot penghafal** | Skrip di dalam HP yang mengulang gerakan hafalan via aksesibilitas |
| proot | 🧳 **Koper Linux** | Lingkungan Linux lipat di dalam Termux |
| Wake lock | ☕ **Kopi untuk Termux** | Menahan Android agar tidak "menidurkan" aplikasi pengendali |

> Kalau ada istilah yang belum ada di sini dan membingungkanmu, itu bukan salahmu —
> itu utang dokumen ini. Catat, dan tambahkan saat mengedit.
