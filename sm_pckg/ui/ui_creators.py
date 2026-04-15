from PySide6.QtCore import (
    QSize,
    QMetaObject,
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
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QFrame,
    QCheckBox,
    QLineEdit,
    QLabel,
    QPushButton,
    QSpinBox,
    QAbstractSpinBox
)


class LayerCreatorUI(object):

    def setup_ui(self, layerCreator_dialog):
        if not layerCreator_dialog.objectName():
            layerCreator_dialog.setObjectName(u"layerCreator_dialog")

        layerCreator_dialog.resize(300, 360)
        layerCreator_dialog.setWindowTitle("Layer Creator")

        sizePolicy_mainWindow = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layerCreator_dialog.setSizePolicy(sizePolicy_mainWindow)
        layerCreator_dialog.setFixedSize(QSize(320, 360))
        size_checkbox = QSize(130, 30)

        font_bold = QFont("JetBrains Mono", 8, 75)
        font_bold.setBold(True)

        layerCreator_dialog.setStyleSheet(
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

            "QCheckBox::indicator{"
            "background-color: rgb(28, 31, 39);"
            "color:  rgb(125, 147, 154);"
            "padding: 1px;}"

            "QCheckBox::indicator:checked{"
            "background-color: rgb(125, 147, 154);"
            "color:  rgb(125, 147, 154);"
            "padding: 1px;}"

        )

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.preset_layout = QGridLayout()
        self.preset_layout.setSpacing(10)
        self.preset_layout.setContentsMargins(5, 5, 30, 30)

        self.widget = QWidget(layerCreator_dialog)
        self.widget.setLayout(self.main_layout)

        self.preset_frame = QFrame(layerCreator_dialog)
        self.preset_frame.setObjectName(u"frame")
        self.preset_frame.setMinimumSize(QSize(300, 200))
        self.preset_frame.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        self.master_layer_checkbox = QCheckBox(self.preset_frame)
        self.master_layer_checkbox.setObjectName(u"master_layer_checkbox")
        self.master_layer_checkbox.setText("Master")
        self.master_layer_checkbox.setMinimumSize(size_checkbox)

        self.global_background_checkbox = QCheckBox(self.preset_frame)
        self.global_background_checkbox.setObjectName(u"global_background_checkbox")
        self.global_background_checkbox.setText("Global background")
        self.global_background_checkbox.setMinimumSize(size_checkbox)

        self.global_foreground_checkbox = QCheckBox(self.preset_frame)
        self.global_foreground_checkbox.setObjectName(u"global_foreground_checkbox")
        self.global_foreground_checkbox.setText("Global foreground")
        self.global_foreground_checkbox.setMinimumSize(size_checkbox)

        self.shot_background_checkbox = QCheckBox(self.preset_frame)
        self.shot_background_checkbox.setObjectName(u"shot_background_checkbox")
        self.shot_background_checkbox.setText("Background")
        self.shot_background_checkbox.setMinimumSize(size_checkbox)

        self.shot_foreground_checkbox = QCheckBox(self.preset_frame)
        self.shot_foreground_checkbox.setObjectName(u"Shot_fg_checkbox")
        self.shot_foreground_checkbox.setText("Foreground")
        self.shot_foreground_checkbox.setMinimumSize(size_checkbox)

        self.custom_layer_checkbox = QCheckBox(self.preset_frame)
        self.custom_layer_checkbox.setObjectName(u"custom_layer_checkbox")
        self.custom_layer_checkbox.setText("Custom layer")
        self.custom_layer_checkbox.setMinimumSize(size_checkbox)

        self.custom_beauty_input = QLineEdit(self.preset_frame)
        self.custom_beauty_input.setObjectName(u"custom_beauty_input")
        self.custom_beauty_input.setMinimumSize(size_checkbox)
        self.custom_beauty_input.setEnabled(False)
        self.custom_beauty_input.setClearButtonEnabled(True)

        # Column 0
        self.preset_layout.addWidget(self.master_layer_checkbox, 0, 0)
        self.preset_layout.addWidget(self.shot_foreground_checkbox, 1, 0)
        self.preset_layout.addWidget(self.shot_background_checkbox, 2, 0)
        self.preset_layout.addWidget(self.custom_layer_checkbox, 3, 0)

        # Column 1
        self.preset_layout.addWidget(self.global_foreground_checkbox, 0, 1)
        self.preset_layout.addWidget(self.global_background_checkbox, 1, 1)
        self.preset_layout.addWidget(self.custom_beauty_input, 3, 1)

        self.render_presets_label = QLabel()
        self.render_presets_label.setObjectName(u"render_presets_label")
        self.render_presets_label.setText("RENDER PRESETS")
        self.render_presets_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.render_presets_label.setMinimumSize(QSize(300, 50))

        self.createLayers_button = QPushButton()
        self.createLayers_button.setText("CREATE LAYERS")
        self.createLayers_button.setObjectName(u"createLayers_button")
        self.createLayers_button.setFixedHeight(30)

        self.preset_frame.setLayout(self.preset_layout)
        self.main_layout.addWidget(self.render_presets_label)
        self.main_layout.addWidget(self.preset_frame)
        self.main_layout.addWidget(self.createLayers_button)

        QMetaObject.connectSlotsByName(layerCreator_dialog)

        self.createLayers_button.setToolTip("Create checked render layers for selected shots.")

        self.global_background_checkbox.setToolTip(
            "Includes background/environment, generic and shot lights. Product is "
            "included only for shadow casting with Primary Visibility set to Off."
        )

        self.master_layer_checkbox.setToolTip(
            "Includes hero product, generic lights and product specific lights, if "
            "they exist. Background is included with Primary Visibility set to Off."
        )

        self.global_foreground_checkbox.setToolTip(
            "Includes hero product, generic lights and product specific lights, if "
            "they exist. Background is included with Primary Visibility set to Off."
        )

        self.custom_layer_checkbox.setToolTip("Custom layer with empty background and foreground sets.")

        self.custom_beauty_input.setToolTip(
            "Write the name of every object you want to build a layer for. "
            "Resulting layer name will be s000_object_bty"
        )

