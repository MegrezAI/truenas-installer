from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout
from qfluentwidgets import (
    SubtitleLabel,
    setFont,
    FluentIcon as FIF,
    PrimaryPushButton,
    CardWidget,
    PushButton,
    StrongBodyLabel,
)


class MainMenuPage(QFrame):
    installationRequested = pyqtSignal()
    shellRequested = pyqtSignal()
    rebootRequested = pyqtSignal()
    shutdownRequested = pyqtSignal()
    backRequested = pyqtSignal()

    def __init__(self, installer, i18n):
        super().__init__()
        self.installer = installer
        self.i18n = i18n
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 标题
        self.title_label = SubtitleLabel(
            f"{self.installer.vendor} {self.installer.version}", self
        )
        setFont(self.title_label, 24)
        layout.addWidget(self.title_label)

        # 创建卡片容器
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        # 添加顶部弹性空间
        card_layout.addStretch()

        # 欢迎消息
        self.welcome_label = StrongBodyLabel(self.i18n.get("welcome_message"), self)
        self.welcome_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.welcome_label)

        card_layout.addSpacing(20)

        # 操作按钮
        actions_config = [
            {
                "text": self.i18n.get("install_upgrade"),
                "icon": FIF.UPDATE,
                "signal": self.installationRequested,
                "primary": True,
            },
            {
                "text": self.i18n.get("shell"),
                "icon": FIF.COMMAND_PROMPT,
                "signal": self.shellRequested,
                "primary": False,
            },
            {
                "text": self.i18n.get("reboot"),
                "icon": FIF.POWER_BUTTON,
                "signal": self.rebootRequested,
                "primary": False,
            },
            {
                "text": self.i18n.get("shutdown"),
                "icon": FIF.CLOSE,
                "signal": self.shutdownRequested,
                "primary": False,
            },
        ]

        # 创建并添加按钮
        for config in actions_config:
            button_layout = QHBoxLayout()
            button_layout.setSpacing(0)

            # 创建按钮
            if config["primary"]:
                button = PrimaryPushButton(config["text"], self)
            else:
                button = PushButton(config["text"], self)

            button.setIcon(config["icon"].icon())
            button.setFixedHeight(40)
            button.setFixedWidth(300)
            button.clicked.connect(config["signal"].emit)

            # 添加按钮到水平布局并居中
            button_layout.addStretch()
            button_layout.addWidget(button)
            button_layout.addStretch()

            # 添加按钮布局到卡片
            card_layout.addLayout(button_layout)
            card_layout.addSpacing(8)  # 按钮之间的间距

        # 添加底部弹性空间
        card_layout.addStretch()

        # 将卡片添加到主布局
        layout.addWidget(card, stretch=1)

        # 添加底部空间
        layout.addStretch()

        # 添加按钮布局
        button_layout = QHBoxLayout()

        # 添加返回按钮
        self.back_button = PrimaryPushButton(self.i18n.get("back"), self)
        self.back_button.setFixedWidth(120)
        self.back_button.clicked.connect(self.backRequested.emit)
        button_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)

    def update_texts(self):
        self.title_label.setText(f"{self.installer.vendor} {self.installer.version}")
        self.welcome_label.setText(self.i18n.get("welcome_message"))
        self.back_button.setText(self.i18n.get("back"))

        # 更新按钮文本
        for button in self.findChildren(PushButton):
            if isinstance(button, PrimaryPushButton):
                if button != self.back_button:  # 不是返回按钮
                    button.setText(self.i18n.get("install_upgrade"))
            else:
                if "shell" in button.text().lower():
                    button.setText(self.i18n.get("shell"))
                elif "reboot" in button.text().lower():
                    button.setText(self.i18n.get("reboot"))
                elif "shutdown" in button.text().lower():
                    button.setText(self.i18n.get("shutdown"))
