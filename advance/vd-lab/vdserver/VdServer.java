
import android.content.Context;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.view.Display;

public class VdServer {
    public static void main(String[] args) throws Exception {
        int w = Integer.parseInt(args[0]);
        int h = Integer.parseInt(args[1]);
        int dpi = Integer.parseInt(args[2]);
        String name = args.length > 3 ? args[3] : "muse-vd";
        System.out.println("STAGE1-start"); System.out.flush();
        Looper.prepare();
        HandlerThread ht = new HandlerThread("vd-frames");
        ht.start();
        Handler handler = new Handler(ht.getLooper());
        ImageReader reader = ImageReader.newInstance(w, h, PixelFormat.RGBA_8888, 2);
        reader.setOnImageAvailableListener(r -> {
            Image img = r.acquireLatestImage();
            if (img != null) img.close();
        }, handler);
        Object at = Class.forName("android.app.ActivityThread").getMethod("systemMain").invoke(null);
        System.out.println("STAGE2-reader-ok"); System.out.flush();
        Context ctx = (Context) at.getClass().getMethod("getSystemContext").invoke(at);
        DisplayManager dm = (DisplayManager) ctx.getSystemService(Context.DISPLAY_SERVICE);
        int flags = args.length > 4 ? Integer.parseInt(args[4])
                  : (DisplayManager.VIRTUAL_DISPLAY_FLAG_PUBLIC | DisplayManager.VIRTUAL_DISPLAY_FLAG_PRESENTATION);
        System.out.println("STAGE3-sebelum-buat-vd"); System.out.flush();
        VirtualDisplay vd = dm.createVirtualDisplay(name, w, h, dpi, reader.getSurface(), flags);
        if (vd == null) {
            System.out.println("VD_GAGAL=null");
            System.out.flush();
            return;
        }
        Display d = vd.getDisplay();
        System.out.println("DISPLAY_ID=" + d.getDisplayId());
        System.out.flush();
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try { vd.release(); } catch (Exception ignored) {}
        }));
        Looper.loop();
    }
}
