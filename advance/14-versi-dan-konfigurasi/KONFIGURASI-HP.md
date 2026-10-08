# KONFIGURASI-HP — Gambaran Workflow & Konfigurasi Produksi

> **Bahasa awam:** ini peta dapurnya — berkas apa saja yang hidup di HP
> dan di komputer pengendali, siapa mengerjakan apa, dan urutan menyalakan
> semuanya bila ada yang mati. Tujuannya agar workflow ini bisa dipahami,
> ditiru, dan diperbaiki orang lain. **Tidak ada satu pun rahasia di
> dokumen ini** — kata sandi, API key, dan kunci pribadi memang sengaja
> tidak pernah ditulis di repo; nilai yang bersifat contoh diganti
> *placeholder*.

## 1. Peta alur (siapa bicara ke siapa)

```
Komputer pengendali (agen AI)
   │  SSH (satu koneksi dibuka sekali, dipakai berulang — ControlMaster)
   ▼
Termux di HP ──► tiga "kaki kendali":
   ├─ Kaki 1: server residen uiautomator2 — http://127.0.0.1:9008
   │          (dump UI, ketuk, geser; paling cepat, paling sering dipakai)
   ├─ Kaki 2: rish → Shizuku — shell uid=2000
   │          (penyalur hak: start aplikasi, screencap, hidupkan kaki 1)
   └─ Kaki 3: aplikasi pendamping (UserService Shizuku) — socket :19101
              (jalur cadangan sekelas kaki 1)
   ▲
   └─ penjaga kaki (loop 60 dtk): mengawasi ketiganya, menghidupkan
      kaki 1 bila mati, dan memberi tahu pemilik bila Shizuku mati
      (hanya pemilik yang bisa menyalakan Shizuku, dari aplikasinya)
```

## 2. Tata letak di HP (Termux, `~` = home Termux)

| Berkas/folder | Isi & guna |
|---|---|
| `rish` + `rish_shizuku.dex` | Jembatan ke Shizuku. Wajib `export RISH_APPLICATION_ID=com.termux` sebelum memanggilnya. |
| `u2.jar` | Server residen UiAutomator (kaki 1), dijalankan lewat `app_process` sebagai uid shell. |
| `mulai-server.sh` | Starter kaki 1 (+ memastikan penjaga kaki ikut hidup). Salinan resmi: `../01-server-residen/mulai-server.sh`. Berhenti: `bash ~/mulai-server.sh --berhenti`. |
| `penjaga-kaki.sh` | Penjaga residen (advance/13). Keadaan & log: `~/.penjaga-kaki/status`, `~/.penjaga-kaki/penjaga.log`. |
| `probe-u2.py`, `list-teks.py`, `probe-glints.py` | Alat periksa cepat: kesehatan server + daftar teks layar tanpa screenshot. |
| `~/muse-droid/misi-cepat.py` | Runner misi residen (advance/11) — salinan kerja toolkit di HP. |
| `~/muse-droid/navigasi-glints/` | Generator + template misi navigasi (advance/12). |
| `~/muse-droid/misi/` | Berkas `.job` hasil generator & misi yang dijalankan. |
| `~/muse-droid/bukti/` | Screenshot bukti dari eksekusi misi. |
| `~/muse-droid/antrean/`, `selesai/`, `gagal/`, `log/` | Folder keadaan misi: menunggu, beres, gagal, catatan. |
| `/sdcard/Download/lamaran-<tanggal>/` | Berkas lamaran per hari: CV hasil sesuaikan, surat, teks pesan chat. Pemilih file Android mengingat folder ini — penggantian CV jadi cepat. |

Di komputer pengendali, salinan sumber toolkit adalah repo ini; salinan
kerja operasional (antrean, log lamaran, cron) hidup di workspace goal
pemilik — bukan bagian repo publik ini.

## 3. Konfigurasi SSH pengendali → HP (contoh tersanitasi)

```sshconfig
Host termux-hp
  HostName <IP-TAILSCALE-HP>          # ganti: IP Tailscale HP tujuan
  Port 8022                            # sshd Termux
  User <user-termux>                   # ganti: user Termux, mis. u0_aXXX
  IdentityFile ~/.ssh/<kunci-khusus-hp>
  ProxyCommand <perintah-proxy>        # produksi kami: socat PROXY via proxy Tailscale
  ControlMaster auto
  ControlPath ~/.ssh/mux-%r@%h:%p
  ControlPersist 10m
  ServerAliveInterval 15
  ServerAliveCountMax 3
```

Dua pelajaran yang membuat blok ini seperti sekarang:

- **ControlMaster itu wajib untuk kerja jarak jauh yang enak.** Tanpa
  mux, tiap perintah SSH membayar jabat tangan penuh (terukur 4,1 dtk →
  1,5 dtk per panggilan sesudah mux aktif).
- **Flag `-F <lokasi-config>`** dipakai di semua perintah kami
  (`ssh -F ... termux-hp`) karena proses agen di mesin kami berjalan
  dengan home berbeda dari yang dibaca OpenSSH — tanpa flag itu, blok
  `Host termux-hp` terlewat diam-diam dan koneksi nyasar.

## 4. Kait penjaga di starter server

`mulai-server.sh` (salinan di `../01-server-residen/`) memuat blok ini —
setiap server dinyalakan, penjaga kaki dipastikan ikut hidup:

```bash
if [ -f "$HOME/penjaga-kaki.sh" ] && ! pgrep -f "penjaga-kaki[.]sh" >/dev/null 2>&1; then
  nohup "$HOME/penjaga-kaki.sh" >/dev/null 2>&1 &
  echo "penjaga kaki dihidupkan"
fi
```

Berhenti total (server + penjaga): `bash ~/mulai-server.sh --berhenti`
lalu `kill $(cat ~/.penjaga-kaki/penjaga.pid)`.

## 5. Urutan pemulihan bila kaki mati (checklist)

1. Baca `~/.penjaga-kaki/status` — kaki mana yang tercatat mati, sejak kapan.
2. **Shizuku mati** → hanya pemilik: buka aplikasi Shizuku → **Start**.
   (Penjaga sudah mengirim notifikasi begitu kematian terdeteksi.)
3. rish menjawab `uid=2000`? → jalankan `bash ~/mulai-server.sh`
   (kaki 1 hidup; penjaga ikut dipastikan hidup oleh kait §4).
4. Kaki 3 (pendamping) mati → buka aplikasinya sekali dari launcher.
5. Verifikasi papan hijau: `scripts/cek-siap.sh` di repo ini, atau ping
   `curl http://127.0.0.1:9008/ping` harus menjawab `pong`.

## 6. Yang sengaja TIDAK ada di repo

Kredensial apa pun: API key provider AI, kunci klien antar-mesin, kata
sandi akun, kunci pribadi SSH. Prinsip proyek: **rahasia berpindah
mesin-ke-mesin atau lewat brankas aman — tidak pernah lewat dokumen,
chat, atau commit.** Konfigurasi di dokumen ini adalah *struktur &
workflow*; siapa pun yang meniru harus mengisi nilainya sendiri.
