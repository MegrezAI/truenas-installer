from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class ProgressPage(QWidget):
    installationCompleted = pyqtSignal()
    rebootRequested = pyqtSignal()
    
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        self.title = QLabel(self.i18n.get("installation_progress"))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title)

        self.progress_label = QLabel(self.i18n.get("please_wait"))
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(400)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        
        self.reboot_btn = QPushButton(self.i18n.get("reboot"))
        self.reboot_btn.setFixedWidth(200)
        self.reboot_btn.clicked.connect(self.rebootRequested.emit)
        self.reboot_btn.hide()
        layout.addWidget(self.reboot_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def update_progress(self, progress, message):
        percentage = int(progress * 100)
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)

    def show_completion(self):
        self.progress_bar.setValue(100)
        self.progress_label.setText(self.i18n.get("install_complete"))
        self.reboot_btn.show()
        self.installationCompleted.emit()

    def show_error(self):
        self.progress_label.setText(self.i18n.get("install_failed"))
        self.reboot_btn.hide()

    def update_texts(self):
        self.title.setText(self.i18n.get("installation_progress"))
        self.progress_label.setText(self.i18n.get("please_wait"))
        self.reboot_btn.setText(self.i18n.get("reboot")) 