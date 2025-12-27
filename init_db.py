import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, UserProfile, UserSetting
from app.models.fund import Fund, FundMarketData, FundGroup, FavoriteFundRelation
from app.models.transaction import Holding, Transaction
from app.models.notification import Notification
from datetime import datetime

app = create_app()

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