#!/usr/bin/env python3
import socket, json, base64, os, time

SERVER = ("127.0.0.1", 6667)
DELIM  = "\r\n\r\n"

def send(cmd_str):
    try:
        with socket.socket() as s:
            s.settimeout(300)
            s.connect(SERVER)
            s.sendall((cmd_str + DELIM).encode())

            buf = ""
            while DELIM not in buf:
                data = s.recv(4096)
                if not data:
                    break
                buf += data.decode()
        return json.loads(buf.split(DELIM)[0])
    except (socket.timeout, ConnectionResetError) as e:
        print(f"⚠ Client send exception: {e}")
        return {"status":"ERROR", "data": str(e)}
    except Exception as e:
        print(f"⚠ Client unexpected exception: {e}")
        return {"status":"ERROR", "data": str(e)}


def client_list():
    return send("LIST")["data"]

def client_download(fn):
    r = send(f"GET {fn}")
    if r["status"]=="OK":
        data = base64.b64decode(r["data"])
        with open(f"dl_{fn}","wb") as f: f.write(data)
        return True, len(data)
    return False, 0

def client_upload(path):
    b64 = base64.b64encode(open(path,"rb").read()).decode()
    fn  = os.path.basename(path)
    r  = send(f"UPLOAD {fn} {b64}")
    return r["status"]=="OK", 0
