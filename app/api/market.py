from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.fund import Fund, FundMarketData
from app.models.transaction import Holding, Transaction

api = Namespace('market', description='市场行情相关操作')

# 数据模型定义
market_fund_model = api.model('MarketFund', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'fund_type': fields.String(description='基金类型'),
    'net_value': fields.String(description='最新净值'),
    'daily_change': fields.String(description='日涨跌额'),
    'daily_change_rate': fields.String(description='日涨跌幅'),
    'update_time': fields.DateTime(description='更新时间')
})

sector_model = api.model('Sector', {
    'sector_code': fields.String(required=True, description='板块代码'),
    'sector_name': fields.String(required=True, description='板块名称'),
    'daily_change_rate': fields.String(description='日涨跌幅'),
    'weekly_change_rate': fields.String(description='周涨跌幅'),
    'monthly_change_rate': fields.String(description='月涨跌幅'),
    'yearly_change_rate': fields.String(description='年涨跌幅'),
    'hot_score': fields.Integer(description='热门度'),
    'update_time': fields.DateTime(description='更新时间')
})

news_model = api.model('News', {
    'news_id': fields.String(required=True, description='新闻ID'),
    'title': fields.String(required=True, description='标题'),
    'source': fields.String(description='来源'),
    'publish_time': fields.DateTime(description='发布时间'),
    'content_url': fields.String(description='内容链接'),
    'thumbnail_url': fields.String(description='缩略图链接'),
    'category': fields.String(description='分类'),
    'is_read': fields.Boolean(description='是否已读')
})

index_model = api.model('Index', {
    'index_code': fields.String(required=True, description='指数代码'),
    'index_name': fields.String(required=True, description='指数名称'),
    'current_point': fields.String(description='当前点数'),
    'daily_change': fields.String(description='日涨跌'),
    'daily_change_rate': fields.String(description='日涨跌幅'),
    'update_time': fields.DateTime(description='更新时间')
})

prediction_model = api.model('Prediction', {
    'prediction_id': fields.String(required=True, description='预测ID'),
    'sector_code': fields.String(required=True, description='板块代码'),
    'sector_name': fields.String(required=True, description='板块名称'),
    'prediction_trend': fields.String(required=True, description='预测趋势'),
    'confidence_score': fields.Integer(description='可信度'),
    'prediction_basis': fields.String(description='预测依据'),
    'prediction_time': fields.DateTime(description='预测时间')
})

market_fund_list_model = api.model('MarketFundList', {
    'items': fields.List(fields.Nested(market_fund_model)),
    'total': fields.Integer,
    'page': fields.Integer,
    'pages': fields.Integer,
    'per_page': fields.Integer
})

sector_list_model = api.model('SectorList', {
    'items': fields.List(fields.Nested(sector_model))
})

news_list_model = api.model('NewsList', {
    'items': fields.List(fields.Nested(news_model))
})

index_list_model = api.model('IndexList', {
    'items': fields.List(fields.Nested(index_model))
})

