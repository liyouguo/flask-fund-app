# 场外基金投资辅助工具 - API接口文档

## 1. 用户认证模块

### 1.1 用户注册
- **接口地址**: `POST /api/auth/register`
- **功能描述**: 新用户注册
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | username | string | 是 | 用户名 |
  | email | string | 是 | 邮箱地址 |
  | password | string | 是 | 密码 |

- **返回数据结构示例**:
```json
{
  "id": "user-uuid-string",
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2023-10-01T10:00:00Z"
}
```

### 1.2 用户登录
- **接口地址**: `POST /api/auth/login`
- **功能描述**: 用户登录
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | email | string | 是 | 邮箱地址 |
  | password | string | 是 | 密码 |

- **返回数据结构示例**:
```json
{
  "access_token": "jwt-token-string",
  "refresh_token": "refresh-token-string",
  "user": {
    "id": "user-uuid-string",
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### 1.3 刷新令牌
- **接口地址**: `POST /api/auth/refresh`
- **功能描述**: 刷新访问令牌
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer refresh_token |

- **返回数据结构示例**:
```json
{
  "access_token": "new-jwt-token-string"
}
```

### 1.4 获取用户资料
- **接口地址**: `GET /api/auth/profile`
- **功能描述**: 获取当前登录用户资料
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "id": "user-uuid-string",
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2023-10-01T10:00:00Z"
}
```

### 1.5 更新用户资料
- **接口地址**: `PUT /api/auth/profile`
- **功能描述**: 更新当前登录用户资料
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | username | string | 否 | 用户名 |

- **返回数据结构示例**:
```json
{
  "id": "user-uuid-string",
  "username": "updated-username",
  "email": "test@example.com",
  "created_at": "2023-10-01T10:00:00Z"
}
```

