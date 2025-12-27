from bson.objectid import ObjectId
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from face_engine import FaceEngine

app = Flask(__name__)
app.secret_key = "kunci_rahasia_sistem_absensi"

# --- 1. KONEKSI MONGODB ATLAS ---
MONGO_URI = "mongodb+srv://ayerell:farell240507@cluster0.iepzxdd.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['db_absensi']
    collection = db['log_absensi']
    print("✅ Terhubung ke MongoDB Atlas")
except Exception as e:
    print(f"❌ Error Koneksi: {e}")

# --- 2. INISIALISASI ENGINE ---
face_engine = FaceEngine(known_faces_dir='known_faces')

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
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', role=session['role'])


@app.route('/riwayat')
def riwayat():
    if 'user' not in session:
        return redirect(url_for('login'))
    logs = list(collection.find().sort("created_at", -1))
    return render_template('riwayat.html', logs=logs)


@app.route('/delete_log/<id>', methods=['POST'])
def delete_log(id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Akses ditolak!"})
    try:
        result = collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            return jsonify({"status": "success", "message": "Data berhasil dihapus!"})
        return jsonify({"status": "error", "message": "Data tidak ditemukan."})
    except:
        return jsonify({"status": "error", "message": "ID tidak valid."})

# --- 5. API PROSES SCAN (VERSI AUTO-SCAN) ---


@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        data = request.json['image']

        # Proses Image
        img = face_engine.process_base64_image(data)

        # Deteksi & Kenali
        status, message, nama = face_engine.recognize_face(img)

        if status == "error":
            return jsonify({"status": "error", "message": message})

        # Jika berhasil dikenali
        tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")

        # --- CEK DUPLIKAT (SUDAH ABSEN ATAU BELUM) ---
        log_ada = collection.find_one({"nama": nama, "tanggal": tgl_hari_ini})

        if log_ada:
            return jsonify({
                "status": "already_present",
                "message": f"{nama} sudah terabsensi hadir",
                "nama": nama
            })

        # --- SIMPAN ABSENSI BARU ---
        collection.insert_one({
            "nama": nama,
            "tanggal": tgl_hari_ini,
            "waktu": datetime.now().strftime("%H:%M:%S"),
            "created_at": datetime.now()
        })

        return jsonify({
            "status": "success",
            "message": f"Berhasil Absen: {nama}",
            "nama": nama
        })

    except Exception as e:
        print(f"❌ Error Processing: {e}")
        return jsonify({"status": "error", "message": "Terjadi kesalahan sistem."})


@app.route('/tambah_wajah', methods=['GET', 'POST'])
def tambah_wajah():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        nama = request.form['nama']
        img_data = request.form['image_base64']

        success, msg = face_engine.register_face(nama, img_data)

        if success:
            return jsonify({"status": "success", "message": msg})
        else:
            return jsonify({"status": "error", "message": msg})

    return render_template('tambah_wajah.html')


@app.route('/api/today_log')
def today_log():
    tgl = datetime.now().strftime("%Y-%m-%d")
    logs = list(collection.find({"tanggal": tgl}).sort("created_at", -1))
    return jsonify([{"nama": l['nama'], "waktu": l['waktu']} for l in logs])


if __name__ == '__main__':
    app.run(debug=True)

    # app.run(host='0.0.0.0', port=1324)
    app.run(host='localhost', port=1324)
