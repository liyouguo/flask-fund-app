from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.fund import Fund, FundMarketData, FundGroup, FavoriteFundRelation

api = Namespace('funds', description='基金数据相关操作')

# 数据模型定义
fund_model = api.model('Fund', {
    'id': fields.String(required=True, description='基金ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'fund_type': fields.String(description='基金类型'),
    'risk_level': fields.String(description='风险等级'),
    'company': fields.String(description='基金公司'),
    'net_asset_value': fields.String(description='基金规模'),
    'management_fee': fields.String(description='管理费率'),
    'custody_fee': fields.String(description='托管费率')
})

fund_detail_model = api.model('FundDetail', {
    'id': fields.String(required=True, description='基金ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'fund_type': fields.String(description='基金类型'),
    'risk_level': fields.String(description='风险等级'),
    'company': fields.String(description='基金公司'),
    'net_asset_value': fields.String(description='基金规模'),
    'management_fee': fields.String(description='管理费率'),
    'custody_fee': fields.String(description='托管费率'),
    'market_data': fields.Raw(description='市场数据')
})

fund_list_model = api.model('FundList', {
    'items': fields.List(fields.Nested(fund_model)),
    'total': fields.Integer,
    'page': fields.Integer,
    'pages': fields.Integer,
    'per_page': fields.Integer,
    'has_next': fields.Boolean,
    'has_prev': fields.Boolean
})

@api.route('/')
class FundList(Resource):
    @api.doc('list_funds')
    @api.marshal_with(fund_list_model)
    def get(self):
        """获取基金列表（支持分页和筛选）"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        fund_type = request.args.get('type')
        search = request.args.get('search')
        
        query = Fund.query
        
        if fund_type:
            query = query.filter(Fund.fund_type == fund_type)
        
        if search:
            query = query.filter(Fund.fund_name.contains(search) | Fund.fund_code.contains(search))
        
        funds = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = {
            'items': [],
            'total': funds.total,
            'page': funds.page,
            'pages': funds.pages,
            'per_page': funds.per_page,
            'has_next': funds.has_next,
            'has_prev': funds.has_prev
        }
        
        for fund in funds.items:
            fund_data = {
                'id': fund.id,
                'fund_code': fund.fund_code,
                'fund_name': fund.fund_name,
                'fund_type': fund.fund_type,
                'risk_level': fund.risk_level,
                'company': fund.company,
                'net_asset_value': str(fund.net_asset_value) if fund.net_asset_value else None,
                'management_fee': str(fund.management_fee) if fund.management_fee else None,
                'custody_fee': str(fund.custody_fee) if fund.custody_fee else None
            }
            result['items'].append(fund_data)
        
        return result

@api.route('/<string:fund_code>')
@api.param('fund_code', '基金代码')
class FundDetail(Resource):
    @api.doc('get_fund')
    @api.marshal_with(fund_detail_model)
    def get(self, fund_code):
        """获取单个基金的详细信息"""
        fund = Fund.query.filter_by(fund_code=fund_code).first_or_404()
        
        # 获取最新的市场数据
        market_data = FundMarketData.query.filter_by(fund_code=fund_code).order_by(FundMarketData.update_time.desc()).first()
        
        result = {
            'id': fund.id,
            'fund_code': fund.fund_code,
            'fund_name': fund.fund_name,
            'fund_type': fund.fund_type,
            'risk_level': fund.risk_level,
            'company': fund.company,
            'net_asset_value': str(fund.net_asset_value) if fund.net_asset_value else None,
            'management_fee': str(fund.management_fee) if fund.management_fee else None,
            'custody_fee': str(fund.custody_fee) if fund.custody_fee else None,
            'market_data': {
                'id': market_data.id if market_data else None,
                'fund_code': market_data.fund_code if market_data else None,
                'net_value': str(market_data.net_value) if market_data else None,
                'daily_change': str(market_data.daily_change) if market_data else None,
                'daily_change_rate': str(market_data.daily_change_rate) if market_data else None,
                'weekly_change_rate': str(market_data.weekly_change_rate) if market_data else None,
                'monthly_change_rate': str(market_data.monthly_change_rate) if market_data else None,
                'quarterly_change_rate': str(market_data.quarterly_change_rate) if market_data else None,
                'yearly_change_rate': str(market_data.yearly_change_rate) if market_data else None,
                'three_year_change_rate': str(market_data.three_year_change_rate) if market_data else None,
                'update_time': market_data.update_time.isoformat() if market_data else None
            } if market_data else None
        }
        
        return result

@api.route('/search')
class FundSearch(Resource):
    @api.doc('search_funds')
    @api.marshal_with(fund_list_model)
    def get(self):
        """搜索基金"""
        q = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        if not q:
            api.abort(400, '搜索关键词不能为空')
        
        funds = Fund.query.filter(
            Fund.fund_name.contains(q) | Fund.fund_code.contains(q)
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        result = {
            'items': [],
            'total': funds.total,
            'page': funds.page,
            'pages': funds.pages,
            'per_page': funds.per_page,
            'has_next': funds.has_next,
            'has_prev': funds.has_prev
        }
        
        for fund in funds.items:
            fund_data = {
                'id': fund.id,
                'fund_code': fund.fund_code,
                'fund_name': fund.fund_name,
                'fund_type': fund.fund_type,
                'risk_level': fund.risk_level,
                'company': fund.company,
                'net_asset_value': str(fund.net_asset_value) if fund.net_asset_value else None,
                'management_fee': str(fund.management_fee) if fund.management_fee else None,
                'custody_fee': str(fund.custody_fee) if fund.custody_fee else None
            }
            result['items'].append(fund_data)
        
        return result

@api.route('/<string:fund_code>/history')
@api.param('fund_code', '基金代码')
class FundHistory(Resource):
    @api.doc('get_fund_history')
    def get(self, fund_code):
        """获取基金历史净值数据"""
        days = request.args.get('days', 30, type=int)
        
        # 这里简化处理，实际应用中需要查询历史净值数据表
        # 暂时返回模拟数据
        history_data = {
            'fund_code': fund_code,
            'history': [
                {
                    'date': '2023-10-01',
                    'net_value': '2.3567',
                    'daily_change': '0.035',
                    'daily_change_rate': '0.015'
                }
            ],
            'time_range': f'最近{days}天'
        }
        
        return history_data