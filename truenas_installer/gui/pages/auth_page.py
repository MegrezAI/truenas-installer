from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import (
    SubtitleLabel,
    LineEdit,
    CardWidget,
    setFont,
    MessageBox,
    PrimaryPushButton,
    StrongBodyLabel,
)


class AuthPage(QFrame):
    installationRequested = pyqtSignal(dict)  # auth_method

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 标题
        self.title = SubtitleLabel(self.i18n.get("authentication"), self)
        setFont(self.title, 24)
        layout.addWidget(self.title)

        # 创建卡片容器
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        # 说明文字

        # 密码输入区域
        self.password_widget = CardWidget(card)
        self.password_widget.setObjectName("passwordCard")
        pass_layout = QVBoxLayout(self.password_widget)
        pass_layout.setSpacing(16)

        self.desc_label = StrongBodyLabel(
            self.i18n.get("admin_user"), self.password_widget
        )
        pass_layout.addWidget(self.desc_label, alignment=Qt.AlignCenter)

        # 密码输入框
        self.pass_input = LineEdit(self.password_widget)
        self.pass_input.setEchoMode(LineEdit.Password)
        self.pass_input.setFixedWidth(300)
        self.pass_input.setPlaceholderText(self.i18n.get("password"))
        self.pass_input.textChanged.connect(self.check_password_state)
        pass_layout.addWidget(self.pass_input, alignment=Qt.AlignCenter)

        # 确认密码输入框
        self.pass_confirm = LineEdit(self.password_widget)
        self.pass_confirm.setEchoMode(LineEdit.Password)
        self.pass_confirm.setFixedWidth(300)
        self.pass_confirm.setPlaceholderText(self.i18n.get("confirm_password"))
        self.pass_confirm.textChanged.connect(self.check_password_state)
        pass_layout.addWidget(self.pass_confirm, alignment=Qt.AlignCenter)

        card_layout.addWidget(self.password_widget, alignment=Qt.AlignCenter)

        # 将卡片添加到主布局
        layout.addWidget(card, 1)

        # 添加弹性空间
        layout.addStretch()

        # 添加按钮布局
        button_layout = QHBoxLayout()

        # 添加返回按钮
        self.back_button = PrimaryPushButton(self.i18n.get("back"), self)
        self.back_button.setFixedWidth(120)
        self.back_button.clicked.connect(self.on_back_clicked)
        button_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        button_layout.addStretch()

        # 安装按钮
        self.next_button = PrimaryPushButton(self.i18n.get("install"), self)
        self.next_button.setFixedWidth(120)
        self.next_button.clicked.connect(self.on_next_clicked)
        self.next_button.setEnabled(False)  # 初始状态设置为禁用

        button_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)

    def validate_and_get_auth(self):
        if self.pass_input.text() != self.pass_confirm.text():
            MessageBox(
                self.i18n.get("error"), self.i18n.get("passwords_not_match"), self
            ).exec()
            return None
        return {"username": "truenas_admin", "password": self.pass_input.text()}

    def on_back_clicked(self):
        window = self.window()
        window.switchTo(window.disk_selection_page)

    def on_next_clicked(self):
        auth_data = self.validate_and_get_auth()
        if auth_data:
            self.installationRequested.emit(auth_data)

    def update_texts(self):
        self.title.setText(self.i18n.get("authentication"))
        self.desc_label.setText(self.i18n.get("admin_user"))
        self.pass_input.setPlaceholderText(self.i18n.get("password"))
        self.pass_confirm.setPlaceholderText(self.i18n.get("confirm_password"))
        self.back_button.setText(self.i18n.get("back"))
        self.next_button.setText(self.i18n.get("install"))

    def check_password_state(self):
        has_content = bool(
            self.pass_input.text().strip() and self.pass_confirm.text().strip()
        )
        self.next_button.setEnabled(has_content)
