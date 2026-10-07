// MainActivity.kt — aplikasi pendamping muse-droid (build pertama, teruji 8 Okt 2026).
// Aktivitas utama:
//   1) memeriksa Shizuku hidup & izin sudah diberikan,
//   2) meminta izin bila belum (requestPermission),
//   3) menyalakan LayananLokal (layanan biasa dari latar-depan; pemakaian
//      foreground service = penyempurnaan berikutnya — lihat README 10).
package id.musedroid.pendamping

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import rikka.shizuku.Shizuku
import rikka.sui.Sui

class MainActivity : Activity() {

    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Sui.init mengambil binder langsung dari aplikasi Shizuku — penting
        // untuk aplikasi yang DIPASANG SESUDAH server Shizuku start (binder
        // tidak dikirim ulang ke provider baru sampai server restart;
        // terbukti di perangkat 8 Okt 2026).
        try { Sui.init(packageName) } catch (e: Throwable) { /* status akan melaporkan */ }
        val induk = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 64, 48, 48)
        }
        status = TextView(this).apply { textSize = 18f }
        induk.addView(status)
        induk.addView(Button(this).apply {
            text = "Minta Izin Shizuku"
            setOnClickListener { mintaIzin() }
        })
        induk.addView(Button(this).apply {
            text = "Nyalakan Layanan Lokal (127.0.0.1:19101)"
            setOnClickListener { nyalakanLayanan() }
        })
        setContentView(induk)
        Shizuku.addRequestPermissionResultListener { _, _ -> segarkanStatus() }
        segarkanStatus()
    }

    override fun onResume() {
        super.onResume()
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
            Shizuku.requestPermission(1)
        }
    }

    private fun nyalakanLayanan() {
        startService(Intent(this, LayananLokal::class.java))
        status.text = "Layanan dinyalakan — uji: kirim baris PING ke 127.0.0.1:19101."
    }
}
