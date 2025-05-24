#!/usr/bin/env python3
import os, subprocess, time, signal, json, csv

# ——— konfigurasi eksperimen ———
SERVER_SCRIPTS = {
    "thread":   "file_server_multithreadpool.py",
    "process":  "file_server_multiprocesspool.py"
}
SERVER_WS      = [1, 5, 50]            # jumlah server worker pool
CLIENT_WS      = [1, 5, 50]            # jumlah client worker pool
OPS            = ["download", "upload"]
SIZES_MB       = [10, 50, 100]
OUT_CSV        = "results.csv"
# ——————————————————————————————

def start_server(mode, workers):
    env = os.environ.copy()
    env["MAX_WORKERS"] = str(workers)
    return subprocess.Popen(
        ["python3", SERVER_SCRIPTS[mode]],
        env=env,
        preexec_fn=os.setsid,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def run_stress(op, size, cworkers):
    env = os.environ.copy()
    env.update({
        "STRESS_OP":       op,
        "FILE_SIZE_MB":    str(size),
        "CLIENT_POOL":     str(cworkers),
        # client always pakai ThreadPoolExecutor (default)
    })
    proc = subprocess.run(
        ["python3", "stress_test.py"],
        capture_output=True, env=env, text=True
    )
    return json.loads(proc.stdout)

def kill_server(p):
    os.killpg(os.getpgid(p.pid), signal.SIGTERM)

def main():
    # Tulis header CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        cols = [
            "Nomor",
            "Model concurrency",         # multithreading/process
            "Operasi",
            "Volume",
            "Jumlah client worker pool",
            "Jumlah server worker pool",
            "Waktu total per client",
            "Throughput per client",
            "Jumlah client sukses",
            "Jumlah client gagal",
            "Jumlah server sukses",
            "Jumlah server gagal"
        ]
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()

        counter = 1
        for model in SERVER_SCRIPTS:              # 2 mode
            for sw in SERVER_WS:                  # 3 opsi server pool
                print(f"> START SERVER {model} w={sw}")
                srv = start_server(model, sw)
                time.sleep(1)  # tunggu server siap

                for op in OPS:                    # 2 operasi
                    for sz in SIZES_MB:           # 3 volume
                        for cw in CLIENT_WS:      # 3 client pool size
                            print(f"  • {model} | {op} | {sz}MB | client×{cw}")
                            try:
                                res = run_stress(op, sz, cw)
                            except Exception as e:
                                print(f"  ✖ stress_test error (JSON decode): {e}")
                                # Buat row hasil gagal total
                                res = {
                                    "total_time_s": 0,
                                    "throughput_Bps": 0,
                                    "succeed": 0,
                                    "failed": cw,
                                }
                            row = {
                                "Nomor":                     counter,
                                "Model concurrency":         model,
                                "Operasi":                   op,
                                "Volume":                    f"{sz} MB",
                                "Jumlah client worker pool": cw,
                                "Jumlah server worker pool": sw,
                                "Waktu total per client":    res["total_time_s"],
                                "Throughput per client":     res["throughput_Bps"],
                                "Jumlah client sukses":      res["succeed"],
                                "Jumlah client gagal":       res["failed"],
                                # asumsi server pool selalu sukses penuh
                                "Jumlah server sukses":      sw,
                                "Jumlah server gagal":       0
                            }
                            writer.writerow(row)
                            f.flush()
                            counter += 1

                kill_server(srv)
                time.sleep(0.5)

    print("✅ Semua eksperimen selesai — hasil ada di", OUT_CSV)

if __name__ == "__main__":
    main()
