# 场外基金投资辅助工具 - Flask+SQLite后端开发计划

## 项目概述

基于需求文档，这是一个场外基金投资辅助工具，包含首页、自选、市场、交易、我的等核心功能模块。后端将使用Flask框架配合SQLite数据库实现。

## 技术栈

- **后端框架**: Flask 2.x
- **数据库**: SQLite 3
- **数据库ORM**: SQLAlchemy
- **API文档**: Flask-RESTX
- **用户认证**: Flask-JWT-Extended
- **数据验证**: Marshmallow
- **文件上传**: Flask-Uploads (用于OCR功能)

## 数据库设计

### 核心数据表设计

1. **用户表 (users)**
   - 用户基本信息、认证信息

2. **用户资料表 (user_profiles)**
   - 用户详细资料、风险评估等

3. **基金基础信息表 (funds)**
   - 基金代码、名称、类型等基础信息

4. **基金行情表 (fund_market_data)**
   - 基金净值、涨跌幅等实时数据

5. **用户自选关系表 (favorite_fund_relations)**
   - 用户自选基金关系

6. **基金分组表 (fund_groups)**
   - 用户自选分组信息

7. **持仓表 (holdings)**
   - 用户基金持仓信息

8. **交易记录表 (transactions)**
   - 用户交易历史记录

9. **消息通知表 (notifications)**
   - 系统消息、交易通知等

10. **用户设置表 (user_settings)**
    - 用户个性化设置

## API接口设计

### 1. 用户认证模块
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/refresh` - 刷新token
- `GET /api/auth/profile` - 获取用户资料
- `PUT /api/auth/profile` - 更新用户资料

### 2. 基金数据模块
- `GET /api/funds` - 获取基金列表（支持分页、筛选）
- `GET /api/funds/<code>` - 获取基金详情
- `GET /api/funds/<code>/history` - 获取基金历史净值
- `GET /api/funds/search` - 搜索基金
- `GET /api/sectors` - 获取板块数据
- `GET /api/sectors/<code>/prediction` - 获取板块预测

### 3. 自选功能模块
- `GET /api/favorites` - 获取用户自选基金列表
- `POST /api/favorites` - 添加自选基金
- `DELETE /api/favorites/<fund_code>` - 移除自选基金
- `GET /api/favorite-groups` - 获取自选分组列表
- `POST /api/favorite-groups` - 创建自选分组
- `PUT /api/favorite-groups/<group_id>` - 更新自选分组
- `DELETE /api/favorite-groups/<group_id>` - 删除自选分组

### 4. 市场行情模块
- `GET /api/market/funds` - 获取市场基金列表
- `GET /api/market/sectors` - 获取热门板块
- `GET /api/market/news` - 获取市场资讯
- `GET /api/market/index` - 获取主要指数

### 5. 交易功能模块
- `GET /api/holdings` - 获取持仓列表
- `GET /api/holdings/<fund_code>` - 获取单只基金持仓详情
- `POST /api/transactions/buy` - 买入基金
- `POST /api/transactions/sell` - 卖出基金
- `GET /api/transactions` - 获取交易记录
- `POST /api/holdings/import` - 导入持仓数据（OCR）

### 6. 消息中心模块
- `GET /api/notifications` - 获取消息列表
- `PUT /api/notifications/<id>/read` - 标记消息为已读
- `DELETE /api/notifications/<id>` - 删除消息
- `PUT /api/notifications/read-all` - 标记所有消息为已读

### 7. 设置模块
- `GET /api/settings` - 获取用户设置
- `PUT /api/settings` - 更新用户设置
- `POST /api/settings/clear-cache` - 清理缓存

## 开发计划

### 第一阶段 - 基础架构 (1-2周)

1. **项目初始化**
   - 创建Flask项目结构
   - 配置数据库连接（SQLite）
   - 集成SQLAlchemy ORM
   - 配置API文档（Flask-RESTX）

2. **用户认证系统**
   - 实现用户注册、登录、登出功能
   - 集成JWT认证
   - 实现密码加密存储
   - 创建用户资料管理功能

3. **数据库模型设计**
   - 设计并创建用户相关表
   - 设计并创建基金基础信息表
   - 实现数据模型关系

### 第二阶段 - 核心数据功能 (2-3周)

1. **基金数据API**
   - 实现基金列表查询接口
   - 实现基金详情查询接口
   - 实现基金搜索功能
   - 创建基金行情数据模型

2. **自选功能API**
   - 实现自选基金增删改查
   - 实现自选分组管理
   - 实现分组内基金管理

3. **数据导入导出**
   - 实现基础数据导入功能
   - 为OCR功能预留接口

### 第三阶段 - 交易与市场功能 (2-3周)

1. **市场行情API**
   - 实现市场基金列表
   - 实现板块数据展示
   - 实现市场资讯功能

2. **交易功能API**
   - 实现持仓管理功能
   - 实现交易记录功能
   - 实现买入卖出模拟功能

3. **首页数据API**
   - 实现首页资产概览
   - 实现个性化推荐接口

### 第四阶段 - 消息与设置功能 (1-2周)

1. **消息中心API**
   - 实现消息列表功能
   - 实现消息状态管理
   - 实现消息推送机制

2. **设置功能API**
   - 实现用户设置管理
   - 实现缓存清理功能
   - 实现个性化设置

### 第五阶段 - 测试与优化 (1-2周)

1. **单元测试**
   - 为各模块编写单元测试
   - 进行API功能测试
   - 进行数据库操作测试

2. **集成测试**
   - 进行端到端测试
   - 进行性能测试
   - 进行安全测试

3. **优化与部署**
   - 优化数据库查询性能
   - 优化API响应速度
   - 准备部署文档

## 项目结构

```
flask-fund-app/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── fund.py
│   │   ├── favorite.py
│   │   ├── transaction.py
│   │   └── notification.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── fund.py
│   │   ├── favorite.py
│   │   ├── market.py
│   │   ├── transaction.py
│   │   ├── notification.py
│   │   └── settings.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── validators.py
│   └── config.py
├── migrations/
├── tests/
├── requirements.txt
├── run.py
└── README.md
```

## 安全考虑

1. **认证与授权**
   - 使用JWT进行用户认证
   - 实现细粒度权限控制
   - 防止未授权访问

2. **数据安全**
   - 密码加密存储
   - SQL注入防护
   - XSS防护

3. **API安全**
   - 请求频率限制
   - 输入数据验证
   - 敏感信息脱敏

## 部署考虑

1. **生产环境配置**
   - 使用Gunicorn作为WSGI服务器
   - 配置Nginx反向代理
   - 配置HTTPS

2. **数据库备份**
   - 定期备份SQLite数据库
   - 配置自动备份脚本

## 实施建议

1. **分阶段开发**
   - 按照开发计划分阶段实现功能
   - 每个阶段完成后进行测试
   - 确保功能的稳定性和可靠性

2. **代码质量**
   - 遵循Flask最佳实践
   - 编写单元测试和集成测试
   - 使用代码格式化和静态分析工具

3. **文档维护**
   - 维护API文档
   - 记录数据库设计和变更
   - 编写部署和运维文档

这个开发计划涵盖了需求文档中的所有核心功能，采用分阶段开发方式，确保每个阶段都有可交付的功能。Flask+SQLite的组合适合初期开发，后期如有需要可以轻松迁移到更强大的数据库系统。