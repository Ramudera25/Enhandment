#!/usr/bin/env bash
# cek-koneksi.sh — verifikasi 4 prasyarat jalur kendali HP (SSH -> Termux -> rish).
# Pakai:  HP_SSH_ALIAS=termux-hp ./cek-koneksi.sh
# Semua nilai di sini contoh — sesuaikan dengan alias SSH milikmu sendiri.

set -u
ALIAS="${HP_SSH_ALIAS:-termux-hp}"
RISH_ID="${RISH_APPLICATION_ID:-com.termux}"
gagal=0

echo "[1/4] SSH ke Termux..."
if ssh -o ConnectTimeout=15 "$ALIAS" 'echo tersambung' >/dev/null 2>&1; then
  echo "      OK — sshd hidup, jaringan sampai."
else
  echo "      GAGAL — cek: Tailscale di HP aktif? sshd Termux jalan?"
  gagal=1
fi

echo "[2/4] rish / uid shell..."
ID_OUT="$(ssh -o ConnectTimeout=15 "$ALIAS" "RISH_APPLICATION_ID=$RISH_ID ./rish -c 'id'" 2>/dev/null)"
if echo "$ID_OUT" | grep -q 'uid=2000(shell)'; then
  echo "      OK — $ID_OUT" | cut -c1-80
else
  echo "      GAGAL — Shizuku mungkin mati (aktivasi ulang sekali dari HP)."
  gagal=1
fi

echo "[3/4] Layar tidak terkunci..."
KG="$(ssh -o ConnectTimeout=15 "$ALIAS" "RISH_APPLICATION_ID=$RISH_ID ./rish -c 'dumpsys window policy'" 2>/dev/null | grep -ci 'keyguard')x"
if ssh -o ConnectTimeout=15 "$ALIAS" "RISH_APPLICATION_ID=$RISH_ID ./rish -c 'dumpsys window policy'" 2>/dev/null | grep -qiE 'mKeyguardShowing=false|showing=false'; then
  echo "      OK — keyguard tidak tampil."
else
  echo "      PERIKSA — tidak bisa memastikan status kunci dari output dumpsys;"
  echo "      pastikan layar HP terbuka sebelum menjalankan tugas."
fi

echo "[4/4] Wakefulness layar..."
ssh -o ConnectTimeout=15 "$ALIAS" "RISH_APPLICATION_ID=$RISH_ID ./rish -c 'dumpsys power'" 2>/dev/null \
  | grep -m1 'mWakefulness=' || echo "      (tidak terbaca — abaikan bila langkah 1-2 OK)"

if [ "$gagal" -eq 0 ]; then
  echo "HASIL: jalur kendali SIAP."
else
  echo "HASIL: BELUM siap — perbaiki langkah yang GAGAL dulu."
  exit 1
fi
