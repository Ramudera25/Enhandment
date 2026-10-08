#!/usr/bin/env python3
# misi-ad-hoc.py — Runner misi AD-HOC generik muse-droid (advance/16).
#
# Untuk tugas dadakan di aplikasi yang BELUM punya misi khusus (advance/12
# dkk.): agen menyusun berkas .job pendek dari hasil rekognisi, runner ini
# yang menjalankan perjalanan deterministiknya di dalam HP, dan titik
# keputusan (terutama langkah destruktif) tetap di tangan agen. Playbook
# lengkapnya ada di README.md folder ini.
#
# Hubungan dengan misi-cepat.py (advance/11): bahasa .job kompatibel
# (TARGET, BUKA, TAUTAN, TUNGGU_TEKS, KETUK_TEKS, KETUK, GESER, KETIK,
# TEMPEL, TOMBOL, JEDA, FOTO, CEK_TEKS) dan disiplinnya sama — satu proses
# persisten, penjaga TARGET, setiap langkah dicatat durasinya (ms).
# Dua direktif baru di sini:
#   - BUKA_APLIKASI <paket>  : buka aplikasi dari nama paket saja
#                              (resolve-activity), tanpa tahu activity-nya.
#   - ISI_TEKS <teks>        : fokus kolom lewat ketuk, lalu set-text pada
#                              node hidup lewat perintah ISI server pohon;
#                              cadangan: strategi KETIK lama (input text
#                              terverifikasi, lalu TEMPEL).
#
# Observasi BERLAPIS (yang utama didahulukan, mode tercatat di log MULAI):
#   1. mode pohon — server pohon aksesibilitas di aplikasi pendamping
#      (TCP 127.0.0.1:19102, protokol baris: PING/CARI/TEKS?/PAKET?/POHON/
#      ISI). Menjawab dari SALINAN pohon yang dipelihara dari peristiwa —
#      milidetik, tanpa dump UiAutomation.
#   2. mode dump  — server pohon tidak ada: dump uiautomator2
#      (127.0.0.1:9008/jsonrpc/0) per langkah, sama seperti misi-cepat.
#   3. mode jembatan — keduanya mati, rish/Shizuku hidup: dump lewat
#      `uiautomator dump` via rish + tangan `input` via rish. Lambat,
#      tapi jujur dan tetap berpenjaga TARGET.
# Tangan (klik/geser/tombol) lewat u2 bila hidup, selain itu rish.
#
# ATURAN KEBENARAN (DESAIN-V3-POHON-UI.md §4) — ditegakkan di kode, bukan
# sekadar ditulis:
#   - Setiap jawaban pohon membawa umur_ms + versi. Jawaban berumur
#     > 500 ms DITOLAK sebagai dasar langkah pengubah layar (koordinat
#     KETUK_TEKS dikueri ulang; tetap basi -> jatuh ke dump segar).
#   - Sesudah ketukan, keadaan baru hanya dipercaya bila VERSI pohon NAIK
#     dari versi pra-ketuk (gerbang versi di TUNGGU_TEKS/CEK_TEKS). Versi
#     tidak naik dalam 1,2 dtk -> verifikasi dialihkan ke dump cadangan.
#   - Langkah buta (KETUK/GESER/TOMBOL/ISI_TEKS/TEMPEL) dibatalkan jujur
#     bila paket depan != TARGET; paket dibaca murah dari PAKET? dan
#     dikonfirmasi dump pada langkah buta pertama.
#   - Langkah destruktif TIDAK diputuskan runner dari salinan pohon —
#     misi ad-hoc berhenti sebelum langkah itu; agen memutuskan dari
#     dump segar/screenshot (lihat README).
#   - Server pohon mati di tengah misi -> turun kelas dengan jujur ke
#     dump dan dicatat di log; tidak pura-pura cepat.
#
# Pakai (di Termux HP):  python3 misi-ad-hoc.py <berkas.job>
# Kebutuhan: server pohon pendamping (19102) dan/atau server u2 (9008);
# jembatan darurat: rish/Shizuku hidup.

import http.client
import json
import re
import socket
import subprocess
import sys
import time

