# Tugas ETS — File Server Multithread & Multiprocess

## Deskripsi
Folder ini berisi implementasi dan eksperimen file server dengan dua model concurrency: **ThreadPool** dan **ProcessPool**. Eksperimen dilakukan untuk mengukur performa server saat menangani operasi file (download/upload) secara paralel dengan berbagai jumlah worker.

## Struktur File

- [`file_server_multithreadpool.py`](file_server_multithreadpool.py)  
  File server berbasis ThreadPoolExecutor. Setiap koneksi client diproses oleh thread pool.

- [`file_server_multiprocesspool.py`](file_server_multiprocesspool.py)  
  File server berbasis ProcessPoolExecutor. Setiap koneksi client diproses oleh process pool.

- [`client_worker.py`](client_worker.py)  
  Kode client untuk melakukan operasi `LIST`, `GET`, dan `UPLOAD` ke server. Digunakan oleh script stress test.

- [`stress_test.py`](stress_test.py)  
  Script untuk melakukan stress test ke server dengan banyak client secara paralel (thread/process). Mengukur waktu dan throughput.

- [`run_experiment.py`](run_experiment.py)  
  Script utama untuk menjalankan eksperimen otomatis: menjalankan server, menjalankan stress test dengan berbagai parameter, dan menyimpan hasil ke CSV.

## Cara Menjalankan Eksperimen

1. **Jalankan Eksperimen Otomatis**
   ```bash
   python run_experiment.py
   ```
   Hasil eksperimen akan tersimpan di file `results.csv`.

2. **Menjalankan Server Saja**
   - ThreadPool:  
     ```bash
     python file_server_multithreadpool.py
     ```
   - ProcessPool:  
     ```bash
     python file_server_multiprocesspool.py
     ```

3. **Menjalankan Stress Test Manual**
   ```bash
   python stress_test.py
   ```
   Bisa dikonfigurasi dengan environment variable:
   - `STRESS_OP` (`download`/`upload`)
   - `FILE_SIZE_MB` (ukuran file dummy)
   - `CLIENT_POOL` (jumlah client paralel)
   - `CLIENT_POOL_TYPE` (`thread`/`process`)

## Penjelasan Singkat Kode

- **Server** menerima perintah `LIST`, `GET <file>`, dan `UPLOAD <file> <base64>`. Semua data file dikirim dalam format base64.
- **Client** (`client_worker.py`) mengirim perintah ke server dan mengukur waktu transfer.
- **Stress Test** (`stress_test.py`) menjalankan banyak client secara paralel untuk mengukur performa server.
- **run_experiment.py** menjalankan seluruh kombinasi eksperimen (model server, jumlah worker, ukuran file, jumlah client) dan mencatat hasilnya.

---

> Andika Rahman Teja (5025221022)