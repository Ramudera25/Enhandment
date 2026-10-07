// MainActivity.kt — KERANGKA (belum dibuild). Lihat README.md folder ini.
// Aktivitas utama aplikasi pendamping muse-droid:
//   1) memeriksa Shizuku hidup & izin sudah diberikan,
//   2) meminta izin bila belum (requestPermission),
//   3) menyalakan / mematikan LayananLokal.
package id.musedroid.pendamping

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import rikka.shizuku.Shizuku

class MainActivity : Activity() {

    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // TODO: layout sederhana (status + dua tombol) — dibuat saat build pertama.
        status = TextView(this)
        Button(this).apply {
            text = "Minta Izin Shizuku"
            setOnClickListener { mintaIzin() }
        }
        segarkanStatus()
    }

    private fun segarkanStatus() {
        val hidup = try { Shizuku.pingBinder() } catch (e: Throwable) { false }
        val izin = hidup && Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED
        status.text = when {
            !hidup -> "Shizuku tidak hidup — aktifkan Shizuku dulu."
            !izin -> "Shizuku hidup, izin belum diberikan."
            else -> "Siap. Layanan lokal dapat dinyalakan."
        }
    }

    private fun mintaIzin() {
        if (Shizuku.pingBinder() && Shizuku.checkSelfPermission() != PackageManager.PERMISSION_GRANTED) {
            Shizuku.requestPermission(1) // hasil kembali lewat OnRequestPermissionResultListener
        }
    }

    private fun nyalakanLayanan() {
        startForegroundService(Intent(this, LayananLokal::class.java))
    }
}
