from app import db
from datetime import datetime
import uuid


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)  # 消息标题
    content = db.Column(db.String(500), nullable=False)  # 消息内容
    notification_type = db.Column(db.String(20), default='system')  # system/market/account
    is_read = db.Column(db.Boolean, default=False)  # 是否已读
    related_fund_code = db.Column(db.String(10))  # 相关基金代码
    related_transaction_id = db.Column(db.String(36))  # 相关交易ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)  # 阅读时间
    
    def __repr__(self):
        return f'<Notification {self.title}>'