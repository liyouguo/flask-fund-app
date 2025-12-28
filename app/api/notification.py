from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.notification import Notification
from app.models.user import User
from app.models.fund import Fund
from app.models.transaction import Transaction

api = Namespace('notifications', description='消息通知相关操作')

# 数据模型定义
notification_model = api.model('Notification', {
    'id': fields.String(required=True, description='消息ID'),
    'title': fields.String(required=True, description='消息标题'),
    'content': fields.String(required=True, description='消息内容'),
    'notification_type': fields.String(required=True, description='消息类型'),
    'is_read': fields.Boolean(required=True, description='是否已读'),
    'related_fund_code': fields.String(description='相关基金代码'),
    'related_transaction_id': fields.String(description='相关交易ID'),
    'created_at': fields.DateTime(required=True, description='创建时间'),
    'read_at': fields.DateTime(description='阅读时间')
})

notification_list_model = api.model('NotificationList', {
    'items': fields.List(fields.Nested(notification_model)),
    'total': fields.Integer,
    'page': fields.Integer,
    'pages': fields.Integer,
    'per_page': fields.Integer,
    'has_next': fields.Boolean,
    'has_prev': fields.Boolean
})

@api.route('/')
class NotificationList(Resource):
    @api.doc('list_notifications')
    @jwt_required()
    @api.marshal_with(notification_list_model)
    def get(self):
        """获取消息列表"""
        current_user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        notification_type = request.args.get('type')
        is_read = request.args.get('is_read')
        
        query = Notification.query.filter_by(user_id=current_user_id)
        
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        
        if is_read is not None:
            is_read_bool = is_read.lower() in ['true', '1', 'yes']
            query = query.filter(Notification.is_read == is_read_bool)
        
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'items': [],
            'total': notifications.total,
            'page': notifications.page,
            'pages': notifications.pages,
            'per_page': notifications.per_page,
            'has_next': notifications.has_next,
            'has_prev': notifications.has_prev
        }
        
        for notification in notifications.items:
            notification_data = {
                'id': notification.id,
                'title': notification.title,
                'content': notification.content,
                'notification_type': notification.notification_type,
                'is_read': notification.is_read,
                'related_fund_code': notification.related_fund_code,
                'related_transaction_id': notification.related_transaction_id,
                'created_at': notification.created_at,
                'read_at': notification.read_at
            }
            result['items'].append(notification_data)
        
        return result

@api.route('/<string:notification_id>')
@api.param('notification_id', '消息ID')
class NotificationDetail(Resource):
    @api.doc('get_notification')
    @jwt_required()
    @api.marshal_with(notification_model)
    def get(self, notification_id):
        """获取消息详情"""
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first_or_404()
        
        # 标记为已读
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = db.func.current_timestamp()
            db.session.commit()
        
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'content': notification.content,
            'notification_type': notification.notification_type,
            'is_read': notification.is_read,
            'related_fund_code': notification.related_fund_code,
            'related_transaction_id': notification.related_transaction_id,
            'created_at': notification.created_at,
            'read_at': notification.read_at
        }
        
        return notification_data

@api.route('/<string:notification_id>/read')
@api.param('notification_id', '消息ID')
class NotificationMarkRead(Resource):
    @api.doc('mark_notification_read')
    @jwt_required()
    @api.marshal_with(notification_model)
    def put(self, notification_id):
        """标记消息为已读"""
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first_or_404()
        
        notification.is_read = True
        notification.read_at = db.func.current_timestamp()
        db.session.commit()
        
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'content': notification.content,
            'notification_type': notification.notification_type,
            'is_read': notification.is_read,
            'related_fund_code': notification.related_fund_code,
            'related_transaction_id': notification.related_transaction_id,
            'created_at': notification.created_at,
            'read_at': notification.read_at
        }
        
        return notification_data
@api.route('/read-all')
class NotificationMarkAllRead(Resource):
    @api.doc('mark_all_notifications_read')
    @jwt_required()
    def put(self):
        """标记所有消息为已读"""
        current_user_id = get_jwt_identity()
        
        db.session.query(Notification).filter(
            Notification.user_id == current_user_id,
            Notification.is_read == False
        ).update({Notification.is_read: True, Notification.read_at: db.func.current_timestamp()})
        
        db.session.commit()
        
        return {'message': '所有消息已标记为已读'}, 200

@api.route('/<string:notification_id>')
@api.param('notification_id', '消息ID')
class Notification(Resource):
    @api.doc('delete_notification')
    @jwt_required()
    def delete(self, notification_id):
        """删除消息"""
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first_or_404()
        
        db.session.delete(notification)
        db.session.commit()
        
        return {'message': '消息已删除'}, 200