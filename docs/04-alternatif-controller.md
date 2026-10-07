# 04 — Alternatif Controller

Kemampuan akhirnya selalu sama — **lihat layar + sentuh layar** — tetapi "siapa yang
mengendalikan" dan "lewat pintu apa" bisa berbeda. Dokumen ini memetakan alternatifnya,
termasuk bila otaknya diganti AI lain (mis. Hermes) atau pendekatannya diganti total.

## A. Agent lain di VM lain (kasus Hermes)

Skenario terverifikasi: sebuah agent (Hermes) berjalan di VM terpisah yang **tidak
memegang kunci SSH Termux** milik jalur utama. Akibatnya ia memilih pintu lain:

| Aspek | Jalur utama (repo ini) | Jalur agent di VM lain (ADB) |
|---|---|---|
| Pintu masuk | SSH → Termux → `rish` (Shizuku) | `adb` via Wireless Debugging |
| Kunci/kredensial | Pasangan kunci SSH (di VM pemilik jalur) | Pasangan kunci ADB sendiri (`~/.android/adbkey` di VM itu) |
| Syarat di HP | Shizuku hidup; sshd hidup | Wireless Debugging **harus tetap hidup** selama sesi; koneksi ADB mudah putus |
| Identitas di Android | `uid 2000 (shell)` | `uid 2000 (shell)` — **identik** |
| Perintah kendali | `uiautomator`, `input`, `screencap` via `rish -c` | perintah yang sama persis via `adb shell` |
| Kelemahan khas | Mati bila HP restart (Shizuku perlu aktivasi ulang) | Sesi ADB putus = kendali hilang; pasangan perangkat bisa dicabut sistem |

**Kesimpulan:** berganti AI tidak mengubah apa pun di sisi HP. Yang berubah hanya
inventaris pintu di sisi pengendali: agent yang tidak punya kunci SSH akan (terpaksa)
memakai ADB, dan sebaliknya. Bila dua agent perlu berbagi satu HP, cara terbersih adalah
memberi keduanya akses ke pintu yang sama — mis. masing-masing memasang kunci SSH-nya
ke Termux — daripada menumpuk pintu.

## B. Skrip di perangkat: AutoX.js / Auto.js ("autojax")

Pendekatan berbeda secara arsitektur: tidak ada shell dan tidak ada pengendali eksternal.
Sebuah aplikasi Android (AutoX.js/Auto.js) menjalankan skrip JavaScript **di dalam HP**
dengan kuasa **Layanan Aksesibilitas**:

- Skrip membaca pohon UI lewat API aksesibilitas dan mengetuk lewat `click()`, `swipe()`.
- Cocok untuk alur pendek, berulang, dan tampilannya stabil (auto-klik sederhana).
- Rapuh untuk alur panjang yang reaktif: tidak ada "otak" yang menilai konteks —
  skrip berjalan sesuai urutan yang ditulis, dan perubahan tampilan kecil bisa
  menggagalkannya diam-diam.
- Dalam operasi yang didokumentasikan repo ini, pendekatan ini **tidak dipakai**:
  begitu shell tersedia, loop agent eksternal lebih fleksibel dan bisa diawasi.

## C. Manusia ikut mengemudi: scrcpy

Dari komputer, `scrcpy` memantulkan layar HP dan meneruskan klik/tik manusia.
Berguna sebagai **mode takeover**: agent menyiapkan keadaan, manusia menyelesaikan
satu langkah sensitif (mis. verifikasi), lalu agent melanjutkan. Melengkapi, bukan
menggantikan, jalur shell.

## D. Tanpa HP fisik

| Alternatif | Miripnya | Bedanya |
|---|---|---|
| Emulator Android (AVD) di komputer | ADB penuh, `input`/`uiautomator` sama | Bukan perangkat asli: sebagian aplikasi menolak emulator; tidak ada sesi "asli" pengguna |
| Cloud phone / device farm | Perangkat asli jarak jauh | Biaya, latensi, dan ketergantungan pihak ketiga |
| Browser web di VM | Alur mirip (baca DOM → klik) | Beda dunia: anti-bot web (CAPTCHA) — justru yang dihindari jalur ini |

## Matriks keputusan singkat

- Punya kunci SSH Termux + Shizuku hidup → **jalur utama** (paling stabil dari VM).
- Agent di mesin tanpa kunci SSH → **ADB** (USB bila bisa, Wi-Fi bila terpaksa).
- Tugasnya manusiawi sesekali dan perlu diawasi mata → tambahkan **scrcpy**.
- Alur sangat pendek & berulang di perangkat yang sama → AutoX.js bisa dipertimbangkan.
