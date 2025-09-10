# AiNiee API 参考文档

## 核心API接口

### 文件访问器 (FileAccessor)

#### BaseReader
文件读取器基类，所有读取器都应继承此类。

```python
class BaseReader:
    def read_file(self, file_path: str) -> dict:
        """
        读取文件内容
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            dict: 标准化的文件数据格式
            {
                "file_type": "文件类型",
                "content": [
                    {
                        "id": "唯一标识",
                        "source": "原文",
                        "translation": "译文",
                        "context": "上下文信息"
                    }
                ]
            }
        """
        
    def is_supported_file(self, file_path: str) -> bool:
        """检查是否支持该文件格式"""
        
    def get_file_format(self) -> str:
        """返回支持的文件格式标识"""
```

#### BaseWriter
文件写入器基类。

```python
class BaseWriter:
    def write_file(self, data: dict, output_path: str) -> bool:
        """
        写入文件
        
        Args:
            data (dict): 标准化的文件数据
            output_path (str): 输出文件路径
            
        Returns:
            bool: 写入是否成功
        """
        
    def get_file_format(self) -> str:
        """返回支持的文件格式标识"""
```

### 大语言模型请求器 (LLMRequester)

#### BaseLLMRequester
LLM请求基类。

```python
class BaseLLMRequester:
    def make_request(self, messages: list, model: str = None, **kwargs) -> dict:
        """
        发送请求到LLM服务
        
        Args:
            messages (list): 消息列表
            model (str): 模型名称
            **kwargs: 其他参数
            
        Returns:
            dict: 响应数据
            {
                "success": bool,
                "content": str,
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                },
                "error": str  # 错误信息（如果有）
            }
        """
        
    def get_supported_models(self) -> list:
        """获取支持的模型列表"""
        
    def calculate_tokens(self, text: str) -> int:
        """计算文本token数量"""
```

#### OpenAIRequester
OpenAI API请求器。

```python
class OpenAIRequester(BaseLLMRequester):
    def __init__(self, api_key: str, base_url: str = None, proxy: str = None):
        """
        初始化OpenAI请求器
        
        Args:
            api_key (str): OpenAI API密钥
            base_url (str): 自定义API端点
            proxy (str): 代理设置
        """
```

#### ClaudeRequester
Anthropic Claude API请求器。

```python
class ClaudeRequester(BaseLLMRequester):
    def __init__(self, api_key: str, base_url: str = None):
        """
        初始化Claude请求器
        
        Args:
            api_key (str): Anthropic API密钥
            base_url (str): 自定义API端点
        """
```

### 任务执行器 (TaskExecutor)

#### TaskExecutor
主任务执行器，负责协调整个翻译流程。

```python
class TaskExecutor:
    def __init__(self, config: dict):
        """
        初始化任务执行器
        
        Args:
            config (dict): 任务配置
        """
        
    def execute_translation_task(self, input_path: str, output_path: str) -> dict:
        """
        执行翻译任务
        
        Args:
            input_path (str): 输入文件/目录路径
            output_path (str): 输出路径
            
        Returns:
            dict: 执行结果
            {
                "success": bool,
                "processed_files": int,
                "failed_files": int,
                "total_tokens": int,
                "elapsed_time": float,
                "errors": list
            }
        """
        
    def pause_task(self):
        """暂停任务"""
        
    def resume_task(self):
        """恢复任务"""
        
    def cancel_task(self):
        """取消任务"""
        
    def get_progress(self) -> dict:
        """
        获取任务进度
        
        Returns:
            dict: 进度信息
            {
                "current_file": str,
                "processed_count": int,
                "total_count": int,
                "progress_percentage": float,
                "estimated_time_remaining": float
            }
        """
```

### 文本处理器 (TextProcessor)

#### TextProcessor
文本预处理和后处理。

```python
class TextProcessor:
    def preprocess_text(self, text: str, context: dict = None) -> str:
        """
        文本预处理
        
        Args:
            text (str): 原始文本
            context (dict): 上下文信息
            
        Returns:
            str: 处理后的文本
        """
        
    def postprocess_text(self, text: str, context: dict = None) -> str:
        """
        文本后处理
        
        Args:
            text (str): 翻译后的文本
            context (dict): 上下文信息
            
        Returns:
            str: 处理后的文本
        """
        
    def extract_terms(self, text: str) -> list:
        """
        提取术语
        
        Args:
            text (str): 文本内容
            
        Returns:
            list: 术语列表
        """
        
    def apply_glossary(self, text: str, glossary: dict) -> str:
        """
        应用术语表
        
        Args:
            text (str): 文本内容
            glossary (dict): 术语表
            
        Returns:
            str: 应用术语表后的文本
        """
```

