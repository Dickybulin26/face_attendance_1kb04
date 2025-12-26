# face_attendance_1kb04

```markdown
# 📷 AbsensiPro - Face Recognition System (Dark Glassmorphism)

Sistem Absensi Berbasis Pengenalan Wajah (Face Recognition) yang dirancang dengan antarmuka modern **Dark Glassmorphism**. Aplikasi ini memungkinkan pencatatan kehadiran secara real-time dengan integrasi database cloud.

---

## ✨ Fitur Unggulan
- 👤 **Real-time Face Recognition**: Menggunakan algoritma pengenalan wajah tingkat tinggi.
- 🌑 **Modern Dark UI**: Tampilan transparan bergaya *glassmorphism* yang nyaman di mata.
- 🛡️ **Admin Control**: Menu khusus untuk registrasi wajah baru dan pengelolaan data.
- ☁️ **Cloud Database**: Tersambung dengan MongoDB Atlas untuk penyimpanan log permanen.
- ⚡ **Smooth Animations**: Efek *scanning line* dan transisi baris tabel yang halus.
- ⏱️ **Anti-Spam System**: Fitur cooldown 10 detik untuk menghindari duplikasi data absensi.

---

## 🛠️ Prasyarat & Instalasi

### 1. Kloning Repositori
```bash
git clone [https://github.com/username-anda/nama-repo-anda.git](https://github.com/username-anda/nama-repo-anda.git)
cd nama-repo-anda

```

### 2. Instalasi Library Python

Pastikan Anda memiliki Python 3.8+ dan compiler C++ (untuk instalasi `dlib`). Jalankan perintah berikut:

```bash
pip install flask pymongo face_recognition opencv-python dlib numpy

```

### 3. Konfigurasi Database

Buka file `app.py` dan sesuaikan koneksi **MongoDB Atlas** Anda:

```python
MONGO_URI = "mongodb+srv://USER:PASSWORD@cluster.xxx.mongodb.net/db_absensi"

```

---

## 📂 Struktur Proyek

```text
├── app.py              # Logic Utama Flask & Pengenalan Wajah
├── known_faces/        # Database Foto Personel (.jpg / .png)
├── templates/          # Folder Tampilan HTML
│   ├── index.html      # Dashboard & Kamera Scan
│   ├── riwayat.html    # Laporan Log Kehadiran
│   └── tambah_wajah.html# Form Registrasi Wajah Baru
└── README.md

```

---

## 🚀 Cara Penggunaan

1. **Jalankan Aplikasi**:
```bash
python app.py

```


2. **Akses Dashboard**: Buka `http://127.0.0.1:5000` di browser Anda.
3. **Pendaftaran**: Gunakan menu **Admin** (Tambah Wajah) untuk mendaftarkan wajah baru dengan kamera.
4. **Absensi**: Di halaman utama, klik **Mulai Scan**. Sistem akan mengenali wajah dan otomatis menyimpan waktu masuk ke database.
5. **Cek Riwayat**: Lihat data yang masuk di halaman **Riwayat** dan Admin dapat menghapus data jika diperlukan.

---

## 🖥️ Tampilan UI

| Dashboard Utama | Laporan Riwayat |
| --- | --- |
|  |  |

---

## ⚠️ Catatan

* **Pencahayaan**: Kualitas pengenalan sangat bergantung pada pencahayaan ruangan saat pendaftaran wajah.
* **Kapasitas**: Untuk performa terbaik, gunakan foto wajah yang jelas (tanpa masker/kacamata hitam saat registrasi).

---

**Kontributor:** 
- Farell Rhezky Alvianto 20125328
- Dicky Asqealani

**Lisensi:** MIT License

```

NOTE : Jangan lupa install Virtual Enviromentnya [ venv]