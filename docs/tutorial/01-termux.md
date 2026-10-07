# Tutorial 01 — Termux: Terminal & Pintu Masuk di HP

**Tujuan akhir bab ini:** dari mesin agent, kamu bisa mengetik `ssh termux-hp` dan
langsung masuk ke HP. Waktu: ±15 menit.

## Apa itu Termux?

Termux adalah aplikasi terminal Linux untuk Android — anggap saja "jendela perintah"
di HP. Di dalamnya kita memasang **sshd** (server SSH), yaitu pintu yang akan dimasuki
agent dari jauh. Tanpa root, tanpa oprek aneh-aneh.

## Langkah 1 — Pasang Termux (dan Termux:API)

1. Unduh Termux dari **F-Droid** atau **GitHub releases resmi Termux**.
   ⚠️ Jangan pakai versi Play Store — itu versi lama yang sudah tidak diperbarui,
   sumber masalah klasik pemula.
2. Pasang juga **Termux:API** (dari sumber yang sama) — dipakai untuk notifikasi dsb.

## Langkah 2 — Perintah pertama

Buka Termux, lalu jalankan (copy-paste saja):

```bash
pkg update -y && pkg upgrade -y
pkg install -y openssh termux-api
termux-setup-storage    # meminta izin akses penyimpanan — izinkan
```

## Langkah 3 — Sekali klik: skrip persiapan repo ini

Repo ini menyediakan skrip yang melakukan sisanya (memasang paket pendukung dan
menyiapkan kunci). Salin repo ke HP (atau unduh file skripnya), lalu:

```bash
bash scripts/setup-termux.sh
```

Skrip ini akan: memasang `openssh` bila belum ada, membuat direktori `.ssh`,
dan menampilkan perintah lanjutan dengan jelas. Aman dijalankan berulang kali.

## Langkah 4 — Pasang kunci publik agent

Agent masuk pakai **kunci**, bukan password — lebih aman dan tidak perlu mengetik apa pun.

Di **mesin agent** (sekali saja, bila belum punya kunci):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/termux_hp
cat ~/.ssh/termux_hp.pub      # ini kunci publiknya — yang ini boleh dibagikan
```

Salin isi kunci publik itu ke HP, simpan sebagai file `kunci.pub`, lalu di Termux:

```bash
mkdir -p ~/.ssh
cat kunci.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## Langkah 5 — Nyalakan pintu (sshd)

Di Termux:

```bash
sshd            # mulai server SSH (port bawaan Termux: 8022)
whoami          # catat username-mu (contoh: u0_a261)
```

Agar sshd ikut menyala tiap Termux dibuka, tambahkan baris `sshd` ke `~/.bashrc`:

```bash
echo 'sshd 2>/dev/null' >> ~/.bashrc
```

Tips daya: jalankan `termux-wake-lock` agar Android tidak membunuh Termux saat layar mati,
dan kecualikan Termux dari penghemat baterai di Pengaturan Android.

## Langkah 6 — Buat alias di mesin agent

Di mesin agent, tambahkan ke `~/.ssh/config`:

```
Host termux-hp
    HostName <alamat-hp>        # diisi setelah bab Tailscale (02)
    User <username-termuxmu>
    Port 8022
    IdentityFile ~/.ssh/termux_hp
```

Uji (setelah Tailscale tersambung di bab berikut):

```bash
ssh termux-hp 'echo "Halo dari HP!"'
```

Kalau balasan itu muncul: **pintu selesai.** 🎉 Lanjut ke [02 — Tailscale](02-tailscale.md).

## Kalau gagal

- **`Connection refused`** → `sshd` belum jalan di Termux. Jalankan `sshd` lagi.
- **`Permission denied (publickey)`** → kunci publik belum masuk `authorized_keys`,
  atau izin file salah. Ulangi Langkah 4 dan pastikan `chmod 600`.
- **Koneksi putus-putus** → Android membunuh Termux. `termux-wake-lock` +
  kecualikan dari penghemat baterai.
- **Nama user tidak tahu** → di Termux ketik `whoami`.
