#!/usr/bin/env bash
# eksekutor.sh — Eksekutor lokal muse-droid ("Jalan 0").
#
# Berjalan DI DALAM Termux (di HP). Membaca berkas tugas (.job) dan menjalankan
# seluruh langkahnya SECARA LOKAL lewat rish (uid shell) — agent cukup mengirim
# satu berkas per misi, bukan satu perintah SSH per langkah.
#
# Pakai:
#   eksekutor.sh <berkas.job>     jalankan satu tugas sampai selesai
#   eksekutor.sh --jaga           mode residen: pantau folder antrean terus-menerus
#
# Struktur folder (dibuat otomatis di $MUSE_DROID_HOME, bawaan ~/muse-droid):
#   antrean/  tugas .job menunggu      selesai/  tugas yang berhasil + .hasil
#   gagal/    tugas yang gagal + .hasil          bukti/    screenshot (FOTO)
#   log/      gabungan laporan
#
# Format berkas .job: satu perintah per baris. Baris kosong & diawali # diabaikan.
#   BUKA <paket>/<aktivitas> | BUKA <aksi-intent>   buka aplikasi
#   TUNGGU_TEKS "teks" [timeout-detik]              tunggu teks tampil di layar
#   KETUK_TEKS "teks"                               ketuk elemen berteks itu
#   KETUK <x> <y>                                   ketuk koordinat
#   GESER <x1> <y1> <x2> <y2> [ms]                  geser/swipe
#   KETIK "teks"                                    mengetik (spasi otomatis %s)
#   TEMPEL "teks"                                   isi clipboard lalu paste
#   TOMBOL home|back|enter|wakeup                   tombol sistem
#   JEDA <detik>                                    tidur
#   FOTO <nama.png>                                 screenshot ke folder bukti/
#   CEK_TEKS "teks"                                 gagal bila teks TIDAK tampil
#
# Sifat: berhenti pada kegagalan pertama (fail-fast) dan melaporkannya.
# Kebutuhan: Termux + rish/Shizuku aktif + python3 (pkg install python).

set -u
RID="${RISH_APPLICATION_ID:-com.termux}"
RISH_BIN="${RISH_BIN:-$HOME/rish}"
BASE="${MUSE_DROID_HOME:-$HOME/muse-droid}"
LOGFILE=""

rish() { RISH_APPLICATION_ID="$RID" "$RISH_BIN" -c "$1" 2>/dev/null < /dev/null; }

catat() {  # catat <status> <pesan>
  local baris="[$(date '+%H:%M:%S')] $1 $2"
  echo "$baris"
  [ -n "$LOGFILE" ] && echo "$baris" >> "$LOGFILE"
  echo "$baris" >> "$BASE/log/eksekutor.log"
}

dump_xml() {
  # Jembatan Download: output rish terpotong di ±8 KB, jadi XML dipindah dulu
  # sebagai berkas ke Download (bisa ditulis rish), lalu dibaca dari sisi Termux.
  rish 'uiautomator dump /sdcard/md-dump.xml >/dev/null 2>&1; cp /sdcard/md-dump.xml /sdcard/Download/md-dump.xml >/dev/null 2>&1'
  cat "/sdcard/Download/md-dump.xml" 2>/dev/null || cat "/storage/emulated/0/Download/md-dump.xml" 2>/dev/null
}

