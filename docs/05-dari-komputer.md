# 05 — Dari Komputer: Apakah Sama?

**Jawaban singkat: ya, sama — bahkan pintunya lebih mudah.**

Dari komputer (Windows/macOS/Linux), pengendali tidak perlu Shizuku maupun Termux
sama sekali, karena ADB lewat **USB** langsung memberi `uid shell` yang sama:

```
komputer ──USB──► adb shell ──► uid 2000 (shell)
                                ├─ uiautomator dump   (melihat)
                                ├─ input tap/text     (menyentuh)
                                └─ screencap          (verifikasi)
```

Loop kerjanya identik dengan `03-workflow.md`; yang berganti hanya awalan perintahnya:

| Aksi | Jalur VM (rish) | Jalur komputer (adb) |
|---|---|---|
| Baca layar | `rish -c 'uiautomator dump …'` | `adb shell uiautomator dump …` |
| Ketuk | `rish -c 'input tap x y'` | `adb shell input tap x y` |
| Ketik | `rish -c 'input text "…"'` | `adb shell input text "…"` |
| Buka aplikasi | `rish -c 'am start -n …'` | `adb shell am start -n …` |
| Bukti layar | `rish -c 'screencap -p …'` | `adb exec-out screencap -p > file.png` |

## Perbedaan praktis komputer vs VM

| Aspek | Komputer (USB) | VM/server (SSH + Shizuku) |
|---|---|---|
| Kedekatan fisik | HP tertambat kabel ke komputer | HP bebas di mana pun sejangkauan jaringan |
| Stabilitas sesi | Sangat stabil; ADB USB jarang putus | Bergantung jaringan + proses Termux/Shizuku tetap hidup |
| Aktivasi awal | Aktifkan "USB debugging" sekali + setujui sidik jari komputer di HP | Pasang kunci SSH + aktifkan Shizuku sekali |
| Restart HP | ADB USB pulih begitu kabel tersambung & debugging disetujui | Shizuku perlu aktivasi ulang manual dari HP |
| Mirror visual | Mudah: `scrcpy` untuk menonton/mengambil alih | Tidak ada mirror bawaan; andalkan dump + screencap |
| Cocok untuk | Pengembangan, uji alur, operasi yang diawasi manusia | Operasi otonom terjadwal (agent di server bekerja saat manusia tidak di depan komputer) |

## Catatan

- ADB via **Wi-Fi** dari komputer pun bisa (Wireless Debugging), tetapi mewarisi
  kerapuhan sesi yang sama seperti pada kasus agent VM lain: koneksi mudah putus dan
  Wireless Debugging harus tetap menyala. USB adalah pintu komputer yang paling dapat
  diandalkan.
- Identitas dan kuasa akhirnya **persis sama**: `uid 2000 (shell)`. "Komputer vs VM"
  bukan perbedaan kemampuan — hanya perbedaan logistik: siapa yang dekat dengan HP,
  dan pintu mana yang paling jarang tertutup.
