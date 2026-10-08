# VERSI — Penomoran & Riwayat Versi Enhandment

> **Bahasa awam:** dokumen ini adalah "nomor seri" perkembangan alat ini.
> Setiap kali kemampuannya naik kelas **dan sudah terbukti jalan di HP
> beneran**, versinya naik: V1 → V2 → V3, dan seterusnya. Pembaca bisa tahu
> sekilas: versi berapa yang sedang dibicarakan, isinya apa, buktinya di
> mana. Versi saat ini: **V3.0**.

## Skema penomoran

Format: **V\<Mayor\>.\<Minor\>** — tag git-nya `v<Mayor>.<Minor>`
(contoh: `v3.0`).

- **Mayor naik** bila ada lompatan cara kerja utama: kaki kendali baru,
  runner baru, model observasi baru, atau paket besar yang mengubah
  workflow operasi sehari-hari.
- **Minor naik** untuk paket kemampuan teruji di dalam arsitektur yang
  sama: template baru, strategi yang diperbaiki dengan angka terukur,
  penjaga baru, dan sejenisnya (contoh pola: V3.1, V3.2).
- **Aturan keras proyek berlaku penuh:** versi hanya naik untuk kemampuan
  yang **teruji di perangkat nyata** dan tercatat di `../PENGUJIAN.md`.
  Desain yang belum dibangun tidak menaikkan versi — ia *calon* versi
  berikutnya.
- Penomoran ini diterapkan **surut** pada 8 Okt 2026 berdasarkan riwayat
  git + jurnal pengujian. Jangkar tiap versi adalah tag git pada commit
  yang menyelesaikan cakupannya, jadi isi persis tiap versi bisa dibuka
  kembali kapan pun (`git checkout v2.0`, dst.).

## Riwayat versi

| Versi | Tanggal | Isi pokok | Jangkar | Bukti uji |
|---|---|---|---|---|
| **V1.0** | 7 Okt 2026 | **Fondasi kendali.** Shizuku/rish memberi shell uid=2000 tanpa root; eksekutor lokal "Jalan 0" + bahasa misi `.job`; dump UI sebagai mata; protokol dua mata & grid (docs/09–10). Misi demo 6 langkah BERES langsung di HP. | commit `ded1950`, tag `v1.0` | Fase 0–7, docs/09–10 |
| **V2.0** | 8 Okt 2026 | **Residen & cepat.** Server residen uiautomator2 di dalam HP (`01`), aplikasi pendamping Shizuku tersambung penuh (`10`), eksekutor generasi baru + runner makro persisten `misi-cepat` (`11`): siklus lihat→ketuk→lihat di perangkat 0,8–1,0 dtk; misi standar 9 langkah 47,8 → 22,3 dtk (2,1×). | commit `37b168d`, tag `v2.0` | Fase 8, 9, 11 |
| **V3.0** | 8 Okt 2026 | **Operasional nyata.** Misi navigasi Glints untuk pekerjaan produksi (`12`: deep link + pencarian, misi pencarian 8 langkah 12,6 dtk), penjaga kaki residen (`13`: server mati dipulihkan ±91 dtk, kematian Shizuku diberitahukan ±1 menit), playbook batch lamaran memakai misi + deep link + observasi dump-first, aturan URL detail wajib di antrean HP. | commit dokumentasi versi ini, tag `v3.0` | Fase 12, 13 |

## Calon versi berikutnya (belum terbit — menunggu bukti)

- **V4.0 (calon):** pohon UI tersimpan lewat layanan aksesibilitas —
  observasi turun ke puluhan milidetik. Desain:
  `../DESAIN-V3-POHON-UI.md`. Syarat: pemilik mengaktifkan layanan
  aksesibilitas sekali di Pengaturan HP + pembangunan + uji terukur.
- **V3.x (calon):** isi teks langsung (set-text) untuk memangkas sisa
  waktu TEMPEL; aplikasi pendamping menjadi *foreground service* agar
  tidak mati saat lama menganggur.

## Catatan penamaan (jangan tertukar)

Di dalam repo ada penomoran lain yang tumbuh lebih dulu secara organik:
"eksekutor v3", "DESAIN-V3", "Jalan 0/1/2". Itu nomor **generasi komponen**
pada masanya, bukan versi rilis. Sejak dokumen ini ada, **satu-satunya
nomor rilis proyek adalah versi di dokumen ini.** Contoh akibatnya:
dokumen `DESAIN-V3` (generasi desain eksekutor) bila dibangun akan terbit
sebagai **proyek V4.0**.

## Checklist menaikkan versi

1. Kemampuan teruji di perangkat nyata; fase baru tercatat di
   `../PENGUJIAN.md` dengan angka terukur.
2. Papan `../README.md` + jurnal `../LOG-PEMBAHARUAN.md` diperbarui.
3. Baris baru di tabel riwayat dokumen ini (isi pokok + jangkar + bukti).
4. Badge versi di `../../README.md` disesuaikan.
5. Commit, lalu tag: `git tag -a vX.Y -m "Vx.Y — <ringkasan>"` pada
   commit itu; push branch beserta tag-nya.
