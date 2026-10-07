# Tutorial 01 — Termux: Terminal & Pintu Masuk di HP

> 📦 **Bahasa bayi:** Kita memasang ruang kerja (Termux) di dalam rumah (HP),
> lalu memasang pintu depan (sshd) lengkap dengan kunci rumahnya (kunci SSH).
> Centang kotak sambil jalan — selesai bab ini, sopir bisa masuk.

**Tujuan akhir bab ini:** dari mesin agent, kamu bisa mengetik `ssh termux-hp` dan
langsung masuk ke HP. Waktu: ±15 menit.

## Apa itu Termux?

Termux adalah aplikasi terminal Linux untuk Android — anggap saja "jendela perintah"
di HP. Di dalamnya kita memasang **sshd** (server SSH), yaitu pintu yang akan dimasuki
agent dari jauh. Tanpa root, tanpa oprek aneh-aneh.

## Checklist

### Bagian 1 — Pasang aplikasinya

- [ ] Unduh **Termux** dari **F-Droid** atau **GitHub releases resmi Termux**
  - ⚠️ Jangan pakai versi Play Store — itu versi lama yang sudah tidak diperbarui,
    sumber masalah klasik pemula.
- [ ] Pasang juga **Termux:API** dari sumber yang sama (untuk notifikasi dsb.)
- [ ] Buka Termux — kamu disambut layar hitam dengan prompt. Itu normal, jangan takut.

### Bagian 2 — Perintah pertama (copy-paste)

- [ ] Jalankan di Termux:

```bash
pkg update -y && pkg upgrade -y
pkg install -y openssh termux-api
termux-setup-storage    # meminta izin akses penyimpanan — izinkan
```

### Bagian 3 — Sekali klik: skrip persiapan repo ini

- [ ] Salin repo ini ke HP (atau unduh file skripnya), lalu jalankan:

```bash
bash scripts/setup-termux.sh
```

Skrip ini memasang paket pendukung, menyiapkan folder `.ssh`, dan menyalakan sshd.
Aman dijalankan berulang kali.

### Bagian 4 — Pasang kunci publik agent

Agent masuk pakai **kunci**, bukan password — lebih aman dan tidak perlu mengetik apa pun.

- [ ] Di **mesin agent** (sekali saja, bila belum punya kunci):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/termux_hp
cat ~/.ssh/termux_hp.pub      # kunci PUBLIK — yang ini boleh dibagikan
```

- [ ] Salin isi kunci publik itu ke HP, simpan sebagai file `kunci.pub`
- [ ] Di Termux, daftarkan kuncinya:

```bash
mkdir -p ~/.ssh
cat kunci.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Bagian 5 — Nyalakan pintunya

- [ ] Di Termux:

```bash
sshd            # mulai server SSH (port bawaan Termux: 8022)
whoami          # catat username-mu (contoh: u0_a261) — tulis di sini: ______
```

- [ ] Agar sshd ikut menyala tiap Termux dibuka:

```bash
echo 'sshd 2>/dev/null' >> ~/.bashrc
```

- [ ] Jalankan `termux-wake-lock` (kopi untuk Termux, agar tidak ditidurkan Android)
- [ ] Kecualikan Termux dari penghemat baterai di Pengaturan Android

### Bagian 6 — Buat alias di mesin agent

- [ ] Di mesin agent, tambahkan ke `~/.ssh/config`:

```
Host termux-hp
    HostName <alamat-hp>        # diisi setelah bab Tailscale (02)
    User <username-termuxmu>
    Port 8022
    IdentityFile ~/.ssh/termux_hp
```

- [ ] Uji (setelah Tailscale tersambung di bab berikut):

```bash
ssh termux-hp 'echo "Halo dari HP!"'
```

Balasan itu muncul? **Pintu selesai.** 🎉 Lanjut ke [02 — Tailscale](02-tailscale.md).

## Kalau gagal

- **`Connection refused`** → `sshd` belum jalan di Termux. Jalankan `sshd` lagi.
- **`Permission denied (publickey)`** → kunci publik belum masuk `authorized_keys`,
  atau izin file salah. Ulangi Bagian 4 dan pastikan `chmod 600`.
- **Koneksi putus-putus** → Android membunuh Termux. `termux-wake-lock` +
  kecualikan dari penghemat baterai.
- **Nama user tidak tahu** → di Termux ketik `whoami`.
- Masih buntu? → [../troubleshooting.md](../troubleshooting.md)
