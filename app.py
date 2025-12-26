from bson.objectid import ObjectId
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
import face_recognition
import cv2
import numpy as np
import os
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = "kunci_rahasia_sistem_absensi"

# --- 1. KONEKSI MONGODB ATLAS ---
MONGO_URI = "mongodb+srv://ayerell:farell240507@cluster0.iepzxdd.mongodb.net/?appName=Cluster0"

@app.route('/delete_log/<id>', methods=['POST'])
def delete_log(id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Akses ditolak!"})
    
    try:
        # Konversi string ID dari URL menjadi ObjectId MongoDB
        result = db.log_absensi.delete_one({"_id": ObjectId(id)})
        
        if result.deleted_count > 0:
            return jsonify({"status": "success", "message": "Data berhasil dihapus!"})
        else:
            return jsonify({"status": "error", "message": "Data tidak ditemukan di database."})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Format ID tidak valid."})
    
try:
    client = MongoClient(MONGO_URI)
    db = client['db_absensi']
    collection = db['log_absensi']
    print("✅ Terhubung ke MongoDB Atlas")
except Exception as e:
    print(f"❌ Error Koneksi: {e}")

# --- 2. KONFIGURASI WAJAH ---
KNOWN_FACES_DIR = 'known_faces'
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

known_face_encodings = []
known_face_names = []

def reload_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)
            if enc:
                known_face_encodings.append(enc[0])
                known_face_names.append(os.path.splitext(filename)[0])
    print(f"🔄 Database wajah dimuat: {len(known_face_names)} orang.")

reload_faces()

# --- 3. SISTEM LOGIN ---
USERS = {"admin": "123", "user": "123"}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user in USERS and USERS[user] == pw:
            session['user'] = user
            session['role'] = 'admin' if user == 'admin' else 'user'
            return redirect(url_for('index'))
        return "Login Gagal!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 4. HALAMAN UTAMA & RIWAYAT ---
@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', role=session['role'])

@app.route('/riwayat')
def riwayat():
    if 'user' not in session: return redirect(url_for('login'))
    logs = list(collection.find().sort("created_at", -1))
    return render_template('riwayat.html', logs=logs)

# --- 5. API PROSES SCAN & REGISTRASI ---
@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json['image']
    header, encoded = data.split(",", 1)
    nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_img)
    encs = face_recognition.face_encodings(rgb_img, face_locations)

    if not encs:
        return jsonify({"status": "error", "message": "Wajah tidak terdeteksi!"})

    matches = face_recognition.compare_faces(known_face_encodings, encs[0])
    if True in matches:
        nama = known_face_names[matches.index(True)]
        tgl = datetime.now().strftime("%Y-%m-%d")
        
        # Cek Duplikat di MongoDB
        if collection.find_one({"nama": nama, "tanggal": tgl}):
            return jsonify({"status": "warning", "message": f"{nama} sudah absen hari ini."})
        
        # Simpan
        collection.insert_one({
            "nama": nama, "tanggal": tgl,
            "waktu": datetime.now().strftime("%H:%M:%S"),
            "created_at": datetime.now()
        })
        return jsonify({"status": "success", "message": f"Berhasil Absen: {nama}"})
    
    return jsonify({"status": "error", "message": "Wajah tidak dikenal."})

@app.route('/tambah_wajah', methods=['GET', 'POST'])
def tambah_wajah():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    if request.method == 'POST':
        nama = request.form['nama'].lower().replace(" ", "_")
        img_data = request.form['image_base64'].split(",")[1]
        with open(f"{KNOWN_FACES_DIR}/{nama}.jpg", "wb") as f:
            f.write(base64.b64decode(img_data))
        reload_faces()
        return jsonify({"status": "success", "message": f"Wajah {nama} berhasil didaftarkan!"})
    return render_template('tambah_wajah.html')

@app.route('/api/today_log')
def today_log():
    tgl = datetime.now().strftime("%Y-%m-%d")
    logs = list(collection.find({"tanggal": tgl}).sort("created_at", -1))
    return jsonify([{"nama": l['nama'], "waktu": l['waktu']} for l in logs])

if __name__ == '__main__':
    app.run(debug=True)