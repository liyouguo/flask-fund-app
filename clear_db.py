#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清空数据库脚本
用于清空所有表的数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User, UserProfile, UserSetting
from app.models.fund import Fund, FundMarketData, FundGroup, FavoriteFundRelation
from app.models.transaction import Holding, Transaction
from app.models.notification import Notification
from app import db


def clear_database():
    """清空数据库"""
    app = create_app()
    
    with app.app_context():
        print("开始清空数据库...")
        
        # 按依赖顺序清空表（从依赖较多的表开始）
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
        
        print("数据库清空完成！")


if __name__ == '__main__':
    clear_database()