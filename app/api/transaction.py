from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.transaction import Holding, Transaction
from app.models.fund import Fund, FundMarketData

api = Namespace('transactions', description='交易功能相关操作')

# 数据模型定义
holding_model = api.model('Holding', {
    'id': fields.String(required=True, description='持仓ID'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'shares': fields.String(required=True, description='持有份额'),
    'cost_basis': fields.String(required=True, description='成本基础'),
    'current_value': fields.String(required=True, description='当前市值'),
    'daily_pnl': fields.String(required=True, description='当日盈亏'),
    'daily_pnl_rate': fields.String(required=True, description='当日盈亏率'),
    'total_pnl': fields.String(required=True, description='累计盈亏'),
    'total_pnl_rate': fields.String(required=True, description='累计盈亏率'),
    'latest_net_value': fields.String(required=True, description='最新净值')
})

transaction_model = api.model('Transaction', {
    'id': fields.String(required=True, description='交易ID'),
    'order_id': fields.String(required=True, description='订单号'),
    'fund_code': fields.String(required=True, description='基金代码'),
    'fund_name': fields.String(required=True, description='基金名称'),
    'transaction_type': fields.String(required=True, description='交易类型'),
    'transaction_amount': fields.String(required=True, description='交易金额'),
    'transaction_shares': fields.String(required=True, description='交易份额'),
    'transaction_price': fields.String(required=True, description='交易价格'),
    'fee': fields.String(required=True, description='手续费'),
    'transaction_status': fields.String(required=True, description='交易状态'),
    'transaction_time': fields.DateTime(required=True, description='交易时间'),
    'confirmed_time': fields.DateTime(description='确认时间')
})

transaction_list_model = api.model('TransactionList', {
    'items': fields.List(fields.Nested(transaction_model)),
    'total': fields.Integer,
    'page': fields.Integer,
    'pages': fields.Integer,
    'per_page': fields.Integer
})

portfolio_overview_model = api.model('PortfolioOverview', {
    'total_assets': fields.String(required=True, description='总资产'),
    'daily_pnl': fields.String(required=True, description='当日盈亏'),
    'daily_pnl_rate': fields.String(required=True, description='当日盈亏率'),
    'total_pnl': fields.String(required=True, description='累计盈亏'),
    'total_pnl_rate': fields.String(required=True, description='累计盈亏率'),
    'holdings_count': fields.Integer(required=True, description='持仓数量')
})

buy_model = api.model('Buy', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'amount': fields.Float(required=True, description='购买金额')
})

sell_model = api.model('Sell', {
    'fund_code': fields.String(required=True, description='基金代码'),
    'shares': fields.Float(required=True, description='卖出份额')
})

import_holdings_model = api.model('ImportHoldings', {
    'holdings': fields.List(fields.Raw, required=True, description='持仓数据列表')
})

@api.route('/holdings')
class HoldingList(Resource):
    @api.doc('list_holdings')
    @jwt_required()
    @api.marshal_with(holding_model)
    def get(self):
        """获取持仓列表"""
        current_user_id = get_jwt_identity()
        
        holdings = Holding.query.filter_by(user_id=current_user_id).all()
        result = []
        
        for holding in holdings:
            fund = Fund.query.filter_by(fund_code=holding.fund_code).first()
            if fund:
                holding_data = {
                    'id': holding.id,
                    'fund_code': holding.fund_code,
                    'fund_name': fund.fund_name,
                    'shares': str(holding.shares),
                    'cost_basis': str(holding.cost_basis),
                    'current_value': str(holding.current_value),
                    'daily_pnl': str(holding.daily_pnl),
                    'daily_pnl_rate': str(holding.daily_pnl_rate),
                    'total_pnl': str(holding.total_pnl),
                    'total_pnl_rate': str(holding.total_pnl_rate),
                    'latest_net_value': str(holding.latest_net_value) if holding.latest_net_value else '0.0000'
                }
                result.append(holding_data)
        
        return result

@api.route('/holdings/<string:fund_code>')
@api.param('fund_code', '基金代码')
class HoldingDetail(Resource):
    @api.doc('get_holding')
    @jwt_required()
    @api.marshal_with(holding_model)
    def get(self, fund_code):
        """获取单只基金持仓详情"""
        current_user_id = get_jwt_identity()
        
        holding = Holding.query.filter_by(user_id=current_user_id, fund_code=fund_code).first_or_404()
        fund = Fund.query.filter_by(fund_code=fund_code).first_or_404()
        
        holding_data = {
            'id': holding.id,
            'fund_code': holding.fund_code,
            'fund_name': fund.fund_name,
            'shares': str(holding.shares),
            'cost_basis': str(holding.cost_basis),
            'current_value': str(holding.current_value),
            'daily_pnl': str(holding.daily_pnl),
            'daily_pnl_rate': str(holding.daily_pnl_rate),
            'total_pnl': str(holding.total_pnl),
            'total_pnl_rate': str(holding.total_pnl_rate),
            'latest_net_value': str(holding.latest_net_value) if holding.latest_net_value else '0.0000'
        }
        
        return holding_data

