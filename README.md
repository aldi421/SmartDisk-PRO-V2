# SmartDiskAnalyzer

Aplikasi desktop Windows untuk menganalisis penggunaan storage, menelusuri file/folder terbesar, mencari duplikat, mengatur file, dan meninjau file sampah. Dibangun dengan Python + CustomTkinter.

## Jalankan dari source

```bash
py -m pip install -r requirements.txt
py main.py
```

## Buat aplikasi EXE (Windows)

1. Pastikan Python 3.11+ terpasang dan opsi **Add Python to PATH** dicentang.
2. Ekstrak folder proyek ke lokasi biasa, misalnya Documents (jangan jalankan dari dalam file ZIP).
3. Klik dua kali `build_windows.bat`.
4. Setelah selesai, jalankan `dist\SmartDiskAnalyzer.exe` dengan double-click. Tidak perlu membuka CMD atau mengetik perintah lagi.

Build EXE perlu dilakukan di Windows. File EXE hasil build tidak bisa dibuat secara native dari lingkungan Linux ini; script builder disediakan di proyek agar bisa dibuat langsung pada laptop Windows.

## Fitur

- **Dashboard:** pemakaian drive, ruang kosong, dan ringkasan scan terakhir.
- **Storage Analyzer:** scan folder rekursif, tampilkan hingga 1.000 file terbesar dan 1.000 folder terbesar, filter nama/path, pilih jumlah tampilan (50/100/250/500/1.000), buka lokasi, dan ekspor CSV.
- **File Organizer:** mengelompokkan file lepas berdasarkan tipe dengan pratinjau dan undo.
- **Duplicate Finder:** mencari file duplikat berdasarkan ukuran dan hash.
- **Smart Cleaner:** meninjau file sampah sebelum tindakan hapus.
- **Smart Insights:** rekomendasi berbasis hasil scan yang tersimpan lokal.
- **Settings:** pengaturan tema dan warna aksen.

## Catatan

- Analyzer menyimpan maksimal 1.000 hasil file/folder terbesar agar hasil bisa dibuka dengan cepat dan pemakaian memori untuk daftar file tidak membengkak.
- Scan berjalan secara lokal. Hasil scan tidak dikirim ke server.
- Periksa pilihan dengan teliti sebelum menghapus file. Cleaner dan Duplicate Finder melakukan tindakan hapus hanya setelah konfirmasi.
- Pengaturan disimpan di `%APPDATA%\SmartDiskAnalyzer\user_settings.json` pada Windows.
