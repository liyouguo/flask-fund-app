from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.models.fund import Fund, FundMarketData
from app import db
from datetime import datetime, timedelta
import random

api = Namespace('market', description='市场行情相关操作')

# 数据模型定义
market_fund_model = api.model('MarketFund', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'fund_type': fields.String(description='基金类型'),
    'net_value': fields.Arbitrary(description='最新净值'),
    'daily_change': fields.Arbitrary(description='日涨跌额'),
    'daily_change_rate': fields.Arbitrary(description='日涨跌幅'),
    'update_time': fields.DateTime(description='更新时间')
})

sector_model = api.model('Sector', {
    'sector_code': fields.String(required=True, description='板块代码'),
    'sector_name': fields.String(required=True, description='板块名称'),
    'daily_change_rate': fields.Arbitrary(description='日涨跌幅'),
    'weekly_change_rate': fields.Arbitrary(description='周涨跌幅'),
    'monthly_change_rate': fields.Arbitrary(description='月涨跌幅'),
    'yearly_change_rate': fields.Arbitrary(description='年涨跌幅'),
    'hot_score': fields.Integer(description='热度评分'),
    'update_time': fields.DateTime(description='更新时间')
})

news_model = api.model('News', {
    'news_id': fields.String(required=True, description='资讯ID'),
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
    'current_point': fields.Arbitrary(description='当前点数'),
    'daily_change': fields.Arbitrary(description='日涨跌额'),
    'daily_change_rate': fields.Arbitrary(description='日涨跌幅'),
    'update_time': fields.DateTime(description='更新时间')
})

# 板块预测模型
sector_prediction_model = api.model('SectorPrediction', {
    'prediction_id': fields.String(required=True, description='预测ID'),
    'sector_code': fields.String(required=True, description='板块代码'),
    'sector_name': fields.String(required=True, description='板块名称'),
    'prediction_trend': fields.String(required=True, description='预测趋势'),
    'confidence_score': fields.Integer(required=True, description='置信度'),
    'prediction_basis': fields.String(required=True, description='预测依据'),
    'prediction_time': fields.DateTime(description='预测时间')
})


