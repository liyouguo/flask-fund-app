from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.transaction import Holding, Transaction
from app.models.fund import Fund, FundMarketData
from app.models.user import User
from app import db
from datetime import datetime, timedelta
import random

api = Namespace('transactions', description='交易功能相关操作')

# 数据模型定义
holding_model = api.model('Holding', {
    'id': fields.String(required=True, description='持仓ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'shares': fields.Arbitrary(description='持有份额'),
    'cost_basis': fields.Arbitrary(description='成本基础'),
    'current_value': fields.Arbitrary(description='当前市值'),
    'daily_pnl': fields.Arbitrary(description='当日盈亏'),
    'daily_pnl_rate': fields.Arbitrary(description='当日盈亏率'),
    'total_pnl': fields.Arbitrary(description='累计盈亏'),
    'total_pnl_rate': fields.Arbitrary(description='累计盈亏率'),
    'latest_net_value': fields.Arbitrary(description='最新净值')
})

transaction_model = api.model('Transaction', {
    'id': fields.String(required=True, description='交易ID'),
    'order_id': fields.String(required=True, description='订单号'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'transaction_type': fields.String(required=True, description='交易类型'),
    'transaction_amount': fields.Arbitrary(description='交易金额'),
    'transaction_shares': fields.Arbitrary(description='交易份额'),
    'transaction_price': fields.Arbitrary(description='交易价格'),
    'fee': fields.Arbitrary(description='手续费'),
    'transaction_status': fields.String(required=True, description='交易状态'),
    'transaction_time': fields.DateTime(description='交易时间'),
    'confirmed_time': fields.DateTime(description='确认时间')
})

buy_request_model = api.model('BuyRequest', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'amount': fields.Arbitrary(required=True, description='购买金额')
})

sell_request_model = api.model('SellRequest', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'shares': fields.Arbitrary(required=True, description='卖出份额')
})

