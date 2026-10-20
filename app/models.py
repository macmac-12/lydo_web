from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50)) # Religious, Civic, Academic
    mission = db.Column(db.Text)
    president = db.Column(db.String(100))
    vice_president = db.Column(db.String(100))
    secretary = db.Column(db.String(100))
    members = db.Column(db.Text)

class YouthProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    barangay = db.Column(db.String(50), nullable=False)
    skills = db.Column(db.String(200))
    education = db.Column(db.String(50))
    employment = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Official(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    barangay = db.Column(db.String(50))
    photo_url = db.Column(db.String(100)) # e.g., 'officer1.jpg'


class LydoStructure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lydo_head = db.Column(db.String(100))
    admin_staff = db.Column(db.Text)  # comma-separated list
    lydc_members = db.Column(db.Text)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    email = db.Column(db.String(120), unique=True, nullable=True)
    confirmed = db.Column(db.Boolean, default=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def generate_confirmation_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.email or self.username, salt='email-confirm-salt')

    @staticmethod
    def confirm_token(token, expiration=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt='email-confirm-salt', max_age=expiration)
        except Exception:
            return None
        return data