# Tutorial 00 — Mulai di Sini (Peta Jalan Pemula)

> 📦 **Bahasa bayi:** Kamu akan menyambungkan tiga hal: sopir (AI), pintu masuk,
> dan kunci gudang (kuasa shell). Halaman ini cuma peta — pilih jalanmu, lalu ikuti
> tanda-tandanya satu per satu. Setiap tutorial berbentuk checklist: centang sambil jalan.

Selamat datang! Halaman ini adalah **satu-satunya halaman yang wajib kamu baca dulu**.
Sisanya tinggal mengikuti jalur yang kamu pilih.

## Gambaran besarnya

```
AI agent  ──(jaringan)──►  pintu masuk di HP  ──(kuasa shell)──►  layar HP
  (sopir)                     (pintu)              (kunci gudang)
```

- **AI agent**: "otak" yang membaca layar dan memutuskan ketukan (Muse, Hermes, dsb.).
- **Pintu masuk**: cara agent masuk ke HP — SSH ke Termux, atau ADB dari komputer.
- **Kuasa shell**: identitas `uid shell` Android yang bisa membaca & menyentuh layar,
  didapat lewat Shizuku (di HP) atau langsung dari ADB (dari komputer).

## Tiga jalur — pilih satu

### Jalur A — Server/VM (jalur utama repo ini) 🏆
Agent tinggal di server/VM dan mengendalikan HP dari jauh, 24 jam.
Urutan tutorial:
1. [01 — Termux](01-termux.md): pasang Termux + pintu SSH di HP.
2. [02 — Tailscale](02-tailscale.md): sambungkan HP ↔ server dengan jaringan privat.
3. [03 — Shizuku](03-shizuku.md): aktifkan kuasa shell di HP.

### Jalur B — Komputer Windows 🪟
Agent/manusia mengendalikan dari PC Windows lewat kabel USB atau Wi-Fi.
Cukup satu tutorial: [04 — Windows](04-windows.md).

### Jalur C — Komputer Linux 🐧
Sama seperti B, dari terminal Linux.
Cukup satu tutorial: [05 — Linux](05-linux.md).

> Jalur B/C tidak butuh Termux/Tailscale/Shizuku sama sekali — ADB via USB langsung
> memberi kuasa shell. Jalur A lebih repot di awal, tapi satu-satunya yang membuat
> HP bisa bekerja saat kamu tidak di depan komputer sama sekali.

## Yang kamu butuhkan

- [ ] 1 HP Android (versi 8+ disarankan; makin nganggur HP-nya, makin ideal)
- [ ] Untuk Jalur A: satu mesin agent (server/VM/komputer yang menyala) untuk tempat AI tinggal
- [ ] Untuk Jalur B/C: satu kabel USB (atau Wi-Fi yang sama untuk mode nirkabel)
- [ ] Waktu ±30–45 menit untuk persiapan pertama — sekali saja, setelah itu tinggal pakai

## Setelah persiapan selesai

- [ ] Verifikasi: jalankan `examples/cek-koneksi.sh` (Jalur A) atau `adb devices` (Jalur B/C)
- [ ] Pelajari loop kerjanya: [../03-workflow.md](../03-workflow.md)
- [ ] Lihat satu misi utuh: [../08-misi-lengkap.md](../08-misi-lengkap.md)
- [ ] Pilih otaknya: [../07-ai-controller.md](../07-ai-controller.md)

## Kalau tersesat

- Setiap tutorial punya bagian **"Kalau gagal"** di bawahnya — dan semuanya bermuara
  ke satu tempat: [../troubleshooting.md](../troubleshooting.md) (pohon keputusan).
- Istilah asing? Cek [../glosarium.md](../glosarium.md) — kamus bahasa bayinya.
