// LayananPriv.kt — sisi server UserService Shizuku (proses uid shell).
// Diinstansiasi Shizuku secara reflektif dari APK ini; JANGAN daftarkan
// di manifest (bukan android.app.Service).
package id.musedroid.pendamping

import java.io.File
import java.net.HttpURLConnection
import java.net.URL

class LayananPriv : ILayananPriv.Stub() {

    override fun jalankan(perintah: String): String {
        return try {
            val pb = ProcessBuilder("sh", "-c", perintah)
            pb.redirectErrorStream(true)
            val proses = pb.start()
            val teks = proses.inputStream.bufferedReader().readText()
            proses.waitFor()
            teks
        } catch (e: Exception) {
            "GAGAL: ${e.message}"
        }
    }

    override fun dumpXml(): String {
        // Jalur cepat: server residen u2 (UiAutomation sudah terikat di sana).
        try {
            val conn = URL("http://127.0.0.1:9008/jsonrpc/0").openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.doOutput = true
            conn.connectTimeout = 3000
            conn.readTimeout = 8000
            conn.setRequestProperty("Content-Type", "application/json")
            conn.outputStream.write(
                """{"jsonrpc":"2.0","id":1,"method":"dumpWindowHierarchy","params":[false,50]}""".toByteArray()
            )
            val badan = conn.inputStream.bufferedReader().readText()
            // Urus JSON dengan pengurai bawaan Android — membuka-escape
            // manual terbukti meninggalkan sisa "\r\n" literal di XML.
            val hasil = org.json.JSONObject(badan).optString("result", "")
            if (hasil.startsWith("<?xml")) return hasil
        } catch (e: Exception) {
            // jatuh ke cadangan di bawah
        }
        // Cadangan: uiautomator dump ke berkas milik proses ini, lalu baca.
        val berkas = File("/data/local/tmp/md-priv-dump.xml")
        val hasil = jalankan("uiautomator dump ${berkas.absolutePath} >/dev/null 2>&1; echo rc=\$?")
        return try {
            if (berkas.exists() && berkas.length() > 0) berkas.readText()
            else "GAGAL: uiautomator tidak menghasilkan dump ($hasil)"
        } catch (e: Exception) {
            "GAGAL: ${e.message}"
        }
    }

    override fun uidSaya(): Int = android.os.Process.myUid()

    override fun destroy() {
        System.exit(0)
    }
}
