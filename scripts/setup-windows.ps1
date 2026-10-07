# setup-windows.ps1 — persiapan komputer Windows sebagai pengendali HP.
# Memasang via winget: Android Platform-Tools (adb), scrcpy, (opsional) Tailscale.
#
#   Jalankan di PowerShell:  ./scripts/setup-windows.ps1
#   Bila diblokir policy:     powershell -ExecutionPolicy Bypass -File ./scripts/setup-windows.ps1

Write-Host "== muse-droid: persiapan Windows =="

function Install-Paket($id, $nama) {
    Write-Host "[*] Memasang $nama ..."
    winget install --id $id -e --accept-package-agreements --accept-source-agreements
}

Install-Paket "Google.PlatformTools" "Android SDK Platform-Tools (adb)"
Install-Paket "Genymobile.scrcpy" "scrcpy (cermin layar)"

$jawab = Read-Host "Pasang Tailscale juga? (hanya untuk jalur jaringan privat) [y/N]"
if ($jawab -eq "y" -or $jawab -eq "Y") {
    Install-Paket "Tailscale.Tailscale" "Tailscale"
}

Write-Host ""
Write-Host "SELESAI. Langkah berikutnya:"
Write-Host "1) Di HP: aktifkan 'USB debugging' (Pengaturan > Opsi Pengembang)."
Write-Host "2) Colok USB, setujui dialog izin di HP."
Write-Host "3) Buka PowerShell BARU (agar PATH segar), lalu verifikasi:"
Write-Host "     adb devices    -> status 'device'"
Write-Host "     adb shell id   -> uid=2000(shell)"
Write-Host "     scrcpy         -> cermin layar (bonus)"