### 1.6 用户登出
- **接口地址**: `POST /api/auth/logout`
- **功能描述**: 用户登出
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "message": "登出成功"
}
```

## 2. 基金数据模块

### 2.1 获取基金列表
- **接口地址**: `GET /api/funds/`
- **功能描述**: 获取基金列表（支持分页和筛选）
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | page | integer | 否 | 页码，默认为1 |
  | per_page | integer | 否 | 每页数量，默认为20，最大100 |
  | type | string | 否 | 基金类型筛选 |
  | search | string | 否 | 搜索关键词 |

- **返回数据结构示例**:
```json
{
  "items": [
    {
      "id": "fund-uuid-string",
      "fund_code": "000001",
      "fund_name": "华夏成长混合",
      "fund_type": "混合型",
      "risk_level": "R3",
      "company": "华夏基金管理有限公司",
      "net_asset_value": "100.5",
      "management_fee": "0.015",
      "custody_fee": "0.002",
      "establishment_date": "2001-12-18"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5,
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```

### 2.2 获取基金详情
- **接口地址**: `GET /api/funds/{fund_code}`
- **功能描述**: 获取单个基金的详细信息
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |

- **返回数据结构示例**:
```json
{
  "id": "fund-uuid-string",
  "fund_code": "000001",
  "fund_name": "华夏成长混合",
  "fund_type": "混合型",
  "risk_level": "R3",
  "company": "华夏基金管理有限公司",
  "net_asset_value": "100.5",
  "management_fee": "0.015",
  "custody_fee": "0.002",
  "establishment_date": "2001-12-18",
  "market_data": {
    "id": "market-data-uuid-string",
    "fund_code": "000001",
    "net_value": "2.3567",
    "daily_change": "0.035",
    "daily_change_rate": "0.015",
    "weekly_change_rate": "-0.025",
    "monthly_change_rate": "0.056",
    "quarterly_change_rate": "0.123",
    "yearly_change_rate": "0.234",
    "three_year_change_rate": "0.456",
    "update_time": "2023-10-01T10:00:00Z"
  }
}
```

### 2.3 获取基金历史净值
- **接口地址**: `GET /api/funds/{fund_code}/history`
- **功能描述**: 获取基金历史净值数据
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | days | integer | 否 | 获取最近N天的数据，默认为30天 |

- **返回数据结构示例**:
```json
{
  "fund_code": "000001",
  "history": [
    {
      "date": "2023-10-01",
      "net_value": "2.3567",
      "daily_change": "0.035",
      "daily_change_rate": "0.015"
    }
  ],
  "time_range": "最近30天"
}
```

### 2.4 基金搜索
- **接口地址**: `GET /api/funds/search`
- **功能描述**: 搜索基金
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | q | string | 是 | 搜索关键词 |
  | page | integer | 否 | 页码，默认为1 |
  | per_page | integer | 否 | 每页数量，默认为20，最大100 |

- **返回数据结构示例**:
```json
{
  "items": [
    {
      "id": "fund-uuid-string",
      "fund_code": "000001",
      "fund_name": "华夏成长混合",
      "fund_type": "混合型",
      "risk_level": "R3",
      "company": "华夏基金管理有限公司",
      "net_asset_value": "100.5",
      "management_fee": "0.015",
      "custody_fee": "0.002",
      "establishment_date": "2001-12-18"
    }
  ],
  "total": 5,
  "page": 1,
  "pages": 1,
  "per_page": 20,
  "has_next": false,
  "has_prev": false
}
```

## 3. 自选功能模块

### 3.1 获取自选基金列表
- **接口地址**: `GET /api/favorites/`
- **功能描述**: 获取用户自选基金列表
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
[
  {
    "group": {
      "id": "group-uuid-string",
      "user_id": "user-uuid-string",
      "group_name": "我的自选",
      "order_index": 0,
      "is_default": true,
      "created_at": "2023-10-01T10:00:00Z",
      "updated_at": "2023-10-01T10:00:00Z"
    },
    "favorites": [
      {
        "id": "favorite-uuid-string",
        "fund": {
          "fund_code": "000001",
          "fund_name": "华夏成长混合",
          "fund_type": "混合型",
          "risk_level": "R3"
        },
        "group": {
          "id": "group-uuid-string",
          "user_id": "user-uuid-string",
          "group_name": "我的自选",
          "order_index": 0,
          "is_default": true,
          "created_at": "2023-10-01T10:00:00Z",
          "updated_at": "2023-10-01T10:00:00Z"
        },
        "added_at": "2023-10-01T10:00:00Z"
      }
    ]
  }
]
```

### 3.2 添加自选基金
- **接口地址**: `POST /api/favorites/`
- **功能描述**: 添加基金到自选列表
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |
  | group_id | string | 是 | 分组ID |

- **返回数据结构示例**:
```json
{
  "id": "favorite-uuid-string",
  "user_id": "user-uuid-string",
  "fund_code": "000001",
  "group_id": "group-uuid-string",
  "added_at": "2023-10-01T10:00:00Z",
  "updated_at": "2023-10-01T10:00:00Z",
  "is_deleted": false
}
```

### 3.3 批量添加自选基金
- **接口地址**: `POST /api/favorites/batch`
- **功能描述**: 批量添加自选基金
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_codes | array | 是 | 基金代码列表 |
  | group_id | string | 是 | 分组ID |

- **返回数据结构示例**:
```json
{
  "message": "批量添加完成，成功添加 2 只基金",
  "added_count": 2,
  "failed_count": 0,
  "failed_funds": []
}
```

### 3.4 移除自选基金
- **接口地址**: `DELETE /api/favorites/{fund_code}`
- **功能描述**: 移除自选基金
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "message": "自选基金已移除"
}
```

### 3.5 获取自选分组列表
- **接口地址**: `GET /api/favorites/groups`
- **功能描述**: 获取自选分组列表
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
[
  {
    "id": "group-uuid-string",
    "user_id": "user-uuid-string",
    "group_name": "我的自选",
    "order_index": 0,
    "is_default": true,
    "created_at": "2023-10-01T10:00:00Z",
    "updated_at": "2023-10-01T10:00:00Z"
  }
]
```

### 3.6 创建自选分组
- **接口地址**: `POST /api/favorites/groups`
- **功能描述**: 创建自选分组
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | group_name | string | 是 | 分组名称 |
  | order_index | integer | 否 | 排序序号，默认为0 |

- **返回数据结构示例**:
```json
{
  "id": "group-uuid-string",
  "user_id": "user-uuid-string",
  "group_name": "科技股",
  "order_index": 1,
  "is_default": false,
  "created_at": "2023-10-01T10:00:00Z",
  "updated_at": "2023-10-01T10:00:00Z"
}
```

### 3.7 更新自选分组
- **接口地址**: `PUT /api/favorites/groups/{group_id}`
- **功能描述**: 更新自选分组（重命名）
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | group_id | string | 是 | 分组ID |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | group_name | string | 是 | 新分组名称 |

- **返回数据结构示例**:
```json
{
  "id": "group-uuid-string",
  "user_id": "user-uuid-string",
  "group_name": "新分组名称",
  "order_index": 1,
  "is_default": false,
  "created_at": "2023-10-01T10:00:00Z",
  "updated_at": "2023-10-01T11:00:00Z"
}
```

### 3.8 删除自选分组
- **接口地址**: `DELETE /api/favorites/groups/{group_id}`
- **功能描述**: 删除自选分组
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | group_id | string | 是 | 分组ID |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "message": "分组已删除"
}
```

### 3.9 重新排序分组
- **接口地址**: `PUT /api/favorites/groups/reorder`
- **功能描述**: 重新排序分组
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | group_ids | array | 是 | 分组ID列表（按新顺序） |

- **返回数据结构示例**:
```json
{
  "message": "分组排序更新成功"
}
```

### 3.10 清空分组
- **接口地址**: `POST /api/favorites/groups/{group_id}/clear`
- **功能描述**: 清空分组（移除分组内所有基金）
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | group_id | string | 是 | 分组ID |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "message": "分组 \"分组名称\" 已清空"
}
```

## 4. 交易功能模块

### 4.1 获取持仓列表
- **接口地址**: `GET /api/transactions/holdings`
- **功能描述**: 获取持仓列表
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
[
  {
    "id": "holding-uuid-string",
    "fund_code": "000001",
    "fund_name": "华夏成长混合",
    "shares": "1000.0000",
    "cost_basis": "2356.70",
    "current_value": "2356.70",
    "daily_pnl": "35.00",
    "daily_pnl_rate": "1.50",
    "total_pnl": "35.00",
    "total_pnl_rate": "1.50",
    "latest_net_value": "2.3567"
  }
]
```

### 4.2 获取单只基金持仓详情
- **接口地址**: `GET /api/transactions/holdings/{fund_code}`
- **功能描述**: 获取单只基金持仓详情
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "id": "holding-uuid-string",
  "fund_code": "000001",
  "fund_name": "华夏成长混合",
  "shares": "1000.0000",
  "cost_basis": "2356.70",
  "current_value": "2356.70",
  "daily_pnl": "35.00",
  "daily_pnl_rate": "1.50",
  "total_pnl": "35.00",
  "total_pnl_rate": "1.50",
  "latest_net_value": "2.3567"
}
```

### 4.3 买入基金
- **接口地址**: `POST /api/transactions/buy`
- **功能描述**: 买入基金
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |
  | amount | number | 是 | 购买金额 |

- **返回数据结构示例**:
```json
{
  "id": "transaction-uuid-string",
  "order_id": "BUY2023100110001234",
  "fund_code": "000001",
  "fund_name": "华夏成长混合",
  "transaction_type": "buy",
  "transaction_amount": "1000.00",
  "transaction_shares": "424.3500",
  "transaction_price": "2.3567",
  "fee": "1.50",
  "transaction_status": "success",
  "transaction_time": "2023-10-01T10:00:00Z",
  "confirmed_time": null
}
```

### 4.4 卖出基金
- **接口地址**: `POST /api/transactions/sell`
- **功能描述**: 卖出基金
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |
  | shares | number | 是 | 卖出份额 |

- **返回数据结构示例**:
```json
{
  "id": "transaction-uuid-string",
  "order_id": "SELL2023100110001234",
  "fund_code": "000001",
  "fund_name": "华夏成长混合",
  "transaction_type": "sell",
  "transaction_amount": "1000.00",
  "transaction_shares": "424.3500",
  "transaction_price": "2.3567",
  "fee": "5.00",
  "transaction_status": "success",
  "transaction_time": "2023-10-01T10:00:00Z",
  "confirmed_time": null
}
```

### 4.5 获取交易记录
- **接口地址**: `GET /api/transactions/transactions`
- **功能描述**: 获取交易记录
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | page | integer | 否 | 页码，默认为1 |
  | per_page | integer | 否 | 每页数量，默认为20，最大100 |
  | type | string | 否 | 交易类型筛选 |
  | status | string | 否 | 交易状态筛选 |

- **返回数据结构示例**:
```json
{
  "items": [
    {
      "id": "transaction-uuid-string",
      "order_id": "BUY2023100110001234",
      "fund_code": "000001",
      "fund_name": "华夏成长混合",
      "transaction_type": "buy",
      "transaction_amount": "1000.00",
      "transaction_shares": "424.3500",
      "transaction_price": "2.3567",
      "fee": "1.50",
      "transaction_status": "success",
      "transaction_time": "2023-10-01T10:00:00Z",
      "confirmed_time": null
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1,
  "per_page": 20
}
```

### 4.6 获取资产概览
- **接口地址**: `GET /api/transactions/portfolio/overview`
- **功能描述**: 获取资产概览
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "total_assets": "10000.00",
  "daily_pnl": "150.00",
  "daily_pnl_rate": "1.52",
  "total_pnl": "500.00",
  "total_pnl_rate": "5.26",
  "holdings_count": 5
}
```

### 4.7 导入持仓数据
- **接口地址**: `POST /api/transactions/holdings/import`
- **功能描述**: 导入持仓数据
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | holdings | array | 是 | 持仓数据列表 |

- **返回数据结构示例**:
```json
{
  "message": "成功导入 3 条持仓记录",
  "imported_count": 3
}
```

## 5. 首页模块

### 5.1 获取首页概览
- **接口地址**: `GET /api/home/overview`
- **功能描述**: 获取首页概览数据
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "asset_overview": {
    "total_assets": "10000.00",
    "daily_pnl": "150.00",
    "daily_pnl_rate": "1.52",
    "total_pnl": "500.00",
    "total_pnl_rate": "5.26",
    "holdings_count": 5
  },
  "holdings_summary": [
    {
      "fund_code": "000001",
      "fund_name": "华夏成长混合",
      "shares": "1000.0000",
      "current_value": "2356.70",
      "daily_pnl": "35.00",
      "daily_pnl_rate": "1.50"
    }
  ],
  "index_summary": [
    {
      "index_code": "000001",
      "index_name": "上证指数",
      "current_point": "3250.12",
      "daily_change": "15.23",
      "daily_change_rate": "0.47"
    }
  ],
  "recommended_funds": [
    {
      "fund_code": "000001",
      "fund_name": "华夏成长混合",
      "fund_type": "混合型",
      "risk_level": "R3",
      "net_value": "2.3567",
      "daily_change_rate": "1.50",
      "recommendation_reason": "符合您的风险偏好(R3)",
      "performance_rank": "同类第5名"
    }
  ],
  "quick_actions": [
    {
      "id": "trade_buy",
      "name": "买入",
      "icon": "buy",
      "url": "/trade/buy",
      "order": 1
    }
  ],
  "unread_notifications_count": 3,
  "update_time": "2023-10-01T10:00:00Z"
}
```

