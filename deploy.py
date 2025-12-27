#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部署脚本
用于初始化数据库和启动应用
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def install_dependencies():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        sys.exit(1)


def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    try:
        # 导入并运行数据库初始化脚本
        import init_db_standalone
        init_db_standalone.init_database()
        print("✓ 数据库初始化完成")
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        sys.exit(1)


def run_app():
    """运行应用"""
    print("正在启动应用...")
    try:
        from run import app
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"✗ 应用启动失败: {e}")
        sys.exit(1)


def run_tests():
    """运行测试"""
    print("正在运行测试...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        print("✓ 所有测试通过")
    except subprocess.CalledProcessError as e:
        print(f"✗ 测试失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='场外基金投资辅助工具部署脚本')
    parser.add_argument('action', choices=['install', 'init', 'run', 'test', 'deploy'], 
                        help='执行的操作: install(安装依赖), init(初始化数据库), run(运行应用), test(运行测试), deploy(完整部署)')
    
    args = parser.parse_args()
    
    # 切换到脚本所在目录
    os.chdir(Path(__file__).parent)
    
    if args.action == 'install':
        install_dependencies()
    elif args.action == 'init':
        init_database()
    elif args.action == 'run':
        run_app()
    elif args.action == 'test':
        run_tests()
    elif args.action == 'deploy':
        print("开始完整部署...")
        install_dependencies()
        init_database()
        print("\n✓ 完整部署完成！")
        print("要启动应用，请运行: python deploy.py run")


if __name__ == "__main__":
    main()