import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from datetime import datetime, timedelta
from flask import request, jsonify

app = Flask(__name__)
app.secret_key = 'GG_Alfian'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
conn = get_db_connection()
try:
    conn.execute("ALTER TABLE user_progress ADD COLUMN updated_at TEXT")
    conn.commit()
except:
    pass
conn.close()

@app.route('/')
def index():
    fitur_list = [
        {"judul": "Quiz", "desc": "Mengerjakan soal mengenai Networking.", "img": url_for('static', filename='photos/review-quiz.png')},
        {"judul": "Modul TKJ", "desc": "Materi lengkap dari kelas X hingga XII.", "img": url_for('static', filename='photos/review-modul.png')},
        {"judul": "Video Tutorial", "desc": "Belajar teknis lewat panduan visual yang jelas.", "img": url_for('static', filename='photos/review-video.PNG')}
    ]
    guru_all = [
        {"nama": "Pak Husni", "mapel": "Penanggung Jawab Lab 4", "img": url_for('static', filename='photos/foto-pak-husni.JPG')},
        {"nama": "Pak Faisal", "mapel": "Penanggung Jawab Lab 1", "img": url_for('static', filename='photos/foto-pak-faisal.JPG')},
        {"nama": "Pak Gama", "mapel": "Penanggung Jawab Lab 2", "img": url_for('static', filename='photos/foto-pak-gama.JPG')},
        {"nama": "Pak afandi", "mapel": "Penanggung Jawab Lab 3", "img": url_for('static', filename='photos/foto-pak-afandi.JPG')},
        {"nama": "Bu Arini", "mapel": "Kepala Bengkel", "img": url_for('static', filename='photos/foto-bu-arini.JPG')},
        {"nama": "Bu Vera", "mapel": "Penanggung Jawab Lab 7", "img": url_for('static', filename='photos/foto-bu-vera.JPG')},
        {"nama": "Bu Hafni", "mapel": "Penanggung Jawab Lab 6", "img": url_for('static', filename='photos/foto-bu-hafni.JPG')},
        {"nama": "Bu Tutus", "mapel": "Penanggung Jawab Lab 8", "img": url_for('static', filename='photos/foto-bu-tutus.JPG')},
        {"nama": "Pak Rifki", "mapel": "Toolman", "img": url_for('static', filename='photos/foto-pak-rifki.JPG')},
        {"nama": "Pak Indra", "mapel": "Ketua Jurusan", "img": url_for('static', filename='photos/foto-pak-indra.JPG')},
        {"nama": "Pak Harits", "mapel": "Guru Pengajar", "img": url_for('static', filename='photos/foto-pak-harits.JPG')},
    ]
    faq_list = [
        {"tanya": "Apa itu TKJ Smart?", "jawab": "TKJ Smart adalah platform pembelajaran online khusus jurusan Teknik Komputer dan Jaringan (TKJ) yang menyediakan modul, video tutorial, dan latihan soal untuk membantu siswa memahami materi dengan lebih mudah dan interaktif."},
        {"tanya": "Apakah saya harus login untuk menggunakan fitur?", "jawab": "Ya, kamu perlu login menggunakan akun sekolah agar bisa mengakses fitur seperti mengerjakan quiz, melihat progress belajar, dan menyimpan streak harian."},
        {"tanya": "Apa itu streak dan bagaimana cara meningkatkannya?", "jawab": "Streak adalah jumlah hari berturut-turut kamu aktif belajar di platform. Streak akan bertambah jika kamu melakukan aktivitas (membaca modul, menonton video, atau mengerjakan quiz) setiap hari tanpa terputus."},
        {"tanya": "Kenapa progress saya tidak bertambah?", "jawab": "Progress hanya bertambah jika kamu benar-benar menyelesaikan aktivitas, seperti: Membaca modul sampai selesai, Menonton video sampai akhir atau Menyelesaikan quiz. Pastikan koneksi internet stabil agar progress tersimpan dengan baik."},
        {"tanya": "Apakah saya bisa mengakses TKJ Smart dari HP?", "jawab": "Bisa. TKJ Smart dirancang responsif sehingga dapat digunakan di laptop maupun smartphone tanpa perlu aplikasi tambahan."},
    ]
    return render_template('index.html', fitur=fitur_list, guru=guru_all, faq=faq_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            session['nama_lengkap'] = user['nama_lengkap']
            session['email'] = user['email']
            session['user_id'] = user['id']           
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau Password salah!', 'danger') 
            return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
    
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    user_id = session['user_id']
    conn = get_db_connection()
    now_utc = datetime.utcnow()
    now_wib = now_utc + timedelta(hours=7)
    today = now_wib.date()
    user = conn.execute(
        'SELECT streak, last_login FROM users WHERE id = ?', 
        (user_id,)
    ).fetchone()
    current_streak = user['streak'] or 0
    last_login_str = user['last_login']
    if last_login_str:
        last_login_date = datetime.strptime(last_login_str, '%Y-%m-%d').date()
        selisih = (today - last_login_date).days
        if selisih == 1:
            current_streak += 1
        elif selisih > 1:
            current_streak = 1
    else:
        current_streak = 1
    conn.execute(
        'UPDATE users SET streak = ?, last_login = ? WHERE id = ?',
        (current_streak, today.strftime('%Y-%m-%d'), user_id)
    )
    conn.commit()
    day_list = [0] * 7
    for i in range(7):
        tanggal = today - timedelta(days=i)
        aktivitas = conn.execute('''
            SELECT 1 FROM (
                SELECT updated_at FROM user_progress WHERE user_id=?
                UNION
                SELECT updated_at FROM user_quiz WHERE user_id=?
                UNION
                SELECT updated_at FROM user_video WHERE user_id=?
            )
            WHERE DATE(updated_at)=?
            LIMIT 1
        ''', (user_id, user_id, user_id, tanggal.strftime('%Y-%m-%d'))).fetchone()
        if aktivitas:
            index = tanggal.weekday()
            day_list[index] = 1
    progress_data = conn.execute('''
        SELECT up.progress, m.judul, m.deskripsi_singkat, m.id 
        FROM user_progress up 
        JOIN modul m ON up.modul_id = m.id 
        WHERE up.user_id = ? 
        ORDER BY up.id DESC LIMIT 1
    ''', (user_id,)).fetchone()
    rekomendasi = conn.execute(
        'SELECT * FROM modul ORDER BY RANDOM() LIMIT 3'
    ).fetchall()
    conn.close()
    return render_template(
        'dashboard.html',
        progres=progress_data['progress'] if progress_data else 0,
        materi=progress_data['judul'] if progress_data else None,
        deskripsi=progress_data['deskripsi_singkat'] if progress_data else None,
        modul_id=progress_data['id'] if progress_data else None,
        rekomendasi=rekomendasi,
        streak=current_streak,
        day_list=day_list
    )

@app.route('/modul/<kat>')
def show_modul(kat):
    kategori_dicari = kat.lower().strip() 
    conn = get_db_connection()
    cek_isi = conn.execute('SELECT COUNT(*) FROM modul').fetchone()
    print(f"Total baris di tabel modul: {cek_isi[0]}") 
    materi = conn.execute('SELECT * FROM modul WHERE kategori = ?', (kategori_dicari,)).fetchall()
    conn.close()
    print(f"Mencari: '{kategori_dicari}', Hasil: {len(materi)} materi")
    return render_template('modul_kategori.html', 
                           materi_list=materi, 
                           nama_kategori=kat.capitalize())
    
@app.route('/modul/<int:modul_id>')
def detail_modul(modul_id):
    conn = get_db_connection()
    materi = conn.execute('SELECT * FROM modul WHERE id = ?', (modul_id,)).fetchone()
    conn.close()
    return render_template('detail_modul.html', materi=materi)    
    
@app.route('/modul/baca/<int:id>')
def baca_modul(id):
    conn = get_db_connection()
    materi = conn.execute('SELECT * FROM modul WHERE id = ?', (id,)).fetchone()
    rekomendasi = conn.execute('SELECT * FROM modul WHERE id != ? LIMIT 3', (id,)).fetchall()
    conn.close()
    if materi is None:
        return "Materi tidak ditemukan", 404  
    return render_template('baca_modul.html', m=materi, rekomendasi=rekomendasi)

@app.route('/video')
def video_page():
    search_query = request.args.get('q', '')
    conn = get_db_connection()
    if search_query:
        query = "SELECT * FROM video WHERE judul LIKE ? OR deskripsi LIKE ?"
        search_term = f"%{search_query}%"
        videos = conn.execute(query, (search_term, search_term)).fetchall()
    else:
        videos = conn.execute('SELECT * FROM video').fetchall() 
    conn.close()
    return render_template('video.html', videos=videos)

@app.route('/video/watch/<int:id>')
def watch_video(id):
    conn = get_db_connection()
    video = conn.execute('SELECT * FROM video WHERE id = ?', (id,)).fetchone()
    sidebar_videos = conn.execute('SELECT * FROM video WHERE id != ? LIMIT 4', (id,)).fetchall()
    now = datetime.now().strftime('%Y-%m-%d')
    conn.execute('''
		INSERT INTO user_video (user_id, video_id, updated_at)
		VALUES (?, ?, ?)
	''', (session['user_id'], id, now))
    conn.commit()
    conn.close()
    if video is None:
        return "Video tidak ditemukan", 404
    return render_template('video_watch.html', v=video, saran=sidebar_videos)
    
@app.route('/quiz')
def quiz_menu():
    conn = get_db_connection()
    quizzes = conn.execute('SELECT * FROM quiz_list').fetchall()
    conn.close()
    return render_template('quiz_menu.html', quiz_list=quizzes)
    
@app.route('/quiz/kerjakan/<int:quiz_id>')
def quiz_pengerjaan(quiz_id):
    conn = get_db_connection()
    questions_raw = conn.execute('SELECT * FROM quiz_questions WHERE quiz_id = ?', (quiz_id,)).fetchall()
    info_kuis = conn.execute('SELECT judul FROM quiz_list WHERE id = ?', (quiz_id,)).fetchone()
    conn.close()
    soal_list_js = []
    for q in questions_raw:
        soal_list_js.append({
            "id": q['id'],
            "tanya": q['pertanyaan'],
            "opsi": [q['opsi_a'], q['opsi_b'], q['opsi_c'], q['opsi_d']],
            "kunci": q['jawaban_benar'] 
        })
    return render_template('quiz_kerjakan.html', 
                           soal_list=soal_list_js, 
                           judul=info_kuis['judul'] if info_kuis else "Quiz")
from datetime import datetime, timedelta

@app.route('/account')
def account():
    conn = get_db_connection()
    user_id = session.get('user_id')
    labels = []
    modul_data = []
    quiz_data = []
    video_data = []
    for i in range(4, -1, -1):
        hari = datetime.now() - timedelta(days=i)
        tanggal = hari.strftime('%Y-%m-%d')
        labels.append(hari.strftime('%d/%m'))
        jumlah_modul = conn.execute('''
			SELECT COUNT(*) FROM user_progress
			WHERE user_id=? AND updated_at = ?
		''', (user_id, tanggal)).fetchone()[0]
        jumlah_quiz = conn.execute('''
			SELECT COUNT(*) FROM user_quiz
			WHERE user_id=? AND updated_at = ?
		''', (user_id, tanggal)).fetchone()[0]
        jumlah_video = conn.execute('''
			SELECT COUNT(*) FROM user_video
			WHERE user_id=? AND updated_at = ?
		''', (user_id, tanggal)).fetchone()[0] if True else 0
        modul_data.append(jumlah_modul)
        quiz_data.append(jumlah_quiz)
        video_data.append(jumlah_video)
    kategori = conn.execute('''
        SELECT m.kategori, COUNT(*) as total
        FROM user_progress up
        JOIN modul m ON up.modul_id = m.id
        WHERE up.user_id=?
        GROUP BY m.kategori
    ''', (user_id,)).fetchall()
    pie_labels = [k['kategori'] for k in kategori]
    pie_data = [k['total'] for k in kategori]
    poin = conn.execute('''
        SELECT COALESCE(SUM(score), 0) FROM user_quiz WHERE user_id=?
    ''', (user_id,)).fetchone()[0]
    kuis_selesai = conn.execute('''
        SELECT COUNT(*) FROM user_quiz WHERE user_id=?
    ''', (user_id,)).fetchone()[0]
    modul_selesai = conn.execute('''
        SELECT COUNT(*) FROM user_progress 
        WHERE user_id=? AND progress=100
    ''', (user_id,)).fetchone()[0]
    user_data = {
        "sekolah": "SMKN 2 Probolinggo",
    }
    conn.close()
    return render_template(
        'account.html',
        poin=poin,
        user=user_data,
        kuis_selesai=kuis_selesai,
        modul_selesai=modul_selesai,
        bar_labels=labels or [],
		modul_data=modul_data or [],
		quiz_data=quiz_data or [],
		video_data=video_data or [],
		pie_labels=pie_labels or [],
		pie_data=pie_data or []
    )

@app.route('/admin')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    per_page = 10
    modul_page = request.args.get('modul_page', 1, type=int)
    modul_search = request.args.get('modul_search', '')
    modul_offset = (modul_page - 1) * per_page
    modul_query = 'FROM modul'
    modul_params = []
    if modul_search:
        modul_query += ' WHERE judul LIKE ?'
        modul_params.append(f'%{modul_search}%')
    modules = conn.execute(
        f'SELECT * {modul_query} LIMIT ? OFFSET ?',
        (*modul_params, per_page, modul_offset)
    ).fetchall()
    total_modul = conn.execute(
        f'SELECT COUNT(*) {modul_query}',
        modul_params
    ).fetchone()[0]
    modul_pages = (total_modul + per_page - 1) // per_page
    video_page = request.args.get('video_page', 1, type=int)
    video_search = request.args.get('video_search', '')
    video_offset = (video_page - 1) * per_page
    video_query = 'FROM video'
    video_params = []
    if video_search:
        video_query += ' WHERE judul LIKE ?'
        video_params.append(f'%{video_search}%')
    videos = conn.execute(
        f'SELECT * {video_query} LIMIT ? OFFSET ?',
        (*video_params, per_page, video_offset)
    ).fetchall()
    total_video = conn.execute(
        f'SELECT COUNT(*) {video_query}',
        video_params
    ).fetchone()[0]
    video_pages = (total_video + per_page - 1) // per_page
    user_page = request.args.get('user_page', 1, type=int)
    user_search = request.args.get('user_search', '')
    user_offset = (user_page - 1) * per_page
    user_query = 'FROM users'
    user_params = []
    if user_search:
        user_query += ' WHERE nama_lengkap LIKE ? OR email LIKE ?'
        user_params.extend([f'%{user_search}%', f'%{user_search}%'])
    users = conn.execute(
        f'SELECT * {user_query} LIMIT ? OFFSET ?',
        (*user_params, per_page, user_offset)
    ).fetchall()
    total_user = conn.execute(
        f'SELECT COUNT(*) {user_query}',
        user_params
    ).fetchone()[0]
    user_pages = (total_user + per_page - 1) // per_page
    quiz_page = request.args.get('quiz_page', 1, type=int)
    quiz_search = request.args.get('quiz_search', '')
    quiz_offset = (quiz_page - 1) * per_page
    quiz_query = '''
        FROM quiz_list ql 
        LEFT JOIN quiz_questions qq ON ql.id = qq.quiz_id
    '''
    quiz_params = []
    if quiz_search:
        quiz_query += ' WHERE ql.judul LIKE ?'
        quiz_params.append(f'%{quiz_search}%')
    quizzes = conn.execute(f'''
        SELECT ql.*, COUNT(qq.id) as jumlah_soal
        {quiz_query}
        GROUP BY ql.id
        LIMIT ? OFFSET ?
    ''', (*quiz_params, per_page, quiz_offset)).fetchall()
    total_quiz = conn.execute(
        f'SELECT COUNT(*) FROM quiz_list'
    ).fetchone()[0]
    quiz_pages = (total_quiz + per_page - 1) // per_page
    conn.close()
    return render_template(
        'admin_dashboard.html',
        modules=modules,
        modul_page=modul_page,
        modul_pages=modul_pages,
        total_modul=total_modul,
        modul_search=modul_search,
        videos=videos,
        video_page=video_page,
        video_pages=video_pages,
        total_video=total_video,
        video_search=video_search,
        users=users,
        user_page=user_page,
        user_pages=user_pages,
        total_user=total_user,
        user_search=user_search,
        quizzes=quizzes,
        quiz_page=quiz_page,
        quiz_pages=quiz_pages,
        total_quiz=total_quiz,
        quiz_search=quiz_search
    )

@app.route('/admin/add-modul')
def form_add_modul():
    return render_template('admin_form_modul.html', is_edit=False)

@app.route('/admin/add-video')
def form_add_video():
    return render_template('admin_form_video.html', is_edit=False)
    
@app.route('/admin/add-account')
def form_add_account():
    return render_template('admin_form_akun.html', is_edit=False)
        

@app.route('/admin/add-quiz')
def add_quiz():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template(
        'admin_full_quiz.html',
        quiz=None,
        questions=[],
        is_edit=False
    )    
    
@app.route('/admin/delete-user/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-modul/<int:id>')
def delete_modul(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM modul WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-video/<int:id>')
def delete_video(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM video WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))
    
@app.route('/admin/delete-latihan/<int:id>')
def delete_latihan(id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))       
    conn = get_db_connection()
    conn.execute('DELETE FROM quiz_list WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Latihan Soal berhasil dihapus!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-question/<int:id>/<int:quiz_id>')
