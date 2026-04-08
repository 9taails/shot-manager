import sys
from PySide6.QtWidgets import QApplication
from source.ShotManager import ShotManager


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShotManager()
    window.show()
    app.exec()
