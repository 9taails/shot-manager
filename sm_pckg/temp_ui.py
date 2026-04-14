def setup_ui(self):
        """ Creates UI elements. """

        # Size and alignment properties
        self.edit_size_str = QSize(60, 30)
        self.edit_size_int = QSize(40, 30)
        self.icon_size = QSize(22, 30)
        self.aov_icon_size = QSize(20, 20)
        self.button_size = QSize(18, 30)
        self.align_center = Qt.AlignmentFlag.AlignCenter

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.master_layout = QHBoxLayout()
        self.master_layout.setSpacing(2)
        self.master_layout.setContentsMargins(5, 2, 5, 2)

        self.shot_layout = QHBoxLayout()
        self.shot_layout.setContentsMargins(0, 5, 5, 5)
        self.shot_layout.setSpacing(1)
        self.shot_layout.setAlignment(self.align_center)

        self.aov_layout = QHBoxLayout()
        self.aov_layout.setSpacing(1)
        self.aov_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.layer_layout = QHBoxLayout()
        self.layer_layout.setSpacing(3)
        self.layer_layout.setAlignment(self.align_center)

        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(3)
        self.info_layout.setAlignment(self.align_center)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(5)
        self.button_layout.setContentsMargins(1, 0, 1, 0)
        self.button_layout.setAlignment(self.align_center)

        # Frame
        self.frame = QFrame(self)
        self.frame.setLayout(self.master_layout)
        self.main_layout.addWidget(self.frame)

         # Name input
        self.shot_name_validator = QRegularExpressionValidator(
            QRegularExpression(r'(p\d\d-)?s\d\d\d$'))
        self.shot_pattern = f"{self.name}"
        self.layer_pattern = self.shot_pattern + "\\w"
        self.layer_regex = QRegularExpression(self.layer_pattern)
        self.layer_validator = QRegularExpressionValidator(self.layer_regex)

        self.name_field = QLineEdit("name")
        self.name_field.setFixedSize(self.edit_size_str)
        self.name_field.setEnabled(False)
        self.name_field.setToolTip("Shot name.")
        self.name_field.setAlignment(self.align_center)
        self.name_field.setFont(QFont("Open Sans ExtraBold", 10, 100))
        self.name_field.setText(self.name)

        if isinstance(self, Shot):
            self.name_field.setValidator(self.shot_name_validator)
        elif isinstance(self, RenderLayer):
            self.name_field.setValidator(self.layer_validator)
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
        self.frame_range_button.setIconSize(self.icon_size)

        self.number_validator = QIntValidator(0, 20000)

        self.start = QLineEdit("start")
        self.start.setFixedSize(self.edit_size_int)
        self.start.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.start.setValidator(self.number_validator)
        self.start.setToolTip("Start frame.")
        self.start.setAlignment(self.align_center)

        self.separator_01 = QLabel("-")
        self.separator_01.setAlignment(self.align_center)

        self.end = QLineEdit("end")
        self.end.setFixedSize(self.edit_size_int)
        self.end.setToolTip("End frame.")
        self.end.setAlignment(self.align_center)

        self.line_02 = QLabel()
        self.line_02.setObjectName("line")
        self.line_02.setFixedSize(1, 30)
        self.line_02.setAlignment(self.align_center)
        self.line_02.setStyleSheet(self.frame_styles["QLabel"][self.color])

        self.spacer = QLabel("")

        # Resolution inputs

        self.resolution_button = QToolButton()
        self.resolution_button.setObjectName("resolution_button")
        self.resolution_button.setIcon(QIcon(Paths.icon("icon_resolution.png")))
        self.resolution_button.setIconSize(self.icon_size)

        self.width_input = QLineEdit("width_input")
        self.width_input.setFixedSize(self.edit_size_int)
        self.width_input.setValidator(self.number_validator)
        self.width_input.setToolTip("Resolution width.")
        self.width_input.setAlignment(self.align_center)

        self.separator_02 = QLabel("x")
        self.separator_02.setAlignment(self.align_center)

        self.height_input = QLineEdit("height_input")
        self.height_input.setFixedSize(self.edit_size_int)
        self.height_input.setValidator(self.number_validator)
        self.height_input.setToolTip("Resolution height.")
        self.height_input.setAlignment(self.align_center)

        self.line_03 = QLabel()
        self.line_03.setObjectName("line")
        self.line_03.setFixedSize(1, 30)
        self.line_03.setAlignment(self.align_center)
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
        self.aov_beauty_button.setIconSize(self.aov_icon_size)
        self.aov_beauty_button.setToolTip("Beauty AOVs")

        self.aov_utility_button = QToolButton()
        self.aov_utility_button.setObjectName("aov_utility_button")
        self.aov_utility_button.setCheckable(True)
        self.aov_utility_button.setIcon(QIcon(Paths.icon("icon_aov_utility_off.png")))
        self.aov_utility_button.setIconSize(self.aov_icon_size)
        self.aov_utility_button.setToolTip("Utility AOVs")

        # Shot only UI

        if isinstance(self, Shot):

            self.layers_icon = QToolButton()
            self.layers_icon.setObjectName("layers_icon")
            self.layers_icon.setIcon(QIcon(Paths.icon("icon_layers.png")))
            self.layers_icon.setIconSize(self.icon_size)

            self.layers_label = QLabel()
            self.layers_label.setMinimumSize(QSize(50, 20))
            self.layers_label.setToolTip("Number of existing layers for this shot.")
            self.layers_label.setAlignment(self.align_center)

            self.line_04 = QLabel()
            self.line_04.setObjectName("line")
            self.line_04.setFixedSize(1, 30)
            self.line_04.setAlignment(self.align_center)
            self.line_04.setStyleSheet(self.frame_styles["QLabel"][self.color])

            self.edit_button = QToolButton()
            self.edit_button.setObjectName("edit_button")
            self.edit_button.setIcon(QIcon(Paths.icon("icon_edit.png")))
            self.edit_button.setIconSize(self.button_size)
            self.edit_button.setToolTip("Edit shot.")
            self.edit_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Shot edit buttons

        self.visibility_button = QToolButton()
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setParent(self.frame)
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setIconSize(self.button_size)
        self.visibility_button.setToolTip("No active layers in this shot.")

        self.render_button = QToolButton()
        self.render_button.setObjectName("render_button")
        self.render_button.setCheckable(True)
        self.render_button.setIconSize(self.button_size)
        self.render_button.setToolTip("Renderable status.")

        self.delete_button = QToolButton()
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setIcon(QIcon(Paths.icon("icon_delete.png")))
        self.delete_button.setIconSize(self.button_size)
        self.delete_button.setToolTip("Delete shot.")

        # Layout widgets

        self.shot_layout.addWidget(self.name_field)
        self.shot_layout.addWidget(self.line)
        self.shot_layout.addWidget(self.spacer)
        self.shot_layout.addWidget(self.frame_range_button)
        self.shot_layout.addWidget(self.start)
        self.shot_layout.addWidget(self.separator_01)
        self.shot_layout.addWidget(self.end)
        self.shot_layout.addWidget(self.line_02)
        self.shot_layout.addWidget(self.spacer)
        self.shot_layout.addWidget(self.resolution_button)
        self.shot_layout.addWidget(self.width_input)
        self.shot_layout.addWidget(self.separator_02)
        self.shot_layout.addWidget(self.height_input)
        self.shot_layout.addWidget(self.line_03)
        self.shot_layout.addWidget(self.spacer)

        self.aov_layout.addWidget(self.aov_button)
        self.aov_layout.addWidget(self.aov_beauty_button)
        self.aov_layout.addWidget(self.aov_utility_button)

        if isinstance(self, Shot):
            self.layer_layout.addWidget(self.layers_icon)
            self.layer_layout.addWidget(self.layers_label)
            self.layer_layout.addWidget(self.spacer)
            self.layer_layout.addWidget(self.spacer)
            self.button_layout.addWidget(self.line_04)

        self.button_layout.addWidget(self.visibility_button)

        if isinstance(self, Shot):
            self.button_layout.addWidget(self.edit_button)

        self.button_layout.addWidget(self.render_button)
        self.button_layout.addWidget(self.delete_button)

        self.master_layout.addLayout(self.shot_layout)
        self.master_layout.addLayout(self.info_layout)
        self.info_layout.addLayout(self.aov_layout)
        self.info_layout.addLayout(self.layer_layout)
        self.master_layout.addLayout(self.button_layout)