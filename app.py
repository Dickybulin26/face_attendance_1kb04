import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from face_engine import FaceEngine
from dotenv import load_dotenv
from utils import compress_base64_image
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# ============================================
# 1. FUNGSI GOOGLE SHEETS
# ============================================


def log_to_sheets(user_name, user_id):
    try:
        # Setup koneksi
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.getenv("GOOGLE_SHEETS_CREDENTIALS"), scope)
        client = gspread.authorize(creds)

        # Buka spreadsheet (Pastikan nama file di Google Drive SAMA PERSIS)
        sheet = client.open(os.getenv("GOOGLE_SHEETS_NAME")).sheet1

        # Siapkan data
        now = datetime.now()
        date_string = now.strftime("%d-%m-%Y")
        time_string = now.strftime("%H:%M:%S")

        row = [date_string, time_string, user_name, user_id]

        # Masukkan data ke baris terakhir
        sheet.append_row(row)
        print(f"✅ Berhasil mencatat absen {user_name} ke Google Sheets")

    except Exception as e:
        print(f"❌ Gagal menyambung ke Sheets: {e}")


# ============================================
# 2. KONEKSI DATABASE & ENGINE
# ============================================
MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    db = client['db_absensi']
    collection = db['log_absensi']        # Riwayat Absen
    users_collection = db['daftar_wajah']  # Data Wajah
    print("✅ Berhasil Terhubung ke MongoDB Atlas")
except Exception as e:
    print(f"❌ Gagal Database: {e}")

if not os.path.exists('known_faces'):
    os.makedirs('known_faces')
face_engine = FaceEngine(known_faces_dir='known_faces')

# ============================================
# 3. AUTHENTICATION & HELPERS
# ============================================
USERS = {"admin": "123", "user": "123"}


def is_logged_in():
    return 'user' in session


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle AJAX/JSON Login
        if request.is_json:
            data = request.json
            user = data.get('username')
            pw = data.get('password')
            if user in USERS and USERS[user] == pw:
                session['user'] = user
                session['role'] = 'admin' if user == 'admin' else 'user'
                session['logged_in'] = True
                return jsonify({"status": "success", "redirect": url_for('index')})
            return jsonify({"status": "error", "message": "Username atau Password salah!"})

        # Handle Standard Form Login
        user = request.form['username']
        pw = request.form['password']
        if user in USERS and USERS[user] == pw:
            session['user'] = user
            session['role'] = 'admin' if user == 'admin' else 'user'
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Username atau Password salah!")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ============================================
# 4. PAGE ROUTES
# ============================================


@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html', role=session.get('role'))


@app.route('/riwayat')
def riwayat():
    if not is_logged_in():
        return redirect(url_for('login'))
    role = session.get('role')
    user_sekarang = session.get('user')
    if role == 'admin':
        logs = list(collection.find().sort("created_at", -1))
    else:
        logs = list(collection.find(
            {"nama": user_sekarang}).sort("created_at", -1))
    for log in logs:
        log['id'] = str(log['_id'])
    return render_template('riwayat.html', logs=logs, role=role)


@app.route('/daftar_user')
def daftar_user():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    users = list(users_collection.find().sort("nama", 1))
    return render_template('daftar_user.html', users=users, role=session.get('role'))


@app.route('/tambah_wajah')
def tambah_wajah_view():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    return render_template('tambah_wajah.html', role=session.get('role'))

# ============================================
# 5. API MANAGEMENT (EDIT/DELETE)
# ============================================


@app.route('/edit_user/<id>', methods=['POST'])
def edit_user(id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error"})
    new_nama = request.json.get('nama')
    try:
        users_collection.update_one({"_id": ObjectId(id)}, {
                                    "$set": {"nama": new_nama}})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})


@app.route('/delete_user/<id>', methods=['POST'])
def delete_user(id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error"})
    try:
        users_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})


