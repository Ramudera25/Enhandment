# Tutorial 04 — Persiapan dari Komputer Windows

> 📦 **Bahasa bayi:** Dari komputer, rumahnya tidak perlu dipasangi pintu baru —
> ada pintu samping (ADB) yang tinggal dibuka dengan kabel USB. Bonusnya: kamu
> dapat jendela intip (scrcpy) untuk menonton HP bekerja.

**Tujuan akhir bab ini:** dari PowerShell, perintah `adb shell id` menjawab
`uid=2000(shell)` — HP siap dikendalikan dari PC-mu. Waktu: ±10 menit.
Jalur ini **tidak butuh** Termux, Tailscale, maupun Shizuku.

## Checklist

### Bagian 1 — Sekali klik: skrip persiapan

- [ ] Buka **PowerShell**, arahkan ke folder repo ini
- [ ] Jalankan:

```powershell
./scripts/setup-windows.ps1
```

Skrip itu memasang lewat `winget`: **Android SDK Platform-Tools** (berisi `adb`),
**scrcpy** (cermin layar), dan **Tailscale** (opsional, hanya bila mau nirkabel lintas jaringan).

- [ ] Tidak mau skrip? Pasang manual:

```powershell
winget install --id Google.PlatformTools -e
winget install --id Genymobile.scrcpy -e
```

### Bagian 2 — Aktifkan USB debugging di HP

- [ ] **Pengaturan → Tentang → ketuk "Nomor build" 7×** (Opsi Pengembang aktif)
- [ ] **Pengaturan → Opsi Pengembang → aktifkan "USB debugging"**
- [ ] Colok HP ke PC dengan kabel USB
- [ ] Di HP muncul dialog "Izinkan USB debugging?" → **Izinkan** (centang "selalu")

### Bagian 3 — Tes

- [ ] Buka PowerShell **baru** (agar PATH segar), lalu:

```powershell
adb devices          # HP-mu harus tampil dengan status "device"
adb shell id         # → uid=2000(shell) …
```

- [ ] Coba membaca layar dan mengetuk:

```powershell
adb shell uiautomator dump /sdcard/d.xml
adb shell input tap 540 1200    # contoh koordinat
```

- [ ] Bonus — tonton HP-mu bergerak sendiri:

```powershell
scrcpy               # cermin layar + bisa diklik pakai mouse
```

## Mode nirkabel (opsional)

Satu Wi-Fi yang sama dengan PC:

- [ ] HP: **Opsi Pengembang → Wireless debugging → aktifkan**
- [ ] "Pair device with pairing code" → catat IP:port pairing + kodenya
- [ ] Di PowerShell:

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
- Masih buntu? → [../troubleshooting.md](../troubleshooting.md)

Berikutnya: beri dia otak → [../07-ai-controller.md](../07-ai-controller.md).
