// LayananAkses.kt — layanan aksesibilitas pendamping muse-droid (V4.0).
// Tugasnya OBSERVASI: memelihara salinan pohon UI jendela aktif di memori,
// diperbarui dari peristiwa aksesibilitas (debounce), lalu menyajikannya
// lewat socket lokal 127.0.0.1:19102 agar agen bisa bertanya "di mana teks
// X" dalam milidetik — tanpa dump UiAutomation yang mahal (0,5–0,95 dtk).
//
// Protokol (satu baris UTF-8 per koneksi, balasan satu baris JSON):
//   PING          -> {"pong":true,"versi":N,"umur_ms":N}
//   PAKET?        -> {"paket":"nama.paket","umur_ms":N}
//   TEKS? <teks>  -> {"ada":bool,"umur_ms":N,"versi":N}
//   CARI <teks>   -> {"ada":true,"x":N,"y":N,"bounds":"[x1,y1][x2,y2]",
//                     "umur_ms":N,"versi":N} | {"ada":false,...}
//   POHON         -> {"versi":N,"umur_ms":N,"nodes":[{t,d,k,b,klik,edit,fokus}]}
//   ISI <teks>    -> {"ok":bool,"sebab":"..."}  (set-text pada node edit
//                     yang sedang fokus — dikerjakan pada node HIDUP,
//                     bukan pada salinan, sesuai aturan kebenaran desain;
//                     V4.1: menunggu kolom fokus muncul maks ~600 ms dulu)
//   KETUK x y     -> {"ok":bool,"versi_sblm":N,"versi_ssdh":N,"naik":bool,
//   TAHAN x y        "latensi_ms":N}  (gestur dispatchGesture V4.1 —
//   GESER x1 y1 x2 y2 [ms]   tangan di proses yang sama dengan mata;
//                     balasan menunggu versi salinan NAIK (verifikasi
//                     bawaan, batas 1,2 dtk) sebelum dikirim)
//   GLOBAL BACK|HOME|RECENTS -> sama (performGlobalAction)
//   TOMBOL <kode>  -> {"ok":bool,"kode":N,"versi_sblm":N,"versi_ssdh":N,
//                     "naik":bool,"latensi_ms":N[, "sebab":"..."]}
//                     V4.2: 224 (WAKEUP) via wakelock ACQUIRE_CAUSES_WAKEUP
//                     (tanpa Shizuku/rish); 3 (HOME) & 4 (BACK) via aksi
//                     global; kode lain jujur ditolak (butuh injeksi input).
//
// Aturan kebenaran (DESAIN-V3-POHON-UI.md §4): umur salinan selalu
// dilaporkan; konsumen menolak jawaban basi untuk langkah pengubah layar;
// langkah destruktif tidak pernah diputuskan dari salinan. Server ini
// hanya ada selama layanan aksesibilitas aktif — ketiadaannya adalah
// sinyal turun-kelas yang jujur ke mode dump.
package id.musedroid.pendamping

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.graphics.Rect
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.os.SystemClock
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.InetAddress
import java.net.ServerSocket
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread
import org.json.JSONArray
import org.json.JSONObject

object PohonUI {
    data class Simpul(
        val paket: String, val kelas: String, val teks: String, val desc: String,
        val x1: Int, val y1: Int, val x2: Int, val y2: Int,
        val klik: Boolean, val edit: Boolean, val fokus: Boolean
    ) {
        val cx: Int get() = (x1 + x2) / 2
        val cy: Int get() = (y1 + y2) / 2
    }

    @Volatile var versi: Long = 0
    @Volatile var stempelMs: Long = 0
    @Volatile var paketDepan: String = ""
    @Volatile var simpul: List<Simpul> = emptyList()

    fun umurMs(): Long =
        if (stempelMs == 0L) -1 else SystemClock.uptimeMillis() - stempelMs
}

class LayananAkses : AccessibilityService() {

    companion object {
        const val PORT_POHON = 19102
        @Volatile var aktif: Boolean = false
        @Volatile var instans: LayananAkses? = null
    }

