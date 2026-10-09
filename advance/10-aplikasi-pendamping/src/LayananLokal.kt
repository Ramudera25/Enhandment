// LayananLokal.kt — layanan latar aplikasi pendamping muse-droid.
// Membuka server socket di 127.0.0.1:19101 (hanya lokal) dan melayani
// perintah satu baris. Perintah istimewa dijalankan lewat UserService
// Shizuku (LayananPriv, proses uid shell) yang diikat dari sini.
//
// Protokol:
//   PING                  -> PONG
//   UID                   -> "UID <n>" dari proses layanan istimewa
//   DUMP                  -> XML hierarki, diakhiri baris ".AKHIR"
//   KETUK <x> <y>         -> OK / GAGAL <sebab>
//   GESER <x1> <y1> <x2> <y2> [ms] -> OK / GAGAL <sebab>
//   TOMBOL <kode>         -> OK / GAGAL <sebab>  (kode keyevent Android)
package id.musedroid.pendamping

import android.app.Service
import android.content.ComponentName
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.IBinder
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.ServerSocket
import kotlin.concurrent.thread
import rikka.shizuku.Shizuku

class LayananLokal : Service() {

    companion object { const val PORT = 19101 }

    @Volatile private var jalan = false
    @Volatile private var priv: ILayananPriv? = null
    @Volatile private var sedangMengikat = false

    private val koneksi = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            priv = ILayananPriv.Stub.asInterface(binder)
            sedangMengikat = false
        }
        override fun onServiceDisconnected(name: ComponentName?) {
            priv = null
            sedangMengikat = false
        }
    }

    private fun ikatPriv() {
        if (priv != null || sedangMengikat) return
        try {
            if (!Shizuku.pingBinder()) return
            if (Shizuku.checkSelfPermission() != PackageManager.PERMISSION_GRANTED) return
            sedangMengikat = true
            val args = Shizuku.UserServiceArgs(
                ComponentName(packageName, LayananPriv::class.java.name)
            ).daemon(false).tag("muse-priv").processNameSuffix("priv")
                .debuggable(false).version(1)
            Shizuku.bindUserService(args, koneksi)
        } catch (e: Exception) {
            sedangMengikat = false
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        ikatPriv()
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

    private fun lewatPriv(aksi: (ILayananPriv) -> String): String {
        val p = priv ?: run { ikatPriv(); return "GAGAL layanan istimewa belum tersambung (sedang mengikat — coba lagi)" }
        return try { aksi(p) } catch (e: Exception) { "GAGAL ${e.message}" }
    }

    private fun jalankan(perintah: String): String {
        val bagian = perintah.trim().split(Regex("\\s+"))
        return when (bagian[0]) {
            "PING" -> "PONG"
            "UID" -> lewatPriv { "UID ${it.uidSaya()}" }
            "DUMP" -> lewatPriv { p ->
                val xml = p.dumpXml()
                if (xml.startsWith("GAGAL")) xml else xml + "\n.AKHIR"
            }
            "KETUK" -> {
                if (bagian.size < 3) return "GAGAL format: KETUK <x> <y>"
                lewatPriv { p ->
                    val out = p.jalankan("input tap ${bagian[1]} ${bagian[2]}")
                    if (out.contains("GAGAL") || out.contains("Exception")) "GAGAL $out" else "OK"
                }
            }
            "GESER" -> {
                if (bagian.size < 5) return "GAGAL format: GESER <x1> <y1> <x2> <y2> [ms]"
                val ms = if (bagian.size >= 6) bagian[5] else "300"
                lewatPriv { p ->
                    val out = p.jalankan("input swipe ${bagian[1]} ${bagian[2]} ${bagian[3]} ${bagian[4]} $ms")
                    if (out.contains("GAGAL") || out.contains("Exception")) "GAGAL $out" else "OK"
                }
            }
            "TOMBOL" -> {
                if (bagian.size < 2) return "GAGAL format: TOMBOL <kode>"
                lewatPriv { p ->
                    val out = p.jalankan("input keyevent ${bagian[1]}")
                    if (out.contains("GAGAL") || out.contains("Exception")) "GAGAL $out" else "OK"
                }
            }
            else -> "GAGAL perintah tidak dikenal"
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        jalan = false
        super.onDestroy()
    }
}