# cari_titik "teks" -> mencetak "x y" titik tengah elemen berteks itu (substring)
cari_titik() {
  dump_xml | python3 -c '
import sys, re
data, target = sys.stdin.read(), sys.argv[1]
for m in re.finditer(r"<node[^>]*>", data):
    tag = m.group(0)
    t = re.search(r"text=\"([^\"]*)\"", tag)
    if t and target in t.group(1):
        b = re.search(r"bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\"", tag)
        if b:
            x1, y1, x2, y2 = map(int, b.groups())
            print((x1+x2)//2, (y1+y2)//2)
            sys.exit(0)
sys.exit(1)' "$1"
}

teks_tampil() { dump_xml | grep -q "$1"; }

tanpa_kutip() { local s="$1"; s="${s%\"}"; s="${s#\"}"; echo "$s"; }

langkah_gagal() { catat "GAGAL" "langkah $1: $2 — misi dihentikan."; return 1; }

jalankan_job() {  # jalankan_job <file.job> -> 0 sukses, 1 gagal
  local job="$1" baris cmd sisa langkah=0
  LOGFILE="$BASE/log/$(basename "$job" .job)-$(date '+%Y%m%d-%H%M%S').hasil"
  catat "MULAI" "tugas: $job"
  local siap=0 i
  for i in 1 2 3 4 5; do
    if rish 'id' | grep -q 'uid=2000'; then siap=1; break; fi
    sleep 2
  done
  if [ "$siap" != 1 ]; then
    catat "GAGAL" "rish tidak memberi uid=2000 setelah 5 percobaan — Shizuku mati? Misi dibatalkan."
    return 1
  fi
  while IFS= read -r baris || [ -n "$baris" ]; do
    baris="${baris%$'\r'}"
    case "$baris" in ''|'#'*) continue ;; esac
    langkah=$((langkah+1))
    cmd="${baris%% *}"; sisa="${baris#* }"
    [ "$sisa" = "$baris" ] && sisa=""
    case "$cmd" in
      BUKA)
        case "$sisa" in */*) rish "am start -n $sisa" >/dev/null ;; *) rish "am start -a $sisa" >/dev/null ;; esac
        sleep 2; catat "OK" "$langkah BUKA $sisa" ;;
      TUNGGU_TEKS)
        local teks to; teks="$(tanpa_kutip "${sisa% *}")"; to="${sisa##* }"
        [ "$to" = "$sisa" ] && to=30
        [[ "$to" =~ ^[0-9]+$ ]] || to=30
        local tunggu=0
        until teks_tampil "$teks"; do
          tunggu=$((tunggu+10)); [ "$tunggu" -ge "$to" ] && { langkah_gagal "$langkah" "TUNGGU_TEKS \"$teks\" timeout ${to}d"; return 1; }
          sleep 8   # jeda wajar antar-dump: polling rapat terbukti menumbangkan uiautomator/Shizuku (uji 7-8 Okt)
        done
        catat "OK" "$langkah TUNGGU_TEKS \"$teks\" (tampil setelah ±${tunggu}d)" ;;
      KETUK_TEKS)
        local teks2 titik; teks2="$(tanpa_kutip "$sisa")"
        titik="$(cari_titik "$teks2")" || { langkah_gagal "$langkah" "KETUK_TEKS \"$teks2\" tidak ditemukan di layar"; return 1; }
        rish "input tap $titik" >/dev/null; sleep 1
        catat "OK" "$langkah KETUK_TEKS \"$teks2\" @ $titik" ;;
      KETUK)
        rish "input tap $sisa" >/dev/null; sleep 1; catat "OK" "$langkah KETUK $sisa" ;;
      GESER)
        rish "input swipe $sisa" >/dev/null; sleep 1; catat "OK" "$langkah GESER $sisa" ;;
      KETIK)
        local teks3; teks3="$(tanpa_kutip "$sisa")"
        rish "input text \"${teks3// /%s}\"" >/dev/null; sleep 1
        catat "OK" "$langkah KETIK (${#teks3} karakter)" ;;
      TEMPEL)
        local teks4; teks4="$(tanpa_kutip "$sisa")"
        if command -v termux-clipboard-set >/dev/null 2>&1; then
          printf '%s' "$teks4" | termux-clipboard-set
          # keyevent 279 terbukti tidak menempel di banyak aplikasi (Glints,
          # KitaLulus). Jalan utama v2 (perbaikan 8 Okt — kegagalan lama
          # dianalisis: eksekutor menekan-lama TANPA memastikan kolom fokus
          # dan memakai koordinat dump SEBELUM keyboard naik):
          #   1) temukan kolom teks, KETUK dulu untuk memaksa fokus + keyboard
          #   2) dump SEGAR -> koordinat pasca-keyboard
          #   3) tekan-lama di sana, ketuk menu "Tempel"/"Paste"
          #   4) verifikasi jujur: kata pertama harus tampil
          local dx node b tengah tm cara=""
          titik_kolom() {
            dx="$(dump_xml 2>/dev/null)" || dx=""
            node="$(printf '%s' "$dx" | grep -o '<node[^>]*>' | grep -m1 'EditText')" \
              || node="$(printf '%s' "$dx" | grep -o '<node[^>]*focused="true"[^>]*>' | head -1)" || node=""
            b="$(printf '%s' "$node" | grep -o 'bounds="\[[0-9,]*\]\[[0-9,]*\]"' | head -1)"
            [ -n "$b" ] && printf '%s' "$b" | awk -F'[^0-9]+' '{printf "%d %d", ($2+$4)/2, ($3+$5)/2}'
          }
          tengah="$(titik_kolom)" || tengah=""
          if [ -n "$tengah" ]; then
            rish "input tap $tengah" >/dev/null; sleep 2
            tengah="$(titik_kolom)" || tengah=""
            if [ -n "$tengah" ]; then
              rish "input swipe $tengah $tengah 800" >/dev/null; sleep 1
              tm="$(cari_titik "Tempel" 2>/dev/null)" || tm="$(cari_titik "Paste" 2>/dev/null)" || tm=""
              [ -n "$tm" ] && { rish "input tap $tm" >/dev/null; cara="fokus+tekan-lama+menu @ $tm"; }
            fi
          fi
          [ -n "$cara" ] || { rish 'input keyevent 279' >/dev/null; cara="keyevent 279"; }
          sleep 1
          local probe="${teks4%% *}"
          if teks_tampil "$probe"; then
            catat "OK" "$langkah TEMPEL (${#teks4} karakter via clipboard, $cara, terverifikasi tampil)"
          else
            langkah_gagal "$langkah" "TEMPEL tidak terbukti tampil di layar (cara terakhir: $cara)"; return 1
          fi
        else
          langkah_gagal "$langkah" "TEMPEL butuh termux-api (termux-clipboard-set tidak ada)"; return 1
        fi ;;
      TOMBOL)
        local k
        case "$sisa" in home) k=3 ;; back) k=4 ;; enter) k=66 ;; wakeup) k=224 ;; *) k="$sisa" ;; esac
        rish "input keyevent $k" >/dev/null; sleep 1; catat "OK" "$langkah TOMBOL $sisa" ;;
      JEDA)
        sleep "$sisa"; catat "OK" "$langkah JEDA ${sisa}d" ;;
      FOTO)
        local nama="${sisa:-foto.png}"
        rish "screencap -p /sdcard/md-foto.png" >/dev/null
        rish "cp /sdcard/md-foto.png /sdcard/Download/$nama" >/dev/null 2>&1 || true
        cp "/sdcard/Download/$nama" "$BASE/bukti/$nama" 2>/dev/null || cp "/storage/emulated/0/Download/$nama" "$BASE/bukti/$nama" 2>/dev/null || true
        catat "OK" "$langkah FOTO $nama" ;;
      CEK_TEKS)
        local teks5; teks5="$(tanpa_kutip "$sisa")"
        teks_tampil "$teks5" && catat "OK" "$langkah CEK_TEKS \"$teks5\" tampil" \
          || { langkah_gagal "$langkah" "CEK_TEKS \"$teks5\" TIDAK tampil"; return 1; } ;;
      *)
        langkah_gagal "$langkah" "perintah tidak dikenal: $cmd"; return 1 ;;
    esac
  done < "$job"
  catat "BERES" "tugas selesai: $job ($langkah langkah)"
  return 0
}

mkdir -p "$BASE"/{antrean,selesai,gagal,bukti,log}

case "${1:-}" in
  --jaga)
    echo "Eksekutor muse-droid berjaga di $BASE/antrean (Ctrl+C untuk berhenti)"
    while true; do
      for job in "$BASE"/antrean/*.job; do
        [ -e "$job" ] || continue
        if jalankan_job "$job"; then
          mv "$job" "$BASE/selesai/"; cp "$LOGFILE" "$BASE/selesai/$(basename "$job" .job).hasil" 2>/dev/null || true
        else
          mv "$job" "$BASE/gagal/"; cp "$LOGFILE" "$BASE/gagal/$(basename "$job" .job).hasil" 2>/dev/null || true
        fi
      done
      sleep 5
    done ;;
  '')
    echo "Pakai: eksekutor.sh <berkas.job> | eksekutor.sh --jaga" >&2; exit 2 ;;
  *)
    jalankan_job "$1" ;;
esac
