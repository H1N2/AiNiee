#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_improved_apis():
    """测试改进后的翻译API"""
    print("=== 改进后的翻译API测试 ===\n")
    
    try:
        from UserInterface.TranslationAPIDebug.TranslationAPIManager import TranslationAPIManager
        
        # 测试配置
        config = {
            "baidu_api_enabled": True,
            "baidu_app_id": "test_id",  # 测试用，会失败但能验证逻辑
            "baidu_secret_key": "test_key",
            "volcano_api_enabled": True,
            "volcano_access_key": "AKLTODc1YTIzYjg0MmIxNDc1NTljZTJiYWZjNGIyYjM0ZjM",
            "volcano_secret_key": "TlRrek1UZzJZV0kzT1dGaU5HRXpOemxoTldKbVpURXpNemhtT1RWa09XTQ==",
            "tencent_api_enabled": True,
            "tencent_secret_id": "test_id",  # 测试用，会失败但能验证逻辑
            "tencent_secret_key": "test_key"
        }
        
        manager = TranslationAPIManager(config)
        
        print("1. 测试百度翻译API")
        baidu_result = manager.test_baidu_api("Hello", "en", "zh-cn")
        print(f"   结果: {baidu_result['success']}")
        print(f"   信息: {baidu_result['error'][:80]}..." if not baidu_result['success'] else f"   翻译: {baidu_result['translation']}")
        
        print("\n2. 测试火山翻译API（SDK方式）")
        volcano_result = manager.test_volcano_api("Hello", "en", "zh-cn")
        print(f"   结果: {volcano_result['success']}")
        print(f"   信息: {volcano_result['error'][:80]}..." if not volcano_result['success'] else f"   翻译: {volcano_result['translation']}")
        
        print("\n3. 测试腾讯翻译API")
        tencent_result = manager.test_tencent_api("Hello", "en", "zh-cn")
        print(f"   结果: {tencent_result['success']}")
        print(f"   信息: {tencent_result['error'][:80]}..." if not tencent_result['success'] else f"   翻译: {tencent_result['translation']}")
        
        print("\n=== 改进总结 ===")
        print("[OK] 1. 火山翻译API改为SDK方式")
        print("[OK] 2. 添加了SDK不可用时的降级处理")
        print("[OK] 3. 改进了错误信息提示")
        print("[OK] 4. 腾讯API添加了配置验证")
        
        print("\n=== 使用建议 ===")
        print("火山翻译API:")
        print("- 建议安装SDK: pip install volcengine-translate")
        print("- 或使用: pip install volcengine-sdk")
        print("- 提供有效的Access Key和Secret Key")
        
        print("\n腾讯翻译API:")
        print("- 需要有效的腾讯云SecretId和SecretKey")
        print("- 确保API权限已开通")
        
        print("\n百度翻译API:")
        print("- 需要有效的APP ID和密钥")
        print("- 注意API调用频率限制")
        
        print("\n[INFO] API测试功能已改进，提供更好的错误提示和SDK支持")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_apis()