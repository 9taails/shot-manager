from PySide6.QtCore import (
    QSize,
    QMetaObject
)
from PySide6.QtGui import (
    QFont,
    QIcon,
    Qt
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QPushButton,
    QSpacerItem,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QMainWindow,
    QTreeView, 
    QHeaderView
)

from source.util_paths import Paths


class ShotManagerWindow(QMainWindow):
    def setup_ui(self, shotManager_window):
        if not shotManager_window.objectName():
            shotManager_window.setObjectName(u"shotManager_window")

        sizePolicy_mainWindow = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy_pushButtons = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        font = QFont("Open Sans", 11, 5)
        font2 = QFont("Open Sans Bold", 10, 75)
        font2.setBold(True)

        shotManager_window.setSizePolicy(sizePolicy_mainWindow)
        sizePolicy_mainWindow.setHeightForWidth(shotManager_window.sizePolicy().hasHeightForWidth())
        shotManager_window.setMinimumSize(QSize(600, 800))
        shotManager_window.setMaximumSize(QSize(600, 1200))
        shotManager_window.setFont(font)

        style_sheet_file = Paths.resource_file("style_sheet.css")

        # Load the CSS style sheet
        with open(style_sheet_file, "r") as file:
            style_sheet = file.read()

        shotManager_window.setStyleSheet(style_sheet)

        self.centralwidget = QWidget(shotManager_window)
        self.centralwidget.setObjectName(u"central_widget")
        self.centralwidget.setMinimumSize(QSize(0, 50))
        self.centralwidget.setFont(font)

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"mainWindow_layout")

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"dummy_widget")
        self.widget.setMinimumSize(QSize(0, 50))

        self.button_layout = QHBoxLayout(self.widget)
        self.button_layout.setSpacing(10)
        self.button_layout.setObjectName(u"button_layout")
        self.button_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.button_layout.setContentsMargins(10, -1, -1, -1)

        self.newShot_button = QPushButton(self.widget)
        self.newShot_button.setObjectName(u"newShot_button")
        self.newShot_button.setSizePolicy(sizePolicy_pushButtons)
        self.newShot_button.setMinimumSize(QSize(100, 0))
        self.newShot_button.setFont(font2)

        self.newLayer_button = QPushButton(self.widget)
        self.newLayer_button.setObjectName(u"newLayer_button")
        self.newLayer_button.setSizePolicy(sizePolicy_pushButtons)
        self.newLayer_button.setMinimumSize(QSize(100, 0))
        self.newLayer_button.setFont(font2)

        sizePolicy_pushButtons.setHeightForWidth(self.newShot_button.sizePolicy().hasHeightForWidth())
        sizePolicy_pushButtons.setHeightForWidth(self.newLayer_button.sizePolicy().hasHeightForWidth())

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.sync_button = QToolButton(self.widget)
        self.sync_button.setObjectName(u"sync_button")

        self.sync_button.setIcon(QIcon(Paths.icon("refresh.png")))
        self.sync_button.setIconSize(QSize(24, 24))

        self.update_button = QToolButton(self.widget)
        self.update_button.setObjectName(u"update_button")
        self.update_button.setIcon(QIcon(Paths.icon("refresh.png")))
        self.update_button.setIconSize(QSize(24, 24))

        self.button_layout.addWidget(self.newShot_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.button_layout.addWidget(self.newLayer_button, 0, Qt.AlignmentFlag.AlignLeft)
        self.button_layout.addItem(self.horizontalSpacer)
        self.button_layout.addWidget(self.sync_button)
        self.button_layout.addWidget(self.update_button)

        self.verticalLayout.addWidget(self.widget, 0, Qt.AlignmentFlag.AlignVCenter)

        self.shotList_treeWidget = QTreeView()

        """ __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"")"""
        #header = QHeaderView(Qt.Orientation.Horizontal, self.shotList_treeWidget)

        #self.shotList_treeWidget.setHeader(header)
        self.shotList_treeWidget.setObjectName(u"shotList_treeWidget")
        self.shotList_treeWidget.setFont(font)
        self.shotList_treeWidget.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.shotList_treeWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.shotList_treeWidget.setIconSize(QSize(10, 10))
        self.shotList_treeWidget.setRootIsDecorated(True)
        self.shotList_treeWidget.setSortingEnabled(True)
        self.shotList_treeWidget.header().setVisible(False)

        self.verticalLayout.addWidget(self.shotList_treeWidget)

        shotManager_window.setCentralWidget(self.centralwidget)

        self.newShot_button.setDefault(True)
        self.newLayer_button.setDefault(True)

        QMetaObject.connectSlotsByName(shotManager_window)
        shotManager_window.setWindowTitle("Shot Manager 1.0")
        self.newShot_button.setToolTip("Add new shot to the scene.")
        self.newShot_button.setText("new shot")
        self.newLayer_button.setToolTip("Add a new render layer to selected shot.")
        self.newLayer_button.setText("new layer")
