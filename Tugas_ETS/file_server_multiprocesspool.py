#!/usr/bin/env python3
import os, base64, logging, socket, json
from concurrent.futures import ProcessPoolExecutor

PORT        = 6667
DATA_DIR    = "server_files"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))
DELIMITER   = b"\r\n\r\n"

def handle_fd(fd):
    conn = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
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
            resp = {"status":"OK", "data": os.listdir(DATA_DIR)}
        elif cmd == "UPLOAD":
            fn, b64 = parts[1], parts[2]
            with open(os.path.join(DATA_DIR, fn),"wb") as f:
                f.write(base64.b64decode(b64))
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
    os.close(fd)

def main():
    import json
    os.makedirs(DATA_DIR, exist_ok=True)
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    srv.bind(("0.0.0.0", PORT)); srv.listen()
    logging.info(f"[PROCESS] port={PORT} workers={MAX_WORKERS}")
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        while True:
            conn, _ = srv.accept()
            fd = os.dup(conn.fileno())
            pool.submit(handle_fd, fd)
            conn.close()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    main()
