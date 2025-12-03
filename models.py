from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Model untuk menyimpan data pengguna"""
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(200))
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash password dan simpan"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifikasi password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_full_name(self):
        """Dapatkan nama lengkap"""
        return f"{self.first_name} {self.last_name}"

class Transaction(db.Model):
    """Model untuk menyimpan transaksi"""
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdraw, transfer
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    recipient_account = db.Column(db.String(20))  # Untuk transfer
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')  # completed, pending, failed
    balance_after = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'
