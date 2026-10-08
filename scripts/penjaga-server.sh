#!/usr/bin/env bash
# penjaga-server.sh — jaga server residen u2 (Fase 8) tetap hidup.
# Jalankan DI HP (Termux):  bash ~/penjaga-server.sh cek|pulihkan
#   cek      -> cetak status (hidup + umur proses / mati)
#   pulihkan -> bila mati, nyalakan ulang lewat mulai-server.sh
set -u

hidup() {
  python3 -c '
import socket, sys
try:
    s = socket.create_connection(("127.0.0.1", 9008), timeout=3)
    s.sendall(b"GET /ping HTTP/1.0\r\n\r\n")
    ok = b"200" in s.recv(64)
    s.close()
    sys.exit(0 if ok else 1)
except Exception:
    sys.exit(1)' 2>/dev/null
}

case "${1:-cek}" in
  cek)
    if hidup; then
      # Umur proses hanya garnish — ambil lewat rish bila bisa (ps Termux
      # tidak melihat proses shell). Penanda hidupnya adalah /ping di atas.
      umur="$(export RISH_APPLICATION_ID=com.termux; ~/rish -c 'ps -A -o PPID,ETIME,NAME' 2>/dev/null | awk '$1==1 && $3=="app_process" {print $2; exit}')"
      echo "server residen HIDUP${umur:+ (umur $umur)}"
    else
      echo "server residen MATI"
      exit 1
    fi ;;
  pulihkan)
    if hidup; then
      echo "sudah hidup — tidak ada yang dilakukan"
    else
      echo "menyalakan ulang…"
      bash ~/mulai-server.sh
    fi ;;
  *) echo "pakai: penjaga-server.sh cek|pulihkan"; exit 2 ;;
esac
