from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from app import db
from datetime import datetime

api = Namespace('auth', description='用户认证相关操作')

# 数据模型定义
user_model = api.model('User', {
    'id': fields.String(required=True, description='用户ID'),
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码')
})

login_response_model = api.model('LoginResponse', {
    'access_token': fields.String(description='访问令牌'),
    'refresh_token': fields.String(description='刷新令牌'),
    'user': fields.Nested(user_model, description='用户信息')
})

refresh_token_model = api.model('RefreshToken', {
    'access_token': fields.String(description='新的访问令牌')
})

register_model = api.model('Register', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码')
})

profile_model = api.model('Profile', {
    'id': fields.String(required=True, description='用户ID'),
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'created_at': fields.DateTime(description='创建时间')
})


@api.route('/register')
class Register(Resource):
    @api.expect(register_model)
    @api.marshal_with(user_model)
    @api.response(201, '用户注册成功')
    def post(self):
        """用户注册"""
        data = request.get_json()
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            api.abort(400, '邮箱已被注册')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            api.abort(400, '用户名已被使用')
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # 创建用户资料记录
        from app.models.user import UserProfile, UserSetting
        user_profile = UserProfile(user_id=user.id)
        user_setting = UserSetting(user_id=user.id)
        
        db.session.add(user_profile)
        db.session.add(user_setting)
        db.session.commit()
        
        return user, 201


@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.marshal_with(login_response_model)
    @api.response(200, '登录成功')
    def post(self):
        """用户登录"""
        data = request.get_json()
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            # 更新最后登录时间
            user_profile = user.profile
            user_profile.last_login_time = datetime.utcnow()
            db.session.commit()
            
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, 200
        else:
            api.abort(401, '邮箱或密码错误')


@api.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    @api.doc('refresh_token')
    @api.marshal_with(refresh_token_model)
    def post(self):
        """刷新访问令牌"""
        current_user_id = get_jwt_identity()
        
        # 验证用户是否存在
        user = User.query.get(current_user_id)
        if not user:
            api.abort(404, '用户不存在')
        
        new_access_token = create_access_token(identity=current_user_id)
        
        return {
            'access_token': new_access_token
        }


@api.route('/profile')
class Profile(Resource):
    @jwt_required()
    @api.marshal_with(profile_model)
    def get(self):
        """获取用户资料"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            api.abort(404, '用户不存在')
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        }
    
    @jwt_required()
    @api.expect(profile_model)
    @api.marshal_with(profile_model)
    def put(self):
        """更新用户资料"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            api.abort(404, '用户不存在')
        
        data = request.get_json()
        
        # 更新用户名（如果提供）
        if 'username' in data:
            # 检查新用户名是否已被使用
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user.id:
                api.abort(400, '用户名已被使用')
            user.username = data['username']
        
        db.session.commit()
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        }


@api.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        """用户登出"""
        # 在实际应用中，可能需要将JWT加入黑名单
        return {'message': '登出成功'}, 200