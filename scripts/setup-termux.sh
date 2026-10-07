#!/usr/bin/env bash
# setup-termux.sh — JALANKAN DI DALAM TERMUX (di HP).
# Memasang pintu masuk agent: openssh + termux-api, menyiapkan ~/.ssh,
# dan (opsional) menyalakan sshd. Aman dijalankan berulang kali.
#
#   bash setup-termux.sh

set -u
echo "== muse-droid: persiapan Termux =="

echo "[1/5] Update paket…"
pkg update -y >/dev/null 2>&1 || true

echo "[2/5] Pasang openssh + termux-api…"
pkg install -y openssh termux-api >/dev/null 2>&1
command -v sshd >/dev/null && echo "      sshd: ada" || echo "      PERINGATAN: sshd tidak ditemukan"

echo "[3/5] Izin penyimpanan (untuk membaca berkas dari /sdcard)…"
termux-setup-storage >/dev/null 2>&1 || true

echo "[4/5] Siapkan ~/.ssh…"
mkdir -p ~/.ssh && chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys

echo "[5/5] Nyalakan sshd + wake lock…"
sshd 2>/dev/null || true
termux-wake-lock 2>/dev/null || true

cat <<'SELESAI'

SELESAI. Langkah manual terakhir (sekali saja):

1) Pasang kunci publik agent ke HP ini:
     cat kunci-publik-agent.pub >> ~/.ssh/authorized_keys
   (file .pub berasal dari mesin agent: ssh-keygen -t ed25519 -f ~/.ssh/termux_hp)

2) Username Termux kamu (untuk konfigurasi SSH di mesin agent):
SELESAI
echo "     user: $(whoami)   port sshd: 8022"

echo
echo "Berikutnya: Tutorial 02 (Tailscale) lalu 03 (Shizuku) di docs/tutorial/."
