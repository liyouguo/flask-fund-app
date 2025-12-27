from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.fund import Fund, FundMarketData
from app.models.user import User, UserProfile
from app.models.transaction import Holding
from app.models.notification import Notification
from app import db
from datetime import datetime, timedelta
import random

api = Namespace('home', description='首页相关操作')

# 数据模型定义
# 资产概览模型
asset_overview_model = api.model('AssetOverview', {
    'total_assets': fields.Arbitrary(required=True, description='总资产'),
    'daily_pnl': fields.Arbitrary(required=True, description='当日盈亏'),
    'daily_pnl_rate': fields.Arbitrary(required=True, description='当日盈亏率'),
    'total_pnl': fields.Arbitrary(required=True, description='累计盈亏'),
    'total_pnl_rate': fields.Arbitrary(required=True, description='累计盈亏率'),
    'holdings_count': fields.Integer(required=True, description='持仓数量')
})

# 持仓概览模型
holding_summary_model = api.model('HoldingSummary', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'shares': fields.Arbitrary(description='持有份额'),
    'current_value': fields.Arbitrary(description='当前市值'),
    'daily_pnl': fields.Arbitrary(description='当日盈亏'),
    'daily_pnl_rate': fields.Arbitrary(description='当日盈亏率')
})

# 指数概览模型
index_summary_model = api.model('IndexSummary', {
    'index_code': fields.String(required=True, description='指数代码'),
    'index_name': fields.String(required=True, description='指数名称'),
    'current_point': fields.Arbitrary(required=True, description='当前点数'),
    'daily_change': fields.Arbitrary(required=True, description='日涨跌额'),
    'daily_change_rate': fields.Arbitrary(required=True, description='日涨跌幅')
})

# 基金推荐模型
fund_recommendation_model = api.model('FundRecommendation', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'fund_type': fields.String(description='基金类型'),
    'risk_level': fields.String(description='风险等级'),
    'net_value': fields.Arbitrary(description='最新净值'),
    'daily_change_rate': fields.Arbitrary(description='日涨跌幅'),
    'recommendation_reason': fields.String(description='推荐理由'),
    'performance_rank': fields.String(description='业绩排名')
})

# 首页快捷入口模型
quick_action_model = api.model('QuickAction', {
    'id': fields.String(required=True, description='快捷入口ID'),
    'name': fields.String(required=True, description='名称'),
    'icon': fields.String(description='图标'),
    'url': fields.String(required=True, description='跳转链接'),
    'order': fields.Integer(description='排序')
})

# 首页响应模型
home_response_model = api.model('HomeResponse', {
    'asset_overview': fields.Nested(asset_overview_model, description='资产概览'),
    'holdings_summary': fields.List(fields.Nested(holding_summary_model), description='持仓概览'),
    'index_summary': fields.List(fields.Nested(index_summary_model), description='指数概览'),
    'recommended_funds': fields.List(fields.Nested(fund_recommendation_model), description='推荐基金'),
    'quick_actions': fields.List(fields.Nested(quick_action_model), description='快捷入口'),
    'unread_notifications_count': fields.Integer(description='未读消息数量'),
    'update_time': fields.DateTime(description='更新时间')
})


