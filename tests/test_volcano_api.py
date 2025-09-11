#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from UserInterface.TranslationAPIDebug.TranslationAPIManager import TranslationAPIManager

def test_volcano_api():
    """测试火山翻译API"""
    print("开始测试火山翻译API...")
    
    # 使用提供的密钥
    config = {
        "volcano_api_enabled": True,
        "volcano_access_key": "AKLTODc1YTIzYjg0MmIxNDc1NTljZTJiYWZjNGIyYjM0ZjM",
        "volcano_secret_key": "TlRrek1UZzJZV0kzT1dGaU5HRXpOemxoTldKbVpURXpNemhtT1RWa09XTQ=="
    }
    
    manager = TranslationAPIManager(config)
    
    # 测试连接
    print("测试API连接中...")
    result = manager.test_api_connection("volcano")
    
    print(f"测试结果: {result}")
    
    if result["success"]:
        print("[SUCCESS] 火山翻译API连接成功!")
        print(f"翻译结果: {result.get('translation', 'N/A')}")
    else:
        print(f"[ERROR] 火山翻译API连接失败: {result['error']}")
        
        # 进一步调试
        print("\n开始详细调试...")
        test_result = manager.test_volcano_api("Hello", "en", "zh-cn")
        print(f"详细测试结果: {test_result}")

if __name__ == "__main__":
    test_volcano_api()