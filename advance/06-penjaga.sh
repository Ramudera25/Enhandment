#!/usr/bin/env bash
# 06-penjaga.sh — watchdog prasyarat muse-droid di HP (sshd + Shizuku).
# Status: PROTOTIPE (folder advance/) — berjalan di Termux.
#
# Kenapa: dua dari tiga kegagalan uji pertama eksekutor akarnya bukan misi,
# melainkan prasyarat yang mati/dingin (rish tidak menjawab, sshd mati setelah
# HP restart). Penjaga ini memeriksa prasyarat berkala, menyalakan yang bisa
# dinyalakan sendiri (sshd), dan MENCATAT yang tidak bisa (Shizuku hanya bisa
# diaktifkan dari HP) supaya agent tidak mengira misinya yang salah.
#
# Pakai:
#   06-penjaga.sh cek        periksa sekali, cetak status, exit != 0 bila ada mati
#   06-penjaga.sh jaga       periksa berkala (bawaan tiap 300 dtk) — untuk tmux/nohup
#
# Catatan: penjaga menulis status terakhir ke ~/muse-droid/log/status-prasyarat.txt
# yang bisa dibaca agent sebelum mengirim misi ("jangan kirim misi ke HP mati").

set -u
RID="${RISH_APPLICATION_ID:-com.termux}"
RISH_BIN="${RISH_BIN:-$HOME/rish}"
BASE="${MUSE_DROID_HOME:-$HOME/muse-droid}"
STATUS="$BASE/log/status-prasyarat.txt"
mkdir -p "$BASE/log"

periksa() {
  local sshd_ok=0 shizuku_ok=0 baris
  pgrep -x sshd >/dev/null 2>&1 && sshd_ok=1
  if [ "$sshd_ok" = 0 ] && command -v sshd >/dev/null 2>&1; then
    sshd >/dev/null 2>&1; sleep 1
    pgrep -x sshd >/dev/null 2>&1 && sshd_ok=1
  fi
  # Shizuku: coba sampai 3x (panggilan pertama setelah dingin memang lambat)
  for i in 1 2 3; do
    if RISH_APPLICATION_ID="$RID" "$RISH_BIN" -c 'id' 2>/dev/null < /dev/null | grep -q 'uid=2000'; then
      shizuku_ok=1; break
    fi
    sleep 2
  done
  baris="[$(date '+%F %T')] sshd=$([ $sshd_ok = 1 ] && echo HIDUP || echo MATI) shizuku=$([ $shizuku_ok = 1 ] && echo HIDUP || echo MATI)"
  echo "$baris" | tee "$STATUS"
  [ "$sshd_ok" = 1 ] && [ "$shizuku_ok" = 1 ]
}

case "${1:-cek}" in
  cek) periksa ;;
  jaga)
    echo "penjaga berjaga (interval ${2:-300} dtk) — Ctrl+C berhenti"
    while true; do periksa || true; sleep "${2:-300}"; done ;;
  *) echo "Pakai: 06-penjaga.sh cek | jaga [interval]" >&2; exit 2 ;;
esac
