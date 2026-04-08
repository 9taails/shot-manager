from PySide6 import QtWidgets
import sys
from ShotManager import ShotManager

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ShotManager()
    window.show()
    app.exec()
