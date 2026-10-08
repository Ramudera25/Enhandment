#!/data/data/com.termux/files/usr/bin/bash
# penjaga-kaki.sh — penjaga residen tiga kaki kendali HP (Enhandment advance/13)
#
# Siklus ringan tiap 60 detik:
#   1. Server residen u2 — ping HTTP /ping. Bila mati DAN rish hidup:
#      hidupkan ulang lewat ~/mulai-server.sh.
#   2. rish/Shizuku — probe `rish -c id` harus menjawab uid=2000.
#      Shizuku TIDAK bisa dihidupkan ulang dari skrip (harus ketuk Start di
#      aplikasinya oleh pemilik HP), jadi penjaga mengirim notifikasi Termux
#      SEKALI per episode kematian, dan mencatat pemulihannya di log.
#   3. Aplikasi pendamping (port 19101) — hanya dicatat perubahan statusnya;
#      menghidupkannya perlu membuka aplikasinya (mengganggu layar), jadi
#      penjaga tidak menyentuh kaki ini.
#
# Pelajaran Fase 6 berlaku: penjaga TIDAK PERNAH memanggil dump UI — hanya
# ping HTTP dan probe shell ringan, jauh di bawah ambang yang menumbangkan
# UiAutomation.
#
# Berkas keadaan & log: ~/.penjaga-kaki/ (status, penjaga.log terkendali 200KB)
# Satu instans saja (pidfile). Berhenti: bunuh PID di ~/.penjaga-kaki/penjaga.pid
#
# Kenop uji (variabel lingkungan):
#   PENJAGA_SIKLUS=detik     jeda antar siklus (default 60)
#   PENJAGA_SATU_KALI=1      jalankan satu siklus lalu keluar
#   PENJAGA_DIR=path         direktori keadaan alternatif (untuk uji terisolasi)
#   PENJAGA_RISH_CMD=cmd     perintah probe rish alternatif (untuk uji simulasi mati)

export RISH_APPLICATION_ID="com.termux"
DIR="${PENJAGA_DIR:-$HOME/.penjaga-kaki}"
SIKLUS="${PENJAGA_SIKLUS:-60}"
mkdir -p "$DIR"
LOG="$DIR/penjaga.log"
STATUSF="$DIR/status"
PIDF="$DIR/penjaga.pid"

if [ -f "$PIDF" ]; then
  pid_lama="$(cat "$PIDF" 2>/dev/null)"
  if [ -n "$pid_lama" ] && kill -0 "$pid_lama" 2>/dev/null; then
    echo "penjaga-kaki sudah jalan (pid $pid_lama) — instans ini keluar."
    exit 0
  fi
fi
echo $$ > "$PIDF"

catat() {
  # rotasi sederhana: potong log bila > 200 KB
  if [ -f "$LOG" ] && [ "$(stat -c %s "$LOG" 2>/dev/null || echo 0)" -gt 204800 ]; then
    tail -c 100000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
  fi
  echo "$(date '+%F %T') $*" >> "$LOG"
}

tulis_status() { # tulis_status kunci nilai
  local kunci="$1" nilai="$2" tmp="$STATUSF.tmp"
  grep -v "^$kunci=" "$STATUSF" 2>/dev/null > "$tmp" || true
  echo "$kunci=$nilai" >> "$tmp"
  mv "$tmp" "$STATUSF"
}

baca_status() { grep "^$1=" "$STATUSF" 2>/dev/null | cut -d= -f2; }

ping_u2() {
  [ "$(curl -s -m 3 http://127.0.0.1:9008/ping 2>/dev/null)" = "pong" ]
}

probe_rish_sekali() {
  if [ -n "$PENJAGA_RISH_CMD" ]; then
    timeout 15 bash -c "$PENJAGA_RISH_CMD" 2>/dev/null | grep -q "uid=2000"
  else
    timeout 15 "$HOME/rish" -c "id" 2>/dev/null | grep -q "uid=2000"
  fi
}

