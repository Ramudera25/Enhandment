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
//                     bukan pada salinan, sesuai aturan kebenaran desain)
//
// Aturan kebenaran (DESAIN-V3-POHON-UI.md §4): umur salinan selalu
// dilaporkan; konsumen menolak jawaban basi untuk langkah pengubah layar;
// langkah destruktif tidak pernah diputuskan dari salinan. Server ini
// hanya ada selama layanan aksesibilitas aktif — ketiadaannya adalah
// sinyal turun-kelas yang jujur ke mode dump.
package id.musedroid.pendamping

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.graphics.Rect
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.InetAddress
import java.net.ServerSocket
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
        val akar = try { rootInActiveWindow } catch (e: Exception) { null }
        if (akar == null) return out.put("ok", false).put("sebab", "tidak ada jendela aktif")
        var sasaran: AccessibilityNodeInfo? = null
        var cadangan: AccessibilityNodeInfo? = null
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
        val node = sasaran ?: cadangan
            ?: return out.put("ok", false).put("sebab", "tidak ada kolom edit di jendela aktif")
        val args = Bundle()
        args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, teks)
        val ok = try { node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args) }
            catch (e: Exception) { false }
        if (ok) segarkan()
        return out.put("ok", ok).put("sebab", if (ok) "" else "ACTION_SET_TEXT ditolak node")
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
