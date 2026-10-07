# _umum — Pelajaran lintas aplikasi (alat & perangkat)

## rish / Shizuku
- Panggilan `rish` pertama setelah lama diam bisa gagal/kosong ("dingin").
  Selalu coba ulang sampai 5x sebelum menyatakan Shizuku mati.
  (Terbukti 7 Okt 2026 pada uji pertama eksekutor.)
- Program yang berjalan di dalam loop pembaca berkas tugas WAJIB menutup
  stdin-nya (`< /dev/null`) — `rish`/`app_process` menelan sisa berkas tugas
  bila tidak. (Bug nyata pertama eksekutor.)
- **Output rish terpotong ±8 KB.** Dump XML besar harus dipindah sebagai berkas
  lewat folder Download (rish menulis, Termux membaca), bukan lewat stdout.
- Menyalin berkas dari uid shell langsung ke folder privat aplikasi lain
  (mis. home Termux) ditolak SELinux — pakai jembatan Download yang sama.

## Perangkat
- Layar terkunci = misi berhenti. Shell tidak bisa (dan tidak boleh) membuka
  kunci aman; atur Smart Lock / HP pekerja khusus bila misi harus otonom.
- Screenshot untuk vision: resolusi asli perangkat uji 1080×2400; grid 6×12
  memberi sel 180×200 — cukup untuk target besar, rapatkan grid untuk target
  kecil.
