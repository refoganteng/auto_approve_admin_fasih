# auto_approve_admin_fasih

Otomasi persetujuan (*approval*) dokumen Sensus Ekonomi 2026 oleh Admin Kabupaten pada aplikasi FASIH-SM BPS.

## 🚀 Fitur Utama

1. **Anti-Bot & Bebas Blokir**: Menggunakan Google Chrome asli via CDP (*Chrome DevTools Protocol*), menghindari deteksi bot otomasi standar.
2. **Sesi Persisten**: Cookies dan sesi login tersimpan di folder profil browser sehingga tidak perlu login berulang kali.
3. **Tata Letak Split-Screen (Setengah Layar)**: Jendela Chrome otomatis diposisikan di setengah layar sebelah KANAN, dan Terminal di sebelah KIRI. Anda dapat memantau log proses bot secara langsung di terminal sambil melihat browser bekerja di sebelah kanan tanpa saling menutupi.
4. **Fokus Tetap Terjaga**: Fokus kursor/keyboard otomatis dijaga tetap di Terminal/aplikasi kerja Anda saat tab baru dibuka dan ditutup.
   - Membuka modal review dari kode assignment di tabel.
   - Membuka tab review assignment.
   - Mengeklik tombol approve (checklist hijau).
   - Mengonfirmasi modal approve.
   - Menunggu 2 detik untuk memastikan data tersimpan di server.
   - Menutup tab assignment dan menutup modal review.
5. **Auto Pagination**: Otomatis berpindah ke halaman berikutnya saat semua baris data di halaman aktif selesai diproses.

## 🛠️ Prasyarat

```bash
pip install playwright playwright-stealth
```

## 📋 Cara Penggunaan

1. Jalankan script:
   ```bash
   python3 auto_approve.py
   ```
2. Google Chrome akan terbuka. Login ke akun FASIH-SM jika belum login.
3. Masuk ke halaman **Data** survei SE2026.
4. Pasang filter status: **`EDITED BY ADMIN KABUPATEN`** dan ubah jumlah rows per halaman menjadi **100**.
5. Kembali ke terminal dan tekan **ENTER**.
6. Chrome akan berjalan rapi di setengah layar sebelah kanan, sementara Anda dapat memantau jalannya log terminal di sebelah kiri dengan nyaman.
