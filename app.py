import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from models import db, User, Transaction
from config import Config
import re

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi database dan login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone')
    address = TextAreaField('Address')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email sudah terdaftar.')
    
    def validate_password(self, field):
        if field.data != self.confirm_password.data:
            raise ValidationError('Password tidak cocok.')

class TransferForm(FlaskForm):
    recipient_account = StringField('Nomor Rekening Penerima', validators=[DataRequired()])
    amount = FloatField('Jumlah', validators=[DataRequired(), NumberRange(min=1000)])
    description = TextAreaField('Keterangan')

class DepositForm(FlaskForm):
    amount = FloatField('Jumlah Deposit', validators=[DataRequired(), NumberRange(min=1000)])

class WithdrawForm(FlaskForm):
    amount = FloatField('Jumlah Penarikan', validators=[DataRequired(), NumberRange(min=1000)])

# Helper functions
def generate_account_number():
    """Generate nomor rekening unik"""
    return str(uuid.uuid4().int)[:16]

def generate_transaction_id():
    """Generate ID transaksi unik"""
    return f"TRX-{uuid.uuid4().hex[:8].upper()}"

def validate_account_number(account_number):
    """Validasi format nomor rekening"""
    return bool(re.match(r'^\d{16}$', account_number))

# Routes
@app.route('/')
def index():
    """Halaman utama"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrasi pengguna baru"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Buat user baru
        user = User(
            account_number=generate_account_number(),
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login pengguna"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user)
                next_page = request.args.get('next')
                flash('Login berhasil!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Akun dinonaktifkan. Hubungi customer service.', 'danger')
        else:
            flash('Email atau password salah.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout pengguna"""
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard pengguna"""
    # Ambil 5 transaksi terakhir
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.timestamp.desc())\
        .limit(5)\
        .all()
    
    return render_template('dashboard.html', 
                          user=current_user,
                          transactions=recent_transactions)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    """Transfer uang ke rekening lain"""
    form = TransferForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        recipient_account = form.recipient_account.data
        
        # Validasi saldo
        if current_user.balance < amount:
            flash('Saldo tidak mencukupi.', 'danger')
            return render_template('transfer.html', form=form)
        
        # Cari penerima
        recipient = User.query.filter_by(account_number=recipient_account).first()
        if not recipient:
            flash('Nomor rekening penerima tidak ditemukan.', 'danger')
            return render_template('transfer.html', form=form)
        
        if recipient.id == current_user.id:
            flash('Tidak dapat transfer ke rekening sendiri.', 'danger')
            return render_template('transfer.html', form=form)
        
        # Proses transfer
        try:
            # Kurangi saldo pengirim
            current_user.balance -= amount
            
            # Tambah saldo penerima
            recipient.balance += amount
            
            # Buat transaksi pengirim
            sender_transaction = Transaction(
                transaction_id=generate_transaction_id(),
                user_id=current_user.id,
                transaction_type='transfer',
                amount=-amount,
                description=f"Transfer ke {recipient_account}: {form.description.data}",
                recipient_account=recipient_account,
                balance_after=current_user.balance
            )
            
            # Buat transaksi penerima
            recipient_transaction = Transaction(
                transaction_id=generate_transaction_id(),
                user_id=recipient.id,
                transaction_type='transfer',
                amount=amount,
                description=f"Transfer dari {current_user.account_number}: {form.description.data}",
                recipient_account=current_user.account_number,
                balance_after=recipient.balance
            )
            
            db.session.add(sender_transaction)
            db.session.add(recipient_transaction)
            db.session.commit()
            
            flash(f'Transfer berhasil! Saldo tersisa: Rp {current_user.balance:,.2f}', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat transfer. Silakan coba lagi.', 'danger')
    
    return render_template('transfer.html', form=form)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    """Deposit uang ke rekening"""
    form = DepositForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        
        # Tambah saldo
        current_user.balance += amount
        
        # Buat transaksi
        transaction = Transaction(
            transaction_id=generate_transaction_id(),
            user_id=current_user.id,
            transaction_type='deposit',
            amount=amount,
            description='Deposit',
            balance_after=current_user.balance
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Deposit berhasil! Saldo sekarang: Rp {current_user.balance:,.2f}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('deposit.html', form=form)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """Penarikan uang dari rekening"""
    form = WithdrawForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        
        # Validasi saldo
        if current_user.balance < amount:
            flash('Saldo tidak mencukupi.', 'danger')
            return render_template('withdraw.html', form=form)
        
        # Kurangi saldo
        current_user.balance -= amount
        
        # Buat transaksi
        transaction = Transaction(
            transaction_id=generate_transaction_id(),
            user_id=current_user.id,
            transaction_type='withdraw',
            amount=-amount,
            description='Penarikan',
            balance_after=current_user.balance
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Penarikan berhasil! Saldo tersisa: Rp {current_user.balance:,.2f}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('withdraw.html', form=form)

@app.route('/transactions')
@login_required
def transactions():
    """Riwayat transaksi"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    transaction_query = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.timestamp.desc())
    
    pagination = transaction_query.paginate(page=page, per_page=per_page, error_out=False)
    transactions_list = pagination.items
    
    return render_template('transactions.html', 
                          transactions=transactions_list,
                          pagination=pagination)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Profil pengguna"""
    if request.method == 'POST':
        # Update profil
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        current_user.last_name = request.form.get('last_name', current_user.last_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.address = request.form.get('address', current_user.address)
        
        db.session.commit()
        flash('Profil berhasil diperbarui!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=current_user)

# API Routes
@app.route('/api/balance')
@login_required
def api_balance():
    """API untuk mendapatkan saldo"""
    return jsonify({
        'balance': current_user.balance,
        'account_number': current_user.account_number,
        'full_name': current_user.get_full_name()
    })

@app.route('/api/transactions/recent')
@login_required
def api_recent_transactions():
    """API untuk transaksi terakhir"""
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.timestamp.desc())\
        .limit(5)\
        .all()
    
    transactions_data = [{
        'id': t.id,
        'type': t.transaction_type,
        'amount': t.amount,
        'description': t.description,
        'timestamp': t.timestamp.isoformat(),
        'balance_after': t.balance_after
    } for t in transactions]
    
    return jsonify(transactions_data)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Database initialization
def init_db():
    """Inisialisasi database"""
    with app.app_context():
        db.create_all()
        
        # Buat user admin jika tidak ada
        admin = User.query.filter_by(email='admin@bank.com').first()
        if not admin:
            admin = User(
                account_number='0000000000000001',
                email='admin@bank.com',
                first_name='Admin',
                last_name='Bank',
                phone='081234567890',
                address='Kantor Pusat'
            )
            admin.set_password('admin123')
            admin.balance = 10000000
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
