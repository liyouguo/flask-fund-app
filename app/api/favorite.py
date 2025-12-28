from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.fund import Fund, FundGroup, FavoriteFundRelation

api = Namespace('favorites', description='自选功能相关操作')

# 数据模型定义
favorite_model = api.model('Favorite', {
    'id': fields.String(required=True, description='自选ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'group_id': fields.String(required=True, description='分组ID'),
    'added_at': fields.DateTime(description='添加时间')
})

favorite_with_fund_model = api.model('FavoriteWithFund', {
    'id': fields.String(required=True, description='自选ID'),
    'fund': fields.Raw(description='基金信息'),
    'group': fields.Raw(description='分组信息'),
    'added_at': fields.DateTime(description='添加时间')
})

group_model = api.model('Group', {
    'id': fields.String(required=True, description='分组ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'group_name': fields.String(required=True, description='分组名称'),
    'order_index': fields.Integer(description='排序序号'),
    'is_default': fields.Boolean(description='是否为默认分组'),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

favorite_group_model = api.model('FavoriteGroup', {
    'group': fields.Nested(group_model),
    'favorites': fields.List(fields.Nested(favorite_with_fund_model))
})

add_favorite_model = api.model('AddFavorite', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'group_id': fields.String(required=True, description='分组ID')
})

add_favorite_batch_model = api.model('AddFavoriteBatch', {
    'fund_codes': fields.List(fields.String, required=True, description='基金代码列表'),
    'group_id': fields.String(required=True, description='分组ID')
})

create_group_model = api.model('CreateGroup', {
    'group_name': fields.String(required=True, description='分组名称'),
    'order_index': fields.Integer(description='排序序号')
})

update_group_model = api.model('UpdateGroup', {
    'group_name': fields.String(required=True, description='新分组名称')
})

reorder_groups_model = api.model('ReorderGroups', {
    'group_ids': fields.List(fields.String, required=True, description='分组ID列表（按新顺序）')
})

@api.route('/')
class FavoriteList(Resource):
    @api.doc('list_favorites')
    @jwt_required()
    @api.marshal_with(favorite_group_model)
    def get(self):
        """获取用户自选基金列表"""
        current_user_id = get_jwt_identity()
        
        # 获取用户的所有分组
        groups = FundGroup.query.filter_by(user_id=current_user_id).order_by(FundGroup.order_index).all()
        
        result = []
        
        for group in groups:
            # 获取该分组下的自选基金
            favorites = FavoriteFundRelation.query.filter_by(
                user_id=current_user_id,
                group_id=group.id,
                is_deleted=False
            ).all()
            
            group_data = {
                'group': {
                    'id': group.id,
                    'user_id': group.user_id,
                    'group_name': group.group_name,
                    'order_index': group.order_index,
                    'is_default': group.is_default,
                    'created_at': group.created_at,
                    'updated_at': group.updated_at
                },
                'favorites': []
            }
            
            for favorite in favorites:
                fund = Fund.query.filter_by(fund_code=favorite.fund_code).first()
                if fund:
                    favorite_data = {
                        'id': favorite.id,
                        'fund': {
                            'fund_code': fund.fund_code,
                            'fund_name': fund.fund_name,
                            'fund_type': fund.fund_type,
                            'risk_level': fund.risk_level
                        },
                        'group': {
                            'id': group.id,
                            'user_id': group.user_id,
                            'group_name': group.group_name,
                            'order_index': group.order_index,
                            'is_default': group.is_default,
                            'created_at': group.created_at,
                            'updated_at': group.updated_at
                        },
                        'added_at': favorite.added_at
                    }
                    group_data['favorites'].append(favorite_data)
            
            result.append(group_data)
        
        return result

    @api.doc('add_favorite')
    @api.expect(add_favorite_model)
    @jwt_required()
    @api.marshal_with(favorite_model)
    def post(self):
        """添加基金到自选列表"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        fund_code = data.get('fund_code')
        group_id = data.get('group_id')
        
        # 验证基金是否存在
        fund = Fund.query.filter_by(fund_code=fund_code).first()
        if not fund:
            api.abort(404, '基金不存在')
        
        # 验证分组是否属于当前用户
        group = FundGroup.query.filter_by(id=group_id, user_id=current_user_id).first()
        if not group:
            api.abort(404, '分组不存在或不属于当前用户')
        
        # 检查是否已存在
        existing_favorite = FavoriteFundRelation.query.filter_by(
            user_id=current_user_id,
            fund_code=fund_code,
            group_id=group_id
        ).first()
        
        if existing_favorite:
            if existing_favorite.is_deleted:
                # 如果之前已删除，恢复它
                existing_favorite.is_deleted = False
                db.session.commit()
                return existing_favorite
            else:
                api.abort(400, '基金已在当前分组中')
        
        # 创建新的自选关系
        favorite = FavoriteFundRelation(
            user_id=current_user_id,
            fund_code=fund_code,
            group_id=group_id
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return favorite
@api.route('/batch')
class FavoriteBatch(Resource):
    @api.doc('add_favorite_batch')
    @api.expect(add_favorite_batch_model)
    @jwt_required()
    def post(self):
        """批量添加自选基金"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        fund_codes = data.get('fund_codes', [])
        group_id = data.get('group_id')
        
        # 验证分组是否属于当前用户
        group = FundGroup.query.filter_by(id=group_id, user_id=current_user_id).first()
        if not group:
            api.abort(404, '分组不存在或不属于当前用户')
        
        added_count = 0
        failed_funds = []
        
        for fund_code in fund_codes:
            # 验证基金是否存在
            fund = Fund.query.filter_by(fund_code=fund_code).first()
            if not fund:
                failed_funds.append({'fund_code': fund_code, 'reason': '基金不存在'})
                continue
            
            # 检查是否已存在
            existing_favorite = FavoriteFundRelation.query.filter_by(
                user_id=current_user_id,
                fund_code=fund_code,
                group_id=group_id
            ).first()
            
            if existing_favorite:
                if existing_favorite.is_deleted:
                    # 如果之前已删除，恢复它
                    existing_favorite.is_deleted = False
                else:
                    failed_funds.append({'fund_code': fund_code, 'reason': '基金已在当前分组中'})
                    continue
            else:
                # 创建新的自选关系
                favorite = FavoriteFundRelation(
                    user_id=current_user_id,
                    fund_code=fund_code,
                    group_id=group_id
                )
                db.session.add(favorite)
            
            added_count += 1
        
        db.session.commit()
        
        return {
            'message': f'批量添加完成，成功添加 {added_count} 只基金',
            'added_count': added_count,
            'failed_count': len(failed_funds),
            'failed_funds': failed_funds
        }, 200

@api.route('/<string:fund_code>')
@api.param('fund_code', '基金代码')
class Favorite(Resource):
    @api.doc('remove_favorite')
    @jwt_required()
    def delete(self, fund_code):
        """移除自选基金"""
        current_user_id = get_jwt_identity()
        
        # 查找用户在所有分组中的该基金自选记录
        favorites = FavoriteFundRelation.query.filter_by(
            user_id=current_user_id,
            fund_code=fund_code
        ).all()
        
        if not favorites:
            api.abort(404, '自选基金不存在')
        
        # 将自选记录标记为已删除
        for favorite in favorites:
            favorite.is_deleted = True
        
        db.session.commit()
        
        return {'message': '自选基金已移除'}, 200

@api.route('/groups')
class GroupList(Resource):
    @api.doc('list_groups')
    @jwt_required()
    @api.marshal_with(group_model)
    def get(self):
        """获取自选分组列表"""
        current_user_id = get_jwt_identity()
        
        groups = FundGroup.query.filter_by(user_id=current_user_id).order_by(FundGroup.order_index).all()
        
        return groups
    
    @api.doc('create_group')
    @api.expect(create_group_model)
    @jwt_required()
    @api.marshal_with(group_model)
    def post(self):
        """创建自选分组"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        group_name = data.get('group_name')
        order_index = data.get('order_index', 0)
        
        # 检查分组名称是否已存在
        existing_group = FundGroup.query.filter_by(
            user_id=current_user_id,
            group_name=group_name
        ).first()
        
        if existing_group:
            api.abort(400, '分组名称已存在')
        
        group = FundGroup(
            user_id=current_user_id,
            group_name=group_name,
            order_index=order_index
        )
        
        db.session.add(group)
        db.session.commit()
        
        return group

@api.route('/groups/<string:group_id>')
@api.param('group_id', '分组ID')
class Group(Resource):
    @api.doc('update_group')
    @api.expect(update_group_model)
    @jwt_required()
    @api.marshal_with(group_model)
    def put(self, group_id):
        """更新自选分组（重命名）"""
        current_user_id = get_jwt_identity()
        
        group = FundGroup.query.filter_by(id=group_id, user_id=current_user_id).first_or_404()
        
        data = request.get_json()
        new_name = data.get('group_name')
        
        # 检查新名称是否已存在
        existing_group = FundGroup.query.filter_by(
            user_id=current_user_id,
            group_name=new_name
        ).first()
        
        if existing_group and existing_group.id != group.id:
            api.abort(400, '分组名称已存在')
        
        group.group_name = new_name
        db.session.commit()
        
        return group
    
    @api.doc('delete_group')
    @jwt_required()
    def delete(self, group_id):
        """删除自选分组"""
        current_user_id = get_jwt_identity()
        
        group = FundGroup.query.filter_by(id=group_id, user_id=current_user_id).first_or_404()
        
        if group.is_default:
            api.abort(400, '不能删除默认分组')
        
        # 将该分组下的所有自选基金移到默认分组
        default_group = FundGroup.query.filter_by(user_id=current_user_id, is_default=True).first()
        if default_group:
            favorites = FavoriteFundRelation.query.filter_by(group_id=group_id).all()
            for favorite in favorites:
                favorite.group_id = default_group.id
        
        db.session.delete(group)
        db.session.commit()
        
        return {'message': '分组已删除'}, 200

@api.route('/groups/reorder')
class GroupReorder(Resource):
    @api.doc('reorder_groups')
    @api.expect(reorder_groups_model)
    @jwt_required()
    def put(self):
        """重新排序分组"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        group_ids = data.get('group_ids', [])
        
        # 验证所有分组都属于当前用户
        groups = FundGroup.query.filter(
            FundGroup.id.in_(group_ids),
            FundGroup.user_id == current_user_id
        ).all()
        
        if len(groups) != len(group_ids):
            api.abort(400, '部分分组不存在或不属于当前用户')
        
        # 更新排序
        for index, group_id in enumerate(group_ids):
            group = next(g for g in groups if g.id == group_id)
            group.order_index = index
        
        db.session.commit()
        
        return {'message': '分组排序更新成功'}, 200

@api.route('/groups/<string:group_id>/clear')
@api.param('group_id', '分组ID')
class GroupClear(Resource):
    @api.doc('clear_group')
    @jwt_required()
    def post(self, group_id):
        """清空分组（移除分组内所有基金）"""
        current_user_id = get_jwt_identity()
        
        group = FundGroup.query.filter_by(id=group_id, user_id=current_user_id).first_or_404()
        
        # 将该分组下的所有自选基金标记为删除
        favorites = FavoriteFundRelation.query.filter_by(group_id=group_id).all()
        for favorite in favorites:
            favorite.is_deleted = True
        
        db.session.commit()
        
        return {'message': f'分组 "{group.group_name}" 已清空'}, 200