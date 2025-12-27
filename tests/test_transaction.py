import pytest
import json
from app.models.user import User
from app.models.fund import Fund


def test_create_transaction(client):
    """测试创建交易记录"""
    # 先注册并登录用户
    client.post('/api/auth/register', 
               data=json.dumps({
                   'username': 'trans_test_user',
                   'email': 'trans_test@example.com',
                   'password': 'testpassword123'
               }),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps({
                                    'email': 'trans_test@example.com',
                                    'password': 'testpassword123'
                                }),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    # 添加一个基金
    client.post('/api/funds/', 
               data=json.dumps({
                   'fund_code': '000004',
                   'fund_name': '测试交易基金',
                   'fund_type': '股票型',
                   'company': '测试基金公司',
                   'risk_level': '高风险'
               }),
               content_type='application/json')
    
    # 创建交易
    response = client.post('/api/transactions/',
                          data=json.dumps({
                              'fund_code': '000004',
                              'transaction_type': '买入',
                              'amount': 1000,
                              'shares': 950,
                              'price': 1.0526,
                              'transaction_date': '2023-06-15'
                          }),
                          content_type='application/json',
                          headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'transaction' in data


def test_get_transactions(client):
    """测试获取交易记录"""
    # 先注册并登录用户
    client.post('/api/auth/register', 
               data=json.dumps({
                   'username': 'trans_test_user2',
                   'email': 'trans_test2@example.com',
                   'password': 'testpassword123'
               }),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps({
                                    'email': 'trans_test2@example.com',
                                    'password': 'testpassword123'
                                }),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    # 获取交易记录
    response = client.get('/api/transactions/',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'transactions' in data