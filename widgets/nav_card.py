from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton


class NavCardButton(QPushButton):
    clicked_index = pyqtSignal(int)

    def __init__(self, title: str, subtitle: str, color: str, index: int, parent=None) -> None:
        super().__init__(parent)
        self.index = index
        self._color = QColor(color)
        self.setProperty("class", "nav-card")
        self.setMinimumHeight(104)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        icon_row = QLabel("")
        icon_row.setMinimumSize(36, 36)
        icon_row.setMaximumSize(36, 36)
        icon_row.setStyleSheet("background: rgba(255, 255, 255, 0.18); border-radius: 8px;")

        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "nav-title")

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setProperty("class", "nav-subtitle")

        self.chevron = QLabel("›")
        self.chevron.setProperty("class", "nav-chevron")
        self.chevron.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        layout.addWidget(icon_row, 0, Qt.AlignLeft)
        layout.addStretch(1)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.chevron)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._color)
        painter.drawRoundedRect(self.rect(), 12, 12)
        super().paintEvent(event)