@api.route('/buy')
class BuyFund(Resource):
    @api.doc('buy_fund')
    @api.expect(buy_model)
    @jwt_required()
    @api.marshal_with(transaction_model)
    def post(self):
        """买入基金"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        fund_code = data.get('fund_code')
        amount = data.get('amount')
        
        if not fund_code or not amount:
            api.abort(400, '基金代码和金额不能为空')
        
        if amount <= 0:
            api.abort(400, '购买金额必须大于0')
        
        fund = Fund.query.filter_by(fund_code=fund_code).first_or_404()
        market_data = FundMarketData.query.filter_by(fund_code=fund_code).order_by(FundMarketData.update_time.desc()).first()
        
        if not market_data:
            api.abort(404, '基金市场数据不存在')
        
        transaction_price = market_data.net_value
        transaction_shares = amount / transaction_price if transaction_price else 0
        
        # 计算手续费（简化计算）
        fee = amount * 0.0015  # 0.15%手续费
        
        # 创建交易记录
        transaction = Transaction(
            user_id=current_user_id,
            fund_code=fund_code,
            transaction_type='buy',
            transaction_amount=amount,
            transaction_shares=transaction_shares,
            transaction_price=transaction_price,
            fee=fee,
            transaction_status='success'
        )
        
        db.session.add(transaction)
        
        # 更新或创建持仓
        holding = Holding.query.filter_by(user_id=current_user_id, fund_code=fund_code).first()
        if holding:
            # 更新现有持仓
            total_cost = holding.cost_basis + amount
            total_shares = holding.shares + transaction_shares
            holding.cost_basis = total_cost
            holding.shares = total_shares
            holding.latest_net_value = transaction_price
        else:
            # 创建新持仓
            holding = Holding(
                user_id=current_user_id,
                fund_code=fund_code,
                shares=transaction_shares,
                cost_basis=amount,
                latest_net_value=transaction_price
            )
            db.session.add(holding)
        
        db.session.commit()
        
        # 重新获取完整的交易信息用于返回
        transaction = Transaction.query.filter_by(id=transaction.id).first()
        fund = Fund.query.filter_by(fund_code=fund_code).first()
        
        transaction_data = {
            'id': transaction.id,
            'order_id': transaction.order_id,
            'fund_code': transaction.fund_code,
            'fund_name': fund.fund_name,
            'transaction_type': transaction.transaction_type,
            'transaction_amount': str(transaction.transaction_amount),
            'transaction_shares': str(transaction.transaction_shares),
            'transaction_price': str(transaction.transaction_price),
            'fee': str(transaction.fee),
            'transaction_status': transaction.transaction_status,
            'transaction_time': transaction.transaction_time,
            'confirmed_time': transaction.confirmed_time
        }
        
        return transaction_data

@api.route('/sell')
class SellFund(Resource):
    @api.doc('sell_fund')
    @api.expect(sell_model)
    @jwt_required()
    @api.marshal_with(transaction_model)
    def post(self):
        """卖出基金"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        fund_code = data.get('fund_code')
        shares = data.get('shares')
        
        if not fund_code or not shares:
            api.abort(400, '基金代码和份额不能为空')
        
        if shares <= 0:
            api.abort(400, '卖出份额必须大于0')
        
        fund = Fund.query.filter_by(fund_code=fund_code).first_or_404()
        market_data = FundMarketData.query.filter_by(fund_code=fund_code).order_by(FundMarketData.update_time.desc()).first()
        
        if not market_data:
            api.abort(404, '基金市场数据不存在')
        
        # 检查持仓是否足够
        holding = Holding.query.filter_by(user_id=current_user_id, fund_code=fund_code).first()
        if not holding or holding.shares < shares:
            api.abort(400, '持仓不足')
        
        transaction_price = market_data.net_value
        transaction_amount = shares * transaction_price
        
        # 计算手续费（简化计算）
        fee = transaction_amount * 0.005  # 0.5%手续费
        
        # 创建交易记录
        transaction = Transaction(
            user_id=current_user_id,
            fund_code=fund_code,
            transaction_type='sell',
            transaction_amount=transaction_amount,
            transaction_shares=shares,
            transaction_price=transaction_price,
            fee=fee,
            transaction_status='success'
        )
        
        db.session.add(transaction)
        
        # 更新持仓
        holding.shares -= shares
        if holding.shares <= 0:
            # 如果份额卖完，删除持仓记录
            db.session.delete(holding)
        else:
            # 更新持仓市值等信息
            holding.current_value = holding.shares * transaction_price
            holding.latest_net_value = transaction_price
        
        db.session.commit()
        
        # 重新获取完整的交易信息用于返回
        transaction = Transaction.query.filter_by(id=transaction.id).first()
        fund = Fund.query.filter_by(fund_code=fund_code).first()
        
        transaction_data = {
            'id': transaction.id,
            'order_id': transaction.order_id,
            'fund_code': transaction.fund_code,
            'fund_name': fund.fund_name,
            'transaction_type': transaction.transaction_type,
            'transaction_amount': str(transaction.transaction_amount),
            'transaction_shares': str(transaction.transaction_shares),
            'transaction_price': str(transaction.transaction_price),
            'fee': str(transaction.fee),
            'transaction_status': transaction.transaction_status,
            'transaction_time': transaction.transaction_time,
            'confirmed_time': transaction.confirmed_time
        }
        
        return transaction_data

