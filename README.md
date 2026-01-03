
# AbsensiPro: Face Recognition Attendance System

**Sistem Absensi Berbasis Pengenalan Wajah dengan Antarmuka Modern Dark Glassmorphism.**


**Projek Semester 1 - Algoritma Pemrograman 1C**
**Kontributor: Kelas 1KB04 - Sistem Komputer - Universitas Gunadarma**

---

## Ikhtisar

**AbsensiPro** adalah solusi manajemen kehadiran real-time yang mengintegrasikan algoritma visi komputer tingkat tinggi dengan teknologi cloud. Dirancang untuk kelas **1KB04 Universitas Gunadarma**, sistem ini menawarkan akurasi deteksi yang dioptimalkan dan penyimpanan database terpusat menggunakan MongoDB Atlas.

### Fitur Utama

* **Real-time Recognition**: Deteksi dan identifikasi wajah secara instan.
* **Modern UI/UX**: Antarmuka berbasis *Dark Glassmorphism* dengan animasi *scanning line* yang halus.
* **Admin Dashboard**: Kendali penuh untuk registrasi wajah baru dan manajemen data log.
* **Cloud Integration**: Penyimpanan log kehadiran permanen dan aman di MongoDB Atlas.
* **Anti-Spam System**: Mekanisme *cooldown* 10 detik untuk mencegah duplikasi data absensi dalam waktu singkat.

---

## Analisis Algoritma (Berdasarkan Referensi Ilmiah)

Sistem ini mengintegrasikan metodologi Computer Vision yang berfokus pada ketahanan deteksi di berbagai kondisi lingkungan. Arsitektur logika sistem didasarkan pada tiga pilar utama:
1. Preprocessing: Contrast Limited Adaptive Histogram Equalization (CLAHE)

Berdasarkan paper Optimalisasi Deteksi Wajah Dlib-HOG, tantangan utama deteksi adalah rendahnya kontras pada citra. Sistem ini menerapkan CLAHE untuk mendistribusikan ulang nilai intensitas piksel secara adaptif.

Berbeda dengan Histogram Equalization (HE) standar yang menggunakan transformasi global:
### $$s=T(r)=∫0r​pr​(w)dw$$

CLAHE membatasi penguatan kontras dengan memotong histogram pada ambang batas (clip limit) tertentu untuk menghindari amplifikasi noise. Nilai piksel baru dihitung secara interpolasi antar ubin (tiles) lokal, sehingga menghasilkan citra yang lebih jelas bagi algoritma HOG untuk mengekstraksi fitur wajah meski dalam kondisi cahaya redup (meningkatkan akurasi hingga 96,4%).
2. Deteksi Wajah: Histogram of Oriented Gradients (HOG)

Sistem menggunakan Dlib-HOG yang bekerja dengan menangkap struktur bentuk (garis dan tepi) wajah. Proses matematisnya meliputi:

Perhitungan Gradien: Menghitung besarnya perubahan intensitas pada sumbu x dan y menggunakan kernel filter:

### $$Gx=I(x+1,y)−I(x−1,y)$$
### $$Gy=I(x,y+1)−I(x,y−1)$$

Magnitudo dan Orientasi: Menentukan kekuatan tepi dan arah sudutnya:
### $$Magnitude ∣G∣=Gx2+Gy2​​,θ=arctan(GxGy​​)$$

Vektorisasi: Nilai-nilai ini dikelompokkan ke dalam sel dan blok untuk membentuk deskriptor fitur yang tahan terhadap perubahan cahaya global.

3. Ekstraksi Fitur: 128-D Facial Embeddings

Setelah wajah terdeteksi, sistem menggunakan Deep Metric Learning untuk mengubah gambar wajah menjadi titik koordinat dalam ruang multidimensi.

Landmark Detection: Mengidentifikasi 68 titik kunci (eyes, eyebrows, nose, mouth, jawline).

Euclidean Distance: Untuk mengenali wajah, sistem menghitung jarak antara vektor wajah input (d) dengan vektor wajah yang tersimpan di database (k). Identitas dikonfirmasi jika jaraknya berada di bawah ambang batas (threshold):
### $$dist(d,k)=i=1∑n​(di​−ki​)^2$$

Di mana n=128. Jika dist<0.6, maka wajah dianggap cocok (match).

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
```bash
pip install -r requirements.txt
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

---

## Catatan Teknis

* **Kualitas Kamera**: Gunakan kamera dengan resolusi minimal 720p untuk hasil terbaik.
* **Pencahayaan**: Pastikan wajah menghadap sumber cahaya saat pendaftaran.
* **Keamanan**: Data wajah diproses secara lokal di server sebelum dikirim ke database dalam bentuk log teks (bukan gambar mentah), sehingga menjaga privasi pengguna.

---

Sumber Referensi:
- Analysis of Face Recognition Algorithm: Dlib and OpenCV (https://www.researchgate.net/publication/343718108_Analysis_of_Face_Recognition_Algorithm_Dlib_and_OpenCV)
- OPTIMALISASI DETEKSI WAJAH DLIB-HOG
PADA CITRA INTENSITAS RENDAH DENGAN
PREPROCESSING CLAHE (https://ejournal1.unud.ac.id/index.php/spektrum/article/view/3427)
