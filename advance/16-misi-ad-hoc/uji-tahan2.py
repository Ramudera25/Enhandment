# Uji TAHAN native v2: pemulihan dulu, lalu berbasis KONTEN pohon
# (pelajaran: gerbang umur salah — layar statis tak memicu event).
import socket, json, time, subprocess

def kirim(perintah, to=8):
    s = socket.create_connection(("127.0.0.1", 19102), 3)
    s.settimeout(to)
    s.sendall((perintah + "\n").encode())
    buf = b""
    while True:
        try:
            d = s.recv(65536)
        except socket.timeout:
            break
        if not d: break
        buf += d
        if buf.endswith(b"\n"): break
    s.close()
    try: return json.loads(buf.decode("utf-8", "replace"))
    except Exception: return {"mentah": buf.decode("utf-8", "replace")[:150]}

def nodes_dgn(teks, ulang=30, jeda=0.2):
    """Poll sampai teks muncul di pohon (konten, bukan umur)."""
    for _ in range(ulang):
        try:
            j = kirim("POHON")
            ns = j.get("nodes", [])
            for n in ns:
                if teks.lower() in (n.get("t") or "").lower() and n.get("klik"):
                    b = n.get("b") or "[0,0][0,0]"
                    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
                    if m:
                        x1,y1,x2,y2 = map(int, m.groups())
                        return ((x1+x2)//2, (y1+y2)//2, n.get("t","")[:40])
        except Exception:
            return None
        time.sleep(jeda)
    return None

import re
print("0. pulihkan pohon via am start pendamping")
subprocess.run(["am","start","-n","id.musedroid.pendamping/.MainActivity"],
               capture_output=True, timeout=15)
ok = False
for i in range(20):
    try:
        j = kirim("PING", 3)
        if j.get("pong"): ok = True; break
    except Exception: pass
    time.sleep(0.5)
print("   pohon:", "HIDUP v%s" % kirim("PING").get("versi") if ok else "TETAP MATI")
if not ok: raise SystemExit("pohon tak bisa dipulihkan tanpa sentuhan")

print("1. buka WiFi, tunggu 'Add network' (konten)")
subprocess.run(["am","start","-a","android.settings.WIFI_SETTINGS"],
               capture_output=True, timeout=15)
kolom = nodes_dgn("Add network", 40)
print("   Add network:", kolom)
if not kolom:
    j = kirim("POHON")
    ns = j.get("nodes", [])
    teks = [n.get("t","")[:25] for n in ns if n.get("t")][:10]
    print("   GAGAL. isi pohon kini (%d node): %s" % (len(ns), teks))
    raise SystemExit("layar kemungkinan mati / Settings tak tampil")

print("2. ketuk Add network, tunggu 'Network name'")
kirim("KETUK %d %d" % (kolom[0], kolom[1]))
nama = nodes_dgn("Network name", 40)
print("   Network name:", nama)
assert nama, "dialog tak terbuka"

print("3. TAHAN native di kolom %d,%d" % (nama[0], nama[1]))
t0 = time.time()
j = kirim("TAHAN %d %d" % (nama[0], nama[1]))
print("   balasan: %s (%.0f ms)" % (json.dumps(j), (time.time()-t0)*1000))

print("4. poll menu Tempel (30ms x 40)")
menu = nodes_dgn("Tempel", 40, 0.03) or nodes_dgn("Paste", 10, 0.03)
print("   menu Tempel:", menu)
if menu:
    kirim("KETUK %d %d" % (menu[0], menu[1]))
    time.sleep(0.5)
kirim("TOMBOL 4"); time.sleep(0.3); kirim("TOMBOL 4")
print("KESIMPULAN: tekan-lama native %s" % (
    "BEKERJA penuh (menu Tempel muncul & diketuk)" if menu
    else "TAHAN terkirim tapi menu tak terdeteksi (cek Manual)"))
