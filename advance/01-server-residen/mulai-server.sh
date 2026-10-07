#!/usr/bin/env bash
# mulai-server.sh — nyalakan server UiAutomator residen (Jalan 1) dari Termux.
# Status: PROTOTIPE (folder advance/) — belum diuji di perangkat.
#
# Kebutuhan:
#   - rish/Shizuku aktif (seperti biasa)
#   - JAR_URL: alamat jar server dari rilis openatx/android-uiautomator-server
#     (berkas app-uiautomator-server / android-uiautomator-server.jar).
#
# Pakai:  JAR_URL=https://... bash mulai-server.sh
#         bash mulai-server.sh --berhenti

set -u
RID="${RISH_APPLICATION_ID:-com.termux}"
RISH_BIN="${RISH_BIN:-$HOME/rish}"
TUJUAN="/data/local/tmp/md-server.jar"
PORT="${MD_SERVER_PORT:-9008}"

rish() { RISH_APPLICATION_ID="$RID" "$RISH_BIN" -c "$1" 2>/dev/null < /dev/null; }

if [ "${1:-}" = "--berhenti" ]; then
  rish 'pkill -f md-server.jar; echo dimatikan'
  exit 0
fi

[ -n "${JAR_URL:-}" ] || { echo "JAR_URL belum diisi — lihat README.md folder ini." >&2; exit 2; }

MAIN_CLASS="${MD_MAIN_CLASS:-com.github.uiautomator.Main}"
if [ -f "$JAR_URL" ]; then
  echo "1/4 memakai berkas lokal: $JAR_URL"
  cp "$JAR_URL" ${TMPDIR:-/tmp}/md-server.jar
else
  echo "1/4 mengunduh jar server..."
  curl -L -o ${TMPDIR:-/tmp}/md-server.jar "$JAR_URL" || { echo "unduh gagal" >&2; exit 1; }
fi

echo "2/4 menaruh jar ke $TUJUAN (lewat jembatan Download)..."
cp ${TMPDIR:-/tmp}/md-server.jar /sdcard/Download/md-server.jar
rish "cp /sdcard/Download/md-server.jar $TUJUAN; chmod 644 $TUJUAN"

echo "3/4 menjalankan server sebagai uid shell (app_process)..."
rish "CLASSPATH=$TUJUAN nohup app_process /system/bin $MAIN_CLASS --port $PORT >/data/local/tmp/md-server.log 2>&1 &"

echo "4/4 memeriksa kesehatan server..."
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s -m 2 "http://127.0.0.1:$PORT/ping" >/dev/null 2>&1; then
    echo "SERVER HIDUP di port $PORT"
    exit 0
  fi
  sleep 2
done
echo "server tidak menjawab — cek log: rish 'cat /data/local/tmp/md-server.log'" >&2
exit 1
