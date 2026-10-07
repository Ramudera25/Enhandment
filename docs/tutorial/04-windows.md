# Tutorial 04 — Persiapan dari Komputer Windows

**Tujuan akhir bab ini:** dari PowerShell, perintah `adb shell id` menjawab
`uid=2000(shell)` — HP siap dikendalikan dari PC-mu. Waktu: ±10 menit.
Jalur ini **tidak butuh** Termux, Tailscale, maupun Shizuku.

## Langkah 1 — Sekali klik: skrip persiapan

Buka **PowerShell**, arahkan ke folder repo ini, lalu:

```powershell
./scripts/setup-windows.ps1
```

Skrip itu memasang lewat `winget`: **Android SDK Platform-Tools** (berisi `adb`),
**scrcpy** (cermin layar), dan **Tailscale** (opsional, hanya bila mau nirkabel lintas jaringan).
Tidak mau skrip? Pasang manual:

```powershell
winget install --id Google.PlatformTools -e
winget install --id Genymobile.scrcpy -e
```

## Langkah 2 — Aktifkan USB debugging di HP

1. **Pengaturan → Tentang → ketuk "Nomor build" 7×** (Opsi Pengembang aktif).
2. **Pengaturan → Opsi Pengembang → aktifkan "USB debugging"**.
3. Colok HP ke PC dengan kabel USB.
4. Di HP muncul dialog "Izinkan USB debugging?" → **Izinkan** (centang "selalu").

## Langkah 3 — Tes

```powershell
adb devices          # HP-mu harus tampil dengan status "device"
adb shell id         # → uid=2000(shell) …
adb shell uiautomator dump /sdcard/d.xml; adb shell cat /sdcard/d.xml   # membaca layar
adb shell input tap 540 1200    # mengetuk (contoh koordinat)
```

Berhasil? Kamu sudah memegang kedua kuasa itu. Lihat HP-mu bergerak sendiri lewat:

```powershell
scrcpy               # cermin layar + bisa diklik pakai mouse
```

## Mode nirkabel (opsional)

Satu Wi-Fi yang sama dengan PC:

1. HP: **Opsi Pengembang → Wireless debugging → aktifkan**.
2. "Pair device with pairing code" → catat IP:port pairing + kodenya.
3. Di PowerShell:

```powershell
adb pair <ip>:<port-pairing>     # masukkan kode saat diminta
adb connect <ip>:<port-wireless-debugging>
adb devices                      # sekarang tanpa kabel
```

⚠️ Koneksi nirkabel putus bila Wireless debugging dimatikan, HP restart, atau ganti
jaringan. Untuk operasi yang serius dan lama, **kabel USB tetap raja**.

## Kalau gagal

- **`adb` tidak dikenal** → Platform-Tools belum terpasang atau PowerShell belum
  dibuka ulang setelah instalasi. Tutup-buka PowerShell, coba lagi.
- **Status `unauthorized`** → dialog izin di HP belum disetujui. Cabut-colok kabel,
  dialognya muncul lagi.
- **Perangkat tidak tampil sama sekali** → kabel hanya untuk mengisi daya (coba kabel
  lain), atau mode USB di HP perlu diubah ke "Transfer file".
- **`winget` tidak ada** → perbarui "App Installer" dari Microsoft Store, atau unduh
  platform-tools manual dari developer.android.com lalu tambahkan ke PATH.

Berikutnya: beri dia otak → [../07-ai-controller.md](../07-ai-controller.md).
