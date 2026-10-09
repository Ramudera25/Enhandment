import json, re, urllib.request

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
req = urllib.request.Request(
    "http://127.0.0.1:9008/jsonrpc/0",
    data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "dumpWindowHierarchy", "params": [False, 50]}).encode(),
    headers={"Content-Type": "application/json"})
r = json.load(op.open(req, timeout=10))
xml = r.get("result") or ""
pkgs = re.findall(r'package="([^"]+)"', xml)
print("paket unik:", sorted(set(pkgs)))
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
print("jumlah teks:", len(texts))
for t in texts:
    print(" -", t[:60])
