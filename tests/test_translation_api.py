#!/usr/bin/env python3
"""
测试翻译API调试模块
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from UserInterface.TranslationAPIDebug.TranslationAPIManager import TranslationAPIManager

def test_translation_api_manager():
    """测试翻译API管理器"""
    print("[TEST] 测试翻译API调试模块...")
    
    # 创建测试配置
    config = {
        "baidu_api_enabled": True,
        "baidu_app_id": "test_app_id",
        "baidu_secret_key": "test_secret_key",
        "volcano_api_enabled": False,
        "volcano_access_key": "",
        "volcano_secret_key": "",
        "tencent_api_enabled": False,
        "tencent_secret_id": "",
        "tencent_secret_key": "",
    }
    
    # 初始化API管理器
    api_manager = TranslationAPIManager(config)
    
    # 测试语言代码转换
    print("[OK] 测试语言代码转换...")
    baidu_lang = api_manager._convert_lang_code_for_baidu("zh-cn")
    assert baidu_lang == "zh", f"百度语言代码转换失败: {baidu_lang}"
    
    volcano_lang = api_manager._convert_lang_code_for_volcano("en")
    assert volcano_lang == "en", f"火山语言代码转换失败: {volcano_lang}"
    
    tencent_lang = api_manager._convert_lang_code_for_tencent("ja")
    assert tencent_lang == "ja", f"腾讯语言代码转换失败: {tencent_lang}"
    
    print("[OK] 语言代码转换测试通过")
    
    # 测试API调用（会失败，因为使用的是测试密钥）
    print("[TEST] 测试API调用...")
    test_text = "Hello, world!"
    results = api_manager.test_all_apis(test_text, "en", "zh-cn")
    
    print("[RESULT] API调用结果:")
    for api_name, result in results.items():
        status = "[SUCCESS]" if result["success"] else "[FAILED]"
        print(f"  {api_name}: {status}")
        if not result["success"]:
            print(f"    错误: {result['error']}")
        else:
            print(f"    翻译: {result['translation']}")
    
    print("[DONE] 翻译API调试模块测试完成！")

if __name__ == "__main__":
    test_translation_api_manager()