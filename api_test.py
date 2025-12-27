import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

def test_api():
    print("开始测试API接口...")
    print("="*50)
    
    # 1. 测试首页概览（无需认证）
    print("\n1. 测试首页概览接口:")
    try:
        response = requests.get(f"{BASE_URL}/api/home/overview")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ 预期结果: 需要认证")
        else:
            print(f"   响应: {response.text[:100]}...")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 2. 测试用户注册
    print("\n2. 测试用户注册接口:")
    try:
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", 
                                json=register_data)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 201:
            print("   ✓ 用户注册成功")
        else:
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 3. 测试用户登录
    print("\n3. 测试用户登录接口:")
    login_token = None
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                                json=login_data)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            login_token = result.get('access_token')
            if login_token:
                print("   ✓ 用户登录成功")
                print(f"   Token: {login_token[:20]}...")
            else:
                print("   ✗ 登录成功但未返回token")
        else:
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 4. 如果登录成功，测试需要认证的接口
    if login_token:
        headers = {'Authorization': f'Bearer {login_token}'}
        
        print("\n4. 测试获取用户资料接口:")
        try:
            response = requests.get(f"{BASE_URL}/api/auth/profile", 
                                   headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ 获取用户资料成功")
            else:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")
        
        print("\n5. 测试首页概览接口 (认证后):")
        try:
            response = requests.get(f"{BASE_URL}/api/home/overview", 
                                   headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ 获取首页概览成功")
                data = response.json()
                print(f"   返回字段: {list(data.keys())}")
            else:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")
        
        print("\n6. 测试基金列表接口:")
        try:
            response = requests.get(f"{BASE_URL}/api/funds/")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ 获取基金列表成功")
                data = response.json()
                print(f"   返回字段: {list(data.keys())}")
            else:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")
        
        print("\n7. 测试市场行情接口:")
        try:
            response = requests.get(f"{BASE_URL}/api/market/funds")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ 获取市场行情成功")
                data = response.json()
                print(f"   返回字段: {list(data.keys())}")
            else:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")
        
        print("\n8. 测试自选基金接口:")
        try:
            response = requests.get(f"{BASE_URL}/api/favorites/", 
                                   headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ 获取自选基金成功")
                data = response.json()
                print(f"   返回字段: {list(data.keys())}")
            else:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")
    
    print("\n" + "="*50)
    print("API测试完成!")

if __name__ == "__main__":
    # 等待服务器启动
    time.sleep(2)
    test_api()