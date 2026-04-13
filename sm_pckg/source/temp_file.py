

class CustomQTreeWidgetItem(QStandardItem):
    """
    Custom widget representing a shot.

    Attributes:
        data_file_directory (str): The path to the data file.
        frame_styles (dict): Dictionary containing style sheet for QFrame
        style_sheet (dict): Dictionary containing global style sheet

    """
    # Define a unique type ID for your class
    TYPE_ID = QStandardItem.ItemType.UserType

    def __init__(self):
        super().__init__()

        self.objectName = None
        self.shot_name = None
        self.visibility_button = None
        self.data_file_directory = Paths.return_shot_data_full_filepath()  # Path to data file
        self.style_sheet = util.load_style_sheet()
        self.frame_styles = util.load_frame_style()

    def apply_frame_style(self, color):
        """ Applies a style sheet to QFrame button for active/inactive shot.

            Args:
                color (str): color name from the style sheet
        """

        # Get the correct style sheet for the QFrame
        style = self.frame_styles["QFrame"][color]

        # Assign the style sheet
        self.setBackground(style)

    def toggle_style_frame(self):
        """ Reads in the style sheet and applies the correct frame style based on visibility of the shot."""

        data = util.shot_data_directory()
        shot_color = data[self.shot_name]["color"]
        active_color = shot_color + "_active"
        
        if self.visibility_button is not None:
            if self.visibility_button.isChecked():
                self.apply_frame_style(active_color)

            else:
                self.apply_frame_style(shot_color)

    def type(self):
        return 1000

    def setParent(self, parent):
       self.parent = parent
       return self.parent

    @staticmethod
    def return_parent(widget):
        """
        Returns the parent Shot object containing the widget.

        Args:
            widget (QWidget): The widget to find the parent Shot object for.

        Returns:
            shot_widget (Shot): The parent Shot object containing the widget.
        """

        frame_widget = widget.parentWidget()
        parent = frame_widget.parentWidget()

        return parent

    def return_child_widget(self, widget_name):
        """
        Returns the child widget with the given name.

        Args:
            widget_name (str): The name of the child widget to return.

        Returns:
            widget (QWidget): The child widget with the given name.
        """

        widget = self.__getattribute__(widget_name)
        return widget

    @staticmethod
    def return_button_checked_state(widget: QToolButton):
        """ Returns the checked state of a QToolButton. """

        return widget.isChecked()

    @staticmethod
    def toggle_icon(button: QToolButton):
        """
        Toggles the icon based on the checked state of the button.

        Args:
            button (QToolButton): The button to toggle the icon for.
        """

        if not button.isChecked():
            status = "off"
        else:
            status = "on"

        icon, tooltip = util.return_icon_and_tooltip(button.objectName(), status)

        button.setIcon(icon)
        button.setToolTip(tooltip)

    def setObjectName(self, name):
        self.objectName = name
        return self.objectName

