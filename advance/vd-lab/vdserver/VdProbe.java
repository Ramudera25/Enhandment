import android.content.Context;
import android.hardware.display.DisplayManager;
import android.os.Looper;
import android.view.Display;

public class VdProbe {
    public static void main(String[] args) throws Exception {
        Looper.prepare();
        Object at = Class.forName("android.app.ActivityThread").getMethod("systemMain").invoke(null);
        Context ctx = (Context) at.getClass().getMethod("getSystemContext").invoke(at);
        DisplayManager dm = (DisplayManager) ctx.getSystemService(Context.DISPLAY_SERVICE);
        Display[] ds = dm.getDisplays();
        System.out.println("JUMLAH_DISPLAY=" + ds.length);
        for (Display d : ds) System.out.println("display " + d.getDisplayId() + " " + d.getName());
        System.out.flush();
        System.exit(0);
    }
}
