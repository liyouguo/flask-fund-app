from app import db
from datetime import datetime
import uuid


class Holding(db.Model):
    __tablename__ = 'holdings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    shares = db.Column(db.Numeric(15, 4), default=0.0000)  # 持有份额
    cost_basis = db.Column(db.Numeric(15, 2), default=0.00)  # 成本基础
    current_value = db.Column(db.Numeric(15, 2), default=0.00)  # 当前市值
    daily_pnl = db.Column(db.Numeric(15, 2), default=0.00)  # 当日盈亏
    daily_pnl_rate = db.Column(db.Numeric(6, 2), default=0.00)  # 当日盈亏率
    total_pnl = db.Column(db.Numeric(15, 2), default=0.00)  # 累计盈亏
    total_pnl_rate = db.Column(db.Numeric(6, 2), default=0.00)  # 累计盈亏率
    latest_net_value = db.Column(db.Numeric(10, 4))  # 最新净值
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Holding {self.user_id} - {self.fund_code}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 买入/卖出/定投
    transaction_amount = db.Column(db.Numeric(15, 2))  # 交易金额
    transaction_shares = db.Column(db.Numeric(15, 4))  # 交易份额
    transaction_price = db.Column(db.Numeric(10, 4))  # 交易价格
    fee = db.Column(db.Numeric(10, 2), default=0.00)  # 手续费
    transaction_status = db.Column(db.String(20), default='pending')  # pending/success/failed
    transaction_time = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_time = db.Column(db.DateTime)  # 确认时间
    order_id = db.Column(db.String(30))  # 订单号
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.order_id} - {self.transaction_type}>'