from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserProfile
from app.models.transaction import Holding, Transaction
from app.models.fund import Fund, FundMarketData, FavoriteFundRelation
from app.models.notification import Notification

api = Namespace('home', description='首页相关操作')

# 数据模型定义
asset_overview_model = api.model('AssetOverview', {
    'total_assets': fields.String(required=True, description='总资产'),
    'daily_pnl': fields.String(required=True, description='当日盈亏'),
    'daily_pnl_rate': fields.String(required=True, description='当日盈亏率'),
    'total_pnl': fields.String(required=True, description='累计盈亏'),
    'total_pnl_rate': fields.String(required=True, description='累计盈亏率'),
    'holdings_count': fields.Integer(required=True, description='持仓数量')
})

holding_summary_model = api.model('HoldingSummary', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'shares': fields.String(required=True, description='持有份额'),
    'current_value': fields.String(required=True, description='当前市值'),
    'daily_pnl': fields.String(required=True, description='当日盈亏'),
    'daily_pnl_rate': fields.String(required=True, description='当日盈亏率')
})

index_summary_model = api.model('IndexSummary', {
    'index_code': fields.String(required=True, description='指数代码'),
    'index_name': fields.String(required=True, description='指数名称'),
    'current_point': fields.String(required=True, description='当前点数'),
    'daily_change': fields.String(required=True, description='日涨跌'),
    'daily_change_rate': fields.String(required=True, description='日涨跌幅')
})

recommended_fund_model = api.model('RecommendedFund', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'fund_type': fields.String(required=True, description='基金类型'),
    'risk_level': fields.String(required=True, description='风险等级'),
    'net_value': fields.String(required=True, description='净值'),
    'daily_change_rate': fields.String(required=True, description='日涨跌幅'),
    'recommendation_reason': fields.String(required=True, description='推荐理由'),
    'performance_rank': fields.String(required=True, description='业绩排名')
})

quick_action_model = api.model('QuickAction', {
    'id': fields.String(required=True, description='操作ID'),
    'name': fields.String(required=True, description='操作名称'),
    'icon': fields.String(required=True, description='图标'),
    'url': fields.String(required=True, description='链接地址'),
    'order': fields.Integer(required=True, description='排序')
})

home_overview_model = api.model('HomeOverview', {
    'asset_overview': fields.Nested(asset_overview_model, required=True, description='资产概览'),
    'holdings_summary': fields.List(fields.Nested(holding_summary_model), required=True, description='持仓概览'),
    'index_summary': fields.List(fields.Nested(index_summary_model), required=True, description='指数概览'),
    'recommended_funds': fields.List(fields.Nested(recommended_fund_model), required=True, description='推荐基金'),
    'quick_actions': fields.List(fields.Nested(quick_action_model), required=True, description='快捷操作'),
    'unread_notifications_count': fields.Integer(required=True, description='未读消息数量'),
    'update_time': fields.DateTime(required=True, description='更新时间')
})

@api.route('/overview')
class HomeOverview(Resource):
    @api.doc('get_home_overview')
    @jwt_required()
    @api.marshal_with(home_overview_model)
    def get(self):
        """获取首页概览数据"""
        current_user_id = get_jwt_identity()
        
        # 获取用户资产概览
        holdings = Holding.query.filter_by(user_id=current_user_id).all()
        
        total_assets = 0
        daily_pnl = 0
        total_pnl = 0
        
        for holding in holdings:
            total_assets += holding.current_value or 0
            daily_pnl += holding.daily_pnl or 0
            total_pnl += holding.total_pnl or 0
        
        daily_pnl_rate = (daily_pnl / (total_assets - daily_pnl) * 100) if (total_assets - daily_pnl) != 0 else 0
        total_pnl_rate = (total_pnl / (total_assets - total_pnl) * 100) if (total_assets - total_pnl) != 0 else 0
        
        asset_overview = {
            'total_assets': str(total_assets),
            'daily_pnl': str(daily_pnl),
            'daily_pnl_rate': str(round(daily_pnl_rate, 2)),
            'total_pnl': str(total_pnl),
            'total_pnl_rate': str(round(total_pnl_rate, 2)),
            'holdings_count': len(holdings)
        }
        
        # 获取持仓概览
        holdings_summary = []
        for holding in holdings:
            fund = Fund.query.filter_by(fund_code=holding.fund_code).first()
            if fund:
                holding_summary = {
                    'fund_code': holding.fund_code,
                    'fund_name': fund.fund_name,
                    'shares': str(holding.shares),
                    'current_value': str(holding.current_value),
                    'daily_pnl': str(holding.daily_pnl),
                    'daily_pnl_rate': str(holding.daily_pnl_rate)
                }
                holdings_summary.append(holding_summary)
        
        # 获取指数概览（模拟数据）
        index_summary = [
            {
                'index_code': '000001',
                'index_name': '上证指数',
                'current_point': '3250.12',
                'daily_change': '15.23',
                'daily_change_rate': '0.47'
            },
            {
                'index_code': '399001',
                'index_name': '深证成指',
                'current_point': '11023.56',
                'daily_change': '45.67',
                'daily_change_rate': '0.42'
            }
        ]
        
        # 获取推荐基金（基于用户持仓和风险偏好）
        recommended_funds = []
        
        # 获取用户的风险等级
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        user_risk_level = user_profile.risk_level if user_profile else 'R3'
        
        # 获取最近有更新的基金
        recent_funds = FundMarketData.query.order_by(FundMarketData.update_time.desc()).limit(5).all()
        
        for market_data in recent_funds:
            fund = Fund.query.filter_by(fund_code=market_data.fund_code).first()
            if fund and fund.risk_level == user_risk_level:
                recommended_fund = {
                    'fund_code': fund.fund_code,
                    'fund_name': fund.fund_name,
                    'fund_type': fund.fund_type,
                    'risk_level': fund.risk_level,
                    'net_value': str(market_data.net_value) if market_data.net_value else '0.0000',
                    'daily_change_rate': str(market_data.daily_change_rate) if market_data.daily_change_rate else '0.00',
                    'recommendation_reason': f'符合您的风险偏好({user_risk_level})',
                    'performance_rank': '同类第5名'
                }
                recommended_funds.append(recommended_fund)
        
        # 快捷操作
        quick_actions = [
            {
                'id': 'trade_buy',
                'name': '买入',
                'icon': 'buy',
                'url': '/trade/buy',
                'order': 1
            },
            {
                'id': 'trade_sell',
                'name': '卖出',
                'icon': 'sell',
                'url': '/trade/sell',
                'order': 2
            },
            {
                'id': 'add_favorite',
                'name': '自选',
                'icon': 'favorite',
                'url': '/favorites',
                'order': 3
            }
        ]
        
        # 未读消息数量
        unread_notifications_count = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).count()
        
        result = {
            'asset_overview': asset_overview,
            'holdings_summary': holdings_summary,
            'index_summary': index_summary,
            'recommended_funds': recommended_funds,
            'quick_actions': quick_actions,
            'unread_notifications_count': unread_notifications_count,
            'update_time': '2023-10-01T10:00:00Z'
        }
        
        return result