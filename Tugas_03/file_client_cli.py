import socket
import json
import base64
import logging
import os

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall((command_str + "\r\n\r\n").encode())
        data_received="" #empty string
        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False

def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filepath=""):
    try:
        with open(filepath, 'rb') as f:
            encoded_content = base64.b64encode(f.read()).decode('utf-8').replace('\n', '').replace('\r', '') # coba decode dengan utf-8
        filename = os.path.basename(filepath)
        command_str = f'UPLOAD {filename} {encoded_content}'
        hasil = send_command(command_str)
        print(hasil)
    except Exception as e:
        print(f"Gagal upload: {str(e)}")

def remote_delete(filename=""):
    hasil = send_command(f"DELETE {filename}")
    print(hasil)

if __name__ == '__main__':
    server_address=('172.16.16.101',6667)
    logging.warning("Client started")

    while True:
        print("\nPilih perintah berikut:")
        print("1. LIST")
        print("2. GET <file>")
        print("3. UPLOAD <file>")
        print("4. DELETE <file>")
        print("5. Keluar")

        user_input = input("Perintah: ").strip()
        match user_input.split(maxsplit=1):
            case ["1"]:
                remote_list()
            case ["2", filename]:
                remote_get(filename.strip())
            case ["3", filepath]:
                remote_upload(filepath.strip())
            case ["4", filename]:
                remote_delete(filename.strip())
            case ["5"]:
                print("Program dihentikan.")
                break
            case _:
                print("Perintah tidak dikenali.")