## 6. 市场行情模块

### 6.1 获取市场基金列表
- **接口地址**: `GET /api/market/funds`
- **功能描述**: 获取市场基金列表
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | page | integer | 否 | 页码，默认为1 |
  | per_page | integer | 否 | 每页数量，默认为20，最大100 |
  | type | string | 否 | 基金类型筛选 |

- **返回数据结构示例**:
```json
{
  "items": [
    {
      "fund_code": "000001",
      "fund_name": "华夏成长混合",
      "fund_type": "混合型",
      "net_value": "2.3567",
      "daily_change": "0.035",
      "daily_change_rate": "1.50",
      "update_time": "2023-10-01T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5,
  "per_page": 20
}
```

### 6.2 获取热门板块
- **接口地址**: `GET /api/market/sectors`
- **功能描述**: 获取热门板块
- **返回数据结构示例**:
```json
{
  "items": [
    {
      "sector_code": "C01",
      "sector_name": "科技板块",
      "daily_change_rate": "2.50",
      "weekly_change_rate": "3.20",
      "monthly_change_rate": "5.60",
      "yearly_change_rate": "15.80",
      "hot_score": 95,
      "update_time": "2023-10-01T10:00:00Z"
    }
  ]
}
```

### 6.3 获取市场资讯
- **接口地址**: `GET /api/market/news`
- **功能描述**: 获取市场资讯
- **返回数据结构示例**:
```json
{
  "items": [
    {
      "news_id": "news_001",
      "title": "科技股今日大幅上涨",
      "source": "财经日报",
      "publish_time": "2023-10-01T08:00:00Z",
      "content_url": "https://example.com/news/001",
      "thumbnail_url": "https://example.com/thumbnails/001.jpg",
      "category": "市场动态",
      "is_read": false
    }
  ]
}
```

