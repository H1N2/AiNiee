import json
import time
import os
from typing import Optional, Callable
from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo
from volcengine.base.Service import Service

class VolcTranslator():
    def __init__(
        self,
        api_key: str,
        src_lang: str,
        dst_lang: str
    ):
        # 解析API密钥（格式：access_key:secret_key）
        self.api_key = api_key
        self.src_lang = src_lang
        self.dst_lang = dst_lang
        try:
            self.access_key, self.secret_key = api_key.split(':')
        except ValueError:
            raise ValueError("火山引擎API密钥格式错误。正确格式：access_key:secret_key")
        
        service_info = ServiceInfo(
            'translate.volcengineapi.com',
            {"Content-Type": "application/json"},
            Credentials(self.access_key, self.secret_key,'translate', 'cn-north-1'),
            5,
            5
        )
        
        k_query = {
        'Action': 'TranslateText',
        'Version': '2020-06-01'
        }
        k_api_info = {
            'translate': ApiInfo('POST', '/', k_query, {}, {})
        }
        self.service = Service(service_info, k_api_info)
        
        # 语言代码映射
        self.lang_map = {
            "zh": "zh",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
            "zh-Hant": "zh-Hant",
            "fr": "fr",
            "es": "es",
            "de": "de",
            "it": "it",
            "pt": "pt",
            "ru": "ru"
        }


    def translate_text(self, text: str) -> str:
        if not text.strip():
            return text
        
        try:
            # 解析输入的JSON字符串
            try:
                text_dict = json.loads(text)
                # 收集所有需要翻译的文本
                texts_to_translate = list(text_dict.values())
                keys = list(text_dict.keys())
            except json.JSONDecodeError:
                # 如果不是JSON，直接使用原文本
                text_dict = None
                texts_to_translate = [text]

            body = {
                "SourceLanguage": self.lang_map.get(self.src_lang, "auto"),
                "TargetLanguage": self.lang_map.get(self.dst_lang, "zh"),
                "TextList": texts_to_translate
            }
            
            response = self.service.json('translate', {}, json.dumps(body))
            response = json.loads(response)

            # 检查响应是否为字符串（可能是错误信息）
            if isinstance(response, str):
                raise ValueError(f"API返回错误: {response}")
            
            # 检查响应格式
            if not isinstance(response, dict):
                raise ValueError(f"API返回格式错误: {response}")
            
            if "TranslationList" not in response or not response["TranslationList"]:
                raise ValueError(f"翻译失败: {response.get('Message', '未知错误')}")
            
            translations = [item["Translation"] for item in response["TranslationList"]]
            
            # 如果输入是JSON格式，返回相同格式的JSON
            if text_dict is not None:
                result = dict(zip(keys, translations))
                return json.dumps(result, ensure_ascii=False, indent=4)
            
            return translations[0]
            
        except Exception as e:
            raise ValueError(f"火山引擎API调用失败: {str(e)}") 