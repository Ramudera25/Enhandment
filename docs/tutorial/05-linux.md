# Tutorial 05 — Persiapan dari Komputer Linux

**Tujuan akhir bab ini:** dari terminal, `adb shell id` menjawab `uid=2000(shell)`.
Waktu: ±10 menit. Jalur ini **tidak butuh** Termux/Tailscale/Shizuku.

## Langkah 1 — Sekali jalan: skrip persiapan

```bash
bash scripts/setup-linux.sh
```

Skrip itu (untuk keluarga Debian/Ubuntu) memasang: `adb`, `scrcpy`, `openssh-client`,
dan `tailscale`, lalu mengingatkan langkah di sisi HP. Manualnya pun singkat:

```bash
sudo apt update
sudo apt install -y adb scrcpy openssh-client
curl -fsSL https://tailscale.com/install.sh | sh   # hanya bila perlu jalur jaringan privat
```

Distribusi lain: paketnya bernama sama di hampir semua repo (`adb`/`android-tools`,
`scrcpy`). Arch: `sudo pacman -S android-tools scrcpy`. Fedora: `sudo dnf install android-tools scrcpy`.

## Langkah 2 — Aktifkan USB debugging di HP

1. **Pengaturan → Tentang → ketuk "Nomor build" 7×**.
2. **Pengaturan → Opsi Pengembang → aktifkan "USB debugging"**.
3. Colok USB → setujui dialog "Izinkan USB debugging?" di HP.

Di sebagian distribusi, user-mu perlu grup `plugdev` agar udev mengizinkan akses:

```bash
sudo usermod -aG plugdev "$USER"   # lalu logout-login
```

## Langkah 3 — Tes loop penuh

```bash
adb devices                                   # status harus "device"
adb shell id                                  # uid=2000(shell)
adb shell uiautomator dump /sdcard/d.xml && adb exec-out cat /sdcard/d.xml | head -c 400
adb shell input keyevent 3                    # HOME — layar HP harus bereaksi
scrcpy                                        # cermin layar (opsional, menyenangkan)
```

## Langkah 4 (opsional) — Jadikan mesin ini "agent server"

Komputer Linux yang menyala terus bisa berperan seperti VM di jalur utama:

- Pasang Tailscale (Langkah 1) bila HP harus dijangkau lintas jaringan lewat ADB Wi-Fi.
- Atau gabungkan kedua dunia: komputer ini masuk SSH ke Termux (Jalur A) —
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

Berikutnya: [../07-ai-controller.md](../07-ai-controller.md) untuk memilih otaknya.
