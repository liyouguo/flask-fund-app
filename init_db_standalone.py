from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# 创建独立的Flask应用和数据库实例用于初始化
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# 定义模型类（与现有模型保持一致）
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    real_name = db.Column(db.String(50))
    id_card_number = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    risk_level = db.Column(db.String(10))
    last_login_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSetting(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    notification_enabled = db.Column(db.Boolean, default=True)
    market_alert_enabled = db.Column(db.Boolean, default=True)
    theme_setting = db.Column(db.String(20), default='light')
    font_size = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 导入SQLAlchemy的ForeignKey
from sqlalchemy import ForeignKey

class Fund(db.Model):
    __tablename__ = 'funds'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fund_code = db.Column(db.String(10), unique=True, nullable=False)
    fund_name = db.Column(db.String(100), nullable=False)
    fund_type = db.Column(db.String(20))
    risk_level = db.Column(db.String(10))
    company = db.Column(db.String(100))
    establishment_date = db.Column(db.Date)
    net_asset_value = db.Column(db.Numeric(10, 4))
    management_fee = db.Column(db.Numeric(5, 4))
    custody_fee = db.Column(db.Numeric(5, 4))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FundMarketData(db.Model):
    __tablename__ = 'fund_market_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    net_value = db.Column(db.Numeric(10, 4))
    daily_change = db.Column(db.Numeric(8, 4))
    daily_change_rate = db.Column(db.Numeric(6, 2))
    weekly_change_rate = db.Column(db.Numeric(6, 2))
    monthly_change_rate = db.Column(db.Numeric(6, 2))
    quarterly_change_rate = db.Column(db.Numeric(6, 2))
    yearly_change_rate = db.Column(db.Numeric(6, 2))
    three_year_change_rate = db.Column(db.Numeric(6, 2))
    update_time = db.Column(db.DateTime, default=datetime.utcnow)

class FundGroup(db.Model):
    __tablename__ = 'fund_groups'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    group_name = db.Column(db.String(20), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FavoriteFundRelation(db.Model):
    __tablename__ = 'favorite_fund_relations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    group_id = db.Column(db.String(36), db.ForeignKey('fund_groups.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

class Holding(db.Model):
    __tablename__ = 'holdings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    shares = db.Column(db.Numeric(15, 4), default=0.0000)
    cost_basis = db.Column(db.Numeric(15, 2), default=0.00)
    current_value = db.Column(db.Numeric(15, 2), default=0.00)
    daily_pnl = db.Column(db.Numeric(15, 2), default=0.00)
    daily_pnl_rate = db.Column(db.Numeric(6, 2), default=0.00)
    total_pnl = db.Column(db.Numeric(15, 2), default=0.00)
    total_pnl_rate = db.Column(db.Numeric(6, 2), default=0.00)
    latest_net_value = db.Column(db.Numeric(10, 4))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    transaction_amount = db.Column(db.Numeric(15, 2))
    transaction_shares = db.Column(db.Numeric(15, 4))
    transaction_price = db.Column(db.Numeric(10, 4))
    fee = db.Column(db.Numeric(10, 2), default=0.00)
    transaction_status = db.Column(db.String(20), default='pending')
    transaction_time = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_time = db.Column(db.DateTime)
    order_id = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    notification_type = db.Column(db.String(20), default='system')
    is_read = db.Column(db.Boolean, default=False)
    related_fund_code = db.Column(db.String(10))
    related_transaction_id = db.Column(db.String(36))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认管理员用户（如果不存在）
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.flush()  # 确保ID被分配，但不提交事务
            
            # 为管理员创建资料和设置
            user_profile = UserProfile(user_id=admin_user.id)
            user_setting = UserSetting(user_id=admin_user.id)
            
            db.session.add(user_profile)
            db.session.add(user_setting)
            
            # 创建默认分组
            default_group = FundGroup(
                user_id=admin_user.id,
                group_name='全部自选',
                is_default=True
            )
            db.session.add(default_group)
            
            db.session.commit()
        
        print("数据库初始化完成！")

if __name__ == '__main__':
    init_database()