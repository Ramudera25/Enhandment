# Contoh sesi kendali (tersanitasi)

Transkrip ringkas satu sesi nyata, dengan nama paket/perusahaan diganti placeholder.
Pola perintahnya persis seperti yang dijalankan agent dari VM menuju HP.

```console
# 0) Verifikasi jalur
$ ./examples/cek-koneksi.sh
[1/4] SSH ke Termux...        OK
[2/4] rish / uid shell...     OK — uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),…
[3/4] Layar tidak terkunci... OK
HASIL: jalur kendali SIAP.

# 1) Buka aplikasi lowongan
$ ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'am start -n <paket-lowongan>/<aktivitas>'"

# 2) Baca layar: daftar lowongan
$ ssh termux-hp "RISH_APPLICATION_ID=com.termux ./rish -c 'uiautomator dump /sdcard/d.xml; cat /sdcard/d.xml'"
#    → agent menemukan node teks "<Posisi Target>" dengan bounds="[40,820][1040,900]"
#    → titik ketuk = tengah bounds = (540, 860)

# 3) Ketuk lowongan, verifikasi pindah ke halaman detail
$ ssh termux-hp "… ./rish -c 'input tap 540 860'"
$ ssh termux-hp "… ./rish -c 'uiautomator dump /sdcard/d.xml; cat /sdcard/d.xml'"
#    → terbaca tombol "Lamar" / "Chat" dan deskripsi lowongan

# 4) Masuk percakapan, kirim surat lamaran sebagai teks
$ ssh termux-hp "… ./rish -c 'input tap <x-chat> <y-chat>'"
$ ssh termux-hp "… ./rish -c 'input tap <x-kolom-teks> <y-kolom-teks>'"
$ ssh termux-hp "… ./rish -c 'input text \"<isi surat lamaran>\"'"
$ ssh termux-hp "… ./rish -c 'input tap <x-kirim> <y-kirim>'"

# 5) Lampirkan CV lewat menu lampiran aplikasi, lalu verifikasi visual
$ ssh termux-hp "… ./rish -c 'screencap -p /sdcard/bukti.png'"
#    → pesan + lampiran terlihat terkirim di percakapan

# 6) Agent mencatat hasil ke log: TERKIRIM (tanggal, jam, posisi, perusahaan, bukti)
```

Catatan pola:

- Setiap `input` selalu diikuti `uiautomator dump` — tidak ada aksi buta berurutan.
- Koordinat tidak pernah ditebak dari ingatan; selalu dihitung dari `bounds` dump terakhir.
- Sesi selesai tanpa menyentuh layar sama sekali dari sisi manusia.
