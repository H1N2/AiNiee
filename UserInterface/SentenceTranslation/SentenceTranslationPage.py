import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QFrame, QProgressBar
from qfluentwidgets import (
    FluentIcon, PushButton, TextEdit, BodyLabel, StrongBodyLabel,
    CardWidget, ScrollArea, ComboBox, MessageBox
)

from Base.Base import Base
from ModuleFolders.TaskConfig.TaskConfig import TaskConfig
from ModuleFolders.LLMRequester.LLMRequester import LLMRequester
from ModuleFolders.PromptBuilder.PromptBuilder import PromptBuilder
from ModuleFolders.ResponseExtractor.ResponseExtractor import ResponseExtractor
from ModuleFolders.Cache.CacheManager import CacheManager
from ModuleFolders.RequestLimiter.RequestLimiter import RequestLimiter


class SentenceTranslationWorker(QThread):
    """语句翻译工作线程"""
    translation_completed = pyqtSignal(str)  # 翻译完成信号
    translation_error = pyqtSignal(str)      # 翻译错误信号
    progress = pyqtSignal(str)               # 进度信号
    
    def __init__(self, text, source_lang, target_lang):
        super().__init__()
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.cache_manager = CacheManager()
        self.request_limiter = RequestLimiter()
        
        # 语言映射字典
        self.lang_mapping = {
            "中文": "Chinese",
            "英文": "English", 
            "日文": "Japanese",
            "韩文": "Korean",
            "法文": "French",
            "德文": "German",
            "西班牙文": "Spanish",
            "俄文": "Russian"
        }
        
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
            
            # 获取源语言和目标语言
            source_language = self.lang_mapping.get(self.source_lang, "Japanese")
            target_language = self.lang_mapping.get(self.target_lang, "Chinese")
            
            # 构建提示词
            system_prompt = f"You are a professional translator. Translate the following text from {source_language} to {target_language}. Only return the translation, no explanations."
            
            # 使用PromptBuilder构建更完整的提示词
            try:
                prompt_builder = PromptBuilder(config)
                enhanced_prompt = prompt_builder.build_translation_prompt(
                    source_text=self.text,
                    source_lang=source_language,
                    target_lang=target_language,
                    translation_type='sentence'
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


class SentenceTranslationPage(ScrollArea, Base):
    """独立的语句翻译页面"""
    
    def __init__(self, object_name: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(object_name)
        
        # 初始化UI
        self.init_ui()
        
        # 翻译工作线程
        self.translation_worker = None
        
    def init_ui(self):
        """初始化用户界面"""
        # 主布局
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # 页面标题
        title_label = StrongBodyLabel(self.tra("语句翻译"))
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        self.main_layout.addWidget(title_label)
        
        # 说明文本
        description_label = BodyLabel(self.tra("在此页面可以直接翻译单个语句或段落，无需上传文件"))
        description_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        self.main_layout.addWidget(description_label)
        
        # 语言选择卡片
        self.lang_card = CardWidget()
        lang_layout = QVBoxLayout(self.lang_card)
        
        lang_title = StrongBodyLabel(self.tra("语言设置："))
        lang_layout.addWidget(lang_title)
        
        # 语言选择区域
        lang_selection_layout = QHBoxLayout()
        
        # 源语言选择
        lang_selection_layout.addWidget(BodyLabel(self.tra("源语言:")))
        self.source_lang_combo = ComboBox()
        self.source_lang_combo.addItems(["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"])
        self.source_lang_combo.setCurrentText("日文")
        lang_selection_layout.addWidget(self.source_lang_combo)
        
        lang_selection_layout.addWidget(BodyLabel("→"))
        
        # 目标语言选择
        lang_selection_layout.addWidget(BodyLabel(self.tra("目标语言:")))
        self.target_lang_combo = ComboBox()
        self.target_lang_combo.addItems(["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"])
        self.target_lang_combo.setCurrentText("中文")
        lang_selection_layout.addWidget(self.target_lang_combo)
        
        lang_selection_layout.addStretch()
        lang_layout.addLayout(lang_selection_layout)
        
        self.main_layout.addWidget(self.lang_card)
        
        # 输入区域卡片
        self.input_card = CardWidget()
        input_layout = QVBoxLayout(self.input_card)
        
        # 输入标签
        input_label = StrongBodyLabel(self.tra("输入要翻译的文本："))
        input_layout.addWidget(input_label)
        
        # 输入文本框
        self.input_text = TextEdit()
        self.input_text.setPlaceholderText(self.tra("请输入要翻译的语句或段落..."))
        self.input_text.setMinimumHeight(150)
        input_layout.addWidget(self.input_text)
        
        self.main_layout.addWidget(self.input_card)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 翻译按钮
        self.translate_button = PushButton(FluentIcon.PLAY, self.tra("开始翻译"))
        self.translate_button.clicked.connect(self.start_translation)
        button_layout.addWidget(self.translate_button)
        
        # 清空按钮
        self.clear_button = PushButton(FluentIcon.DELETE, self.tra("清空内容"))
        self.clear_button.clicked.connect(self.clear_content)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        self.main_layout.addLayout(button_layout)
        
        # 输出区域卡片
        self.output_card = CardWidget()
        output_layout = QVBoxLayout(self.output_card)
        
        # 输出标签
        output_label = StrongBodyLabel(self.tra("翻译结果："))
        output_layout.addWidget(output_label)
        
        # 输出文本框
        self.output_text = TextEdit()
        self.output_text.setPlaceholderText(self.tra("翻译结果将显示在这里..."))
        self.output_text.setMinimumHeight(150)
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        
        self.main_layout.addWidget(self.output_card)
        
        # 进度和状态区域
        self.progress_card = CardWidget()
        progress_layout = QVBoxLayout(self.progress_card)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = BodyLabel("")
        self.status_label.setStyleSheet("color: #666;")
        progress_layout.addWidget(self.status_label)
        
        self.main_layout.addWidget(self.progress_card)
        
        # 设置滚动区域
        self.setWidget(self.main_widget)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
    def start_translation(self):
        """开始翻译"""
        source_text = self.input_text.toPlainText().strip()
        
        if not source_text:
            MessageBox(self.tra("警告"), self.tra("请先输入要翻译的文本"), self).exec()
            return
            
        source_lang = self.source_lang_combo.currentText()
        target_lang = self.target_lang_combo.currentText()
        
        if source_lang == target_lang:
            MessageBox(self.tra("警告"), self.tra("源语言和目标语言不能相同"), self).exec()
            return
            
        # 禁用翻译按钮，显示进度
        self.translate_button.setEnabled(False)
        self.translate_button.setText(self.tra("翻译中..."))
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.status_label.setText(self.tra("正在翻译..."))
        
        # 清空输出区域
        self.output_text.clear()
        
        # 创建并启动翻译工作线程
        self.translation_worker = SentenceTranslationWorker(source_text, source_lang, target_lang)
        self.translation_worker.translation_completed.connect(self.on_translation_completed)
        self.translation_worker.translation_error.connect(self.on_translation_error)
        self.translation_worker.progress.connect(self.on_translation_progress)
        self.translation_worker.start()
        
    def on_translation_completed(self, translated_text):
        """翻译完成回调"""
        self.output_text.setPlainText(translated_text)
        self.translate_button.setEnabled(True)
        self.translate_button.setText(self.tra("开始翻译"))
        self.progress_bar.setVisible(False)
        self.status_label.setText(self.tra("翻译完成"))
        
    def on_translation_error(self, error_message):
        """翻译错误回调"""
        self.output_text.setPlainText(f"{self.tra('翻译失败：')}{error_message}")
        self.translate_button.setEnabled(True)
        self.translate_button.setText(self.tra("开始翻译"))
        self.progress_bar.setVisible(False)
        self.status_label.setText(self.tra("翻译失败"))
        
    def on_translation_progress(self, progress_msg):
        """翻译进度回调"""
        self.status_label.setText(progress_msg)
        
    def clear_content(self):
        """清空输入和输出内容"""
        self.input_text.clear()
        self.output_text.clear()