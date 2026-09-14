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
   - Menunggu data assignment tersinkronisasi sempurna sebelum klik approve.
   - Menunggu mutasi konfirmasi selesai diproses di server sebelum menutup tab.
   - Menutup tab assignment dan menutup modal review.
5. **Auto Pagination**: Otomatis berpindah ke halaman berikutnya saat semua baris data di halaman aktif selesai diproses.
6. **Anti-Screen Off (Layar Tetap Menyala)**: Otomatis mencegah layar mati (*screen off*) atau komputer tidur (*sleep*) selama otomasi berlangsung di macOS (`caffeinate`), Windows (`SetThreadExecutionState`), dan Linux (`xset`).

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

## ⚙️ Pengaturan Delay (Opsional)
Jika koneksi internet atau server FASIH sedang lambat, Anda dapat menyesuaikan jeda waktu pada baris 45-50 di `auto_approve.py`:
- `DELAY_AFTER_TAB_LOAD`: Jeda setelah tab terbuka sebelum klik tombol approve (default: `3.5` detik).
- `DELAY_BEFORE_CONFIRM`: Jeda pada modal sebelum klik 'Konfirmasi' (default: `1.5` detik).
- `DELAY_AFTER_CONFIRM`: Jeda setelah klik 'Konfirmasi' agar status tersimpan (default: `3.5` detik).
