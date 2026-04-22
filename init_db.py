import sqlite3

def init_db():
    # 1. Koneksi ke database
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    with connection:
        
        # 3. Buat tabel modul dengan kolom yang lengkap
        connection.execute('''
            CREATE TABLE IF NOT EXISTS modul (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                kategori TEXT NOT NULL,
                konten TEXT NOT NULL,
                deskripsi_singkat TEXT,
                icon TEXT
            )
        ''')
        
        connection.execute('''
			CREATE TABLE IF NOT EXISTS user_video (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INTEGER,
				video_id INTEGER,
				updated_at TEXT
			);
		''')
        
        connection.execute('''
			CREATE TABLE IF NOT EXISTS user_progress (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INTEGER,
				modul_id INTEGER,
				progress INTEGER DEFAULT 0,
				updated_at TEXT
			)
		''')
		
        connection.execute('''
			CREATE TABLE IF NOT EXISTS user_quiz (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INTEGER,
				quiz_id INTEGER,
				score INTEGER,
				max_score INTEGER,
				updated_at TEXT
			);
		''')
        
        cursor.execute('''
			CREATE TABLE IF NOT EXISTS quiz_list (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				judul TEXT NOT NULL,
				icon TEXT NOT NULL
			)
		''')
		
        cursor.execute('''
			CREATE TABLE IF NOT EXISTS quiz_questions (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				quiz_id INTEGER,
				pertanyaan TEXT NOT NULL,
				opsi_a TEXT NOT NULL,
				opsi_b TEXT NOT NULL,
				opsi_c TEXT NOT NULL,
				opsi_d TEXT NOT NULL,
				jawaban_benar TEXT NOT NULL,
				FOREIGN KEY (quiz_id) REFERENCES quiz_list (id) ON DELETE CASCADE
			)
		''')
		
        # 4. Data contoh untuk masing-masing kategori
        # Format: (Judul, Kategori, Konten_Lengkap, Deskripsi_Singkat, Icon_FontAwesome)
        data_materi = [
            # Kategori: mikrotik
            ('Konfigurasi Dasar MikroTik', 'mikrotik', 
             '<h2>Langkah Awal</h2><p>Gunakan Winbox untuk login ke router...</p>', 
             'Belajar cara setting IP Address dan DHCP Server di MikroTik.', 
             'fas fa-microchip'),
            
            ('Routing Statis MikroTik', 'mikrotik', 
             '<h2>Konsep Routing</h2><p>Routing statis dilakukan secara manual...</p>', 
             'Panduan menghubungkan dua jaringan berbeda dengan Static Route.', 
             'fas fa-route'),

            # Kategori: cisco
            ('VLAN Dasar Cisco', 'cisco', 
             '<h2>Apa itu VLAN?</h2><p>Virtual LAN memungkinkan pemisahan jaringan...</p>', 
             'Cara membuat dan mengelola VLAN pada Switch Cisco Catalyst.', 
             'fas fa-network-wired'),
            
            ('Inter-VLAN Routing', 'cisco', 
             '<h2>Router on a Stick</h2><p>Menghubungkan antar VLAN menggunakan satu link...</p>', 
             'Menghubungkan komunikasi antar VLAN yang berbeda pada Cisco.', 
             'fas fa-project-diagram'),

            # Kategori: linux
            ('Installasi Web Server Apache', 'linux', 
             '<h2>Step by Step</h2><p>Gunakan perintah apt install apache2...</p>', 
             'Membangun server web sendiri menggunakan Ubuntu Server.', 
             'fas fa-server'),
             
            ('Manajemen User & Group', 'linux', 
             '<h2>Hak Akses</h2><p>Memahami perintah chmod dan chown...</p>', 
             'Mengelola keamanan file dan hak akses user di sistem Linux.', 
             'fas fa-user-shield')
        ]
        
        # 5. Masukkan semua data sekaligus
        connection.executemany('''
            INSERT INTO modul (judul, kategori, konten, deskripsi_singkat, icon) 
            VALUES (?, ?, ?, ?, ?)
        ''', data_materi)    
        
        # --- DI DALAM init_db.py ---

		# 1. Tabel Video
        connection.execute('''
            CREATE TABLE IF NOT EXISTS video(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                thumbnail TEXT NOT NULL,  -- URL gambar thumbnail
                durasi TEXT NOT NULL,     -- Contoh: "10:25"
                deskripsi TEXT NOT NULL,       -- Deskripsi singkat (v.desc)
                youtube_id TEXT NOT NULL  -- ID untuk halaman nonton nanti
            )
		''')

		
			# 1. Membuat Tabel Users
		# id: kunci utama otomatis
		# username: harus unik (tidak boleh ada yang sama)
		# password: teks biasa (atau hash nanti)
		# role: untuk membedakan 'admin' dan 'siswa'
        cursor.execute('''
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT UNIQUE NOT NULL,
				nama_lengkap TEXT,
				password TEXT NOT NULL,
				role TEXT DEFAULT 'siswa',
				email TEXT,
				streak INTEGER DEFAULT 0, 
				last_login DATE
			)
		''')

		# 2. Membuat Akun Admin Default
		# Menggunakan INSERT OR IGNORE agar jika script dijalankan ulang, 
		# data tidak double atau error karena kolom UNIQUE.
		# Username: admin | Password: admin
        cursor.execute('''
			INSERT OR IGNORE INTO users (username, nama_lengkap, password, role, email) 
			VALUES ('admin', 'admin', 'admin', 'admin', 'admin')
		''')

		# Tambahan: Kamu bisa masukkan beberapa akun siswa contoh di sini
        cursor.execute('''
			INSERT OR IGNORE INTO users (username, nama_lengkap, password, role, email) 
			VALUES ('siswa1', 'Abi Manyu Alfian Hidayanto', '12345', 'siswa', 'abimanyu.04042009@gmail.com')
		''')
        
        connection.execute('''
            INSERT INTO video (judul, thumbnail, durasi, deskripsi, youtube_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('Judul Video', 'thumb.jpg', '10:00', 'Deskripsi video', 'xyz123'))
        
        try:
            connection.execute("ALTER TABLE user_progress ADD COLUMN updated_at TEXT")
        except:
            pass

        try:
            connection.execute("ALTER TABLE user_quiz ADD COLUMN updated_at TEXT")
        except:
            pass

        try:
            connection.execute("ALTER TABLE user_video ADD COLUMN updated_at TEXT")
        except:
            pass

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login DATE")
            print("Kolom streak & last_login berhasil ditambahkan!")
        except sqlite3.OperationalError:
            # Jika kolom sudah ada, sqlite akan melempar error, kita abaikan saja
            print("Kolom sudah ada, tidak ada perubahan.")
        
    connection.commit()		
    connection.close()
    print("✅ Database 'database.db' berhasil diperbarui!")

if __name__ == '__main__':
    init_db()
