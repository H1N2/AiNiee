import hashlib
import hmac
import requests
import hashlib
import hmac
import time
import json
import uuid
from urllib.parse import quote
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ModuleFolders.LLMRequester.LLMRequester import LLMRequester
from ModuleFolders.TaskConfig.TaskConfig import TaskConfig
from ModuleFolders.TaskConfig.TaskType import TaskType


class TranslationAPIManager:
    """翻译API管理器"""

    def __init__(self, config):
        self.config = config

    def update_config(self, config):
        """更新配置"""
        self.config.update(config)

    def test_api_connection(self, api_type):
        """测试单个API连接"""
        test_text = "Hello"
        source_lang = "en"
        target_lang = "zh-cn"

        if api_type == "baidu":
            return self.test_baidu_api(test_text, source_lang, target_lang)
        elif api_type == "volcano":
            return self.test_volcano_api(test_text, source_lang, target_lang)
        elif api_type == "tencent":
            return self.test_tencent_api(test_text, source_lang, target_lang)
        else:
            return {"success": False, "error": "不支持的API类型"}

    def test_all_apis(self, text, source_lang, target_lang):
        """测试所有启用的API"""
        results = {}

        # 测试百度翻译API
        if self.config.get("baidu_api_enabled", False):
            results["百度翻译"] = self.test_baidu_api(text, source_lang, target_lang)

        # 测试火山翻译API
        if self.config.get("volcano_api_enabled", False):
            results["火山翻译"] = self.test_volcano_api(text, source_lang, target_lang)

        # 测试腾讯翻译API
        if self.config.get("tencent_api_enabled", False):
            results["腾讯翻译"] = self.test_tencent_api(text, source_lang, target_lang)

        # 如果有多个结果，进行AI质量对比
        if len([r for r in results.values() if r["success"]]) > 1:
            results["ai_comparison"] = self.compare_translations_with_ai(text, results)

        return results

    def test_baidu_api(self, text, source_lang, target_lang):
        """测试百度翻译API"""
        try:
            app_id = self.config.get("baidu_app_id", "")
            secret_key = self.config.get("baidu_secret_key", "")

            if not app_id or not secret_key:
                return {"success": False, "error": "百度API配置不完整"}

            # 百度翻译API参数
            salt = str(int(time.time()))
            sign_str = app_id + text + salt + secret_key
            sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

            # 语言代码转换
            from_lang = self._convert_lang_code_for_baidu(source_lang)
            to_lang = self._convert_lang_code_for_baidu(target_lang)

            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': app_id,
                'salt': salt,
                'sign': sign
            }

            response = requests.get(
                'https://fanyi-api.baidu.com/api/trans/vip/translate',
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP错误: {response.status_code}"}

            result = response.json()

            if 'trans_result' in result and len(result['trans_result']) > 0:
                translation = result['trans_result'][0]['dst']
                return {"success": True, "translation": translation}
            elif 'error_code' in result:
                error_codes = {
                    '52001': 'APP ID不存在',
                    '52002': '签名错误',
                    '52003': '访问频率受限',
                    '54000': '必填参数为空',
                    '54001': '签名错误',
                    '54003': '访问频率受限',
                    '54004': '账户余额不足',
                    '54005': '长query请求频繁',
                    '58000': '客户端IP非法',
                    '58001': '译文语言方向不支持',
                    '58002': '服务当前已关闭',
                    '90107': '认证未通过或未生效'
                }
                error_code = result['error_code']
                error_msg = error_codes.get(error_code, f'未知错误码: {error_code}')
                return {"success": False, "error": error_msg}
            else:
                return {"success": False, "error": "返回结果格式异常"}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "网络连接错误"}
        except json.JSONDecodeError:
            return {"success": False, "error": "响应JSON解析失败"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}

    def _test_volcano_api_legacy(self, access_key, secret_key, text, source_lang, target_lang):
        """使用旧版火山引擎SDK的备选方法"""
        try:
            from volcengine.ApiInfo import ApiInfo
            from volcengine.Credentials import Credentials
            from volcengine.ServiceInfo import ServiceInfo
            from volcengine.base.Service import Service

            # 创建服务配置
            service_info = ServiceInfo(
                'translate.volcengineapi.com',
                {"Content-Type": "application/json"},
                Credentials(access_key, secret_key, 'translate', 'cn-north-1'),
                5,
                5
            )

            # 创建API信息
            k_query = {
                'Action': 'TranslateText',
                'Version': '2020-06-01'
            }
            k_api_info = {
                'translate': ApiInfo('POST', '/', k_query, {}, {})
            }

            # 创建服务实例
            service = Service(service_info, k_api_info)

            # 语言代码转换
            source_language = self._convert_lang_code_for_volcano(source_lang)
            target_language = self._convert_lang_code_for_volcano(target_lang)

            # 构建请求体
            body = {
                "SourceLanguage": source_language,
                "TargetLanguage": target_language,
                "TextList": [text]
            }

            # 调用API
            response = service.json('translate', {}, json.dumps(body))
            response_data = json.loads(response)

            # 检查响应格式
            if isinstance(response_data, str):
                return {"success": False, "error": f"API返回错误: {response_data}"}

            if not isinstance(response_data, dict):
                return {"success": False, "error": f"API返回格式错误: {response_data}"}

            if "TranslationList" not in response_data or not response_data["TranslationList"]:
                error_msg = response_data.get('Message', '未知错误')
                return {"success": False, "error": f"翻译失败: {error_msg}"}

            # 提取翻译结果
            translation = response_data["TranslationList"][0]["Translation"]
            return {"success": True, "translation": translation}

        except ImportError:
            return {"success": False, "error": "火山引擎SDK未安装。请运行: pip install volcengine 或 pip install volcengine-python-sdk"}
        except Exception as e:
            return {"success": False, "error": f"旧版SDK调用失败: {str(e)}"}

    def test_volcano_api(self, text, source_lang, target_lang):
        """测试火山翻译API（使用新版SDK）"""
        try:
            # 获取API密钥配置
            api_key = self.config.get("volcano_api_key", "")
            access_key = self.config.get("volcano_access_key", "")
            secret_key_encoded = self.config.get("volcano_secret_key", "")
            secret_key = secret_key_encoded
            # 优先使用组合格式的API密钥
