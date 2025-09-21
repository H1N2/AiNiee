from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QGroupBox, QScrollArea, QTextBrowser
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from qfluentwidgets import HorizontalSeparator, PillPushButton, MessageBox, InfoBar, InfoBarPosition, Pivot, qrouter, PushButton, FluentIcon

from Base.Base import Base
from Widget.ComboBoxCard import ComboBoxCard
from Widget.SwitchButtonCard import SwitchButtonCard
from Widget.LineEditCard import LineEditCard
from Widget.TextEditCard import TextEditCard

from .TranslationAPIManager import TranslationAPIManager


class TranslationTestThread(QThread):
    """翻译测试线程"""
    test_completed = pyqtSignal(dict)
    test_error = pyqtSignal(str)

    def __init__(self, api_manager, text, source_lang, target_lang):
        super().__init__()
        self.api_manager = api_manager
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang

    def run(self):
        try:
            results = self.api_manager.test_all_apis(self.text, self.source_lang, self.target_lang)
            self.test_completed.emit(results)
        except Exception as e:
            self.test_error.emit(str(e))


class APIConnectionTestThread(QThread):
    """API连接测试线程"""
    test_completed = pyqtSignal(str, dict)
    test_error = pyqtSignal(str, str)

    def __init__(self, api_manager, api_type):
        super().__init__()
        self.api_manager = api_manager
        self.api_type = api_type

    def run(self):
        try:
            result = self.api_manager.test_api_connection(self.api_type)
            self.test_completed.emit(self.api_type, result)
        except Exception as e:
            self.test_error.emit(self.api_type, str(e))


