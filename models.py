from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    urls = db.relationship('URLMapping', backref='user', lazy=True)

class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(6), unique=True, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)
    custom_url = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
