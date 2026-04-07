from PySide6.QtCore import (
    QSize,
    QRect,
    QMetaObject
)
from PySide6.QtGui import (
    QFont,
    Qt
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QPushButton,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QAbstractSpinBox,
    QHBoxLayout,
    QCheckBox
)


class ShotBuilderUI(object):

    def setup_ui(self, createShots_dialog):
        if not createShots_dialog.objectName():
            createShots_dialog.setObjectName(u"createShots_dialog")

        size_policy_fixed = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        size_policy_fixed.setHorizontalStretch(0)
        size_policy_fixed.setVerticalStretch(0)
        size_policy_fixed.setHeightForWidth(createShots_dialog.sizePolicy().hasHeightForWidth())

        size_policy_min = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        size_policy_min.setHorizontalStretch(0)
        size_policy_min.setVerticalStretch(0)

        size_policy_preferred = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        size_policy_preferred.setHorizontalStretch(0)
        size_policy_preferred.setVerticalStretch(0)

        createShots_dialog.setSizePolicy(size_policy_fixed)
        createShots_dialog.setFixedSize(QSize(420, 260))

        font_bold = QFont("JetBrains Mono", 8, 50)
        font_bold.setBold(True)

        font_normal = QFont("JetBrains Mono", 8, 50)

        createShots_dialog.setFont(font_bold)
        createShots_dialog.setStyleSheet(
            "QWidget{"
            "background-color:rgb(41, 45, 56);"
            "color: rgb(125, 147, 154);"
            "border-color:rgb(125, 147, 154);}"
 
            "QLabel{"
            "background-color: rgb(41, 45, 56);"
            "color: rgb(125, 147, 154);"
            "border-color:  rgb(125, 147, 154);}"

            "QPushButton{"
            "background-color: rgb(22, 24, 30);"
            "color: rgb(125, 147, 154);"
            "border-style: solid;"
            "border-color: rgb(125, 147, 154);"
            "font-weight : bold;"
            "padding: 1px;}"

            "QPushButton::hover{"
            "background-color: rgb(125, 147, 154);"
            "color: #000000;"
            "border-style: solid;"
            "border-color: #000000;"
            "font-weight : bold;"
            "padding: 1px;}"

            "QPushButton::pressed{"
            "background-color:rgb(41, 45, 56);"
            "color: #000000;"
            "border-style: solid;"
            "border-color: #000000;"
            "font-weight : bold;"
            "padding: 1px;}"

            "QLineEdit{"
            "background-color: rgb(28, 31, 39);"
            "color:rgb(125, 147, 154);"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color:  rgb(41, 45, 56);"
            "padding: 1px;}"

            "QLineEdit::hover{"
            "background-color: rgb(41, 45, 56);"
            "color: #3e93ca;"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color:  rgb(125, 147, 154);"
            "padding: 1px;}"

            "QLineEdit::focus{"
            "color:  rgb(125, 147, 154);"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: rgb(125, 147, 154);"
            "padding: 1px;}"

            "QSpinBox{"
            "background-color: rgb(28, 31, 39);"
            "color:rgb(125, 147, 154);"
            "padding: 1px;}"

            "QCheckBox::indicator{"
            "background-color: rgb(28, 31, 39);"
            "color:  rgb(125, 147, 154);"
            "padding: 1px;}"

            "QCheckBox::indicator:checked{"
            "background-color: rgb(125, 147, 154);"
            "color:  rgb(125, 147, 154);"
            "padding: 1px;}"

        )

        self.add_shots_button = QPushButton(createShots_dialog)
        self.add_shots_button.setObjectName(u"addShots_button")
        self.add_shots_button.setEnabled(True)
        self.add_shots_button.setGeometry(QRect(110, 160, 191, 41))
        self.add_shots_button.setSizePolicy(size_policy_min)
        self.add_shots_button.setFont(font_bold)

        self.gridLayoutWidget = QWidget(createShots_dialog)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 390, 91))
        self.gridLayoutWidget.setFont(font_bold)

        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setColumnMinimumWidth(2, 20)

        self.shot_length_value = QLineEdit(self.gridLayoutWidget)
        self.shot_length_value.setObjectName(u"shotLength_input")
        self.shot_length_value.setEnabled(True)
        self.shot_length_value.setSizePolicy(size_policy_min)
        self.shot_length_value.setMaximumSize(QSize(80, 40))
        self.shot_length_value.setFont(font_normal)
        self.shot_length_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.shot_count_value = QSpinBox(self.gridLayoutWidget)
        self.shot_count_value.setObjectName(u"numberOfShots_input")
        self.shot_count_value.setEnabled(True)
        self.shot_count_value.setSizePolicy(size_policy_preferred)
        self.shot_count_value.setMaximumSize(QSize(50, 40))
        self.shot_count_value.setFont(font_normal)
        self.shot_count_value.setFrame(True)
        self.shot_count_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shot_count_value.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.shot_count_value.setMinimum(1)
        self.shot_count_value.setMaximum(100)
        self.shot_count_value.setSingleStep(1)
        self.shot_count_value.setValue(1)
        self.shot_count_value.setDisplayIntegerBase(10)

        self.start_shot_value = QSpinBox(self.gridLayoutWidget)
        self.start_shot_value.setObjectName(u"shotNumberStart_input")
        self.start_shot_value.setEnabled(True)
        self.start_shot_value.setSizePolicy(size_policy_preferred)
        self.start_shot_value.setMinimumSize(QSize(50, 40))
        self.start_shot_value.setFont(font_normal)
        self.start_shot_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_shot_value.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.start_shot_value.setMinimum(10)
        self.start_shot_value.setMaximum(1000)
        self.start_shot_value.setSingleStep(10)
        self.start_shot_value.setValue(10)

        self.shot_count_label = QLabel(self.gridLayoutWidget)
        self.shot_count_label.setObjectName(u"shotCount_label")
        self.shot_count_label.setSizePolicy(size_policy_min)
        self.shot_count_label.setFont(font_bold)
        self.shot_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shot_count_label.setWordWrap(True)

        self.start_shot_label = QLabel(self.gridLayoutWidget)
        self.start_shot_label.setObjectName(u"startShot_label")
        self.start_shot_label.setSizePolicy(size_policy_min)
        self.start_shot_label.setFont(font_bold)
        self.start_shot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_shot_label.setWordWrap(True)

        self.shot_length_label = QLabel(self.gridLayoutWidget)
        self.shot_length_label.setObjectName(u"shotLength_label")
        self.shot_length_label.setSizePolicy(size_policy_min)
        self.shot_length_label.setFont(font_bold)
        self.shot_length_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shot_length_label.setWordWrap(True)

        self.gridLayout.addWidget(self.start_shot_label, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.start_shot_value, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.shot_count_label, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.shot_count_value, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.shot_length_label, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.shot_length_value, 1, 3, 1, 1)
        self.gridLayout.addLayout(QHBoxLayout(), 0, 0, 1, 1)

        self.cameraAim_checkbox = QCheckBox(createShots_dialog)
        self.cameraAim_checkbox.setObjectName(u"cameraAim_checkbox")
        self.cameraAim_checkbox.setGeometry(QRect(10, 120, 231, 16))
        self.cameraAim_checkbox.setFont(font_normal)
        self.cameraAim_checkbox.setChecked(False)
        self.cameraAim_checkbox.setToolTip("Select if you want to import camera with aim.")
        self.cameraAim_checkbox.setText("Import camera with aim")

        QMetaObject.connectSlotsByName(createShots_dialog)

        createShots_dialog.setWindowTitle("New shot")
        self.add_shots_button.setToolTip("Build shot")
        self.add_shots_button.setText("ADD SHOT(s)")
        self.shot_length_value.setToolTip("All created shots will start at frame 1000 and have this length.")
        self.shot_length_value.setText("200")
        self.shot_count_value.setToolTip("Number of shots to create.")
        self.start_shot_value.setToolTip("Shots are numbered in increments of 10 by default."
                                         "Other numbers can be entered manually.")
        self.shot_count_label.setText("COUNT")
        self.start_shot_label.setText("SHOT")
        self.shot_length_label.setText("LENGTH")