@app.route('/delete_log/<id>', methods=['POST'])
def delete_log(id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error"}), 403
    try:
        collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})


@app.route('/clear_logs')
def clear_logs():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    collection.delete_many({})
    return redirect(url_for('riwayat'))

# ============================================
# 6. CORE FACE RECOGNITION API
# ============================================


@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        data = request.json['image']
        img = face_engine.process_base64_image(data)
        status, message, nama = face_engine.recognize_face(img)

        if status == "error":
            return jsonify({"status": "error", "message": message})

        tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")

        # Cek apakah sudah absen hari ini di MongoDB
        log_ada = collection.find_one({"nama": nama, "tanggal": tgl_hari_ini})
        if log_ada:
            return jsonify({"status": "already_present", "nama": nama})

        # A. Simpan ke MongoDB
        collection.insert_one({
            "nama": nama,
            "tanggal": tgl_hari_ini,
            "waktu": datetime.now().strftime("%H:%M:%S"),
            "created_at": datetime.now()
        })

        # B. KIRIM KE GOOGLE SHEETS
        # Menggunakan ID singkat dari nama atau UID statis
        u_id = f"ID-{(nama[:3]).upper()}"
        log_to_sheets(nama, u_id)

        return jsonify({"status": "success", "nama": nama})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route('/register_face', methods=['POST'])
def register_face():
    if session.get('role') != 'admin':
        return jsonify({"status": "error"})
    data = request.json
    nama = data.get('nama')
    img_data = data.get('image')
    
    # Register face with original image for face recognition
    success, msg = face_engine.register_face(nama, img_data)
    
    if success:
        # Compress image for database storage (preview only)
        try:
            compressed_image = compress_base64_image(img_data, max_width=400, quality=85)
            print(f"✅ Image compressed successfully for {nama}")
        except Exception as e:
            print(f"⚠️ Image compression failed, using original: {e}")
            compressed_image = img_data
        
        # Save to database with compressed image
        users_collection.insert_one({
            "nama": nama,
            "created_at": datetime.now(),
            "image_preview": compressed_image
        })
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg})

# ============================================
# 7. CALENDAR & UTILITY
# ============================================


@app.route('/api/today_log')
def today_log():
    tgl = datetime.now().strftime("%Y-%m-%d")
    role = session.get('role')
    user_sekarang = session.get('user')
    query = {"tanggal": tgl}
    if role != 'admin':
        query["nama"] = user_sekarang
    logs = list(collection.find(query).sort("created_at", -1))
    return jsonify([{"nama": l.get('nama', 'Unknown'), "waktu": l['waktu']} for l in logs])


@app.route('/api/calendar_events')
def calendar_events():
    if not is_logged_in():
        return jsonify([])
    role = session.get('role')
    user_sekarang = session.get('user')
    events = []
    if role == 'admin':
        pipeline = [{"$group": {"_id": "$tanggal", "count": {"$sum": 1}, "details": {
            "$push": {"nama": {"$ifNull": ["$nama", "Unknown"]}, "waktu": "$waktu"}}}}]
        logs_grouped = list(collection.aggregate(pipeline))
        for g in logs_grouped:
            events.append({"title": str(g['count']), "start": g['_id'], "extendedProps": {
                          "is_admin": True, "count": g['count'], "users": g['details']}, "backgroundColor": "transparent", "borderColor": "transparent"})
    else:
        logs = list(collection.find({"nama": user_sekarang}))
        for l in logs:
            events.append({"title": "Hadir", "start": l['tanggal'], "extendedProps": {"is_admin": False, "nama": l.get(
                'nama', user_sekarang), "waktu": l['waktu']}, "backgroundColor": "transparent", "borderColor": "transparent"})
    return jsonify(events)


if __name__ == '__main__':
    host = os.getenv("FLASK_HOST")
    port = os.getenv("FLASK_PORT")
    debug = os.getenv("FLASK_DEBUG")
    app.run(host=host, port=port, debug=debug)
