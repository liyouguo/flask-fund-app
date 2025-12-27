import pytest
import json
from app.models.fund import Fund


def test_get_funds(client):
    """测试获取基金列表"""
    response = client.get('/api/funds/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'funds' in data
    assert 'total' in data
    assert 'page' in data
    assert 'pages' in data


def test_get_fund_detail(client):
    """测试获取基金详情"""
    # 先添加一个基金
    client.post('/api/funds/', 
               data=json.dumps({
                   'fund_code': '000001',
                   'fund_name': '测试基金',
                   'fund_type': '股票型',
                   'company': '测试基金公司',
                   'risk_level': '高风险'
               }),
               content_type='application/json')
    
    response = client.get('/api/funds/000001')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'fund' in data
    assert data['fund']['fund_code'] == '000001'


def test_search_funds(client):
    """测试搜索基金"""
    response = client.get('/api/funds/search?q=测试')
    assert response.status_code == 200