class ShotOld(CustomQTreeWidgetItem):
    """
    Custom widget representing a shot.

    Args:
        shot_name (str): The name of the shot.

    Attributes:
        data_file_directory (str): The path to the data file.
        shot_name (str): The name of the shot

    """
    TYPE_ID = QStandardItem.ItemType.UserType


    def __init__(self, shot_name: str):
        super().__init__()

        self.data_file_directory = Paths.return_shot_data_full_filepath()

        self.shot_name = shot_name
        self.setup_ui()


        # Connect signals and slots
        self.render_button.clicked.connect(lambda: self.toggle_icon(self.render_button))
        self.visibility_button.clicked.connect(lambda: self.toggle_icon(self.visibility_button))
        self.frame_range_button.clicked.connect(lambda: self.toggle_icon(self.frame_range_button))
        self.change_aov_icon_from_layers_aov_status()

        self.name.textEdited.connect(lambda: self.update_field("name", self.name.text()))
        self.start.editingFinished.connect(lambda: self.update_field("start", self.start.text()))
        self.end.editingFinished.connect(lambda: self.update_field("end", self.end.text()))
        self.width_input.editingFinished.connect(lambda: self.update_field("width", self.width_input.text()))
        self.height_input.editingFinished.connect(lambda: self.update_field("height", self.height_input.text()))
        self.visibility_button.toggled.connect(lambda: self.toggle_style_frame())

    def setup_ui(self):
        """
       Sets up the user interface for the shot widget.
       """

        # Layouts

        master_layout = QHBoxLayout()
        master_layout.setSpacing(2)

        shot_layout = QHBoxLayout()
        shot_layout.setContentsMargins(-5, 5, 5, 5)
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

        frame_size = QSize(550, 70)
        edit_size_str = QSize(60, 30)
        edit_size_int = QSize(40, 30)
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        icon_size = QSize(22, 30)
        aov_icon_size = QSize(20, 20)
        button_size = QSize(18, 30)

        # Frame

        self.frame = QFrame()
        self.frame.setMaximumSize(frame_size)
        self.frame.setSizePolicy(size_policy)

        # Shot name input

        shot_name_validator = QRegularExpressionValidator(QRegularExpression(r'(p\d\d-)?s\d\d\d$'))

        self.name = QLineEdit("name")
        self.name.setFixedSize(edit_size_str)
        self.name.setValidator(shot_name_validator)
        self.name.setEnabled(False)
        self.name.setToolTip("Shot name.")
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setFont(QFont("Open Sans ExtraBold", 10, 100))
        self.name.setText(self.shot_name)

        color = self.return_shot_color()

        self.line = QLabel()
        self.line.setObjectName("line")
        self.line.setFixedSize(2, 50)
        self.line.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.line.setStyleSheet(self.frame_styles["QLabel"][color])

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
        self.line_02.setStyleSheet(self.frame_styles["QLabel"][color])

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
        self.line_03.setStyleSheet(self.frame_styles["QLabel"][color])

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

        # Render layers info

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
        self.line_04.setStyleSheet(self.frame_styles["QLabel"][color])

        # Shot edit buttons

        self.visibility_button = QToolButton()
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setParent(self.frame)
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setIconSize(button_size)
        self.visibility_button.setToolTip("No active layers in this shot.")

        self.edit_button = QToolButton()
        self.edit_button.setObjectName("edit_button")
        self.edit_button.setIcon(QIcon(Paths.icon("icon_edit.png")))
        self.edit_button.setIconSize(button_size)
        self.edit_button.setToolTip("Edit shot.")
        self.edit_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

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

        shot_layout.addWidget(self.name)
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

        layer_layout.addWidget(self.layers_icon)
        layer_layout.addWidget(self.layers_label)
        layer_layout.addWidget(self.spacer)
        layer_layout.addWidget(self.spacer)

        button_layout.addWidget(self.line_04)
        button_layout.addWidget(self.visibility_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.render_button)
        button_layout.addWidget(self.delete_button)

        master_layout.addLayout(shot_layout)
        master_layout.addLayout(info_layout)
        info_layout.addLayout(aov_layout)
        info_layout.addLayout(layer_layout)
        master_layout.addLayout(button_layout)

        self.frame.setLayout(master_layout)

        # ---> End layout

    def update_shot_widgets(self, data):
        """Sets the values of all fields from the data dictionary. Dictionary cannot be empty.

        Args:
            data (dict): A dictionary saved out in the JSON file.
        """
        if data:
            for key, value in data.items():

                if key == "name":
                    self.setObjectName(value)
                    self.frame.setObjectName(value)
                    #self.setObjectName(value + "_shot")
                    self.start.setObjectName(value + "_start")
                    self.end.setObjectName(value + "_end")
                    self.width_input.setObjectName(value + "_width")
                    self.height_input.setObjectName(value + "_height")
                    self.layers_label.setObjectName(value + "_layers")
                    self.name.setText(value)

                elif key == "start":

                    self.start.setText(str(value))

                elif key == "end":
                    self.end.setText(str(value))

                elif key == "width":
                    self.width_input.setText(str(value))

                elif key == "height":
                    self.height_input.setText(str(value))

                elif key == "render_layers":
                    no_layers = len(value)

                    if no_layers == 1:
                        self.layers_label.setText(str(no_layers) + " layer")
                    else:
                        self.layers_label.setText(str(no_layers) + " layers")

    def update_field(self, field_name, field_value):
        """
       Updates the field value in the data dictionary and saves it to the data file.

       Args:
           field_name (str): The name of the field to update.
           field_value (str): The value of the field to update.
       """

        data_dict = util.shot_data_directory()

        try:
            data_dict[self.shot_name].update({
                field_name: int(field_value)
            })
        except ValueError:
            data_dict[self.shot_name].update({
                field_name: field_value
            })

        with open(self.data_file_directory, "w") as data_dump:
            json.dump(data_dict, data_dump, indent=4)

    @staticmethod
    def return_shot_name(widget):
        """
        Returns the name of the Shot object containing the widget.

        Args:
            widget (QWidget): The widget to find the parent Shot object for.

        Returns:
            shot_name (str): The name of the Shot object containing the widget.
        """

        frame_widget = widget.parentWidget()
        shot_widget = frame_widget.parentWidget()
        shot_name = shot_widget.objectName()

        return shot_name

    def return_shot_color(self):
        try:
            data = util.shot_data_directory()
            return data[self.shot_name]["color"]
        except KeyError:
            pass

    def change_aov_icon_from_layers_aov_status(self):
        """Toggles the icon and AOV render mode for the render layer."""

        data = util.shot_data_directory()
        status_set = set()

        b: QToolButton
        b = self.aov_button
        shot = self.shot_name

        # Get AOVs mode for the layer
        layers_list = data[shot]["render_layers"]
        layers_dict = data[shot]["layers"]

        for layer in layers_list:
            status = layers_dict[layer].get("AOV mode")
            status_set.add(status)

        status_list = [s for s in status_set]
        list_len = len(status_list)

        # Set checked state for each button based on the AOVs value
        if list_len == 1:

            if status_list[0] == 0:     # All AOV modes are off
                icon, tooltip = util.return_icon_and_tooltip("aov_button", "off")
                b.setChecked(False)

            else:    # All AOV modes are on
                icon, tooltip = util.return_icon_and_tooltip("aov_button", "on")
                b.setChecked(True)

        else:
            icon, tooltip = util.return_icon_and_tooltip("aov_button", "mid")
            b.setChecked(True)

        b.setIcon(icon)
        b.setToolTip(tooltip)


