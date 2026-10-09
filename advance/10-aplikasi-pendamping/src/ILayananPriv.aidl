// ILayananPriv.aidl — antarmuka layanan istimewa (UserService Shizuku).
// Layanan ini berjalan dengan uid shell (2000) di proses terpisah yang
// dibuat Shizuku dari APK ini; aplikasi utama memanggilnya lewat binder.
package id.musedroid.pendamping;

interface ILayananPriv {
    /** Jalankan perintah shell, kembalikan gabungan stdout+stderr. */
    String jalankan(String perintah);

    /** XML hierarki layar saat ini (lewat server residen u2 bila hidup,
     *  cadangan uiautomator). String kosong + awalan GAGAL bila gagal. */
    String dumpXml();

    /** UID proses layanan — bukti tingkat hak (harapan: 2000 = shell). */
    int uidSaya();

    /** Dipanggil Shizuku saat layanan dilepas. */
    void destroy();
}
