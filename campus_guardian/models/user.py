from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    college = db.Column(db.String(100), default='TKM College of Engineering')
    branch = db.Column(db.String(100), default='ECE/EEE')
    current_semester = db.Column(db.Integer, default=3)
    theme = db.Column(db.String(10), default='dark')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subjects = db.relationship('Subject', backref='user', lazy=True, cascade='all, delete-orphan')
    timetable = db.relationship('TimetableEntry', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
