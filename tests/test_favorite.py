import pytest
import json
from app.models.user import User
from app.models.fund import Fund


def test_add_favorite(client):
    """测试添加自选基金"""
    # 先注册并登录用户
    client.post('/api/auth/register', 
               data=json.dumps({
                   'username': 'fav_test_user',
                   'email': 'fav_test@example.com',
                   'password': 'testpassword123'
               }),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps({
                                    'email': 'fav_test@example.com',
                                    'password': 'testpassword123'
                                }),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    # 添加一个基金
    client.post('/api/funds/', 
               data=json.dumps({
                   'fund_code': '000002',
                   'fund_name': '测试自选基金',
                   'fund_type': '混合型',
                   'company': '测试基金公司',
                   'risk_level': '中风险'
               }),
               content_type='application/json')
    
    # 添加到自选
    response = client.post('/api/favorites/',
                          data=json.dumps({
                              'fund_code': '000002'
                          }),
                          content_type='application/json',
                          headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == '基金已添加到自选'


def test_get_favorites(client):
    """测试获取自选基金列表"""
    # 先注册并登录用户
    client.post('/api/auth/register', 
               data=json.dumps({
                   'username': 'fav_test_user2',
                   'email': 'fav_test2@example.com',
                   'password': 'testpassword123'
               }),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps({
                                    'email': 'fav_test2@example.com',
                                    'password': 'testpassword123'
                                }),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    # 添加一个基金
    client.post('/api/funds/', 
               data=json.dumps({
                   'fund_code': '000003',
                   'fund_name': '测试自选基金2',
                   'fund_type': '债券型',
                   'company': '测试基金公司',
                   'risk_level': '低风险'
               }),
               content_type='application/json')
    
    # 添加到自选
    client.post('/api/favorites/',
               data=json.dumps({
                   'fund_code': '000003'
               }),
               content_type='application/json',
               headers={'Authorization': f'Bearer {token}'})
    
    # 获取自选列表
    response = client.get('/api/favorites/',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'favorites' in data
    assert len(data['favorites']) >= 1