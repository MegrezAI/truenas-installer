from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

class LanguagePage(QWidget):
    languageChanged = pyqtSignal(str)
    
    def __init__(self, i18n, installer_version):
        super().__init__()
        self.i18n = i18n
        self.installer_version = installer_version
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Welcome title
        self.welcome_title = QLabel(self.i18n.get("welcome_title"))
        self.welcome_title.setAlignment(Qt.AlignCenter)
        self.welcome_title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2980b9;
        """)
        layout.addWidget(self.welcome_title)

        # Welcome message
        self.welcome_msg = QLabel(self.i18n.get("welcome_message"))
        self.welcome_msg.setAlignment(Qt.AlignCenter)
        self.welcome_msg.setWordWrap(True)
        self.welcome_msg.setStyleSheet("""
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        """)
        layout.addWidget(self.welcome_msg)

        # Language selection container
        lang_container = self._create_language_section()
        layout.addWidget(lang_container)
        
        layout.addStretch()
        
        # Version info
        version_label = QLabel(f"Version {self.installer_version}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #999; font-size: 12px;")
        layout.addWidget(version_label)

        self.setLayout(layout)

    def _create_language_section(self):
        lang_container = QFrame()
        lang_layout = QVBoxLayout(lang_container)
        lang_layout.setSpacing(15)

        # Title
        self.lang_title = QLabel(self.i18n.get("language_selection"))
        self.lang_title.setObjectName("languageSelectionLabel")
        self.lang_title.setAlignment(Qt.AlignCenter)
        self.lang_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)
        lang_layout.addWidget(self.lang_title)

        # Combobox
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "中文"])
        self.language_combo.setFixedWidth(200)
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        
        combo_container = QWidget()
        combo_layout = QHBoxLayout()
        combo_layout.addStretch()
        combo_layout.addWidget(self.language_combo)
        combo_layout.addStretch()
        combo_container.setLayout(combo_layout)
        
        lang_layout.addWidget(combo_container)
        
        return lang_container

    def _on_language_changed(self, selected_language):
        self.languageChanged.emit(selected_language)

    def update_texts(self):
        self.welcome_title.setText(self.i18n.get("welcome_title"))
        self.welcome_msg.setText(self.i18n.get("welcome_message"))
        self.lang_title.setText(self.i18n.get("language_selection"))
        