// LayananLokal.kt — KERANGKA (belum dibuild). Lihat README.md folder ini.
// Layanan latar aplikasi pendamping muse-droid:
//   - membuka server socket di 127.0.0.1:PORT (hanya lokal, tidak ke jaringan),
//   - menerima perintah satu baris (teks), menjalankan aksi, membalas hasil.
// Protokol (sengaja meniru bahasa .job eksekutor agar alat lama tetap nyambung):
//   PING                 -> PONG
//   DUMP                 -> XML uiautomator (diambil lewat proses berhak Shizuku)
//   KETUK <x> <y>        -> OK / GAGAL <sebab>
//   GESER <x1> <y1> <x2> <y2>
//   KETIK <teks...>      -> lewat IME pendamping (tahap berikutnya)
//   FOTO                 -> PNG (base64) dari screencap
//   TUNGGU_TEKS <teks> <detik>  -> OK saat tampil / TIMEOUT
package id.musedroid.pendamping

import android.app.Service
import android.content.Intent
import android.os.IBinder
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.ServerSocket
import kotlin.concurrent.thread

class LayananLokal : Service() {

    companion object { const val PORT = 19101 }  // port tetap (TODO lama selesai, build 8 Okt 2026)

    @Volatile private var jalan = false

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (!jalan) {
            jalan = true
            thread { dengarkan() }
        }
        return START_STICKY
    }

    private fun dengarkan() {
        ServerSocket(PORT, 50,
            java.net.InetAddress.getByName("127.0.0.1")).use { server ->
            while (jalan) {
                val klien = server.accept()
                thread {
                    klien.use {
                        val masuk = BufferedReader(InputStreamReader(it.getInputStream()))
                        val keluar = PrintWriter(it.getOutputStream(), true)
                        val perintah = masuk.readLine() ?: return@thread
                        keluar.println(jalankan(perintah))
                    }
                }
            }
        }
    }

    // TODO saat build pertama: sambungkan tiap perintah ke UserService Shizuku
    // (proses terpisah berhak shell) — di sanalah dump/ketuk/foto dieksekusi.
    private fun jalankan(perintah: String): String = when {
        perintah == "PING" -> "PONG"
        perintah.startsWith("KETUK ") -> "GAGAL belum disambungkan (kerangka)"
        perintah.startsWith("DUMP") -> "GAGAL belum disambungkan (kerangka)"
        else -> "GAGAL perintah tidak dikenal"
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        jalan = false
        super.onDestroy()
    }
}
