#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于运行所有测试用例
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_auth import *
from test_fund import *
from test_favorite import *
from test_market import *
from test_transaction import *
from test_home import *


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestLoader().discover('.', pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 根据测试结果设置退出码
    sys.exit(0 if result.wasSuccessful() else 1)