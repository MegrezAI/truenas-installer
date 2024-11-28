from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                           QGridLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

class AuthPage(QWidget):
    installationRequested = pyqtSignal(dict)  # auth_method
    
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        self.title = QLabel(self.i18n.get("authentication"))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title)

        # Auth method
        self.auth_label = QLabel(self.i18n.get("web_ui_auth"))
        self.auth_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.auth_label)

        self.auth_combo = QComboBox()
        self.auth_combo.addItems([
            self.i18n.get("admin_user"),
            self.i18n.get("configure_webui")
        ])
        self.auth_combo.setFixedWidth(300)
        layout.addWidget(self.auth_combo, alignment=Qt.AlignCenter)

        # Password fields
        self.password_widget = QWidget()
        pass_layout = QGridLayout()
        pass_layout.setSpacing(10)
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedWidth(200)
        
        self.pass_confirm = QLineEdit()
        self.pass_confirm.setEchoMode(QLineEdit.Password)
        self.pass_confirm.setFixedWidth(200)
        
        self.pass_label = QLabel(self.i18n.get("password"))
        self.confirm_label = QLabel(self.i18n.get("confirm_password"))
        
        pass_layout.addWidget(self.pass_label, 0, 0)
        pass_layout.addWidget(self.pass_input, 0, 1)
        pass_layout.addWidget(self.confirm_label, 1, 0)
        pass_layout.addWidget(self.pass_confirm, 1, 1)
        
        self.password_widget.setLayout(pass_layout)
        layout.addWidget(self.password_widget, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def validate_and_get_auth(self):
        if self.auth_combo.currentText() == self.i18n.get("admin_user"):
            if self.pass_input.text() != self.pass_confirm.text():
                QMessageBox.warning(self, "Error", self.i18n.get("passwords_not_match"))
                return None
            return {
                "username": "truenas_admin",
                "password": self.pass_input.text()
            }
        return None

    def update_texts(self):
        self.title.setText(self.i18n.get("authentication"))
        self.auth_label.setText(self.i18n.get("web_ui_auth"))
        
        self.auth_combo.clear()
        self.auth_combo.addItems([
            self.i18n.get("admin_user"),
            self.i18n.get("configure_webui")
        ])
        
        self.pass_label.setText(self.i18n.get("password"))
        self.confirm_label.setText(self.i18n.get("confirm_password"))