# 场外基金投资辅助工具 - Flask后端

这是一个基于Flask和SQLite的场外基金投资辅助工具后端项目，提供完整的基金投资管理功能。

## 项目结构

```
flask-fund-app/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models/              # 数据模型
│   │   ├── user.py          # 用户相关模型
│   │   ├── fund.py          # 基金相关模型
│   │   ├── transaction.py   # 交易相关模型
│   │   └── notification.py  # 通知相关模型
│   ├── api/                 # API接口
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证接口
│   │   ├── fund.py          # 基金接口
│   │   ├── favorite.py      # 自选接口
│   │   ├── market.py        # 市场接口
│   │   ├── transaction.py   # 交易接口
│   │   ├── notification.py  # 通知接口
│   │   └── settings.py      # 设置接口
│   ├── utils/               # 工具函数
│   └── config.py            # 配置文件
├── migrations/              # 数据库迁移
├── tests/                   # 测试文件
├── requirements.txt         # 依赖包
├── run.py                   # 启动文件
├── init_db.py               # 数据库初始化
└── README.md                # 项目说明
```

## 功能模块

### 1. 用户认证模块
- 用户注册、登录、登出
- JWT身份验证
- 用户资料管理

### 2. 基金数据模块
- 基金列表查询（支持分页、筛选）
- 基金详情查看
- 基金搜索功能
- 基金历史净值查询

### 3. 自选功能模块
- 自选基金增删改查
- 自选分组管理
- 分组内基金管理

### 4. 市场行情模块
- 市场基金列表
- 热门板块展示
- 市场资讯功能
- 主要指数查询

### 5. 交易功能模块
- 持仓管理功能
- 交易记录功能
- 买入/卖出模拟功能

### 6. 消息中心模块
- 消息列表功能
- 消息状态管理
- 消息推送机制

### 7. 设置模块
- 用户设置管理
- 缓存清理功能
- 个性化设置

## API文档

启动应用后，访问 http://127.0.0.1:5000/docs/ 查看交互式API文档。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db_standalone.py
```

### 3. 启动应用

```bash
python run.py
```

应用将在 http://127.0.0.1:5000 上运行

## 环境配置

项目使用以下环境变量（也可以在config.py中修改）：
- SECRET_KEY: 应用密钥
- JWT_SECRET_KEY: JWT密钥
- DATABASE_URL: 数据库连接地址（默认使用SQLite）

## 数据库设计

项目使用SQLite数据库，包含以下核心表：

- users: 用户信息表
- user_profiles: 用户资料表
- user_settings: 用户设置表
- funds: 基金基础信息表
- fund_market_data: 基金行情数据表
- fund_groups: 基金分组表
- favorite_fund_relations: 用户自选关系表
- holdings: 用户持仓表
- transactions: 交易记录表
- notifications: 消息通知表

## 安全考虑

- 使用JWT进行用户认证
- 密码加密存储
- SQL注入防护
- 敏感信息脱敏

## 测试

项目包含全面的测试套件，涵盖所有API端点：

### 运行测试

```bash
# 使用pytest运行测试
pip install pytest
pytest

# 或运行测试脚本
python -m pytest tests/run_tests.py
```

### 测试覆盖

测试套件包括：
- 用户认证测试
- 基金数据测试
- 自选功能测试
- 市场行情测试
- 交易功能测试
- 首页功能测试

## 部署建议

在生产环境中，建议：
- 使用Gunicorn作为WSGI服务器
- 配置Nginx反向代理
- 使用HTTPS
- 配置更强大的数据库（如PostgreSQL）
- 设置定期数据库备份