class RenderLayerOld(CustomQTreeWidgetItem):
    """
    Represents a render layer widget.

    Args:
        layer_name (str): The name of the render layer.
    """

    def __init__(self, layer_name):
        super(RenderLayer, self).__init__()

        self.data_file_directory = Paths.return_shot_data_full_filepath()  # Path to data file
        self.layer_name = layer_name
        self.shot_name = self.layer_name[:4]
        self.data_model = RenderLayerDataModel(self.data_file_directory)
        self.setup_ui()

        # Connect signals and slots
        self.render_button.clicked.connect(lambda: self.render_button.toggle())
        self.render_button.clicked.connect(lambda: self.toggle_icon(self.render_button))
        self.visibility_button.clicked.connect(lambda: self.toggle_icon(self.visibility_button))
        self.visibility_button.toggled.connect(lambda: self.toggle_style_frame())
        self.aov_button.clicked.connect(lambda: self.aov_button.toggle())
        self.aov_button.toggled.connect(lambda: self.toggle_icon(self.aov_button))
        self.aov_button.clicked.connect(lambda: self.toggle_aov_mode_checked(self.aov_button))
        self.aov_beauty_button.clicked.connect(lambda: self.aov_beauty_button.toggle())
        self.aov_beauty_button.toggled.connect(lambda: self.toggle_icon(self.aov_beauty_button))
        self.aov_utility_button.clicked.connect(lambda: self.aov_utility_button.toggle())
        self.aov_utility_button.toggled.connect(lambda: self.toggle_icon(self.aov_utility_button))

        self.name.editingFinished.connect(lambda: self.update_field("name", self.name.text()))
        self.name.editingFinished.connect(lambda: util.rename_layers(self.layer_name, self.name.text()))
        self.start.editingFinished.connect(
            lambda: util.edit_overrides(layer_name, "start", int(self.start.text()), "defaultRenderGlobals"))
        self.end.editingFinished.connect(
            lambda: util.edit_overrides(layer_name, "end", int(self.end.text()), "defaultRenderGlobals"))

    def setup_ui(self):
        """
        Sets up the user interface for the render layer widget.
        """
        # Layouts

        master_layout = QHBoxLayout()

        layer_layout = QHBoxLayout()
        layer_layout.setContentsMargins(-5, 5, 5, 5)
        layer_layout.setSpacing(2)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        aov_layout = QHBoxLayout()
        aov_layout.setSpacing(1)
        aov_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(-5, 0, 5, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Size properties

        frame_size = QSize(520, 55)
        edit_str_size = QSize(130, 20)
        edit_int_size = QSize(40, 20)
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        icon_size = QSize(15, 20)
        aov_icon_size = QSize(13, 13)
        button_size = QSize(18, 20)

        # Frame

        self.frame = QFrame()
        self.frame.setMaximumSize(frame_size)
        self.frame.setSizePolicy(size_policy)

        # Shot name input

        self.name = QLineEdit("name")
        self.name.setMinimumSize(edit_str_size)
        self.name.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.name.setReadOnly(True)
        self.name.setMouseTracking(True)
        self.name.installEventFilter(self.name)
        self.name.setFont(QFont("Open Sans Bold", 8, 100))
        self.name.setToolTip("Layer name")

        shot_pattern = f"{self.shot_name}"
        layer_pattern = shot_pattern + "\\w"
        layer_regex = QRegularExpression(layer_pattern)
        layer_validator = QRegularExpressionValidator(layer_regex)
        self.name.setValidator(layer_validator)

        self.line = QLabel()
        self.line.setObjectName("line")
        self.line.setFixedSize(2, 50)
        self.line.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Frame range inputs

        self.frame_range_button = QToolButton()
        self.frame_range_button.setObjectName("frame_range_button")
        self.frame_range_button.setCheckable(True)
        self.frame_range_button.setIconSize(icon_size)
        self.frame_range_button.setIcon(QIcon(Paths.icon("icon_frame_range.png")))

        number_validator = QIntValidator(0, 20000)

        self.start = QLineEdit("start")
        self.start.setMinimumSize(edit_int_size)
        self.start.setSizePolicy(size_policy)
        self.start.setValidator(number_validator)
        self.start.setToolTip("Layer start frame")
        self.start.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.separator_01 = QLabel("-")
        self.separator_01.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.end = QLineEdit("end")
        self.end.setMinimumSize(edit_int_size)
        self.end.setSizePolicy(size_policy)
        # self.end.setValidator(number_validator)
        self.end.setToolTip("Layer end frame")
        self.end.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # AOVs

        self.aov_button = QToolButton()
        self.aov_button.setObjectName("aov_button")
        self.aov_button.setCheckable(True)
        icon, tooltip = util.return_icon_and_tooltip("aov_button", "off")
        self.aov_button.setIcon(icon)
        self.aov_button.setToolTip(tooltip)

        self.aov_beauty_button = QToolButton()
        self.aov_beauty_button.setObjectName("aov_beauty_button")
        self.aov_beauty_button.setCheckable(True)
        icon_1, tooltip_1 = util.return_icon_and_tooltip("aov_beauty_button", "on")
        self.aov_beauty_button.setIcon(icon_1)
        self.aov_beauty_button.setToolTip(tooltip_1)
        self.aov_beauty_button.setIconSize(aov_icon_size)

        self.aov_utility_button = QToolButton()
        self.aov_utility_button.setObjectName("aov_utility_button")
        self.aov_utility_button.setCheckable(True)
        icon_2, tooltip_2 = util.return_icon_and_tooltip("aov_utility_button", "on")
        self.aov_utility_button.setIcon(icon_2)
        self.aov_utility_button.setIconSize(aov_icon_size)
        self.aov_utility_button.setToolTip(tooltip_2)

        self.spacer = QLabel("")
        self.spacer.setFixedSize(10, 20)

        self.spacer_02 = QLabel("")
        self.spacer_02.setFixedSize(50, 20)

        self.line_03 = QLabel()
        self.line_03.setObjectName("line")
        self.line_03.setFixedSize(1, 30)
        self.line_03.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Shot edit buttons

        self.visibility_button = QToolButton()
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIconSize(button_size)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setToolTip("Set " + f"{self.layer_name}" + " as active layer")

        self.render_button = QToolButton()
        self.render_button.setObjectName("render_button")
        self.render_button.setCheckable(True)
        self.render_button.setIcon(QIcon(Paths.icon("icon_renderable_green.png")))
        self.render_button.setIconSize(button_size)

        self.delete_button = QToolButton()
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setIcon(QIcon(Paths.icon("icon_delete.png")))
        self.delete_button.setIconSize(button_size)

        # Layout widgets

        layer_layout.addWidget(self.name)
        layer_layout.addWidget(self.line)
        layer_layout.addWidget(self.spacer)
        layer_layout.addWidget(self.frame_range_button)
        layer_layout.addWidget(self.start)
        layer_layout.addWidget(self.separator_01)
        layer_layout.addWidget(self.end)
        layer_layout.addWidget(self.spacer)

        # aov_layout.addWidget(self.line_02)
        aov_layout.addWidget(self.aov_button)
        aov_layout.addWidget(self.aov_beauty_button)
        aov_layout.addWidget(self.aov_utility_button)
        aov_layout.addWidget(self.spacer)

        button_layout.addWidget(self.line_03)
        button_layout.addWidget(self.visibility_button)
        button_layout.addWidget(self.render_button)
        button_layout.addWidget(self.delete_button)

        master_layout.addLayout(layer_layout)
        master_layout.addLayout(aov_layout)
        master_layout.addLayout(button_layout)

        self.frame.setLayout(master_layout)

        # ---> End layout

    def update_layer_widgets(self, shot, layer):
        """
        Updates the render layer widget with the layer information from JSON file.

        Args:
            shot (str): The name of the shot.
            layer (str): The name of the layer.
        """

        data = util.shot_data_directory()

        try:
            layer_dict = data[shot]["layers"][layer]

        except KeyError:
            layer_dict = data[shot]

        if data and layer_dict:

            renderable = layer_dict.get("renderable")
            aov_mode = layer_dict.get("AOV mode")
            aovs = layer_dict.get("AOVs")

            for key, value in layer_dict.items():

                if key == "name":
                    self.setObjectName(value)
                    self.frame.setObjectName(value)
                    self.name.setObjectName(value + "_layer")
                    self.start.setObjectName(value + "_start")
                    self.end.setObjectName(value + "_end")
                    self.name.setText(value)

                if key == "start":

                    self.start.setText(str(value))
                    self.update_field("start", str(value))

                if key == "end":
                    self.end.setText(str(value))
                    self.update_field("end", str(value))

            # Check renderable status and set .isChecked for button and correct icon
            if renderable is not None:
                if renderable:
                    icon, tooltip = util.return_icon_and_tooltip("render_button", "on")
                    self.render_button.setChecked(True)

                else:
                    icon, tooltip = util.return_icon_and_tooltip("render_button", "off")
                    self.render_button.setChecked(False)

                self.render_button.setIcon(icon)
                self.render_button.setToolTip(tooltip)

            # Check for the AOV mode key and value. Set .isChecked for button and correct icon.
            if aov_mode is not None:
                if aov_mode == 1:
                    icon, tooltip = util.return_icon_and_tooltip("aov_button", "on")

                else:
                    icon, tooltip = util.return_icon_and_tooltip("aov_button", "off")

                self.aov_button.setToolTip(tooltip)
                self.aov_button.setIcon(icon)

            # Check for the AOV mode key and value. Set .isChecked for button and correct icon.

            if aovs is not None:
                if isinstance(aovs, int):
                    aov_list = ([], 0)
                    RenderLayerDataModel(self.data_file_directory).update_layer(shot, layer, "AOVs", aov_list)

                else:

                    if "beauty" in aovs:

                        icon_beauty, tooltip_beauty = util.return_icon_and_tooltip("aov_beauty_button", "on")
                        self.aov_beauty_button.setChecked(True)
                        self.aov_beauty_button.setIcon(icon_beauty)
                        self.aov_beauty_button.setToolTip(tooltip_beauty)

                    elif "utility" in aovs:

                        icon_utility, tooltip_utility = util.return_icon_and_tooltip("aov_utility_button", "on")
                        self.aov_utility_button.setChecked(True)
                        self.aov_utility_button.setIcon(icon_utility)
                        self.aov_utility_button.setToolTip(tooltip_utility)

    def update_field(self, field_name, field_value):
        try:
            self.data_model.update_layer(self.shot_name, self.layer_name, field_name, field_value)
        except Exception as e:
            # Handle the specific exception(s) that may occur during the update
            print(f"Error updating field: {e}")

    @staticmethod
    def return_layer_name(widget: QWidget):
        """
        Returns the name of the layer associated with the widget.

        Args:
            widget (QWidget): The widget.

        Returns:
            str: The name of the layer.
        """

        frame_widget = widget.parentWidget()
        if frame_widget is not None:
            parent = frame_widget.parentWidget()
            if parent is not None:
                layer_name = parent.objectName()
                return layer_name
        return ""

    def return_shot_name(self, widget: QWidget):
        """
        Returns the name of the shot associated with the widget.

        Args:
            widget (QWidget): The widget.

        Returns:
            str: The name of the shot.
        """

        parent = self.return_parent(widget)
        layer_name = parent.objectName()
        shot_name = layer_name[:4]

        return shot_name

    def toggle_range_icon(self, button: QToolButton):

        status = self.compare_range_values()

        if not status:
            icon, tooltip = util.return_icon_and_tooltip("frame_range_button", "on")
            button.setChecked(True)

        else:
            icon, tooltip = util.return_icon_and_tooltip("frame_range_button", "off")
            button.setChecked(False)

        button.setIcon(icon)
        button.setToolTip(tooltip)

    @staticmethod
    def toggle_aov_mode_checked(button: QToolButton):

        if button.isChecked():
            button.setChecked(False)

        else:
            button.setChecked(True)

    def compare_range_values(self):
        """ Checks start and end frame for the layer and compares them to the shot frame range. Toggles the icon based
            on the result of comparison.
        """

        data = self.data_model.load_data()

        shot_name = self.shot_name

        shot_dict = data[shot_name]

        shot_start = int(shot_dict["start"])
        shot_end = int(shot_dict["end"])

        layer_start = int(shot_dict["layers"][self.layer_name]["start"])
        layer_end = int(shot_dict["layers"][self.layer_name]["end"])

        if layer_start != shot_start or layer_end != shot_end:
            return False

        else:
            return True

    def eventFilter(self, obj, event):
        if obj == self.name and event.type() == QEvent.Type.MouseButtonDblClick:
            self.name.setReadOnly(False)
            return True
        return super().eventFilter(obj, event)

    def return_shot_color(self):
        try:
            data = util.shot_data_directory()
            return data[self.shot_name]["color"]
        except KeyError:
            pass

    def set_line_color(self):
        color = self.return_shot_color()
        self.line.setStyleSheet(self.frame_styles["QLabel"][color])
        self.line_03.setStyleSheet(self.frame_styles["QLabel"][color])


for shot in to_add_list:
                    
                    shot_item = QStandardItem(shot)
                    self.root.appendRow(shot_item)
                    parent_item = shot_item

                    shot_name_dict = data[shot]  # Name of the new shot
                    shot_color = data[shot]["color"]  # Assigned color

                    new_shot_instance = Shot(shot)  # Class Shot
                    new_shot_instance.update_shot_widgets(shot_name_dict)
                    new_shot_instance.setObjectName(shot)
                    #new_shot_instance.setParent(self)

                    shot_item.setChild(0, new_shot_instance) # Class QTreeWidgetItem

                    new_shot_instance.setSizeHint(QSize(550, 75))
                    #Shot.apply_frame_style(new_shot_instance, shot_color)


                    new_entry = self.root.child(self.model.rowCount() - 1)
                    
                    layer_list = sorted(data[shot]["render_layers"])

                    """# Create layers per shot
                    for layer in layer_list:

                        child_item = QStandardItem(layer)
                        parent_item.appendRow(child_item)

                        new_layer_instance = RenderLayer(layer)
                        new_layer_instance.update_layer_widgets(shot, layer)
                        new_layer_instance.setObjectName(layer)
                        new_layer_instance.setParent(new_shot_instance)
                        child_item.setSizeHint(QSize(550, 60))

                        child_item.setChild(0, new_layer_instance)

                        #CustomQTreeWidgetItem.apply_frame_style(
                                #new_layer_instance, shot_color)"""
        
        self.shotList_treeWidget.setModel(self.model)
        
        
        
        
def setup_ui(self):
        """
        Sets up the user interface for the render layer widget.
        """
        # Layouts

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        master_layout = QHBoxLayout()
        master_layout.setContentsMargins(5, 2, 5, 2)

        layer_layout = QHBoxLayout()
        layer_layout.setContentsMargins(0, 5, 5, 5)
        layer_layout.setSpacing(2)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        aov_layout = QHBoxLayout()
        aov_layout.setSpacing(1)
        aov_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(-5, 0, 5, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Size properties

        frame_size = QSize(520, 55)
        edit_str_size = QSize(130, 20)
        edit_int_size = QSize(40, 20)
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        icon_size = QSize(15, 20)
        aov_icon_size = QSize(13, 13)
        button_size = QSize(18, 20)

        # Frame

        self.frame = QFrame(self)
        self.frame.setMinimumHeight(55)
        self.frame.setLayout(master_layout)
        self.main_layout.addWidget(self.frame)

        # Shot name input

        self.name = QLineEdit("name")
        self.name.setMinimumSize(edit_str_size)
        self.name.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.name.setReadOnly(True)
        self.name.setMouseTracking(True)
        self.name.installEventFilter(self.name)
        self.name.setFont(QFont("Open Sans Bold", 8, 100))
        self.name.setToolTip("Layer name")

        shot_pattern = f"{self.shot_name}"
        layer_pattern = shot_pattern + "\\w"
        layer_regex = QRegularExpression(layer_pattern)
        layer_validator = QRegularExpressionValidator(layer_regex)
        self.name.setValidator(layer_validator)

        self.line = QLabel()
        self.line.setObjectName("line")
        self.line.setFixedSize(2, 50)
        self.line.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Frame range inputs

        self.frame_range_button = QToolButton()
        self.frame_range_button.setObjectName("frame_range_button")
        self.frame_range_button.setCheckable(True)
        self.frame_range_button.setIconSize(icon_size)
        self.frame_range_button.setIcon(QIcon(Paths.icon("icon_frame_range.png")))

        number_validator = QIntValidator(0, 20000)

        self.start = QLineEdit("start")
        self.start.setMinimumSize(edit_int_size)
        self.start.setSizePolicy(size_policy)
        self.start.setValidator(number_validator)
        self.start.setToolTip("Layer start frame")
        self.start.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.separator_01 = QLabel("-")
        self.separator_01.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.end = QLineEdit("end")
        self.end.setMinimumSize(edit_int_size)
        self.end.setSizePolicy(size_policy)
        # self.end.setValidator(number_validator)
        self.end.setToolTip("Layer end frame")
        self.end.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # AOVs

        self.aov_button = QToolButton()
        self.aov_button.setObjectName("aov_button")
        self.aov_button.setCheckable(True)
        icon, tooltip = util.return_icon_and_tooltip("aov_button", "off")
        self.aov_button.setIcon(icon)
        self.aov_button.setToolTip(tooltip)

        self.aov_beauty_button = QToolButton()
        self.aov_beauty_button.setObjectName("aov_beauty_button")
        self.aov_beauty_button.setCheckable(True)
        icon_1, tooltip_1 = util.return_icon_and_tooltip("aov_beauty_button", "on")
        self.aov_beauty_button.setIcon(icon_1)
        self.aov_beauty_button.setToolTip(tooltip_1)
        self.aov_beauty_button.setIconSize(aov_icon_size)

        self.aov_utility_button = QToolButton()
        self.aov_utility_button.setObjectName("aov_utility_button")
        self.aov_utility_button.setCheckable(True)
        icon_2, tooltip_2 = util.return_icon_and_tooltip("aov_utility_button", "on")
        self.aov_utility_button.setIcon(icon_2)
        self.aov_utility_button.setIconSize(aov_icon_size)
        self.aov_utility_button.setToolTip(tooltip_2)

        self.spacer = QLabel("")
        self.spacer.setFixedSize(10, 20)

        self.spacer_02 = QLabel("")
        self.spacer_02.setFixedSize(50, 20)

        self.line_03 = QLabel()
        self.line_03.setObjectName("line")
        self.line_03.setFixedSize(1, 30)
        self.line_03.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Shot edit buttons

        self.visibility_button = QToolButton()
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIconSize(button_size)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setToolTip("Set " + f"{self.layer_name}" + " as active layer")

        self.render_button = QToolButton()
        self.render_button.setObjectName("render_button")
        self.render_button.setCheckable(True)
        self.render_button.setIcon(QIcon(Paths.icon("icon_renderable_green.png")))
        self.render_button.setIconSize(button_size)

        self.delete_button = QToolButton()
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setIcon(QIcon(Paths.icon("icon_delete.png")))
        self.delete_button.setIconSize(button_size)

        # Layout widgets

        layer_layout.addWidget(self.name)
        layer_layout.addWidget(self.line)
        layer_layout.addWidget(self.spacer)
        layer_layout.addWidget(self.frame_range_button)
        layer_layout.addWidget(self.start)
        layer_layout.addWidget(self.separator_01)
        layer_layout.addWidget(self.end)
        layer_layout.addWidget(self.spacer)

        # aov_layout.addWidget(self.line_02)
        aov_layout.addWidget(self.aov_button)
        aov_layout.addWidget(self.aov_beauty_button)
        aov_layout.addWidget(self.aov_utility_button)
        aov_layout.addWidget(self.spacer)

        button_layout.addWidget(self.line_03)
        button_layout.addWidget(self.visibility_button)
        button_layout.addWidget(self.render_button)
        button_layout.addWidget(self.delete_button)

        master_layout.addLayout(layer_layout)
        master_layout.addLayout(aov_layout)
        master_layout.addLayout(button_layout)

        self.frame.setLayout(master_layout)

        # ---> End layout
