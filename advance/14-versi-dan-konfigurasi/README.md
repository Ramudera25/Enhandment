# 14 — Versi & Gambaran Konfigurasi

Folder administrasi rilis: bagaimana proyek ini diberi nomor versi, dan
gambaran konfigurasi produksi (HP + pengendali) yang membuat workflow-nya
jalan — supaya orang lain bisa memahami, meniru, dan meningkatkannya.

- `VERSI.md` — skema penomoran V\<Mayor\>.\<Minor\>, riwayat V1.0 → V3.0
  beserta jangkar commit/tag dan bukti ujinya, calon versi berikutnya,
  dan checklist menaikkan versi.
- `KONFIGURASI-HP.md` — peta alur tiga kaki kendali, tata letak berkas
  di HP, contoh konfigurasi SSH tersanitasi (ControlMaster), kait penjaga
  di starter server, dan checklist urutan pemulihan.

Aturan isi folder ini: teknis dan lengkap untuk yang ingin meniru, tapi
setiap dokumen dibuka dengan ringkasan bahasa awam. Dan satu garis yang
tidak pernah dilanggar: **tidak ada rahasia di sini** — nilai sensitif
selalu *placeholder*.
