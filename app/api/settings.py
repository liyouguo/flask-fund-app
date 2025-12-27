from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, UserSetting
from app import db
from datetime import datetime
import os
import shutil

api = Namespace('settings', description='用户设置相关操作')

# 数据模型定义
user_setting_model = api.model('UserSetting', {
    'id': fields.String(required=True, description='设置ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'notification_enabled': fields.Boolean(required=True, description='是否启用通知'),
    'market_alert_enabled': fields.Boolean(required=True, description='是否启用市场提醒'),
    'theme_setting': fields.String(required=True, description='主题设置'),
    'font_size': fields.String(required=True, description='字体大小'),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

update_setting_model = api.model('UpdateSetting', {
    'notification_enabled': fields.Boolean(description='是否启用通知'),
    'market_alert_enabled': fields.Boolean(description='是否启用市场提醒'),
    'theme_setting': fields.String(description='主题设置'),
    'font_size': fields.String(description='字体大小')
})

clear_cache_response_model = api.model('ClearCacheResponse', {
    'message': fields.String(required=True, description='响应消息'),
    'cache_cleared': fields.Boolean(required=True, description='是否成功清理缓存'),
    'size_cleared': fields.String(description='清理的缓存大小')
})


@api.route('/')
class UserSettings(Resource):
    @jwt_required()
    @api.doc('get_user_settings')
    @api.marshal_with(user_setting_model)
    def get(self):
        """获取用户设置"""
        current_user_id = get_jwt_identity()
        
        user_setting = UserSetting.query.filter_by(user_id=current_user_id).first()
        
        if not user_setting:
            api.abort(404, '用户设置不存在')
        
        return user_setting
    
    @jwt_required()
    @api.expect(update_setting_model)
    @api.doc('update_user_settings')
    @api.marshal_with(user_setting_model)
    def put(self):
        """更新用户设置"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        user_setting = UserSetting.query.filter_by(user_id=current_user_id).first()
        
        if not user_setting:
            api.abort(404, '用户设置不存在')
        
        # 更新设置
        for key, value in data.items():
            if hasattr(user_setting, key):
                setattr(user_setting, key, value)
        
        user_setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return user_setting


@api.route('/clear-cache')
class ClearCache(Resource):
    @jwt_required()
    @api.doc('clear_cache')
    @api.marshal_with(clear_cache_response_model)
    def post(self):
        """清理缓存"""
        # 计算清理前的缓存大小
        cache_dir = 'uploads'
        initial_size = 0
        if os.path.exists(cache_dir):
            for dirpath, dirnames, filenames in os.walk(cache_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    initial_size += os.path.getsize(filepath)
        
        # 清理缓存目录
        try:
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            
            # 转换字节为可读格式
            size_mb = initial_size / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB" if initial_size > 0 else "0 MB"
            
            return {
                'message': '缓存清理成功',
                'cache_cleared': True,
                'size_cleared': size_str
            }
        except Exception as e:
            return {
                'message': f'缓存清理失败: {str(e)}',
                'cache_cleared': False,
                'size_cleared': '0 MB'
            }, 500


@api.route('/about')
class About(Resource):
    @api.doc('about_app')
    def get(self):
        """获取应用信息"""
        return {
            'app_name': '场外基金投资辅助工具',
            'version': '1.0.0',
            'description': '一个帮助用户管理和分析基金投资的移动应用',
            'developer': '场外基金投资辅助工具开发团队',
            'contact': 'support@example.com'
        }