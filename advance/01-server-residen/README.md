# 01 — Server Residen di HP (Jalan 1)

> Status: **prototipe** — belum diuji di perangkat. Bagian dari folder `advance/`
> (lihat [../README.md](../README.md)).

## Masalahnya

Eksekutor lokal (bab 09) memanggil `uiautomator` dari nol di setiap langkah:
proses bangun → baca layar → mati. Biaya bangunnya 2–8 detik per panggilan dan
itulah sisa latensi terbesar di dalam HP sekarang.

## Idenya

Jangan bangunkan pembaca layar berulang kali — **biarkan ia tinggal**. Proyek
openatx/uiautomator2 menyediakan server berbasis UiAutomator yang menetap di
perangkat dan melayani perintah lewat HTTP (JSON-RPC, port 9008): dump, klik,
geser, teks. Langkah yang tadinya detik menjadi ratusan milidetik.

## Isi folder ini

| Berkas | Isi |
|---|---|
| `mulai-server.sh` | Dijalankan di Termux: mengambil jar server, menaruhnya di `/data/local/tmp` lewat rish, menjalankannya dengan `app_process` sebagai uid shell, lalu memeriksa kesehatannya |
| `server-hp.py` | Klien tipis dari mesin agent: `ping`, `dump`, `ketuk`, `tunggu-teks` — antarmuka yang sama semangatnya dengan `hp.sh`, tapi lewat server residen |

## Cara mencoba (nanti, saat sesi uji)

```bash
# 1) di Termux (HP): unduh jar dari rilis openatx/android-uiautomator-server,
#    lalu:
JAR_URL=<url-jar-server> bash mulai-server.sh
# 2) di mesin agent:
python3 server-hp.py ping
python3 server-hp.py dump | head
python3 server-hp.py ketuk 540 1200
```

## Yang harus dibuktikan saat uji

1. Server bisa dinyalakan murni lewat rish (tanpa ADB) dan bertahan > 1 jam.
2. Latensi dump terukur: target < 500 ms (bandingkan 2–8 dtk cara lama).
3. Konsumsi baterai/RAM selama menetap tidak mengganggu HP pekerja.
4. Rencana integrasi: eksekutor mendapat mode `MESIN=server` yang memakai klien
   ini untuk TUNGGU_TEKS/KETUK_TEKS, dengan jatuh-balik otomatis ke cara lama
   bila server tidak menjawab.
