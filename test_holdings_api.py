import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

# 首先创建用户并登录
print("创建测试用户...")
register_data = {
    "username": "test_holdings",
    "email": "test_holdings@example.com",
    "password": "testpassword123"
}
response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
print(f"注册响应: {response.status_code}")

# 登录
login_data = {
    "email": "test_holdings@example.com",
    "password": "testpassword123"
}
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"登录响应: {response.status_code}")

if response.status_code == 200:
    token = response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 买入基金创建持仓
    print("\n买入基金...")
    buy_data = {
        'fund_code': '000001',
        'amount': 1000
    }
    response = requests.post(f"{BASE_URL}/api/transactions/buy", json=buy_data, headers=headers)
    print(f"买入响应: {response.status_code}")
    
    # 获取持仓列表
    print("\n获取持仓列表...")
    response = requests.get(f"{BASE_URL}/api/transactions/holdings", headers=headers)
    print(f"持仓响应状态: {response.status_code}")
    if response.status_code != 200:
        print(f"持仓响应内容: {response.text}")
    else:
        print(f"持仓响应内容: {response.text[:500]}...")