### 6.4 获取主要指数
- **接口地址**: `GET /api/market/index`
- **功能描述**: 获取主要指数
- **返回数据结构示例**:
```json
{
  "items": [
    {
      "index_code": "000001",
      "index_name": "上证指数",
      "current_point": "3250.12",
      "daily_change": "15.23",
      "daily_change_rate": "0.47",
      "update_time": "2023-10-01T10:00:00Z"
    }
  ]
}
```

### 6.5 获取板块预测
- **接口地址**: `GET /api/market/sectors/{sector_code}/prediction`
- **功能描述**: 获取板块预测
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | sector_code | string | 是 | 板块代码 |

- **返回数据结构示例**:
```json
{
  "prediction_id": "pred_C01_20231001",
  "sector_code": "C01",
  "sector_name": "科技板块",
  "prediction_trend": "up",
  "confidence_score": 85,
  "prediction_basis": "基于历史数据和市场趋势分析，科技板块未来一周可能上涨",
  "prediction_time": "2023-10-01T10:00:00Z"
}
```

### 6.6 获取基金分析
- **接口地址**: `GET /api/market/funds/{fund_code}/analysis`
- **功能描述**: 获取基金分析
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | fund_code | string | 是 | 基金代码 |

- **返回数据结构示例**:
```json
{
  "fund_code": "000001",
  "fund_name": "华夏成长混合",
  "current_net_value": "2.3567",
  "daily_change_rate": "1.50",
  "weekly_trend": "上升",
  "monthly_trend": "平稳",
  "risk_level": "R3",
  "risk_analysis": "该基金风险等级为R3，适合平衡型投资者",
  "investment_advice": "建议继续持有"
}
```

