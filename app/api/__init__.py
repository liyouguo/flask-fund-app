from flask import Blueprint

bp = Blueprint('api', __name__)

# 导入各个API模块，以便注册路由
from app.api import auth, fund, favorite, market, transaction, notification, settings

# 定义API命名空间，供app/__init__.py使用
from app.api.auth import api as auth_api
from app.api.fund import api as fund_api
from app.api.favorite import api as favorite_api
from app.api.market import api as market_api
from app.api.transaction import api as transaction_api
from app.api.notification import api as notification_api
from app.api.settings import api as settings_api

__all__ = [
    'bp',
    'auth_api',
    'fund_api', 
    'favorite_api',
    'market_api',
    'transaction_api',
    'notification_api',
    'settings_api'
]