U2_HOST, U2_PORT = "127.0.0.1", 9008
POHON_HOST, POHON_PORT = "127.0.0.1", 19102
POLL_TUNGGU = 0.25       # dtk — polling TUNGGU_TEKS mode pohon/dump
POLL_TUNGGU_JEMBATAN = 8  # dtk — polling mode jembatan (dump rish mahal)
POLL_UBAH = 0.15         # dtk — polling "keadaan berubah" sesudah tindakan
BATAS_UBAH = 1.2         # dtk — batas tunggu versi naik / hierarki berubah
BATAS_UMUR_MS = 500      # ms — aturan §4: jawaban pohon lebih tua = ditolak
COBA_BASI = 3            # kueri ulang maks. saat jawaban pohon basi
NODE_RE = re.compile(r"<node[^>]*>")
ATTR = lambda tag, nama: (re.search(nama + r'="([^"]*)"', tag) or [None, ""])[1]
BOUNDS_RE = re.compile(r"bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\"")
BOUNDS_STR_RE = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")
KODE_TOMBOL = {"home": "3", "back": "4", "enter": "66", "wakeup": "224"}


class KlienU2:
    """Satu koneksi HTTP persisten ke server residen u2 (keep-alive).
    Sama seperti misi-cepat — dump tidak pernah keluar dari proses ini
    tanpa perlu: yang diurai di sini, yang dipakai hanya bounds-nya."""

    def __init__(self):
        self.conn = None
        self.id = 0

    def _sambung(self):
        self.conn = http.client.HTTPConnection(U2_HOST, U2_PORT, timeout=8)

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


class KlienPohon:
    """Koneksi TCP persisten ke server pohon pendamping (port 19102).

    Protokol (patuh spesifikasi advance/15): permintaan satu baris UTF-8
    diakhiri \\n, balasan satu baris JSON.
      PING        -> {"pong":true,"versi":N,"umur_ms":N}
      CARI <teks> -> {"ada":bool,"x":int,"y":int,"bounds":"[..][..]",
                      "umur_ms":N,"versi":N}
      TEKS? <teks>-> {"ada":bool,"umur_ms":N,"versi":N}
      PAKET?      -> {"paket":"nama.paket","umur_ms":N}
      POHON       -> {"versi":N,"umur_ms":N,"nodes":[{t,d,k,b,klik,
                      edit,fokus}]}
      ISI <teks>  -> {"ok":bool,"sebab":"..."}  (set-text node fokus hidup)
    """

    def __init__(self):
        self.sock = None
        self.buf = b""

    def _sambung(self):
        self.sock = socket.create_connection((POHON_HOST, POHON_PORT), timeout=3)
        self.buf = b""

    def _tutup(self):
        try:
            if self.sock is not None:
                self.sock.close()
        except Exception:
            pass
        self.sock = None
        self.buf = b""

    def tanya(self, perintah):
        for percobaan in (1, 2):
            try:
                if self.sock is None:
                    self._sambung()
                self.sock.sendall((perintah + "\n").encode("utf-8"))
                while b"\n" not in self.buf:
                    potong = self.sock.recv(65536)
                    if not potong:
                        raise IOError("server pohon menutup koneksi")
                    self.buf += potong
                baris, self.buf = self.buf.split(b"\n", 1)
                return json.loads(baris.decode("utf-8"))
            except Exception:
                self._tutup()
                if percobaan == 2:
                    raise


def rish(perintah):
    import os
    env = dict(os.environ)
    env["RISH_APPLICATION_ID"] = "com.termux"
    return subprocess.run([os.path.expanduser("~/rish"), "-c", perintah],
                          env=env, capture_output=True, text=True, timeout=30).stdout


