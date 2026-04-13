from PySide6.QtCore import (
    QSize,
    Qt,
    QRegularExpression,
    QEvent
)
from PySide6.QtGui import (
    QIcon,
    QRegularExpressionValidator,
    QIntValidator,
    QFont
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QLineEdit,
    QToolButton,
    QLabel,
    QVBoxLayout,
    QWidget,
    QStyledItemDelegate,
    QStyle
)

class UI(QWidget):
    
    def __init__(self):
        super(UI, self).__init__()
    
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        master_layout = QHBoxLayout()
        master_layout.setSpacing(2)
        master_layout.setContentsMargins(5, 2, 5, 2)

        shot_layout = QHBoxLayout()
        shot_layout.setContentsMargins(0, 5, 5, 5)
        shot_layout.setSpacing(1)
        shot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        aov_layout = QHBoxLayout()
        aov_layout.setSpacing(1)
        aov_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layer_layout = QHBoxLayout()
        layer_layout.setSpacing(3)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(1, 0, 1, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Size properties

        edit_size_str = QSize(60, 30)
        edit_size_int = QSize(40, 30)
        icon_size = QSize(22, 30)
        aov_icon_size = QSize(20, 20)
        button_size = QSize(18, 30)

        # Frame
       
        self.frame = QFrame(self)
        self.frame.setLayout(master_layout)
        self.main_layout.addWidget(self.frame)
        
         # Name input

        shot_name_validator = QRegularExpressionValidator(QRegularExpression(r'(p\d\d-)?s\d\d\d$'))
        
        shot_pattern = f"{self.name}"
        layer_pattern = shot_pattern + "\\w"
        layer_regex = QRegularExpression(layer_pattern)
        layer_validator = QRegularExpressionValidator(layer_regex)

        self.name_field = QLineEdit("name")
        self.name_field.setFixedSize(edit_size_str)
        self.name_field.setEnabled(False)
        self.name_field.setToolTip("Shot name.")
        self.name_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_field.setFont(QFont("Open Sans ExtraBold", 10, 100))
        self.name_field.setText(self.name)
        
        if isinstance(self, Shot):
            self.name_field.setValidator(shot_name_validator)
        elif isinstance(self, RenderLayer):
            self.name_field.setValidator(layer_validator)
            self.name_field.setReadOnly(True)
            self.name_field.setMouseTracking(True)
            self.name_field.installEventFilter(self.name_field)

        self.line = QLabel()
        self.line.setObjectName("line")
        self.line.setFixedSize(2, 50)
        self.line.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.line.setStyleSheet(self.frame_styles["QLabel"].get(self.color))

        # Frame range inputs

        self.frame_range_button = QToolButton()
        self.frame_range_button.setChecked(False)
        self.frame_range_button.setObjectName("frame_range_button")
        self.frame_range_button.setIcon(QIcon(Paths.icon("icon_frame_range.png")))
        self.frame_range_button.setIconSize(icon_size)

        number_validator = QIntValidator(0, 20000)

        self.start = QLineEdit("start")
        self.start.setFixedSize(edit_size_int)
        self.start.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.start.setValidator(number_validator)
        self.start.setToolTip("Start frame.")
        self.start.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.separator_01 = QLabel("-")
        self.separator_01.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.end = QLineEdit("end")
        self.end.setFixedSize(edit_size_int)
        self.end.setToolTip("End frame.")
        self.end.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.line_02 = QLabel()
        self.line_02.setObjectName("line")
        self.line_02.setFixedSize(1, 30)
        self.line_02.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_02.setStyleSheet(self.frame_styles["QLabel"][self.color])

        self.spacer = QLabel("")

        # Resolution inputs

        self.resolution_button = QToolButton()
        self.resolution_button.setObjectName("resolution_button")
        self.resolution_button.setIcon(QIcon(Paths.icon("icon_resolution.png")))
        self.resolution_button.setIconSize(icon_size)

        self.width_input = QLineEdit("width_input")
        self.width_input.setFixedSize(edit_size_int)
        self.width_input.setValidator(number_validator)
        self.width_input.setToolTip("Resolution width.")
        self.width_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.separator_02 = QLabel("x")
        self.separator_02.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.height_input = QLineEdit("height_input")
        self.height_input.setFixedSize(edit_size_int)
        self.height_input.setValidator(number_validator)
        self.height_input.setToolTip("Resolution height.")
        self.height_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.line_03 = QLabel()
        self.line_03.setObjectName("line")
        self.line_03.setFixedSize(1, 30)
        self.line_03.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_03.setStyleSheet(self.frame_styles["QLabel"][self.color])

        # AOVs

        self.aov_button = QToolButton()
        self.aov_button.setObjectName("aov_button")
        self.aov_button.setCheckable(True)
        self.aov_button.setIcon(QIcon(Paths.icon("icon_aov_off.png")))

        self.aov_beauty_button = QToolButton()
        self.aov_beauty_button.setObjectName("aov_beauty_button")
        self.aov_beauty_button.setCheckable(True)
        self.aov_beauty_button.setIcon(QIcon(Paths.icon("icon_aov_beauty_off.png")))
        self.aov_beauty_button.setIconSize(aov_icon_size)
        self.aov_beauty_button.setToolTip("Beauty AOVs")

        self.aov_utility_button = QToolButton()
        self.aov_utility_button.setObjectName("aov_utility_button")
        self.aov_utility_button.setCheckable(True)
        self.aov_utility_button.setIcon(QIcon(Paths.icon("icon_aov_utility_off.png")))
        self.aov_utility_button.setIconSize(aov_icon_size)
        self.aov_utility_button.setToolTip("Utility AOVs")

        # Shot only UI
        
        if isinstance(self, Shot):

            self.layers_icon = QToolButton()
            self.layers_icon.setObjectName("layers_icon")
            self.layers_icon.setIcon(QIcon(Paths.icon("icon_layers.png")))
            self.layers_icon.setIconSize(icon_size)

            self.layers_label = QLabel()
            self.layers_label.setMinimumSize(QSize(50, 20))
            self.layers_label.setToolTip("Number of existing layers for this shot.")
            self.layers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.line_04 = QLabel()
            self.line_04.setObjectName("line")
            self.line_04.setFixedSize(1, 30)
            self.line_04.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.line_04.setStyleSheet(self.frame_styles["QLabel"][self.color])
            
            self.edit_button = QToolButton()
            self.edit_button.setObjectName("edit_button")
            self.edit_button.setIcon(QIcon(Paths.icon("icon_edit.png")))
            self.edit_button.setIconSize(button_size)
            self.edit_button.setToolTip("Edit shot.")
            self.edit_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Shot edit buttons

        self.visibility_button = QToolButton()
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setParent(self.frame)
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setIconSize(button_size)
        self.visibility_button.setToolTip("No active layers in this shot.")

        self.render_button = QToolButton()
        self.render_button.setObjectName("render_button")
        self.render_button.setCheckable(True)
        self.render_button.setIconSize(button_size)
        self.render_button.setToolTip("Renderable status.")

        self.delete_button = QToolButton()
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setIcon(QIcon(Paths.icon("icon_delete.png")))
        self.delete_button.setIconSize(button_size)
        self.delete_button.setToolTip("Delete shot.")

        # Layout widgets

        shot_layout.addWidget(self.name_field)
        shot_layout.addWidget(self.line)
        shot_layout.addWidget(self.spacer)
        shot_layout.addWidget(self.frame_range_button)
        shot_layout.addWidget(self.start)
        shot_layout.addWidget(self.separator_01)
        shot_layout.addWidget(self.end)
        shot_layout.addWidget(self.line_02)
        shot_layout.addWidget(self.spacer)
        shot_layout.addWidget(self.resolution_button)
        shot_layout.addWidget(self.width_input)
        shot_layout.addWidget(self.separator_02)
        shot_layout.addWidget(self.height_input)
        shot_layout.addWidget(self.line_03)
        shot_layout.addWidget(self.spacer)

        aov_layout.addWidget(self.aov_button)
        aov_layout.addWidget(self.aov_beauty_button)
        aov_layout.addWidget(self.aov_utility_button)

        if isinstance(self, Shot):
            layer_layout.addWidget(self.layers_icon)
            layer_layout.addWidget(self.layers_label)
            layer_layout.addWidget(self.spacer)
            layer_layout.addWidget(self.spacer)
            button_layout.addWidget(self.line_04)
            
        button_layout.addWidget(self.visibility_button)
        
        if isinstance(self, Shot):
            button_layout.addWidget(self.edit_button)
            
        button_layout.addWidget(self.render_button)
        button_layout.addWidget(self.delete_button)

        master_layout.addLayout(shot_layout)
        master_layout.addLayout(info_layout)
        info_layout.addLayout(aov_layout)
        info_layout.addLayout(layer_layout)
        master_layout.addLayout(button_layout)