@api.route('/funds')
class MarketFundList(Resource):
    @api.doc('list_market_funds')
    @api.marshal_with(market_fund_list_model)
    def get(self):
        """获取市场基金列表"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        fund_type = request.args.get('type')
        
        # 查询基金和对应的最新市场数据
        query = db.session.query(Fund, FundMarketData).join(
            FundMarketData, Fund.fund_code == FundMarketData.fund_code
        ).order_by(FundMarketData.daily_change_rate.desc())
        
        if fund_type:
            query = query.filter(Fund.fund_type == fund_type)
        
        result = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for fund, market_data in result.items:
            item = {
                'fund_code': fund.fund_code,
                'fund_name': fund.fund_name,
                'fund_type': fund.fund_type,
                'net_value': str(market_data.net_value) if market_data.net_value else None,
                'daily_change': str(market_data.daily_change) if market_data.daily_change else None,
                'daily_change_rate': str(market_data.daily_change_rate) if market_data.daily_change_rate else None,
                'update_time': market_data.update_time
            }
            items.append(item)
        
        return {
            'items': items,
            'total': result.total,
            'page': result.page,
            'pages': result.pages,
            'per_page': result.per_page
        }

@api.route('/sectors')
class SectorList(Resource):
    @api.doc('list_sectors')
    @api.marshal_with(sector_list_model)
    def get(self):
        """获取热门板块"""
        # 模拟热门板块数据
        sectors = [
            {
                'sector_code': 'C01',
                'sector_name': '科技板块',
                'daily_change_rate': '2.50',
                'weekly_change_rate': '3.20',
                'monthly_change_rate': '5.60',
                'yearly_change_rate': '15.80',
                'hot_score': 95,
                'update_time': '2023-10-01T10:00:00Z'
            },
            {
                'sector_code': 'C02',
                'sector_name': '消费板块',
                'daily_change_rate': '1.20',
                'weekly_change_rate': '0.80',
                'monthly_change_rate': '2.10',
                'yearly_change_rate': '8.50',
                'hot_score': 85,
                'update_time': '2023-10-01T10:00:00Z'
            },
            {
                'sector_code': 'C03',
                'sector_name': '医药板块',
                'daily_change_rate': '-0.50',
                'weekly_change_rate': '1.20',
                'monthly_change_rate': '-1.80',
                'yearly_change_rate': '5.20',
                'hot_score': 78,
                'update_time': '2023-10-01T10:00:00Z'
            }
        ]
        
        return {'items': sectors}

@api.route('/news')
class NewsList(Resource):
    @api.doc('list_news')
    @api.marshal_with(news_list_model)
    def get(self):
        """获取市场资讯"""
        # 模拟市场资讯数据
        news = [
            {
                'news_id': 'news_001',
                'title': '科技股今日大幅上涨',
                'source': '财经日报',
                'publish_time': '2023-10-01T08:00:00Z',
                'content_url': 'https://example.com/news/001',
                'thumbnail_url': 'https://example.com/thumbnails/001.jpg',
                'category': '市场动态',
                'is_read': False
            },
            {
                'news_id': 'news_002',
                'title': '央行发布最新货币政策',
                'source': '金融时报',
                'publish_time': '2023-09-30T16:30:00Z',
                'content_url': 'https://example.com/news/002',
                'thumbnail_url': 'https://example.com/thumbnails/002.jpg',
                'category': '政策解读',
                'is_read': True
            }
        ]
        
        return {'items': news}

@api.route('/index')
class IndexList(Resource):
    @api.doc('list_index')
    @api.marshal_with(index_list_model)
    def get(self):
        """获取主要指数"""
        # 模拟主要指数数据
        indices = [
            {
                'index_code': '000001',
                'index_name': '上证指数',
                'current_point': '3250.12',
                'daily_change': '15.23',
                'daily_change_rate': '0.47',
                'update_time': '2023-10-01T10:00:00Z'
            },
            {
                'index_code': '399001',
                'index_name': '深证成指',
                'current_point': '11023.56',
                'daily_change': '45.67',
                'daily_change_rate': '0.42',
                'update_time': '2023-10-01T10:00:00Z'
            },
            {
                'index_code': '399006',
                'index_name': '创业板指',
                'current_point': '2245.78',
                'daily_change': '12.34',
                'daily_change_rate': '0.55',
                'update_time': '2023-10-01T10:00:00Z'
            }
        ]
        
        return {'items': indices}

@api.route('/sectors/<string:sector_code>/prediction')
@api.param('sector_code', '板块代码')
class SectorPrediction(Resource):
    @api.doc('get_sector_prediction')
    @api.marshal_with(prediction_model)
    def get(self, sector_code):
        """获取板块预测"""
        # 模拟板块预测数据
        prediction = {
            'prediction_id': f'pred_{sector_code}_20231001',
            'sector_code': sector_code,
            'sector_name': '科技板块' if sector_code == 'C01' else '未知板块',
            'prediction_trend': 'up',
            'confidence_score': 85,
            'prediction_basis': '基于历史数据和市场趋势分析，科技板块未来一周可能上涨',
            'prediction_time': '2023-10-01T10:00:00Z'
        }
        
        return prediction

@api.route('/funds/<string:fund_code>/analysis')
@api.param('fund_code', '基金代码')
class FundAnalysis(Resource):
    @api.doc('get_fund_analysis')
    def get(self, fund_code):
        """获取基金分析"""
        fund = Fund.query.filter_by(fund_code=fund_code).first_or_404()
        market_data = FundMarketData.query.filter_by(fund_code=fund_code).order_by(FundMarketData.update_time.desc()).first()
        
        if not market_data:
            api.abort(404, '基金市场数据不存在')
        
        analysis = {
            'fund_code': fund.fund_code,
            'fund_name': fund.fund_name,
            'current_net_value': str(market_data.net_value),
            'daily_change_rate': str(market_data.daily_change_rate),
            'weekly_trend': '上升' if market_data.weekly_change_rate and float(market_data.weekly_change_rate) > 0 else '下降',
            'monthly_trend': '平稳' if abs(float(market_data.monthly_change_rate or 0)) < 2 else ('上升' if float(market_data.monthly_change_rate or 0) > 0 else '下降'),
            'risk_level': fund.risk_level,
            'risk_analysis': f'该基金风险等级为{fund.risk_level}，适合平衡型投资者',
            'investment_advice': '建议继续持有'
        }
        
        return analysis