##            if api_key and ':' in api_key:
##                try:
##                    access_key, secret_key = api_key.split(':', 1)
##                except ValueError:
##                    return {"success": False, "error": "火山引擎API密钥格式错误。正确格式：access_key:secret_key"}
            #elif access_key and secret_key_encoded:
                # 解码secret key
                #import base64
                #try:
                #    secret_key = base64.b64decode(secret_key_encoded).decode('utf-8')
                #    print('Decode scret')
                #except Exception:
                #    secret_key = secret_key_encoded  # 如果解码失败，使用原始值
##            else:
##                return {"success": False, "error": "火山API配置不完整。请提供volcano_api_key（格式：access_key:secret_key）或分别提供access_key和secret_key"}

            # 尝试使用新版火山引擎SDK（参考ok_test_volcaon.py）
            try:
                import volcenginesdkcore
                import volcenginesdktranslate20250301
                from volcenginesdkcore.rest import ApiException

                # 创建配置
                configuration = volcenginesdkcore.Configuration()
                configuration.ak = access_key
                configuration.sk = secret_key
                configuration.region = "cn-beijing"

                # 设置默认配置
                volcenginesdkcore.Configuration.set_default(configuration)

                # 创建API实例
                api_instance = volcenginesdktranslate20250301.TRANSLATE20250301Api()

                # 语言代码转换
                source_language = self._convert_lang_code_for_volcano(source_lang)
                target_language = self._convert_lang_code_for_volcano(target_lang)

                # 创建翻译请求
                translate_text_request = volcenginesdktranslate20250301.TranslateTextRequest(
                    target_language=target_language,
                    source_language=source_language,
                    text_list=[text]
                )

                # 调用API
                response = api_instance.translate_text(translate_text_request)

                # 检查响应
                if hasattr(response, 'translation_list') and response.translation_list:
                    translation = response.translation_list[0].translation
                    return {"success": True, "translation": translation}
                else:
                    return {"success": False, "error": "翻译响应格式异常"}

            except ImportError as import_error:
                # 如果新版SDK不可用，尝试使用旧版SDK
                return self._test_volcano_api_legacy(access_key, secret_key, text, source_lang, target_lang)
            except ApiException as api_error:
                return {"success": False, "error": f"API调用异常: {str(api_error)}"}
            except Exception as sdk_error:
                return {"success": False, "error": f"SDK调用失败: {str(sdk_error)}"}

        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}

    def _test_volcano_api_rest(self, access_key, secret_key, text, source_lang, target_lang):
        """火山翻译API REST方式（备用）"""
        try:
            # 简化的REST API调用
            url = "https://translate.volcengineapi.com/api/v1/translate/text"

            # 语言代码转换
            source_language = self._convert_lang_code_for_volcano(source_lang)
            target_language = self._convert_lang_code_for_volcano(target_lang)

            # 请求体
            payload = {
                "SourceLanguage": source_language,
                "TargetLanguage": target_language,
                "Text": text
            }

            # 基本请求头
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'AiNiee-Translation-Debug/1.0'
            }

            # 发送请求（不使用签名，仅用于测试连通性）
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code == 401:
                return {"success": False, "error": "认证失败，需要正确的API密钥和签名。建议使用SDK方式。"}
            elif response.status_code == 403:
                return {"success": False, "error": "访问被拒绝，请检查API权限。"}
            elif response.status_code != 200:
                return {"success": False, "error": f"HTTP错误: {response.status_code}"}

            result = response.json()

            if result.get("Code") == 0 and "Data" in result:
                translation = result["Data"].get("TargetText", "")
                return {"success": True, "translation": translation}
            else:
                error_msg = result.get("Message", "未知错误")
                return {"success": False, "error": f"API错误: {error_msg}"}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "网络连接错误"}
        except Exception as e:
            return {"success": False, "error": f"REST API调用失败: {str(e)}"}

    def test_tencent_api(self, text, source_lang, target_lang):
        """测试腾讯翻译API - 使用腾讯云SDK"""
        try:
            # 解析API密钥
            secret_id = self.config.get("tencent_secret_id", "")
            secret_key = self.config.get("tencent_secret_key", "")
            
            # 处理组合格式的密钥
            if "|" in secret_id:
                parts = secret_id.split("|")
                if len(parts) >= 2:
                    secret_id = parts[0]
                    secret_key = parts[1]
            
            # 解码base64格式的密钥
            try:
                import base64
                secret_id = base64.b64decode(secret_id).decode('utf-8')
                secret_key = base64.b64decode(secret_key).decode('utf-8')
            except:
                pass  # 如果不是base64格式，保持原样
            
            if not secret_id or not secret_key or secret_id == "test_id":
                return {"success": False, "error": "腾讯API配置不完整，请提供有效的SecretId和SecretKey"}
            
            # 尝试使用新版腾讯云SDK
            try:
                from tencentcloud.common import credential
                from tencentcloud.common.profile.client_profile import ClientProfile
                from tencentcloud.common.profile.http_profile import HttpProfile
                from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
                from tencentcloud.tmt.v20180321 import tmt_client, models
                
                # 语言代码转换
                source_language = self._convert_lang_code_for_tencent(source_lang)
                target_language = self._convert_lang_code_for_tencent(target_lang)
                
                # 创建认证对象
                cred = credential.Credential(secret_id, secret_key)
                
                # 创建HTTP配置
                httpProfile = HttpProfile()
                httpProfile.endpoint = "tmt.tencentcloudapi.com"
                
                # 创建客户端配置
                clientProfile = ClientProfile()
                clientProfile.httpProfile = httpProfile
                
                # 创建客户端
                client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)
                
                # 创建请求对象
                req = models.TextTranslateRequest()
                req.SourceText = text
                req.Source = source_language
                req.Target = target_language
                req.ProjectId = 0
                
                # 发送请求
                resp = client.TextTranslate(req)
                
                return {"success": True, "translation": resp.TargetText}
                
            except ImportError:
                # 如果新版SDK不可用，使用旧版手动签名方法
                return self._test_tencent_api_legacy(secret_id, secret_key, text, source_lang, target_lang)
            except TencentCloudSDKException as err:
                return {"success": False, "error": f"腾讯云SDK错误: {str(err)}"}
            except Exception as e:
                return {"success": False, "error": f"SDK调用失败: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "error": f"腾讯翻译API调用失败: {str(e)}"}

    def _test_tencent_api_legacy(self, secret_id, secret_key, text, source_lang, target_lang):
        """腾讯翻译API旧版实现 - 手动签名方式"""
        try:
            # 腾讯翻译API参数
            host = "tmt.tencentcloudapi.com"
            service = "tmt"
            version = "2018-03-21"
            action = "TextTranslate"
            region = "ap-beijing"

            # 语言代码转换
            source_language = self._convert_lang_code_for_tencent(source_lang)
            target_language = self._convert_lang_code_for_tencent(target_lang)

            # 请求体
            payload = {
                "SourceText": text,
                "Source": source_language,
                "Target": target_language,
                "ProjectId": 0
            }

            payload_json = json.dumps(payload, separators=(',', ':'))

            # 时间戳
            timestamp = int(time.time())
            date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')

            # 构建签名
            algorithm = 'TC3-HMAC-SHA256'

            # 构建规范请求
            method = 'POST'
            uri = '/'
            query_string = ''

            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Host': host,
                'X-TC-Action': action,
                'X-TC-Timestamp': str(timestamp),
                'X-TC-Version': version,
                'X-TC-Region': region
            }

            # 构建签名字符串
            signed_headers = ';'.join([k.lower() for k in sorted(headers.keys())])
            canonical_headers = '\n'.join([f"{k.lower()}:{v}" for k, v in sorted(headers.items())]) + '\n'

            payload_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()

            canonical_request = f"{method}\n{uri}\n{query_string}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

            # 创建签名字符串
            credential_scope = f"{date}/{service}/tc3_request"
            string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

            # 计算签名
            def sign(key, msg):
                return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

            secret_date = sign(('TC3' + secret_key).encode('utf-8'), date)
            secret_service = sign(secret_date, service)
            secret_signing = sign(secret_service, 'tc3_request')
            signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

            # 构建授权头
            authorization = f"{algorithm} Credential={secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

            headers['Authorization'] = authorization

            # 发送请求
            url = f"https://{host}/"
            response = requests.post(url, headers=headers, data=payload_json, timeout=10)

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP错误: {response.status_code}"}

            result = response.json()

            if 'Response' in result:
                if 'TargetText' in result['Response']:
                    translation = result['Response']['TargetText']
                    return {"success": True, "translation": translation}
                elif 'Error' in result['Response']:
                    error_msg = result['Response']['Error'].get('Message', '未知错误')
                    error_code = result['Response']['Error'].get('Code', '')
                    return {"success": False, "error": f"{error_code}: {error_msg}"}

            return {"success": False, "error": "返回结果格式异常"}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "网络连接错误"}
        except json.JSONDecodeError:
            return {"success": False, "error": "响应JSON解析失败"}
        except Exception as e:
            return {"success": False, "error": f"旧版API调用失败: {str(e)}"}

    def compare_translations_with_ai(self, original_text, translation_results):
        """使用AI对比翻译质量"""
        try:
            # 构建对比提示
            successful_translations = {k: v for k, v in translation_results.items()
                                     if v.get("success", False)}

            if len(successful_translations) < 2:
                return "需要至少两个成功的翻译结果才能进行对比"

            # 尝试使用AI模型进行深度分析
            ai_analysis = self._get_ai_quality_analysis(original_text, successful_translations)
            if ai_analysis:
                return ai_analysis

            # 如果AI分析失败，回退到基础指标分析
            analysis = f"原文：{original_text}\n\n翻译结果对比分析：\n\n"

            # 简单的质量分析（基于长度、字符多样性等基础指标）
            for api_name, result in successful_translations.items():
                translation = result['translation']

                # 基础质量指标
                length_score = min(100, (len(translation) / len(original_text)) * 100) if len(original_text) > 0 else 0
                char_diversity = len(set(translation)) / len(translation) if len(translation) > 0 else 0

                # 简单的质量评估
                if length_score > 80 and char_diversity > 0.3:
                    quality = "良好"
                elif length_score > 60 and char_diversity > 0.2:
                    quality = "一般"
                else:
                    quality = "需要改进"

                analysis += f"{api_name}：\n"
                analysis += f"  翻译内容：{translation}\n"
                analysis += f"  长度比例：{length_score:.1f}%\n"
                analysis += f"  字符多样性：{char_diversity:.2f}\n"
                analysis += f"  质量评估：{quality}\n\n"

            # 添加总结
            best_api = max(successful_translations.keys(),
                          key=lambda k: len(successful_translations[k]['translation']))
            analysis += f"推荐：{best_api} 的翻译结果相对较好\n"
            analysis += "\n注意：这是基于基础指标的简单分析。AI深度分析功能当前不可用。"

            return analysis

        except Exception as e:
            return f"AI对比失败：{str(e)}"

    def _convert_lang_code_for_baidu(self, lang_code):
        """转换语言代码为百度翻译API格式"""
        lang_map = {
            "auto": "auto",
            "en": "en",
            "zh": "zh",
            "zh-cn": "zh",
            "zh-tw": "cht",
            "ja": "jp",
            "ko": "kor"
        }
        return lang_map.get(lang_code, "auto")

    def _convert_lang_code_for_volcano(self, lang_code):
        """转换语言代码为火山翻译API格式"""
        lang_map = {
            "auto": "auto",
            "en": "en",
            "zh": "zh",
            "zh-cn": "zh",
            "zh-tw": "zh-Hant",
            "ja": "ja",
            "ko": "ko"
        }
        return lang_map.get(lang_code, "auto")

    def _convert_lang_code_for_tencent(self, lang_code):
        """转换语言代码为腾讯翻译API格式"""
        lang_map = {
            "auto": "auto",
            "en": "en",
            "zh": "zh",
            "zh-cn": "zh",
            "zh-tw": "zh-TW",
            "ja": "ja",
            "ko": "ko"
        }
        return lang_map.get(lang_code, "auto")

    def _get_ai_quality_analysis(self, original_text, translation_results):
         """使用AI模型进行翻译质量分析"""
         try:
             # 检查是否有可用的AI配置
             config = TaskConfig()
             config.initialize()
             
             # 检查是否配置了翻译接口
             if not hasattr(config, 'api_settings'):
                 print("[DEBUG] TaskConfig没有api_settings属性")
                 return None
                 
             translate_platform = config.api_settings.get('translate')
             if not translate_platform:
                 print("[DEBUG] 未配置翻译接口平台")
                 return None
                 
             if not hasattr(config, 'platforms') or translate_platform not in config.platforms:
                 print(f"[DEBUG] 翻译平台 {translate_platform} 不存在于platforms配置中")
                 return None
                 
             # 准备翻译配置
             config.prepare_for_translation(TaskType.TRANSLATION)
             
             # 构建AI分析提示
             prompt = f"""请分析以下翻译结果的质量，从准确性、流畅性、自然度等方面进行评价：

原文：{original_text}

翻译结果：
"""
             
             for api_name, result in translation_results.items():
                 if result.get("success", False):
                     prompt += f"{api_name}：{result['translation']}\n"
             
             prompt += "\n请为每个翻译结果打分（1-10分）并说明理由，最后推荐最佳翻译。"
             
             # 构建消息列表
             messages = [
                 {
                     "role": "user",
                     "content": prompt
                 }
             ]
             
             # 获取平台配置
             platform_config = config.get_platform_configuration("translationReq")
             print(f"[DEBUG] 平台配置获取成功: {platform_config.get('target_platform', 'unknown')}")
             
             # 使用LLMRequester进行分析
             llm_requester = LLMRequester()
             skip, response_think, response_content, prompt_tokens, completion_tokens = llm_requester.sent_request(
                 messages=messages,
                 system_prompt="你是一个专业的翻译质量评估专家，请客观公正地分析翻译质量。",
                 platform_config=platform_config
             )
             
             print(f"[DEBUG] LLM请求结果: skip={skip}, response_content存在={bool(response_content)}")
             
             if not skip and response_content:
                 return f"AI质量分析：\n{response_content}"
             else:
                 print(f"[DEBUG] AI分析失败: skip={skip}, response_content={response_content}")
                 return None
                 
         except Exception as e:
             # 如果AI分析失败，返回详细错误信息用于调试
             print(f"[DEBUG] AI质量分析异常: {str(e)}")
             import traceback
             traceback.print_exc()
             return None