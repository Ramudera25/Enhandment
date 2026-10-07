# 02 — Tools

> 📦 **Bahasa bayi:** Ini daftar peralatannya sopir: kunci rumah (SSH), jalan tol
> (Tailscale), bel satpam (`rish`), mata (`uiautomator`), tangan (`input`), dan
> kamera bukti (`screencap`). Tidak ada alat sihir — semuanya bawaan atau gratis.

Inventaris komponen pada jalur utama (SSH → Termux → Shizuku/`rish`), beserta peran
dan cara verifikasi cepatnya. Semua nilai contoh memakai placeholder — jangan pernah
menaruh kredensial/IP pribadi asli di repo.

## Di sisi HP (Android)

| Tool | Jenis | Peran | Verifikasi |
|---|---|---|---|
| **Termux** | Aplikasi terminal | Rumah bagi `sshd`, `rish`, dan skrip agent di HP | `termux-info` |
| **OpenSSH (`sshd`)** | Paket Termux | Pintu masuk agent; autentikasi kunci publik | dari agent: `ssh <alias-hp> 'echo ok'` |
| **Termux:API** | Aplikasi + paket | Notifikasi (`termux-notification`), baterai, toast, TTS | `termux-battery-status` |
| **Shizuku** | Aplikasi | Server hak akses `shell`; jembatan `rish` | buka aplikasi: status "running" |
| **`rish` + `rish_shizuku.dex`** | File di home Termux | Entry point shell uid 2000 dari Termux | `RISH_APPLICATION_ID=<id-aplikasi> ./rish -c 'id'` → `uid=2000(shell)` |
| **proot-distro (opsional)** | Paket Termux | Lingkungan Linux penuh di dalam Termux (untuk agent yang tinggal di HP) | `proot-distro list` |

## Bawaan Android (dipakai lewat shell)

| Perintah | Peran |
|---|---|
| `uiautomator dump` | Membaca pohon elemen UI layar aktif (XML: teks, class, bounds) |
| `input tap/swipe/text/keyevent` | Menyuntikkan sentuhan, geseran, teks, tombol |
| `screencap -p` | Tangkapan layar PNG |
| `am start / force-stop` | Membuka / menghentikan aplikasi |
| `dumpsys window / power / activity` | Status jendela depan, layar kunci, daya |
| `pm list packages` | Inventaris aplikasi terpasang |

## Di sisi agent (VM/komputer)

| Tool | Peran |
|---|---|
| Klien **OpenSSH** | Menyambung ke Termux; konfigurasi alias + `ProxyCommand` bila perlu proxy egress |
| **Tailscale** | Menyediakan alamat stabil HP lintas jaringan (`100.x.y.z` / MagicDNS) |
| Agent itu sendiri (Muse, Hermes, skrip) | Otak loop kendali: baca layar → putuskan → aksi → verifikasi → catat |

## Tool alternatif (bukan jalur utama)

| Tool | Peran | Kapan dipilih |
|---|---|---|
| **adb** (Android SDK platform-tools) | Pintu shell klasik dari komputer/VM via USB/Wi-Fi | Agent tidak punya kunci SSH Termux, atau kontrolernya komputer (lihat `05`) |
| **scrcpy** | Mirror + kendali layar dari komputer | Manusia ikut menonton/mengambil alih |
| **AutoX.js / Auto.js** | Skrip otomasi di perangkat via Layanan Aksesibilitas | Tanpa shell sama sekali; alur pendek dan stabil tampilannya |
| **Appium / UiAutomator2 driver** | Framework uji otomatis | Kebutuhan testing formal, bukan operator harian |

## Catatan pemasangan (ringkas)

1. Pasang Termux (+ Termux:API) dari sumber resmi (F-Droid/GitHub), bukan Play Store lama.
2. `pkg install openssh termux-api` → buat kunci di sisi agent → pasang `.pub` ke
   `~/.ssh/authorized_keys` Termux → jalankan `sshd` (port bawaan Termux: 8022).
3. Pasang Shizuku → aktifkan sekali (Wireless Debugging → "Start via Wireless debugging",
   atau perintah ADB dari komputer) → salin `rish` + `rish_shizuku.dex` dari Shizuku ke
   home Termux → set `RISH_APPLICATION_ID` sesuai petunjuk Shizuku → tes `rish -c 'id'`.
4. Uji loop penuh dengan skrip `examples/cek-koneksi.sh`.
