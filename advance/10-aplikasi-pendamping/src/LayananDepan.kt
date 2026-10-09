// LayananDepan.kt — layanan depan (foreground service) pendamping muse-droid.
// Jangkar hidup aplikasi: selama layanan ini berjalan dengan notifikasi
// tetap, Android menahan proses dari pembunuhan latar — sehingga
// LayananLokal (socket 19101) dan LayananAkses (pohon UI 19102) tidak
// mati diam-diam saat HP lama menganggur (kelemahan build pertama).
//
// Satu pintu masuk: onStartCommand menyalakan LayananLokal sekalian,
// jadi penjaga kaki / MainActivity cukup menghidupkan layanan ini.
package id.musedroid.pendamping

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.PowerManager

class LayananDepan : Service() {

    companion object {
        const val ID_NOTIF = 19100
        const val KANAL = "pendamping-depan"
    }

    // B1 (spek bayu 9 Okt): jangkar hidup juga menjaga daya —
    //  (1) PARTIAL_WAKE_LOCK: CPU tetap hidup walau layar mati, agar
    //      LayananLokal (19101) & LayananAkses (19102) tidak dibekukan
    //      doze saat misi berjalan;
    //  (2) SCREEN_BRIGHT_WAKE_LOCK: layar tidak mati karena TIMEOUT
    //      selama layanan depan aktif (sebab kegagalan misi 9 Okt pagi:
    //      screen_off_timeout pendek membekukan peristiwa & am start).
    //      Tombol daya tetap mengalahkan wakelock ini (hak pengguna);
    //      bangun ulang lewat TOMBOL 224 di server pohon (B2).
    //  Keduanya dilepas bersih di onDestroy (tak ada wakelock menggantung).
    private var wlCpu: PowerManager.WakeLock? = null
    private var wlLayar: PowerManager.WakeLock? = null

    override fun onCreate() {
        super.onCreate()
        val nm = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= 26) {
            nm?.createNotificationChannel(
                NotificationChannel(KANAL, "Pendamping siaga",
                    NotificationManager.IMPORTANCE_LOW)
            )
        }
        val notif: Notification = Notification.Builder(this, KANAL)
            .setContentTitle("muse-droid Pendamping siaga")
            .setContentText("Kaki kendali lokal aktif — pohon UI & socket lokal.")
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(ID_NOTIF, notif,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(ID_NOTIF, notif)
        }
        val pm = getSystemService(PowerManager::class.java)
        wlCpu = pm?.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,
            "musedroid:jangkar")?.apply {
            setReferenceCounted(false); acquire()
        }
        @Suppress("DEPRECATION")
        wlLayar = pm?.newWakeLock(
            PowerManager.SCREEN_BRIGHT_WAKE_LOCK or
                PowerManager.ON_AFTER_RELEASE,
            "musedroid:layar")?.apply {
            setReferenceCounted(false); acquire()
        }
    }

    override fun onDestroy() {
        wlCpu?.release(); wlCpu = null
        wlLayar?.release(); wlLayar = null
        super.onDestroy()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        try {
            startService(Intent(this, LayananLokal::class.java))
        } catch (e: Exception) {
            // LayananLokal bisa gagal dinyalakan dari konteks tertentu;
            // layanan depan sendiri tetap hidup sebagai jangkar.
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
