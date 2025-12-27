from app import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    favorites = db.relationship('FavoriteFundRelation', backref='user', lazy=True, cascade='all, delete-orphan')
    holdings = db.relationship('Holding', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('UserSetting', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    real_name = db.Column(db.String(50))
    id_card_number = db.Column(db.String(20))  # 身份证号
    phone_number = db.Column(db.String(20))
    gender = db.Column(db.String(10))  # 男/女/保密
    birthday = db.Column(db.Date)
    risk_level = db.Column(db.String(10))  # R1-R5风险等级
    last_login_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.real_name}>'


class UserSetting(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    notification_enabled = db.Column(db.Boolean, default=True)
    market_alert_enabled = db.Column(db.Boolean, default=True)
    theme_setting = db.Column(db.String(20), default='light')  # light/dark/auto
    font_size = db.Column(db.String(20), default='medium')  # small/medium/large
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)