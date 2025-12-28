# 项目结构说明

## 项目整体结构

```
flask-fund-app/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models/              # 数据模型
│   │   ├── __init__.py
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
│   │   ├── settings.py      # 设置接口
│   │   └── home.py          # 首页接口
│   └── utils/               # 工具函数
├── migrations/              # 数据库迁移
├── tests/                   # 测试文件
├── instance/                # 实例文件（数据库等）
├── requirements.txt         # 依赖包
├── config.py                # 配置文件
├── run.py                   # 启动文件
├── init_db.py               # 数据库初始化
├── init_db_standalone.py    # 独立数据库初始化
├── deploy.py                # 部署脚本
├── README.md                # 项目说明
├── API接口文档.md            # API接口文档
├── PROJECT_SUMMARY.md       # 项目总结
└── PROJECT_STRUCTURE.md     # 项目结构说明
```

## 核心模块说明

### 1. app/ 目录

- `__init__.py`: 应用工厂函数，初始化Flask应用和各种扩展
- `models/`: 数据模型定义，包含所有数据库表的模型类
- `api/`: API接口实现，每个模块一个文件
- `utils/`: 工具函数，包含通用的辅助函数

### 2. models/ 模块

- `user.py`: 用户、用户资料、用户设置模型
- `fund.py`: 基金、基金市场数据、基金分组、自选关系模型
- `transaction.py`: 持仓、交易记录模型
- `notification.py`: 通知模型

### 3. api/ 模块

- `auth.py`: 用户认证相关接口（注册、登录、资料管理等）
- `fund.py`: 基金数据相关接口（查询、搜索、详情等）
- `favorite.py`: 自选功能相关接口（增删改查、分组管理等）
- `market.py`: 市场行情相关接口（基金列表、板块、资讯等）
- `transaction.py`: 交易功能相关接口（持仓、买卖、记录等）
- `notification.py`: 消息中心相关接口（消息列表、状态管理等）
- `settings.py`: 设置相关接口（用户设置、缓存清理等）
- `home.py`: 首页相关接口（概览数据等）

## 配置文件

- `config.py`: 项目配置，包含数据库、JWT等配置项
- `run.py`: 应用启动文件
- `init_db_standalone.py`: 独立的数据库初始化脚本

## 文档文件

- `README.md`: 项目说明文档
- `API接口文档.md`: 详细的API接口文档
- `PROJECT_SUMMARY.md`: 项目总结文档
- `PROJECT_STRUCTURE.md`: 项目结构说明文档

## 测试文件

- `tests/`: 包含所有测试文件

## 依赖管理

- `requirements.txt`: 项目依赖包列表