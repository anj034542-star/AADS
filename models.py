from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

db = SQLAlchemy()

# Predefined tracking IDs for residents (as in original)
AVAILABLE_IDS = [
    "UID-992-XQ-2026", "UID-118-BT-7734", "UID-404-NM-8812",
    "UID-607-TR-1190", "UID-223-KL-5561", "UID-884-PL-0092",
    "UID-331-VB-4478", "UID-559-QA-3321", "UID-770-MK-6610",
    "UID-101-ZZ-9943"
]

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), default='resident')  # 'resident' only
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    office = db.Column(db.String(100), nullable=False)  # e.g. "Barangay Officials"

    def __repr__(self):
        return f'<Admin {self.username} - {self.office}>'

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    office = db.Column(db.String(50))          # original office from upload form
    target_office = db.Column(db.String(50), default='Office 1')
    filename = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='PENDING')
    decline_reason = db.Column(db.Text, nullable=True)
    declined_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.String(80))     # username of resident

    def to_dict(self):
        return {
            'tracking_id': self.tracking_id,
            'title': self.title,
            'desc': self.description,
            'office': self.office,
            'target_office': self.target_office,
            'filename': self.filename,
            'status': self.status,
            'decline_reason': self.decline_reason,
            'declined_by': self.declined_by,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }

def generate_tracking_id():
    return f"TRK-{random.randint(10000, 99999)}"