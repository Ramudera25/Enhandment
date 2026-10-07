# Tutorial 02 — Tailscale: Jalan Tol Pribadi HP ↔ Mesin Agent

> 📦 **Bahasa bayi:** Rumah (HP) kamu pindah-pindah alamat terus. Tailscale memberinya
> alamat tetap dan jalan tol pribadi yang terenkripsi, supaya sopir selalu tahu
> harus ke mana — dari jaringan mana pun, tanpa membuka pintu ke publik.

**Tujuan akhir bab ini:** HP dan mesin agent saling terjangkau dengan alamat tetap,
dari jaringan mana pun. Waktu: ±10 menit.

## Kenapa Tailscale?

HP berpindah-pindah jaringan (Wi-Fi rumah, kantor, data seluler) dan alamat IP-nya
berubah-ubah. Tailscale memberi setiap perangkat **alamat tetap** (`100.x.y.z`) dan
nama (MagicDNS), terenkripsi, tanpa membuka port apa pun ke internet publik.

> Satu Wi-Fi yang sama? Langkah ini bisa dilewati — pakai alamat IP lokal HP.
> Tapi untuk agent di server/VPS, Tailscale praktis wajib.

## Checklist

### Bagian 1 — Pasang di kedua sisi (akun yang sama!)

- [ ] **Di HP:** pasang aplikasi **Tailscale** (Play Store / F-Droid) → masuk dengan akunmu
- [ ] **Di mesin agent (Linux/VM):**

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

- [ ] **Di Windows:** unduh dari tailscale.com/download → pasang → masuk akun yang sama
- [ ] Aktifkan saklar VPN Tailscale di aplikasi HP sampai statusnya tersambung

### Bagian 2 — Catat alamat HP

- [ ] Buka aplikasi Tailscale di HP → catat alamat perangkatmu (`100.x.y.z`)
  dan/atau nama MagicDNS-nya — tulis di sini: ______
- [ ] Dari mesin agent, cek:

```bash
tailscale status        # HP-mu harus tampil di daftar
ping <alamat-hp>        # ada balasan? bagus.
```

### Bagian 3 — Isi alamat ke konfigurasi SSH

- [ ] Kembali ke `~/.ssh/config` di mesin agent (dari Tutorial 01), lengkapi:

```
Host termux-hp
    HostName <alamat-tailscale-hp>
    User <username-termuxmu>
    Port 8022
    IdentityFile ~/.ssh/termux_hp
```

- [ ] Uji penuh:

```bash
ssh termux-hp 'echo "Halo dari HP!" && whoami'
```

Berhasil? 🛣️ Jalan tol resmi dibuka. Lanjut: [03 — Shizuku](03-shizuku.md).

## Catatan untuk lingkungan VM khusus

Sebagian VM/server hanya boleh keluar lewat **proxy egress** (gerbang tol).
Gejalanya: Tailscale tersambung tapi SSH ke HP "reset" atau timeout. Solusinya,
bungkus SSH dengan `ProxyCommand` yang meneruskan koneksi lewat proxy tersebut
(penyedia VM-mu biasanya mendokumentasikan host & port-nya). Contoh pola:

```
Host termux-hp
    ProxyCommand <perintah-proxy-ke-%h:%p>
    ...
```

Yang penting diingat: **SSH bisa dititipkan lewat proxy** — jangan menyerah hanya
karena jalur langsungnya tertutup.

## Kalau gagal

- **HP tidak tampil di `tailscale status`** → aplikasi di HP belum masuk akun yang
  sama, atau VPN-nya belum diaktifkan (saklar di aplikasi).
- **`ping` diam saja** → HP sedang menghemat daya; bangunkan layarnya, ulangi.
- **Dua VPN bertabrakan** → Android hanya mengizinkan satu VPN aktif; matikan VPN lain.
- **SSH tetap gagal padahal ping jalan** → itu urusan bab 01 (`sshd`/kunci), bukan Tailscale.
- Masih buntu? → [../troubleshooting.md](../troubleshooting.md)
