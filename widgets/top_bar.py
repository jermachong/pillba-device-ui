from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class TopBar(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(48)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)

        self.back_button = QPushButton("←")
        self.back_button.setObjectName("back-btn")
        self.back_button.setFixedSize(36, 36)
        self.back_button.clicked.connect(self.back_clicked.emit)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("topbar-title")
        self.title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.back_button)
        layout.addWidget(self.title_label, 1)

