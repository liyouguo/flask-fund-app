import pytest
import json
from app.models.user import User


def test_register_user(client):
    """测试用户注册"""
    response = client.post('/api/auth/register', 
                          data=json.dumps({
                              'username': 'testuser',
                              'email': 'test@example.com',
                              'password': 'testpassword123'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == '用户注册成功'


def test_login_user(client):
    """测试用户登录"""
    # 先注册用户
    client.post('/api/auth/register', 
               data=json.dumps({
                   'username': 'testuser2',
                   'email': 'test2@example.com',
                   'password': 'testpassword123'
               }),
               content_type='application/json')
    
    # 登录
    response = client.post('/api/auth/login',
                          data=json.dumps({
                              'email': 'test2@example.com',
                              'password': 'testpassword123'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_get_profile(client):
    """测试获取用户资料"""
    # 先登录获取token
    client.post('/api/auth/register', 
               data=json.dumps({
                   'username': 'testuser3',
                   'email': 'test3@example.com',
                   'password': 'testpassword123'
               }),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps({
                                    'email': 'test3@example.com',
                                    'password': 'testpassword123'
                                }),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    response = client.get('/api/auth/profile',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'test3@example.com'