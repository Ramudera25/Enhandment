#!/usr/bin/env python3
# misi-cepat.py — Runner makro residen muse-droid (advance/11).
#
# Penggabungan dua peningkatan dari roadmap LOG-PEMBAHARUAN.md §8:
#   (1) Eksekusi makro penuh di perangkat: SATU proses Python yang tinggal
#       hidup selama misi berjalan. Menghilangkan pajak terbesar eksekutor
#       lama yang tersembunyi: setiap panggilan RPC di eksekutor.sh
#       men-spawn proses python3 baru (±100-300 ms per langkah hanya untuk
#       menyalakan interpreter), ditambah sleep datar 1 dtk sesudah hampir
#       setiap langkah.
#   (2) Kueri terarah: dump XML TIDAK pernah keluar dari proses ini.
#       Pencarian teks mengurai pohon di dalam proses dan hanya memakai
#       bounds-nya — tidak ada transfer/parse ulang 60-130 KB di luar.
#
# Bahasa misi: kompatibel dengan berkas .job eksekutor.sh (TARGET, BUKA,
# TUNGGU_TEKS, KETUK_TEKS, KETUK, GESER, KETIK, TEMPEL, TOMBOL, JEDA,
# FOTO, CEK_TEKS). Perbedaan perilaku yang disengaja:
#   - Gerbang masuk TIDAK lagi wajib rish: misi jalan bila server residen
#     u2 sehat (mode server); rish hanya cadangan (mode jembatan, lambat).
#   - TUNGGU_TEKS polling 250 ms di mode server (dulu 1 dtk).
#   - Sesudah ketukan: tunggu hierarki BERUBAH (polling 150 ms, batas
#     1,2 dtk) menggantikan sleep datar 1 dtk.
#   - Setiap langkah dilaporkan dengan durasinya (ms) — benchmark bawaan.
#   - Penjaga TARGET dipertahankan persis: langkah buta dibatalkan jujur
#     bila paket target tidak ada di hierarki layar.
#
# Pakai (di Termux HP):  python3 misi-cepat.py <berkas.job>
# Kebutuhan: server residen u2 hidup di 127.0.0.1:9008 (cek: cek-siap.sh).

import http.client
import json
import re
import subprocess
import sys
import time

HOST, PORT = "127.0.0.1", 9008
POLL_TUNGGU = 0.25     # dtk — polling TUNGGU_TEKS mode server
POLL_UBAH = 0.15       # dtk — polling "hierarki berubah" sesudah ketukan
BATAS_UBAH = 1.2       # dtk — batas tunggu perubahan sesudah ketukan
NODE_RE = re.compile(r"<node[^>]*>")
ATTR = lambda tag, nama: (re.search(nama + r'="([^"]*)"', tag) or [None, ""])[1]
BOUNDS_RE = re.compile(r"bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\"")


