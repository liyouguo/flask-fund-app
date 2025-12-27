from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.notification import Notification
from app.models.user import User
from app import db
from datetime import datetime

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
    'created_at': fields.DateTime(description='创建时间'),
    'read_at': fields.DateTime(description='阅读时间')
})

notifications_pagination_model = api.model('NotificationsPagination', {
    'items': fields.List(fields.Nested(notification_model), description='消息列表'),
    'total': fields.Integer(description='总数'),
    'page': fields.Integer(description='当前页'),
    'pages': fields.Integer(description='总页数'),
    'per_page': fields.Integer(description='每页数量'),
    'has_next': fields.Boolean(description='是否有下一页'),
    'has_prev': fields.Boolean(description='是否有上一页')
})


@api.route('/')
class NotificationList(Resource):
    @jwt_required()
    @api.doc('list_notifications')
    @api.marshal_with(notifications_pagination_model)
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
        
        pagination = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }


@api.route('/<string:notification_id>')
@api.param('notification_id', '消息ID')
class NotificationResource(Resource):
    @jwt_required()
    @api.doc('get_notification')
    @api.marshal_with(notification_model)
    def get(self, notification_id):
        """获取消息详情"""
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        
        if not notification:
            api.abort(404, '消息不存在')
        
        return notification
    
    @jwt_required()
    @api.doc('delete_notification')
    def delete(self, notification_id):
        """删除消息"""
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        
        if not notification:
            api.abort(404, '消息不存在')
        
        db.session.delete(notification)
        db.session.commit()
        
        return {'message': '消息已删除'}, 200


@api.route('/<string:notification_id>/read')
@api.param('notification_id', '消息ID')
class NotificationRead(Resource):
    @jwt_required()
    @api.doc('mark_notification_read')
    @api.marshal_with(notification_model)
    def put(self, notification_id):
        """标记消息为已读"""
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        
        if not notification:
            api.abort(404, '消息不存在')
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        db.session.commit()
        
        return notification


@api.route('/read-all')
class NotificationReadAll(Resource):
    @jwt_required()
    @api.doc('mark_all_notifications_read')
    def put(self):
        """标记所有消息为已读"""
        current_user_id = get_jwt_identity()
        
        notifications = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).all()
        
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'message': f'已标记 {len(notifications)} 条消息为已读'}, 200