from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_jwt_extended import JWTManager
from config import Config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)

    # 创建API实例并初始化
    api = Api(
        app,
        title='场外基金投资辅助工具 API',
        version='1.0',
        description='场外基金投资辅助工具后端API接口',
        doc='/docs/'
    )

    # 注册API命名空间，指定正确的路径
    from app.api.auth import api as auth_api
    from app.api.fund import api as fund_api
    from app.api.favorite import api as favorite_api
    from app.api.market import api as market_api
    from app.api.transaction import api as transaction_api
    from app.api.notification import api as notification_api
    from app.api.settings import api as settings_api
    from app.api.home import api as home_api
    
    api.add_namespace(auth_api, path='/api/auth')
    api.add_namespace(fund_api, path='/api/funds')
    api.add_namespace(favorite_api, path='/api/favorites')
    api.add_namespace(market_api, path='/api/market')
    api.add_namespace(transaction_api, path='/api/transactions')
    api.add_namespace(notification_api, path='/api/notifications')
    api.add_namespace(settings_api, path='/api/settings')
    api.add_namespace(home_api, path='/api/home')

    return app