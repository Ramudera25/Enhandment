# 01 — Arsitektur

## Prinsip dasar

Android mengenal identitas khusus `shell` (uid 2000), dipakai oleh ADB dan tool bawaan
sistem. Grup yang menyertainya (`input`, `adb`, `log`, `sdcard_rw`, `inet`, …) memberinya
dua kuasa yang relevan untuk otomasi:

1. **Membaca keadaan UI** — lewat `uiautomator` (pohon elemen) dan `screencap` (piksel).
2. **Menyuntikkan input** — lewat `input` (tap, swipe, text, keyevent).

Setiap pendekatan kendali HP — Shizuku, ADB, bahkan layanan aksesibilitas — pada akhirnya
adalah cara berbeda untuk mendapatkan dua kuasa ini. Perbedaan pendekatan = perbedaan
**pintu** dan **siapa yang memegang kuncinya**, bukan perbedaan kemampuan akhir.

## Lapisan sistem

### L1 — Jaringan
Agent dan HP harus saling terjangkau. Opsi yang terverifikasi:

- **Tailscale** (mesh VPN): HP dapat dijangkau dari VM mana pun, lintas jaringan,
  tanpa membuka port publik. Cocok untuk agent yang hidup di server.
- **Satu LAN**: paling sederhana bila agent berjalan di komputer serumah.
- Dalam beberapa lingkungan VM, lalu lintas keluar harus lewat proxy egress —
  SSH dapat dibungkus `ProxyCommand` agar tetap tersambung ke jaringan mesh.

### L2 — Pintu masuk ke HP
- **Termux + `sshd`**: server SSH ringan di HP, autentikasi kunci (tanpa password).
  Ini pintu yang dipakai jalur utama: agent masuk sebagai user Termux.
- Alternatif pintu: sesi **ADB** (lihat `04-alternatif-controller.md`).

### L3 — Jembatan hak akses (privilege bridge)
User Termux biasa tidak punya kuasa `input`. Di sinilah Shizuku berperan:

- **Shizuku** adalah aplikasi Android yang menjalankan server dengan hak `shell`
  (diaktifkan sekali lewat Wireless Debugging atau ADB dari komputer).
- **`rish`** adalah entry point-nya dari Termux: menjalankan perintah dengan
  `uid=2000(shell)`. Verifikasi cukup satu perintah: `rish -c 'id'`
  → mengembalikan `uid=2000(shell) gid=2000(shell) groups=...,1004(input),...`.

Selama proses server Shizuku hidup, pintu ini terbuka. Ia mati bila HP restart
atau prosesnya terbunuh sistem — aktivasi ulang satu kali dari HP.

### L4 — Persepsi (melihat)
- `uiautomator dump /dev/tty` (atau ke file): XML pohon elemen layar aktif —
  teks, class, `resource-id`, dan `bounds` (koordinat) tiap elemen.
  Inilah "mata" utama: agent membaca layar seperti membaca DOM halaman web.
- `screencap -p <file>`: tangkapan layar PNG untuk verifikasi visual / bukti.

### L5 — Aksi (menyentuh)
- `input tap <x> <y>`, `input swipe <x1> <y1> <x2> <y2> <ms>`,
  `input text "<teks>"`, `input keyevent <kode>` (BACK=4, HOME=3, WAKEUP=224, ENTER=66).
- `am start -n <paket>/<aktivitas>`: membuka aplikasi secara deterministik.

### L6 — Loop agent
Lapisan kecerdasan: agent membaca state (L4), memutuskan aksi berikutnya (L5),
memverifikasi, mencatat, dan tahu kapan berhenti. Lapisan ini yang membedakan
"skrip maksa" dari "operator": ia reaktif terhadap isi layar, bukan urutan buta.

## Alur data satu perintah (contoh: mengetuk tombol "Kirim")

```
agent ──SSH──► Termux: RISH_APPLICATION_ID=<id> ./rish -c 'input tap 540 2100'
                     │
                     └─► proses server Shizuku (uid shell) menyuntikkan event input
                         ke InputManager ──► aplikasi menerima ketukan persis seperti jari
agent ──SSH──► rish -c 'uiautomator dump' ──► XML baru ──► agent memastikan layar berubah
```

## Kenapa jalur aplikasi-native bisa lolos saat web gagal

Aplikasi di HP memakai sesi login asli pengguna, identitas perangkat asli, dan
API aplikasi itu sendiri. Hambatan khas web otomatis (CAPTCHA Cloudflare berbasis
sidik jari browser/IP pusat data) tidak terlibat sama sekali. Bukan sulap anti-deteksi —
hanya jalur yang berbeda secara fundamental dari browser.
