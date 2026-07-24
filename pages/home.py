from __future__ import annotations

from PyQt5.QtCore import QDateTime, QTimer, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QVBoxLayout, QWidget

from widgets.card import CardWidget, StatusBanner
from widgets.nav_card import NavCardButton


class HomeWidget(QWidget):
    navigate = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(112)
        header.setStyleSheet("background: #0F172A;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 10, 12, 10)
        header_layout.setSpacing(10)

        left_column = QVBoxLayout()
        left_column.setSpacing(2)
        pillba_label = QLabel("PILLBA")
        pillba_label.setProperty("class", "micro-label")
        pillba_label.setStyleSheet("color: rgba(248, 250, 252, 0.55); letter-spacing: 2px;")
        self.clock_label = QLabel("--:--")
        self.clock_label.setProperty("class", "clock")
        self.date_label = QLabel("--")
        self.date_label.setProperty("class", "caption")
        self.date_label.setStyleSheet("color: rgba(248, 250, 252, 0.6);")
        left_column.addWidget(pillba_label)
        left_column.addWidget(self.clock_label)
        left_column.addWidget(self.date_label)

        right_column = QVBoxLayout()
        right_column.setAlignment(Qt.AlignRight | Qt.AlignTop)
        right_column.setSpacing(4)
        online_badge = QLabel("● Online")
        online_badge.setStyleSheet(
            "background: rgba(13, 148, 136, 0.2); color: #14B8A6; border-radius: 10px; padding: 3px 8px; font-size: 11px; font-weight: 700;"
        )
        self.next_dose_label = QLabel("Next: --:--")
        self.next_dose_label.setProperty("class", "caption")
        self.next_dose_label.setStyleSheet("color: rgba(248, 250, 252, 0.55);")
        right_column.addWidget(online_badge, 0, Qt.AlignRight)
        right_column.addWidget(self.next_dose_label, 0, Qt.AlignRight)

        header_layout.addLayout(left_column, 1)
        header_layout.addLayout(right_column)

        nav_grid = QGridLayout()
        nav_grid.setContentsMargins(12, 12, 12, 12)
        nav_grid.setSpacing(10)

        nav_cards = [
            ("View Schedule", "Manage daily doses", "#0D9488", 1),
            ("Manual Dispense", "Bypass schedule", "#F59E0B", 3),
            ("View Log", "Track recent events", "#3B82F6", 4),
            ("Device Settings", "Wi-Fi and alerts", "#475569", 5),
        ]
        for index, (title, subtitle, color, target) in enumerate(nav_cards):
            card = NavCardButton(title, subtitle, color, target)
            card.clicked.connect(lambda checked=False, value=target: self.navigate.emit(value))
            row = index // 2
            col = index % 2
            nav_grid.addWidget(card, row, col)

        footer = QWidget()
        footer.setFixedHeight(32)
        footer.setStyleSheet("border-top: 1px solid #E2E8F0; background: #F8FAFC;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 0, 12, 0)
        footer_layout.setSpacing(8)
        self.compartments_label = QLabel("Compartments: 0/8 filled")
        self.compartments_label.setProperty("class", "caption")
        footer_layout.addWidget(self.compartments_label)
        footer_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_clock)
        self._timer.start(1000)
        self._update_clock()

        layout.addWidget(header)
        layout.addLayout(nav_grid, 1)
        layout.addWidget(footer)

    def _update_clock(self) -> None:
        now = QDateTime.currentDateTime()
        self.clock_label.setText(now.toString("hh:mm"))
        self.date_label.setText(now.toString("ddd, MMM d"))
        self.next_dose_label.setText("Next: 14:00")

    def on_device_status(self, status: object) -> None:
        filled = getattr(status, "compartments_filled", 0)
        self.compartments_label.setText(f"Compartments: {filled}/8 filled")

