#!/usr/bin/env python3
import os, time, json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from client_worker import client_download, client_upload

OP   = os.getenv("STRESS_OP","download")
SIZE = int(os.getenv("FILE_SIZE_MB",10))
POOL = os.getenv("CLIENT_POOL_TYPE","thread")
CNT  = int(os.getenv("CLIENT_POOL",1))
FILE = f"dummy_{SIZE}MB.bin"

def prep():
    # pastikan direktori server ada dan file dummy tersedia
    os.makedirs("server_files", exist_ok=True)
    server_path = os.path.join("server_files", FILE)
    if not os.path.exists(server_path):
        with open(server_path, "wb") as f:
            f.write(os.urandom(SIZE * 1024 * 1024))
    # untuk upload: buat juga file dummy di CWD klien
    if OP == "upload":
        if not os.path.exists(FILE):
            # cukup copy dari server_files
            with open(server_path, "rb") as sf, open(FILE, "wb") as cf:
                cf.write(sf.read())

def worker(_):
    start = time.time()
    try:
        if OP == "download":
            ok, b = client_download(FILE)
        else:
            ok, _ = client_upload(FILE)
            b = SIZE * 1024 * 1024 if ok else 0
    except Exception as e:
        print(f"⚠ Worker exception: {e}")
        ok, b = False, 0
    elapsed = time.time() - start
    return {"ok": ok, "time": elapsed, "bytes": b}

def main():
    prep()
    Executor = ThreadPoolExecutor if POOL == "thread" else ProcessPoolExecutor
    with Executor(max_workers=CNT) as exec:
        results = list(exec.map(worker, range(CNT)))

    total_t = sum(r["time"] for r in results)
    total_b = sum(r["bytes"] for r in results)
    succ    = sum(1 for r in results if r["ok"])
    fail    = CNT - succ

    output = {
        "clients": CNT,
        "pool": POOL,
        "op": OP,
        "size_mb": SIZE,
        "total_time_s": round(total_t, 3),
        "throughput_Bps": int(total_b / total_t) if total_t > 0 else 0,
        "succeed": succ,
        "failed":  fail
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
