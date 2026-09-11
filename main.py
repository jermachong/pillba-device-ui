from __future__ import annotations

import os
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

from pages.add_medication import AddMedicationWidget
from pages.dispense import DispenseWidget
from pages.home import HomeWidget
from pages.log import LogWidget
from pages.schedule import ScheduleWidget
from pages.settings import SettingsWidget
from serial_worker import SerialWorker
from lcd_display import ST7796Display, qimage_to_pil


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
    lcd_enabled = os.environ.get("PILLBA_LCD") == "1"
    if lcd_enabled:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    app = QApplication(sys.argv)
    window = MainWindow()

    if not lcd_enabled:
        window.showFullScreen()
        return app.exec_()

    window.show()
    lcd = ST7796Display()

    def refresh_lcd() -> None:
        app.processEvents()
        lcd.show(qimage_to_pil(window.grab().toImage()))

    refresh_timer = QTimer(window)
    refresh_timer.timeout.connect(refresh_lcd)
    refresh_timer.start(200)
    refresh_lcd()

    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
