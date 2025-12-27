from bson.objectid import ObjectId
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from face_engine import FaceEngine
import os

app = Flask(__name__)
app.secret_key = "kunci_rahasia_sistem_absensi_pro"

# --- 1. KONEKSI MONGODB ATLAS ---
MONGO_URI = "mongodb+srv://ayerell:farell240507@cluster0.iepzxdd.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['db_absensi']
    collection = db['log_absensi']        # Koleksi Riwayat Absen
    users_collection = db['daftar_wajah']  # Koleksi Data Wajah Terdaftar
    print("✅ Berhasil Terhubung ke MongoDB Atlas")
except Exception as e:
    print(f"❌ Gagal Terhubung ke Database: {e}")

# --- 2. INISIALISASI ENGINE ---
if not os.path.exists('known_faces'):
    os.makedirs('known_faces')
face_engine = FaceEngine(known_faces_dir='known_faces')

# --- 3. HELPER / MIDDLEWARE ---
def is_logged_in():
    return 'user' in session

# Data Dummy Login
USERS = {"admin": "123", "user": "123"}

# --- 4. AUTHENTICATION ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user in USERS and USERS[user] == pw:
            session['user'] = user
            session['role'] = 'admin' if user == 'admin' else 'user'
            return redirect(url_for('index'))
        return render_template('login.html', error="Username atau Password salah!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 5. MAIN PAGE ROUTES ---

@app.route('/')
def index():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('index.html', role=session.get('role'))

@app.route('/riwayat')
def riwayat():
    if not is_logged_in(): return redirect(url_for('login'))
    
    role = session.get('role')
    user_sekarang = session.get('user')
    
    if role == 'admin':
        logs = list(collection.find().sort("created_at", -1))
    else:
        logs = list(collection.find({"nama": user_sekarang}).sort("created_at", -1))
        
    return render_template('riwayat.html', logs=logs, role=role)

@app.route('/daftar_user')
def daftar_user():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    users = list(users_collection.find().sort("nama", 1))
    return render_template('daftar_user.html', users=users, role=session.get('role'))

@app.route('/tambah_wajah')
def tambah_wajah_view():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    return render_template('tambah_wajah.html', role=session.get('role'))

# --- 6. USER & LOG MANAGEMENT API ---

@app.route('/edit_user/<id>', methods=['POST'])
def edit_user(id):
    if session.get('role') != 'admin': return jsonify({"status": "error"})
    new_nama = request.json.get('nama')
    try:
        users_collection.update_one({"_id": ObjectId(id)}, {"$set": {"nama": new_nama}})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})

@app.route('/delete_user/<id>', methods=['POST'])
def delete_user(id):
    if session.get('role') != 'admin': return jsonify({"status": "error"})
    try:
        users_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})

@app.route('/delete_log/<id>', methods=['POST'])
def delete_log(id):
    if session.get('role') != 'admin': return jsonify({"status": "error"})
    try:
        collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})

# --- 7. FACE ENGINE API ---

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        data = request.json['image']
        img = face_engine.process_base64_image(data)
        status, message, nama = face_engine.recognize_face(img)

        if status == "error":
            return jsonify({"status": "error", "message": message})

        tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
        log_ada = collection.find_one({"nama": nama, "tanggal": tgl_hari_ini})
        
        if log_ada:
            return jsonify({"status": "already_present", "nama": nama})

        collection.insert_one({
            "nama": nama,
            "tanggal": tgl_hari_ini,
            "waktu": datetime.now().strftime("%H:%M:%S"),
            "created_at": datetime.now()
        })
        return jsonify({"status": "success", "nama": nama})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/register_face', methods=['POST'])
def register_face():
    if session.get('role') != 'admin': return jsonify({"status": "error"})
    data = request.json
    nama = data.get('nama')
    img_data = data.get('image')
    success, msg = face_engine.register_face(nama, img_data)

    if success:
        users_collection.insert_one({
            "nama": nama,
            "created_at": datetime.now(),
            "image_preview": img_data 
        })
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg})

# --- 8. UTILITY API (UPDATED FOR CALENDAR BUG) ---

@app.route('/api/today_log')
def today_log():
    tgl = datetime.now().strftime("%Y-%m-%d")
    role = session.get('role')
    user_sekarang = session.get('user')
    query = {"tanggal": tgl}
    if role != 'admin': query["nama"] = user_sekarang
    logs = list(collection.find(query).sort("created_at", -1))
    return jsonify([{"nama": l.get('nama', 'Unknown'), "waktu": l['waktu']} for l in logs])

@app.route('/api/calendar_events')
def calendar_events():
    if not is_logged_in(): return jsonify([])
    
    role = session.get('role')
    user_sekarang = session.get('user')
    events = []
    
    if role == 'admin':
        # Perbaikan bug: Menggunakan nama asli dari database, jika tidak ada pakai 'Unknown'
        pipeline = [
            {"$group": {
                "_id": "$tanggal",
                "count": {"$sum": 1},
                "details": {"$push": {"nama": {"$ifNull": ["$nama", "Unknown"]}, "waktu": "$waktu"}}
            }}
        ]
        logs_grouped = list(collection.aggregate(pipeline))
        for g in logs_grouped:
            events.append({
                "title": str(g['count']), # Mengirim angka sebagai string
                "start": g['_id'],
                "extendedProps": {
                    "is_admin": True, 
                    "count": g['count'], 
                    "users": g['details']
                },
                "backgroundColor": "transparent",
                "borderColor": "transparent"
            })
    else:
        logs = list(collection.find({"nama": user_sekarang}))
        for l in logs:
            events.append({
                "title": "Hadir",
                "start": l['tanggal'],
                "extendedProps": {
                    "is_admin": False, 
                    "nama": l.get('nama', user_sekarang),
                    "waktu": l['waktu']
                },
                "backgroundColor": "transparent",
                "borderColor": "transparent"
            })
    return jsonify(events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1324, debug=True)