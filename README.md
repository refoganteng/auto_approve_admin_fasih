# auto_approve_admin_fasih

Otomasi persetujuan (*approval*) dokumen Sensus Ekonomi 2026 oleh Admin Kabupaten pada aplikasi FASIH-SM BPS.

## 🚀 Fitur Utama

1. **Anti-Bot & Bebas Blokir**: Menggunakan Google Chrome asli via CDP (*Chrome DevTools Protocol*), menghindari deteksi bot otomasi standar.
2. **Sesi Persisten**: Cookies dan sesi login tersimpan di folder profil browser sehingga tidak perlu login berulang kali.
3. **Background Off-Screen Window**: Jendela Chrome otomatis dipindahkan ke luar layar (*off-screen*) saat otomasi berjalan, sehingga membuka/menutup tab tidak merebut fokus layar atau mengganggu pekerjaan Anda di Mac.
4. **Alur Otomatis Penuh**:
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
6. Chrome akan berjalan di background dan Anda bebas melanjutkan pekerjaan lain di Mac.
