from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class ChartPlaceholder(QWidget):
    def __init__(self, label: str, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.title = QLabel(label)
        self.title.setProperty("class", "micro-label")
        layout.addWidget(self.title)
        layout.addWidget(_MiniChart())


class _MiniChart(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(76)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)

        width = self.width()
        height = self.height()
        points = [0.18, 0.42, 0.35, 0.62, 0.58, 0.80, 0.72]
        bar_width = max(10, int((width - 24) / (len(points) * 1.25)))
        gap = bar_width // 2
        x = 12
        painter.setPen(Qt.NoPen)
        for index, value in enumerate(points):
            bar_height = max(8, int((height - 18) * value))
            color = QColor("#0D9488") if index % 2 == 0 else QColor("#14B8A6")
            painter.setBrush(color)
            painter.drawRoundedRect(x, height - bar_height - 8, bar_width, bar_height, 3, 3)
            x += bar_width + gap
