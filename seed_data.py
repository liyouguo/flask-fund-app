#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据注入脚本
用于向数据库中添加测试数据
"""

import os
import sys
import uuid
from datetime import datetime, date
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User, UserProfile, UserSetting
from app.models.fund import Fund, FundMarketData, FundGroup, FavoriteFundRelation
from app.models.transaction import Holding, Transaction
from app.models.notification import Notification
from app import db


def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        print("开始注入测试数据...")
        
        # 清空现有数据（可选）
        print("清空现有测试数据...")
        db.session.execute(db.delete(Notification))
        db.session.execute(db.delete(Transaction))
        db.session.execute(db.delete(Holding))
        db.session.execute(db.delete(FavoriteFundRelation))
        db.session.execute(db.delete(FundGroup))
        db.session.execute(db.delete(FundMarketData))
        db.session.execute(db.delete(Fund))
        db.session.execute(db.delete(UserSetting))
        db.session.execute(db.delete(UserProfile))
        db.session.execute(db.delete(User))
        db.session.commit()
        
        print("创建用户数据...")
        # 创建测试用户
        test_user = User(
            username='testuser',
            email='test@example.com'
        )
        test_user.set_password('testpassword123')
        db.session.add(test_user)
        db.session.flush()  # 确保ID被分配
        
        # 创建用户资料和设置
        user_profile = UserProfile(user_id=test_user.id)
        user_setting = UserSetting(user_id=test_user.id)
        
        db.session.add(user_profile)
        db.session.add(user_setting)
        
        # 创建默认分组
        default_group = FundGroup(
            user_id=test_user.id,
            group_name='我的自选',
            is_default=True
        )
        db.session.add(default_group)
        db.session.flush()
        
        print("创建基金基础数据...")
        # 创建一些基金数据
        funds_data = [
            {'fund_code': '000001', 'fund_name': '华夏成长混合', 'fund_type': '混合型', 'risk_level': '中风险', 'company': '华夏基金'},
            {'fund_code': '000002', 'fund_name': '易方达消费行业股票', 'fund_type': '股票型', 'risk_level': '高风险', 'company': '易方达基金'},
            {'fund_code': '000003', 'fund_name': '嘉实沪深300ETF联接', 'fund_type': '指数型', 'risk_level': '中风险', 'company': '嘉实基金'},
            {'fund_code': '000004', 'fund_name': '南方中证500ETF联接', 'fund_type': '指数型', 'risk_level': '中风险', 'company': '南方基金'},
            {'fund_code': '000005', 'fund_name': '招商中证白酒指数', 'fund_type': '指数型', 'risk_level': '高风险', 'company': '招商基金'},
        ]
        
        for fund_data in funds_data:
            fund = Fund(**fund_data)
            db.session.add(fund)
        
        db.session.commit()
        
        print("创建基金市场数据...")
        # 创建基金市场数据
        market_data = [
            {'fund_code': '000001', 'net_value': Decimal('1.5678'), 'daily_change': Decimal('0.0123'), 'daily_change_rate': Decimal('0.79')},
            {'fund_code': '000002', 'net_value': Decimal('2.3456'), 'daily_change': Decimal('-0.0234'), 'daily_change_rate': Decimal('-0.99')},
            {'fund_code': '000003', 'net_value': Decimal('0.8765'), 'daily_change': Decimal('0.0087'), 'daily_change_rate': Decimal('1.00')},
            {'fund_code': '000004', 'net_value': Decimal('0.9876'), 'daily_change': Decimal('-0.0156'), 'daily_change_rate': Decimal('-1.56')},
            {'fund_code': '000005', 'net_value': Decimal('0.7654'), 'daily_change': Decimal('0.0234'), 'daily_change_rate': Decimal('3.12')},
        ]
        
        for data in market_data:
            market_entry = FundMarketData(**data)
            db.session.add(market_entry)
        
        db.session.commit()
        
        print("创建持仓数据...")
        # 创建持仓数据
        holdings_data = [
            {'user_id': test_user.id, 'fund_code': '000001', 'shares': Decimal('1000.0000'), 'cost_basis': Decimal('1500.00')},
            {'user_id': test_user.id, 'fund_code': '000002', 'shares': Decimal('500.0000'), 'cost_basis': Decimal('1200.00')},
            {'user_id': test_user.id, 'fund_code': '000003', 'shares': Decimal('800.0000'), 'cost_basis': Decimal('700.00')},
        ]
        
        for holding_data in holdings_data:
            holding = Holding(**holding_data)
            db.session.add(holding)
        
        db.session.commit()
        
        print("创建交易记录...")
        # 创建交易记录
        transactions_data = [
            {
                'user_id': test_user.id,
                'fund_code': '000001',
                'transaction_type': 'buy',
                'transaction_amount': Decimal('1000.00'),
                'transaction_shares': Decimal('638.0000'),
                'transaction_price': Decimal('1.5678'),
                'fee': Decimal('1.50'),
                'transaction_status': 'success',
                'transaction_time': datetime.now()
            },
            {
                'user_id': test_user.id,
                'fund_code': '000002',
                'transaction_type': 'buy',
                'transaction_amount': Decimal('1200.00'),
                'transaction_shares': Decimal('511.0000'),
                'transaction_price': Decimal('2.3456'),
                'fee': Decimal('1.80'),
                'transaction_status': 'success',
                'transaction_time': datetime.now()
            },
            {
                'user_id': test_user.id,
                'fund_code': '000003',
                'transaction_type': 'buy',
                'transaction_amount': Decimal('700.00'),
                'transaction_shares': Decimal('798.0000'),
                'transaction_price': Decimal('0.8765'),
                'fee': Decimal('1.05'),
                'transaction_status': 'success',
                'transaction_time': datetime.now()
            }
        ]
        
        for transaction_data in transactions_data:
            transaction = Transaction(**transaction_data)
            db.session.add(transaction)
        
        db.session.commit()
        
        print("创建自选数据...")
        # 创建自选关系
        favorite_relations = [
            {'user_id': test_user.id, 'fund_code': '000001', 'group_id': default_group.id},
            {'user_id': test_user.id, 'fund_code': '000002', 'group_id': default_group.id},
            {'user_id': test_user.id, 'fund_code': '000005', 'group_id': default_group.id},
        ]
        
        for relation_data in favorite_relations:
            relation = FavoriteFundRelation(**relation_data)
            db.session.add(relation)
        
        db.session.commit()
        
        print("创建消息通知...")
        # 创建消息通知
        notifications_data = [
            {
                'user_id': test_user.id,
                'title': '市场提醒：华夏成长混合今日上涨0.79%',
                'content': '您关注的华夏成长混合基金今日表现良好，净值上涨0.79%',
                'notification_type': 'market',
                'related_fund_code': '000001'
            },
            {
                'user_id': test_user.id,
                'title': '持仓提醒：您的总资产有所增加',
                'content': '根据最新市场数据，您的总资产较昨日有所增加',
                'notification_type': 'portfolio',
            },
            {
                'user_id': test_user.id,
                'title': '系统通知：新功能上线',
                'content': '我们新增了定投计划功能，欢迎体验',
                'notification_type': 'system',
            }
        ]
        
        for notification_data in notifications_data:
            notification = Notification(**notification_data)
            db.session.add(notification)
        
        db.session.commit()
        
        print("测试数据注入完成！")
        print(f"创建了1个用户")
        print(f"创建了5只基金")
        print(f"创建了3个持仓记录")
        print(f"创建了3个交易记录")
        print(f"创建了3个自选关系")
        print(f"创建了3条消息通知")


def verify_data():
    """验证数据是否正确插入"""
    app = create_app()
    
    with app.app_context():
        print("\n验证数据...")
        
        # 验证用户
        user_count = User.query.count()
        print(f"用户数量: {user_count}")
        
        # 验证基金
        fund_count = Fund.query.count()
        print(f"基金数量: {fund_count}")
        
        # 验证持仓
        holding_count = Holding.query.count()
        print(f"持仓数量: {holding_count}")
        
        # 验证交易
        transaction_count = Transaction.query.count()
        print(f"交易数量: {transaction_count}")
        
        # 验证自选
        favorite_count = FavoriteFundRelation.query.count()
        print(f"自选数量: {favorite_count}")
        
        # 验证消息
        notification_count = Notification.query.count()
        print(f"消息数量: {notification_count}")
        
        print("数据验证完成！")


if __name__ == '__main__':
    create_test_data()
    verify_data()