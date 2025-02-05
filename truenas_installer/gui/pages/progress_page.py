from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame, QVBoxLayout
from qfluentwidgets import (
    SubtitleLabel,
    ProgressBar,
    CardWidget,
    PrimaryPushButton,
    StrongBodyLabel,
    setFont,
)
from ..message_dialog import MessageDialog


class ProgressPage(QFrame):
    installationCompleted = pyqtSignal()
    rebootRequested = pyqtSignal()

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 标题
        self.title = SubtitleLabel(self.i18n.get("installation_progress"), self)
        setFont(self.title, 24)
        layout.addWidget(self.title)

        # 创建卡片容器
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        # 添加顶部弹性空间
        card_layout.addStretch()

        # 标题
        self.install_title = SubtitleLabel(self.i18n.get("installing"), self)
        setFont(self.install_title, 20)
        self.install_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.install_title)

        card_layout.addSpacing(20)

        # 进度消息
        self.progress_label = StrongBodyLabel(self.i18n.get("please_wait"), self)
        self.progress_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.progress_label)

        card_layout.addSpacing(20)

        # 进度条
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setFixedWidth(400)
        self.progress_bar.setFixedHeight(8)  # 设置进度条高度
        card_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # 进度百分比标签
        self.percentage_label = StrongBodyLabel("0%", self)
        self.percentage_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.percentage_label)

        card_layout.addSpacing(20)

        # 重启按钮
        self.reboot_btn = PrimaryPushButton(self.i18n.get("reboot"), self)
        self.reboot_btn.setFixedWidth(200)
        self.reboot_btn.clicked.connect(self.rebootRequested.emit)
        self.reboot_btn.hide()
        card_layout.addWidget(self.reboot_btn, alignment=Qt.AlignCenter)

        # 添加底部弹性空间
        card_layout.addStretch()

        # 将卡片添加到主布局
        layout.addWidget(card, stretch=1)

    def update_progress(self, progress, message):
        percentage = int(progress * 100)
        self.percentage_label.setText(f"{percentage}%")
        self.progress_label.setText(message)
        self.progress_bar.setValue(percentage)

    def show_completion(self):
        self.progress_bar.setValue(100)
        self.percentage_label.setText("100%")
        self.install_title.setText(self.i18n.get("install_complete"))
        self.progress_label.setText("")
        self.reboot_btn.show()
        self.installationCompleted.emit()

        # 显示安装成功的提示信息
        success_message = self.i18n.get("install_success_message")
        MessageDialog(self.i18n.get("install_success"), success_message, self).exec()

    def show_error(self):
        self.install_title.setText(self.i18n.get("install_failed"))
        self.progress_label.setText(self.i18n.get("install_failed"))
        self.reboot_btn.hide()

    def update_texts(self):
        self.title.setText(self.i18n.get("installation_progress"))
        self.install_title.setText(self.i18n.get("installing"))
        self.progress_label.setText(self.i18n.get("please_wait"))
        self.reboot_btn.setText(self.i18n.get("reboot"))
