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
  # Jalur utama (8 Okt, Fase 8): server residen u2 di 127.0.0.1:9008 —
  # dump 0,56 dtk dan selalu segar. Eksekutor berjalan di HP, jadi bisa
  # memanggilnya langsung tanpa SSH.
  local via_server
  via_server="$(python3 -c '
import json, urllib.request
# Endpoint server u2 yang benar: /jsonrpc/0 (dengan /0) — /jsonrpc polos
# menjawab 404 (terbukti 8 Okt; dugaan awal "proxy" ternyata keliru).
# ProxyHandler kosong tetap dipasang sebagai asuransi env proxy Termux.
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
req = urllib.request.Request("http://127.0.0.1:9008/jsonrpc/0",
  data=json.dumps({"jsonrpc":"2.0","id":1,"method":"dumpWindowHierarchy","params":[False,50]}).encode(),
  headers={"Content-Type":"application/json"})
try:
    r = json.load(opener.open(req, timeout=6))
    print(r.get("result") or "", end="")
except Exception:
    pass
' 2>/dev/null)"
  if [ "${via_server#\<?xml}" != "$via_server" ]; then DUMP_VIA="server"; printf '%s' "$via_server"; return 0; fi
  # Cadangan: jembatan Download (output rish terpotong ±8 KB, XML dipindah
  # sebagai berkas). PENJAGA KESEGARAN: berkas hanya diterima bila mtime-nya
  # MAJU sesudah perintah dump — dump basi pernah menggagalkan TEMPEL
  # (08 Okt: titik kolom dibaca dari halaman lama).
  local berkas="/sdcard/Download/md-dump.xml" sebelum=""
  [ -f "$berkas" ] && sebelum="$(stat -c %Y "$berkas" 2>/dev/null)"
  rish 'uiautomator dump /sdcard/md-dump.xml >/dev/null 2>&1; cp /sdcard/md-dump.xml /sdcard/Download/md-dump.xml >/dev/null 2>&1'
  local sesudah=""
  [ -f "$berkas" ] && sesudah="$(stat -c %Y "$berkas" 2>/dev/null)"
  DUMP_VIA="jembatan"
  if [ -n "$sesudah" ] && [ "$sesudah" != "$sebelum" ]; then cat "$berkas" 2>/dev/null; return 0; fi
  cat "$berkas" 2>/dev/null || cat "/storage/emulated/0/Download/md-dump.xml" 2>/dev/null
}

# --- Tangan server residen (percepatan 8 Okt) ---
# click/swipe/pressKey lewat JSON-RPC u2: ±0,16-0,4 dtk, lawan 1-2 dtk
# per panggilan rish (spawn proses). Gagal -> pemanggil jatuh ke rish.
DUMP_VIA=""
rpc_u2() { # rpc_u2 <metode> <params-json>
  python3 -c '
import json, sys, urllib.request
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
req = urllib.request.Request("http://127.0.0.1:9008/jsonrpc/0",
  data=json.dumps({"jsonrpc":"2.0","id":1,"method":sys.argv[1],"params":json.loads(sys.argv[2])}).encode(),
  headers={"Content-Type":"application/json"})
try:
    r = json.load(op.open(req, timeout=8))
    sys.exit(0 if r.get("result") is not None else 1)
except Exception:
    sys.exit(1)
' "$1" "$2" 2>/dev/null
}
ketuk_di() { # ketuk_di "x y"
  local x="${1%% *}" y="${1##* }"
  rpc_u2 click "[$x,$y]" || rish "input tap $x $y" >/dev/null
}
geser_di() { # geser_di "x1 y1 x2 y2 [ms]"
  set -- $1
  # Langkah swipe server u2 ≈ 5 ms/langkah (800 ms tekan-lama = 160).
  # Bagi-10 terbukti kurang panjang: menu tempel tidak muncul (uji 07.30).
  local langkah=$(( ${5:-300} / 5 )); [ "$langkah" -lt 5 ] && langkah=5
  rpc_u2 swipe "[$1,$2,$3,$4,$langkah]" || rish "input swipe $*" >/dev/null
}