## 7. 消息中心模块

### 7.1 获取消息列表
- **接口地址**: `GET /api/notifications/`
- **功能描述**: 获取消息列表
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | page | integer | 否 | 页码，默认为1 |
  | per_page | integer | 否 | 每页数量，默认为20，最大100 |
  | type | string | 否 | 消息类型筛选 |
  | is_read | boolean | 否 | 是否已读筛选 |

- **返回数据结构示例**:
```json
{
  "items": [
    {
      "id": "notification-uuid-string",
      "title": "基金净值更新提醒",
      "content": "华夏成长混合基金净值更新至2.3567",
      "notification_type": "market_update",
      "is_read": false,
      "related_fund_code": "000001",
      "related_transaction_id": null,
      "created_at": "2023-10-01T10:00:00Z",
      "read_at": null
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1,
  "per_page": 20,
  "has_next": false,
  "has_prev": false
}
```

### 7.2 获取消息详情
- **接口地址**: `GET /api/notifications/{notification_id}`
- **功能描述**: 获取消息详情
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | notification_id | string | 是 | 消息ID |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "id": "notification-uuid-string",
  "title": "基金净值更新提醒",
  "content": "华夏成长混合基金净值更新至2.3567",
  "notification_type": "market_update",
  "is_read": false,
  "related_fund_code": "000001",
  "related_transaction_id": null,
  "created_at": "2023-10-01T10:00:00Z",
  "read_at": null
}
```

### 7.3 删除消息
- **接口地址**: `DELETE /api/notifications/{notification_id}`
- **功能描述**: 删除消息
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | notification_id | string | 是 | 消息ID |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "message": "消息已删除"
}
```

