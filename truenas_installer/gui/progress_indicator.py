from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import IndeterminateProgressBar, StrongBodyLabel


class ProgressIndicator(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent=parent)
        self.initUI(text)

    def initUI(self, text):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.progress_bar = IndeterminateProgressBar(self)
        self.progress_bar.setFixedWidth(400)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        self.message_label = StrongBodyLabel(text, self)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

    def setText(self, text):
        self.message_label.setText(text)

    def show(self):
        super().show()
        self.progress_bar.show()
        self.message_label.show()

    def hide(self):
        super().hide()
        self.progress_bar.hide()
        self.message_label.hide()
