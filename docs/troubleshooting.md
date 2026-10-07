# Troubleshooting — Pohon Keputusan Saat Macet

> 📦 **Bahasa bayi:** HP tidak bergerak? Jangan panik dan jangan mengacak-acak.
> Ikuti pohon ini dari atas, jawab ya/tidak, dan kamu akan tiba di obatnya.
> Hampir semua kemacetan di dunia ini disebabkan empat syarat yang salah satunya mati.

## Pohon utama

```
                    HP TIDAK BISA DIKENDALIKAN
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     Kamu pakai JALUR A              Kamu pakai JALUR B/C
     (SSH + Termux + rish)           (ADB dari komputer)
              │                               │
   ssh termux-hp tersambung?         adb devices menampilkan HP?
      │              │                  │                 │
     TIDAK           YA                TIDAK               YA
      │              │                  │                 │
      ▼              ▼                  ▼                 ▼
  [POHON A1]    rish menjawab      kabel/USB debug/    adb shell id
                uid=2000?          izin dialog?        uid=2000?
                  │      │          perbaiki itu        │        │
                 TIDAK    YA        (Tutorial 04/05)    TIDAK      YA
                  │      │                               │        │
                  ▼      ▼                               ▼        ▼
             [POHON A2]  layar bisa              koneksi ADB   masalahnya
                         dibaca (dump)?          nirkabel putus:  bukan pintu —
                           │        │            sambung ulang   lanjut ke
                          TIDAK      YA            (Tutorial 02/07) [POHON B]
                           │        │
                           ▼        ▼
                      layar       berarti kendali
                      terkunci?   SEBENARNYA HIDUP:
                      buka kunci  masalah di aplikasinya
                      HP-nya      → [POHON B]
```

### POHON A1 — SSH tidak tersambung

```
ssh gagal. Err-nya apa?
├─ "Connection refused"      → sshd mati. Di Termux: jalankan `sshd`.
├─ "Permission denied"       → kunci belum cocok. Cek authorized_keys + chmod 600 (Tutorial 01).
├─ Timeout / reset           → jaringan. Tailscale di HP hidup? Satu jaringan?
│                              Di VM berproxy: cek ProxyCommand (Tutorial 02).
└─ "Could not resolve"       → alamat salah. Cek `tailscale status`, perbaiki HostName.
```

### POHON A2 — `rish` tidak memberi uid=2000

```
rish bermasalah. Pesannya apa?
├─ "RISH_APPLICATION_ID is not set" → teruskan variabelnya:
│     RISH_APPLICATION_ID=com.termux ./rish -c 'id'
├─ error binder / tidak merespons   → Shizuku mati (biasanya habis restart HP).
│     Buka Shizuku → Start (Tutorial 03, Langkah 2).
└─ uid yang keluar BUKAN 2000       → file rish basi. Ekspor ulang rish +
      rish_shizuku.dex dari aplikasi Shizuku (Tutorial 03, Langkah 3).
```

### POHON B — Pintu hidup, tapi tugas gagal

```
Gejalanya apa?
├─ Dump membaca layar kunci        → HP terkunci. Buka kuncinya; agent tidak menebak PIN.
├─ Dump kosong / aplikasi berbeda  → aplikasi pindah layar sendiri (dialog/update).
│                                    Baca dump terbaru, jangan pakai koordinat lama.
├─ Ketukan tidak berefek           → koordinat dari dump basi, atau UI masih loading.
│                                    Dump ulang, beri jeda, hitung ulang bounds.
├─ Aplikasi menutup sendiri        → crash / dibunuh penghemat baterai.
│                                    Buka ulang via am start; kecualikan dari hemat baterai.
└─ Muncul OTP / CAPTCHA / pairing  → wilayah manusia. Berhenti & lapor — memang begitu aturannya.
```

## Tabel cepat: gejala → penyebab → obat

| Gejala | Penyebab tersering | Obat |
|---|---|---|
| Semua koneksi mati mendadak | HP restart / Termux terbunuh | Buka Termux, `sshd`, Start Shizuku, `termux-wake-lock` |
| Kemarin bisa, hari ini tidak | Salah satu dari 4 syarat mati semalam | Jalankan `examples/cek-koneksi.sh`, perbaiki yang merah |
| `adb devices` kosong (nirkabel) | Wireless Debugging mati / ganti Wi-Fi | Pairing/connect ulang (Tutorial 04) |
| `adb` status `unauthorized` | Dialog izin belum disetujui | Colok ulang, setujui di layar HP |
| Ketuk meleset terus | Memakai koordinat dari dump lama | Selalu `hp.sh dump` tepat sebelum `hp.sh tap` |
| Teks yang diketik berantakan | Karakter khusus lolos dari `input text` | Pecah teks per baris; hindari simbol langka; verifikasi via dump |
| Agent berhenti sendiri di tengah | Kondisi berhenti tercapai (kunci/OTP/3× gagal) | Itu fitur, bukan bug — baca laporannya |
| Lambat sekali | Sifat loop baca–pikir–gerak–cek | Normal. Jalankan saat HP menganggur/di-charge saja |

## Masih buntu?

Kumpulkan tiga hal ini sebelum bertanya ke siapa pun (atau ke AI lain):

1. Output `examples/cek-koneksi.sh` (Jalur A) atau `adb devices` + `adb shell id` (Jalur B/C).
2. Pesan error **persis** seperti tampil — jangan diterjemahkan.
3. Langkah terakhir yang berhasil sebelum macet.

Dengan tiga itu, hampir semua masalah selesai dalam satu kali tanya.