def cari_titik(xml, teks):
    """Kueri terarah atas dump XML: titik tengah node pertama yang
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
    """Titik tengah kolom teks (EditText / node terfokus) pertama di dump."""
    for m in NODE_RE.finditer(xml):
        tag = m.group(0)
        if "EditText" in ATTR(tag, "class") or ATTR(tag, "focused") == "true":
            b = BOUNDS_RE.search(tag)
            if b:
                x1, y1, x2, y2 = map(int, b.groups())
                return (x1 + x2) // 2, (y1 + y2) // 2
    return None


def titik_dari_bounds(teks_bounds):
    """"[x1,y1][x2,y2]" (format bounds server pohon) -> titik tengah."""
    m = BOUNDS_STR_RE.match(teks_bounds or "")
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


class MisiGagal(Exception):
    pass


class Runner:
    def __init__(self):
        self.klien = KlienU2()
        self.pohon = KlienPohon()
        self.target = ""
        self.mode = None        # "pohon" | "dump" | "jembatan"
        self.tangan = None      # "u2" | "rish"
        self.pohon_hidup = False
        self.u2_hidup = False
        self.versi = None       # versi salinan pohon terakhir yang terlihat
        self.gerbang_versi = None  # versi pra-ketuk yang harus DILAMPAUI
        self.buta_pertama = True   # langkah buta pertama dikonfirmasi dump
        self.xml_terakhir = ""
        self.t_xml = 0.0

    # -- infrastruktur -------------------------------------------------
    def catat(self, status, pesan):
        print("[%s] %s %s" % (time.strftime("%H:%M:%S"), status, pesan), flush=True)

    def _pohon(self, perintah):
        """Satu kueri ke server pohon; None bila pohon tidak menjawab
        (turun kelas dicatat sekali, sesudahnya observasi murni dump)."""
        if not self.pohon_hidup:
            return None
        try:
            j = self.pohon.tanya(perintah)
        except Exception:
            self.pohon_hidup = False
            self.catat("INFO", "server pohon tidak menjawab — observasi jatuh "
                               "ke dump (turun kelas jujur, mode pohon berakhir)")
            return None
        v = j.get("versi")
        if isinstance(v, int):
            self.versi = v
        return j

    def dump(self, paksa=False):
        """Dump UiAutomation — kebenaran dasar & cadangan semua mode.
        Lewat u2 bila hidup; mode jembatan: `uiautomator dump` via rish."""
        if not paksa and self.xml_terakhir and time.time() - self.t_xml < 0.3:
            return self.xml_terakhir
        if self.u2_hidup:
            xml = self.klien.dump()
        else:
            xml = rish("uiautomator dump /sdcard/md-adhoc-dump.xml "
                       ">/dev/null 2>&1; cat /sdcard/md-adhoc-dump.xml")
            if not xml or "<?xml" not in xml:
                raise IOError("dump via rish tidak valid")
        self.xml_terakhir = xml
        self.t_xml = time.time()
        return xml

    # -- tangan ----------------------------------------------------------
    def tangan_klik(self, x, y):
        if self.tangan == "u2":
            self.klien.klik(x, y)
        else:
            rish("input tap %d %d" % (x, y))

    def tangan_geser(self, x1, y1, x2, y2, ms):
        if self.tangan == "u2":
            self.klien.geser(x1, y1, x2, y2, ms)
        else:
            rish("input swipe %d %d %d %d %d" % (x1, y1, x2, y2, ms))

    def tangan_tombol(self, nama):
        if self.tangan == "u2" and nama in ("home", "back", "enter"):
            self.klien.tombol(nama)
        else:
            rish("input keyevent %s" % KODE_TOMBOL.get(nama, nama))

    # -- observasi terarah ------------------------------------------------
    def paket_depan(self):
        """Paket jendela depan: murah dari PAKET? (mode pohon), selain
        itu dari node akar dump."""
        if self.mode == "pohon":
            j = self._pohon("PAKET?")
            if j is not None:
                return j.get("paket") or ""
        m = re.search(r'package="([^"]+)"', self.dump(paksa=True))
        return m.group(1) if m else ""

    def node_semua(self):
        """Daftar node seragam {teks, desc, kelas, klik, edit, fokus,
        titik} — dari POHON (mode pohon) atau diurai dari dump."""
        if self.mode == "pohon":
            j = self._pohon("POHON")
            if j is not None:
                hasil = []
                for n in j.get("nodes") or []:
                    hasil.append({
                        "teks": n.get("t") or "", "desc": n.get("d") or "",
                        "kelas": n.get("k") or "", "klik": bool(n.get("klik")),
                        "edit": bool(n.get("edit")), "fokus": bool(n.get("fokus")),
                        "titik": titik_dari_bounds(n.get("b"))})
                if hasil:
                    return hasil
        hasil = []
        for m in NODE_RE.finditer(self.dump(paksa=True)):
            tag = m.group(0)
            b = BOUNDS_RE.search(tag)
            titik = None
            if b:
                x1, y1, x2, y2 = map(int, b.groups())
                titik = (x1 + x2) // 2, (y1 + y2) // 2
            hasil.append({
                "teks": ATTR(tag, "text"), "desc": ATTR(tag, "content-desc"),
                "kelas": ATTR(tag, "class"),
                "klik": ATTR(tag, "clickable") == "true",
                "edit": "EditText" in ATTR(tag, "class"),
                "fokus": ATTR(tag, "focused") == "true", "titik": titik})
        return hasil

    def cari_titik_teks(self, teks):
        """Cari titik ketuk untuk `teks` -> (x, y, sumber) | None.
        Mode pohon: CARI didahulukan, TETAPI jawaban berumur > 500 ms
        ditolak untuk tindakan (aturan §4) — dikueri ulang; tetap basi
        atau tidak ada -> dump segar yang memutuskan."""
        if self.mode == "pohon":
            for _ in range(COBA_BASI):
                j = self._pohon("CARI " + teks)
                if j is None:
                    break
                if not j.get("ada"):
                    break  # salinan bisa terlewat peristiwa: dump memastikan
                if j.get("umur_ms", 10 ** 9) <= BATAS_UMUR_MS:
                    titik = titik_dari_bounds(j.get("bounds"))
                    if titik is None and "x" in j and "y" in j:
                        titik = (j["x"], j["y"])
                    if titik:
                        return titik[0], titik[1], "pohon"
                    break
                time.sleep(0.1)  # basi: beri waktu salinan menyegar, kueri lagi
        titik = cari_titik(self.dump(paksa=True), teks)
        if titik:
            return titik[0], titik[1], "dump"
        return None

    # -- gerbang kebenaran --------------------------------------------------
    def sebelum_tindakan(self):
        """Snapshot pra-tindakan: tetapkan gerbang versi (mode pohon)
        atau simpan dump lama (mode lain) untuk tunggu_berubah."""
        if self.mode == "pohon":
            if self.versi is None:
                self._pohon("PING")
            self.gerbang_versi = self.versi
            return None
        try:
            return self.dump()
        except Exception:
            return None

    def tunggu_berubah(self, xml_lama=None):
        """Sesudah tindakan: tunggu keadaan BARU terbukti.
        Mode pohon: versi salinan harus NAIK dari gerbang (<= 1,2 dtk);
        tidak naik -> dump disegarkan sebagai pegangan verifikasi
        berikutnya dan dicatat (bukan diam-diam dipercaya).
        Mode lain: hierarki dump harus berbeda dari sebelum tindakan."""
        if self.mode == "pohon":
            if self.gerbang_versi is None:
                return
            t0 = time.time()
            while time.time() - t0 < BATAS_UBAH:
                time.sleep(POLL_UBAH)
                self._pohon("PING")
                if self.versi is not None and self.versi > self.gerbang_versi:
                    self.gerbang_versi = None
                    return
            self.gerbang_versi = None
            try:
                self.dump(paksa=True)
                self.catat("INFO", "versi pohon tidak naik dalam %.1f dtk — "
                                   "verifikasi berikutnya dialihkan ke dump" % BATAS_UBAH)
            except Exception:
                pass
            return
        if xml_lama is None:
            return
        t0 = time.time()
        while time.time() - t0 < BATAS_UBAH:
            time.sleep(POLL_UBAH)
            try:
                if self.dump(paksa=True) != xml_lama:
                    return
            except Exception:
                return

    def cek_target(self):
        if not self.target:
            return True
        try:
            if self.paket_depan() != self.target:
                return False
        except Exception:
            return False
        if self.buta_pertama:
            # Aturan §4: guard dari salinan dikonfirmasi dump pada
            # langkah buta pertama misi ini.
            self.buta_pertama = False
            if self.mode == "pohon" and self.u2_hidup:
                try:
                    return 'package="%s"' % self.target in self.dump(paksa=True)
                except Exception:
                    return False
        return True

    def wajib_target(self, cmd):
        if not self.cek_target():
            raise MisiGagal("TARGET %s tidak di layar depan — %s dibatalkan demi keamanan"
                            % (self.target, cmd))

    # -- langkah: buka ---------------------------------------------------
    def _tunggu_paket(self, paket, batas=6):
        t0 = time.time()
        while time.time() - t0 < batas:
            time.sleep(POLL_UBAH)
            try:
                if self.paket_depan() == paket:
                    return True
            except Exception:
                continue
        return False

    def buka_aplikasi(self, paket):
        # resolve-activity lewat rish (shell uid=2000 punya `cmd package`);
        # keluaran --brief: baris terakhir berbentuk "paket/.Activity".
        komponen = None
        keluar = rish("cmd package resolve-activity --brief %s" % paket)
        for baris in reversed((keluar or "").splitlines()):
            baris = baris.strip()
            if "/" in baris and " " not in baris:
                komponen = baris
                break
        self.sebelum_tindakan()
        if komponen:
            r = subprocess.run(["am", "start", "-n", komponen],
                               capture_output=True, text=True, timeout=20)
            if r.returncode != 0:
                rish("am start -n %s" % komponen)
        else:
            # Cadangan: monkey meluncurkan activity LAUNCHER paket.
            rish("monkey -p %s -c android.intent.category.LAUNCHER 1" % paket)
        if not self._tunggu_paket(paket):
            raise MisiGagal("BUKA_APLIKASI %s: paket tidak tampil di depan "
                            "dalam 6 dtk (resolve: %s)" % (paket, komponen or "-"))
        self.tunggu_berubah()
        return komponen or "monkey"

    def buka(self, sisa):
        # Kompatibel misi-cepat: komponen "paket/.Activity" atau aksi intent.
        self.sebelum_tindakan()
        if "/" in sisa:
            r = subprocess.run(["am", "start", "-n", sisa],
                               capture_output=True, text=True, timeout=20)
            if r.returncode != 0 and self.mode == "jembatan":
                rish("am start -n %s" % sisa)
        else:
            subprocess.run(["am", "start", "-a", sisa],
                           capture_output=True, text=True, timeout=20)
        sasaran = self.target or sisa.split("/")[0]
        self._tunggu_paket(sasaran)
        self.tunggu_berubah()

    def tautan(self, url):
        # Deep link: intent VIEW (sama seperti misi-cepat advance/12).
        # Bila URL tidak diklaim aplikasi target, tunggu habis tanpa tampil
        # — langkah berikutnya (TUNGGU_TEKS/CEK_TEKS) yang gagal jujur.
        self.sebelum_tindakan()
        r = subprocess.run(["am", "start", "-a", "android.intent.action.VIEW",
                            "-d", url], capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            rish('am start -a android.intent.action.VIEW -d "%s"' % url)
        if self.target:
            self._tunggu_paket(self.target)
        self.tunggu_berubah()

    # -- langkah: tunggu & cek --------------------------------------------
    def tunggu_teks(self, teks, timeout):
        t0 = time.time()
        if self.mode == "pohon":
            cek_dump_terakhir = 0.0
            while True:
                if not self.pohon_hidup:
                    break  # pohon mati di tengah tunggu: cabang dump di bawah
                j = self._pohon("TEKS? " + teks)
                if j is not None and j.get("ada"):
                    v = j.get("versi")
                    # Gerbang versi: "ada" dari salinan pra-ketuk TIDAK
                    # dihitung — versi harus sudah melampaui gerbang.
                    if self.gerbang_versi is None or \
                            (v is not None and v > self.gerbang_versi):
                        self.gerbang_versi = None
                        return time.time() - t0
                if self.gerbang_versi is not None and \
                        time.time() - cek_dump_terakhir > BATAS_UBAH:
                    # Versi macet: dump cadangan yang memutuskan (§4).
                    cek_dump_terakhir = time.time()
                    try:
                        if teks in self.dump(paksa=True):
                            self.gerbang_versi = None
                            self.catat("INFO", 'TUNGGU_TEKS "%s": terbukti via '
                                               'dump (versi pohon macet)' % teks)
                            return time.time() - t0
                    except Exception:
                        pass
                if time.time() - t0 >= timeout:
                    raise MisiGagal('TUNGGU_TEKS "%s" timeout %sd' % (teks, timeout))
                time.sleep(POLL_TUNGGU)
        jeda = POLL_TUNGGU if self.mode == "dump" else POLL_TUNGGU_JEMBATAN
        while True:
            if teks in self.dump(paksa=True):
                return time.time() - t0
            if time.time() - t0 >= timeout:
                raise MisiGagal('TUNGGU_TEKS "%s" timeout %sd' % (teks, timeout))
            time.sleep(jeda)

    def cek_teks(self, teks):
        """-> sumber bukti ("pohon"/"dump"). Gagal = MisiGagal jujur."""
        if self.mode == "pohon":
            for _ in range(COBA_BASI):
                j = self._pohon("TEKS? " + teks)
                if j is None:
                    break
                if j.get("umur_ms", 10 ** 9) > BATAS_UMUR_MS:
                    time.sleep(0.1)  # basi: jangan putuskan, kueri lagi
                    continue
                v = j.get("versi")
                if self.gerbang_versi is not None and \
                        not (v is not None and v > self.gerbang_versi):
                    time.sleep(0.1)  # masih salinan pra-ketuk: belum sah
                    continue
                if j.get("ada"):
                    self.gerbang_versi = None
                    return "pohon"
                break  # "tidak ada" dari salinan segar: dump memastikan
        if teks in self.dump(paksa=True):
            return "dump"
        raise MisiGagal('CEK_TEKS "%s" TIDAK tampil' % teks)

    # -- langkah: ketuk & isi ----------------------------------------------
    def ketuk_teks(self, teks):
        hasil = self.cari_titik_teks(teks)
        if not hasil:
            raise MisiGagal('KETUK_TEKS "%s" tidak ditemukan di layar' % teks)
        x, y, sumber = hasil
        xml_lama = self.sebelum_tindakan()
        self.tangan_klik(x, y)
        self.tunggu_berubah(xml_lama)
        return (x, y), sumber

    def isi_teks(self, teks):
        self.wajib_target("ISI_TEKS")
        if self.mode == "pohon":
            # Fokus kolom dulu lewat ketuk (bila belum ada kolom terfokus):
            # kata ISI server pohon bekerja pada node edit yang HIDUP.
            nodes = self.node_semua()
            fokus = next((n for n in nodes if n["edit"] and n["fokus"] and n["titik"]), None)
            if not fokus:
                calon = next((n for n in nodes if n["edit"] and n["titik"]), None)
                if calon:
                    xml_lama = self.sebelum_tindakan()
                    self.tangan_klik(*calon["titik"])
                    self.tunggu_berubah(xml_lama)
            j = self._pohon("ISI " + teks)
            if j is not None and j.get("ok"):
                # Verifikasi dari keadaan segar: kata pertama harus tampil.
                # ISI mengaku ok tapi tak terlihat = berhenti jujur, JANGAN
                # jatuh ke KETIK (risiko mengetik ganda).
                probe = teks.split(" ")[0]
                try:
                    self.tunggu_teks(probe, 3)
                except MisiGagal:
                    raise MisiGagal("ISI mengaku berhasil tapi teks tidak "
                                    "terlihat — berhenti jujur agar tidak "
                                    "mengetik ganda")
                return "ISI server pohon, terverifikasi"
            sebab = (j or {}).get("sebab") or "server pohon tidak menjawab"
            self.catat("INFO", "ISI via pohon gagal (%s) — jatuh ke KETIK lama" % sebab)
        return self.ketik(teks)

    def ketik(self, teks):
        # Strategi warisan misi-cepat (bukti perangkat 8 Okt):
        # (1) input text via rish ke kolom fokus, diverifikasi dari layar;
        # (2) TEMPEL clipboard sebagai cadangan. Mode jembatan: langsung rish.
        if self.mode in ("pohon", "dump"):
            try:
                rish('input text "%s"' % teks.replace(" ", "%s"))
                time.sleep(0.5)
                probe = teks.split(" ")[0]
                terbukti = False
                if self.mode == "pohon":
                    j = self._pohon("TEKS? " + probe)
                    terbukti = bool(j and j.get("ada"))
                if not terbukti:
                    terbukti = probe in self.dump(paksa=True)
                if not terbukti:
                    raise IOError("input-text tidak terbukti tampil di layar")
                return "(%d karakter via rish input-text, terverifikasi)" % len(teks)
            except MisiGagal:
                raise
            except Exception:
                cara = self.tempel(teks)
                return "(%d karakter via tempel: %s)" % (len(teks), cara)
        self.wajib_target("KETIK")
        rish('input text "%s"' % teks.replace(" ", "%s"))
        return "(%d karakter via rish)" % len(teks)

    def tempel(self, teks):
        self.wajib_target("TEMPEL")
        subprocess.run(["termux-clipboard-set"], input=teks.encode(), timeout=15)
        nodes = self.node_semua()
        kolom = next((n for n in nodes if n["edit"] and n["titik"]), None)
        if not kolom:
            titik = kolom_teks(self.dump(paksa=True))
            if not titik:
                raise MisiGagal("TEMPEL: kolom teks tidak ditemukan")
            kolom = {"titik": titik}
        xml_lama = self.sebelum_tindakan()
        self.tangan_klik(*kolom["titik"])
        self.tunggu_berubah(xml_lama)
        time.sleep(0.4)
        # Segarkan titik kolom: keyboard bisa menggeser tata letak.
        nodes = self.node_semua()
        kolom2 = next((n for n in nodes if n["edit"] and n["titik"]), None)
        if kolom2:
            kolom = kolom2
        # Jalur A: chip clipboard di toolbar keyboard (node berisi potongan
        # awal isi clipboard) — terverifikasi manual 8 Okt di Glints lewat
        # misi-cepat. Kolom masih kosong di titik ini, jadi node yang cocok
        # dengan potongan awal teks pastilah chip-nya, bukan isi kolom.
        chip = self.cari_titik_teks(teks[:15].strip()) if teks.strip() else None
        if chip:
            self.tangan_klik(chip[0], chip[1])
            cara = "chip-clipboard-keyboard"
        else:
            # Jalur B: tekan-lama 800 ms (geser diam) lalu menu Tempel/Paste.
            self.tangan_geser(kolom["titik"][0], kolom["titik"][1],
                              kolom["titik"][0], kolom["titik"][1], 800)
            time.sleep(0.6)
            tm = self.cari_titik_teks("Tempel") or self.cari_titik_teks("Paste")
            if tm:
                self.tangan_klik(tm[0], tm[1])
                cara = "fokus+tekan-lama+menu"
            else:
                raise MisiGagal("TEMPEL: menu Tempel/Paste tidak muncul dan "
                                "chip clipboard tidak terlihat")
        time.sleep(0.5)
        probe = teks.split(" ")[0]
        terbukti = False
        if self.mode == "pohon":
            j = self._pohon("TEKS? " + probe)
            terbukti = bool(j and j.get("ada"))
        if not terbukti:
            terbukti = probe in self.dump(paksa=True)
        if not terbukti:
            raise MisiGagal("TEMPEL tidak terbukti tampil di layar (%s)" % cara)
        return cara

    # -- mesin utama ---------------------------------------------------------
    def jalankan(self, path):
        # Gerbang kaki kendali: pohon dulu, u2 berikutnya, rish terakhir.
        try:
            j = self.pohon.tanya("PING")
            if j and j.get("pong"):
                self.pohon_hidup = True
                v = j.get("versi")
                if isinstance(v, int):
                    self.versi = v
        except Exception:
            self.pohon_hidup = False
        try:
            self.klien.dump()
            self.u2_hidup = True
        except Exception:
            self.u2_hidup = False
        if self.pohon_hidup:
            self.mode = "pohon"
        elif self.u2_hidup:
            self.mode = "dump"
        else:
            try:
                if "uid=2000" in rish("id"):
                    self.mode = "jembatan"
                else:
                    raise IOError("rish tanpa uid=2000")
            except Exception:
                self.catat("GAGAL", "server pohon mati DAN server u2 mati DAN "
                                    "rish/Shizuku mati — misi dibatalkan. Hidupkan "
                                    "Shizuku dari aplikasinya, atau periksa "
                                    "pendamping & server residen.")
                return 1
        self.tangan = "u2" if self.u2_hidup else "rish"
        self.catat("MULAI", "tugas: %s (mode %s, tangan %s%s)" % (
            path, self.mode, self.tangan,
            ", pohon v%s" % self.versi if self.mode == "pohon" else ""))
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
                if cmd == "BUKA_APLIKASI":
                    ket = self.buka_aplikasi(sisa)
                elif cmd == "BUKA":
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
                    titik, sumber = self.ketuk_teks(sisa.strip('"'))
                    ket = '"%s" @ %d %d via %s' % (sisa.strip('"'), titik[0], titik[1], sumber)
                elif cmd == "ISI_TEKS":
                    ket = self.isi_teks(sisa.strip('"'))
                elif cmd == "KETIK":
                    ket = self.ketik(sisa.strip('"'))
                elif cmd == "TEMPEL":
                    cara = self.tempel(sisa.strip('"'))
                    ket = "(%d karakter via clipboard, %s, terverifikasi tampil)" \
                          % (len(sisa.strip('"')), cara)
                elif cmd == "KETUK":
                    self.wajib_target("KETUK")
                    x, y = map(int, sisa.split())
                    xml_lama = self.sebelum_tindakan()
                    self.tangan_klik(x, y)
                    self.tunggu_berubah(xml_lama)
                    ket = sisa
                elif cmd == "GESER":
                    self.wajib_target("GESER")
                    a = list(map(int, sisa.split()))
                    ms = a[4] if len(a) > 4 else 300
                    xml_lama = self.sebelum_tindakan()
                    self.tangan_geser(a[0], a[1], a[2], a[3], ms)
                    self.tunggu_berubah(xml_lama)
                    ket = sisa
                elif cmd == "TOMBOL":
                    self.wajib_target("TOMBOL")
                    xml_lama = self.sebelum_tindakan()
                    self.tangan_tombol(sisa)
                    self.tunggu_berubah(xml_lama)
                    ket = sisa
                elif cmd == "JEDA":
                    time.sleep(float(sisa)); ket = "%sd" % sisa
                elif cmd == "FOTO":
                    rish("screencap -p /sdcard/md-foto.png; "
                         "cp /sdcard/md-foto.png /sdcard/Download/%s"
                         % (sisa or "foto.png"))
                    ket = sisa or "foto.png"
                elif cmd == "CEK_TEKS":
                    teks = sisa.strip('"')
                    sumber = self.cek_teks(teks)
                    ket = '"%s" tampil (via %s)' % (teks, sumber)
                else:
                    raise MisiGagal("perintah tidak dikenal: %s" % cmd)
            except MisiGagal as g:
                self.catat("GAGAL", "langkah %d: %s — misi dihentikan." % (langkah, g))
                return 1
            except Exception as e:
                self.catat("GAGAL", "langkah %d: %s: %s — misi dihentikan."
                           % (langkah, type(e).__name__, str(e)[:120]))
                return 1
            self.catat("OK", "%d %s %s (%d ms)" % (langkah, cmd, ket,
                                                  (time.time() - t0) * 1000))
        self.catat("BERES", "tugas selesai: %s (%d langkah, total %.2f dtk, "
                            "mode %s, tangan %s)"
                   % (path, langkah, time.time() - t_misi, self.mode, self.tangan))
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Pakai: misi-ad-hoc.py <berkas.job>", file=sys.stderr)
        sys.exit(2)
    sys.exit(Runner().jalankan(sys.argv[1]))
