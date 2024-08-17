from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import DateTime
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    urls = db.relationship('URLMapping', backref='user', lazy=True, cascade="all, delete-orphan")
    
    @property 
    def is_active(self):
        # If you don't have an "active" column, just return True
        return True    
    @property 
    def is_authenticated(self):
        # Always returns True because the presence of the user object indicates the user is authenticated
        return True
    @property
    def is_anonymous(self):
        # Return False because a valid user object indicates the user is not anonymous
        return False
    
    def get_id(self):
        return str(self.id)
class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(6), unique=True, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)
    custom_url = db.Column(db.String(64), unique=True)
    created_at = db.Column(DateTime, default=datetime.datetime())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    clicks = db.relationship('Click', backref='url_mapping', lazy=True)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)  # Supports IPv4 and IPv6
    country = db.Column(db.String(100))
    user_agent = db.Column(db.String(256))
    url_id = db.Column(db.Integer, db.ForeignKey('url_mapping.id'), nullable=False)
