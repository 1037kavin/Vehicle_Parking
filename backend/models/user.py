from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app import db
from backend.utils.timezone import get_utc_now, format_ist_iso

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=get_utc_now)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'role': self.role,
            'created_at': format_ist_iso(self.created_at),
            'last_login': format_ist_iso(self.last_login),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

