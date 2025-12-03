# Aplikasi-Web-Perbankan-dengan-Python-
# Aplikasi Web Perbankan Digital

Aplikasi web perbankan digital sederhana yang dibangun dengan Python Flask.

## Fitur

- ✅ Registrasi dan Login Pengguna
- ✅ Dashboard dengan informasi saldo
- ✅ Transfer antar rekening
- ✅ Deposit dan Penarikan uang
- ✅ Riwayat transaksi
- ✅ Manajemen profil pengguna
- ✅ Responsive design
- ✅ Validasi form dan keamanan

## Teknologi yang Digunakan

- **Backend:** Python Flask
- **Database:** SQLite (dapat diganti dengan PostgreSQL/MySQL)
- **Frontend:** HTML5, CSS3, JavaScript
- **Authentication:** Flask-Login dengan password hashing
- **Form Handling:** Flask-WTF

## Instalasi dan Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/username/banking-app.git
cd banking-app

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

4. Setup Environment Variables

Buat file .env:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///bank.db
```

5. Inisialisasi Database

```bash
python app.py
```

Aplikasi akan otomatis membuat database dan user admin.

6. Jalankan Aplikasi

```bash
python app.py
```

Buka browser dan akses: http://localhost:5000

Akun Default

· Admin: admin@bank.com / admin123
· Saldo awal: Rp 10,000,000

Struktur Proyek

```
banking-app/
├── app.py              # Aplikasi utama Flask
├── models.py           # Model database
├── config.py           # Konfigurasi aplikasi
├── requirements.txt    # Dependencies
├── static/            # File statis (CSS, JS)
├── templates/         # Template HTML
└── README.md          # Dokumentasi
```

API Endpoints

· GET /api/balance - Mendapatkan saldo pengguna
· GET /api/transactions/recent - Mendapatkan transaksi terakhir

Keamanan

· Password di-hash dengan bcrypt
· Session management dengan Flask-Login
· CSRF protection dengan Flask-WTF
· Validasi input server-side

Deployment

Untuk deployment ke production:

1. Ganti SECRET_KEY dengan yang lebih aman
2. Gunakan database production (PostgreSQL/MySQL)
3. Setup HTTPS
4. Gunakan WSGI server (Gunicorn)
5. Setup reverse proxy (Nginx)

Lisensi

MIT License

Kontribusi

Pull requests dipersilakan. Untuk perubahan besar, buka issue terlebih dahulu.

Penafian

Aplikasi ini hanya untuk tujuan edukasi dan demonstrasi. Tidak untuk digunakan dalam produksi nyata.

```

## 7. Template HTML Lainnya

Karena keterbatasan ruang, berikut adalah template penting lainnya:

### `templates/login.html`
```html
{% extends "base.html" %}
{% block title %}Login - Bank Digital{% endblock %}

{% block content %}
<div class="form-container">
    <h2>Login</h2>
    <form method="POST" action="{{ url_for('login') }}">
        {{ form.hidden_tag() }}
        
        <div class="form-group">
            {{ form.email.label }}
            {{ form.email(class="form-control") }}
        </div>
        
        <div class="form-group">
            {{ form.password.label }}
            {{ form.password(class="form-control") }}
        </div>
        
        <button type="submit" class="btn btn-primary btn-block">Login</button>
    </form>
    
    <p class="text-center mt-3">
        Belum punya akun? <a href="{{ url_for('register') }}">Daftar di sini</a>
    </p>
</div>
{% endblock %}
```

Cara Menggunakan dan Deploy ke GitHub

Langkah-langkah:

1. Buat repository baru di GitHub
   · Login ke GitHub
   · Klik "+" → "New repository"
   · Beri nama "banking-app"
   · Pilih "Public"
   · Jangan centang "Initialize with README"
2. Setup proyek lokal

```bash
# Buat folder proyek
mkdir banking-app
cd banking-app

# Inisialisasi git
git init

# Buat struktur folder
mkdir -p static/css static/js templates
```

1. Salin semua file kode ke folder yang sesuai
2. Commit dan push ke GitHub

```bash
# Tambahkan semua file
git add .

# Commit
git commit -m "Initial commit: Aplikasi web perbankan dengan Flask"

# Tambahkan remote repository
git remote add origin https://github.com/username/banking-app.git

# Push ke GitHub
git branch -M main
git push -u origin main
```

1. Install dependencies dan jalankan

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan (Windows)
venv\Scripts\activate

# Aktifkan (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
```

Fungsi Kode Utama

models.py

· User Model: Menyimpan data pengguna (akun, email, password, saldo)
· Transaction Model: Menyimpan riwayat transaksi
· Password Hashing: Menggunakan bcrypt untuk keamanan password

app.py

· Routing: Menangani semua endpoint aplikasi
· Authentication: Login, register, logout dengan Flask-Login
· Business Logic: Transfer, deposit, withdraw dengan validasi
· Error Handling: Menangani error 404 dan 500
· API Endpoints: Endpoint JSON untuk integrasi

Fitur Keamanan

1. Password hashing dengan bcrypt
2. Session management dengan Flask-Login
3. CSRF protection dengan Flask-WTF
4. Input validation di server-side
5. SQL injection prevention dengan SQLAlchemy

Fitur yang Dapat Ditambahkan

1. Email verification untuk registrasi
2. 2-Factor Authentication
3. Export transaksi ke PDF/Excel
4. Currency conversion
5. Transaction limits dan alerts
6. Admin dashboard untuk manajemen user

Aplikasi ini siap digunakan sebagai basis untuk pengembangan aplikasi perbankan yang lebih lengkap. Pastikan untuk menambah fitur keamanan tambahan sebelum digunakan dalam produksi nyata.
