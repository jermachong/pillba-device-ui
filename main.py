from __future__ import annotations

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

from pages.add_medication import AddMedicationWidget
from pages.dispense import DispenseWidget
from pages.home import HomeWidget
from pages.log import LogWidget
from pages.schedule import ScheduleWidget
from pages.settings import SettingsWidget
from serial_worker import SerialWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("root")
        self.setFixedSize(320, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self._load_fonts()
        self._load_styles()

        self.stack = QStackedWidget()
        self.home = HomeWidget()
        self.schedule = ScheduleWidget()
        self.add_med = AddMedicationWidget()
        self.dispense = DispenseWidget()
        self.log = LogWidget()
        self.settings_page = SettingsWidget()

        for widget in [
            self.home,
            self.schedule,
            self.add_med,
            self.dispense,
            self.log,
            self.settings_page,
        ]:
            self.stack.addWidget(widget)

        self.setCentralWidget(self.stack)

        self.home.navigate.connect(self.go_to)
        self.schedule.go_back.connect(lambda: self.go_to(0))
        self.schedule.go_add.connect(lambda: self.go_to(2))
        self.add_med.go_back.connect(lambda: self.go_to(1))
        self.dispense.go_back.connect(lambda: self.go_to(0))
        self.log.go_back.connect(lambda: self.go_to(0))
        self.settings_page.go_back.connect(lambda: self.go_to(0))

        self.worker = SerialWorker()
        self.worker.device_status.connect(self.home.on_device_status)

    def _load_fonts(self) -> None:
        for font_name in [
            "Nunito-Regular.ttf",
            "Nunito-SemiBold.ttf",
            "Nunito-Bold.ttf",
        ]:
            font_path = os.path.join(os.path.dirname(__file__), "fonts", font_name)
            if os.path.exists(font_path):
                QFontDatabase.addApplicationFont(font_path)

    def _load_styles(self) -> None:
        style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        with open(style_path, encoding="utf-8") as handle:
            self.setStyleSheet(handle.read())

    def go_to(self, index: int) -> None:
        self.stack.setCurrentIndex(index)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
