from app import db
from datetime import datetime
import uuid


class RecurringInvestment(db.Model):
    """
    定投计划模型
    """
    __tablename__ = 'recurring_investments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # 定投金额
    frequency = db.Column(db.String(20), nullable=False)  # 定投频率: daily, weekly, biweekly, monthly
    start_date = db.Column(db.Date, nullable=False)  # 开始日期
    end_date = db.Column(db.Date)  # 结束日期（可选）
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    next_investment_date = db.Column(db.Date)  # 下次定投日期
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='recurring_investments')
    fund = db.relationship('Fund', backref='recurring_investments')
    
    def __repr__(self):
        return f'<RecurringInvestment {self.user_id} - {self.fund_code} - {self.amount}>'