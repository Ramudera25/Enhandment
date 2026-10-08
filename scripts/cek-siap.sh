#!/usr/bin/env bash
# cek-siap.sh — periksa seluruh rantai muse-droid sekali jalan, dari VM.
# Read-only: tidak mengetuk layar, tidak mengubah apa pun di HP.
# Pakai: bash scripts/cek-siap.sh
set -u
SSH="ssh -F /home/hatch/.ssh/config termux-hp"
PYCEK='import json,urllib.request
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
req=urllib.request.Request("http://127.0.0.1:9008/jsonrpc/0",data=json.dumps({"jsonrpc":"2.0","id":1,"method":"dumpWindowHierarchy","params":[True,50]}).encode(),headers={"Content-Type":"application/json"})
x=json.load(op.open(req,timeout=8)).get("result") or ""
print(len(x))'

echo "== cek-siap muse-droid =="
printf "1) SSH ke Termux (mux) : "; $SSH 'echo tersambung' 2>/dev/null || echo "GAGAL"
printf "2) Shizuku/rish        : "; $SSH 'export RISH_APPLICATION_ID=com.termux; ./rish -c id 2>/dev/null' 2>/dev/null | grep -o 'uid=[0-9]*' || echo "GAGAL"
printf "3) Server residen u2   : "; baris3="$($SSH 'export RISH_APPLICATION_ID=com.termux; ./rish -c "ps -A -o PID,PPID,ETIME,NAME" 2>/dev/null' 2>/dev/null | awk '$2==1 && $4=="app_process" {print $3; exit}')"; [ -n "$baris3" ] && echo "hidup, umur $baris3" || echo "tidak terbaca via rish"
printf "   dump lewat server   : "; n="$($SSH "python3 -c '$PYCEK'" 2>/dev/null)"; [ -n "$n" ] && echo "$n byte OK" || echo "GAGAL"
printf "4) Pendamping PING/UID : "; $SSH 'python3 -c "
import socket
def k(p):
    s=socket.create_connection((\"127.0.0.1\",19101),timeout=6); s.sendall((p+\"\\n\").encode()); d=s.recv(256).decode().strip(); s.close(); return d
print(k(\"PING\"), \"/\", k(\"UID\"))" 2>/dev/null' 2>/dev/null || echo "GAGAL (layanan belum dinyalakan?)"
printf "5) Eksekutor           : "; $SSH 'test -x ~/eksekutor.sh -o -f ~/eksekutor.sh && echo siap' 2>/dev/null || echo "GAGAL"