# --- Penjaga TARGET (keamanan, 8 Okt) ---
# Misi boleh menyatakan "TARGET <paket>" (baris direktif, bukan langkah).
# Sebelum langkah BUTA (KETUK/GESER/KETIK/TOMBOL/TEMPEL) eksekutor
# memastikan paket target masih ada di hierarki layar; bila layar sudah
# berpindah tangan (pengguna memakai HP, aplikasi lain di depan), langkah
# DIBATALKAN dengan GAGAL jujur — pelajaran kejadian 07.34: misi TEMPEL
# menempel ke bilah alamat Brave yang sedang dipakai pengguna.
TARGET_MISI=""
cek_target() {
  [ -n "$TARGET_MISI" ] || return 0
  dump_xml 2>/dev/null | grep -q "package=\"$TARGET_MISI\""
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
  TARGET_MISI=""
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
    if [ "${baris%% *}" = "TARGET" ]; then TARGET_MISI="${baris#* }"; catat "INFO" "target misi: $TARGET_MISI"; continue; fi
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
        local tunggu=0 jeda=8
        until teks_tampil "$teks"; do
          # Polling rapat HANYA aman lewat server residen (HTTP, tanpa spawn
          # uiautomator). Jalur jembatan tetap berjeda 8 dtk — polling rapat
          # di jalur itu terbukti menumbangkan uiautomator/Shizuku (7-8 Okt).
          [ "$DUMP_VIA" = "server" ] && jeda=1 || jeda=8
          tunggu=$((tunggu+jeda)); [ "$tunggu" -ge "$to" ] && { langkah_gagal "$langkah" "TUNGGU_TEKS \"$teks\" timeout ${to}d"; return 1; }
          sleep $jeda
        done
        catat "OK" "$langkah TUNGGU_TEKS \"$teks\" (tampil setelah ±${tunggu}d)" ;;
      KETUK_TEKS)
        local teks2 titik; teks2="$(tanpa_kutip "$sisa")"
        titik="$(cari_titik "$teks2")" || { langkah_gagal "$langkah" "KETUK_TEKS \"$teks2\" tidak ditemukan di layar"; return 1; }
        ketuk_di "$titik"; sleep 1
        catat "OK" "$langkah KETUK_TEKS \"$teks2\" @ $titik" ;;
      KETUK)
        cek_target || { langkah_gagal "$langkah" "TARGET $TARGET_MISI tidak di layar depan — KETUK dibatalkan demi keamanan"; return 1; }
        ketuk_di "$sisa"; sleep 1; catat "OK" "$langkah KETUK $sisa" ;;
      GESER)
        cek_target || { langkah_gagal "$langkah" "TARGET $TARGET_MISI tidak di layar depan — GESER dibatalkan demi keamanan"; return 1; }
        geser_di "$sisa"; sleep 1; catat "OK" "$langkah GESER $sisa" ;;
      KETIK)
        cek_target || { langkah_gagal "$langkah" "TARGET $TARGET_MISI tidak di layar depan — KETIK dibatalkan demi keamanan"; return 1; }
        local teks3; teks3="$(tanpa_kutip "$sisa")"
        rish "input text \"${teks3// /%s}\"" >/dev/null; sleep 1
        catat "OK" "$langkah KETIK (${#teks3} karakter)" ;;
      TEMPEL)
        cek_target || { langkah_gagal "$langkah" "TARGET $TARGET_MISI tidak di layar depan — TEMPEL dibatalkan demi keamanan"; return 1; }
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
            ketuk_di "$tengah"; sleep 2
            tengah="$(titik_kolom)" || tengah=""
            if [ -n "$tengah" ]; then
              geser_di "$tengah $tengah 800"; sleep 1
              tm="$(cari_titik "Tempel" 2>/dev/null)" || tm="$(cari_titik "Paste" 2>/dev/null)" || tm=""
              [ -n "$tm" ] && { ketuk_di "$tm"; cara="fokus+tekan-lama+menu @ $tm"; }
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
        cek_target || { langkah_gagal "$langkah" "TARGET $TARGET_MISI tidak di layar depan — TOMBOL dibatalkan demi keamanan"; return 1; }
        local k
        case "$sisa" in home) k=3 ;; back) k=4 ;; enter) k=66 ;; wakeup) k=224 ;; *) k="$sisa" ;; esac
        case "$sisa" in
          home|back|enter) rpc_u2 pressKey "[\"$sisa\"]" || rish "input keyevent $k" >/dev/null ;;
          *) rish "input keyevent $k" >/dev/null ;;
        esac
        sleep 1; catat "OK" "$langkah TOMBOL $sisa" ;;
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
