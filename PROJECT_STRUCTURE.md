# 项目结构说明

## 整体结构
```
flask-fund-app/
├── app/
│   ├── __init__.py              # 应用工厂
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── fund.py              # 基金相关模型
│   │   ├── notification.py      # 通知相关模型
│   │   ├── transaction.py       # 交易相关模型
│   │   └── user.py              # 用户相关模型
│   ├── api/                     # API接口
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证接口
│   │   ├── favorite.py          # 自选接口
│   │   ├── fund.py              # 基金接口
│   │   ├── home.py              # 首页接口
│   │   ├── market.py            # 市场接口
│   │   ├── notification.py      # 通知接口
│   │   ├── settings.py          # 设置接口
│   │   └── transaction.py       # 交易接口
│   └── utils/                   # 工具函数
├── tests/                       # 测试文件
│   ├── __init__.py
│   ├── conftest.py              # 测试配置
│   ├── run_tests.py             # 测试运行脚本
│   ├── test_auth.py             # 认证测试
│   ├── test_favorite.py         # 自选测试
│   ├── test_fund.py             # 基金测试
│   ├── test_home.py             # 首页测试
│   ├── test_market.py           # 市场测试
│   └── test_transaction.py      # 交易测试
├── instance/                    # 实例文件（数据库等）
│   └── fund_app.db              # SQLite数据库文件
├── config.py                    # 配置文件
├── deploy.py                    # 部署脚本
├── init_db.py                   # 数据库初始化脚本
├── init_db_standalone.py        # 独立数据库初始化脚本
├── run.py                       # 应用启动脚本
├── requirements.txt             # 依赖包列表
├── pytest.ini                   # pytest配置
├── README.md                    # 项目说明
├── API_USAGE.md                 # API使用说明
├── PROJECT_SUMMARY.md           # 项目总结
├── PROJECT_STRUCTURE.md         # 项目结构说明
└── test_api.py                  # 旧版API测试脚本
```

## 详细说明

### app/ - 应用主目录
- `__init__.py`: 应用工厂函数，初始化Flask应用和扩展
- `models/`: 数据模型定义
  - `user.py`: 用户相关模型（User, UserProfile, UserSetting）
  - `fund.py`: 基金相关模型（Fund, FundMarketData, FundGroup, FavoriteFundRelation）
  - `transaction.py`: 交易相关模型（Holding, Transaction）
  - `notification.py`: 通知相关模型（Notification）
- `api/`: API接口定义
  - `auth.py`: 认证相关的API端点
  - `fund.py`: 基金数据相关的API端点
  - `favorite.py`: 自选功能相关的API端点
  - `market.py`: 市场行情相关的API端点
  - `transaction.py`: 交易功能相关的API端点
  - `notification.py`: 通知相关的API端点
  - `settings.py`: 设置相关的API端点
  - `home.py`: 首页功能相关的API端点
- `utils/`: 工具函数（预留目录）

### tests/ - 测试目录
- `conftest.py`: pytest配置，定义测试用的fixture
- `run_tests.py`: 统一的测试运行脚本
- `test_*.py`: 各模块的测试文件

### 根目录文件
- `config.py`: 应用配置，包含开发、测试、生产环境配置
- `deploy.py`: 部署脚本，集成安装依赖、初始化数据库、运行应用等功能
- `init_db.py`: 数据库初始化脚本（集成在应用中）
- `init_db_standalone.py`: 独立的数据库初始化脚本
- `run.py`: 应用启动脚本
- `requirements.txt`: 项目依赖包列表
- `pytest.ini`: pytest配置文件

### 配置文件
- `instance/`: Flask实例目录，包含运行时文件如数据库
- `config.py`: 包含不同环境的配置类

## 依赖关系

### 核心依赖
- Flask: Web框架
- Flask-SQLAlchemy: ORM
- Flask-RESTX: API框架
- Flask-JWT-Extended: JWT认证
- Werkzeug: WSGI工具库
- requests: HTTP请求库（测试用）

### 开发依赖
- pytest: 测试框架
- python-dotenv: 环境变量管理

## 部署流程

1. 安装依赖: `pip install -r requirements.txt`
2. 初始化数据库: `python init_db_standalone.py`
3. 启动应用: `python run.py`
4. 访问API文档: `http://127.0.0.1:5000/docs/`

## 测试流程

1. 运行所有测试: `pytest`
2. 运行特定测试: `python -m pytest tests/test_auth.py -v`
3. 运行测试脚本: `python tests/run_tests.py`

## API访问

- 基础URL: `http://127.0.0.1:5000`
- API文档: `http://127.0.0.1:5000/docs/`
- 认证后API需要在请求头中添加: `Authorization: Bearer <token>`