# Tutorial 02 — Tailscale: Jalan Tol Pribadi HP ↔ Mesin Agent

**Tujuan akhir bab ini:** HP dan mesin agent saling terjangkau dengan alamat tetap,
dari jaringan mana pun. Waktu: ±10 menit.

## Kenapa Tailscale?

HP berpindah-pindah jaringan (Wi-Fi rumah, kantor, data seluler) dan alamat IP-nya
berubah-ubah. Tailscale memberi setiap perangkat **alamat tetap** (`100.x.y.z`) dan
nama (MagicDNS), terenkripsi, tanpa membuka port apa pun ke internet publik.
Anggap saja kabel LAN virtual yang sangat panjang.

> Satu Wi-Fi yang sama? Langkah ini bisa dilewati — pakai alamat IP lokal HP.
> Tapi untuk agent di server/VPS, Tailscale praktis wajib.

## Langkah 1 — Pasang di kedua sisi

**Di HP:** pasang aplikasi **Tailscale** dari Play Store / F-Droid → masuk dengan
akun yang sama (Google/GitHub/Microsoft — bebas, yang penting sama).

**Di mesin agent (Linux/VM):**

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**Di Windows:** unduh dari tailscale.com/download → pasang → masuk akun yang sama.

## Langkah 2 — Catat alamat HP

Buka aplikasi Tailscale di HP → perangkatmu sendiri akan tampil dengan alamat
`100.x.y.z` dan nama MagicDNS (mis. `samsung-a13.tailnet-xxxx.ts.net`).
Catat salah satunya.

Cek dari mesin agent:

```bash
tailscale status        # HP-mu harus tampil di daftar
ping <alamat-hp>        # balas? bagus.
```

## Langkah 3 — Isi alamat ke konfigurasi SSH

Kembali ke `~/.ssh/config` di mesin agent (dari Tutorial 01), isi:

```
Host termux-hp
    HostName <alamat-tailscale-hp>
    User <username-termuxmu>
    Port 8022
    IdentityFile ~/.ssh/termux_hp
```

Uji penuh:

```bash
ssh termux-hp 'echo "Halo dari HP!" && whoami'
```

## Catatan untuk lingkungan VM khusus

Sebagian VM/server hanya boleh keluar lewat **proxy egress**. Gejalanya: `tailscale`
tersambung tapi SSH ke HP "reset" atau timeout. Solusinya, bungkus SSH dengan
`ProxyCommand` yang meneruskan koneksi lewat proxy tersebut (penyedia VM-mu biasanya
mendokumentasikan host & port-nya). Contoh pola:

```
Host termux-hp
    ProxyCommand <perintah-proxy-ke-%h:%p>
    ...
```

Detail pola ini tergantung penyedia — yang penting diingat: **SSH itu bisa dititipkan
lewat proxy**, jadi jangan menyerah hanya karena jalur langsungnya tertutup.

## Kalau gagal

- **HP tidak tampil di `tailscale status`** → aplikasi Tailscale di HP belum masuk
  akun yang sama, atau VPN-nya belum diaktifkan (saklar di aplikasi).
- **`ping` diam saja** → wajar bila HP menghemat daya; coba bangunkan layar HP lalu ulangi.
- **Dua VPN bertabrakan** → Android hanya mengizinkan satu VPN aktif; matikan VPN lain.
- **SSH tetap gagal padahal ping jalan** → itu urusan bab 01 (`sshd`/kunci), bukan Tailscale.

Lanjut: [03 — Shizuku](03-shizuku.md) untuk membuka kuasa shell-nya.
