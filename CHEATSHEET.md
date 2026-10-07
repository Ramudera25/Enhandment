# CHEATSHEET — Semua Perintah Penting, Satu Halaman

> 📦 **Bahasa bayi:** Ini contekan di dinding. Semua yang sering dipakai, tanpa cerita.
> Istilahnya lupa? [docs/glosarium.md](docs/glosarium.md). Macet? [docs/troubleshooting.md](docs/troubleshooting.md).

## Cara seragam (untuk manusia & AI) — `scripts/hp.sh`

```bash
export HP_MODE=rish          # rish (bawaan) | rish-local | adb
hp.sh id                     # harus menjawab uid=2000(shell)
hp.sh dump                   # baca layar (XML)
hp.sh shot bukti.png         # tangkapan layar
hp.sh tap 540 1200           # ketuk koordinat
hp.sh swipe 540 1600 540 700 # geser ke atas
hp.sh text "isi teks"        # mengetik
hp.sh key home               # home | back | enter | wakeup
hp.sh open <paket>/<aktivitas>   # buka aplikasi
```

## Jalur A — SSH + Termux + rish (mentahnya)

```bash
ssh termux-hp                                   # masuk ke Termux HP
ssh termux-hp 'echo ok'                         # tes pintu
RISH="RISH_APPLICATION_ID=com.termux ./rish -c"
ssh termux-hp "$RISH 'id'"                      # uid=2000?
ssh termux-hp "$RISH 'uiautomator dump /sdcard/d.xml; cat /sdcard/d.xml'"
ssh termux-hp "$RISH 'input tap 540 1200'"
ssh termux-hp "$RISH 'am start -n <paket>/<aktivitas>'"
examples/cek-koneksi.sh                         # verifikasi 4 syarat sekaligus
```

Di dalam Termux (di HP):

```bash
sshd                    # nyalakan pintu
termux-wake-lock        # kopi untuk Termux
whoami                  # username-mu
RISH_APPLICATION_ID=com.termux ./rish -c 'id'   # tes satpam
```

## Jalur B/C — ADB dari komputer

```bash
adb devices                       # HP tampil? status "device"?
adb shell id                      # uid=2000(shell)
adb shell uiautomator dump /sdcard/d.xml
adb exec-out screencap -p > layar.png
adb shell input tap 540 1200
adb shell input text "halo"
adb shell input keyevent 3        # HOME (4=BACK, 66=ENTER, 224=WAKEUP)
adb shell am start -n <paket>/<aktivitas>
scrcpy                            # cermin layar
# nirkabel:
adb pair <ip>:<port-pairing>
adb connect <ip>:<port>
```

## Jaringan (Tailscale)

```bash
tailscale status        # siapa saja yang tersambung
tailscale ip -4         # alamatmu sendiri
ping <alamat-hp>        # HP terjangkau?
```

## Kunci SSH

```bash
ssh-keygen -t ed25519 -f ~/.ssh/termux_hp        # buat kunci (di mesin agent)
cat ~/.ssh/termux_hp.pub                          # kunci publik — boleh dibagikan
# di Termux: cat kunci.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

## Pertolongan pertama

| Keadaan | Perintah / tindakan |
|---|---|
| Habis restart HP | Termux: `sshd` · Shizuku: Start · lalu `cek-koneksi.sh` |
| Layar terkunci | Buka kunci HP-nya. Titik. |
| ADB nirkabel putus | `adb connect` ulang, atau kembali ke USB |
| Semua gagal | Ikuti pohon di [docs/troubleshooting.md](docs/troubleshooting.md) |
