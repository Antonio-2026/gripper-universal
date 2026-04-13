"""Entry point for the Universal Gripper Control desktop app."""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from gripper_control.core.controller import GripperController
from gripper_control.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    GripperController(window)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
