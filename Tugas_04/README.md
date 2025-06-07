# Tugas 4

## Deskripsi

Tugas ini adalah mengembangkan HTTP server yang mampu melakukan 3 fitur tambahan melalui metode HTTP standar:

1. **Melihat daftar file** di direktori server (`GET /list`)
2. **Mengunggah file** ke server (`POST /upload` dengan header `Filename:`)
3. **Menghapus file** dari server (`DELETE /<filename>`)

Fitur-fitur ini diimplementasikan dalam dua mode concurrency:

* `Thread Pool`
* `Process Pool`

## Modifikasi Kode

* [http.py](http.py): Logika utama HTTP server, kini mendukung GET, POST, dan DELETE untuk manipulasi file.
* [server_thread_pool_http.py](server_thread_pool_http.py): Server HTTP dengan ThreadPoolExecutor.
* [server_process_pool_http.py](server_process_pool_http.py): Server HTTP dengan ProcessPoolExecutor.
* [client.py](client/client.py): Client interaktif untuk mengakses ketiga fitur (list, upload, delete).

## Cara Menjalankan Kode

```bash
# Jalankan server dalam mode thread
python server_thread_pool_http.py

# Atau jalankan dalam mode process
python server_process_pool_http.py

# Jalankan client pada mesin lain
python client/client.py
```
