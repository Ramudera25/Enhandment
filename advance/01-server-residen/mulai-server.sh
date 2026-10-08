#!/usr/bin/env bash
# mulai-server.sh — nyalakan server UiAutomator residen (Jalan 1) dari Termux.
# Status: TERUJI di perangkat (8 Okt 2026 — lihat ../PENGUJIAN.md Fase 8).
#
# Resep yang TERBUKTI (dari kode sumber uiautomator2 3.7.0, core.py):
# servernya adalah u2.jar dengan kelas utama com.wetest.uia2.Main, dijalankan
# lewat app_process dengan CLASSPATH di environment. Percobaan sebelumnya
# (app-uiautomator.apk sebagai jar + com.github.uiautomator.Main) CRASH
# SIGABRT — APK itu aplikasi pendamping/keeper, bukan servernya.
#
# Kebutuhan:
#   - rish/Shizuku aktif (seperti biasa)
#   - u2.jar: ambil dari wheel pip uiautomator2 (uiautomator2/assets/u2.jar).
#     Taruh di ~/u2.jar di Termux, atau isi JAR_URL dengan alamat unduhnya.
#
# Pakai:  bash mulai-server.sh            # nyalakan + cek kesehatan
#         bash mulai-server.sh --berhenti # matikan

set -u
RID="${RISH_APPLICATION_ID:-com.termux}"
RISH_BIN="${RISH_BIN:-$HOME/rish}"
TUJUAN="/data/local/tmp/u2.jar"
LOG="/data/local/tmp/md-server.log"
PORT="${MD_SERVER_PORT:-9008}"

rish() { RISH_APPLICATION_ID="$RID" "$RISH_BIN" -c "$1" 2>/dev/null < /dev/null; }

if [ "${1:-}" = "--berhenti" ]; then
  rish 'pkill -f "com.wetest.uia2[.]Main"; echo dimatikan'
  exit 0
fi

# penjaga kaki (Enhandment advance/13): pastikan loop penjaga hidup —
# ia yang menghidupkan ulang server ini bila mati dan memberi tahu pemilik
# bila Shizuku mati. Berhenti total: bunuh juga PID di ~/.penjaga-kaki/penjaga.pid.
if [ -f "$HOME/penjaga-kaki.sh" ] && ! pgrep -f "penjaga-kaki[.]sh" >/dev/null 2>&1; then
  nohup "$HOME/penjaga-kaki.sh" >/dev/null 2>&1 &
  echo "penjaga kaki dihidupkan"
fi

# 1/4 siapkan u2.jar di Termux home
if [ -f "${JAR_URL:-}" ]; then
  echo "1/4 memakai berkas lokal: $JAR_URL"; cp "$JAR_URL" "$HOME/u2.jar"
elif [ -n "${JAR_URL:-}" ]; then
  echo "1/4 mengunduh u2.jar..."; curl -L -o "$HOME/u2.jar" "$JAR_URL" || { echo "unduh gagal" >&2; exit 1; }
elif [ -f "$HOME/u2.jar" ]; then
  echo "1/4 u2.jar sudah ada di $HOME"
else
  echo "u2.jar tidak ada — taruh di ~/u2.jar atau isi JAR_URL (lihat README.md)." >&2; exit 2
fi

echo "2/4 menaruh jar ke $TUJUAN (lewat jembatan Download)..."
cp "$HOME/u2.jar" /sdcard/Download/u2.jar
rish "cp /sdcard/Download/u2.jar $TUJUAN; ls -la $TUJUAN" | tail -1

echo "3/4 menjalankan server sebagai uid shell (app_process)..."
rish "CLASSPATH=$TUJUAN nohup app_process / com.wetest.uia2.Main -p $PORT >$LOG 2>&1 &"

echo "4/4 memeriksa kesehatan server (boleh sampai ±60 dtk saat UiAutomation"
echo "    masih terikat sesi dump lama — bersabarlah, jangan diluncurkan dua kali)..."
for i in $(seq 1 30); do
  if [ "$(curl -s -m 2 "http://127.0.0.1:$PORT/ping" 2>/dev/null)" = "pong" ]; then
    echo "SERVER HIDUP di port $PORT (percobaan $i)"
    exit 0
  fi
  sleep 2
done
echo "server tidak menjawab — cek log: rish 'cat $LOG'" >&2
exit 1