### 提示词构建器 (PromptBuilder)

#### PromptBuilder
构建AI翻译提示词。

```python
class PromptBuilder:
    def build_translation_prompt(self, 
                                source_text: str,
                                target_language: str,
                                context: dict = None,
                                style_guide: str = None) -> str:
        """
        构建翻译提示词
        
        Args:
            source_text (str): 源文本
            target_language (str): 目标语言
            context (dict): 上下文信息
            style_guide (str): 翻译风格指南
            
        Returns:
            str: 构建的提示词
        """
        
    def build_polishing_prompt(self, text: str, requirements: str = None) -> str:
        """
        构建润色提示词
        
        Args:
            text (str): 待润色文本
            requirements (str): 润色要求
            
        Returns:
            str: 构建的提示词
        """
        
    def build_term_extraction_prompt(self, text: str, domain: str = None) -> str:
        """
        构建术语提取提示词
        
        Args:
            text (str): 源文本
            domain (str): 专业领域
            
        Returns:
            str: 构建的提示词
        """
```

### 响应处理器

#### ResponseExtractor
从AI响应中提取翻译内容。

```python
class ResponseExtractor:
    def extract_translation(self, response: str, format_type: str = "auto") -> str:
        """
        提取翻译内容
        
        Args:
            response (str): AI响应内容
            format_type (str): 响应格式类型
            
        Returns:
            str: 提取的翻译内容
        """
        
    def extract_terms(self, response: str) -> dict:
        """
        提取术语对照
        
        Args:
            response (str): AI响应内容
            
        Returns:
            dict: 术语对照字典
        """
```

#### ResponseChecker
检查AI响应质量。

```python
class ResponseChecker:
    def check_translation_quality(self, 
                                 source: str, 
                                 translation: str, 
                                 context: dict = None) -> dict:
        """
        检查翻译质量
        
        Args:
            source (str): 源文本
            translation (str): 翻译文本
            context (dict): 上下文信息
            
        Returns:
            dict: 质量检查结果
            {
                "score": float,  # 0-1分数
                "issues": list,  # 发现的问题
                "suggestions": list  # 改进建议
            }
        """
        
    def check_format_consistency(self, source: str, translation: str) -> bool:
        """检查格式一致性"""
        
    def check_length_ratio(self, source: str, translation: str) -> float:
        """检查长度比例"""
```

### 请求限制器 (RequestLimiter)

#### RequestLimiter
控制API请求频率。

```python
class RequestLimiter:
    def __init__(self, 
                 requests_per_minute: int = 60,
                 requests_per_day: int = 1000):
        """
        初始化请求限制器
        
        Args:
            requests_per_minute (int): 每分钟请求数限制
            requests_per_day (int): 每天请求数限制
        """
        
    def can_make_request(self) -> bool:
        """检查是否可以发送请求"""
        
    def wait_if_needed(self):
        """如需要则等待"""
        
    def record_request(self):
        """记录请求"""
        
    def get_remaining_quota(self) -> dict:
        """
        获取剩余配额
        
        Returns:
            dict: 配额信息
            {
                "minute_remaining": int,
                "day_remaining": int,
                "reset_time": datetime
            }
        """
```

### 插件系统

#### PluginBase
插件基类。

```python
class PluginBase:
    def __init__(self):
        self.plugin_name = ""
        self.plugin_version = ""
        self.plugin_author = ""
        self.plugin_description = ""
        
    def on_text_preprocess(self, text: str, context: dict) -> str:
        """文本预处理事件"""
        return text
        
    def on_text_postprocess(self, text: str, context: dict) -> str:
        """文本后处理事件"""
        return text
        
    def on_translation_start(self, task_info: dict):
        """翻译开始事件"""
        pass
        
    def on_translation_complete(self, result: dict):
        """翻译完成事件"""
        pass
        
    def on_error_occurred(self, error: Exception, context: dict):
        """错误发生事件"""
        pass
        
    def get_priority(self) -> int:
        """获取插件优先级"""
        return 100  # 默认优先级
```

#### PluginManager
插件管理器。

