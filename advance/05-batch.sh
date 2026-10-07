#!/usr/bin/env bash
# 05-batch.sh — jalankan BANYAK berkas .job dalam SATU sesi bangun HP.
# Status: PROTOTIPE (folder advance/) — berjalan di Termux, memakai eksekutor.sh.
#
# Kenapa: membangunkan HP, membuka kunci sesi, dan memastikan Shizuku hidup itu
# ongkos tetap. Membayar ongkos itu sekali untuk banyak misi jauh lebih hemat
# daripada sekali per misi — dan lebih sopan ke baterai.
#
# Pakai:
#   05-batch.sh <folder-isi-.job>     jalankan semua .job terurut dalam folder itu
#   05-batch.sh m1.job m2.job ...     atau sebutkan berkasnya satu-satu
#
# Perilaku: layar dibangunkan di awal dan dijaga tetap bangun di antara misi
# (wake lock rish selama batch), tiap misi dijalankan eksekutor seperti biasa
# (log & fail-fast per misi tetap berlaku), di akhir dicetak ringkasan batch:
# berapa beres, berapa gagal, total waktu.

set -u
RID="${RISH_APPLICATION_ID:-com.termux}"
RISH_BIN="${RISH_BIN:-$HOME/rish}"
EKSEKUTOR="${EKSEKUTOR:-$HOME/eksekutor.sh}"
BASE="${MUSE_DROID_HOME:-$HOME/muse-droid}"

rish() { RISH_APPLICATION_ID="$RID" "$RISH_BIN" -c "$1" 2>/dev/null < /dev/null; }

daftar=()
if [ -d "${1:-}" ]; then
  for f in "$1"/*.job; do [ -e "$f" ] && daftar+=("$f"); done
else
  daftar=("$@")
fi
[ "${#daftar[@]}" -gt 0 ] || { echo "tidak ada .job untuk dijalankan" >&2; exit 2; }

echo "=== BATCH: ${#daftar[@]} misi, satu sesi bangun ==="
rish 'input keyevent 224' >/dev/null                     # bangunkan layar
rish 'svc power stayon true' >/dev/null                  # jaga layar selama batch
t0=$(date +%s); beres=0; gagal=0
for job in "${daftar[@]}"; do
  echo "--- $job"
  if bash "$EKSEKUTOR" "$job"; then beres=$((beres+1)); else gagal=$((gagal+1)); fi
done
rish 'svc power stayon false' >/dev/null                 # lepaskan jaga layar
t1=$(date +%s)
mkdir -p "$BASE/log"
echo "[$(date '+%F %T')] batch: ${#daftar[@]} misi | beres $beres | gagal $gagal | $((t1-t0)) dtk" \
  | tee -a "$BASE/log/batch.log"
[ "$gagal" -eq 0 ]
