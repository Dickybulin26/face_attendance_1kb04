import face_recognition
import cv2
import numpy as np
import base64
import os

class FaceEngine:
    def __init__(self, known_faces_dir='known_faces'):
        self.known_faces_dir = known_faces_dir
        self.known_encodings = []
        self.known_names = []
        # Memanggil fungsi load saat pertama kali dijalankan
        self.load_known_faces()

    def load_known_faces(self):
        """Memuat ulang database wajah dari folder ke memori"""
        self.known_encodings = []
        self.known_names = []
        
        # Buat folder jika belum ada
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            
        print("🔄 Sedang memuat ulang database wajah...")
        
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.known_faces_dir, filename)
                try:
                    image = face_recognition.load_image_file(path)
                    encoding = face_recognition.face_encodings(image)
                    if encoding:
                        self.known_encodings.append(encoding[0])
                        self.known_names.append(os.path.splitext(filename)[0])
                except Exception as e:
                    print(f"⚠️ Gagal memuat {filename}: {e}")
        
        print(f"✅ Database siap! Total user: {len(self.known_names)}")

    def process_base64_image(self, base64_string):
        """Mengubah string dari webcam menjadi gambar OpenCV"""
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Optimasi Gambar: Cerahkan sedikit agar deteksi lebih mudah
        img = cv2.convertScaleAbs(img, alpha=1.1, beta=10)
        
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def recognize_face(self, rgb_img):
        """Proses Absensi (Scan)"""
        # Upsample 1x cukup untuk scanning cepat
        face_locations = face_recognition.face_locations(rgb_img)
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

        if not face_encodings:
            return "error", "Wajah tidak terdeteksi", None

        for face_encoding in face_encodings:
            # Tolerance 0.5 agar akurat
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    nama = self.known_names[best_match_index]
                    return "success", "Wajah dikenali", nama

        return "error", "Wajah tidak dikenal", None

    def register_face(self, nama, base64_image):
        """Proses Pendaftaran Wajah Baru (Lebih Teliti)"""
        try:
            img_rgb = self.process_base64_image(base64_image)
            
            # --- FITUR ANTI GAGAL DETEKSI ---
            # number_of_times_to_upsample=2 artinya zoom in 2x secara digital
            # Ini mengatasi masalah webcam yang resolusinya rendah/pecah
            face_locations = face_recognition.face_locations(img_rgb, number_of_times_to_upsample=2)
            
            if not face_locations:
                # Coba sekali lagi dengan kontras tinggi jika gagal
                img_enhanced = cv2.convertScaleAbs(img_rgb, alpha=1.5, beta=20)
                face_locations = face_recognition.face_locations(img_enhanced, number_of_times_to_upsample=2)
                
                if not face_locations:
                    return False, "Wajah tidak ditemukan. Coba mendekat ke kamera."

            # Ambil encoding
            face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
            
            if not face_encodings:
                return False, "Wajah terdeteksi tapi buram. Pastikan cahaya cukup."

            # Simpan File
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            file_path = os.path.join(self.known_faces_dir, f"{nama}.jpg")
            cv2.imwrite(file_path, img_bgr)
            
            # --- PENTING: RELOAD AGAR TIDAK ERROR ---
            self.load_known_faces() 
            
            return True, f"Berhasil! Wajah {nama} disimpan."

        except Exception as e:
            print(f"Error Register: {str(e)}")
            return False, f"System Error: {str(e)}"