def delete_question(id, quiz_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM quiz_questions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Satu soal berhasil dihapus!')
    return redirect(url_for('add_questions', quiz_id=quiz_id))

@app.route('/admin/save-account', methods=['POST'])
def save_account():
    user = request.form.get('username')
    pw = request.form.get('password')
    nama = request.form.get('nama_lengkap') # Ambil input nama
    role = request.form.get('role') # Ambil input role (admin/siswa)
    email = request.form.get('email')
    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)', 
                 (user, pw, nama, role))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))
    
@app.route('/admin/save-modul', methods=['POST'])
def save_modul():
    judul = request.form['judul']
    kategori = request.form['kategori']
    deskripsi_singkat = request.form['deskripsi_singkat']
    konten = request.form['konten']
    icon = request.form['icon'] # <--- Ambil icon
    conn = get_db_connection()
    conn.execute('INSERT INTO modul (judul, kategori, konten, icon) VALUES (?, ?, ?, ?)',
                 (judul, kategori, konten, icon))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))
   
@app.route('/admin/save-video', methods=['POST'])
def save_video():
    judul = request.form['judul']
    yt_id = request.form['youtube_id']
    durasi = request.form['durasi']
    deskripsi = request.form['deskripsi']
    thumb = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO video (judul, youtube_id, durasi, deskripsi, thumbnail) 
        VALUES (?, ?, ?, ?, ?)
    ''', (judul, yt_id, durasi, deskripsi, thumb))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/save-full-quiz', methods=['POST'])
def save_full_quiz():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO quiz_list (judul, icon) VALUES (?, ?)',
        (data['judul'], data['icon'])
    )
    quiz_id = cur.lastrowid
    for q in data['questions']:
        cur.execute('''
            INSERT INTO quiz_questions 
            (quiz_id, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d, jawaban_benar)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            quiz_id,
            q['pertanyaan'],
            q['a'],
            q['b'],
            q['c'],
            q['d'],
            q['jawaban']
        ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
    
