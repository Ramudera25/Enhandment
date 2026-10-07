# 08 — Satu Misi, Dibedah dari Nol sampai Beres

> 📦 **Bahasa bayi:** Anggap kamu mengintip dari balik bahu sopir selama satu tugas
> penuh. Kamu akan membaca apa yang ia lihat, apa yang ia pikirkan, tombol apa yang
> ia tekan, dan apa yang ia lakukan saat jalan buntu. Satu cerita utuh — setelah ini,
> seluruh repo akan terasa masuk akal.

**Misinya:** mengirim **satu lamaran kerja** lewat aplikasi lowongan di HP —
membuka lowongan, masuk ke chat HRD, mengirim surat lamaran, melampirkan CV, dan
memastikan terkirim. (Kisah nyata, nama perusahaan diganti `<Perusahaan>`.)

## Peta misinya dulu

```
 [MULAI]
    │
    ▼
 ① CEK JALUR ──── gagal ──► perbaiki syaratnya dulu (Tutorial 00–03)
    │ lolos
    ▼
 ② BUKA APLIKASI ──► ③ BACA LAYAR ──► ④ KETUK LOWONGAN
                                            │
    ┌───────────────────────────────────────┘
    ▼
 ⑤ BACA DETAIL ──► ⑥ MASUK CHAT ──► ⑦ KETIK SURAT ──► ⑧ LAMPIRKAN CV
                                                              │
    ┌─────────────────────────────────────────────────────────┘
    ▼
 ⑨ CEK BUKTI TERKIRIM ──── tidak ada ──► ulangi ⑦–⑧ (maks 3×) ──► tetap gagal ──► 🛑 LAPOR
    │ ada
    ▼
 ⑩ CATAT HASIL ──► [BERES 🎉]
```

## Langkah demi langkah

### ① Cek jalur (30 detik)

Agent menjalankan `examples/cek-koneksi.sh`. Empat syarat hijau: SSH tersambung,
`rish` menjawab `uid=2000(shell)`, layar tidak terkunci, aplikasi terpasang.

> 🧠 **Isi kepala agent:** *"Sebelum meminta apa pun ke HP, aku pastikan dulu
> pintunya ada, satpamnya bertugas, dan rumahnya tidak dikunci. Empat-empatnya
> hijau. Lanjut."*

### ② Buka aplikasi (teleport, bukan mengetuk ikon)

```bash
hp.sh open <paket-lowongan>/<aktivitas-utama>
```

> 🧠 *"Aku bisa saja mencari ikon di layar utama dan mengetuknya — tapi ikon bisa
> berpindah. `am start` itu teleport: aku selalu tiba di ruangan yang sama."*

### ③ Baca layar — daftar lowongan

```bash
hp.sh dump
```

Layar menjawab dengan daftar isi (XML). Agent memindai teks-teksnya mencari
nama posisi target.

> 🧠 *"Layar menampilkan 6 lowongan. Baris kedua: 'Staff Administrasi — <Perusahaan>'.
> Alamat kotaknya `bounds="[40,820][1040,900]"`. Aku ketuk tengahnya: x=540, y=860.
> Bukan menebak — menghitung."*

### ④ Ketuk lowongan → ⑤ Baca detail

```bash
hp.sh tap 540 860
hp.sh dump
```

> 🧠 *"Sudah di halaman detail. Gajinya cocok, lokasinya cocok, ada tombol 'Chat'
> di bawah. Aku tidak langsung mengetuk — aku baca dulu seluruh halaman, siapa tahu
> lowongan ini meminta syarat yang tidak kupenuhi. Aman. Lanjut."*

**Kemungkinan cabang gagal di sini:** lowongan menampilkan "tidak lagi menerima
lamaran" → agent mencatat *listing tutup* dan **berhenti dengan rapi**, bukan memaksa.
(Di kisah nyata, 4 dari 7 lowongan gugur persis di langkah ini — dan catatan rapi
itulah yang membuat manusia tidak membuang waktu mengejarnya lagi.)

### ⑥ Masuk chat HRD

```bash
hp.sh tap <x-tombol-chat> <y-tombol-chat>
hp.sh dump
```

> 🧠 *"Ruang chat terbuka. Ada kolom teks di bawah dan tombol lampiran (klip kertas).
> Urutan yang aman: tulis surat dulu, periksa, baru kirim — lalu lampirkan CV."*

### ⑦ Ketik surat lamaran

```bash
hp.sh tap <x-kolom-teks> <y-kolom-teks>
hp.sh text "<isi surat lamaran>"
hp.sh dump          # verifikasi teksnya benar sebelum mengirim
hp.sh tap <x-kirim> <y-kirim>
```

> 🧠 *"Aku mengetik isi surat, lalu membaca ulang layarnya. Namaku benar, nama
> perusahaannya benar, tidak ada potongan teks yang hilang. Baru aku tekan kirim."*

### ⑧ Lampirkan CV

Agent mengetuk ikon lampiran, memilih berkas CV dari penyimpanan, menunggu unggahan
selesai (terbaca dari dump: nama berkas muncul di ruang chat).

> 🧠 *"Mengunggah itu tidak instan. Aku menunggu sampai nama berkasnya benar-benar
> tampak di layar. Menganggap 'pasti berhasil' adalah cara tercepat membuat
> lamaran tanpa CV."*

### ⑨ Cek bukti terkirim

```bash
hp.sh dump
hp.sh shot bukti.png
```

Bukti yang dicari: pesan + lampiran tampak di riwayat chat sebagai pengirim.

### ⑩ Catat hasil

```
2026-.. ..:.. | <Posisi> di <Perusahaan> via aplikasi | TERKIRIM | bukti: bukti.png
```

> 🧠 *"Selesai bukan saat aku menekan tombol — selesai saat buktinya terlihat dan
> tercatat. Sekarang misinya benar-benar beres."*

## Cabang-cabang gagal yang sudah disiapkan

| Terjadi di | Gejala | Reaksi agent |
|---|---|---|
| ① | `cek-koneksi` merah | Berhenti; lapor syarat mana yang mati (lihat [troubleshooting](troubleshooting.md)) |
| ③ | Lowongan tidak ditemukan di daftar | Gulir maks 3 layar; tetap tidak ada → catat "tidak ditemukan", berhenti |
| ⑤ | "Tidak lagi menerima lamaran" | Catat *listing tutup*, berhenti rapi |
| ⑥–⑧ | Dialog izin / papan ketik menutupi tombol | Tangani eksplisit (tutup/gulir), jangan mengetuk membabi buta |
| Kapan pun | Layar terkunci di tengah misi | 🛑 Berhenti total, lapor manusia. Tidak menebak PIN. |
| Kapan pun | 3× gagal di langkah yang sama | 🛑 Berhenti, lapor dengan tangkapan layar terakhir |

## Berapa lama semua ini?

Di kisah nyata: tiga lamaran serupa selesai dalam ±35 menit — termasuk satu yang
sempat tertahan dan harus diulang sebagian. Bandingkan dengan jalur web di hari
yang sama: **nol** lamaran dalam 8 jam karena terblokir. Tempo agent memang belum
secepat jempol manusia, tapi ia tidak lelah, tidak mengantuk, dan bekerja persis
saat HP-nya sedang tidak dipakai siapa-siapa.
