#!/usr/bin/env bash
# setup-linux.sh — persiapan komputer Linux sebagai pengendali HP.
# Memasang: adb, scrcpy, openssh-client, (opsional) tailscale.
# Teruji untuk keluarga Debian/Ubuntu; distribusi lain: lihat catatan di bawah.
#
#   bash scripts/setup-linux.sh

set -u
echo "== muse-droid: persiapan Linux =="

if command -v apt >/dev/null 2>&1; then
  echo "[1/3] Pasang adb, scrcpy, openssh-client (sudo)…"
  sudo apt update
  sudo apt install -y adb scrcpy openssh-client
else
  echo "Distribusi non-apt terdeteksi. Pasang manual ekuivalennya:"
  echo "  Arch  : sudo pacman -S android-tools scrcpy openssh"
  echo "  Fedora: sudo dnf install android-tools scrcpy openssh-clients"
  exit 1
fi

echo "[2/3] Grup plugdev (izin akses USB Android)…"
if getent group plugdev >/dev/null; then
  sudo usermod -aG plugdev "$USER" && echo "      ditambahkan — perlu logout/login sekali."
fi

echo "[3/3] Tailscale (opsional — hanya untuk jalur jaringan privat)…"
if ! command -v tailscale >/dev/null 2>&1; then
  read -r -p "      Pasang Tailscale sekarang? [y/N] " jawab
  if [ "$jawab" = "y" ] || [ "$jawab" = "Y" ]; then
    curl -fsSL https://tailscale.com/install.sh | sh
    echo "      Jalankan: sudo tailscale up"
  else
    echo "      Dilewati."
  fi
fi

cat <<'SELESAI'

SELESAI. Di HP: aktifkan "USB debugging" (Opsi Pengembang), colok USB, setujui dialognya.
Lalu verifikasi di sini:
    adb devices     → status "device"
    adb shell id    → uid=2000(shell)

Langkah berikutnya: buka docs/tutorial/05-linux.md (Bagian 3 — tes loop penuh),
lalu docs/07-ai-controller.md untuk memilih otak pengendalinya.
SELESAI
