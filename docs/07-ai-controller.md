# 07 — AI Controller: Siapa Otaknya?

> 📦 **Bahasa bayi:** Mobilnya (HP + kuasa shell) tidak peduli siapa sopirnya.
> Muse bisa, Hermes bisa, OpenCode bisa — syaratnya cuma dua: sopirnya bisa
> menyuruh lewat perintah shell, dan bisa membaca daftar isi layar. Ganti sopir,
> rumah dan jalannya tidak berubah.

Kendali HP ini **tidak terikat pada satu AI**. Syaratnya cuma dua:

1. AI-nya bisa **menjalankan perintah shell** (SSH / adb / lokal), dan
2. bisa **membaca teks** hasil `uiautomator dump` (XML) untuk memutuskan aksi berikutnya.

Model dengan kemampuan *vision* membantu (bisa membaca `screencap` juga), tapi tidak wajib —
pohon elemen XML sudah menceritakan hampir seluruh isi layar dalam bentuk teks.

## AI yang bisa (dan jalurnya)

| Controller | Tinggal di | Pintu yang biasa dipakai | Catatan |
|---|---|---|---|
| **Muse** | VM/server | SSH → Termux → `rish` | Jalur utama repo ini; terverifikasi end-to-end |
| **Hermes** | VM lain / di HP (proot) | ADB (Wireless Debugging) bila tak pegang kunci SSH; `rish` bila tinggal di HP | Lihat resep di bawah |
| **OpenCode** | VM/komputer | SSH atau ADB | Cukup beri brief + wrapper `scripts/hp.sh` |
| **pi** | VM/komputer | SSH atau ADB | Sama — ia hanya butuh perintah shell |
| **aider** | Komputer | ADB (USB) | Nyaman untuk pengembangan alur dari PC |
| **LLM agent lain** (framework apa pun) | Di mana saja | Pintu mana pun | Selama dua syarat di atas terpenuhi |

Intinya: mengganti AI = mengganti sopir. Mobil (HP + kuasa shell) dan jalan (pintu masuk)
tidak berubah.

## Resep universal: wrapper `hp.sh`

Agar AI tidak perlu menghafal perintah panjang, repo ini menyediakan satu perintah
seragam (ada di `scripts/hp.sh`):

```bash
hp.sh id        # verifikasi kuasa shell
hp.sh dump      # baca layar (XML)
hp.sh shot out.png   # tangkapan layar
hp.sh tap 540 1200
hp.sh text "Halo, saya melamar posisi ini…"
hp.sh key home
hp.sh open <paket>/<aktivitas>
```

Di balik layar ia memilih sendiri pintunya lewat variabel `HP_MODE`:

- `HP_MODE=rish` → lewat SSH ke Termux + `rish` (jalur utama).
- `HP_MODE=adb` → lewat `adb shell` dari komputer/VM.

Brief untuk AI mana pun kemudian cukup berbunyi: *"Gunakan `hp.sh`. Baca layar sebelum
setiap aksi. Verifikasi setelahnya. Berhenti dan lapor bila layar terkunci atau muncul
permintaan OTP/CAPTCHA."*

## Resep: Hermes (atau agent lain) dari VM terpisah via ADB

Kasus nyata yang menginspirasi dokumen ini: agent-nya tinggal di VM yang **tidak
memiliki kunci SSH Termux**. Ia memakai pintu ADB. Persiapannya:

**Di HP (sekali):** aktifkan **Wireless Debugging** (Tutorial 03, Langkah 2 butir 1–2).

**Di VM agent (sekali untuk pairing):**

```bash
# pasang adb (Debian/Ubuntu)
sudo apt install -y adb

# pairing — IP & port dari panel Wireless Debugging di HP
adb pair <ip-hp>:<port-pairing>        # masukkan kode pairing
adb connect <ip-hp>:<port-koneksi>
adb devices                            # harus tampil "device"
adb shell id                           # uid=2000(shell) — sampai!
```

**Jadikan `hp.sh` pintunya:**

```bash
export HP_MODE=adb
./scripts/hp.sh dump | head -c 400
```

**Sifat jujur jalur ini:** sesi ADB nirkabel mudah putus (Wireless Debugging mati,
HP restart, ganti jaringan) dan harus disambung ulang dari VM. Itulah alasan jalur
utama repo ini lebih memilih SSH + `rish`: tidak ada sesi yang harus dijaga hidup —
cukup Shizuku yang tetap berjalan di dalam HP.

## Resep: agent yang tinggal di HP itu sendiri

Sebagian agent bisa berjalan **di dalam Termux/proot HP** (mis. Hermes di proot).
Kalau begitu tidak ada SSH sama sekali — agent memanggil `rish` secara lokal:

```bash
export HP_MODE=rish-local
./scripts/hp.sh dump
```

Hemat jaringan, tapi ingat: agent dan yang dikendalikan berbagi nasib — HP mati,
keduanya mati.

## Brief siap copy-paste untuk AI barumu

Tempelkan ini sebagai instruksi tugas ke agent mana pun yang sudah tersambung:

```
Kamu mengendalikan HP Android lewat perintah `hp.sh` (lihat scripts/hp.sh).
Aturan:
1. Selalu mulai dengan `hp.sh id` (harus uid=2000) dan `hp.sh dump` sebelum aksi apa pun.
2. Satu aksi per langkah: tap/text/open, lalu `hp.sh dump` lagi untuk verifikasi.
   Jangan pernah mengasumsikan hasil ketukan.
3. Koordinat diambil dari atribut bounds pada dump terakhir — jangan menebak.
4. Tempo wajar: jeda beberapa detik antar aksi.
5. BERHENTI dan lapor bila: layar terkunci, muncul OTP/CAPTCHA/pairing,
   aplikasi meminta kredensial di luar otorisasi, atau 3 percobaan satu langkah gagal.
6. Catat setiap hasil akhir (berhasil/gagal + penyebab teramati) ke log yang diberikan.
Tugas: <tulis tugasmu di sini>
```