@app.route('/admin/edit-quiz/<int:quiz_id>')
def edit_quiz(quiz_id):
    conn = get_db_connection()
    quiz = conn.execute(
        'SELECT * FROM quiz_list WHERE id=?',
        (quiz_id,)
    ).fetchone()
    questions_raw = conn.execute(
        'SELECT * FROM quiz_questions WHERE quiz_id=?',
        (quiz_id,)
    ).fetchall()
    conn.close()
    quiz = dict(quiz) if quiz else None
    questions = [dict(q) for q in questions_raw]
    return render_template(
        'admin_full_quiz.html',
        quiz=quiz,
        questions=questions,
        is_edit=True
    )
    
@app.route('/admin/update-quiz/<int:quiz_id>', methods=['POST'])
def update_quiz(quiz_id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE quiz_list SET judul=?, icon=? WHERE id=?',
        (data['judul'], data['icon'], quiz_id)
    )
    cur.execute('DELETE FROM quiz_questions WHERE quiz_id=?', (quiz_id,))
    for q in data['questions']:
        cur.execute('''
            INSERT INTO quiz_questions 
            (quiz_id, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d, jawaban_benar)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            quiz_id,
            q.get('pertanyaan'),
            q.get('a') or q.get('opsi_a'),
            q.get('b') or q.get('opsi_b'),
            q.get('c') or q.get('opsi_c'),
            q.get('d') or q.get('opsi_d'),
            q.get('jawaban') or q.get('jawaban_benar')
        ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
    
@app.route('/admin/edit-modul/<int:id>')
def edit_modul(id):
    conn = get_db_connection()
    modul = conn.execute('SELECT * FROM modul WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template(
        'admin_form_modul.html',
        modul=dict(modul),
        is_edit=True
    )
    
@app.route('/admin/edit-video/<int:id>')
def edit_video(id):
    conn = get_db_connection()
    video = conn.execute('SELECT * FROM video WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template(
        'admin_form_video.html',
        video=dict(video),
        is_edit=True
    )
    
@app.route('/admin/edit-user/<int:id>')
def edit_user(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template(
		'admin_form_akun.html',
		is_edit=True,
		user=dict(user)
	)
    
@app.route('/admin/update-modul/<int:id>', methods=['POST'])
def update_modul(id):
    conn = get_db_connection()
    conn.execute('''
        UPDATE modul
        SET judul=?, kategori=?, icon=?, deskripsi_singkat=?, konten=?
        WHERE id=?
    ''', (
        request.form['judul'],
        request.form['kategori'],
        request.form['icon'],
        request.form['deskripsi_singkat'],
        request.form['konten'],
        id
    ))
    conn.commit()
    conn.close()
    return redirect('/admin')
    
@app.route('/admin/update-video/<int:id>', methods=['POST'])
def update_video(id):
    conn = get_db_connection()
    conn.execute('''
        UPDATE video 
        SET judul=?, youtube_id=? 
        WHERE id=?
    ''', (
        request.form['judul'],
        request.form['youtube_id'],
        id
    ))
    conn.commit()
    conn.close()
    return redirect('/admin')
    
@app.route('/admin/update-user/<int:id>', methods=['POST'])
def update_user(id):
    conn = get_db_connection()
    if request.form['password']:  
        conn.execute('''
            UPDATE users 
            SET username=?, nama_lengkap=?, email=?, role=?, password=? 
            WHERE id=?
        ''', (
            request.form['username'],
            request.form['nama_lengkap'],
            request.form['email'],
            request.form['role'],
            request.form['password'],
            id
        ))
    else: 
        conn.execute('''
            UPDATE users 
            SET username=?, nama_lengkap=?, email=?, role=? 
            WHERE id=?
        ''', (
            request.form['username'],
            request.form['nama_lengkap'],
            request.form['email'],
            request.form['role'],
            id
        ))
    conn.commit()
    conn.close()
    return redirect('/admin')
    
@app.route('/update-progress', methods=['POST'])
def update_progress():
    if 'user_id' not in session:
        return {"status": "error"}
    data = request.get_json()
    modul_id = data['modul_id']
    progress = data['progress']
    user_id = session['user_id']
    conn = get_db_connection()
    existing = conn.execute(
        'SELECT * FROM user_progress WHERE user_id=? AND modul_id=?',
        (user_id, modul_id)
    ).fetchone()
    if existing:
        conn.execute(
            'UPDATE user_progress SET progress=? WHERE user_id=? AND modul_id=?',
            (progress, user_id, modul_id)
        )
    else:
        conn.execute(
            'INSERT INTO user_progress (user_id, modul_id, progress) VALUES (?, ?, ?)',
            (user_id, modul_id, progress)
        )       
    now = datetime.now().strftime('%Y-%m-%d')
    conn.execute(
		'UPDATE user_progress SET progress=?, updated_at=? WHERE user_id=? AND modul_id=?',
		(progress, now, user_id, modul_id)
	)
    conn.commit()
    conn.close()
    return {"status": "success"}
    
@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return {"status": "error"}
    data = request.get_json()
    user_id = session['user_id']
    quiz_id = data['quiz_id']
    score = data['score']
    max_score = data['max_score']

    conn = get_db_connection()

    now = datetime.now().strftime('%Y-%m-%d')

    existing = conn.execute(
        'SELECT * FROM user_quiz WHERE user_id=? AND quiz_id=?',
        (user_id, quiz_id)
    ).fetchone()

    if existing:
        if score > existing['score']:
            conn.execute(
                'UPDATE user_quiz SET score=?, updated_at=? WHERE user_id=? AND quiz_id=?',
                (score, now, user_id, quiz_id)
            )
    else:
        conn.execute(
            'INSERT INTO user_quiz (user_id, quiz_id, score, max_score, updated_at) VALUES (?, ?, ?, ?, ?)',
            (user_id, quiz_id, score, max_score, now)
        )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.route('/admin/search-modul')
def search_modul():
    keyword = request.args.get('q', '')

    conn = get_db_connection()

    modules = conn.execute('''
        SELECT * FROM modul
        WHERE judul LIKE ?
        ORDER BY id DESC
        LIMIT 10
    ''', ('%' + keyword + '%',)).fetchall()

    conn.close()

    result = []
    for m in modules:
        result.append({
            "id": m["id"],
            "judul": m["judul"],
            "deskripsi": m["deskripsi_singkat"]
        })

    return jsonify(result)

@app.route('/admin/search-video')
def search_video():
    keyword = request.args.get('q', '')

    conn = get_db_connection()
    videos = conn.execute('''
        SELECT * FROM video
        WHERE judul LIKE ?
        ORDER BY id DESC
        LIMIT 10
    ''', ('%' + keyword + '%',)).fetchall()
    conn.close()

    result = []
    for v in videos:
        result.append({
            "id": v["id"],
            "judul": v["judul"],
            "youtube_id": v["youtube_id"]
        })

    return jsonify(result)

@app.route('/admin/search-quiz')
def search_quiz():
    keyword = request.args.get('q', '')

    conn = get_db_connection()
    quizzes = conn.execute('''
        SELECT ql.*, COUNT(qq.id) as jumlah_soal
        FROM quiz_list ql
        LEFT JOIN quiz_questions qq ON ql.id = qq.quiz_id
        WHERE ql.judul LIKE ?
        GROUP BY ql.id
        ORDER BY ql.id DESC
        LIMIT 10
    ''', ('%' + keyword + '%',)).fetchall()
    conn.close()

    result = []
    for q in quizzes:
        result.append({
            "id": q["id"],
            "judul": q["judul"],
            "jumlah_soal": q["jumlah_soal"]
        })

    return jsonify(result)

@app.route('/admin/search-user')
def search_user():
    keyword = request.args.get('q', '')

    conn = get_db_connection()
    users = conn.execute('''
        SELECT * FROM users
        WHERE nama_lengkap LIKE ? OR email LIKE ?
        ORDER BY id DESC
        LIMIT 10
    ''', (f'%{keyword}%', f'%{keyword}%')).fetchall()
    conn.close()

    result = []
    for u in users:
        result.append({
            "id": u["id"],
            "username": u["username"],
            "nama": u["nama_lengkap"],
            "role": u["role"]
        })

    return jsonify(result)

if __name__ == '__main__':
    app.run()