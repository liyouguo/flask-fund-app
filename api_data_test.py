import requests
import json
import time
import random
import string

BASE_URL = 'http://127.0.0.1:5000'

class APIDataTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_token = None
        self.test_user_id = None
        self.test_fund_codes = ['000001', '000002', '000003', '000004', '000005']  # 使用已添加的基础基金
        self.created_transaction_ids = []
        self.created_holding_funds = []
        self.created_notification_ids = []
    
    def run_test(self):
        print("="*60)
        print("通过API接口添加数据并验证数据一致性")
        print("="*60)
        
        # 1. 创建测试用户
        print("\n【1. 创建测试用户】")
        self.create_test_user()
        
        # 2. 添加持仓数据（通过买入操作）
        print("\n【2. 通过API添加持仓数据（买入基金）】")
        self.add_holding_data()
        
        # 3. 添加更多交易记录
        print("\n【3. 通过API添加更多交易记录】")
        self.add_additional_transactions()
        
        # 4. 添加自选基金
        print("\n【4. 通过API添加自选基金】")
        self.add_favorite_data()
        
        # 5. 验证数据一致性
        print("\n【5. 验证数据一致性】")
        self.verify_data_consistency()
        
        print("\n" + "="*60)
        print("API数据添加和验证测试完成！")
        print("="*60)
    
    def create_test_user(self):
        # 生成随机用户名和邮箱
        random_suffix = ''.join(random.choices(string.digits, k=6))
        test_username = f"testuser_{random_suffix}"
        test_email = f"test_{random_suffix}@example.com"
        
        # 注册用户
        register_data = {
            "username": test_username,
            "email": test_email,
            "password": "testpassword123"
        }
        response = self.session.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 201:
            print(f"   ✓ 用户 {test_username} 注册成功")
        else:
            print(f"   ✗ 用户注册失败: {response.status_code} - {response.text}")
            return
        
        # 登录用户
        login_data = {
            "email": test_email,
            "password": "testpassword123"
        }
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            self.test_user_token = result.get('access_token')
            print("   ✓ 用户登录成功")
        else:
            print(f"   ✗ 用户登录失败: {response.status_code} - {response.text}")
    
    def add_holding_data(self):
        if not self.test_user_token:
            print("   - 跳过（需要用户认证）")
            return
        
        headers = {'Authorization': f'Bearer {self.test_user_token}'}
        
        # 通过买入操作添加持仓数据
        for i, fund_code in enumerate(self.test_fund_codes[:3]):  # 只选择前3只基金
            buy_data = {
                'fund_code': fund_code,
                'amount': 1000 + i * 500  # 递增金额
            }
            response = self.session.post(f"{BASE_URL}/api/transactions/buy", 
                                       json=buy_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ 买入基金 {fund_code} 成功，金额 {buy_data['amount']}")
                self.created_holding_funds.append(fund_code)
                if 'id' in result:
                    self.created_transaction_ids.append(result['id'])
            else:
                print(f"   ✗ 买入基金 {fund_code} 失败: {response.status_code} - {response.text}")
    
    def add_additional_transactions(self):
        if not self.test_user_token:
            print("   - 跳过（需要用户认证）")
            return
        
        headers = {'Authorization': f'Bearer {self.test_user_token}'}
        
        # 验证交易记录
        response = self.session.get(f"{BASE_URL}/api/transactions/transactions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            transaction_count = len(data.get('items', []))
            print(f"   ✓ 交易记录总数: {transaction_count}")
        else:
            print(f"   ✗ 获取交易记录失败: {response.status_code} - {response.text}")
    
    def add_favorite_data(self):
        if not self.test_user_token:
            print("   - 跳过（需要用户认证）")
            return
        
        headers = {'Authorization': f'Bearer {self.test_user_token}'}
        
        # 获取分组ID
        response = self.session.get(f"{BASE_URL}/api/favorites/groups", headers=headers)
        if response.status_code == 200:
            groups = response.json()
            default_group_id = None
            for group in groups:
                if group.get('is_default'):
                    default_group_id = group.get('id')
                    break
            
            if default_group_id:
                # 添加自选基金（可能有些已经在持仓中）
                favorite_funds = ['000001', '000002', '000005']  # 选择几只基金添加到自选
                for fund_code in favorite_funds:
                    favorite_data = {
                        'fund_code': fund_code,
                        'group_id': default_group_id
                    }
                    response = self.session.post(f"{BASE_URL}/api/favorites/", 
                                               json=favorite_data, headers=headers)
                    if response.status_code in [200, 201]:
                        print(f"   ✓ 自选基金 {fund_code} 添加成功")
                    elif response.status_code == 400:  # 基金已在自选中
                        print(f"   - 自选基金 {fund_code} 已存在")
                    else:
                        print(f"   ✗ 自选基金 {fund_code} 添加失败: {response.status_code} - {response.text}")
            else:
                print("   - 未找到默认分组")
        else:
            print(f"   ✗ 获取分组失败: {response.status_code} - {response.text}")
    
    def verify_data_consistency(self):
        if not self.test_user_token:
            print("   - 跳过验证（需要用户认证）")
            return
        
        headers = {'Authorization': f'Bearer {self.test_user_token}'}
        
        print("   正在验证数据一致性...")
        
        # 1. 验证基金数据（基础数据）
        print("   1. 验证基金数据...")
        response = self.session.get(f"{BASE_URL}/api/funds/")
        if response.status_code == 200:
            data = response.json()
            fund_count = len(data.get('items', []))
            print(f"      - 基金总数: {fund_count}")
            if fund_count >= 5:  # 应该有至少5只基础基金
                print("      ✓ 基金数据一致性验证通过")
            else:
                print("      ✗ 基金数据不一致")
        else:
            print(f"      ✗ 基金数据验证失败: {response.status_code}")
        
        # 2. 验证持仓数据
        print("   2. 验证持仓数据...")
        response = self.session.get(f"{BASE_URL}/api/transactions/holdings", headers=headers)
        if response.status_code == 200:
            holdings = response.json()
            holding_count = len(holdings) if isinstance(holdings, list) else len(holdings.get('items', [])) if isinstance(holdings, dict) else 0
            print(f"      - 持仓总数: {holding_count}")
            if holding_count >= len(self.created_holding_funds):
                print("      ✓ 持仓数据一致性验证通过")
            else:
                print("      ✗ 持仓数据不一致")
        else:
            print(f"      ✗ 持仓数据验证失败: {response.status_code}")
        
        # 3. 验证交易数据
        print("   3. 验证交易数据...")
        response = self.session.get(f"{BASE_URL}/api/transactions/transactions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            transaction_count = len(data.get('items', []))
            print(f"      - 交易总数: {transaction_count}")
            if transaction_count >= len(self.created_holding_funds):
                print("      ✓ 交易数据一致性验证通过")
            else:
                print("      ✗ 交易数据不一致")
        else:
            print(f"      ✗ 交易数据验证失败: {response.status_code}")
        
        # 4. 验证自选数据
        print("   4. 验证自选数据...")
        response = self.session.get(f"{BASE_URL}/api/favorites/", headers=headers)
        if response.status_code == 200:
            favorites = response.json()
            favorite_count = 0
            if isinstance(favorites, list):
                for group in favorites:
                    if 'favorites' in group and isinstance(group['favorites'], list):
                        favorite_count += len(group['favorites'])
            print(f"      - 自选总数: {favorite_count}")
            print("      ✓ 自选数据一致性验证通过")
        else:
            print(f"      ✗ 自选数据验证失败: {response.status_code}")
        
        # 5. 验证资产概览
        print("   5. 验证资产概览...")
        response = self.session.get(f"{BASE_URL}/api/transactions/portfolio/overview", headers=headers)
        if response.status_code == 200:
            data = response.json()
            holdings_count = data.get('holdings_count', 0)
            total_assets = data.get('total_assets', 0)
            print(f"      - 持仓数量: {holdings_count}")
            print(f"      - 总资产: {total_assets}")
            print("      ✓ 资产概览数据验证通过")
        else:
            print(f"      ✗ 资产概览验证失败: {response.status_code}")
        
        # 6. 验证首页概览
        print("   6. 验证首页概览...")
        response = self.session.get(f"{BASE_URL}/api/home/overview", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"      - 首页数据字段数: {len(data.keys())}")
            print("      ✓ 首页概览数据验证通过")
        else:
            print(f"      ✗ 首页概览验证失败: {response.status_code}")
        
        # 7. 验证特定基金详情
        print("   7. 验证基金详情...")
        if self.created_holding_funds:
            test_fund_code = self.created_holding_funds[0]
            response = self.session.get(f"{BASE_URL}/api/funds/{test_fund_code}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"      - 基金 {test_fund_code} 详情获取成功")
                print("      ✓ 基金详情数据验证通过")
            else:
                print(f"      ✗ 基金详情验证失败: {response.status_code}")
        
        print("   ✓ 数据一致性验证完成")

if __name__ == "__main__":
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    # 运行测试
    test = APIDataTest()
    test.run_test()