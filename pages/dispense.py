from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from widgets.card import CardWidget, WarningBanner, StatusBanner
from widgets.top_bar import TopBar


class DispenseWidget(QWidget):
    go_back = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top_bar = TopBar("Manual Dispense")
        top_bar.back_clicked.connect(self.go_back.emit)
        layout.addWidget(top_bar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(10)

        form_card = CardWidget()
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setSpacing(8)
        med_selector = QComboBox()
        med_selector.addItems(["Lisinopril 10mg", "Metformin 500mg", "Atorvastatin 20mg"])
        form_layout.addWidget(QLabel("Medication"))
        form_layout.addWidget(med_selector)

        quantity_row = QHBoxLayout()
        quantity_row.addWidget(QLabel("Qty"))
        quantity_row.addStretch(1)
        quantity_value = QLabel("2")
        quantity_value.setAlignment(Qt.AlignCenter)
        quantity_value.setStyleSheet("font-size: 20px; font-weight: 700;")
        quantity_row.addWidget(quantity_value)
        quantity_row.addStretch(1)
        quantity_row.addWidget(QLabel("[-]  [+]"))
        form_layout.addLayout(quantity_row)

        override_row = QHBoxLayout()
        override_left = QVBoxLayout()
        override_left.addWidget(QLabel("Confirm override"))
        override_left.addWidget(QLabel("Required to enable dispense"))
        override_row.addLayout(override_left, 1)
        override_row.addWidget(QLabel("ON"))
        form_layout.addLayout(override_row)
        body_layout.addWidget(form_card)

        warning = WarningBanner()
        warning_layout = QVBoxLayout(warning)
        warning_layout.setContentsMargins(12, 10, 12, 10)
        warning_layout.addWidget(QLabel("Manual dispense bypasses the automated schedule. Use only when necessary."))
        body_layout.addWidget(warning)

        success = StatusBanner()
        success_layout = QVBoxLayout(success)
        success_layout.setContentsMargins(12, 12, 12, 12)
        success_layout.addWidget(QLabel("Dispensed successfully!"))
        body_layout.addWidget(success)

        body_layout.addWidget(QLabel("Dispense Now"))
        layout.addWidget(body)