@api.route('/overview')
class HomeOverview(Resource):
    @jwt_required()
    @api.doc('get_home_overview')
    @api.marshal_with(home_response_model)
    def get(self):
        """获取首页概览数据"""
        current_user_id = get_jwt_identity()
        
        # 获取用户信息
        user = User.query.get(current_user_id)
        if not user:
            api.abort(404, '用户不存在')
        
        # 获取资产概览
        asset_overview = self.get_asset_overview(current_user_id)
        
        # 获取持仓概览
        holdings_summary = self.get_holdings_summary(current_user_id)
        
        # 获取指数概览
        index_summary = self.get_index_summary()
        
        # 获取推荐基金
        recommended_funds = self.get_recommended_funds(current_user_id)
        
        # 获取快捷入口
        quick_actions = self.get_quick_actions()
        
        # 获取未读消息数量
        unread_notifications_count = self.get_unread_notifications_count(current_user_id)
        
        return {
            'asset_overview': asset_overview,
            'holdings_summary': holdings_summary,
            'index_summary': index_summary,
            'recommended_funds': recommended_funds,
            'quick_actions': quick_actions,
            'unread_notifications_count': unread_notifications_count,
            'update_time': datetime.utcnow()
        }
    
    def get_asset_overview(self, user_id):
        """获取资产概览"""
        # 获取用户所有持仓
        holdings = Holding.query.filter_by(user_id=user_id).all()
        
        total_assets = 0
        total_cost = 0
        daily_pnl = 0
        holdings_count = len(holdings)
        
        for holding in holdings:
            # 获取最新的市场数据
            market_data = FundMarketData.query.filter_by(
                fund_code=holding.fund_code
            ).order_by(FundMarketData.update_time.desc()).first()
            
            if market_data and market_data.net_value:
                current_value = float(holding.shares) * float(market_data.net_value)
                total_assets += current_value
                total_cost += float(holding.cost_basis)
                
                # 计算当日盈亏
                if holding.latest_net_value:
                    daily_change = float(market_data.net_value) - float(holding.latest_net_value)
                    daily_pnl += daily_change * float(holding.shares)
        
        total_pnl = total_assets - total_cost
        total_pnl_rate = 0
        if total_cost > 0:
            total_pnl_rate = (total_pnl / total_cost) * 100
        
        daily_pnl_rate = 0
        if total_assets > 0:
            daily_pnl_rate = (daily_pnl / total_assets) * 100
        
        return {
            'total_assets': total_assets,
            'daily_pnl': daily_pnl,
            'daily_pnl_rate': daily_pnl_rate,
            'total_pnl': total_pnl,
            'total_pnl_rate': total_pnl_rate,
            'holdings_count': holdings_count
        }
    
    def get_holdings_summary(self, user_id):
        """获取持仓概览"""
        holdings = Holding.query.filter_by(user_id=user_id).all()
        result = []
        
        for holding in holdings:
            # 获取基金信息
            fund = Fund.query.filter_by(fund_code=holding.fund_code).first()
            
            # 获取最新的市场数据
            market_data = FundMarketData.query.filter_by(
                fund_code=holding.fund_code
            ).order_by(FundMarketData.update_time.desc()).first()
            
            current_value = 0
            daily_pnl = 0
            daily_pnl_rate = 0
            
            if market_data and market_data.net_value:
                current_value = float(holding.shares) * float(market_data.net_value)
                
                # 计算当日盈亏
                if holding.latest_net_value:
                    daily_change = float(market_data.net_value) - float(holding.latest_net_value)
                    daily_pnl = daily_change * float(holding.shares)
                    if holding.latest_net_value > 0:
                        daily_pnl_rate = (daily_change / float(holding.latest_net_value)) * 100
            
            result.append({
                'fund_code': holding.fund_code,
                'fund_name': fund.fund_name if fund else '未知基金',
                'shares': holding.shares,
                'current_value': current_value,
                'daily_pnl': daily_pnl,
                'daily_pnl_rate': daily_pnl_rate
            })
        
        # 按当前市值排序，返回前5只
        result.sort(key=lambda x: x['current_value'], reverse=True)
        return result[:5]  # 只返回前5只持仓
    
    def get_index_summary(self):
        """获取指数概览"""
        # 这里应该从实际数据源获取指数数据
        # 为了示例，返回模拟数据
        indices = [
            {
                'index_code': '000001',
                'index_name': '上证指数',
                'current_point': round(random.uniform(2900, 3300), 2),
                'daily_change': round(random.uniform(-50, 50), 2),
                'daily_change_rate': round(random.uniform(-2, 2), 2)
            },
            {
                'index_code': '399001',
                'index_name': '深证成指',
                'current_point': round(random.uniform(9000, 11000), 2),
                'daily_change': round(random.uniform(-100, 100), 2),
                'daily_change_rate': round(random.uniform(-2, 2), 2)
            },
            {
                'index_code': '399006',
                'index_name': '创业板指',
                'current_point': round(random.uniform(2000, 2500), 2),
                'daily_change': round(random.uniform(-30, 30), 2),
                'daily_change_rate': round(random.uniform(-2, 2), 2)
            }
        ]
        
        return indices
    
    def get_recommended_funds(self, user_id):
        """获取推荐基金"""
        # 获取用户风险偏好
        user_profile = UserProfile.query.filter_by(user_id=user_id).first()
        risk_level = user_profile.risk_level if user_profile else 'R3'
        
        # 根据用户风险偏好推荐基金
        # 这里简化处理，实际应用中应该使用更复杂的推荐算法
        funds = Fund.query.join(FundMarketData).filter(
            Fund.risk_level == risk_level
        ).limit(5).all()
        
        recommendations = []
        for fund in funds:
            market_data = FundMarketData.query.filter_by(
                fund_code=fund.fund_code
            ).order_by(FundMarketData.update_time.desc()).first()
            
            if market_data:
                recommendations.append({
                    'fund_code': fund.fund_code,
                    'fund_name': fund.fund_name,
                    'fund_type': fund.fund_type,
                    'risk_level': fund.risk_level,
                    'net_value': float(market_data.net_value) if market_data.net_value else 0,
                    'daily_change_rate': float(market_data.daily_change_rate) if market_data.daily_change_rate else 0,
                    'recommendation_reason': f'符合您的风险偏好({risk_level})',
                    'performance_rank': f'同类第{random.randint(1, 20)}名'
                })
        
        # 如果推荐基金不足，补充其他基金
        if len(recommendations) < 5:
            additional_funds = Fund.query.join(FundMarketData).filter(
                ~Fund.fund_code.in_([r['fund_code'] for r in recommendations])
            ).limit(5 - len(recommendations)).all()
            
            for fund in additional_funds:
                market_data = FundMarketData.query.filter_by(
                    fund_code=fund.fund_code
                ).order_by(FundMarketData.update_time.desc()).first()
                
                if market_data:
                    recommendations.append({
                        'fund_code': fund.fund_code,
                        'fund_name': fund.fund_name,
                        'fund_type': fund.fund_type,
                        'risk_level': fund.risk_level,
                        'net_value': float(market_data.net_value) if market_data.net_value else 0,
                        'daily_change_rate': float(market_data.daily_change_rate) if market_data.daily_change_rate else 0,
                        'recommendation_reason': '热门推荐',
                        'performance_rank': f'同类第{random.randint(1, 50)}名'
                    })
        
        return recommendations
    
    def get_quick_actions(self):
        """获取快捷入口"""
        # 返回预定义的快捷入口
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
                'id': 'favorite',
                'name': '自选',
                'icon': 'favorite',
                'url': '/favorite',
                'order': 3
            },
            {
                'id': 'portfolio',
                'name': '持仓',
                'icon': 'portfolio',
                'url': '/portfolio',
                'order': 4
            },
            {
                'id': 'market',
                'name': '市场',
                'icon': 'market',
                'url': '/market',
                'order': 5
            }
        ]
        
        return quick_actions
    
    def get_unread_notifications_count(self, user_id):
        """获取未读消息数量"""
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return count