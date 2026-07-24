from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

# from db import list_medications
from widgets.card import CardWidget
from widgets.chart_widgets import ChartPlaceholder
from widgets.toggle_switch import ToggleSwitchWidget
from widgets.top_bar import TopBar


class ScheduleWidget(QWidget):
    go_back = pyqtSignal()
    go_add = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top_bar = TopBar("Schedule")
        top_bar.back_clicked.connect(self.go_back.emit)
        layout.addWidget(top_bar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(10)

        adherence_card = CardWidget()
        adherence_layout = QVBoxLayout(adherence_card)
        adherence_layout.setContentsMargins(12, 12, 12, 12)
        adherence_layout.setSpacing(8)
        adherence_label = QLabel("WEEKLY ADHERENCE")
        adherence_label.setProperty("class", "micro-label")
        adherence_layout.addWidget(adherence_label)
        adherence_layout.addWidget(ChartPlaceholder("taken / missed"))

        body_layout.addWidget(adherence_card)

        # for medication in list_medications():
        #     row_card = CardWidget()
        #     row_layout = QHBoxLayout(row_card)
        #     row_layout.setContentsMargins(12, 12, 12, 12)
        #     row_layout.setSpacing(10)

        #     icon = QLabel("●")
        #     icon.setAlignment(Qt.AlignCenter)
        #     icon.setFixedSize(32, 32)
        #     icon.setStyleSheet("background: rgba(13, 148, 136, 0.12); color: #0D9488; border-radius: 16px;")

        #     text_column = QVBoxLayout()
        #     text_column.setSpacing(2)
        #     name_label = QLabel(medication.name)
        #     name_label.setProperty("class", "card-title")
        #     dose_label = QLabel(f"{medication.dose} · {medication.hour:02d}:{medication.minute:02d}")
        #     dose_label.setProperty("class", "caption")
        #     text_column.addWidget(name_label)
        #     text_column.addWidget(dose_label)

        #     toggle = ToggleSwitchWidget()
        #     toggle.setChecked(bool(medication.active))

        #     row_layout.addWidget(icon)
        #     row_layout.addLayout(text_column, 1)
        #     row_layout.addWidget(toggle)
        #     body_layout.addWidget(row_card)

        add_button = QLabel("Add Medication")
        add_button.setAlignment(Qt.AlignCenter)
        add_button.setStyleSheet("background: #0D9488; color: #FFFFFF; border-radius: 12px; font-size: 12px; font-weight: 700; min-height: 40px;")
        add_button.mousePressEvent = lambda event: self.go_add.emit()
        body_layout.addWidget(add_button)
        body_layout.addStretch(1)

        layout.addWidget(body)
