import pytest
import json
from app.models.fund import Fund, FundMarketData


def test_get_market_data(client):
    """测试获取市场数据"""
    response = client.get('/api/market/funds')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'funds' in data


def test_get_market_indices(client):
    """测试获取指数数据"""
    response = client.get('/api/market/indices')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'indices' in data


def test_get_sector_performance(client):
    """测试获取板块表现"""
    response = client.get('/api/market/sectors')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'sectors' in data