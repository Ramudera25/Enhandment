#!/usr/bin/env bash
# mata.sh — indra tambahan muse-droid, berjalan DI DALAM Termux (di HP).
# Melengkapi eksekutor.sh: foto layar, mata gerak (foto berkala), telinga (notifikasi).
#
# Pakai:
#   mata.sh foto <nama.png>              screenshot -> ~/muse-droid/bukti/
#   mata.sh jaga <interval> <jumlah>     foto berkala -> ~/muse-droid/bukti/gerak/
#   mata.sh notif                        ringkasan notifikasi aktif (nama aplikasi & jumlah saja)
#
# Kebutuhan: rish/Shizuku aktif (sama seperti hp.sh & eksekutor.sh).
# Privasi: 'notif' SENGAJA tidak membaca isi pesan — hanya paket & hitungan.

set -u
RID="${RISH_APPLICATION_ID:-com.termux}"
RISH_BIN="${RISH_BIN:-$HOME/rish}"
BASE="${MUSE_DROID_HOME:-$HOME/muse-droid}"

rish() { RISH_APPLICATION_ID="$RID" "$RISH_BIN" -c "$1" 2>/dev/null < /dev/null; }

satu_foto() {  # satu_foto <path-tujuan-lokal>
  rish 'screencap -p /sdcard/md-mata.png' >/dev/null
  rish 'cp /sdcard/md-mata.png /sdcard/Download/md-mata.png' >/dev/null 2>&1 || true
  cp "/sdcard/Download/md-mata.png" "$1" 2>/dev/null || cp "/storage/emulated/0/Download/md-mata.png" "$1"
}

case "${1:-}" in
  foto)
    mkdir -p "$BASE/bukti"
    satu_foto "$BASE/bukti/${2:-foto.png}" && echo "tersimpan: $BASE/bukti/${2:-foto.png}" ;;
  jaga)
    interval="${2:-5}"; jumlah="${3:-12}"; dir="$BASE/bukti/gerak"
    mkdir -p "$dir"
    echo "mata gerak: $jumlah foto, interval ${interval}d -> $dir"
    for i in $(seq 1 "$jumlah"); do
      satu_foto "$dir/gerak-$(date '+%H%M%S').png" && echo "  foto $i/$jumlah"
      [ "$i" -lt "$jumlah" ] && sleep "$interval"
    done ;;
  notif)
    echo "notifikasi aktif per aplikasi (nama paket & jumlah saja):"
    rish 'dumpsys notification' \
      | grep -oE 'NotificationRecord\(.*pkg=[a-zA-Z0-9_.]+' \
      | grep -oE 'pkg=[a-zA-Z0-9_.]+' | sort | uniq -c | sort -rn \
      | sed 's/pkg=//' ;;
  *)
    echo "Pakai: mata.sh foto <nama.png> | mata.sh jaga <interval> <jumlah> | mata.sh notif" >&2; exit 2 ;;
esac
