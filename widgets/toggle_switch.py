from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt5.QtWidgets import QAbstractButton


class ToggleSwitchWidget(QAbstractButton):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._thumb_x = 2.0
        self._animation = QPropertyAnimation(self, b"thumb_x", self)
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._thumb_x)
        self._animation.setEndValue(22.0 if checked else 2.0)
        self._animation.start()

    def get_thumb_x(self) -> float:
        return self._thumb_x

    def set_thumb_x(self, value: float) -> None:
        self._thumb_x = value
        self.update()

    thumb_x = pyqtProperty(float, get_thumb_x, set_thumb_x)
