
# AbsensiPro: Face Recognition Attendance System

**Sistem Absensi Berbasis Pengenalan Wajah dengan Antarmuka Modern Dark Glassmorphism.**


**Projek Semester 1 - Algoritma Pemrograman 1C**<br>
**Kontributor: Kelas 1KB04 - Sistem Komputer - Universitas Gunadarma**

---

## Ikhtisar

**AbsensiPro** adalah solusi manajemen kehadiran real-time yang mengintegrasikan algoritma visi komputer tingkat tinggi dengan teknologi cloud. Dirancang untuk kelas **1KB04 Jurusan Sistem Komputer Universitas Gunadarma**, sistem ini menawarkan akurasi deteksi yang dioptimalkan dan penyimpanan database terpusat menggunakan MongoDB Atlas.

### Fitur Utama

* **Real-time Recognition**: Deteksi dan identifikasi wajah secara instan.
* **Modern UI/UX**: Antarmuka berbasis *Dark Glassmorphism* dengan animasi *scanning line* yang halus.
* **Admin Dashboard**: Kendali penuh untuk registrasi wajah baru dan manajemen data log.
* **Cloud Integration**: Penyimpanan log kehadiran permanen dan aman di MongoDB Atlas.
* **Anti-Spam System**: Mekanisme *cooldown* 10 detik untuk mencegah duplikasi data absensi dalam waktu singkat.

---

## Analisis Algoritma (Berdasarkan Referensi Ilmiah)

Sistem ini menerapkan pipeline pengenalan wajah biometrik yang terdiri dari empat tahapan utama. Sistem menggunakan metode gabungan HOG + Linear SVM Classification untuk mendeteksi wajah dan metode Euclidean Distance mengidentifikasi wajah.

**1. Pra-pemrosesan Citra (Image Pre-processing)**

Sebelum masuk ke tahap deteksi, citra yang diterima dari stream Base64 mengalami penyesuaian kontras dan kecerahan menggunakan operasi linear pada setiap piksel.

### $$g(x,y)=α⋅I(x,y)+β$$

(Dimana α=1.1 dan β=10)

**2. Deteksi Wajah: HOG & Linear SVM**

<img src="https://media.geeksforgeeks.org/wp-content/uploads/20250605131337992934/Output-Image.jpg" width="700" />

Tahap ini bertujuan untuk menemukan lokasi koordinat wajah (bounding box) dalam gambar. Fungsi face_locations pada sistem secara internal mengimplementasikan algoritma Histogram of Oriented Gradients (HOG) yang diklasifikasikan oleh Linear SVM.

<img src="https://user-images.githubusercontent.com/69381013/210751911-ecfa8517-eb60-4d47-b69a-164137d24ed1.png" width="700" />

A. Ekstraksi Fitur HOG Sistem menghitung perubahan intensitas piksel (gradien) untuk menangkap kontur wajah.

Magnitudo Gradien:
### $$M(x,y)=G_x(x,y)^2+G_y(x,y)^2$$

Orientasi Gradien:
### $$\theta(x,y)=arctan(G_x(x,y)G_y(x,y))$$

B. Klasifikasi Area Wajah (Linear SVM) Setelah fitur HOG terbentuk, algoritma Linear SVM digunakan untuk memisahkan area "Wajah" dan "Bukan Wajah". SVM bekerja dengan mencari hyperplane pemisah dengan margin maksimal:

### $$f(x)=sign(w^Tx+b)$$

Jika f(x)>0, maka area tersebut dikonfirmasi sebagai wajah dan diteruskan ke tahap selanjutnya.

**3. Ekstraksi Fitur: 128-D Deep Metric Learning**

Wajah yang telah dideteksi (di-crop) kemudian diproses oleh jaringan saraf tiruan (ResNet-34) untuk diubah menjadi vektor numerik 128 dimensi (embedding).

### $$v=f_{ResNet}(x)$$

**4. Klasifikasi Identitas: Euclidean Distance**

Untuk menentukan identitas pengguna (misal: "Apakah ini Budi?"), sistem tidak menggunakan SVM, melainkan menggunakan pendekatan geometris Euclidean Distance.

Sistem menghitung jarak L2 antara vektor wajah input (S) dan vektor di database (V).

