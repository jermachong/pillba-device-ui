from __future__ import annotations

from dataclasses import dataclass

from PyQt5.QtCore import QThread, pyqtSignal


@dataclass(frozen=True)
class DeviceStatus:
    battery_pct: int = 100
    wifi_rssi: int = -42
    compartments_filled: int = 0
    error_flags: int = 0


class SerialWorker(QThread):
    device_status = pyqtSignal(object)

    def __init__(self, port: str = "/dev/ttyAMA0", baud: int = 115200) -> None:
        super().__init__()
        self.port = port
        self.baud = baud

    def run(self) -> None:
        self.device_status.emit(DeviceStatus())
