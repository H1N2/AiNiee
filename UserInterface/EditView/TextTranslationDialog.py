import time
import threading
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QProgressBar
from qfluentwidgets import MessageBox, ComboBox, PushButton, TextEdit, BodyLabel, Dialog

from Base import Base
from ModuleFolders.TaskConfig.TaskConfig import TaskConfig
from ModuleFolders.LLMRequester.LLMRequester import LLMRequester
from ModuleFolders.PromptBuilder.PromptBuilder import PromptBuilder
from ModuleFolders.ResponseExtractor.ResponseExtractor import ResponseExtractor
from ModuleFolders.Cache.CacheManager import CacheManager
from ModuleFolders.RequestLimiter.RequestLimiter import RequestLimiter


class TranslationWorkerThread(QThread):
    """翻译工作线程"""
    translation_completed = pyqtSignal(str)  # 翻译完成信号
    translation_error = pyqtSignal(str)      # 翻译错误信号
    progress = pyqtSignal(str)               # 进度信号
    
    def __init__(self, text, source_lang, target_lang, translation_type):
        super().__init__()
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translation_type = translation_type  # 'sentence' 或 'paragraph'
        self.cache_manager = CacheManager()
        self.request_limiter = RequestLimiter()
        
    def run(self):
        """执行翻译任务"""
        try:
            self.progress.emit("正在初始化翻译配置...")
            
            # 检查缓存
            cache_key = f"{self.source_lang}_{self.target_lang}_{hash(self.text)}"
            cached_result = self.cache_manager.get_cache(cache_key)
            if cached_result:
                self.progress.emit("从缓存中获取翻译结果...")
                self.translation_completed.emit(cached_result)
                return
            
            # 请求限制检查
            if not self.request_limiter.can_make_request():
                self.translation_error.emit("请求过于频繁，请稍后再试")
                return
            
            # 加载配置
            config = TaskConfig()
            config.load_config()
            config.prepare_for_translation("TRANSLATION")
            
            self.progress.emit("正在构建翻译请求...")
            
            # 构建提示词
            if self.translation_type == 'sentence':
                system_prompt = f"You are a professional translator. Translate the following sentence from {self.source_lang} to {self.target_lang}. Only return the translation, no explanations."
            else:
                system_prompt = f"You are a professional translator. Translate the following paragraph from {self.source_lang} to {self.target_lang}. Maintain the original formatting and structure. Only return the translation, no explanations."
            
            # 使用PromptBuilder构建更完整的提示词
            try:
                prompt_builder = PromptBuilder(config)
                enhanced_prompt = prompt_builder.build_translation_prompt(
                    source_text=self.text,
                    source_lang=self.source_lang,
                    target_lang=self.target_lang,
                    translation_type=self.translation_type
                )
            except:
                enhanced_prompt = None
            
            # 构建消息
            messages = [
                {"role": "system", "content": enhanced_prompt or system_prompt},
                {"role": "user", "content": self.text}
            ]
            
            self.progress.emit("正在发送翻译请求...")
            
            # 发送请求
            requester = LLMRequester(config)
            response = requester.send_request(messages)
            
            if response and response.get('choices'):
                # 使用ResponseExtractor提取和处理响应
                try:
                    extractor = ResponseExtractor(config)
                    translated_text = extractor.extract_translation_result(response)
                except:
                    # 如果ResponseExtractor失败，使用简单提取
                    translated_text = response['choices'][0]['message']['content'].strip()
                
                if translated_text:
                    # 缓存结果
                    self.cache_manager.set_cache(cache_key, translated_text)
                    self.translation_completed.emit(translated_text)
                else:
                    self.translation_error.emit("翻译结果提取失败")
            else:
                self.translation_error.emit("翻译请求失败，未收到有效响应")
                
        except Exception as e:
            self.translation_error.emit(f"翻译过程中发生错误: {str(e)}")


class TextTranslationDialog(Dialog):
    """文本翻译对话框"""
    
    def __init__(self, translation_type, parent=None):
        super().__init__(parent)
        self.translation_type = translation_type  # 'sentence' 或 'paragraph'
        self.worker_thread = None
        
        self.setWindowTitle(f"{'语句' if translation_type == 'sentence' else '段落'}翻译")
        self.resize(600, 500)
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        
        # 语言选择区域
        lang_layout = QHBoxLayout()
        
        # 源语言选择
        lang_layout.addWidget(BodyLabel("源语言:"))
        self.source_lang_combo = ComboBox()
        self.source_lang_combo.addItems(["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"])
        self.source_lang_combo.setCurrentText("日文")
        lang_layout.addWidget(self.source_lang_combo)
        
        lang_layout.addWidget(BodyLabel("→"))
        
        # 目标语言选择
        lang_layout.addWidget(BodyLabel("目标语言:"))
        self.target_lang_combo = ComboBox()
        self.target_lang_combo.addItems(["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"])
        self.target_lang_combo.setCurrentText("中文")
        lang_layout.addWidget(self.target_lang_combo)
        
        layout.addLayout(lang_layout)
        
        # 输入文本区域
        layout.addWidget(BodyLabel(f"请输入要翻译的{'语句' if self.translation_type == 'sentence' else '段落'}:"))
        self.input_text = TextEdit()
        self.input_text.setPlaceholderText(f"在此输入{'语句' if self.translation_type == 'sentence' else '段落'}...")
        layout.addWidget(self.input_text)
        
        # 翻译结果区域
        layout.addWidget(BodyLabel("翻译结果:"))
        self.output_text = TextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("翻译结果将显示在这里...")
        layout.addWidget(self.output_text)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = BodyLabel("")
        layout.addWidget(self.status_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.translate_btn = PushButton("开始翻译")
        self.translate_btn.clicked.connect(self.start_translation)
        button_layout.addWidget(self.translate_btn)
        
        self.clear_btn = PushButton("清空")
        self.clear_btn.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_btn)
        
        self.close_btn = PushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def connect_signals(self):
        """连接信号"""
        pass
    
    def start_translation(self):
        """开始翻译"""
        text = self.input_text.toPlainText().strip()
        if not text:
            MessageBox("警告", "请输入要翻译的文本", self).exec()
            return
        
        source_lang = self.source_lang_combo.currentText()
        target_lang = self.target_lang_combo.currentText()
        
        if source_lang == target_lang:
            MessageBox("警告", "源语言和目标语言不能相同", self).exec()
            return
        
        # 禁用按钮，显示进度
        self.translate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.status_label.setText("正在翻译...")
        
        # 创建并启动工作线程
        self.worker_thread = TranslationWorkerThread(
            text, source_lang, target_lang, self.translation_type
        )
        self.worker_thread.translation_completed.connect(self.on_translation_completed)
        self.worker_thread.translation_error.connect(self.on_translation_error)
        self.worker_thread.progress.connect(self.on_translation_progress)
        self.worker_thread.start()
    
    def on_translation_completed(self, result):
        """翻译完成回调"""
        self.output_text.setPlainText(result)
        self.translate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("翻译完成")
        
        # 显示成功消息
        MessageBox(
            "成功",
            "翻译完成！",
            self
        ).exec()
    
    def on_translation_progress(self, progress_msg):
        """翻译进度回调"""
        self.status_label.setText(progress_msg)
    
    def on_translation_error(self, error_msg):
        """翻译错误回调"""
        self.translate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("翻译失败")
        
        # 显示错误消息
        MessageBox(
            "错误",
            f"翻译失败：{error_msg}",
            self
        ).exec()
    
    def clear_text(self):
        """清空文本"""
        self.input_text.clear()
        self.output_text.clear()
        self.status_label.setText("")