probe_rish() {
  # Shizuku di HP ini terbukti "berdenyut": timeout binder sesaat (hitungan
  # detik) pernah terjadi di tengah hari yang sehat (kasus 8 Okt 12.04 —
  # probe pertama penjaga sempat menembak notifikasi palsu). Karena itu
  # kematian hanya dinyatakan bila probe gagal DUA kali berurutan dengan
  # jeda 10 detik; deteksi tetap <= ~90 detik, alarm palsu hilang.
  if probe_rish_sekali; then
    return 0
  fi
  sleep 10
  probe_rish_sekali
}

cek_pendamping() {
  timeout 3 bash -c 'exec 3<>/dev/tcp/127.0.0.1/19101' 2>/dev/null
}

notif() {
  termux-notification --priority high --title "$1" --content "$2" >/dev/null 2>&1
  catat "NOTIF terkirim: $1 — $2"
}

siklus() {
  # --- kaki 2 lebih dulu: rish adalah penyalur perbaikan kaki lain ---
  if probe_rish; then
    rish_baru="ok"
  else
    rish_baru="mati"
  fi
  rish_lama="$(baca_status rish)"
  if [ "$rish_baru" = "mati" ] && [ "$rish_lama" != "mati" ]; then
    tulis_status rish mati
    catat "rish/Shizuku MATI (probe gagal)"
    notif "⚠ Shizuku mati — kendali HP lumpuh" \
      "Buka aplikasi Shizuku lalu ketuk Start agar kendali jarak jauh pulih. Terdeteksi penjaga kaki pukul $(date '+%H:%M')."
  elif [ "$rish_baru" = "ok" ] && [ "$rish_lama" = "mati" ]; then
    tulis_status rish ok
    catat "rish/Shizuku PULIH"
  elif [ -z "$rish_lama" ]; then
    tulis_status rish "$rish_baru"
    catat "status awal rish: $rish_baru"
  fi

  # --- kaki 1: server residen u2 ---
  if ping_u2; then
    if [ "$(baca_status u2)" = "mati" ]; then
      tulis_status u2 ok
      catat "server residen u2 PULIH"
    elif [ -z "$(baca_status u2)" ]; then
      tulis_status u2 ok
    fi
  else
    if [ "$(baca_status u2)" != "mati" ]; then
      tulis_status u2 mati
      catat "server residen u2 MATI (ping gagal)"
    fi
    if [ "$rish_baru" = "ok" ] && [ -f "$HOME/mulai-server.sh" ]; then
      catat "menghidupkan ulang server residen via mulai-server.sh..."
      if timeout 150 bash "$HOME/mulai-server.sh" >> "$LOG" 2>&1 && ping_u2; then
        tulis_status u2 ok
        catat "server residen u2 HIDUP lagi oleh penjaga"
      else
        catat "menghidupkan ulang u2 GAGAL — akan dicoba siklus berikutnya"
      fi
    elif [ "$rish_baru" != "ok" ]; then
      catat "u2 mati dan rish juga mati — perbaikan menunggu Shizuku hidup"
    fi
  fi

  # --- kaki 3: aplikasi pendamping (catat saja) ---
  if cek_pendamping; then
    p_baru="ok"
  else
    p_baru="mati"
  fi
  p_lama="$(baca_status pendamping)"
  if [ "$p_baru" != "$p_lama" ]; then
    tulis_status pendamping "$p_baru"
    catat "aplikasi pendamping: ${p_lama:-?} -> $p_baru (dicatat saja, tidak disentuh)"
  fi
}

catat "penjaga-kaki mulai (pid $$, siklus ${SIKLUS}d)"
while true; do
  siklus
  [ -n "$PENJAGA_SATU_KALI" ] && break
  sleep "$SIKLUS"
done
catat "penjaga-kaki berhenti (pid $$)"
rm -f "$PIDF"
