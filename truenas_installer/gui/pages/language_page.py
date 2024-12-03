from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QListWidgetItem, QHBoxLayout
from qfluentwidgets import (
    PrimaryPushButton,
    SubtitleLabel,
    BodyLabel,
    setFont,
    CardWidget,
    LargeTitleLabel,
)


class LanguagePage(QFrame):
    languageChanged = pyqtSignal(str)

    def __init__(self, i18n, version, parent=None):
        super().__init__(parent=parent)
        self.i18n = i18n
        self.version = version

        self.setObjectName("language-page")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 创建卡片容器
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        card_layout.addStretch()

        # 创建一个容器来包含标题和描述
        content_container = QHBoxLayout()
        content_container.addStretch()

        text_layout = QVBoxLayout()

        # 标题
        self.title_label = LargeTitleLabel(self.i18n.get("welcome_title"), self)
        self.title_label.setStyleSheet(
            """
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2980b9;
        """
        )
        self.title_label.setAlignment(Qt.AlignCenter)

        # 描述
        self.description_label = BodyLabel(self.i18n.get("welcome_message"), self)
        self.description_label.setFixedWidth(600)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setStyleSheet(
            """
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        """
        )

        # 将标题和描述添加到垂直布局中
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.description_label)

        # 将垂直布局添加到容器中
        content_container.addLayout(text_layout)
        content_container.addStretch()

        # 将容器添加到卡片布局中
        card_layout.addLayout(content_container)

        card_layout.addSpacing(20)

        # 语言按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # 中文按钮
        self.zh_button = PrimaryPushButton("使用中文进行安装", self)
        self.zh_button.setFixedHeight(40)
        self.zh_button.clicked.connect(lambda: self.on_language_selected("简体中文"))

        # 英文按钮
        self.en_button = PrimaryPushButton("Install with English", self)
        self.en_button.setFixedHeight(40)
        self.en_button.clicked.connect(lambda: self.on_language_selected("English"))

        button_layout.addStretch()
        button_layout.addWidget(self.zh_button)
        button_layout.addWidget(self.en_button)
        button_layout.addStretch()

        card_layout.addSpacing(20)
        card_layout.addLayout(button_layout)

        card_layout.addStretch()

        # 将卡片添加到主布局
        layout.addWidget(card, stretch=1)

    def on_language_selected(self, language):
        self.languageChanged.emit(language)
        window = self.window()
        window.start_installation()

    def update_texts(self):
        self.title_label.setText(self.i18n.get("welcome_title"))
        self.message_label.setText(self.i18n.get("language_selection"))
