from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.fund import Fund, FundMarketData
from app.models.user import User
from app import db
from sqlalchemy import or_
from datetime import datetime, timedelta

api = Namespace('funds', description='基金相关操作')

# 数据模型定义
fund_model = api.model('Fund', {
    'id': fields.String(required=True, description='基金ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'fund_type': fields.String(description='基金类型'),
    'risk_level': fields.String(description='风险等级'),
    'company': fields.String(description='基金公司'),
    'net_asset_value': fields.Arbitrary(description='基金规模'),
    'management_fee': fields.Arbitrary(description='管理费率'),
    'custody_fee': fields.Arbitrary(description='托管费率'),
    'establishment_date': fields.Date(description='成立日期')
})

fund_market_data_model = api.model('FundMarketData', {
    'id': fields.String(required=True, description='数据ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'net_value': fields.Arbitrary(description='最新净值'),
    'daily_change': fields.Arbitrary(description='日涨跌额'),
    'daily_change_rate': fields.Arbitrary(description='日涨跌幅'),
    'weekly_change_rate': fields.Arbitrary(description='周涨跌幅'),
    'monthly_change_rate': fields.Arbitrary(description='月涨跌幅'),
    'quarterly_change_rate': fields.Arbitrary(description='季度涨跌幅'),
    'yearly_change_rate': fields.Arbitrary(description='年涨跌幅'),
    'three_year_change_rate': fields.Arbitrary(description='三年涨跌幅'),
    'update_time': fields.DateTime(description='更新时间')
})

fund_detail_model = api.inherit('FundDetail', fund_model, {
    'market_data': fields.Nested(fund_market_data_model, description='市场数据')
})

funds_pagination_model = api.model('FundsPagination', {
    'items': fields.List(fields.Nested(fund_model), description='基金列表'),
    'total': fields.Integer(description='总数'),
    'page': fields.Integer(description='当前页'),
    'pages': fields.Integer(description='总页数'),
    'per_page': fields.Integer(description='每页数量'),
    'has_next': fields.Boolean(description='是否有下一页'),
    'has_prev': fields.Boolean(description='是否有上一页')
})

# 基金历史净值数据模型
fund_history_model = api.model('FundHistory', {
    'date': fields.Date(required=True, description='净值日期'),
    'net_value': fields.Arbitrary(required=True, description='单位净值'),
    'daily_change': fields.Arbitrary(description='日涨跌额'),
    'daily_change_rate': fields.Arbitrary(description='日涨跌幅')
})

fund_history_response_model = api.model('FundHistoryResponse', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'history': fields.List(fields.Nested(fund_history_model), description='历史净值列表'),
    'time_range': fields.String(required=True, description='时间范围')
})


@api.route('/')
class FundList(Resource):
    @api.doc('list_funds')
    @api.marshal_with(funds_pagination_model)
    def get(self):
        """获取基金列表（支持分页、筛选）"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        fund_type = request.args.get('type')
        search = request.args.get('search')
        
        query = Fund.query
        
        if fund_type:
            query = query.filter(Fund.fund_type == fund_type)
        
        if search:
            query = query.filter(
                or_(
                    Fund.fund_name.contains(search),
                    Fund.fund_code.contains(search)
                )
            )
        
        pagination = query.paginate(
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


@api.route('/<string:fund_code>')
@api.param('fund_code', '基金代码')
class FundDetail(Resource):
    @api.doc('get_fund')
    @api.marshal_with(fund_detail_model)
    def get(self, fund_code):
        """获取基金详情"""
        fund = Fund.query.filter_by(fund_code=fund_code).first()
        
        if not fund:
            api.abort(404, '基金不存在')
        
        # 获取最新的市场数据
        market_data = FundMarketData.query.filter_by(
            fund_code=fund_code
        ).order_by(FundMarketData.update_time.desc()).first()
        
        # 创建一个包含基金和市场数据的字典返回
        result = fund.__dict__.copy()
        result['market_data'] = market_data
        return result


@api.route('/<string:fund_code>/history')
@api.param('fund_code', '基金代码')
class FundHistory(Resource):
    @api.doc('get_fund_history')
    @api.marshal_with(fund_history_response_model)
    def get(self, fund_code):
        """获取基金历史净值"""
        # 验证基金是否存在
        fund = Fund.query.filter_by(fund_code=fund_code).first()
        if not fund:
            api.abort(404, '基金不存在')
        
        # 获取时间参数，默认获取最近30天的数据
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 查询历史数据
        history_data = FundMarketData.query.filter(
            FundMarketData.fund_code == fund_code,
            FundMarketData.update_time >= start_date,
            FundMarketData.update_time <= end_date
        ).order_by(FundMarketData.update_time.desc()).all()
        
        # 转换为所需格式
        history = []
        for data in history_data:
            history.append({
                'date': data.update_time.strftime('%Y-%m-%d'),
                'net_value': float(data.net_value) if data.net_value else None,
                'daily_change': float(data.daily_change) if data.daily_change else None,
                'daily_change_rate': float(data.daily_change_rate) if data.daily_change_rate else None
            })
        
        return {
            'fund_code': fund_code,
            'history': history,
            'time_range': f'最近{days}天'
        }


@api.route('/search')
class FundSearch(Resource):
    @api.doc('search_funds')
    @api.marshal_with(funds_pagination_model)
    def get(self):
        """搜索基金"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        q = request.args.get('q', '')
        
        if not q:
            api.abort(400, '搜索关键词不能为空')
        
        query = Fund.query.filter(
            or_(
                Fund.fund_name.contains(q),
                Fund.fund_code.contains(q)
            )
        )
        
        pagination = query.paginate(
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


# 添加基金数据导入功能
@api.route('/import')
class FundDataImport(Resource):
    @jwt_required()
    def post(self):
        """导入基金数据（管理功能）"""
        # 这里可以实现从文件或API导入基金数据的功能
        # 为了示例，我们只返回一个成功消息
        current_user_id = get_jwt_identity()
        
        # 验证用户权限（只有管理员才能导入数据）
        user = User.query.get(current_user_id)
        if not user or user.email != 'admin@example.com':
            api.abort(403, '权限不足')
        
        # 这里可以实现实际的数据导入逻辑
        data = request.get_json()
        if not data or 'funds' not in data:
            api.abort(400, '缺少基金数据')
        
        # 导入基金数据的逻辑
        imported_count = 0
        for fund_data in data['funds']:
            # 检查基金是否已存在
            existing_fund = Fund.query.filter_by(fund_code=fund_data['fund_code']).first()
            
            if existing_fund:
                # 更新现有基金信息
                for attr, value in fund_data.items():
                    if hasattr(existing_fund, attr):
                        setattr(existing_fund, attr, value)
            else:
                # 创建新基金
                new_fund = Fund(**fund_data)
                db.session.add(new_fund)
            
            imported_count += 1
        
        db.session.commit()
        
        return {
            'message': f'成功导入 {imported_count} 只基金',
            'imported_count': imported_count
        }