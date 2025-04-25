import socket
import threading
from datetime import datetime
import logging

CRLF = b'\r\n' # maksud dari karakter 13 dan karakter 10 (poin c dan d)
# CRLF = Carriage Return Line Feed. Karakter yang digunakan untuk menandai akhir baris dalam protokol komunikasi seperti HTTP.

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self) # implementasi multithreading (poin b)

    def run(self):
        try:
            data_buffer = b''
            while True:
                data = self.connection.recv(32)
                if not data:
                    break
                data_buffer += data
                while CRLF in data_buffer:
                    line, data_buffer = data_buffer.split(CRLF, 1)
                    line_decoded = line.decode('utf-8').strip() # (poin d)

                    if line_decoded.upper() == "QUIT": # (poin c)
                        logging.info(f"Client {self.address} sent QUIT")
                        self.connection.close()
                        return

                    elif line_decoded.upper().startswith("TIME"): # (poin c)
                        now = datetime.now()
                        current_time =  now.strftime("%H:%M:%S") # (poin d)
                        logging.info(f"Client {self.address} requested time")
                        response = f"JAM {current_time}\r\n".encode('utf-8') # (poin c)
                        self.connection.sendall(response)

                    else:
                        self.connection.sendall(b'Invalid command\r\n')
        except Exception as e:
            logging.error(f"Error with client {self.address}: {e}")
        finally:
            self.connection.close()

class Server(threading.Thread):
    def __init__(self):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self) # implementasi multithreading (poin b)

    def run(self):
        self.my_socket.bind(('172.16.16.101', 45000)) # asumsi mesin-1 jadi server (poin a)
        self.my_socket.listen(5)
        logging.info("Time server running on port 45000...")

        while True:
            connection, client_address = self.my_socket.accept()
            logging.info(f"Connection from {client_address}")

            clt = ProcessTheClient(connection, client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    logging.basicConfig(level=logging.INFO)
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()
