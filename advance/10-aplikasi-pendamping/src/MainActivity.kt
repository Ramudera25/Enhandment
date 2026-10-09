// MainActivity.kt — aplikasi pendamping muse-droid (build pertama teruji
// 8 Okt 2026; diperluas V4.0: layanan depan + status aksesibilitas).
// Aktivitas utama:
//   1) memeriksa Shizuku hidup & izin sudah diberikan,
//   2) meminta izin — POPUP OTOMATIS: begitu binder Shizuku tiba dan izin
//      belum ada, dialog izin resmi Shizuku langsung dimunculkan
//      (requestPermission), tanpa berburu daftar aplikasi di manajer,
//   3) menyalakan LayananDepan (foreground service) yang menjadi jangkar
//      hidup proses dan menyalakan LayananLokal (socket 19101) sekalian.
//
// Catatan binder: binder Shizuku dikirim server ke provider aplikasi yang
// dikenalnya (penanda moe.shizuku.client.V3_SUPPORT di manifest). Aplikasi
// yang dipasang sesudah server start mungkin belum menerimanya; tombol
// "Buka Shizuku Sekali" memancing pemindaian ulang — sesudah itu listener
// di bawah menembakkan popup izin sendiri.
package id.musedroid.pendamping

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import rikka.shizuku.Shizuku

class MainActivity : Activity() {

    private lateinit var status: TextView
    private var popupSudahDitembak = false

    private val saatBinderTiba = Shizuku.OnBinderReceivedListener {
        runOnUiThread {
            segarkanStatus()
            tembakPopupIzin()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val induk = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 64, 48, 48)
        }
        status = TextView(this).apply { textSize = 18f }
        induk.addView(status)
        induk.addView(Button(this).apply {
            text = "Minta Izin Shizuku (popup)"
            setOnClickListener { popupSudahDitembak = false; tembakPopupIzin() }
        })
        induk.addView(Button(this).apply {
            text = "Buka Shizuku Sekali (pancing binder)"
            setOnClickListener { bukaShizuku() }
        })
        induk.addView(Button(this).apply {
            text = "Nyalakan Layanan (depan + lokal 19101)"
            setOnClickListener { nyalakanLayanan() }
        })
        setContentView(induk)
        Shizuku.addBinderReceivedListenerSticky(saatBinderTiba)
        Shizuku.addRequestPermissionResultListener { _, _ -> segarkanStatus() }
        mintaIzinNotifikasi()
        segarkanStatus()
        tembakPopupIzin()
    }

    override fun onResume() {
        super.onResume()
        segarkanStatus()
        tembakPopupIzin()  // kembali dari aplikasi Shizuku -> popup langsung muncul
    }

    override fun onDestroy() {
        Shizuku.removeBinderReceivedListener(saatBinderTiba)
        super.onDestroy()
    }

    private fun binderHidup(): Boolean =
        try { Shizuku.pingBinder() } catch (e: Throwable) { false }

    private fun izinAda(): Boolean =
        binderHidup() && Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED

    private fun segarkanStatus() {
        val dasar = when {
            !binderHidup() -> "Binder Shizuku belum tiba. Ketuk 'Buka Shizuku Sekali', lalu kembali ke sini — popup izin muncul otomatis."
            !izinAda() -> "Shizuku hidup, izin belum diberikan — popup izin ditembakkan."
            else -> "Siap. Layanan dapat dinyalakan."
        }
        val akses = if (LayananAkses.aktif)
            "\nPohon UI: AKTIF (socket 19102)."
        else
            "\nPohon UI: belum aktif — Pengaturan > Aksesibilitas > Aplikasi terpasang > muse-droid Pendamping."
        status.text = dasar + akses
    }

    private fun tembakPopupIzin() {
        if (popupSudahDitembak) return
        if (binderHidup() && !izinAda()) {
            popupSudahDitembak = true
            Shizuku.requestPermission(1)  // <- dialog popup resmi Shizuku
        }
    }

    private fun bukaShizuku() {
        popupSudahDitembak = false
        val niat = packageManager.getLaunchIntentForPackage("moe.shizuku.privileged.api")
        if (niat != null) startActivity(niat)
    }

    private fun mintaIzinNotifikasi() {
        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 7)
        }
    }

    private fun nyalakanLayanan() {
        val niat = Intent(this, LayananDepan::class.java)
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(niat)
        else startService(niat)
        status.text = "Layanan depan dinyalakan — uji: PING ke 127.0.0.1:19101 & 19102."
    }
}
