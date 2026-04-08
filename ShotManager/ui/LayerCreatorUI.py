from PySide6.QtCore import (
    QSize,
    QMetaObject
)
from PySide6.QtGui import (
    QFont,
    Qt
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QFrame,
    QCheckBox,
    QLineEdit,
    QLabel,
    QPushButton
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
