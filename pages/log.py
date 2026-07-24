from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from widgets.card import CardWidget
from widgets.chart_widgets import ChartPlaceholder
from widgets.status_badge import StatusBadge
from widgets.top_bar import TopBar


class LogWidget(QWidget):
    go_back = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top_bar = TopBar("Activity Log")
        top_bar.back_clicked.connect(self.go_back.emit)
        layout.addWidget(top_bar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(10)

        chart_card = CardWidget()
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(12, 12, 12, 12)
        chart_layout.setSpacing(8)
        chart_label = QLabel("LAST 7 DAYS")
        chart_label.setProperty("class", "micro-label")
        chart_layout.addWidget(chart_label)
        chart_layout.addWidget(ChartPlaceholder("taken / missed"))

        body_layout.addWidget(chart_card)

        today_label = QLabel("TODAY")
        today_label.setProperty("class", "micro-label")
        body_layout.addWidget(today_label)

        entries = [
            ("Lisinopril", "08:00", "taken", "✓"),
            ("Metformin", "12:00", "missed", "✗"),
            ("Atorvastatin", "19:00", "manual", "↻"),
        ]
        for name, time_text, status, icon_text in entries:
            entry_card = CardWidget()
            entry_layout = QHBoxLayout(entry_card)
            entry_layout.setContentsMargins(12, 12, 12, 12)
            entry_layout.setSpacing(10)
            icon = QLabel(icon_text)
            icon.setAlignment(Qt.AlignCenter)
            icon.setFixedSize(32, 32)
            if status == "taken":
                icon.setStyleSheet("background: #F0FDFA; color: #0D9488; border-radius: 16px;")
            elif status == "missed":
                icon.setStyleSheet("background: #FEF2F2; color: #EF4444; border-radius: 16px;")
            else:
                icon.setStyleSheet("background: #FFFBEB; color: #F59E0B; border-radius: 16px;")
            text_column = QVBoxLayout()
            text_column.setSpacing(2)
            name_label = QLabel(name)
            name_label.setStyleSheet("font-size: 12px; font-weight: 700;")
            time_label = QLabel(time_text)
            time_label.setStyleSheet("font-size: 11px; color: #64748B;")
            text_column.addWidget(name_label)
            text_column.addWidget(time_label)
            badge = StatusBadge(status.capitalize())
            badge.set_status(status)
            entry_layout.addWidget(icon)
            entry_layout.addLayout(text_column, 1)
            entry_layout.addWidget(badge)
            body_layout.addWidget(entry_card)

        layout.addWidget(body)