```python
class PluginManager:
    def load_plugins(self, plugin_dir: str):
        """加载插件目录中的所有插件"""
        
    def register_plugin(self, plugin: PluginBase):
        """注册插件"""
        
    def unregister_plugin(self, plugin_name: str):
        """注销插件"""
        
    def get_loaded_plugins(self) -> list:
        """获取已加载的插件列表"""
        
    def trigger_event(self, event_name: str, *args, **kwargs):
        """触发插件事件"""
```

## 配置管理API

### ConfigManager
配置管理器。

```python
class ConfigManager:
    def load_config(self, config_path: str = None) -> dict:
        """加载配置文件"""
        
    def save_config(self, config: dict, config_path: str = None):
        """保存配置文件"""
        
    def get_setting(self, key: str, default=None):
        """获取配置项"""
        
    def set_setting(self, key: str, value):
        """设置配置项"""
        
    def reset_to_default(self):
        """重置为默认配置"""
        
    def export_config(self, export_path: str):
        """导出配置"""
        
    def import_config(self, import_path: str):
        """导入配置"""
```

## 事件系统

### EventBus
事件总线，用于组件间通信。

```python
class EventBus:
    def subscribe(self, event_type: str, callback: callable):
        """订阅事件"""
        
    def unsubscribe(self, event_type: str, callback: callable):
        """取消订阅"""
        
    def publish(self, event_type: str, data: dict = None):
        """发布事件"""
        
    def clear_subscribers(self, event_type: str = None):
        """清除订阅者"""
```

### 事件类型
```python
class EventTypes:
    TRANSLATION_STARTED = "translation_started"
    TRANSLATION_PROGRESS = "translation_progress"
    TRANSLATION_COMPLETED = "translation_completed"
    TRANSLATION_FAILED = "translation_failed"
    TRANSLATION_PAUSED = "translation_paused"
    TRANSLATION_RESUMED = "translation_resumed"
    FILE_PROCESSED = "file_processed"
    ERROR_OCCURRED = "error_occurred"
```

## 工具函数

### 文本工具
```python
def clean_text(text: str) -> str:
    """清理文本，去除多余空白字符"""
    
def detect_language(text: str) -> str:
    """检测文本语言"""
    
def split_sentences(text: str, language: str = "auto") -> list:
    """分割句子"""
    
def merge_sentences(sentences: list) -> str:
    """合并句子"""
    
def calculate_text_similarity(text1: str, text2: str) -> float:
    """计算文本相似度"""
```

### 文件工具
```python
def get_file_type(file_path: str) -> str:
    """获取文件类型"""
    
def is_text_file(file_path: str) -> bool:
    """检查是否为文本文件"""
    
def get_file_encoding(file_path: str) -> str:
    """检测文件编码"""
    
def backup_file(file_path: str, backup_dir: str = None) -> str:
    """备份文件"""
    
def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> list:
    """查找文件"""
```

### 网络工具
```python
def test_api_connection(api_url: str, timeout: int = 10) -> bool:
    """测试API连接"""
    
def download_file(url: str, save_path: str, progress_callback: callable = None) -> bool:
    """下载文件"""
    
def get_proxy_settings() -> dict:
    """获取代理设置"""
```

## 异常类

```python
class AiNieeException(Exception):
    """AiNiee基础异常类"""
    pass

class FileReadError(AiNieeException):
    """文件读取异常"""
    pass

class FileWriteError(AiNieeException):
    """文件写入异常"""
    pass

class TranslationError(AiNieeException):
    """翻译异常"""
    pass

class APIError(AiNieeException):
    """API调用异常"""
    pass

class ConfigError(AiNieeException):
    """配置异常"""
    pass

class PluginError(AiNieeException):
    """插件异常"""
    pass
```

## 使用示例

### 基本翻译流程
```python
# 初始化配置
config = ConfigManager().load_config()

# 创建任务执行器
executor = TaskExecutor(config)

# 执行翻译任务
result = executor.execute_translation_task(
    input_path="input/game_files/",
    output_path="output/"
)

print(f"翻译完成: {result}")
```

### 自定义插件使用
```python
# 创建自定义插件
class MyCustomPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.plugin_name = "CustomTextFilter"
        
    def on_text_preprocess(self, text: str, context: dict) -> str:
        # 自定义预处理逻辑
        return text.upper()

# 注册插件
plugin_manager = PluginManager()
plugin_manager.register_plugin(MyCustomPlugin())
```

### 批量处理示例
```python
import asyncio

async def batch_translate():
    files = ["file1.txt", "file2.txt", "file3.txt"]
    tasks = []
    
    for file_path in files:
        task = translate_file_async(file_path)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# 运行批量翻译
results = asyncio.run(batch_translate())
```