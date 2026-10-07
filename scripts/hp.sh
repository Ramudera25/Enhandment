#!/usr/bin/env bash
# hp.sh — SATU perintah seragam untuk mengendalikan HP Android, apa pun pintunya.
# Inilah yang dipanggil AI agent (lihat docs/07-ai-controller.md).
#
# Pintu dipilih lewat HP_MODE:
#   HP_MODE=rish        → SSH ke Termux + rish/Shizuku   (bawaan; jalur utama)
#   HP_MODE=rish-local  → rish lokal (agent tinggal DI HP itu sendiri)
#   HP_MODE=adb         → adb shell dari komputer/VM ini
#
# Variabel lain:
#   HP_SSH_ALIAS   (bawaan: termux-hp)   alias ~/.ssh/config untuk Termux
#   RISH_APPLICATION_ID (bawaan: com.termux)
#
# Pakai:
#   hp.sh id | dump | shot <file.png> | tap <x> <y> | swipe <x1> <y1> <x2> <y2> [ms]
#   hp.sh text "<teks>" | key <home|back|enter|wakeup|...> | open <paket>/<aktivitas>

set -u
MODE="${HP_MODE:-rish}"
ALIAS="${HP_SSH_ALIAS:-termux-hp}"
RID="${RISH_APPLICATION_ID:-com.termux}"

run_remote() {  # jalankan perintah sebagai uid shell lewat pintu terpilih
  case "$MODE" in
    rish)       ssh -o ConnectTimeout=20 "$ALIAS" "RISH_APPLICATION_ID=$RID ./rish -c '$1'" ;;
    rish-local) RISH_APPLICATION_ID="$RID" "$HOME/rish" -c "$1" ;;
    adb)        adb shell "$1" ;;
    *) echo "HP_MODE tidak dikenal: $MODE (pilih rish | rish-local | adb)" >&2; exit 2 ;;
  esac
}

cmd="${1:-}"; shift || true
case "$cmd" in
  id)   run_remote 'id' ;;
  dump) run_remote 'uiautomator dump /sdcard/window_dump.xml >/dev/null; cat /sdcard/window_dump.xml' ;;
  shot) run_remote "screencap -p /sdcard/hp-shot.png"
        case "$MODE" in
          rish)       scp -q "$ALIAS":/sdcard/hp-shot.png "${1:-hp-shot.png}" ;;
          rish-local) cp /sdcard/hp-shot.png "${1:-hp-shot.png}" ;;
          adb)        adb exec-out screencap -p > "${1:-hp-shot.png}" ;;
        esac
        echo "tersimpan: ${1:-hp-shot.png}" ;;
  tap)  run_remote "input tap $1 $2" ;;
  swipe) run_remote "input swipe $1 $2 $3 $4 ${5:-300}" ;;
  text) run_remote "input text \"$1\"" ;;
  key)  case "$1" in
          home) k=3 ;; back) k=4 ;; enter) k=66 ;; wakeup) k=224 ;; menu) k=82 ;;
          *) k="$1" ;;
        esac
        run_remote "input keyevent $k" ;;
  open) run_remote "am start -n $1" ;;
  *) echo "Perintah: id | dump | shot <file> | tap <x> <y> | swipe <x1> <y1> <x2> <y2> [ms] | text \"<teks>\" | key <nama> | open <paket>/<aktivitas>" >&2; exit 2 ;;
esac
