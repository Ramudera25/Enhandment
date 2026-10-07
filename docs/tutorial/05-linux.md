# Tutorial 05 — Persiapan dari Komputer Linux

> 📦 **Bahasa bayi:** Versi terminal dari bab Windows. Pintu samping (ADB) dibuka
> lewat kabel, komputer Linux-mu jadi ruang kemudi — dan bila ia menyala 24 jam,
> ia bahkan bisa naik pangkat jadi rumah permanen sang sopir.

**Tujuan akhir bab ini:** dari terminal, `adb shell id` menjawab `uid=2000(shell)`.
Waktu: ±10 menit. Jalur ini **tidak butuh** Termux/Tailscale/Shizuku.

## Checklist

### Bagian 1 — Sekali jalan: skrip persiapan

- [ ] Jalankan:

```bash
bash scripts/setup-linux.sh
```

Skrip itu (keluarga Debian/Ubuntu) memasang: `adb`, `scrcpy`, `openssh-client`,
dan `tailscale` (opsional), lalu mengingatkan langkah di sisi HP.

- [ ] Atau manual:

```bash
sudo apt update
sudo apt install -y adb scrcpy openssh-client
curl -fsSL https://tailscale.com/install.sh | sh   # hanya bila perlu jalur jaringan privat
```

Distribusi lain: Arch `sudo pacman -S android-tools scrcpy` ·
Fedora `sudo dnf install android-tools scrcpy`.

### Bagian 2 — Aktifkan USB debugging di HP

- [ ] **Pengaturan → Tentang → ketuk "Nomor build" 7×**
- [ ] **Pengaturan → Opsi Pengembang → aktifkan "USB debugging"**
- [ ] Colok USB → setujui dialog "Izinkan USB debugging?" di HP
- [ ] (Sebagian distribusi) beri user-mu akses USB Android, lalu logout-login:

```bash
sudo usermod -aG plugdev "$USER"
```

### Bagian 3 — Tes loop penuh

- [ ] Jalankan satu per satu:

```bash
adb devices                                   # status harus "device"
adb shell id                                  # uid=2000(shell)
adb shell uiautomator dump /sdcard/d.xml && adb exec-out cat /sdcard/d.xml | head -c 400
adb shell input keyevent 3                    # HOME — layar HP harus bereaksi
scrcpy                                        # cermin layar (opsional, menyenangkan)
```

Semua bereaksi? 🐧 Selesai — HP-mu sudah bisa dikemudikan dari sini.

### Bagian 4 (opsional) — Jadikan mesin ini "agent server"

Komputer Linux yang menyala terus bisa berperan seperti VM di jalur utama:

- [ ] Pasang Tailscale (Bagian 1) bila HP harus dijangkau lintas jaringan via ADB Wi-Fi, atau
- [ ] Gabungkan dua dunia: komputer ini masuk SSH ke Termux (Jalur A) —
  ikuti [01 — Termux](01-termux.md) & [02 — Tailscale](02-tailscale.md);
  kunci SSH dibuat cukup dengan:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/termux_hp
ssh-copy-id -i ~/.ssh/termux_hp.pub -p 8022 <user-termux>@<alamat-hp>   # bila sshd Termux siap
```

## Kalau gagal

- **`no permissions`** → masalah udev: tambahkan grup `plugdev`, atau pasang aturan
  `android-sdk-platform-tools-common` (Debian/Ubuntu), lalu cabut-colok.
- **`unauthorized`** → setujui dialog di HP (layar harus terbuka saat mencolok).
- **Perangkat kosong** → kabel data vs kabel cas; ganti kabel/port.
- **`adb server` bentrok versi** → `adb kill-server && adb start-server`.
- Masih buntu? → [../troubleshooting.md](../troubleshooting.md)

Berikutnya: [../07-ai-controller.md](../07-ai-controller.md) untuk memilih otaknya.