class ShotCreatorUI(object):

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

        self.shot_length = QLineEdit(self.gridLayoutWidget)
        self.shot_length.setObjectName(u"shotLength_input")
        self.shot_length.setEnabled(True)
        self.shot_length.setSizePolicy(size_policy_min)
        self.shot_length.setMaximumSize(QSize(80, 40))
        self.shot_length.setFont(font_normal)
        self.shot_length.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.shot_count = QSpinBox(self.gridLayoutWidget)
        self.shot_count.setObjectName(u"numberOfShots_input")
        self.shot_count.setEnabled(True)
        self.shot_count.setSizePolicy(size_policy_preferred)
        self.shot_count.setMaximumSize(QSize(50, 40))
        self.shot_count.setFont(font_normal)
        self.shot_count.setFrame(True)
        self.shot_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shot_count.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.shot_count.setMinimum(1)
        self.shot_count.setMaximum(100)
        self.shot_count.setSingleStep(1)
        self.shot_count.setValue(1)
        self.shot_count.setDisplayIntegerBase(10)

        self.start_shot = QSpinBox(self.gridLayoutWidget)
        self.start_shot.setObjectName(u"shotNumberStart_input")
        self.start_shot.setEnabled(True)
        self.start_shot.setSizePolicy(size_policy_preferred)
        self.start_shot.setMinimumSize(QSize(50, 40))
        self.start_shot.setFont(font_normal)
        self.start_shot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_shot.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.start_shot.setMinimum(10)
        self.start_shot.setMaximum(1000)
        self.start_shot.setSingleStep(10)
        self.start_shot.setValue(10)

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
        self.gridLayout.addWidget(self.start_shot, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.shot_count_label, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.shot_count, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.shot_length_label, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.shot_length, 1, 3, 1, 1)
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
        self.shot_length.setToolTip("All created shots will start at frame 1000 and have this length.")
        self.shot_length.setText("200")
        self.shot_count.setToolTip("Number of shots to create.")
        self.start_shot.setToolTip("Shots are numbered in increments of 10 by default."
                                         "Other numbers can be entered manually.")
        self.shot_count_label.setText("COUNT")
        self.start_shot_label.setText("SHOT")
        self.shot_length_label.setText("LENGTH")