@api.route('/transactions')
class TransactionList(Resource):
    @api.doc('list_transactions')
    @jwt_required()
    @api.marshal_with(transaction_list_model)
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
        
        transactions = query.order_by(Transaction.transaction_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'items': [],
            'total': transactions.total,
            'page': transactions.page,
            'pages': transactions.pages,
            'per_page': transactions.per_page
        }
        
        for transaction in transactions.items:
            fund = Fund.query.filter_by(fund_code=transaction.fund_code).first()
            transaction_data = {
                'id': transaction.id,
                'order_id': transaction.order_id,
                'fund_code': transaction.fund_code,
                'fund_name': fund.fund_name if fund else transaction.fund_code,
                'transaction_type': transaction.transaction_type,
                'transaction_amount': str(transaction.transaction_amount),
                'transaction_shares': str(transaction.transaction_shares),
                'transaction_price': str(transaction.transaction_price),
                'fee': str(transaction.fee),
                'transaction_status': transaction.transaction_status,
                'transaction_time': transaction.transaction_time,
                'confirmed_time': transaction.confirmed_time
            }
            result['items'].append(transaction_data)
        
        return result

@api.route('/portfolio/overview')
class PortfolioOverview(Resource):
    @api.doc('get_portfolio_overview')
    @jwt_required()
    @api.marshal_with(portfolio_overview_model)
    def get(self):
        """获取资产概览"""
        current_user_id = get_jwt_identity()
        
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
        
        overview = {
            'total_assets': str(total_assets),
            'daily_pnl': str(daily_pnl),
            'daily_pnl_rate': str(round(daily_pnl_rate, 2)),
            'total_pnl': str(total_pnl),
            'total_pnl_rate': str(round(total_pnl_rate, 2)),
            'holdings_count': len(holdings)
        }
        
        return overview

@api.route('/holdings/import')
class ImportHoldings(Resource):
    @api.doc('import_holdings')
    @api.expect(import_holdings_model)
    @jwt_required()
    def post(self):
        """导入持仓数据"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        holdings_data = data.get('holdings', [])
        imported_count = 0
        
        for holding_data in holdings_data:
            fund_code = holding_data.get('fund_code')
            shares = holding_data.get('shares', 0)
            cost_basis = holding_data.get('cost_basis', 0)
            
            if not fund_code:
                continue
            
            # 检查基金是否存在
            fund = Fund.query.filter_by(fund_code=fund_code).first()
            if not fund:
                continue
            
            # 查找或创建持仓记录
            holding = Holding.query.filter_by(user_id=current_user_id, fund_code=fund_code).first()
            if holding:
                # 更新现有持仓
                holding.shares = shares
                holding.cost_basis = cost_basis
            else:
                # 创建新持仓
                holding = Holding(
                    user_id=current_user_id,
                    fund_code=fund_code,
                    shares=shares,
                    cost_basis=cost_basis
                )
                db.session.add(holding)
            
            imported_count += 1
        
        db.session.commit()
        
        return {
            'message': f'成功导入 {imported_count} 条持仓记录',
            'imported_count': imported_count
        }, 200