@api.route('/funds')
class MarketFunds(Resource):
    @api.doc('list_market_funds')
    @api.marshal_with(api.model('MarketFundsPagination', {
        'items': fields.List(fields.Nested(market_fund_model), description='基金列表'),
        'total': fields.Integer(description='总数'),
        'page': fields.Integer(description='当前页'),
        'pages': fields.Integer(description='总页数'),
        'per_page': fields.Integer(description='每页数量')
    }))
    def get(self):
        """获取市场基金列表"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        fund_type = request.args.get('type')
        
        # 查询基金基础信息和最新的市场数据
        query = db.session.query(Fund, FundMarketData).join(
            FundMarketData, Fund.fund_code == FundMarketData.fund_code
        )
        
        if fund_type:
            query = query.filter(Fund.fund_type == fund_type)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 组装返回数据
        items = []
        for fund, market_data in pagination.items:
            items.append({
                'fund_code': fund.fund_code,
                'fund_name': fund.fund_name,
                'fund_type': fund.fund_type,
                'net_value': float(market_data.net_value) if market_data.net_value else 0,
                'daily_change': float(market_data.daily_change) if market_data.daily_change else 0,
                'daily_change_rate': float(market_data.daily_change_rate) if market_data.daily_change_rate else 0,
                'update_time': market_data.update_time
            })
        
        return {
            'items': items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }


@api.route('/sectors')
class Sectors(Resource):
    @api.doc('list_sectors')
    @api.marshal_with(sector_model)
    def get(self):
        """获取热门板块"""
        # 这里应该查询板块数据
        # 为了示例，返回模拟数据
        sectors = [
            {
                'sector_code': 'C01',
                'sector_name': '科技板块',
                'daily_change_rate': round(random.uniform(-2, 5), 2),
                'weekly_change_rate': round(random.uniform(-5, 8), 2),
                'monthly_change_rate': round(random.uniform(-8, 12), 2),
                'yearly_change_rate': round(random.uniform(5, 25), 2),
                'hot_score': 95,
                'update_time': datetime.utcnow()
            },
            {
                'sector_code': 'C02',
                'sector_name': '消费板块',
                'daily_change_rate': round(random.uniform(-3, 3), 2),
                'weekly_change_rate': round(random.uniform(-4, 6), 2),
                'monthly_change_rate': round(random.uniform(-6, 10), 2),
                'yearly_change_rate': round(random.uniform(3, 20), 2),
                'hot_score': 85,
                'update_time': datetime.utcnow()
            },
            {
                'sector_code': 'C03',
                'sector_name': '医疗板块',
                'daily_change_rate': round(random.uniform(-1, 4), 2),
                'weekly_change_rate': round(random.uniform(-3, 7), 2),
                'monthly_change_rate': round(random.uniform(-5, 11), 2),
                'yearly_change_rate': round(random.uniform(8, 22), 2),
                'hot_score': 90,
                'update_time': datetime.utcnow()
            },
            {
                'sector_code': 'C04',
                'sector_name': '金融板块',
                'daily_change_rate': round(random.uniform(-2, 2), 2),
                'weekly_change_rate': round(random.uniform(-4, 5), 2),
                'monthly_change_rate': round(random.uniform(-6, 9), 2),
                'yearly_change_rate': round(random.uniform(2, 18), 2),
                'hot_score': 80,
                'update_time': datetime.utcnow()
            },
            {
                'sector_code': 'C05',
                'sector_name': '新能源板块',
                'daily_change_rate': round(random.uniform(-4, 6), 2),
                'weekly_change_rate': round(random.uniform(-7, 10), 2),
                'monthly_change_rate': round(random.uniform(-10, 15), 2),
                'yearly_change_rate': round(random.uniform(10, 30), 2),
                'hot_score': 92,
                'update_time': datetime.utcnow()
            }
        ]
        
        return sectors


@api.route('/news')
class News(Resource):
    @jwt_required(optional=True)  # 新闻可以不登录查看
    @api.doc('list_news')
    @api.marshal_with(news_model)
    def get(self):
        """获取市场资讯"""
        # 这里应该查询资讯数据
        # 为了示例，返回模拟数据
        news_list = [
            {
                'news_id': 'news_001',
                'title': '科技股今日大幅上涨',
                'source': '财经日报',
                'publish_time': datetime.utcnow() - timedelta(hours=2),
                'content_url': 'https://example.com/news/001',
                'thumbnail_url': 'https://example.com/thumbnails/001.jpg',
                'category': '市场动态',
                'is_read': False
            },
            {
                'news_id': 'news_002',
                'title': '央行发布最新货币政策',
                'source': '金融时报',
                'publish_time': datetime.utcnow() - timedelta(hours=5),
                'content_url': 'https://example.com/news/002',
                'thumbnail_url': 'https://example.com/thumbnails/002.jpg',
                'category': '政策解读',
                'is_read': False
            },
            {
                'news_id': 'news_003',
                'title': '新能源汽车销量创新高',
                'source': '行业观察',
                'publish_time': datetime.utcnow() - timedelta(hours=8),
                'content_url': 'https://example.com/news/003',
                'thumbnail_url': 'https://example.com/thumbnails/003.jpg',
                'category': '行业资讯',
                'is_read': False
            },
            {
                'news_id': 'news_004',
                'title': '基金公司三季度业绩出炉',
                'source': '基金周刊',
                'publish_time': datetime.utcnow() - timedelta(hours=12),
                'content_url': 'https://example.com/news/004',
                'thumbnail_url': 'https://example.com/thumbnails/004.jpg',
                'category': '基金动态',
                'is_read': False
            }
        ]
        
        return news_list


@api.route('/index')
class Index(Resource):
    @api.doc('list_index')
    @api.marshal_with(index_model)
    def get(self):
        """获取主要指数"""
        # 这里应该查询指数数据
        # 为了示例，返回模拟数据
        indexes = [
            {
                'index_code': '000001',
                'index_name': '上证指数',
                'current_point': round(random.uniform(2900, 3300), 2),
                'daily_change': round(random.uniform(-50, 50), 2),
                'daily_change_rate': round(random.uniform(-2, 2), 2),
                'update_time': datetime.utcnow()
            },
            {
                'index_code': '399001',
                'index_name': '深证成指',
                'current_point': round(random.uniform(9000, 11000), 2),
                'daily_change': round(random.uniform(-100, 100), 2),
                'daily_change_rate': round(random.uniform(-2, 2), 2),
                'update_time': datetime.utcnow()
            },
            {
                'index_code': '399006',
                'index_name': '创业板指',
                'current_point': round(random.uniform(2000, 2500), 2),
                'daily_change': round(random.uniform(-30, 30), 2),
                'daily_change_rate': round(random.uniform(-2, 2), 2),
                'update_time': datetime.utcnow()
            },
            {
                'index_code': '000300',
                'index_name': '沪深300',
                'current_point': round(random.uniform(3500, 4000), 2),
                'daily_change': round(random.uniform(-40, 40), 2),
                'daily_change_rate': round(random.uniform(-2, 2), 2),
                'update_time': datetime.utcnow()
            }
        ]
        
        return indexes


@api.route('/sectors/<string:sector_code>/prediction')
@api.param('sector_code', '板块代码')
class SectorPrediction(Resource):
    @api.doc('get_sector_prediction')
    @api.marshal_with(sector_prediction_model)
    def get(self, sector_code):
        """获取板块预测"""
        # 这里应该查询板块预测数据
        # 为了示例，返回模拟数据
        sector_names = {
            'C01': '科技板块',
            'C02': '消费板块',
            'C03': '医疗板块',
            'C04': '金融板块',
            'C05': '新能源板块'
        }
        
        sector_name = sector_names.get(sector_code, f'未知板块({sector_code})')
        
        trends = ['up', 'down', 'flat']
        trend = random.choice(trends)
        
        prediction = {
            'prediction_id': f'pred_{sector_code}_{datetime.utcnow().strftime("%Y%m%d")}',
            'sector_code': sector_code,
            'sector_name': sector_name,
            'prediction_trend': trend,
            'confidence_score': random.randint(60, 95),
            'prediction_basis': f'基于历史数据和市场趋势分析，{sector_name}未来一周可能{ "上涨" if trend == "up" else ("下跌" if trend == "down" else "横盘") }',
            'prediction_time': datetime.utcnow()
        }
        
        return prediction


@api.route('/funds/<string:fund_code>/analysis')
@api.param('fund_code', '基金代码')
class FundAnalysis(Resource):
    @api.doc('get_fund_analysis')
    def get(self, fund_code):
        """获取基金分析"""
        # 这里应该查询基金的详细分析数据
        # 为了示例，返回模拟数据
        fund = Fund.query.filter_by(fund_code=fund_code).first()
        if not fund:
            api.abort(404, '基金不存在')
        
        market_data = FundMarketData.query.filter_by(
            fund_code=fund_code
        ).order_by(FundMarketData.update_time.desc()).first()
        
        if not market_data:
            api.abort(404, '基金行情数据不存在')
        
        analysis = {
            'fund_code': fund_code,
            'fund_name': fund.fund_name,
            'current_net_value': float(market_data.net_value) if market_data.net_value else 0,
            'daily_change_rate': float(market_data.daily_change_rate) if market_data.daily_change_rate else 0,
            'weekly_trend': random.choice(['上升', '下降', '平稳']),
            'monthly_trend': random.choice(['上升', '下降', '平稳']),
            'risk_level': fund.risk_level or 'R3',
            'risk_analysis': f'该基金风险等级为{fund.risk_level or "R3"}，{random.choice(["适合稳健型投资者", "适合平衡型投资者", "适合积极型投资者"])}',
            'investment_advice': random.choice([
                '建议继续持有',
                '建议关注',
                '短期波动较大，谨慎操作',
                '长期看好，可考虑定投'
            ])
        }
        
        return analysis