### $$dist(S,V)=\sum_{i=1}^{128}(S_i-V_i)^2$$

Identitas ditentukan dengan mencari jarak terpendek (minimum distance):

### $$ID=argmin_k(d(S,V_k))$$

Jika jarak d<0.5, wajah dianggap valid.

---

## Panduan Instalasi

### Prasyarat

* Python 3.11+
* Docker & Docker Compose (Opsional)
* Akun MongoDB Atlas

### Instalasi Lokal

1. **Kloning Repositori**
```bash
git clone https://github.com/Dickybulin26/face_attendance_1kb04.git
cd face_attendance_1kb04
```


2. **Konfigurasi Database**
Edit `app.py` dan masukkan URI MongoDB Atlas Anda:
```python
MONGO_URI = "mongodb+srv://USER:PASSWORD@cluster.mongodb.net/db_absensi"
```


3. **Jalankan Aplikasi**
git clone https://github.com/Dickybulin26/face_attendance_1kb04.git
cd face_attendance_1kb04
```


2. **Konfigurasi Database**
Edit `app.py` dan masukkan URI MongoDB Atlas Anda:
```python
MONGO_URI = "mongodb+srv://USER:PASSWORD@cluster.mongodb.net/db_absensi"
```


3. **Jalankan Aplikasi**
```bash
pip install -r requirements.txt
python app.py
```



### Instalasi via Docker

```bash
docker-compose build --no-cache
docker-compose up -d
python app.py
```



### Instalasi via Docker

```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Cara Penggunaan

1. Akses aplikasi di `http://localhost:1324` (atau URL Ngrok jika di-deploy).
2. **Pendaftaran**: Masuk ke menu **Admin > Tambah Wajah**. Ambil foto wajah dengan pencahayaan yang cukup.
3. **Absensi**: Kembali ke Dashboard, sistem akan otomatis melakukan scanning. Jika wajah dikenali, status "Berhasil Absen" akan muncul.
4. **Riwayat**: Pantau kehadiran di tabel **Riwayat**. Admin memiliki otoritas untuk menghapus log jika terjadi kesalahan.
## Cara Penggunaan

1. Akses aplikasi di `http://localhost:1324` (atau URL Ngrok jika di-deploy).
2. **Pendaftaran**: Masuk ke menu **Admin > Tambah Wajah**. Ambil foto wajah dengan pencahayaan yang cukup.
3. **Absensi**: Kembali ke Dashboard, sistem akan otomatis melakukan scanning. Jika wajah dikenali, status "Berhasil Absen" akan muncul.
4. **Riwayat**: Pantau kehadiran di tabel **Riwayat**. Admin memiliki otoritas untuk menghapus log jika terjadi kesalahan.

---

## Catatan Teknis
## Catatan Teknis

* **Kualitas Kamera**: Gunakan kamera dengan resolusi minimal 720p untuk hasil terbaik.
* **Pencahayaan**: Pastikan wajah menghadap sumber cahaya saat pendaftaran.
* **Keamanan**: Data wajah diproses secara lokal di server sebelum dikirim ke database dalam bentuk log teks (bukan gambar mentah), sehingga menjaga privasi pengguna.
* **Kualitas Kamera**: Gunakan kamera dengan resolusi minimal 720p untuk hasil terbaik.
* **Pencahayaan**: Pastikan wajah menghadap sumber cahaya saat pendaftaran.
* **Keamanan**: Data wajah diproses secara lokal di server sebelum dikirim ke database dalam bentuk log teks (bukan gambar mentah), sehingga menjaga privasi pengguna.

---

Sumber Referensi:
- Analysis of Face Recognition Algorithm: Dlib and OpenCV (https://www.researchgate.net/publication/343718108_Analysis_of_Face_Recognition_Algorithm_Dlib_and_OpenCV)
- Histogram of Oriented Gradients (https://www.geeksforgeeks.org/computer-vision/histogram-of-oriented-gradients)
- C34 | HOG Feature Vector Calculation | Computer Vision | Object Detection | EvODN (https://youtu.be/28xk5i1_7Zc)

- C37 | Dalal & Triggs Object Detection | HOG + SVM | Computer Vision | Machine Learning | EvODN (https://youtu.be/sDByl84n5mY)
