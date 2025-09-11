#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_api_status():
    """检查翻译API状态和配置"""
    print("=== 翻译API状态检查 ===\n")
    
    try:
        from UserInterface.TranslationAPIDebug.TranslationAPIManager import TranslationAPIManager
        
        # 使用提供的火山API密钥进行测试
        config = {
            "baidu_api_enabled": True,
            "baidu_app_id": "demo_app_id",
            "baidu_secret_key": "demo_secret_key",
            "volcano_api_enabled": True,
            "volcano_access_key": "AKLTODc1YTIzYjg0MmIxNDc1NTljZTJiYWZjNGIyYjM0ZjM",
            "volcano_secret_key": "TlRrek1UZzJZV0kzT1dGaU5HRXpOemxoTldKbVpURXpNemhtT1RWa09XTQ==",
            "tencent_api_enabled": True,
            "tencent_secret_id": "demo_secret_id",
            "tencent_secret_key": "demo_secret_key"
        }
        
        manager = TranslationAPIManager(config)
        
        print("1. 检查SDK依赖")
        
        # 检查火山翻译SDK
        try:
            import volcengine_translate
            print("   [OK] volcengine-translate SDK 已安装")
        except ImportError:
            try:
                import volcengine
                print("   [OK] volcengine SDK 已安装")
            except ImportError:
                print("   [WARN] 火山翻译SDK未安装，建议运行:")
                print("         pip install volcengine-translate")
        
        # 检查其他依赖
        try:
            import requests
            print("   [OK] requests 库已安装")
        except ImportError:
            print("   [ERROR] requests 库未安装")
        
        print("\n2. 测试API连接")
        
        apis = [
            ("百度翻译", "baidu"),
            ("火山翻译", "volcano"), 
            ("腾讯翻译", "tencent")
        ]
        
        for api_name, api_type in apis:
            try:
                result = manager.test_api_connection(api_type)
                if result["success"]:
                    print(f"   [OK] {api_name}: 连接成功")
                else:
                    error = result["error"]
                    if "配置不完整" in error:
                        print(f"   [WARN] {api_name}: 需要有效的API密钥")
                    elif "SDK未安装" in error:
                        print(f"   [WARN] {api_name}: {error}")
                    elif "频率受限" in error:
                        print(f"   [WARN] {api_name}: API调用频率受限（正常）")
                    else:
                        print(f"   [ERROR] {api_name}: {error[:50]}...")
            except Exception as e:
                print(f"   [ERROR] {api_name}: 测试异常 - {str(e)[:30]}...")
        
        print("\n3. 配置建议")
        print("   百度翻译API:")
        print("   - 申请地址: https://fanyi-api.baidu.com/")
        print("   - 需要: APP ID 和 密钥")
        
        print("\n   火山翻译API:")
        print("   - 申请地址: https://www.volcengine.cn/product/machine-translation")
        print("   - 需要: Access Key 和 Secret Key")
        print("   - 建议安装SDK: pip install volcengine-translate")
        
        print("\n   腾讯翻译API:")
        print("   - 申请地址: https://cloud.tencent.com/product/tmt")
        print("   - 需要: Secret ID 和 Secret Key")
        
        print("\n[INFO] 翻译API调试功能已准备就绪")
        print("用户可以在界面中配置有效的API密钥进行测试")
        
    except Exception as e:
        print(f"检查失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_api_status()