    private val penangan = Handler(Looper.getMainLooper())
    private val tugasSegarkan = Runnable { segarkan() }
    @Volatile private var serverJalan = false

    override fun onServiceConnected() {
        super.onServiceConnected()
        serviceInfo = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED or
                AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED or
                AccessibilityEvent.TYPE_VIEW_FOCUSED or
                AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED or
                AccessibilityEvent.TYPE_VIEW_CLICKED or
                AccessibilityEvent.TYPE_VIEW_SCROLLED
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            flags = AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or
                AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS or
                AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS
            // Kemampuan gestur (CAPABILITY_CAN_PERFORM_GESTURES) TIDAK diset
            // di sini — properti itu hanya-baca dari Kotlin. Sumber otoritatifnya
            // res/xml/layanan_akses.xml: android:canPerformGestures="true".
            notificationTimeout = 40
        }
        instans = this
        aktif = true
        if (!serverJalan) {
            serverJalan = true
            thread { penyaji() }
        }
        segarkan()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Debounce 40 ms: peristiwa beruntun (animasi, daftar bergeser)
        // diringkas jadi satu penyegaran.
        penangan.removeCallbacks(tugasSegarkan)
        penangan.postDelayed(tugasSegarkan, 40)
    }

    override fun onInterrupt() { /* tidak ada umpan balik yang perlu diputus */ }

    override fun onUnbind(intent: android.content.Intent?): Boolean {
        aktif = false
        instans = null
        serverJalan = false
        return super.onUnbind(intent)
    }

    // ---- penyegaran salinan ----

    private fun segarkan() {
        val akar = try { rootInActiveWindow } catch (e: Exception) { null } ?: return
        val hasil = ArrayList<PohonUI.Simpul>(512)
        val tumpukan = ArrayDeque<AccessibilityNodeInfo>()
        tumpukan.addLast(akar)
        var hitung = 0
        while (tumpukan.isNotEmpty() && hitung < 5000) {
            val n = tumpukan.removeLast()
            hitung++
            try {
                val r = Rect()
                n.getBoundsInScreen(r)
                hasil.add(
                    PohonUI.Simpul(
                        paket = n.packageName?.toString() ?: "",
                        kelas = n.className?.toString() ?: "",
                        teks = n.text?.toString() ?: "",
                        desc = n.contentDescription?.toString() ?: "",
                        x1 = r.left, y1 = r.top, x2 = r.right, y2 = r.bottom,
                        klik = n.isClickable, edit = n.isEditable, fokus = n.isFocused
                    )
                )
                for (i in n.childCount - 1 downTo 0) {
                    val anak = n.getChild(i)
                    if (anak != null) tumpukan.addLast(anak)
                }
            } catch (e: Exception) {
                // Node berubah di tengah jalan — lewati, salinan berikutnya menutupinya.
            }
        }
        PohonUI.simpul = hasil
        PohonUI.paketDepan = akar.packageName?.toString() ?: ""
        PohonUI.stempelMs = SystemClock.uptimeMillis()
        PohonUI.versi++
    }

    // ---- aksi set-text pada node HIDUP (bukan salinan) ----

    fun isiTeks(teks: String): JSONObject {
        val out = JSONObject()
        // V4.1: kolom kerap baru memperoleh fokus beberapa ratus milidetik
        // sesudah layarnya tampil (kasus misi Pengaturan 8 Okt — ISI kalah
        // balapan fokus lalu jatuh ke input-text). Tunggu kolom FOKUS
        // muncul maks ~600 ms (5 percobaan, jeda 120 ms) sebelum menyerah
        // ke kolom cadangan yang tidak fokus.
        var sasaran: AccessibilityNodeInfo? = null
        var cadangan: AccessibilityNodeInfo? = null
        var tungguMs = 0L
        var percobaan = 0
        while (true) {
            val akar = try { rootInActiveWindow } catch (e: Exception) { null }
                ?: return out.put("ok", false).put("sebab", "tidak ada jendela aktif")
            sasaran = null
            val tumpukan = ArrayDeque<AccessibilityNodeInfo>()
            tumpukan.addLast(akar)
            var hitung = 0
            while (tumpukan.isNotEmpty() && hitung < 5000) {
                val n = tumpukan.removeLast()
                hitung++
                try {
                    if (n.isEditable) {
                        if (n.isFocused) { sasaran = n; break }
                        if (cadangan == null) cadangan = n
                    }
                    for (i in n.childCount - 1 downTo 0) {
                        val anak = n.getChild(i)
                        if (anak != null) tumpukan.addLast(anak)
                    }
                } catch (e: Exception) { /* lewati */ }
            }
            if (sasaran != null || percobaan >= 4) break
            percobaan++
            Thread.sleep(120)
            tungguMs += 120
        }
        val node = sasaran ?: cadangan
            ?: return out.put("ok", false).put("sebab", "tidak ada kolom edit di jendela aktif")
        val args = Bundle()
        args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, teks)
        val ok = try { node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args) }
            catch (e: Exception) { false }
        if (ok) segarkan()
        return out.put("ok", ok).put("tunggu_ms", tungguMs)
            .put("sebab", if (ok) "" else "ACTION_SET_TEXT ditolak node")
    }

    // ---- gestur (V4.1): tangan di proses yang sama dengan mata ----
    // dispatchGesture dieksekusi sistem atas nama layanan; balasan socket
    // menunggu versi salinan NAIK (bukti layar berubah) maks 1,2 dtk, jadi
    // satu perintah = aksi + verifikasi dalam satu perjalanan socket.

    private fun tungguVersiNaik(versiSebelum: Long, batasMs: Long = 1200): Boolean {
        val mulai = SystemClock.uptimeMillis()
        while (SystemClock.uptimeMillis() - mulai < batasMs) {
            if (PohonUI.versi > versiSebelum) return true
            Thread.sleep(25)
        }
        return PohonUI.versi > versiSebelum
    }

    private fun lakukanGestur(bangun: () -> GestureDescription): JSONObject {
        val out = JSONObject()
        val versiSebelum = PohonUI.versi
        val mulai = SystemClock.uptimeMillis()
        val gerbang = CountDownLatch(1)
        var hasilKirim = false
        penangan.post {
            try {
                hasilKirim = dispatchGesture(bangun(), object : GestureResultCallback() {
                    override fun onCompleted(g: GestureDescription?) { gerbang.countDown() }
                    override fun onCancelled(g: GestureDescription?) { gerbang.countDown() }
                }, null)
            } catch (e: Exception) {
                gerbang.countDown()
            }
        }
        gerbang.await(900, TimeUnit.MILLISECONDS)
        val naik = tungguVersiNaik(versiSebelum)
        val lat = SystemClock.uptimeMillis() - mulai
        return out.put("ok", hasilKirim).put("versi_sblm", versiSebelum)
            .put("versi_ssdh", PohonUI.versi).put("naik", naik)
            .put("latensi_ms", lat)
    }

    fun gesturKetuk(x: Int, y: Int): JSONObject = lakukanGestur {
        val jalur = Path().apply { moveTo(x.toFloat(), y.toFloat()) }
        GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(jalur, 0, 80)).build()
    }

    fun gesturTahan(x: Int, y: Int): JSONObject = lakukanGestur {
        val jalur = Path().apply { moveTo(x.toFloat(), y.toFloat()) }
        GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(jalur, 0, 650)).build()
    }

    fun gesturGeser(x1: Int, y1: Int, x2: Int, y2: Int, durasiMs: Long): JSONObject =
        lakukanGestur {
            val jalur = Path().apply {
                moveTo(x1.toFloat(), y1.toFloat())
                lineTo(x2.toFloat(), y2.toFloat())
            }
            GestureDescription.Builder()
                .addStroke(GestureDescription.StrokeDescription(
                    jalur, 0, durasiMs.coerceIn(50, 2000))).build()
        }

    fun aksiGlobal(nama: String): JSONObject {
        val out = JSONObject()
        val kode = when (nama) {
            "BACK" -> GLOBAL_ACTION_BACK
            "HOME" -> GLOBAL_ACTION_HOME
            "RECENTS" -> GLOBAL_ACTION_RECENTS
            else -> return out.put("ok", false)
                .put("sebab", "aksi global tidak dikenal: $nama")
        }
        val versiSebelum = PohonUI.versi
        val mulai = SystemClock.uptimeMillis()
        val gerbang = CountDownLatch(1)
        var okKirim = false
        penangan.post {
            okKirim = try { performGlobalAction(kode) } catch (e: Exception) { false }
            gerbang.countDown()
        }
        gerbang.await(900, TimeUnit.MILLISECONDS)
        val naik = tungguVersiNaik(versiSebelum)
        return out.put("ok", okKirim).put("versi_sblm", versiSebelum)
            .put("versi_ssdh", PohonUI.versi).put("naik", naik)
            .put("latensi_ms", SystemClock.uptimeMillis() - mulai)
    }

    // B2 (spek bayu 9 Okt): keyevent tanpa injeksi input —
    //  uid aplikasi TIDAK punya INJECT_EVENTS (keyevent shell = Security-
    //  Exception, terbukti 9 Okt), tetapi wakelock ACQUIRE_CAUSES_WAKEUP
    //  sah membangunkan layar (permission WAKE_LOCK biasa). 224 = bangun;
    //  3/4 = aksi global layanan (HOME/BACK sudah ada); kode lain ditolak
    //  jujur (butuh Shizuku). Balasan versi-gated seperti gestur.
    fun tombolKode(kode: Int): JSONObject {
        val out = JSONObject()
        val versiSebelum = PohonUI.versi
        val mulai = SystemClock.uptimeMillis()
        var ok = false
        var sebab = ""
        if (kode == 224) {
            val pm = getSystemService(PowerManager::class.java)
            if (pm != null) {
                @Suppress("DEPRECATION")
                val wl = pm.newWakeLock(
                    PowerManager.SCREEN_BRIGHT_WAKE_LOCK or
                        PowerManager.ACQUIRE_CAUSES_WAKEUP or
                        PowerManager.ON_AFTER_RELEASE, "musedroid:bangun")
                wl.acquire(8000)
                Thread.sleep(400)   // beri waktu peristiwa layar menyala
                ok = pm.isInteractive
                if (!ok) sebab = "layar masih mati setelah wakelock bangun"
            } else sebab = "PowerManager tidak tersedia"
        } else if (kode == 3 || kode == 4) {
            return aksiGlobal(if (kode == 3) "HOME" else "BACK").put("kode", kode)
        } else {
            sebab = "keyevent $kode butuh injeksi input (Shizuku/rish) — " +
                    "tidak tersedia dari layanan aksesibilitas"
        }
        val naik = tungguVersiNaik(versiSebelum)
        out.put("ok", ok).put("kode", kode).put("versi_sblm", versiSebelum)
            .put("versi_ssdh", PohonUI.versi).put("naik", naik)
            .put("latensi_ms", SystemClock.uptimeMillis() - mulai)
        if (sebab.isNotEmpty()) out.put("sebab", sebab)
        return out
    }

    // ---- penyaji socket 19102 ----

    private fun penyaji() {
        try {
            ServerSocket(PORT_POHON, 50, InetAddress.getByName("127.0.0.1")).use { server ->
                while (serverJalan) {
                    val klien = try { server.accept() } catch (e: Exception) { break }
                    thread {
                        klien.use {
                            val masuk = BufferedReader(
                                InputStreamReader(it.getInputStream(), Charsets.UTF_8))
                            val keluar = PrintWriter(it.getOutputStream(), true)
                            val perintah = masuk.readLine() ?: return@thread
                            keluar.println(jawab(perintah))
                        }
                    }
                }
            }
        } catch (e: Exception) {
            serverJalan = false
        }
    }

    private fun jawab(perintah: String): String {
        val pisah = perintah.indexOf(' ')
        val kata = if (pisah < 0) perintah.trim() else perintah.substring(0, pisah)
        val arg = if (pisah < 0) "" else perintah.substring(pisah + 1)
        val umur = PohonUI.umurMs()
        return when (kata) {
            "PING" -> JSONObject().put("pong", true)
                .put("versi", PohonUI.versi).put("umur_ms", umur).toString()
            "PAKET?" -> JSONObject().put("paket", PohonUI.paketDepan)
                .put("umur_ms", umur).toString()
            "TEKS?" -> JSONObject().put("ada", cari(arg) != null)
                .put("umur_ms", umur).put("versi", PohonUI.versi).toString()
            "CARI" -> {
                val s = cari(arg)
                if (s == null) JSONObject().put("ada", false)
                    .put("umur_ms", umur).put("versi", PohonUI.versi).toString()
                else JSONObject().put("ada", true).put("x", s.cx).put("y", s.cy)
                    .put("bounds", "[${s.x1},${s.y1}][${s.x2},${s.y2}]")
                    .put("umur_ms", umur).put("versi", PohonUI.versi).toString()
            }
            "POHON" -> {
                val arr = JSONArray()
                var n = 0
                for (s in PohonUI.simpul) {
                    if (s.teks.isEmpty() && s.desc.isEmpty() && !s.klik && !s.edit) continue
                    arr.put(JSONObject().put("t", s.teks).put("d", s.desc).put("k", s.kelas)
                        .put("b", "[${s.x1},${s.y1}][${s.x2},${s.y2}]")
                        .put("klik", s.klik).put("edit", s.edit).put("fokus", s.fokus))
                    if (++n >= 800) break
                }
                JSONObject().put("versi", PohonUI.versi).put("umur_ms", umur)
                    .put("nodes", arr).toString()
            }
            "ISI" -> (instans?.isiTeks(arg)
                ?: JSONObject().put("ok", false).put("sebab", "layanan tidak aktif")).toString()
            "KETUK", "TAHAN" -> {
                val b = arg.trim().split(Regex("\\s+")).mapNotNull { it.toIntOrNull() }
                val lay = instans
                when {
                    lay == null -> JSONObject().put("ok", false)
                        .put("sebab", "layanan tidak aktif").toString()
                    b.size < 2 -> JSONObject().put("ok", false)
                        .put("sebab", "format: $kata x y").toString()
                    kata == "KETUK" -> lay.gesturKetuk(b[0], b[1]).toString()
                    else -> lay.gesturTahan(b[0], b[1]).toString()
                }
            }
            "GESER" -> {
                val b = arg.trim().split(Regex("\\s+")).mapNotNull { it.toIntOrNull() }
                val lay = instans
                when {
                    lay == null -> JSONObject().put("ok", false)
                        .put("sebab", "layanan tidak aktif").toString()
                    b.size < 4 -> JSONObject().put("ok", false)
                        .put("sebab", "format: GESER x1 y1 x2 y2 [ms]").toString()
                    else -> lay.gesturGeser(
                        b[0], b[1], b[2], b[3],
                        if (b.size >= 5) b[4].toLong() else 300L).toString()
                }
            }
            "GLOBAL" -> (instans?.aksiGlobal(arg.trim().uppercase())
                ?: JSONObject().put("ok", false).put("sebab", "layanan tidak aktif")).toString()
            "TOMBOL" -> {
                val kode = arg.trim().toIntOrNull()
                val lay = instans
                when {
                    lay == null -> JSONObject().put("ok", false)
                        .put("sebab", "layanan tidak aktif").toString()
                    kode == null -> JSONObject().put("ok", false)
                        .put("sebab", "format: TOMBOL <kode>").toString()
                    else -> lay.tombolKode(kode).toString()
                }
            }
            else -> JSONObject().put("ok", false)
                .put("sebab", "perintah tidak dikenal").toString()
        }
    }

    private fun cari(teks: String): PohonUI.Simpul? {
        if (teks.isEmpty()) return null
        var substring: PohonUI.Simpul? = null
        for (s in PohonUI.simpul) {
            if (s.teks == teks || s.desc == teks) return s
            if (substring == null && (s.teks.contains(teks) || s.desc.contains(teks)))
                substring = s
        }
        return substring
    }
}
