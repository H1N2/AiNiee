from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt

from qfluentwidgets import CardWidget, CaptionLabel, StrongBodyLabel


class TextEditCard(CardWidget):
    """多行文本编辑卡片"""

    def __init__(self, icon: str, title: str, content: str, config_key: str = None):
        super().__init__(None)
        self.config_key = config_key
        
        # 设置容器
        self.setBorderRadius(4)
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(16, 16, 16, 16)
        self.vbox.setSpacing(8)

        # 标题和描述
        self.title_label = StrongBodyLabel(title, self)
        self.vbox.addWidget(self.title_label)

        self.content_label = CaptionLabel(content, self)
        self.content_label.setTextColor(QColor(96, 96, 96), QColor(160, 160, 160))
        self.vbox.addWidget(self.content_label)

        # 文本编辑框
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(100)
        self.text_edit.setMaximumHeight(200)
        self.vbox.addWidget(self.text_edit)

    def setValue(self, value):
        """设置值"""
        self.text_edit.setPlainText(str(value) if value is not None else "")

    def getValue(self):
        """获取值"""
        return self.text_edit.toPlainText()

    def setPlaceholderText(self, text):
        """设置占位符文本"""
        self.text_edit.setPlaceholderText(text)