# 定投计划模型
recurring_investment_model = api.model('RecurringInvestment', {
    'id': fields.String(required=True, description='定投计划ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'amount': fields.Arbitrary(required=True, description='定投金额'),
    'frequency': fields.String(required=True, description='定投频率'),
    'start_date': fields.Date(required=True, description='开始日期'),
    'end_date': fields.Date(description='结束日期'),
    'is_active': fields.Boolean(required=True, description='是否激活'),
    'next_investment_date': fields.Date(description='下次定投日期')
})

# 资产概览模型
portfolio_overview_model = api.model('PortfolioOverview', {
    'total_assets': fields.Arbitrary(required=True, description='总资产'),
    'daily_pnl': fields.Arbitrary(required=True, description='当日盈亏'),
    'daily_pnl_rate': fields.Arbitrary(required=True, description='当日盈亏率'),
    'total_pnl': fields.Arbitrary(required=True, description='累计盈亏'),
    'total_pnl_rate': fields.Arbitrary(required=True, description='累计盈亏率'),
    'holdings_count': fields.Integer(required=True, description='持仓数量')
})


@api.route('/holdings')
class Holdings(Resource):
    @jwt_required()
    @api.doc('list_holdings')
    @api.marshal_with(holding_model)
    def get(self):
        """获取持仓列表"""
        current_user_id = get_jwt_identity()
        
        # 查询用户的持仓信息
        holdings = Holding.query.filter_by(user_id=current_user_id).all()
        
        result = []
        for holding in holdings:
            # 获取基金信息
            fund = Fund.query.filter_by(fund_code=holding.fund_code).first()
            
            # 获取最新的市场数据来计算当前市值和盈亏
            market_data = FundMarketData.query.filter_by(
                fund_code=holding.fund_code
            ).order_by(FundMarketData.update_time.desc()).first()
            
            # 计算当前市值
            current_value = 0
            latest_net_value = 0
            if market_data and market_data.net_value:
                latest_net_value = float(market_data.net_value)
                current_value = float(holding.shares) * latest_net_value
            
            # 计算盈亏
            total_cost = float(holding.cost_basis)
            total_pnl = current_value - total_cost
            total_pnl_rate = 0
            if total_cost > 0:
                total_pnl_rate = (total_pnl / total_cost) * 100
            
            # 计算当日盈亏（这里简化处理，实际应用中需要比较今日和昨日净值）
            daily_pnl = 0
            daily_pnl_rate = 0
            if holding.latest_net_value and latest_net_value:
                daily_change = latest_net_value - float(holding.latest_net_value)
                daily_pnl = daily_change * float(holding.shares)
                if holding.latest_net_value > 0:
                    daily_pnl_rate = (daily_change / float(holding.latest_net_value)) * 100
            
            result.append({
                'id': holding.id,
                'fund_code': holding.fund_code,
                'fund_name': fund.fund_name if fund else '未知基金',
                'shares': holding.shares,
                'cost_basis': holding.cost_basis,
                'current_value': current_value,
                'daily_pnl': daily_pnl,
                'daily_pnl_rate': daily_pnl_rate,
                'total_pnl': total_pnl,
                'total_pnl_rate': total_pnl_rate,
                'latest_net_value': latest_net_value
            })
        
        return result


@api.route('/holdings/<string:fund_code>')
@api.param('fund_code', '基金代码')
class HoldingDetail(Resource):
    @jwt_required()
    @api.doc('get_holding_detail')
    @api.marshal_with(holding_model)
    def get(self, fund_code):
        """获取单只基金持仓详情"""
        current_user_id = get_jwt_identity()
        
        holding = Holding.query.filter_by(
            user_id=current_user_id,
            fund_code=fund_code
        ).first()
        
        if not holding:
            api.abort(404, '持仓不存在')
        
        # 获取基金信息
        fund = Fund.query.filter_by(fund_code=holding.fund_code).first()
        
        # 获取最新的市场数据来计算当前市值和盈亏
        market_data = FundMarketData.query.filter_by(
            fund_code=holding.fund_code
        ).order_by(FundMarketData.update_time.desc()).first()
        
        # 计算当前市值
        current_value = 0
        latest_net_value = 0
        if market_data and market_data.net_value:
            latest_net_value = float(market_data.net_value)
            current_value = float(holding.shares) * latest_net_value
        
        # 计算盈亏
        total_cost = float(holding.cost_basis)
        total_pnl = current_value - total_cost
        total_pnl_rate = 0
        if total_cost > 0:
            total_pnl_rate = (total_pnl / total_cost) * 100
        
        # 计算当日盈亏
        daily_pnl = 0
        daily_pnl_rate = 0
        if holding.latest_net_value and latest_net_value:
            daily_change = latest_net_value - float(holding.latest_net_value)
            daily_pnl = daily_change * float(holding.shares)
            if holding.latest_net_value > 0:
                daily_pnl_rate = (daily_change / float(holding.latest_net_value)) * 100
        
        return {
            'id': holding.id,
            'fund_code': holding.fund_code,
            'fund_name': fund.fund_name if fund else '未知基金',
            'shares': holding.shares,
            'cost_basis': holding.cost_basis,
            'current_value': current_value,
            'daily_pnl': daily_pnl,
            'daily_pnl_rate': daily_pnl_rate,
            'total_pnl': total_pnl,
            'total_pnl_rate': total_pnl_rate,
            'latest_net_value': latest_net_value
        }


@api.route('/buy')
class BuyFund(Resource):
    @jwt_required()
    @api.expect(buy_request_model)
    @api.doc('buy_fund')
    @api.marshal_with(transaction_model)
    def post(self):
        """买入基金"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证基金是否存在
        fund = Fund.query.filter_by(fund_code=data['fund_code']).first()
        if not fund:
            api.abort(404, '基金不存在')
        
        # 获取基金最新净值
        market_data = FundMarketData.query.filter_by(
            fund_code=data['fund_code']
        ).order_by(FundMarketData.update_time.desc()).first()
        
        if not market_data or not market_data.net_value:
            api.abort(400, '无法获取基金净值，无法进行交易')
        
        # 计算份额
        net_value = float(market_data.net_value)
        amount = float(data['amount'])
        shares = round(amount / net_value, 4)
        
        # 计算手续费（假设费率为0.15%）
        fee = round(amount * 0.0015, 2)
        
        # 创建交易记录
        transaction = Transaction(
            user_id=current_user_id,
            fund_code=data['fund_code'],
            transaction_type='buy',
            transaction_amount=amount,
            transaction_shares=shares,
            transaction_price=net_value,
            fee=fee,
            transaction_status='success',  # 直接设为成功状态
            transaction_time=datetime.utcnow()
        )
        
        # 生成订单号
        transaction.order_id = f"BUY{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        db.session.add(transaction)
        
        # 更新持仓信息
        existing_holding = Holding.query.filter_by(
            user_id=current_user_id,
            fund_code=data['fund_code']
        ).first()
        
        if existing_holding:
            # 更新现有持仓
            total_cost = float(existing_holding.cost_basis) + amount
            total_shares = float(existing_holding.shares) + shares
            existing_holding.cost_basis = total_cost
            existing_holding.shares = total_shares
            existing_holding.current_value = total_shares * net_value
            existing_holding.latest_net_value = net_value
        else:
            # 创建新持仓
            new_holding = Holding(
                user_id=current_user_id,
                fund_code=data['fund_code'],
                shares=shares,
                cost_basis=amount,
                latest_net_value=net_value,
                current_value=shares * net_value
            )
            db.session.add(new_holding)
        
        db.session.commit()
        
        return {
            'id': transaction.id,
            'order_id': transaction.order_id,
            'fund_code': transaction.fund_code,
            'fund_name': fund.fund_name,
            'transaction_type': transaction.transaction_type,
            'transaction_amount': transaction.transaction_amount,
            'transaction_shares': transaction.transaction_shares,
            'transaction_price': transaction.transaction_price,
            'fee': transaction.fee,
            'transaction_status': transaction.transaction_status,
            'transaction_time': transaction.transaction_time,
            'confirmed_time': transaction.confirmed_time
        }


@api.route('/sell')
class SellFund(Resource):
    @jwt_required()
    @api.expect(sell_request_model)
    @api.doc('sell_fund')
    @api.marshal_with(transaction_model)
    def post(self):
        """卖出基金"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证基金是否存在
        fund = Fund.query.filter_by(fund_code=data['fund_code']).first()
        if not fund:
            api.abort(404, '基金不存在')
        
        # 检查用户是否有足够份额
        holding = Holding.query.filter_by(
            user_id=current_user_id,
            fund_code=data['fund_code']
        ).first()
        
        if not holding or float(holding.shares) < float(data['shares']):
            api.abort(400, '份额不足')
        
        # 获取基金最新净值
        market_data = FundMarketData.query.filter_by(
            fund_code=data['fund_code']
        ).order_by(FundMarketData.update_time.desc()).first()
        
        if not market_data or not market_data.net_value:
            api.abort(400, '无法获取基金净值，无法进行交易')
        
        # 计算金额
        net_value = float(market_data.net_value)
        shares = float(data['shares'])
        amount = round(shares * net_value, 2)
        
        # 计算手续费（假设费率为0.5%）
        fee = round(amount * 0.005, 2)
        
        # 创建交易记录
        transaction = Transaction(
            user_id=current_user_id,
            fund_code=data['fund_code'],
            transaction_type='sell',
            transaction_amount=amount,
            transaction_shares=shares,
            transaction_price=net_value,
            fee=fee,
            transaction_status='success',  # 直接设为成功状态
            transaction_time=datetime.utcnow()
        )
        
        # 生成订单号
        transaction.order_id = f"SELL{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        db.session.add(transaction)
        
        # 更新持仓信息
        if float(holding.shares) > shares:
            # 部分卖出，更新持仓
            holding.shares = float(holding.shares) - shares
            holding.cost_basis = float(holding.cost_basis) * (float(holding.shares) - shares) / float(holding.shares)
            holding.current_value = float(holding.shares) * net_value
            holding.latest_net_value = net_value
        else:
            # 全部卖出，删除持仓
            db.session.delete(holding)
        
        db.session.commit()
        
        return {
            'id': transaction.id,
            'order_id': transaction.order_id,
            'fund_code': transaction.fund_code,
            'fund_name': fund.fund_name,
            'transaction_type': transaction.transaction_type,
            'transaction_amount': transaction.transaction_amount,
            'transaction_shares': transaction.transaction_shares,
            'transaction_price': transaction.transaction_price,
            'fee': transaction.fee,
            'transaction_status': transaction.transaction_status,
            'transaction_time': transaction.transaction_time,
            'confirmed_time': transaction.confirmed_time
        }


@api.route('/transactions')
class TransactionList(Resource):
    @jwt_required()
    @api.doc('list_transactions')
    @api.marshal_with(api.model('TransactionsPagination', {
        'items': fields.List(fields.Nested(transaction_model), description='交易列表'),
        'total': fields.Integer(description='总数'),
        'page': fields.Integer(description='当前页'),
        'pages': fields.Integer(description='总页数'),
        'per_page': fields.Integer(description='每页数量')
    }))
    def get(self):
        """获取交易记录"""
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        transaction_type = request.args.get('type')
        status = request.args.get('status')
        
        query = Transaction.query.filter_by(user_id=current_user_id)
        
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        if status:
            query = query.filter(Transaction.transaction_status == status)
        
        pagination = query.order_by(Transaction.transaction_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = []
        for transaction in pagination.items:
            # 获取基金信息
            fund = Fund.query.filter_by(fund_code=transaction.fund_code).first()
            
            items.append({
                'id': transaction.id,
                'order_id': transaction.order_id,
                'fund_code': transaction.fund_code,
                'fund_name': fund.fund_name if fund else '未知基金',
                'transaction_type': transaction.transaction_type,
                'transaction_amount': transaction.transaction_amount,
                'transaction_shares': transaction.transaction_shares,
                'transaction_price': transaction.transaction_price,
                'fee': transaction.fee,
                'transaction_status': transaction.transaction_status,
                'transaction_time': transaction.transaction_time,
                'confirmed_time': transaction.confirmed_time
            })
        
        return {
            'items': items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }


@api.route('/portfolio/overview')
class PortfolioOverview(Resource):
    @jwt_required()
    @api.doc('get_portfolio_overview')
    @api.marshal_with(portfolio_overview_model)
    def get(self):
        """获取资产概览"""
        current_user_id = get_jwt_identity()
        
        # 获取用户所有持仓
        holdings = Holding.query.filter_by(user_id=current_user_id).all()
        
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
        
        total_pnl = total_assets - float(total_cost)
        total_pnl_rate = 0
        if float(total_cost) > 0:
            total_pnl_rate = (total_pnl / float(total_cost)) * 100
        
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


@api.route('/holdings/import')
class HoldingsImport(Resource):
    @jwt_required()
    @api.doc('import_holdings')
    def post(self):
        """导入持仓数据"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'holdings' not in data:
            api.abort(400, '缺少持仓数据')
        
        imported_count = 0
        for holding_data in data['holdings']:
            fund_code = holding_data.get('fund_code')
            shares = holding_data.get('shares')
            cost_basis = holding_data.get('cost_basis')
            
            # 验证基金是否存在
            fund = Fund.query.filter_by(fund_code=fund_code).first()
            if not fund:
                continue  # 跳过不存在的基金
            
            # 检查是否已存在持仓
            existing_holding = Holding.query.filter_by(
                user_id=current_user_id,
                fund_code=fund_code
            ).first()
            
            if existing_holding:
                # 更新现有持仓
                existing_holding.shares = shares
                existing_holding.cost_basis = cost_basis
            else:
                # 创建新持仓
                new_holding = Holding(
                    user_id=current_user_id,
                    fund_code=fund_code,
                    shares=shares,
                    cost_basis=cost_basis
                )
                db.session.add(new_holding)
            
            imported_count += 1
        
        db.session.commit()
        
        return {
            'message': f'成功导入 {imported_count} 条持仓记录',
            'imported_count': imported_count
        }