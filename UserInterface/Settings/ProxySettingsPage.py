import asyncio
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from qfluentwidgets import (
    HorizontalSeparator, PushButton, InfoBar, InfoBarPosition,
    ProgressRing, FluentIcon
)

from Base.Base import Base
from Widget.LineEditCard import LineEditCard
from Widget.SwitchButtonCard import SwitchButtonCard
from Widget.PushButtonCard import PushButtonCard
from ModuleFolders.LLMRequester.ProxyTester import ProxyTester


class ProxyTestThread(QThread):
    """
    代理测试线程
    """
    test_finished = pyqtSignal(dict)
    
    def __init__(self, proxy_url: str, test_type: str = "sync"):
        super().__init__()
        self.proxy_url = proxy_url
        self.test_type = test_type
        self.tester = ProxyTester()
    
    def run(self):
        try:
            if self.test_type == "direct":
                result = self.tester.test_direct_connection()
            else:
                result = self.tester.test_proxy_sync(self.proxy_url)
            self.test_finished.emit(result)
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "proxy_url": self.proxy_url
            }
            self.test_finished.emit(error_result)


class ProxySettingsPage(QFrame, Base):
    """
    网络代理设置页面
    """
    
    def __init__(self, text: str, window) -> None:
        super().__init__(window)
        self.setObjectName(text.replace(" ", "-"))
        
        # 默认配置
        self.default = {
            "proxy_enable": False,
            "proxy_url": "",
            "proxy_auth_enable": False,
            "proxy_username": "",
            "proxy_password": "",
            "proxy_test_timeout": 10
        }
        
        # 载入并保存默认配置
        config = self.save_config(self.load_config_from_default())
        
        # 设置容器
        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(8)
        self.vbox.setContentsMargins(24, 24, 24, 24)
        
        # 测试相关
        self.test_thread = None
        self.tester = ProxyTester()
        
        # 添加控件
        self.add_proxy_enable_widget(self.vbox, config)
        self.add_proxy_url_widget(self.vbox, config)
        self.vbox.addWidget(HorizontalSeparator())
        self.add_proxy_auth_widgets(self.vbox, config)
        self.vbox.addWidget(HorizontalSeparator())
        self.add_test_widgets(self.vbox, config)
        self.add_result_display_widget(self.vbox)
        
        # 填充
        self.vbox.addStretch(1)
    
    def add_proxy_enable_widget(self, parent, config) -> None:
        """
        添加代理启用开关
        """
        def checked_changed(widget, checked: bool) -> None:
            config = self.load_config()
            config["proxy_enable"] = checked
            self.save_config(config)
            
            # 更新环境变量
            self.update_proxy_environment(config)
            
            # 显示状态信息
            if checked:
                proxy_url = config.get("proxy_url", "")
                if proxy_url:
                    self.show_info_bar("success", "代理已启用", f"代理地址: {proxy_url}")
                else:
                    self.show_info_bar("warning", "代理已启用", "但未设置代理地址")
            else:
                self.show_info_bar("info", "代理已禁用", "")
        
        def init(widget) -> None:
            widget.set_checked(config.get("proxy_enable", False))
        
        parent.addWidget(
            SwitchButtonCard(
                self.tra("启用网络代理"),
                self.tra("启用后将通过代理服务器访问网络"),
                init=init,
                checked_changed=checked_changed
            )
        )
    
    def add_proxy_url_widget(self, parent, config) -> None:
        """
        添加代理地址设置
        """
        def text_changed(text: str) -> None:
            config = self.load_config()
            config["proxy_url"] = text.strip()
            self.save_config(config)
            
            # 如果代理已启用，更新环境变量
            if config.get("proxy_enable", False):
                self.update_proxy_environment(config)
        
        def init(widget) -> None:
            widget.set_text(config.get("proxy_url", ""))
            widget.set_placeholder_text("例如: http://127.0.0.1:7890 或 socks5://127.0.0.1:1080")
        
        parent.addWidget(
            LineEditCard(
                self.tra("代理服务器地址"),
                self.tra("支持HTTP、HTTPS、SOCKS5代理协议"),
                init=init,
                text_changed=text_changed
            )
        )
    
    def add_proxy_auth_widgets(self, parent, config) -> None:
        """
        添加代理认证设置
        """
        # 认证启用开关
        def auth_checked_changed(widget, checked: bool) -> None:
            config = self.load_config()
            config["proxy_auth_enable"] = checked
            self.save_config(config)
        
        def auth_init(widget) -> None:
            widget.set_checked(config.get("proxy_auth_enable", False))
        
        parent.addWidget(
            SwitchButtonCard(
                self.tra("启用代理认证"),
                self.tra("如果代理服务器需要用户名和密码认证"),
                init=auth_init,
                checked_changed=auth_checked_changed
            )
        )
        
        # 用户名
        def username_changed(text: str) -> None:
            config = self.load_config()
            config["proxy_username"] = text.strip()
            self.save_config(config)
        
        def username_init(widget) -> None:
            widget.set_text(config.get("proxy_username", ""))
            widget.set_placeholder_text("代理服务器用户名")
        
        parent.addWidget(
            LineEditCard(
                self.tra("代理用户名"),
                self.tra("代理服务器认证用户名"),
                init=username_init,
                text_changed=username_changed
            )
        )
        
        # 密码
        def password_changed(text: str) -> None:
            config = self.load_config()
            config["proxy_password"] = text.strip()
            self.save_config(config)
        
        def password_init(widget) -> None:
            widget.set_text(config.get("proxy_password", ""))
            widget.set_placeholder_text("代理服务器密码")
            widget.line_edit.setEchoMode(widget.line_edit.Password)  # 密码模式
        
        parent.addWidget(
            LineEditCard(
                self.tra("代理密码"),
                self.tra("代理服务器认证密码"),
                init=password_init,
                text_changed=password_changed
            )
        )
    
    def add_test_widgets(self, parent, config) -> None:
        """
        添加测试功能控件
        """
        # 创建水平布局
        test_layout = QHBoxLayout()
        
        # 测试代理按钮
        def test_proxy_clicked() -> None:
            config = self.load_config()
            proxy_url = config.get("proxy_url", "")
            
            if not proxy_url:
                self.show_info_bar("warning", "测试失败", "请先设置代理地址")
                return
            
            self.start_proxy_test(proxy_url, "sync")
        
        def test_proxy_init(widget) -> None:
            widget.set_text("测试代理连接")
            widget.set_icon(FluentIcon.CONNECT)
        
        test_proxy_card = PushButtonCard(
            self.tra("代理连接测试"),
            self.tra("测试当前代理设置是否可用"),
            init=test_proxy_init,
            clicked=test_proxy_clicked
        )
        
        # 测试直连按钮
        def test_direct_clicked() -> None:
            self.start_proxy_test("", "direct")
        
        def test_direct_init(widget) -> None:
            widget.set_text("测试直连")
            widget.set_icon(FluentIcon.WIFI)
        
        test_direct_card = PushButtonCard(
            self.tra("直连网络测试"),
            self.tra("测试不使用代理的网络连接"),
            init=test_direct_init,
            clicked=test_direct_clicked
        )
        
        parent.addWidget(test_proxy_card)
        parent.addWidget(test_direct_card)
    
    def add_result_display_widget(self, parent) -> None:
        """
        添加测试结果显示区域
        """
        # 结果显示标签
        result_label = QLabel("测试结果")
        result_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        parent.addWidget(result_label)
        
        # 结果文本框
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(200)
        self.result_text.setPlainText("点击上方按钮开始测试网络连接...")
        self.result_text.setReadOnly(True)
        parent.addWidget(self.result_text)
    
    def start_proxy_test(self, proxy_url: str, test_type: str) -> None:
        """
        开始代理测试
        
        参数:
            proxy_url: 代理地址
            test_type: 测试类型 ("sync" 或 "direct")
        """
        if self.test_thread and self.test_thread.isRunning():
            self.show_info_bar("warning", "测试进行中", "请等待当前测试完成")
            return
        
        # 显示测试开始信息
        if test_type == "direct":
            self.result_text.setPlainText("🔄 正在测试直连网络...")
            self.show_info_bar("info", "开始测试", "正在测试直连网络连接")
        else:
            self.result_text.setPlainText(f"🔄 正在测试代理连接...\n代理地址: {proxy_url}")
            self.show_info_bar("info", "开始测试", f"正在测试代理: {proxy_url}")
        
        # 启动测试线程
        self.test_thread = ProxyTestThread(proxy_url, test_type)
        self.test_thread.test_finished.connect(self.on_test_finished)
        self.test_thread.start()
    
    def on_test_finished(self, result: dict) -> None:
        """
        测试完成回调
        
        参数:
            result: 测试结果字典
        """
        # 格式化并显示结果
        formatted_result = self.tester.format_test_result(result)
        self.result_text.setPlainText(formatted_result)
        
        # 显示通知
        if result["success"]:
            self.show_info_bar("success", "测试成功", "网络连接正常")
        else:
            error_msg = result.get("error", "未知错误")
            self.show_info_bar("error", "测试失败", error_msg)
    
    def update_proxy_environment(self, config: dict) -> None:
        """
        更新代理环境变量
        
        参数:
            config: 配置字典
        """
        import os
        
        if config.get("proxy_enable", False):
            proxy_url = config.get("proxy_url", "")
            if proxy_url:
                # 处理认证信息
                if config.get("proxy_auth_enable", False):
                    username = config.get("proxy_username", "")
                    password = config.get("proxy_password", "")
                    if username and password:
                        # 在URL中插入认证信息
                        if "://" in proxy_url:
                            protocol, rest = proxy_url.split("://", 1)
                            proxy_url = f"{protocol}://{username}:{password}@{rest}"
                
                os.environ["http_proxy"] = proxy_url
                os.environ["https_proxy"] = proxy_url
            else:
                # 清除环境变量
                os.environ.pop("http_proxy", None)
                os.environ.pop("https_proxy", None)
        else:
            # 清除环境变量
            os.environ.pop("http_proxy", None)
            os.environ.pop("https_proxy", None)
    
    def show_info_bar(self, bar_type: str, title: str, content: str) -> None:
        """
        显示信息条
        
        参数:
            bar_type: 信息条类型 ("success", "warning", "error", "info")
            title: 标题
            content: 内容
        """
        if bar_type == "success":
            InfoBar.success(title, content, parent=self)
        elif bar_type == "warning":
            InfoBar.warning(title, content, parent=self)
        elif bar_type == "error":
            InfoBar.error(title, content, parent=self)
        else:
            InfoBar.info(title, content, parent=self)