class TranslationAPIDebugPage(QFrame, Base):
    """翻译API调试页面"""

    def __init__(self, text: str, window) -> None:
        super().__init__(window)
        self.setObjectName(text.replace(" ", "-"))
        
        # 默认配置
        self.default = {
            "baidu_api_enabled": False,
            "baidu_app_id": "",
            "baidu_secret_key": "",
            "volcano_api_enabled": False,
            "volcano_access_key": "",
            "volcano_secret_key": "",
            "tencent_api_enabled": False,
            "tencent_secret_id": "",
            "tencent_secret_key": "",
            "ai_model_for_comparison": "gpt-3.5-turbo",
            "source_language": "zh",
            "target_language": "en"
        }

        # 载入配置
        config = self.load_config()
        config = self.fill_config(config, self.default)
        
        # 初始化API管理器
        self.api_manager = TranslationAPIManager(config)
        
        # 设置主容器
        self.container = QVBoxLayout(self)
        self.container.setSpacing(8)
        self.container.setContentsMargins(24, 24, 24, 24)

        # 创建标签页导航
        self.pivot = Pivot(self)
        self.container.addWidget(self.pivot)

        # 创建设置页面
        self.settings_widget = QFrame()
        self.settings_scroll = QScrollArea()
        self.settings_scroll.setWidget(self.settings_widget)
        self.settings_scroll.setWidgetResizable(True)
        self.settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.settings_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        settings_layout = QVBoxLayout(self.settings_widget)
        settings_layout.setSpacing(8)
        settings_layout.setContentsMargins(16, 16, 16, 16)
        self.add_api_settings_section(settings_layout, config)

        # 创建测试页面
        self.test_widget = QFrame()
        test_layout = QVBoxLayout(self.test_widget)
        test_layout.setSpacing(8)
        test_layout.setContentsMargins(16, 16, 16, 16)
        self.add_translation_test_section(test_layout, config)
        test_layout.addWidget(HorizontalSeparator())
        self.add_results_section(test_layout)

        # 添加标签页（翻译测试在前，API设置在后）
        self.pivot.addItem(
            routeKey="test",
            text=self.tra("翻译测试"),
            onClick=lambda: self.switch_to_page("test")
        )
        
        self.pivot.addItem(
            routeKey="settings",
            text=self.tra("API设置"),
            onClick=lambda: self.switch_to_page("settings")
        )

        # 默认显示翻译测试页面
        self.container.addWidget(self.test_widget)
        self.pivot.setCurrentItem("test")
        self.current_page = "test"
        
        # 启动定时器检查翻译接口变更
        self.setup_translation_model_monitor()

    def setup_translation_model_monitor(self):
        """设置翻译模型监控定时器"""
        self.translation_model_timer = QTimer()
        self.translation_model_timer.timeout.connect(self.check_translation_model_change)
        self.translation_model_timer.start(5000)  # 每5秒检查一次
        self.last_translation_model = self.get_current_translation_model()

    def check_translation_model_change(self):
        """检查翻译模型是否发生变更"""
        try:
            current_model = self.get_current_translation_model()
            if current_model != self.last_translation_model:
                self.last_translation_model = current_model
                self.update_ai_model_combo()
        except Exception as e:
            print(f"检查翻译模型变更时出错: {e}")

    def update_ai_model_combo(self):
        """更新对比AI模型下拉框"""
        try:
            if not hasattr(self, 'ai_model_combo'):
                return
                
            # 获取当前选择的模型
            current_selection = self.ai_model_combo.combo_box.currentText()
            
            # 获取可用模型列表
            available_models = self.get_tested_success_models()
            current_translation_model = self.get_current_translation_model()
            
            # 如果有翻译接口模型且不在可用模型列表中，则添加到列表开头
            if current_translation_model and current_translation_model not in available_models:
                available_models.insert(0, current_translation_model)
            
            # 清空并重新填充下拉框
            self.ai_model_combo.combo_box.clear()
            if available_models:
                self.ai_model_combo.combo_box.addItems(available_models)
                
                # 优先设置为当前翻译接口模型
                if current_translation_model:
                    index = self.ai_model_combo.combo_box.findText(current_translation_model)
                    if index >= 0:
                        self.ai_model_combo.set_current_index(index)
                # 如果翻译接口模型不存在，尝试恢复之前的选择
                elif current_selection:
                    index = self.ai_model_combo.combo_box.findText(current_selection)
                    if index >= 0:
                        self.ai_model_combo.set_current_index(index)
            else:
                self.ai_model_combo.combo_box.addItem(self.tra("暂无测试通过的模型"))
                
        except Exception as e:
            print(f"更新AI模型下拉框时出错: {e}")

    def add_api_settings_section(self, container, config):
        """添加API设置区域"""
        # 创建水平布局来放置API设置组
        api_groups_layout = QHBoxLayout()
        api_groups_layout.setSpacing(16)
        
        # 百度翻译API设置
        baidu_group = QGroupBox(self.tra("百度翻译API设置"))
        baidu_group.setMaximumWidth(350)
        baidu_layout = QVBoxLayout(baidu_group)
        
        self.baidu_enabled_switch = SwitchButtonCard(
            title=self.tra("启用百度翻译API"),
            description=self.tra("开启后可使用百度翻译API进行翻译测试")
        )
        self.baidu_enabled_switch.set_checked(config.get("baidu_api_enabled", False))
        self.baidu_enabled_switch.switch_button.checkedChanged.connect(self.save_current_config)
        baidu_layout.addWidget(self.baidu_enabled_switch)

        self.baidu_app_id_card = LineEditCard(
            title=self.tra("百度APP ID"),
            description=self.tra("请输入百度翻译API的APP ID")
        )
        self.baidu_app_id_card.set_text(config.get("baidu_app_id", ""))
        self.baidu_app_id_card.line_edit.textChanged.connect(self.save_current_config)
        baidu_layout.addWidget(self.baidu_app_id_card)

        self.baidu_secret_key_card = LineEditCard(
            title=self.tra("百度密钥"),
            description=self.tra("请输入百度翻译API的密钥")
        )
        self.baidu_secret_key_card.set_text(config.get("baidu_secret_key", ""))
        self.baidu_secret_key_card.line_edit.textChanged.connect(self.save_current_config)
        baidu_layout.addWidget(self.baidu_secret_key_card)

        # 百度API测试按钮和状态
        baidu_test_layout = QHBoxLayout()
        self.baidu_test_button = PushButton(FluentIcon.PLAY, self.tra("测试连接"))
        self.baidu_test_button.clicked.connect(lambda: self.test_api_connection("baidu"))
        self.baidu_test_button.setMaximumWidth(120)
        baidu_test_layout.addWidget(self.baidu_test_button)
        
        self.baidu_status_label = QLabel(self.tra("未测试"))
        self.baidu_status_label.setStyleSheet("color: gray;")
        baidu_test_layout.addWidget(self.baidu_status_label)
        baidu_test_layout.addStretch()
        baidu_layout.addLayout(baidu_test_layout)

        api_groups_layout.addWidget(baidu_group)

        # 火山翻译API设置
        volcano_group = QGroupBox(self.tra("火山翻译API设置"))
        volcano_group.setMaximumWidth(350)
        volcano_layout = QVBoxLayout(volcano_group)
        
        self.volcano_enabled_switch = SwitchButtonCard(
            title=self.tra("启用火山翻译API"),
            description=self.tra("开启后可使用火山翻译API进行翻译测试")
        )
        self.volcano_enabled_switch.set_checked(config.get("volcano_api_enabled", False))
        self.volcano_enabled_switch.switch_button.checkedChanged.connect(self.save_current_config)
        volcano_layout.addWidget(self.volcano_enabled_switch)

        self.volcano_access_key_card = LineEditCard(
            title=self.tra("火山Access Key"),
            description=self.tra("请输入火山翻译API的Access Key")
        )
        self.volcano_access_key_card.set_text(config.get("volcano_access_key", ""))
        self.volcano_access_key_card.line_edit.textChanged.connect(self.save_current_config)
        volcano_layout.addWidget(self.volcano_access_key_card)

        self.volcano_secret_key_card = LineEditCard(
            title=self.tra("火山Secret Key"),
            description=self.tra("请输入火山翻译API的Secret Key")
        )
        self.volcano_secret_key_card.set_text(config.get("volcano_secret_key", ""))
        self.volcano_secret_key_card.line_edit.textChanged.connect(self.save_current_config)
        volcano_layout.addWidget(self.volcano_secret_key_card)

        # 火山API测试按钮和状态
        volcano_test_layout = QHBoxLayout()
        self.volcano_test_button = PushButton(FluentIcon.PLAY, self.tra("测试连接"))
        self.volcano_test_button.clicked.connect(lambda: self.test_api_connection("volcano"))
        self.volcano_test_button.setMaximumWidth(120)
        volcano_test_layout.addWidget(self.volcano_test_button)
        
        self.volcano_status_label = QLabel(self.tra("未测试"))
        self.volcano_status_label.setStyleSheet("color: gray;")
        volcano_test_layout.addWidget(self.volcano_status_label)
        volcano_test_layout.addStretch()
        volcano_layout.addLayout(volcano_test_layout)

        api_groups_layout.addWidget(volcano_group)

        # 腾讯翻译API设置
        tencent_group = QGroupBox(self.tra("腾讯翻译API设置"))
        tencent_group.setMaximumWidth(350)
        tencent_layout = QVBoxLayout(tencent_group)
        
        self.tencent_enabled_switch = SwitchButtonCard(
            title=self.tra("启用腾讯翻译API"),
            description=self.tra("开启后可使用腾讯翻译API进行翻译测试")
        )
        self.tencent_enabled_switch.set_checked(config.get("tencent_api_enabled", False))
        self.tencent_enabled_switch.switch_button.checkedChanged.connect(self.save_current_config)
        tencent_layout.addWidget(self.tencent_enabled_switch)

        self.tencent_secret_id_card = LineEditCard(
            title=self.tra("腾讯Secret ID"),
            description=self.tra("请输入腾讯翻译API的Secret ID")
        )
        self.tencent_secret_id_card.set_text(config.get("tencent_secret_id", ""))
        self.tencent_secret_id_card.line_edit.textChanged.connect(self.save_current_config)
        tencent_layout.addWidget(self.tencent_secret_id_card)

        self.tencent_secret_key_card = LineEditCard(
            title=self.tra("腾讯Secret Key"),
            description=self.tra("请输入腾讯翻译API的Secret Key")
        )
        self.tencent_secret_key_card.set_text(config.get("tencent_secret_key", ""))
        self.tencent_secret_key_card.line_edit.textChanged.connect(self.save_current_config)
        tencent_layout.addWidget(self.tencent_secret_key_card)

        # 腾讯API测试按钮和状态
        tencent_test_layout = QHBoxLayout()
        self.tencent_test_button = PushButton(FluentIcon.PLAY, self.tra("测试连接"))
        self.tencent_test_button.clicked.connect(lambda: self.test_api_connection("tencent"))
        self.tencent_test_button.setMaximumWidth(120)
        tencent_test_layout.addWidget(self.tencent_test_button)
        
        self.tencent_status_label = QLabel(self.tra("未测试"))
        self.tencent_status_label.setStyleSheet("color: gray;")
        tencent_test_layout.addWidget(self.tencent_status_label)
        tencent_test_layout.addStretch()
        tencent_layout.addLayout(tencent_test_layout)

        api_groups_layout.addWidget(tencent_group)
        
        # 添加弹性空间
        api_groups_layout.addStretch()
        
        container.addLayout(api_groups_layout)

    def add_translation_test_section(self, container, config):
        """添加翻译测试区域"""
        test_group = QGroupBox(self.tra("翻译测试"))
        test_layout = QVBoxLayout(test_group)

        # 语言设置和按钮的水平布局
        controls_layout = QHBoxLayout()
        
        self.source_lang_combo = ComboBoxCard(
            title=self.tra("源语言"),
            description=self.tra("选择要翻译的源语言"),
            items=[
                self.tra("中文"),
                self.tra("英语"),
                self.tra("法语"),
                self.tra("俄语"),
                self.tra("乌克兰语"),
                self.tra("葡萄牙语"),
                self.tra("西班牙语")
            ]
        )
        self.source_lang_combo.setMaximumWidth(200)
        # 设置语言代码映射
        self.source_lang_map = {
            self.tra("中文"): "zh",
            self.tra("英语"): "en",
            self.tra("法语"): "fr",
            self.tra("俄语"): "ru",
            self.tra("乌克兰语"): "uk",
            self.tra("葡萄牙语"): "pt",
            self.tra("西班牙语"): "es"
        }
        # 设置默认选项
        source_lang = config.get("source_language", "zh-cn")
        for display_name, code in self.source_lang_map.items():
            if code == source_lang:
                index = self.source_lang_combo.combo_box.findText(display_name)
                if index >= 0:
                    self.source_lang_combo.set_current_index(index)
                break
        self.source_lang_combo.combo_box.currentTextChanged.connect(self.save_current_config)
        controls_layout.addWidget(self.source_lang_combo)

        # 添加交换语言按钮
        from qfluentwidgets import ToolButton, FluentIcon
        self.swap_lang_button = ToolButton(FluentIcon.SYNC)
        self.swap_lang_button.setToolTip(self.tra("交换源语言和目标语言"))
        self.swap_lang_button.clicked.connect(self.swap_languages)
        self.swap_lang_button.setFixedSize(40, 40)
        controls_layout.addWidget(self.swap_lang_button)

        self.target_lang_combo = ComboBoxCard(
            title=self.tra("目标语言"),
            description=self.tra("选择翻译的目标语言"),
            items=[
                self.tra("中文"),
                self.tra("英语"),
                self.tra("法语"),
                self.tra("俄语"),
                self.tra("乌克兰语"),
                self.tra("葡萄牙语"),
                self.tra("西班牙语")
            ]
        )
        self.target_lang_combo.setMaximumWidth(200)
        # 设置语言代码映射
        self.target_lang_map = {
            self.tra("中文"): "zh",
            self.tra("英语"): "en",
            self.tra("法语"): "fr",
            self.tra("俄语"): "ru",
            self.tra("乌克兰语"): "uk",
            self.tra("葡萄牙语"): "pt",
            self.tra("西班牙语"): "es"
        }
        target_lang = config.get("target_language", "en")
        for display_name, code in self.target_lang_map.items():
            if code == target_lang:
                index = self.target_lang_combo.combo_box.findText(display_name)
                if index >= 0:
                    self.target_lang_combo.set_current_index(index)
                break
        self.target_lang_combo.combo_box.currentTextChanged.connect(self.save_current_config)
        controls_layout.addWidget(self.target_lang_combo)

        # AI模型选择（用于对比翻译）- 优先使用翻译接口模型
        available_models = self.get_tested_success_models()
        current_translation_model = self.get_current_translation_model()
        
        # 如果有翻译接口模型且不在可用模型列表中，则添加到列表开头
        if current_translation_model and current_translation_model not in available_models:
            available_models.insert(0, current_translation_model)
        
        self.ai_model_combo = ComboBoxCard(
            title=self.tra("对比AI模型"),
            description=self.tra("选择用于对比翻译的AI大模型（自动同步翻译接口模型）"),
            items=available_models if available_models else [self.tra("暂无测试通过的模型")]
        )
        self.ai_model_combo.setMaximumWidth(200)
        
        # 优先设置为当前翻译接口模型，如果没有则使用配置中的模型
        if current_translation_model:
            index = self.ai_model_combo.combo_box.findText(current_translation_model)
            if index >= 0:
                self.ai_model_combo.set_current_index(index)
        else:
            ai_model = config.get("ai_model_for_comparison", "gpt-3.5-turbo")
            index = self.ai_model_combo.combo_box.findText(ai_model)
            if index >= 0:
                self.ai_model_combo.set_current_index(index)
        
        self.ai_model_combo.combo_box.currentTextChanged.connect(self.save_current_config)
        controls_layout.addWidget(self.ai_model_combo)

        # 测试按钮
        self.test_button = PillPushButton(self.tra("开始翻译测试"))
        self.test_button.clicked.connect(self.start_translation_test)
        self.test_button.setMaximumWidth(150)
        controls_layout.addWidget(self.test_button)
        
        # 添加弹性空间
        controls_layout.addStretch()

        test_layout.addLayout(controls_layout)

        # 测试文本输入
        self.test_text_edit = TextEditCard(
            icon="",
            title=self.tra("测试文本"),
            content=self.tra("请输入要进行翻译测试的文本")
        )
        self.test_text_edit.setValue("如果你不开心，那么，能变得开心的唯一办法是开心地坐直身体，并装作很开心的样子说话及行动。如果你的行为散发的是快乐，就不可能在心理上保持忧郁。这点小小的基本真理可以为我们的人生带来奇迹。")
        test_layout.addWidget(self.test_text_edit)

        container.addWidget(test_group)

    def add_results_section(self, container):
        """添加结果显示区域"""
        results_group = QGroupBox(self.tra("翻译结果对比"))
        results_layout = QVBoxLayout(results_group)

        # 使用QTextBrowser支持markdown渲染
        self.results_text_edit = QTextBrowser()
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setMinimumHeight(300)
        # 设置自动换行和滚动条策略
        self.results_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.results_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # 启用markdown支持
        self.results_text_edit.setMarkdown("")
        results_layout.addWidget(self.results_text_edit)

        container.addWidget(results_group)

    def start_translation_test(self):
        """开始翻译测试"""
        test_text = self.test_text_edit.getValue()
        if not test_text.strip():
            InfoBar.error(
                title=self.tra("错误"),
                content=self.tra("请输入测试文本"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        # 记录开始时间
        import time
        self.test_start_time = time.time()

        # 更新API管理器配置
        config = {
            "baidu_api_enabled": self.baidu_enabled_switch.is_checked(),
            "baidu_app_id": self.baidu_app_id_card.get_text(),
            "baidu_secret_key": self.baidu_secret_key_card.get_text(),
            "volcano_api_enabled": self.volcano_enabled_switch.is_checked(),
            "volcano_access_key": self.volcano_access_key_card.get_text(),
            "volcano_secret_key": self.volcano_secret_key_card.get_text(),
            "tencent_api_enabled": self.tencent_enabled_switch.is_checked(),
            "tencent_secret_id": self.tencent_secret_id_card.get_text(),
            "tencent_secret_key": self.tencent_secret_key_card.get_text(),
        }
        self.api_manager.update_config(config)
        
        # 保存配置到文件
        self.save_config(config)

        # 禁用测试按钮
        self.test_button.setEnabled(False)
        self.test_button.setText(self.tra("测试中..."))

        # 清空结果显示
        self.results_text_edit.clear()

        # 启动测试线程
        self.test_thread = TranslationTestThread(
            self.api_manager,
            test_text,
            self.source_lang_map.get(self.source_lang_combo.get_current_text(), "zh"),
            self.target_lang_map.get(self.target_lang_combo.get_current_text(), "zh")
        )
        self.test_thread.test_completed.connect(self.on_test_completed)
        self.test_thread.test_error.connect(self.on_test_error)
        self.test_thread.start()

    def on_test_completed(self, results):
        """测试完成回调"""
        # 计算耗时
        import time
        if hasattr(self, 'test_start_time'):
            elapsed_time = time.time() - self.test_start_time
            time_str = f"{elapsed_time:.2f}秒"
        else:
            time_str = "未知"
        
        self.test_button.setEnabled(True)
        self.test_button.setText(self.tra("开始翻译测试"))

        # 显示结果 - 使用markdown格式
        result_markdown = f"# {self.tra('翻译结果对比')}\n\n"
        result_markdown += f"⏱️ **测试用时**: {time_str}\n\n"
        
        # 分离AI质量分析和翻译结果
        ai_comparison_result = None
        translation_results = {}
        
        for api_name, result in results.items():
            if api_name == "ai_comparison":
                ai_comparison_result = result
            else:
                translation_results[api_name] = result
        
        # 显示翻译结果
        for api_name, result in translation_results.items():
            # 检查result是否为字典类型
            if isinstance(result, dict):
                if result.get("success", False):
                    result_markdown += f"## 🟢 {api_name}\n\n"
                    result_markdown += f"```\n{result.get('translation', 'N/A')}\n```\n\n"
                else:
                    result_markdown += f"## 🔴 {api_name}\n\n"
                    result_markdown += f"**{self.tra('翻译失败')}**: `{result.get('error', '未知错误')}`\n\n"
            else:
                # 如果result不是字典，可能是字符串错误信息
                result_markdown += f"## 🔴 {api_name}\n\n"
                result_markdown += f"**{self.tra('翻译失败')}**: `{str(result)}`\n\n"

        # 如果有AI质量评估结果，只显示一次
        if ai_comparison_result:
            result_markdown += f"\n## 🤖 {self.tra('AI质量评估')}\n\n"
            # 检查AI分析结果是否已经包含markdown格式
            if ai_comparison_result.startswith("AI质量分析："):
                # 如果是AI生成的分析，去掉前缀并直接显示
                clean_result = ai_comparison_result.replace("AI质量分析：\n", "")
                result_markdown += f"{clean_result}\n"
            else:
                # 如果是基础分析或其他格式，保持代码块格式
                result_markdown += f"```\n{ai_comparison_result}\n```\n"

        self.results_text_edit.setMarkdown(result_markdown)

        InfoBar.success(
            title=self.tra("成功"),
            content=f"翻译测试完成，用时 {time_str}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

    def on_test_error(self, error_msg):
        """测试错误回调"""
        # 计算耗时
        import time
        if hasattr(self, 'test_start_time'):
            elapsed_time = time.time() - self.test_start_time
            time_str = f"{elapsed_time:.2f}秒"
        else:
            time_str = "未知"
            
        self.test_button.setEnabled(True)
        self.test_button.setText(self.tra("开始翻译测试"))

        InfoBar.error(
            title=self.tra("错误"),
            content=f"{self.tra('翻译测试失败')}: {error_msg}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def switch_to_page(self, page_key):
        """切换页面"""
        # 移除当前页面
        if hasattr(self, 'current_page'):
            if self.current_page == "settings" and self.container.count() > 1:
                self.container.removeWidget(self.settings_scroll)
                self.settings_scroll.setParent(None)
            elif self.current_page == "test" and self.container.count() > 1:
                self.container.removeWidget(self.test_widget)
                self.test_widget.setParent(None)
        
        # 添加新页面
        if page_key == "settings":
            self.container.addWidget(self.settings_scroll)
        elif page_key == "test":
            self.container.addWidget(self.test_widget)
            # 切换到翻译测试页面时，刷新AI模型选择
            self.update_ai_model_combo()
        
        self.current_page = page_key

    def save_current_config(self):
        """保存当前配置"""
        config = {
            "baidu_api_enabled": self.baidu_enabled_switch.is_checked() if hasattr(self, 'baidu_enabled_switch') else False,
            "baidu_app_id": self.baidu_app_id_card.get_text() if hasattr(self, 'baidu_app_id_card') else "",
            "baidu_secret_key": self.baidu_secret_key_card.get_text() if hasattr(self, 'baidu_secret_key_card') else "",
            "volcano_api_enabled": self.volcano_enabled_switch.is_checked() if hasattr(self, 'volcano_enabled_switch') else False,
            "volcano_access_key": self.volcano_access_key_card.get_text() if hasattr(self, 'volcano_access_key_card') else "",
            "volcano_secret_key": self.volcano_secret_key_card.get_text() if hasattr(self, 'volcano_secret_key_card') else "",
            "tencent_api_enabled": self.tencent_enabled_switch.is_checked() if hasattr(self, 'tencent_enabled_switch') else False,
            "tencent_secret_id": self.tencent_secret_id_card.get_text() if hasattr(self, 'tencent_secret_id_card') else "",
            "tencent_secret_key": self.tencent_secret_key_card.get_text() if hasattr(self, 'tencent_secret_key_card') else "",
            "ai_model_for_comparison": self.ai_model_combo.combo_box.currentText() if hasattr(self, 'ai_model_combo') and self.ai_model_combo.combo_box.currentText() != self.tra("暂无测试通过的模型") else "gpt-3.5-turbo",
            "source_language": self.source_lang_map.get(self.source_lang_combo.combo_box.currentText(), "auto") if hasattr(self, 'source_lang_combo') else "auto",
            "target_language": self.target_lang_map.get(self.target_lang_combo.combo_box.currentText(), "zh-cn") if hasattr(self, 'target_lang_combo') else "zh-cn"
        }
        
        # 合并默认配置
        full_config = self.fill_config(self.load_config(), config)
        self.save_config(full_config)

    def test_api_connection(self, api_type):
        """测试API连接"""
        # 获取相应的按钮和状态标签
        if api_type == "baidu":
            button = self.baidu_test_button
            status_label = self.baidu_status_label
            config = {
                "baidu_app_id": self.baidu_app_id_card.get_text(),
                "baidu_secret_key": self.baidu_secret_key_card.get_text()
            }
        elif api_type == "volcano":
            button = self.volcano_test_button
            status_label = self.volcano_status_label
            config = {
                "volcano_access_key": self.volcano_access_key_card.get_text(),
                "volcano_secret_key": self.volcano_secret_key_card.get_text()
            }
        elif api_type == "tencent":
            button = self.tencent_test_button
            status_label = self.tencent_status_label
            config = {
                "tencent_secret_id": self.tencent_secret_id_card.get_text(),
                "tencent_secret_key": self.tencent_secret_key_card.get_text()
            }
        else:
            return

        # 更新API管理器配置
        self.api_manager.update_config(config)
        
        # 保存配置到文件
        self.save_config(config)

        # 禁用按钮并显示测试中状态
        button.setEnabled(False)
        button.setText(self.tra("测试中..."))
        status_label.setText(self.tra("测试中..."))
        status_label.setStyleSheet("color: orange;")

        # 启动测试线程
        self.connection_test_thread = APIConnectionTestThread(self.api_manager, api_type)
        self.connection_test_thread.test_completed.connect(self.on_connection_test_completed)
        self.connection_test_thread.test_error.connect(self.on_connection_test_error)
        self.connection_test_thread.start()

    def on_connection_test_completed(self, api_type, result):
        """API连接测试完成回调"""
        # 获取相应的按钮和状态标签
        if api_type == "baidu":
            button = self.baidu_test_button
            status_label = self.baidu_status_label
        elif api_type == "volcano":
            button = self.volcano_test_button
            status_label = self.volcano_status_label
        elif api_type == "tencent":
            button = self.tencent_test_button
            status_label = self.tencent_status_label
        else:
            return

        # 恢复按钮状态
        button.setEnabled(True)
        button.setText(self.tra("测试连接"))

        # 显示测试结果
        if isinstance(result, dict) and result.get("success", False):
            status_label.setText(self.tra("连接成功"))
            status_label.setStyleSheet("color: green;")
            InfoBar.success(
                title=self.tra("成功"),
                content=f"{api_type.upper()} API {self.tra('连接测试成功')}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            status_label.setText(self.tra("连接失败"))
            status_label.setStyleSheet("color: red;")
            error_msg = result.get('error', str(result)) if isinstance(result, dict) else str(result)
            InfoBar.error(
                title=self.tra("错误"),
                content=f"{api_type.upper()} API {self.tra('连接失败')}: {error_msg}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def on_connection_test_error(self, api_type, error_msg):
        """API连接测试错误回调"""
        # 获取相应的按钮和状态标签
        if api_type == "baidu":
            button = self.baidu_test_button
            status_label = self.baidu_status_label
        elif api_type == "volcano":
            button = self.volcano_test_button
            status_label = self.volcano_status_label
        elif api_type == "tencent":
            button = self.tencent_test_button
            status_label = self.tencent_status_label
        else:
            return

        # 恢复按钮状态
        button.setEnabled(True)
        button.setText(self.tra("测试连接"))

        # 显示错误状态
        status_label.setText(self.tra("测试错误"))
        status_label.setStyleSheet("color: red;")
        
        InfoBar.error(
            title=self.tra("错误"),
            content=f"{api_type.upper()} API {self.tra('测试失败')}: {error_msg}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def swap_languages(self):
        """交换源语言和目标语言"""
        try:
            # 获取当前选择的语言
            source_text = self.source_lang_combo.combo_box.currentText()
            target_text = self.target_lang_combo.combo_box.currentText()
            
            # 交换语言选择
            source_index = self.target_lang_combo.combo_box.findText(source_text)
            target_index = self.source_lang_combo.combo_box.findText(target_text)
            
            if source_index >= 0:
                self.target_lang_combo.set_current_index(source_index)
            if target_index >= 0:
                self.source_lang_combo.set_current_index(target_index)
                
            # 保存配置
            self.save_current_config()
            
        except Exception as e:
            print(f"交换语言时出错: {e}")
    
    def get_current_translation_model(self):
        """获取当前接口管理中设置的翻译接口模型"""
        try:
            # 导入必要的模块
            from ModuleFolders.TaskConfig.TaskConfig import TaskConfig
            
            # 加载配置
            config = TaskConfig()
            config.initialize()
            
            # 获取翻译接口设置
            translate_platform = config.api_settings.get("translate")
            if translate_platform and translate_platform in config.platforms:
                platform_config = config.platforms[translate_platform]
                model = platform_config.get("model", "")
                if model:
                    return model
            
            return None
            
        except Exception as e:
            print(f"获取当前翻译模型时出错: {e}")
            return None
    
    def get_tested_success_models(self):
        """获取测试通过的AI模型列表"""
        try:
            # 导入必要的模块
            from ModuleFolders.TaskConfig.TaskConfig import TaskConfig
            
            # 加载配置
            config = TaskConfig()
            config.initialize()
            
            # 获取所有平台配置
            platforms = config.platforms
            success_models = []
            
            # 遍历所有平台，查找测试通过的模型
            for platform_key, platform_config in platforms.items():
                # 检查平台是否有测试状态记录（这里需要根据实际的测试状态存储方式调整）
                # 暂时返回一些常用模型作为示例，实际应该根据测试状态来筛选
                if platform_config.get("enabled", False):  # 如果平台启用
                    model_datas = platform_config.get("model_datas", [])
                    if model_datas:
                        success_models.extend(model_datas)
                    else:
                        # 如果没有model_datas，使用默认模型
                        default_model = platform_config.get("model", "")
                        if default_model:
                            success_models.append(default_model)
            
            # 去重并返回
            return list(set(success_models)) if success_models else []
            
        except Exception as e:
            print(f"获取测试通过的模型时出错: {e}")
            # 返回一些默认模型
            return [
                "gpt-3.5-turbo",
                "gpt-4",
                "claude-3-haiku",
                "gemini-pro"
            ]