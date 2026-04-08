from PySide6.QtWidgets import QApplication
import sys
from ShotManager import ShotManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShotManager()
    window.show()
    app.exec()
