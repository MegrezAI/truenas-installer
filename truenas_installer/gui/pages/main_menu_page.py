from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class MainMenuPage(QWidget):
    installationRequested = pyqtSignal()
    shellRequested = pyqtSignal()
    rebootRequested = pyqtSignal()
    shutdownRequested = pyqtSignal()
    
    def __init__(self, installer, i18n):
        super().__init__()
        self.installer = installer
        self.i18n = i18n
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel(f"{self.installer.vendor} {self.installer.version}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)

        # Create buttons
        buttons = [
            (self.i18n.get("install_upgrade"), self.installationRequested),
            (self.i18n.get("shell"), self.shellRequested),
            (self.i18n.get("reboot"), self.rebootRequested),
            (self.i18n.get("shutdown"), self.shutdownRequested)
        ]

        for text, signal in buttons:
            btn = QPushButton(text)
            btn.setFixedWidth(300)
            btn.setFixedHeight(40)
            btn.clicked.connect(signal.emit)
            buttons_layout.addWidget(btn, alignment=Qt.AlignCenter)

        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(buttons_widget)
        layout.addStretch()

        self.setLayout(layout)
        
    def update_texts(self):
        buttons = self.findChildren(QPushButton)
        button_texts = [
            self.i18n.get("install_upgrade"),
            self.i18n.get("shell"),
            self.i18n.get("reboot"),
            self.i18n.get("shutdown")
        ]
        for btn, text in zip(buttons, button_texts):
            btn.setText(text) 