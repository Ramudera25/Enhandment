package id.musedroid.vdlab;

import android.app.Activity;
import android.app.ActivityOptions;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Display;
import android.widget.TextView;
import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends Activity {
    static VirtualDisplay vd;
    static ImageReader reader;
    static int frames = 0;
    TextView tv;
    Handler h = new Handler(Looper.getMainLooper());

    void log(String s) {
        String line = new SimpleDateFormat("HH:mm:ss", Locale.US).format(new Date()) + " " + s;
        try {
            File f = new File(getExternalFilesDir(null), "vdlog.txt");
            FileWriter w = new FileWriter(f, true);
            w.write(line + "\n");
            w.close();
        } catch (Exception ignored) {}
        if (tv != null) tv.append(line + "\n");
    }

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        tv = new TextView(this);
        tv.setTextSize(13);
        setContentView(tv);
        log("VD Lab mulai, uid=" + android.os.Process.myUid());
        h.postDelayed(this::buatVd, 1000);
    }

    void buatVd() {
        DisplayManager dm = (DisplayManager) getSystemService(DISPLAY_SERVICE);
        reader = ImageReader.newInstance(720, 1600, PixelFormat.RGBA_8888, 2);
        reader.setOnImageAvailableListener(r -> {
            Image img = r.acquireLatestImage();
            if (img != null) { simpanFrame(img); img.close(); frames++; }
        }, h);
        int[][] combos = {
            {DisplayManager.VIRTUAL_DISPLAY_FLAG_PUBLIC | DisplayManager.VIRTUAL_DISPLAY_FLAG_PRESENTATION, },
            {DisplayManager.VIRTUAL_DISPLAY_FLAG_PRESENTATION},
            {0}
        };
        for (int[] c : combos) {
            try {
                vd = dm.createVirtualDisplay("muse-vd", 720, 1600, 320, reader.getSurface(), c[0]);
                if (vd != null) {
                    Display d = vd.getDisplay();
                    log("VD BERHASIL flags=" + c[0] + " DISPLAY_ID=" + d.getDisplayId() + " nama=" + d.getName());
                    h.postDelayed(this::cekFrames, 3000);
                    h.postDelayed(this::luncurkanGlints, 4500);
                    return;
                } else {
                    log("VD null flags=" + c[0]);
                }
            } catch (Exception e) {
                log("VD GAGAL flags=" + c[0] + " : " + e.getClass().getSimpleName() + " " + e.getMessage());
            }
        }
        log("SEMUA KOMBINASI FLAGS GAGAL");
    }

    void cekFrames() { log("frame diterima sejauh ini: " + frames); }

    long simpanTerakhir = 0;
    void simpanFrame(Image img) {
        long now = System.currentTimeMillis();
        if (now - simpanTerakhir < 8000) return;
        simpanTerakhir = now;
        try {
            Image.Plane p = img.getPlanes()[0];
            int w = img.getWidth(), hh = img.getHeight();
            int rowPadding = p.getRowStride() - p.getPixelStride() * w;
            android.graphics.Bitmap bmp = android.graphics.Bitmap.createBitmap(
                w + rowPadding / p.getPixelStride(), hh, android.graphics.Bitmap.Config.ARGB_8888);
            bmp.copyPixelsFromBuffer(p.getBuffer());
            android.graphics.Bitmap potong = android.graphics.Bitmap.createBitmap(bmp, 0, 0, w, hh);
            File f = new File(getExternalFilesDir(null), "frame-vd.png");
            java.io.FileOutputStream out = new java.io.FileOutputStream(f);
            potong.compress(android.graphics.Bitmap.CompressFormat.PNG, 90, out);
            out.close();
            log("frame PNG disimpan (" + w + "x" + hh + ")");
        } catch (Exception e) {
            log("simpan frame GAGAL: " + e.getClass().getSimpleName() + " " + e.getMessage());
        }
    }

    void luncurkanGlints() {
        if (vd == null) { log("luncurkan: vd null, lewati"); return; }
        try {
            Intent i = getPackageManager().getLaunchIntentForPackage("com.glints.candidate");
            if (i == null) { log("luncurkan: intent Glints null"); return; }
            ActivityOptions o = ActivityOptions.makeBasic();
            o.setLaunchDisplayId(vd.getDisplay().getDisplayId());
            startActivity(i, o.toBundle());
            log("GLINTS DILUNCURKAN ke display " + vd.getDisplay().getDisplayId());
        } catch (Exception e) {
            log("luncurkan GAGAL: " + e.getClass().getSimpleName() + " " + e.getMessage());
        }
    }
}
