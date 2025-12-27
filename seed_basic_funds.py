#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加基础基金数据脚本
用于向数据库中添加基础基金数据，供API测试使用
"""

import os
import sys
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.fund import Fund, FundMarketData
from app import db


def seed_basic_funds():
    """添加基础基金数据"""
    app = create_app()
    
    with app.app_context():
        print("开始添加基础基金数据...")
        
        # 检查是否已有基金数据
        existing_fund_count = Fund.query.count()
        if existing_fund_count > 0:
            print(f"数据库中已有 {existing_fund_count} 只基金，跳过添加")
            return
        
        # 添加基础基金数据
        funds_data = [
            {
                'fund_code': '000001', 
                'fund_name': '华夏成长混合', 
                'fund_type': '混合型', 
                'risk_level': '中风险', 
                'company': '华夏基金'
            },
            {
                'fund_code': '000002', 
                'fund_name': '易方达消费行业股票', 
                'fund_type': '股票型', 
                'risk_level': '高风险', 
                'company': '易方达基金'
            },
            {
                'fund_code': '000003', 
                'fund_name': '嘉实沪深300ETF联接', 
                'fund_type': '指数型', 
                'risk_level': '中风险', 
                'company': '嘉实基金'
            },
            {
                'fund_code': '000004', 
                'fund_name': '南方中证500ETF联接', 
                'fund_type': '指数型', 
                'risk_level': '中风险', 
                'company': '南方基金'
            },
            {
                'fund_code': '000005', 
                'fund_name': '招商中证白酒指数', 
                'fund_type': '指数型', 
                'risk_level': '高风险', 
                'company': '招商基金'
            },
        ]
        
        for fund_data in funds_data:
            # 检查基金是否已存在
            existing_fund = Fund.query.filter_by(fund_code=fund_data['fund_code']).first()
            if not existing_fund:
                fund = Fund(**fund_data)
                db.session.add(fund)
                print(f"添加基金: {fund_data['fund_code']} - {fund_data['fund_name']}")
        
        # 添加市场数据
        market_data = [
            {
                'fund_code': '000001', 
                'net_value': Decimal('1.5678'), 
                'daily_change': Decimal('0.0123'), 
                'daily_change_rate': Decimal('0.79')
            },
            {
                'fund_code': '000002', 
                'net_value': Decimal('2.3456'), 
                'daily_change': Decimal('-0.0234'), 
                'daily_change_rate': Decimal('-0.99')
            },
            {
                'fund_code': '000003', 
                'net_value': Decimal('0.8765'), 
                'daily_change': Decimal('0.0087'), 
                'daily_change_rate': Decimal('1.00')
            },
            {
                'fund_code': '000004', 
                'net_value': Decimal('0.9876'), 
                'daily_change': Decimal('-0.0156'), 
                'daily_change_rate': Decimal('-1.56')
            },
            {
                'fund_code': '000005', 
                'net_value': Decimal('0.7654'), 
                'daily_change': Decimal('0.0234'), 
                'daily_change_rate': Decimal('3.12')
            },
        ]
        
        for data in market_data:
            # 检查市场数据是否已存在
            existing_market_data = FundMarketData.query.filter_by(fund_code=data['fund_code']).first()
            if not existing_market_data:
                market_entry = FundMarketData(**data)
                db.session.add(market_entry)
                print(f"添加市场数据: {data['fund_code']} - 净值 {data['net_value']}")
        
        db.session.commit()
        
        print("基础基金数据添加完成！")
        print(f"添加了 {len(funds_data)} 只基金")
        print(f"添加了 {len(market_data)} 条市场数据")


if __name__ == '__main__':
    seed_basic_funds()