import pytest
import json
from app.models.user import User
from app.models.fund import Fund


def test_get_home_overview(client):
    """测试获取首页概览"""
    # 先注册并登录用户
    client.post('/api/auth/register', 
               data=json.dumps({
                   'username': 'home_test_user',
                   'email': 'home_test@example.com',
                   'password': 'testpassword123'
               }),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps({
                                    'email': 'home_test@example.com',
                                    'password': 'testpassword123'
                                }),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    # 获取首页概览
    response = client.get('/api/home/overview',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'asset_overview' in data
    assert 'holdings_summary' in data
    assert 'index_summary' in data
    assert 'recommended_funds' in data
    assert 'quick_actions' in data
    assert 'unread_notifications_count' in data