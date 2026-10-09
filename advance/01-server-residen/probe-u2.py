import json, re, sys, time, urllib.request

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def rpc(method, params, timeout=10):
    req = urllib.request.Request(
        "http://127.0.0.1:9008/jsonrpc/0",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    t = time.time()
    r = json.load(op.open(req, timeout=timeout))
    return r.get("result"), time.time() - t

try:
    res, dt = rpc("dumpWindowHierarchy", [False, 50])
    if res:
        pkgs = re.findall(r'package="([^"]+)"', res)
        teks = [t for t in re.findall(r'text="([^"]+)"', res) if t]
        print("DUMP OK %.2f dtk, %d karakter, paket teratas: %s" % (dt, len(res), pkgs[0] if pkgs else "?"))
        print("contoh teks:", teks[:5])
    else:
        print("DUMP result kosong")
except Exception as e:
    print("DUMP GAGAL:", type(e).__name__, str(e)[:140])
    sys.exit(1)
