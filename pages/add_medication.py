from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from widgets.card import CardWidget, StatusBanner, WarningBanner
from widgets.top_bar import TopBar


class AddMedicationWidget(QWidget):
    go_back = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top_bar = TopBar("Add Medication")
        top_bar.back_clicked.connect(self.go_back.emit)
        layout.addWidget(top_bar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(10)

        stepper = CardWidget()
        stepper_layout = QHBoxLayout(stepper)
        stepper_layout.setContentsMargins(12, 10, 12, 10)
        stepper_layout.setSpacing(8)
        for index in range(4):
            circle = QLabel(str(index + 1))
            circle.setAlignment(Qt.AlignCenter)
            circle.setFixedSize(20, 20)
            if index == 0:
                circle.setStyleSheet("background: #0D9488; color: #FFFFFF; border-radius: 10px; font-size: 10px; font-weight: 700;")
            else:
                circle.setStyleSheet("background: #E2E8F0; color: #64748B; border-radius: 10px; font-size: 10px; font-weight: 700;")
            stepper_layout.addWidget(circle)
            if index < 3:
                connector = QLabel("")
                connector.setFixedHeight(2)
                connector.setStyleSheet("background: #E2E8F0;")
                stepper_layout.addWidget(connector, 1)

        body_layout.addWidget(stepper)

        instruction = QLabel("Point camera at prescription bottle")
        instruction.setStyleSheet("font-size: 12px; font-weight: 700; color: #0F172A;")
        body_layout.addWidget(instruction)

        camera_card = CardWidget()
        camera_card.setMinimumHeight(184)
        camera_card.setStyleSheet("background: #0F172A; border-radius: 12px;")
        camera_layout = QVBoxLayout(camera_card)
        camera_layout.setContentsMargins(12, 12, 12, 12)
        camera_layout.setSpacing(8)
        camera_view = QLabel("Camera preview")
        camera_view.setAlignment(Qt.AlignCenter)
        camera_view.setMinimumHeight(126)
        camera_view.setStyleSheet("background: #111827; color: rgba(248, 250, 252, 0.65); border-radius: 12px;")
        scan_bar = QProgressBar()
        scan_bar.setValue(72)
        scan_bar.setTextVisible(False)
        camera_layout.addWidget(camera_view)
        camera_layout.addWidget(scan_bar)
        body_layout.addWidget(camera_card)

        detection = StatusBanner()
        detection_layout = QVBoxLayout(detection)
        detection_layout.setContentsMargins(12, 12, 12, 12)
        detection_layout.setSpacing(2)
        detected_title = QLabel("Detected: Lisinopril 10mg")
        detected_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #0F172A;")
        detected_caption = QLabel("Compartment 4 assigned")
        detected_caption.setStyleSheet("font-size: 11px; color: #64748B;")
        detection_layout.addWidget(detected_title)
        detection_layout.addWidget(detected_caption)
        body_layout.addWidget(detection)

        compartment_card = CardWidget()
        compartment_layout = QVBoxLayout(compartment_card)
        compartment_layout.setContentsMargins(12, 12, 12, 12)
        compartment_layout.setSpacing(8)
        compartment_label = QLabel("Open the correct compartment lid")
        compartment_label.setStyleSheet("font-size: 12px; font-weight: 700;")
        compartment_grid = QGridLayout()
        compartment_grid.setHorizontalSpacing(6)
        compartment_grid.setVerticalSpacing(6)
        for index in range(8):
            slot = QLabel(str(index + 1))
            slot.setAlignment(Qt.AlignCenter)
            slot.setFixedSize(60, 40)
            if index == 3:
                slot.setStyleSheet("background: #0D9488; color: #FFFFFF; border-radius: 8px; font-weight: 700;")
            else:
                slot.setStyleSheet("background: #E2E8F0; color: #64748B; border-radius: 8px; font-weight: 700;")
            compartment_grid.addWidget(slot, index // 4, index % 4)
        warning = WarningBanner()
        warning_layout = QVBoxLayout(warning)
        warning_layout.setContentsMargins(12, 10, 12, 10)
        warning_layout.addWidget(QLabel("Only open Compartment 4. Do not open other lids while the dispenser is active."))
        compartment_layout.addWidget(compartment_label)
        compartment_layout.addLayout(compartment_grid)
        compartment_layout.addWidget(warning)
        body_layout.addWidget(compartment_card)

        fill_card = CardWidget()
        fill_layout = QVBoxLayout(fill_card)
        fill_layout.setContentsMargins(12, 12, 12, 12)
        fill_layout.setSpacing(6)
        fill_title = QLabel("Pour pills into Compartment 4")
        fill_title.setStyleSheet("font-size: 12px; font-weight: 700;")
        fill_progress = QProgressBar()
        fill_progress.setValue(93)
        fill_progress.setTextVisible(True)
        fill_caption = QLabel("Keep pouring… sensor is reading")
        fill_caption.setStyleSheet("font-size: 11px; color: #64748B;")
        fill_layout.addWidget(fill_title)
        fill_layout.addWidget(fill_progress)
        fill_layout.addWidget(fill_caption)
        body_layout.addWidget(fill_card)

        done_card = CardWidget()
        done_layout = QVBoxLayout(done_card)
        done_layout.setContentsMargins(12, 12, 12, 12)
        done_layout.setSpacing(4)
        done_layout.addWidget(QLabel("Medication Added!"))
        done_layout.addWidget(QLabel("Lisinopril 10mg · Compartment 4"))
        body_layout.addWidget(done_card)

        layout.addWidget(body)
