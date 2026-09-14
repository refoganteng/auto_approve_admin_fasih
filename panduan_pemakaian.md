# 📖 Panduan Otomasi Approve Admin Kabupaten FASIH-SM (SE2026)

Panduan lengkap penggunaan script otomasi persetujuan (*approval*) data Sensus Ekonomi 2026 pada sistem FASIH-SM BPS.

---

## 🚀 Fitur Utama Script

1. **Anti-Bot & Bebas Blokir**: Menggunakan Google Chrome asli via CDP (*Chrome DevTools Protocol*), menghindari injeksi automation flag yang biasa dideteksi oleh sistem pengaman BPS.
2. **Sesi Persisten**: Cookie, token, dan sesi login disimpan di folder `./chrome_debug_profile`. Anda tidak perlu login ulang berulang kali jika sesi masih berlaku.
3. **Alur Otomatis Penuh Sesuai Permintaan**:
   - Klik kode identitas assignment di tabel `halaman_data.html`.
   - Klik tombol **Review** pada modal `modal_review.html`.
   - Menunggu seluruh data dan state survei tersinkronisasi penuh (`networkidle` + jeda 3.5 detik).
   - Klik tombol **Approve** (checklist hijau `btn_approve.html`).
   - Jeda 1.5 detik pada modal konfirmasi, lalu klik tombol **Konfirmasi**.
   - Menunggu **3.5 detik** agar request approval selesai diproses & tersimpan di server FASIH.
   - Menutup tab assignment secara otomatis.
   - Menutup modal review di halaman utama.
4. **Auto Pagination**: Otomatis klik tombol **Next Page** setelah seluruh data (misal 100 data) di halaman aktif selesai di-approve.
5. **Eksekusi Langsung Baris demi Baris**: Tidak bergantung pada file riwayat eksternal. Karena Anda selalu memfilter manual di awal, bot akan langsung memproses seluruh baris data yang tampil di tabel secara berurutan.
6. **Tata Letak Split-Screen (Setengah Kanan untuk Chrome, Kiri untuk Terminal)**: Saat dijalankan, jendela Google Chrome otomatis diposisikan di setengah layar sebelah KANAN, dan Terminal di sebelah KIRI. Anda dapat memantau log terminal di kiri sambil melihat proses browser di kanan tanpa saling tumpang tindih. Fokus pengetikan Anda juga tetap terkunci di Terminal.
7. **Anti-Screen Off (Layar Tetap Menyala)**: Otomatis menjaga layar dan sistem agar tidak mati (*screen off*) atau tidur (*sleep*) selama proses approval berlangsung di macOS, Windows, maupun Linux.

---

## 🛠️ Prasyarat

Pastikan dependensi Python sudah terpasang:
```bash
pip install playwright playwright-stealth
```

---

## 📋 Cara Menjalankan

### Langkah 1: Jalankan Script di Terminal
Buka terminal di folder project ini:
```bash
python3 auto_approve.py
```

### Langkah 2: Browser Google Chrome Terbuka
- Jendela Google Chrome akan otomatis terbuka mengarah ke `https://fasih-sm.bps.go.id/`.
- Silakan **LOGIN** dengan akun Anda jika belum login.

### Langkah 3: Navigasi & Filter Data Secara Manual
1. Buka menu survei **SENSUS EKONOMI 2026** -> **PENDATAAN** -> **Data**.
2. Pasang filter status: **`EDITED BY ADMIN KABUPATEN`**.
3. Atur jumlah data per halaman menjadi **100 data**.
4. Pastikan tabel data sudah muncul di layar Chrome.

### Langkah 4: Mulai Otomasi
Kembali ke terminal tempat script berjalan, lalu tekan:
```
ENTER
```
Script akan langsung memproses assignment satu per satu, berpindah tab, melakukan konfirmasi, menutup tab, hingga berpindah ke halaman berikutnya secara otomatis!

---

## ⏹️ Menghentikan Otomasi
Jika ingin berhenti sewaktu-waktu, cukup tekan:
```
Ctrl + C
```
pada terminal. Program akan berhenti secara bersih.

---

## 📁 Struktur File
```
complete_by_admin_fasih/
├── auto_approve.py         # Script utama otomasi
├── panduan_pemakaian.md    # Panduan ini
├── chrome_debug_profile/   # Profil browser & cookies sesi (otomatis dibuat)
├── referensi/              # Script referensi anti-bot sebelumnya
└── *.html                  # File referensi komponen UI FASIH-SM
```
