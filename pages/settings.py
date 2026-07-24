from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget, QComboBox

from widgets.card import CardWidget
from widgets.toggle_switch import ToggleSwitchWidget
from widgets.top_bar import TopBar


class SettingsWidget(QWidget):
    go_back = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top_bar = TopBar("Settings")
        top_bar.back_clicked.connect(self.go_back.emit)
        layout.addWidget(top_bar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(10)

        connectivity = CardWidget()
        conn_layout = QVBoxLayout(connectivity)
        conn_layout.setContentsMargins(12, 12, 12, 12)
        conn_layout.setSpacing(10)
        conn_layout.addWidget(QLabel("Connectivity"))
        for label_text, state_text in [("Wi-Fi", "Home network"), ("Bluetooth", "Off")]:
            row = QHBoxLayout()
            left = QVBoxLayout()
            left.addWidget(QLabel(label_text))
            left.addWidget(QLabel(state_text))
            row.addLayout(left, 1)
            row.addWidget(ToggleSwitchWidget())
            conn_layout.addLayout(row)
        body_layout.addWidget(connectivity)

        notifications = CardWidget()
        notif_layout = QVBoxLayout(notifications)
        notif_layout.setContentsMargins(12, 12, 12, 12)
        notif_layout.setSpacing(10)
        notif_layout.addWidget(QLabel("Notifications"))
        row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Refill Alert"))
        left.addWidget(QLabel("Notify when pills are low"))
        row.addLayout(left, 1)
        row.addWidget(ToggleSwitchWidget())
        notif_layout.addLayout(row)
        volume_row = QHBoxLayout()
        volume_row.addWidget(QLabel("Volume"))
        volume_row.addWidget(QLabel("70%"), 0, Qt.AlignRight)
        notif_layout.addLayout(volume_row)
        slider = QSlider(Qt.Horizontal)
        slider.setValue(70)
        notif_layout.addWidget(slider)
        body_layout.addWidget(notifications)

        system = CardWidget()
        sys_layout = QVBoxLayout(system)
        sys_layout.setContentsMargins(12, 12, 12, 12)
        sys_layout.setSpacing(10)
        sys_layout.addWidget(QLabel("System"))
        tz = QComboBox()
        tz.addItems(["UTC-8", "UTC-5", "UTC+0", "UTC+1", "UTC+2", "UTC+5:30", "UTC+8"])
        sys_layout.addWidget(QLabel("Timezone"))
        sys_layout.addWidget(tz)
        info = QLabel("Firmware v2.4.1 · Serial #MD-00421")
        info.setStyleSheet("font-size: 11px; color: #64748B;")
        sys_layout.addWidget(info)
        reset = QLabel("Factory Reset")
        reset.setAlignment(Qt.AlignCenter)
        reset.setStyleSheet("background: #FEF2F2; color: #EF4444; border: 1px solid rgba(239,68,68,0.2); border-radius: 8px; min-height: 36px; font-weight: 700;")
        sys_layout.addWidget(reset)
        body_layout.addWidget(system)

        layout.addWidget(body)