class KlienU2:
    """Satu koneksi HTTP persisten ke server residen u2 (keep-alive)."""

    def __init__(self):
        self.conn = None
        self.id = 0

    def _sambung(self):
        self.conn = http.client.HTTPConnection(HOST, PORT, timeout=8)

    def rpc(self, method, params):
        body = json.dumps({"jsonrpc": "2.0", "id": self.id, "method": method,
                           "params": params}).encode()
        self.id += 1
        for percobaan in (1, 2):
            try:
                if self.conn is None:
                    self._sambung()
                self.conn.request("POST", "/jsonrpc/0", body,
                                  {"Content-Type": "application/json"})
                resp = self.conn.getresponse()
                data = resp.read()
                if resp.status != 200:
                    raise IOError("HTTP %s" % resp.status)
                return json.loads(data).get("result")
            except Exception:
                self.conn = None
                if percobaan == 2:
                    raise

    def dump(self):
        r = self.rpc("dumpWindowHierarchy", [False, 50])
        if not r or not r.startswith("<?xml"):
            raise IOError("dump tidak valid dari server")
        return r

    def klik(self, x, y):
        return self.rpc("click", [x, y])

    def geser(self, x1, y1, x2, y2, ms):
        langkah = max(5, ms // 5)  # langkah swipe u2 ≈ 5 ms (teruji 8 Okt)
        return self.rpc("swipe", [x1, y1, x2, y2, langkah])

    def tombol(self, nama):
        return self.rpc("pressKey", [nama])


def rish(perintah):
    import os
    env = dict(os.environ)
    env["RISH_APPLICATION_ID"] = "com.termux"
    return subprocess.run([os.path.expanduser("~/rish"), "-c", perintah],
                          env=env, capture_output=True, text=True, timeout=30).stdout


def cari_titik(xml, teks):
    """Kueri terarah: kembalikan 'x y' titik tengah node pertama yang
    teks/content-desc-nya mengandung `teks`; None bila tidak ada."""
    for m in NODE_RE.finditer(xml):
        tag = m.group(0)
        t = ATTR(tag, "text") or ATTR(tag, "content-desc")
        if t and teks in t:
            b = BOUNDS_RE.search(tag)
            if b:
                x1, y1, x2, y2 = map(int, b.groups())
                return (x1 + x2) // 2, (y1 + y2) // 2
    return None


def kolom_teks(xml):
    """Titik tengah kolom teks (EditText / node terfokus) pertama."""
    for m in NODE_RE.finditer(xml):
        tag = m.group(0)
        if "EditText" in ATTR(tag, "class") or ATTR(tag, "focused") == "true":
            b = BOUNDS_RE.search(tag)
            if b:
                x1, y1, x2, y2 = map(int, b.groups())
                return (x1 + x2) // 2, (y1 + y2) // 2
    return None


class MisiGagal(Exception):
    pass


class Runner:
    def __init__(self):
        self.klien = KlienU2()
        self.target = ""
        self.mode = None       # "server" | "jembatan"
        self.xml_terakhir = ""
        self.t_xml = 0.0

    # -- infrastruktur -------------------------------------------------
    def catat(self, status, pesan):
        print("[%s] %s %s" % (time.strftime("%H:%M:%S"), status, pesan), flush=True)

    def dump(self, paksa=False):
        if not paksa and self.xml_terakhir and time.time() - self.t_xml < 0.3:
            return self.xml_terakhir
        self.xml_terakhir = self.klien.dump()
        self.t_xml = time.time()
        return self.xml_terakhir

    def tunggu_berubah(self, xml_lama):
        t0 = time.time()
        while time.time() - t0 < BATAS_UBAH:
            time.sleep(POLL_UBAH)
            try:
                baru = self.dump(paksa=True)
            except Exception:
                return
            if baru != xml_lama:
                return

    def cek_target(self):
        if not self.target:
            return True
        return 'package="%s"' % self.target in self.dump()

    def wajib_target(self, cmd):
        if not self.cek_target():
            raise MisiGagal("TARGET %s tidak di layar depan — %s dibatalkan demi keamanan"
                            % (self.target, cmd))

    # -- langkah ---------------------------------------------------------
    def buka(self, sisa):
        if "/" in sisa:
            r = subprocess.run(["am", "start", "-n", sisa], capture_output=True, text=True, timeout=20)
            if r.returncode != 0 and self.mode == "jembatan":
                rish("am start -n %s" % sisa)
        else:
            subprocess.run(["am", "start", "-a", sisa], capture_output=True, text=True, timeout=20)
        # tunggu paket target (atau perubahan layar) — bukan sleep datar
        t0 = time.time()
        while time.time() - t0 < 6:
            time.sleep(POLL_UBAH)
            try:
                xml = self.dump(paksa=True)
            except Exception:
                continue
            if not self.target or 'package="%s"' % self.target in xml:
                return

    def tautan(self, url):
        # Deep link: intent VIEW. Jalur subprocess (shim am Termux) dulu,
        # cadangan via rish (shell uid=2000) bila perintah gagal. Sesudah
        # dispatch, tunggu paket TARGET tampil di dump (bukan sleep datar).
        # Bila URL tidak diklaim aplikasi target (mis. link explore Glints
        # yang lari ke browser), tunggu habis tanpa tampil — langkah
        # berikutnya (TUNGGU_TEKS/CEK_TEKS) yang menyatakan gagal jujur.
        r = subprocess.run(["am", "start", "-a", "android.intent.action.VIEW",
                            "-d", url], capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            rish('am start -a android.intent.action.VIEW -d "%s"' % url)
        t0 = time.time()
        while time.time() - t0 < 6:
            time.sleep(POLL_UBAH)
            try:
                xml = self.dump(paksa=True)
            except Exception:
                continue
            if not self.target or 'package="%s"' % self.target in xml:
                return

    def tunggu_teks(self, teks, timeout):
        t0 = time.time()
        jeda = POLL_TUNGGU if self.mode == "server" else 8
        while True:
            if teks in self.dump(paksa=True):
                return time.time() - t0
            if time.time() - t0 >= timeout:
                raise MisiGagal('TUNGGU_TEKS "%s" timeout %sd' % (teks, timeout))
            time.sleep(jeda)

    def ketuk_teks(self, teks):
        xml = self.dump()
        titik = cari_titik(xml, teks)
        if not titik:
            xml = self.dump(paksa=True)
            titik = cari_titik(xml, teks)
        if not titik:
            raise MisiGagal('KETUK_TEKS "%s" tidak ditemukan di layar' % teks)
        self.klien.klik(*titik)
        self.tunggu_berubah(xml)
        return titik

    def tempel(self, teks):
        self.wajib_target("TEMPEL")
        subprocess.run(["termux-clipboard-set"], input=teks.encode(), timeout=15)
        kt = kolom_teks(self.dump(paksa=True))
        if not kt:
            raise MisiGagal("TEMPEL: kolom teks tidak ditemukan")
        lama = self.xml_terakhir
        self.klien.klik(*kt)
        self.tunggu_berubah(lama)
        time.sleep(0.4)
        kt = kolom_teks(self.dump(paksa=True)) or kt
        # Jalur A: chip clipboard di toolbar keyboard (Samsung Honeyboard) —
        # node berisi potongan awal isi clipboard. Terverifikasi manual 8 Okt
        # di kolom chat Glints; jalur menu tekan-lama justru GAGAL di kolom
        # pencarian Glints (uji advance/12, 8 Okt 12.08) sehingga chip dicoba
        # lebih dulu. Kolom masih kosong pada titik ini, jadi node yang cocok
        # dengan potongan awal teks pastilah chip-nya, bukan isi kolom.
        chip = cari_titik(self.xml_terakhir, teks[:15].strip()) if teks.strip() else None
        if chip:
            self.klien.klik(*chip)
            cara = "chip-clipboard-keyboard"
        else:
            # Jalur B: tekan-lama 800 ms (geser diam) lalu ketuk menu Tempel/Paste
            self.klien.geser(kt[0], kt[1], kt[0], kt[1], 800)
            time.sleep(0.6)
            xml = self.dump(paksa=True)
            tm = cari_titik(xml, "Tempel") or cari_titik(xml, "Paste")
            if tm:
                self.klien.klik(*tm)
                cara = "fokus+tekan-lama+menu"
            else:
                raise MisiGagal("TEMPEL: menu Tempel/Paste tidak muncul dan chip clipboard tidak terlihat")
        time.sleep(0.5)
        probe = teks.split(" ")[0]
        if probe not in self.dump(paksa=True):
            raise MisiGagal("TEMPEL tidak terbukti tampil di layar (%s)" % cara)
        return cara

    # -- mesin utama -----------------------------------------------------
    def jalankan(self, path):
        # Gerbang kaki kendali: server dulu, rish cadangan.
        try:
            self.klien.dump()
            self.mode = "server"
        except Exception:
            try:
                if "uid=2000" in rish("id"):
                    self.mode = "jembatan"
                else:
                    raise IOError("rish tanpa uid=2000")
            except Exception:
                self.catat("GAGAL", "server residen mati DAN rish/Shizuku mati — misi dibatalkan. "
                                    "Hidupkan Shizuku dari aplikasinya, atau periksa server residen.")
                return 1
        self.catat("MULAI", "tugas: %s (mode %s)" % (path, self.mode))
        t_misi = time.time()
        langkah = 0
        for baris in open(path, encoding="utf-8"):
            baris = baris.rstrip("\n").rstrip("\r")
            if not baris or baris.startswith("#"):
                continue
            if baris.startswith("TARGET"):
                self.target = baris.split(None, 1)[1].strip()
                self.catat("INFO", "target misi: %s" % self.target)
                continue
            langkah += 1
            cmd, _, sisa = baris.partition(" ")
            sisa = sisa.strip()
            t0 = time.time()
            try:
                if cmd == "BUKA":
                    self.buka(sisa); ket = sisa
                elif cmd == "TAUTAN":
                    self.tautan(sisa); ket = sisa
                elif cmd == "TUNGGU_TEKS":
                    bagian = sisa.rsplit(None, 1)
                    if len(bagian) == 2 and bagian[1].isdigit():
                        teks, to = bagian[0].strip('"'), int(bagian[1])
                    else:
                        teks, to = sisa.strip('"'), 30
                    dt = self.tunggu_teks(teks, to)
                    ket = '"%s" (tampil %.2fd)' % (teks, dt)
                elif cmd == "KETUK_TEKS":
                    titik = self.ketuk_teks(sisa.strip('"'))
                    ket = '"%s" @ %d %d' % (sisa.strip('"'), titik[0], titik[1])
                elif cmd == "KETUK":
                    self.wajib_target("KETUK")
                    x, y = map(int, sisa.split())
                    xml = self.dump(); self.klien.klik(x, y); self.tunggu_berubah(xml)
                    ket = sisa
                elif cmd == "GESER":
                    self.wajib_target("GESER")
                    a = list(map(int, sisa.split()))
                    ms = a[4] if len(a) > 4 else 300
                    xml = self.dump(); self.klien.geser(a[0], a[1], a[2], a[3], ms); self.tunggu_berubah(xml)
                    ket = sisa
                elif cmd == "KETIK":
                    # Mode server: urutan strategi per bukti perangkat —
                    # (1) input text via rish ke kolom yang sedang fokus
                    #     (terbukti di kolom pencarian Glints, 8 Okt pagi;
                    #     menu tempel & chip clipboard justru tidak muncul
                    #     di kolom itu), diverifikasi dari dump;
                    # (2) jalur TEMPEL (clipboard) sebagai cadangan umum.
                    # Mode jembatan: input text via rish seperti eksekutor lama.
                    if self.mode == "server":
                        teks_bersih = sisa.strip('"')
                        try:
                            rish('input text "%s"' % teks_bersih.replace(" ", "%s"))
                            time.sleep(0.5)
                            if teks_bersih.split(" ")[0] not in self.dump(paksa=True):
                                raise IOError("input-text tidak terbukti tampil di layar")
                            ket = "(%d karakter via rish input-text, terverifikasi)" % len(teks_bersih)
                        except Exception:
                            cara = self.tempel(teks_bersih)
                            ket = "(%d karakter via tempel-server: %s)" % (len(teks_bersih), cara)
                    else:
                        self.wajib_target("KETIK")
                        rish('input text "%s"' % sisa.strip('"').replace(" ", "%s"))
                        ket = "(%d karakter via rish)" % len(sisa.strip('"'))
                elif cmd == "TEMPEL":
                    cara = self.tempel(sisa.strip('"'))
                    ket = "(%d karakter via clipboard, %s, terverifikasi tampil)" % (len(sisa.strip('"')), cara)
                elif cmd == "TOMBOL":
                    self.wajib_target("TOMBOL")
                    if sisa in ("home", "back", "enter"):
                        xml = self.dump(); self.klien.tombol(sisa); self.tunggu_berubah(xml)
                    else:
                        kunci = {"wakeup": 224}.get(sisa, sisa)
                        rish("input keyevent %s" % kunci)
                    ket = sisa
                elif cmd == "JEDA":
                    time.sleep(float(sisa)); ket = "%sd" % sisa
                elif cmd == "FOTO":
                    keluar = rish("screencap -p /sdcard/md-foto.png; cp /sdcard/md-foto.png /sdcard/Download/%s" % (sisa or "foto.png"))
                    ket = sisa or "foto.png"
                elif cmd == "CEK_TEKS":
                    teks = sisa.strip('"')
                    if teks not in self.dump(paksa=True):
                        raise MisiGagal('CEK_TEKS "%s" TIDAK tampil' % teks)
                    ket = '"%s" tampil' % teks
                else:
                    raise MisiGagal("perintah tidak dikenal: %s" % cmd)
            except MisiGagal as g:
                self.catat("GAGAL", "langkah %d: %s — misi dihentikan." % (langkah, g))
                return 1
            except Exception as e:
                self.catat("GAGAL", "langkah %d: %s: %s — misi dihentikan." % (langkah, type(e).__name__, str(e)[:120]))
                return 1
            self.catat("OK", "%d %s %s (%d ms)" % (langkah, cmd, ket, (time.time() - t0) * 1000))
        self.catat("BERES", "tugas selesai: %s (%d langkah, total %.2f dtk, mode %s)"
                   % (path, langkah, time.time() - t_misi, self.mode))
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Pakai: misi-cepat.py <berkas.job>", file=sys.stderr)
        sys.exit(2)
    sys.exit(Runner().jalankan(sys.argv[1]))
