#!/usr/bin/env python3
import os, base64, logging, socket
from concurrent.futures import ThreadPoolExecutor

PORT        = 6667
DATA_DIR    = "server_files"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))
DELIMITER   = b"\r\n\r\n"

def handle_conn(conn):
    conn.settimeout(300)
    try:
        buf = b""
        while DELIMITER not in buf:
            chunk = conn.recv(2**20)  # 1MB
            if not chunk: break
            buf += chunk
        raw = buf.split(DELIMITER)[0].decode()
        parts = raw.split(" ", 2)
        cmd = parts[0]
        if cmd == "LIST":
            files = os.listdir(DATA_DIR)
            resp = {"status":"OK", "data": files}
        elif cmd == "UPLOAD":
            fn, b64 = parts[1], parts[2]
            data = base64.b64decode(b64)
            with open(os.path.join(DATA_DIR, fn),"wb") as f: f.write(data)
            resp = {"status":"OK","data":"Uploaded"}
        elif cmd == "GET":
            fn = parts[1]
            data = base64.b64encode(open(os.path.join(DATA_DIR, fn),"rb").read()).decode()
            resp = {"status":"OK","data": data}
        else:
            resp = {"status":"ERROR","data":"Unknown"}
    except Exception as e:
        logging.exception(e)
        resp = {"status":"ERROR","data":str(e)}
    conn.sendall((json.dumps(resp)).encode()+DELIMITER)
    conn.close()

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT)); srv.listen()
    logging.info(f"[THREAD] port={PORT} workers={MAX_WORKERS}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        while True:
            conn, _ = srv.accept()
            pool.submit(handle_conn, conn)

if __name__=="__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    main()