### 7.4 标记消息为已读
- **接口地址**: `PUT /api/notifications/{notification_id}/read`
- **功能描述**: 标记消息为已读
- **路径参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | notification_id | string | 是 | 消息ID |

- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "id": "notification-uuid-string",
  "title": "基金净值更新提醒",
  "content": "华夏成长混合基金净值更新至2.3567",
  "notification_type": "market_update",
  "is_read": true,
  "related_fund_code": "000001",
  "related_transaction_id": null,
  "created_at": "2023-10-01T10:00:00Z",
  "read_at": "2023-10-01T10:30:00Z"
}
```

### 7.5 标记所有消息为已读
- **接口地址**: `PUT /api/notifications/read-all`
- **功能描述**: 标记所有消息为已读
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "message": "已标记 5 条消息为已读"
}
```

## 8. 设置模块

### 8.1 获取用户设置
- **接口地址**: `GET /api/settings/`
- **功能描述**: 获取用户设置
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "id": "setting-uuid-string",
  "user_id": "user-uuid-string",
  "notification_enabled": true,
  "market_alert_enabled": true,
  "theme_setting": "light",
  "font_size": "medium",
  "created_at": "2023-10-01T10:00:00Z",
  "updated_at": "2023-10-01T10:00:00Z"
}
```

### 8.2 更新用户设置
- **接口地址**: `PUT /api/settings/`
- **功能描述**: 更新用户设置
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | notification_enabled | boolean | 否 | 是否启用通知 |
  | market_alert_enabled | boolean | 否 | 是否启用市场提醒 |
  | theme_setting | string | 否 | 主题设置 |
  | font_size | string | 否 | 字体大小 |

- **返回数据结构示例**:
```json
{
  "id": "setting-uuid-string",
  "user_id": "user-uuid-string",
  "notification_enabled": false,
  "market_alert_enabled": true,
  "theme_setting": "dark",
  "font_size": "large",
  "created_at": "2023-10-01T10:00:00Z",
  "updated_at": "2023-10-01T11:00:00Z"
}
```

### 8.3 清理缓存
- **接口地址**: `POST /api/settings/clear-cache`
- **功能描述**: 清理缓存
- **请求头**: 
  | 参数名 | 类型 | 是否必填 | 描述 |
  |--------|------|----------|------|
  | Authorization | string | 是 | Bearer token |

- **返回数据结构示例**:
```json
{
  "message": "缓存清理成功",
  "cache_cleared": true,
  "size_cleared": "2.50 MB"
}
```

### 8.4 获取应用信息
- **接口地址**: `GET /api/settings/about`
- **功能描述**: 获取应用信息
- **返回数据结构示例**:
```json
{
  "app_name": "场外基金投资辅助工具",
  "version": "1.0.0",
  "description": "一个帮助用户管理和分析基金投资的移动应用",
  "developer": "场外基金投资辅助工具开发团队",
  "contact": "support@example.com"
}
```

## 通用错误响应格式

所有错误响应都遵循以下格式：
```json
{
  "message": "错误信息"
}
```

## 认证说明

- 大多数API需要JWT认证，请求头中需要包含`Authorization: Bearer <token>`
- 需要认证的接口如果未提供有效的认证令牌，将返回401状态码
- 需要认证的接口如果提供了无效的认证令牌，将返回401状态码