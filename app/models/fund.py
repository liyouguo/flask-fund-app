from app import db
from datetime import datetime
import uuid


class Fund(db.Model):
    __tablename__ = 'funds'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fund_code = db.Column(db.String(10), unique=True, nullable=False)  # 基金代码
    fund_name = db.Column(db.String(100), nullable=False)  # 基金名称
    fund_type = db.Column(db.String(20))  # 基金类型
    risk_level = db.Column(db.String(10))  # 风险等级
    company = db.Column(db.String(100))  # 基金公司
    establishment_date = db.Column(db.Date)  # 成立日期
    net_asset_value = db.Column(db.Numeric(10, 4))  # 基金规模
    management_fee = db.Column(db.Numeric(5, 4))  # 管理费率
    custody_fee = db.Column(db.Numeric(5, 4))  # 托管费率
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    market_data = db.relationship('FundMarketData', backref='fund', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('FavoriteFundRelation', backref='fund', lazy=True)
    holdings = db.relationship('Holding', backref='fund', lazy=True)
    transactions = db.relationship('Transaction', backref='fund', lazy=True)
    
    def __repr__(self):
        return f'<Fund {self.fund_code} - {self.fund_name}>'


class FundMarketData(db.Model):
    __tablename__ = 'fund_market_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    net_value = db.Column(db.Numeric(10, 4))  # 最新净值
    daily_change = db.Column(db.Numeric(8, 4))  # 日涨跌额
    daily_change_rate = db.Column(db.Numeric(6, 2))  # 日涨跌幅
    weekly_change_rate = db.Column(db.Numeric(6, 2))  # 周涨跌幅
    monthly_change_rate = db.Column(db.Numeric(6, 2))  # 月涨跌幅
    quarterly_change_rate = db.Column(db.Numeric(6, 2))  # 季度涨跌幅
    yearly_change_rate = db.Column(db.Numeric(6, 2))  # 年涨跌幅
    three_year_change_rate = db.Column(db.Numeric(6, 2))  # 三年涨跌幅
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FundMarketData {self.fund_code} - {self.net_value}>'


class FundGroup(db.Model):
    __tablename__ = 'fund_groups'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    group_name = db.Column(db.String(20), nullable=False)  # 分组名称
    order_index = db.Column(db.Integer, default=0)  # 排序序号
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认分组
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    favorites = db.relationship('FavoriteFundRelation', backref='group', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FundGroup {self.group_name}>'


class FavoriteFundRelation(db.Model):
    __tablename__ = 'favorite_fund_relations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    fund_code = db.Column(db.String(10), db.ForeignKey('funds.fund_code'), nullable=False)
    group_id = db.Column(db.String(36), db.ForeignKey('fund_groups.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<FavoriteFundRelation {self.user_id} - {self.fund_code}>'