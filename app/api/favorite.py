from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from datetime import datetime

api = Namespace('favorites', description='自选功能相关操作')

# 数据模型定义
favorite_model = api.model('Favorite', {
    'id': fields.String(required=True, description='自选关系ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'group_id': fields.String(required=True, description='分组ID'),
    'added_at': fields.DateTime(description='添加时间'),
    'updated_at': fields.DateTime(description='更新时间'),
    'is_deleted': fields.Boolean(description='是否已删除')
})

fund_group_model = api.model('FundGroup', {
    'id': fields.String(required=True, description='分组ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'group_name': fields.String(required=True, description='分组名称'),
    'order_index': fields.Integer(description='排序序号'),
    'is_default': fields.Boolean(description='是否为默认分组'),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

favorite_with_fund_model = api.model('FavoriteWithFund', {
    'id': fields.String(required=True, description='自选关系ID'),
    'fund': fields.Nested(api.model('FundInFavorite', {
        'fund_code': fields.String(required=True, description='基金代码'),
        'fund_name': fields.String(required=True, description='基金名称'),
        'fund_type': fields.String(description='基金类型'),
        'risk_level': fields.String(description='风险等级')
    }), description='基金信息'),
    'group': fields.Nested(fund_group_model, description='分组信息'),
    'added_at': fields.DateTime(description='添加时间')
})

group_with_favorites_model = api.model('GroupWithFavorites', {
    'group': fields.Nested(fund_group_model, description='分组信息'),
    'favorites': fields.List(fields.Nested(favorite_with_fund_model), description='自选基金列表')
})

# 批量操作模型
batch_favorite_model = api.model('BatchFavorite', {
    'fund_codes': fields.List(fields.String, required=True, description='基金代码列表'),
    'group_id': fields.String(required=True, description='分组ID')
})

# 重命名分组模型
rename_group_model = api.model('RenameGroup', {
    'group_name': fields.String(required=True, description='新分组名称')
})

# 重排序模型
reorder_groups_model = api.model('ReorderGroups', {
    'group_ids': fields.List(fields.String, required=True, description='分组ID列表（按新顺序）')
})


def get_models():
    """延迟导入模型，避免初始化问题"""
    from app.models.fund import Fund, FundGroup, FavoriteFundRelation
    from app.models.user import User
    return Fund, FundGroup, FavoriteFundRelation, User


@api.route('/')
class FavoriteList(Resource):
    @jwt_required()
    @api.doc('list_favorites')
    @api.marshal_with(group_with_favorites_model)
    def get(self):
        """获取用户自选基金列表"""
        current_user_id = get_jwt_identity()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        # 获取用户的所有分组
        groups = FundGroup.query.filter_by(user_id=current_user_id).order_by(FundGroup.order_index).all()
        
        result = []
        for group in groups:
            # 获取该分组下的所有自选基金
            favorites = FavoriteFundRelation.query.filter_by(
                user_id=current_user_id,
                group_id=group.id,
                is_deleted=False
            ).all()
            
            # 为每个自选关系添加基金信息
            favorite_with_fund = []
            for favorite in favorites:
                fund = Fund.query.filter_by(fund_code=favorite.fund_code).first()
                if fund:  # 只添加存在的基金
                    favorite_with_fund.append({
                        'id': favorite.id,
                        'fund': {
                            'fund_code': fund.fund_code,
                            'fund_name': fund.fund_name,
                            'fund_type': fund.fund_type,
                            'risk_level': fund.risk_level
                        },
                        'group': group,
                        'added_at': favorite.added_at
                    })
            
            result.append({
                'group': group,
                'favorites': favorite_with_fund
            })
        
        return result
    
    @jwt_required()
    @api.expect(favorite_model)
    @api.marshal_with(favorite_model)
    @api.response(201, '自选基金添加成功')
    def post(self):
        """添加自选基金"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        # 验证基金是否存在
        fund = Fund.query.filter_by(fund_code=data['fund_code']).first()
        if not fund:
            api.abort(404, '基金不存在')
        
        # 验证分组是否存在且属于当前用户
        group = FundGroup.query.filter_by(
            id=data['group_id'], 
            user_id=current_user_id
        ).first()
        if not group:
            api.abort(404, '分组不存在或不属于当前用户')
        
        # 检查基金是否已在该分组中
        existing_favorite = FavoriteFundRelation.query.filter_by(
            user_id=current_user_id,
            fund_code=data['fund_code'],
            group_id=data['group_id'],
            is_deleted=False
        ).first()
        
        if existing_favorite:
            api.abort(400, '基金已在当前分组中')
        
        # 创建自选关系
        favorite = FavoriteFundRelation(
            user_id=current_user_id,
            fund_code=data['fund_code'],
            group_id=data['group_id']
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return favorite, 201


@api.route('/batch')
class FavoriteBatch(Resource):
    @jwt_required()
    @api.expect(batch_favorite_model)
    @api.doc('batch_add_favorites')
    def post(self):
        """批量添加自选基金"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        group_id = data.get('group_id')
        fund_codes = data.get('fund_codes', [])
        
        # 验证分组是否存在且属于当前用户
        group = FundGroup.query.filter_by(
            id=group_id, 
            user_id=current_user_id
        ).first()
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
            
            # 检查基金是否已在该分组中
            existing_favorite = FavoriteFundRelation.query.filter_by(
                user_id=current_user_id,
                fund_code=fund_code,
                group_id=group_id,
                is_deleted=False
            ).first()
            
            if existing_favorite:
                failed_funds.append({'fund_code': fund_code, 'reason': '基金已在当前分组中'})
                continue
            
            # 创建自选关系
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
        }


@api.route('/<string:fund_code>')
@api.param('fund_code', '基金代码')
class Favorite(Resource):
    @jwt_required()
    @api.doc('remove_favorite')
    def delete(self, fund_code):
        """移除自选基金"""
        current_user_id = get_jwt_identity()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        # 查找自选关系
        favorite = FavoriteFundRelation.query.filter_by(
            user_id=current_user_id,
            fund_code=fund_code,
            is_deleted=False
        ).first()
        
        if not favorite:
            api.abort(404, '自选基金不存在')
        
        # 逻辑删除
        favorite.is_deleted = True
        favorite.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'message': '自选基金已移除'}, 200


@api.route('/groups')
class FundGroupList(Resource):
    @jwt_required()
    @api.doc('list_groups')
    @api.marshal_with(fund_group_model)
    def get(self):
        """获取自选分组列表"""
        current_user_id = get_jwt_identity()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        groups = FundGroup.query.filter_by(user_id=current_user_id).order_by(FundGroup.order_index).all()
        return groups
    
    @jwt_required()
    @api.expect(fund_group_model)
    @api.marshal_with(fund_group_model)
    @api.response(201, '分组创建成功')
    def post(self):
        """创建自选分组"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        # 检查分组名称是否已存在
        existing_group = FundGroup.query.filter_by(
            user_id=current_user_id,
            group_name=data['group_name']
        ).first()
        
        if existing_group:
            api.abort(400, '分组名称已存在')
        
        # 创建新分组
        group = FundGroup(
            user_id=current_user_id,
            group_name=data['group_name'],
            order_index=data.get('order_index', 0)
        )
        
        db.session.add(group)
        db.session.commit()
        
        return group, 201


@api.route('/groups/<string:group_id>')
@api.param('group_id', '分组ID')
class FundGroup(Resource):
    @jwt_required()
    @api.doc('update_group')
    @api.expect(rename_group_model)
    @api.marshal_with(fund_group_model)
    def put(self, group_id):
        """更新自选分组（重命名）"""
        current_user_id = get_jwt_identity()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        group = FundGroup.query.filter_by(
            id=group_id,
            user_id=current_user_id
        ).first()
        
        if not group:
            api.abort(404, '分组不存在或不属于当前用户')
        
        data = request.get_json()
        
        # 检查新的分组名称是否已存在（排除当前分组）
        existing_group = FundGroup.query.filter(
            FundGroup.user_id == current_user_id,
            FundGroup.group_name == data['group_name'],
            FundGroup.id != group_id
        ).first()
        
        if existing_group:
            api.abort(400, '分组名称已存在')
        
        # 更新分组信息
        group.group_name = data['group_name']
        group.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return group
    
    @jwt_required()
    @api.doc('delete_group')
    def delete(self, group_id):
        """删除自选分组"""
        current_user_id = get_jwt_identity()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        group = FundGroup.query.filter_by(
            id=group_id,
            user_id=current_user_id
        ).first()
        
        if not group:
            api.abort(404, '分组不存在或不属于当前用户')
        
        # 检查是否为默认分组
        if group.is_default:
            api.abort(400, '默认分组不能删除')
        
        # 将该分组下的自选基金移动到默认分组
        default_group = FundGroup.query.filter_by(
            user_id=current_user_id,
            is_default=True
        ).first()
        
        if default_group:
            favorites = FavoriteFundRelation.query.filter_by(
                group_id=group_id
            ).all()
            
            for favorite in favorites:
                favorite.group_id = default_group.id
        
        # 删除分组
        db.session.delete(group)
        db.session.commit()
        
        return {'message': '分组已删除'}, 200


@api.route('/groups/reorder')
class FundGroupReorder(Resource):
    @jwt_required()
    @api.expect(reorder_groups_model)
    @api.doc('reorder_groups')
    def put(self):
        """重新排序分组"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        group_ids = data.get('group_ids', [])
        
        # 验证所有分组是否属于当前用户
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
class FundGroupClear(Resource):
    @jwt_required()
    @api.doc('clear_group')
    def post(self, group_id):
        """清空分组（移除分组内所有基金）"""
        current_user_id = get_jwt_identity()
        
        # 延迟导入模型
        Fund, FundGroup, FavoriteFundRelation, User = get_models()
        
        group = FundGroup.query.filter_by(
            id=group_id,
            user_id=current_user_id
        ).first()
        
        if not group:
            api.abort(404, '分组不存在或不属于当前用户')
        
        # 将分组内的基金移到默认分组（而不是删除）
        default_group = FundGroup.query.filter_by(
            user_id=current_user_id,
            is_default=True
        ).first()
        
        if default_group and default_group.id != group_id:
            favorites = FavoriteFundRelation.query.filter_by(
                group_id=group_id
            ).all()
            
            for favorite in favorites:
                favorite.group_id = default_group.id
        else:
            # 如果没有默认分组或正在清空默认分组，则逻辑删除
            favorites = FavoriteFundRelation.query.filter_by(
                group_id=group_id
            ).all()
            
            for favorite in favorites:
                favorite.is_deleted = True
                favorite.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'message': f'分组 "{group.group_name}" 已清空'}, 200