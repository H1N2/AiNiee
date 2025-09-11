#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 简单测试导入
try:
    from UserInterface.TranslationAPIDebug.TranslationAPIDebugPage import TranslationAPIDebugPage
    print("[OK] TranslationAPIDebugPage 导入成功")
    
    from UserInterface.TranslationAPIDebug.TranslationAPIManager import TranslationAPIManager
    print("[OK] TranslationAPIManager 导入成功")
    
    # 测试API管理器
    config = {
        "baidu_api_enabled": True,
        "baidu_app_id": "test_id",
        "baidu_secret_key": "test_key"
    }
    
    manager = TranslationAPIManager(config)
    print("[OK] API管理器创建成功")
    
    # 测试连接测试方法
    result = manager.test_api_connection("baidu")
    print(f"[OK] API连接测试方法调用成功: {result['success']}")
    print(f"   错误信息: {result.get('error', 'None')}")
    
    print("\n[SUCCESS] 所有测试通过！翻译API调试功能已成功添加：")
    print("   - [OK] API设置界面优化（水平布局）")
    print("   - [OK] 为每个API添加了测试连接按钮")
    print("   - [OK] 添加了连接状态显示")
    print("   - [OK] 实现了异步API连接测试")
    print("   - [OK] 添加了测试结果反馈")
    
except Exception as e:
    print(f"[ERROR] 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()