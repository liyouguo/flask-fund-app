from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserSetting

api = Namespace('settings', description='用户设置相关操作')

# 数据模型定义
user_setting_model = api.model('UserSetting', {
    'id': fields.String(required=True, description='设置ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'notification_enabled': fields.Boolean(required=True, description='通知启用'),
    'market_alert_enabled': fields.Boolean(required=True, description='市场提醒启用'),
    'theme_setting': fields.String(required=True, description='主题设置'),
    'font_size': fields.String(required=True, description='字体大小')
})

update_setting_model = api.model('UpdateSetting', {
    'notification_enabled': fields.Boolean(description='通知启用'),
    'market_alert_enabled': fields.Boolean(description='市场提醒启用'),
    'theme_setting': fields.String(description='主题设置'),
    'font_size': fields.String(description='字体大小')
})

@api.route('/')
class UserSettings(Resource):
    @api.doc('get_settings')
    @jwt_required()
    @api.marshal_with(user_setting_model)
    def get(self):
        """获取用户设置"""
        current_user_id = get_jwt_identity()
        
        user_setting = UserSetting.query.filter_by(user_id=current_user_id).first()
        
        if not user_setting:
            # 如果用户设置不存在，创建默认设置
            user_setting = UserSetting(user_id=current_user_id)
            db.session.add(user_setting)
            db.session.commit()
        
        setting_data = {
            'id': user_setting.id,
            'user_id': user_setting.user_id,
            'notification_enabled': user_setting.notification_enabled,
            'market_alert_enabled': user_setting.market_alert_enabled,
            'theme_setting': user_setting.theme_setting,
            'font_size': user_setting.font_size
        }
        
        return setting_data
    
    @api.doc('update_settings')
    @api.expect(update_setting_model)
    @jwt_required()
    @api.marshal_with(user_setting_model)
    def put(self):
        """更新用户设置"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        user_setting = UserSetting.query.filter_by(user_id=current_user_id).first()
        
        if not user_setting:
            # 如果用户设置不存在，创建新的设置
            user_setting = UserSetting(user_id=current_user_id)
            db.session.add(user_setting)
        
        # 更新设置
        if 'notification_enabled' in data:
            user_setting.notification_enabled = data['notification_enabled']
        if 'market_alert_enabled' in data:
            user_setting.market_alert_enabled = data['market_alert_enabled']
        if 'theme_setting' in data:
            user_setting.theme_setting = data['theme_setting']
        if 'font_size' in data:
            user_setting.font_size = data['font_size']
        
        db.session.commit()
        
        setting_data = {
            'id': user_setting.id,
            'user_id': user_setting.user_id,
            'notification_enabled': user_setting.notification_enabled,
            'market_alert_enabled': user_setting.market_alert_enabled,
            'theme_setting': user_setting.theme_setting,
            'font_size': user_setting.font_size
        }
        
        return setting_data

@api.route('/clear-cache')
class ClearCache(Resource):
    @api.doc('clear_cache')
    @jwt_required()
    def post(self):
        """清理缓存"""
        # 这里可以实现清理缓存的逻辑
        # 对于Web API，通常只是返回成功消息
        # 实际的缓存清理可能在服务器端进行
        
        return {'message': '缓存清理成功'}, 200